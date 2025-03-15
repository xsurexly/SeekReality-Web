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
        logging.FileHandler('news_crawler.log'),
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
    'whyta': {
        'name': 'whyta',
        'url': 'https://whyta.cn/api/tx/guonei',
        'key': '96f163cda80b',
        'params': {'num': '50'}
    },
    'other_api': {
        'name': 'other_api',
        'url': 'https://api.example.com/news',  # 示例API
        'key': 'your_api_key',
        'params': {'limit': 10}
    }
    # 可以添加更多的新闻API
}

#新闻类别设置
CATEGORIES = ['社会', '科技', '财经', '体育', '娱乐', '其它']

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/fake_news_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

# 这里使用随机值模拟检测结果，实际应该调用真实的检测API
def simulate_fake_news_detection(news_content):
    fake_score = random.uniform(0, 1)  # 生成0-1之间的随机分数
    return {
        'fake_score': fake_score,
    }

#获取新闻详细内容
def fetch_news_content(url):
    try:
        response = http.get(url, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 定义可能的内容选择器
            content_selectors = [
                {'class': 'article_content', 'id': 'js_article_content'},
                {'class': 'article'},
                {'id': 'chan_newsDetail'},
                {'class': 'content'},
                {'class': 'article-content'},
                {'class': 'news-content'}
            ]

            # 尝试不同的选择器
            article_content = None
            for selector in content_selectors:
                article_content = soup.find('div', selector)
                if article_content:
                    break

            if not article_content:
                article_content = soup.find(['article', 'main'])

            if article_content:
                # 清理内容
                for element in article_content.find_all(['script', 'style', 'iframe', 'form']):
                    element.decompose()

                paragraphs = []
                for p in article_content.find_all(['p', 'div', 'section']):
                    if any(cls in str(p.get('class', [])).lower() for cls in
                           ['nav', 'footer', 'copyright', 'related', 'recommend']):
                        continue

                    text = p.get_text().strip()
                    if text and len(text) > 10:
                        paragraphs.append(text)

                if paragraphs:
                    return "\\n".join(paragraphs)

            # 备选方法：提取body中的主要文本
            main_content = soup.find('body')
            if main_content:
                for element in main_content.find_all(['header', 'footer', 'nav', 'aside']):
                    element.decompose()

                texts = []
                for p in main_content.find_all(['p', 'div', 'section']):
                    text = p.get_text().strip()
                    if text and len(text) > 50:
                        texts.append(text)

                if texts:
                    return "\\n".join(texts)

        return None
    except Exception as e:
        logger.error(f"获取新闻内容失败: {url} - {str(e)}")
        return None

#从指定API获取新闻
def fetch_from_api(api_config):
    try:
        params = api_config['params'].copy()
        params['key'] = api_config['key']
        api_key = '302358f7f53a791a1369a9bf59b57a95'
        url=f'https://apis.tianapi.com/huabian/index?key={api_key}&num={5}'
        response = http.get(url)
        print(response.text)
        if response.status_code == 200:
            data = response.json()
            return data.get('result', {}).get('newslist', [])
        return []
    except Exception as e:
        logger.error(f"从API获取新闻失败 {api_config['name']}: {str(e)}")
        return []

def fetch_and_store_news():
    """获取并存储新闻"""
    logger.info("开始获取新闻...")
    app = create_app()

    with app.app_context():
        try:
            for api_name, api_config in NEWS_APIS.items():
                news_list = fetch_from_api(api_config)

                for news in news_list:
                    if not all(k in news for k in ['id', 'title']):
                        continue

                    existing_news = Newslist.query.get(news['id'])
                    if not existing_news:
                        try:
                            # 获取新闻详细内容
                            content = fetch_news_content(news['url']) if news.get('url') else None

                            # 进行虚假新闻检测
                            detection_result = simulate_fake_news_detection(content or news.get('description', ''))

                            new_news = Newslist(
                                id=news['id'],
                                title=news['title'],
                                ctime=datetime.strptime(news['ctime'],
                                                        '%Y-%m-%d %H:%M') if 'ctime' in news else None,
                                source=news.get('source', '未知来源'),
                                content=content,
                                picUrl=news.get('picUrl', ''),
                                url=news.get('url', ''),
                                fake_score=detection_result['fake_score'],
                                category=random.choice(CATEGORIES),
                                is_finished=False,
                                is_favorite=False,
                            )
                            db.session.add(new_news)
                            logger.info(f"添加新闻: {news['title']}")
                        except Exception as e:
                            logger.error(f"处理新闻失败: {str(e)}")
                            continue


            db.session.commit()
            logger.info("新闻更新完成")

        except Exception as e:
            logger.error(f"获取新闻失败: {str(e)}")
            db.session.rollback()

def run_scheduler():
    """运行定时任务"""
    schedule.every(6).hours.do(fetch_and_store_news)  # 每6小时更新一次

    # 立即运行一次
    fetch_and_store_news()

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()