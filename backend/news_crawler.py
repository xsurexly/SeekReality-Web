import sys
import os
import random
from datetime import datetime, timedelta
import http.client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Newslist
import requests
from bs4 import BeautifulSoup
import logging
import schedule
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_crawler.log', encoding='utf-8'),
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
    '新浪新闻': [
        {'attrs': {'class': ['article-content', 'article-main']}},
        {'attrs': {'id': ['article', 'artibody']}}
    ],
    '腾讯新闻': [
        {'attrs': {'class': ['content-article', 'article-content']},
         'tags': ['div']}
    ],
    '新华网': [
        {'attrs': {'class': ['main-article', 'article']},
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

def fetch_news_content(url,source):

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = http.get(url, timeout=15, headers=headers)

        # 设置合适的编码
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 移除干扰性标签
            for tag in soup(['script', 'style', 'iframe', 'form', 'input', 'button',
                             'meta', 'link', 'noscript', 'svg', 'canvas']):
                tag.decompose()

                # 根据来源获取特定选择器 + 默认选择器
                source_selectors = CONTENT_SELECTORS_BY_SOURCE.get(source, [])
                content_selectors = source_selectors + DEFAULT_CONTENT_SELECTORS

                # 原有内容定位逻辑，使用新的选择器组合
                main_content = None
                for selector in content_selectors:
                    attrs = selector.get('attrs')
                    for key, value in attrs.items():
                        if isinstance(value, list):
                            for v in value:
                                main_content = soup.find(['article', 'div', 'section'], {key: v})
                                if main_content:
                                    break
                        else:
                            main_content = soup.find(['article', 'div', 'section'], {key: value})
                        if main_content:
                            break
                    if main_content:
                        break

            # 若未找到主要内容区域，则选取文本最长的容器作为备选
            if not main_content:
                candidates = soup.find_all(['div', 'article', 'section'])
                if candidates:
                    main_content = max(candidates, key=lambda tag: len(tag.get_text().strip()))

            # 开始提取内容
            if main_content:
                content_parts = []

                # 若未提取到足够内容，则直接使用主要区域的全部 HTML
                if not content_parts:
                    content_parts.append(main_content.decode_contents())

                final_content = '\n'.join(content_parts)

                logger.info(f"成功提取新闻内容，长度: {len(final_content)} 字符")
                logger.debug(f"新闻内容预览: {final_content[:200]}...")
                return final_content

            logger.warning(f"未能找到有效的新闻内容: {url}")
            return None

        else:
            logger.error(f"请求失败，状态码: {response.status_code}，URL: {url}")
            return None

    except Exception as e:
        logger.error(f"获取新闻内容失败: {url} - {str(e)}")
        return None

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

def fetch_and_store_news():
    """获取并存储新闻"""
    logger.info("开始获取新闻...")
    app = create_app()
    with app.app_context():
        try:
            total_added = 0
            total_failed = 0
            for api_name, api_config in NEWS_APIS.items():
                logger.info(f"正在获取 {api_config['category']} 类新闻...")
                news_list = fetch_from_api(api_config)
                logger.info(f"从 {api_name} 获取到 {len(news_list)} 条新闻")
                for news in news_list:
                    try:
                        if not news.get('title'):
                            logger.warning("跳过无标题新闻")
                            continue
                        news_id = news.get('id') or str(
                            hash(f"{news['title']}_{news.get('ctime', datetime.now().strftime('%Y-%m-%d %H:%M'))}")
                        )
                        existing_news = Newslist.query.filter_by(id=news_id).first()
                        if existing_news:
                            logger.info(f"新闻已存在: {news['title']}")
                            continue
                        content = news.get('content', '')
                        if not content and news.get('url'):
                            logger.info(f"尝试获取新闻完整内容: {news['url']}")
                            content = fetch_news_content(news['url'],news['source'])
                            if content:
                                logger.info(f"成功获取新闻内容，长度: {len(content)}")
                            else:
                                logger.warning(f"无法获取新闻内容: {news['url']}")

                        detection_result = simulate_fake_news_detection(content)
                        try:
                            if news.get('ctime'):
                                news_time = datetime.strptime(news['ctime'], '%Y-%m-%d %H:%M')
                            else:
                                news_time = datetime.now()
                        except ValueError as e:
                            logger.warning(f"时间格式错误 '{news.get('ctime')}': {str(e)}")
                            news_time = datetime.now()

                        new_news = Newslist(
                            id=news_id,
                            title=news['title'],
                            ctime=news_time,
                            source=news.get('source', '未知来源'),
                            content=content,
                            picUrl=news.get('picUrl', ''),
                            url=news.get('url', ''),
                            fake_score=detection_result['fake_score'],
                            category=api_config['category'],
                        )
                        db.session.add(new_news)
                        db.session.commit()
                        total_added += 1
                        logger.info(f"成功添加新闻: [{api_config['category']}] {news['title']}")
                    except Exception as e:
                        total_failed += 1
                        logger.error(f"处理新闻失败: {str(e)}")
                        db.session.rollback()
                        continue
            logger.info(f"新闻更新完成: 成功添加 {total_added} 条，失败 {total_failed} 条")
        except Exception as e:
            logger.error(f"获取新闻总体失败: {str(e)}")
            db.session.rollback()
        finally:
            db.session.close()

def run_scheduler():
    """运行定时任务，每6小时更新一次新闻"""
    schedule.every(6).hours.do(fetch_and_store_news)
    fetch_and_store_news()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
