from models import db, Newslist,Newsread  # 导入数据库模型
from flask_redis import FlaskRedis
from datetime import timedelta

from flask import Blueprint, jsonify, request
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import redis
import json
from datetime import timedelta, datetime
import logging
from bs4 import BeautifulSoup
from sqlalchemy import or_, desc, func, case

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建蓝图
news_bp = Blueprint('news', __name__)

# 配置Redis连接
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# 配置 requests 的重试策略
retry_strategy = Retry(
    total=3,  # 最多重试3次
    backoff_factor=0.5,  # 重试间隔
    status_forcelist=[500, 502, 503, 504]  # 哪些状态码需要重试
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

# 备用新闻数据
FALLBACK_NEWS = [
    {
        'id': 'fallback1',
        'title': '暂时无法获取最新新闻',
        'ctime': '2024-03-03 00:00:00',
        'source': '系统提示',
        'description': '由于网络原因，暂时无法获取最新新闻。请稍后再试。',
        'picUrl': '',
        'url': '#'
    }
]

def get_cache_key(params):
    """生成缓存键"""
    return f"news:list:{hash(frozenset(params.items()))}"

def get_cached_news(num):
    """从数据库获取缓存的新闻"""
    try:
        return Newslist.query.order_by(Newslist.ctime.desc()).limit(num).all()
    except Exception as e:
        logger.error(f"从数据库获取新闻失败: {str(e)}")
        return None


@news_bp.route('/get_news', methods=['GET'])
def get_news():
    """获取新闻列表，支持搜索和过滤"""
    try:
        # 获取查询参数
        search_query = request.args.get('query', '')
        source = request.args.get('source', '')
        date_range = request.args.get('date_range', '')
        username=request.args.get('username', '')
        # 构建查询
        query = Newslist.query

        # 添加搜索条件
        if search_query:
            search_filter = or_(
                Newslist.title.ilike(f'%{search_query}%'),
                Newslist.description.ilike(f'%{search_query}%'),
                Newslist.content.ilike(f'%{search_query}%')
            )
            query = query.filter(search_filter)

        # 添加来源筛选
        if source:
            query = query.filter(Newslist.source == source)

        # 添加日期范围筛选
        if date_range:
            days = int(date_range.replace('d', ''))
            date_limit = datetime.now() - timedelta(days=days)
            query = query.filter(Newslist.ctime >= date_limit)

        # 获取新闻列表
        news_items = query.order_by(desc(Newslist.ctime)).all()

        favorite_news_ids = db.session.query(Newsread.news_id).filter_by(username=username, is_favorite=True).all()
        favorite_news_ids = {news_id for (news_id,) in favorite_news_ids}

        # 构建响应数据
        response_data = {
            'news': [
                {**news.to_dict(), 'is_favorite': news.id in favorite_news_ids} for news in news_items
            ],
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"获取新闻列表失败: {str(e)}")
        return jsonify({
            'error': '获取新闻数据失败',
            'news': [],
            'sources': [],
        }), 500

@news_bp.route('/news/<string:news_id>', methods=['GET'])
def get_news_detail(news_id):
    """获取新闻详情"""
    try:
        # 尝试从缓存获取
        cache_key = f"news:detail:{news_id}"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            return jsonify(json.loads(cached_result))
        
        news = Newslist.query.get(news_id)
        if news:
            # 获取相关新闻（同一来源或相似风险等级的新闻）
            related_news = Newslist.query.filter(
                Newslist.id != news_id,
                or_(
                    Newslist.source == news.source,

                )
            ).order_by(desc(Newslist.ctime)).limit(4).all()

            response_data = {
                'news': news.to_dict(),
                'related_news': [n.to_dict() for n in related_news],
            }
            
            # 缓存结果
            redis_client.setex(
                cache_key,
                timedelta(hours=1),
                json.dumps(response_data)
            )
            
            return jsonify(response_data)
            
        return jsonify({'error': '新闻不存在'}), 404
        
    except Exception as e:
        logger.error(f"获取新闻详情失败: {str(e)}")
        return jsonify({'error': '获取新闻详情失败'}), 500


@news_bp.route('/update_favorite/<string:news_id>', methods=['PUT'])
def update_favorite(news_id):
    data = request.get_json()
    username = data.get('username')

    # 查找用户对该新闻的记录
    news_record = Newsread.query.filter_by(news_id=news_id, username=username).first()

    if news_record:
        # 更新新闻记录的收藏状态
        news_record.is_favorite = data.get('is_favorite', news_record.is_favorite)
    else:
        # 如果没有记录，则创建新的记录
        news_record = Newsread(username=username, news_id=news_id, is_favorite=data.get('is_favorite', True), is_finished=False)
        db.session.add(news_record)

    db.session.commit()
    return jsonify({"msg": "新闻收藏状态已更新"}), 200


@news_bp.route('/get_favorite_count', methods=['GET'])
def get_favorite_count():
    username = request.args.get('username')  # Get username from query parameters
    if not username:
        return jsonify({"error": "Username is required"}), 400
    favorite_count = Newsread.query.filter_by(username=username, is_favorite=True).count()
    return jsonify({"favorite_count": favorite_count}), 200
