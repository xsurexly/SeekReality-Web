from models import db, newslist  # 导入数据库模型
from flask_redis import FlaskRedis
from datetime import timedelta

from flask import Blueprint, jsonify, request
import requests
import redis
import json
from datetime import timedelta

# 创建蓝图
news_bp = Blueprint('news', __name__)

# 配置Redis连接
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@news_bp.route('/get_news', methods=['GET'])
def get_news():
    api_key = '96f163cda80b'  # 替换为您的API密钥
    num = request.args.get('num', 10)  # 获取返回新闻的数量，默认为10

    # 缓存的key
    cache_key = f"news_{num}"

    # 检查Redis缓存是否存在
    cached_data = redis_client.get(cache_key)

    #if cached_data:
    #    print("缓存命中:", json.loads(cached_data))  # 打印缓存内容
    #    return jsonify(json.loads(cached_data))

    # 如果缓存中没有数据，调用外部API获取数据
    url = f"https://whyta.cn/api/tx/guonei?key={api_key}&num={num}"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': '无法获取新闻数据'}), 500

    data = response.json()
    print(data)

    # 提取新闻数据
    news_list = data.get('result', {}).get('newslist', [])

    # 将新闻数据存储到MySQL数据库
    for news in news_list:
        # 检查新闻是否已存在，避免重复插入
        existing_news = newslist.query.filter_by(id=news['id']).first()
        if not existing_news:
            new_news = newslist(
                id=news['id'],
                title=news['title'],
                ctime=news['ctime'],
                source=news['source'],
                description=news['description'],
                picUrl=news.get('picUrl', ''),
                url=news.get('url', '')
            )
            db.session.add(new_news)

    db.session.commit()  # 提交数据库事务

    # 将数据存入Redis缓存，并设置过期时间（1小时）
    redis_client.setex(cache_key, timedelta(hours=1), json.dumps(news_list))

    # 返回新闻数据
    return jsonify(news_list)
