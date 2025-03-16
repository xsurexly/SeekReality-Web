import sys
import os
import random
from datetime import datetime, timedelta
import http.client
from apscheduler.schedulers.background import BackgroundScheduler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Newslist
import requests
from bs4 import BeautifulSoup
import logging
import schedule
import time
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask, Blueprint,jsonify

news_crawler_bp = Blueprint('news_crawler', __name__)
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../news_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置请求重试
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

# 新闻API配置
NEWS_APIS = {
    'social': {  # 社会新闻
        'name': 'social_news',
        'url': 'https://apis.tianapi.com/social/index',
        'key': '302358f7f53a791a1369a9bf59b57a95',
        'category': '社会',
        'params': {'num': '10'}
    },
    'tech': {    # 科技新闻
        'name': 'tech_news',
        'url': 'https://apis.tianapi.com/sicprobe/index',
        'key': '302358f7f53a791a1369a9bf59b57a95',
        'category': '科技',
        'params': {'num': '10'}
    },
    'finance': { # 财经新闻
        'name': 'finance_news',
        'url': 'https://apis.tianapi.com/caijing/index',
        'key': '302358f7f53a791a1369a9bf59b57a95',
        'category': '财经',
        'params': {'num': '10'}
    },
    'sports': {  # 体育新闻
        'name': 'sports_news',
        'url': 'https://apis.tianapi.com/tiyu/index',
        'key': '302358f7f53a791a1369a9bf59b57a95',
        'category': '体育',
        'params': {'num': '10'}
    },
    'entertainment': { # 娱乐新闻
        'name': 'entertainment_news',
        'url': 'https://apis.tianapi.com/huabian/index',
        'key': '302358f7f53a791a1369a9bf59b57a95',
        'category': '娱乐',
        'params': {'num': '10'}
    },
    'others': { # 其它新闻
        'name': 'entertainment_news',
        'url': 'https://apis.tianapi.com/internet/index',
        'key': '302358f7f53a791a1369a9bf59b57a95',
        'category': '其它',
        'params': {'num': '10'}
    }
}

# 新闻类别设置
CATEGORIES = ['社会', '科技', '财经', '体育', '娱乐', '其它']

# 定义各新闻来源对应的内容选择器
CONTENT_SELECTORS_BY_SOURCE = {
    '中国体育': [
        {'attrs': {'class': ['main_content']}},
        {'attrs': {'id': ['article', 'artibody']}}
    ],
    'IT家科学探索': [
        {'attrs': {'class': ['post_content']},
         'tags': ['div']}
    ],
    '南方社会': [
        {'attrs': {'class': ['content']},
         'tags': ['div', 'article']}
    ],
    '中国日报财经': [
        {'attrs': {'class': ['article']},
         'tags': ['div', 'article']}
    ],
    '网易互联网': [
        {'attrs': {'class': ['post_body']},
         'tags': ['div', 'article']}
    ],
    '网易明星': [
        {'attrs': {'class': ['post_body']},
         'tags': ['div', 'article']}
    ],
    '默认': [  # 未配置来源时使用的默认选择器
        {'attrs': {'class': ['article-content', 'article_content', 'article-detail']}},
        {'attrs': {'id': ['articleContent', 'content']}}
    ]
}

# 默认的通用内容选择器
DEFAULT_CONTENT_SELECTORS = [
    {'attrs': {'class': ['article-content', 'article_content', 'article-detail']}},
    {'attrs': {'class': ['news-content', 'news_content', 'news-detail']}},
    {'attrs': {'class': ['content-main', 'main-content', 'mainContent']}},
    {'attrs': {'id': ['articleContent', 'content', 'main-content']}},
    {'attrs': {'itemprop': 'articleBody'}}
]

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/fake_news_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

# 模拟虚假新闻检测，实际应调用真实检测接口
def simulate_fake_news_detection(news_content):
    fake_score = random.uniform(0, 1)
    return {'fake_score': fake_score}

#加强图片有效性检查
def is_picurl_accessible(picurl):
    try:
        # 检查URL格式并添加协议
        if picurl.startswith('//'):
            picurl = 'https:' + picurl  # Prepend with https:
        # 限制只下载前1024字节检查
        response = http.get(picurl, stream=True, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'image' not in content_type:
                return False
            # 读取前1KB验证
            for chunk in response.iter_content(1024):
                if chunk:
                    return True
                break
        return False
    except Exception as e:
        logger.error(f"图片检查失败: {picurl} - {str(e)}")
        return False


def fetch_news_content(url, source):
    """增强内容提取功能"""
    try:
        if url.startswith('//'):
            url = 'https:' + url  # Prepend with https:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate'
        }

        # 增加超时和重试
        response = http.get(url, timeout=(10, 60), headers=headers)  # 增加超时时间

        if response.status_code == 404:
            logger.warning(f"请求失败: {url} 状态码: 404 - 资源未找到")
            return None
        elif response.status_code != 200:
            logger.warning(f"请求失败: {url} 状态码: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'lxml')

        # 清理干扰元素
        for tag in soup(['script', 'style', 'iframe', 'nav', 'footer',
                         'aside', 'form', 'input', 'button', 'meta',
                         'link', 'noscript', 'svg', 'canvas']):
            tag.decompose()

        # 组合选择器策略
        selectors = CONTENT_SELECTORS_BY_SOURCE.get(source, []) + DEFAULT_CONTENT_SELECTORS

        main_content = None
        for selector in selectors:
            tags = selector.get('tags', ['article', 'div', 'section'])
            attrs = selector.get('attrs', {})

            for tag in (tags if isinstance(tags, list) else [tags]):
                search = soup.find(tag, attrs=attrs)
                if search:
                    main_content = search
                    break
            if main_content:
                break

        # 二次清理
        if main_content:
            for elem in main_content.find_all(True, class_=lambda x: x and ('comment' in x or 'ad' in x)):
                elem.decompose()

            # 返回HTML内容
            return str(main_content)  # Return the HTML of the main content

        logger.warning(f"未找到有效内容区域: {url}")
        return None

    except Exception as e:
        logger.error(f"内容提取异常: {url} - {str(e)}")
        return None


def fetch_and_store_news():
    """增强数据处理校验"""
    logger.info("开始获取新闻...")
    app = create_app()
    with app.app_context():
        total_added = 0
        total_invalid = 0

        for api_name, api_config in NEWS_APIS.items():
            news_list = fetch_from_api(api_config)
            logger.info(f"处理 {api_config['category']} 类别，获取到 {len(news_list)} 条新闻")

            for news in news_list:
                 # 检查是否已存在
                existing_news = Newslist.query.filter_by(id=news['id']).first()
                if existing_news:
                    logger.info(f"新闻已存在: {news['title']}")
                    continue

                # 基础校验
                if not all([news.get('title'), news.get('url'), news.get('id')]):
                    total_invalid += 1
                    continue

                # 内容获取
                content = fetch_news_content(news['url'], news['source'])
                if not content:
                    total_invalid += 1
                    continue

                # 图片校验
                if news.get('picUrl') and not is_picurl_accessible(news['picUrl']):
                    total_invalid += 1
                    continue


                # 数据库操作
                try:
                    new_entry = Newslist(
                        id=news['id'],
                        title=news['title'],
                        content=content,
                        url=news['url'],
                        picUrl=news.get('picUrl', ''),
                        source=news.get('source', '未知'),
                        category=api_config['category'],
                        fake_score=random.uniform(0, 1),
                        ctime=parse_datetime(news.get('ctime')))

                    db.session.add(new_entry)
                    db.session.commit()
                    total_added += 1
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"数据库操作失败: {str(e)}")
                    total_invalid += 1

        logger.info(f"处理完成: 新增 {total_added} 条，舍弃 {total_invalid} 条无效数据")
def fetch_from_api(api_config):
    """从指定API获取新闻"""
    try:
        url = f"{api_config['url']}?key={api_config['key']}&num={api_config['params']['num']}"
        logger.info(f"正在请求API: {url}")

        response = http.get(url)
        logger.info(f"API响应状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('code') != 200:
                logger.error(f"API返回错误: {data.get('msg')}")
                return []

            raw_news_list = data.get('result', {}).get('newslist', [])
            logger.info(f"获取到 {len(raw_news_list)} 条原始新闻")
            news_list = []
            for news in raw_news_list:
                try:
                    processed_news = {
                        'id': news.get('id', ''),
                        'title': news.get('title', ''),
                        'content': None,
                        'url': news.get('url', ''),
                        'source': news.get('source', '未知来源'),
                        'ctime': news.get('ctime', ''),
                        'picUrl': news.get('picUrl', ''),
                        'category': api_config['category']
                    }
                    if processed_news['title'].strip() and processed_news['url'].strip():
                        news_list.append(processed_news)
                        logger.debug(f"处理新闻: {processed_news['title']}")
                except Exception as e:
                    logger.error(f"处理单条新闻数据失败: {str(e)}")
                    continue
            logger.info(f"成功处理 {len(news_list)} 条新闻")
            return news_list
        else:
            logger.error(f"API请求失败，状态码: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"从API {api_config['name']} 获取新闻失败: {str(e)}")
        return []

def parse_datetime(time_str):
    """增强时间解析"""
    try:
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M') if time_str else datetime.now()
    except:
        return datetime.now()


def schedule_job(app):
    with app.app_context():
        try:
            logger.info("开始定时新闻爬取任务...")
            fetch_and_store_news()
        except Exception as e:
            logger.error(f"定时任务执行失败: {str(e)}")

def init_scheduler(app):
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=lambda: schedule_job(app),
        trigger='interval',
        hours=1,
        id='news_crawler_job'
    )
    scheduler.start()
    logger.info("已启动定时新闻爬取任务（每3小时一次）")
@news_crawler_bp.route('/fetch_news', methods=['GET'])
def fetch_news():
    """手动触发爬虫"""
    logger.info("手动触发爬虫")
    threading.Thread(target=fetch_and_store_news).start()  # 在新线程中运行爬虫
    return jsonify({"message": "爬虫已开始"}), 200


