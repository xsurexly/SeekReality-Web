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
        logging.FileHandler('news_crawler.log', encoding='utf-8'),  # 添加 encoding='utf-8'
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
    """获取新闻详细内容，增强版"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = http.get(url, timeout=15, headers=headers)

        # 尝试检测并设置正确的编码
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. 预处理：移除干扰元素
            for element in soup.find_all(['script', 'style', 'iframe', 'form', 'input', 'button',
                                          'meta', 'link', 'noscript', 'svg', 'canvas']):
                element.decompose()

            # 2. 增强的内容选择器
            content_selectors = [
                # 常见的文章内容容器
                {'class_': ['article-content', 'article_content', 'article-detail', 'article_detail']},
                {'class_': ['news-content', 'news_content', 'news-detail', 'news_detail']},
                {'class_': ['content-main', 'main-content', 'main_content', 'mainContent']},
                {'class_': ['detail-content', 'detail_content', 'detailContent']},
                {'id': ['articleContent', 'article-content', 'article_content']},
                {'id': ['content', 'main-content', 'mainContent']},
                # 特定网站的内容容器
                {'class_': ['post-content', 'entry-content', 'single-content']},
                {'class_': ['story-content', 'story_content', 'storyContent']},
                {'class_': ['text-content', 'text_content', 'textContent']},
                # 通用内容容器
                {'role': 'article'},
                {'role': 'main'},
                {'itemprop': 'articleBody'}
            ]

            # 3. 查找主要内容区域
            main_content = None
            article_title = None

            # 3.1 尝试找到文章标题
            title_selectors = [
                {'class_': ['article-title', 'news-title', 'post-title', 'title']},
                {'id': ['article-title', 'news-title', 'post-title', 'title']},
                {'itemprop': 'headline'}
            ]

            for selector in title_selectors:
                title_elem = soup.find(['h1', 'h2'], selector)
                if title_elem:
                    article_title = title_elem.get_text().strip()
                    break

            # 3.2 查找主要内容区域
            for selector in content_selectors:
                for key, value in selector.items():
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

            # 4. 如果没找到主要内容区域，使用备选方案
            if not main_content:
                # 4.1 尝试找到最长的文本容器
                text_blocks = soup.find_all(['div', 'article', 'section'])
                if text_blocks:
                    main_content = max(text_blocks, key=lambda x: len(x.get_text().strip()))

            if main_content:
                # 5. 提取并清理内容
                content_parts = []

                # 5.1 添加标题（如果找到）
                if article_title:
                    content_parts.append(f"标题：{article_title}\n")

                # 5.2 提取正文内容
                for element in main_content.find_all(['p', 'div', 'section', 'h2', 'h3', 'h4']):
                    # 过滤无关内容
                    if any(cls in str(element.get('class', [])).lower() for cls in
                           ['ad', 'advertisement', 'recommend', 'related', 'share', 'social',
                            'comment', 'copyright', 'disclaimer', 'footer', 'header']):
                        continue

                    text = element.get_text().strip()

                    # 内容质量检查
                    if text and len(text) > 15:  # 确保段落有足够的长度
                        # 过滤常见的干扰文本
                        if not any(keyword in text.lower() for keyword in
                                   ['版权所有', '未经授权', '相关阅读', '点击查看', '广告',
                                    '推荐阅读', '责任编辑', '关注我们']):
                            content_parts.append(text)

                if content_parts:
                    # 6. 合并内容并进行最终清理
                    full_content = '\n'.join(content_parts)

                    # 6.1 清理特殊字符和多余空白
                    full_content = ' '.join(full_content.split())

                    # 6.2 清理重复内容
                    seen_paragraphs = set()
                    unique_paragraphs = []
                    for paragraph in full_content.split('\n'):
                        if paragraph not in seen_paragraphs:
                            seen_paragraphs.add(paragraph)
                            unique_paragraphs.append(paragraph)

                    # 6.3 重新组合内容
                    final_content = '\n'.join(unique_paragraphs)

                    # 7. 调试输出
                    logger.info(f"成功提取新闻内容，长度: {len(final_content)} 字符")
                    logger.debug(f"新闻内容预览: {final_content[:200]}...")

                    return final_content

            logger.warning(f"未能找到有效的新闻内容: {url}")
            return None

    except Exception as e:
        logger.error(f"获取新闻内容失败: {url} - {str(e)}")
        return None

#从指定API获取新闻
def fetch_from_api(api_config):
    """从指定API获取新闻"""
    try:
        # 构建请求URL和参数
        url = f"{api_config['url']}?key={api_config['key']}&num={api_config['params']['num']}"
        logger.info(f"正在请求API: {url}")

        response = http.get(url)
        logger.info(f"API响应状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # 检查API返回状态
            if data.get('code') != 200:
                logger.error(f"API返回错误: {data.get('msg')}")
                return []

            # 获取新闻列表
            raw_news_list = data.get('result', {}).get('newslist', [])
            logger.info(f"获取到 {len(raw_news_list)} 条原始新闻")

            news_list = []
            for news in raw_news_list:
                try:
                    # 统一新闻数据格式
                    processed_news = {
                        'id': news.get('id', ''),
                        'title': news.get('title', ''),
                        'content': news.get('description', ''),
                        'url': news.get('url', ''),
                        'source': news.get('source', '未知来源'),
                        'ctime': news.get('ctime', ''),
                        'picUrl': news.get('picUrl', ''),
                        'category': api_config['category']
                    }

                    # 确保必要字段存在且不为空
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
                        # 确保必要字段存在
                        if not news.get('title'):
                            logger.warning("跳过无标题新闻")
                            continue

                        # 使用API返回的ID或生成新的ID
                        news_id = news.get('id') or str(
                            hash(f"{news['title']}_{news.get('ctime', datetime.now().strftime('%Y-%m-%d %H:%M'))}"))

                        # 检查新闻是否已存在
                        existing_news = Newslist.query.filter_by(id=news_id).first()
                        if existing_news:
                            logger.info(f"新闻已存在: {news['title']}")
                            continue

                        # 获取完整新闻内容
                        content = news.get('content', '')
                        if not content and news.get('url'):
                            logger.info(f"尝试获取新闻完整内容: {news['url']}")
                            content = fetch_news_content(news['url'])
                            if content:
                                logger.info(f"成功获取新闻内容，长度: {len(content)}")
                            else:
                                logger.warning(f"无法获取新闻内容: {news['url']}")
                                content = news.get('description', '') or news.get('title', '')

                        # 进行虚假新闻检测
                        detection_result = simulate_fake_news_detection(content)

                        # 处理时间格式
                        try:
                            if news.get('ctime'):
                                news_time = datetime.strptime(news['ctime'], '%Y-%m-%d %H:%M')
                            else:
                                news_time = datetime.now()
                        except ValueError as e:
                            logger.warning(f"时间格式错误 '{news.get('ctime')}': {str(e)}")
                            news_time = datetime.now()

                        # 创建新闻对象
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

                        # 添加到数据库会话
                        db.session.add(new_news)
                        # 立即提交每条新闻，避免全部失败
                        db.session.commit()

                        total_added += 1
                        logger.info(f"成功添加新闻: [{api_config['category']}] {news['title']}")

                    except Exception as e:
                        total_failed += 1
                        logger.error(f"处理新闻失败: {str(e)}")
                        db.session.rollback()  # 回滚当前新闻的事务
                        continue

            logger.info(f"新闻更新完成: 成功添加 {total_added} 条，失败 {total_failed} 条")

        except Exception as e:
            logger.error(f"获取新闻总体失败: {str(e)}")
            db.session.rollback()
        finally:
            db.session.close()  # 确保会话被正确关闭

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