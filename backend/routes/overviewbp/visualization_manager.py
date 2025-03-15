from typing import Dict, List, Any
from models import Newslist, Newsread, User, db
from sqlalchemy import func, and_, extract, text
from datetime import datetime, timedelta
#import pandas as pd
#import jieba
#from collections import Counter

class VisualizationManager:
    def __init__(self):
        pass

    def get_news_source_distribution(self) -> Dict[str, Any]:
        """获取新闻来源分布数据"""
        try:
            # 查询每个来源的新闻数量
            source_counts = db.session.query(
                Newslist.source,
                func.count(Newslist.id).label('count')
            ).group_by(Newslist.source).all()

            # 格式化数据
            data = {
                'sources': [item[0] for item in source_counts if item[0]],
                'counts': [item[1] for item in source_counts if item[0]]
            }
            return data
        except Exception as e:
            print(f"Error getting news source distribution: {e}")
            return {'sources': [], 'counts': []}

    def get_daily_news_trend(self, days: int = 30) -> Dict[str, Any]:
        """获取每日新闻趋势数据"""
        try:
            # 计算起始日期
            start_date = datetime.now() - timedelta(days=days)

            # 查询每天的新闻数量
            daily_counts = db.session.query(
                func.date(Newslist.ctime).label('date'),
                func.count(Newslist.id).label('count')
            ).filter(
                Newslist.ctime >= start_date
            ).group_by(
                func.date(Newslist.ctime)
            ).order_by(
                func.date(Newslist.ctime)
            ).all()

            # 格式化数据
            data = {
                'dates': [item[0].strftime('%Y-%m-%d') for item in daily_counts],
                'counts': [item[1] for item in daily_counts]
            }
            return data
        except Exception as e:
            print(f"Error getting daily news trend: {e}")
            return {'dates': [], 'counts': []}

    def get_fake_news_distribution(self) -> Dict[str, Any]:
        """获取真假新闻分布数据"""
        try:
            # 定义真假新闻的阈值
            threshold = 0.5

            # 查询真假新闻数量
            fake_count = db.session.query(func.count(Newslist.id)).filter(
                Newslist.fake_score >= threshold
            ).scalar()

            real_count = db.session.query(func.count(Newslist.id)).filter(
                Newslist.fake_score < threshold
            ).scalar()

            data = {
                'labels': ['真实新闻', '虚假新闻'],
                'values': [real_count, fake_count]
            }
            return data
        except Exception as e:
            print(f"Error getting fake news distribution: {e}")
            return {'labels': [], 'values': []}

    def get_user_reading_habits(self, username: str) -> Dict[str, Any]:
        """获取用户阅读习惯数据"""
        try:
            # 查询用户最近30天的阅读记录
            thirty_days_ago = datetime.now() - timedelta(days=30)
            reading_records = db.session.query(
                func.date(Newsread.read_time).label('date'),
                func.count(Newsread.id).label('count')
            ).filter(
                Newsread.username == username,
                Newsread.read_time >= thirty_days_ago
            ).group_by(
                func.date(Newsread.read_time)
            ).order_by(
                func.date(Newsread.read_time)
            ).all()

            # 格式化数据
            data = {
                'dates': [record[0].strftime('%Y-%m-%d') for record in reading_records],
                'counts': [record[1] for record in reading_records]
            }
            return data
        except Exception as e:
            print(f"Error getting user reading habits: {e}")
            return {'dates': [], 'counts': []}

    def get_user_interests(self, username: str) -> Dict[str, Any]:
        """获取用户兴趣分布数据"""
        try:
            # 查询用户阅读的新闻来源分布
            source_counts = db.session.query(
                Newslist.source,
                func.count(Newsread.id).label('count')
            ).join(
                Newsread, Newsread.news_id == Newslist.id
            ).filter(
                Newsread.username == username
            ).group_by(
                Newslist.source
            ).all()

            # 格式化数据
            data = {
                'sources': [item[0] for item in source_counts if item[0]],
                'counts': [item[1] for item in source_counts if item[0]]
            }
            return data
        except Exception as e:
            print(f"Error getting user interests: {e}")
            return {'sources': [], 'counts': []}

    def get_detection_statistics(self) -> Dict[str, Any]:
        """获取新闻检测统计数据"""
        try:
            # 计算总检测数量
            total_detections = db.session.query(func.count(Newslist.id)).filter(
                Newslist.fake_score.isnot(None)
            ).scalar()

            # 计算各个置信度区间的数量
            confidence_ranges = [
                (0, 0.2, '极低'),
                (0.2, 0.4, '低'),
                (0.4, 0.6, '中等'),
                (0.6, 0.8, '高'),
                (0.8, 1.0, '极高')
            ]

            confidence_counts = []
            for start, end, label in confidence_ranges:
                count = db.session.query(func.count(Newslist.id)).filter(
                    Newslist.fake_score.between(start, end)
                ).scalar()
                confidence_counts.append({
                    'range': label,
                    'count': count
                })

            data = {
                'total_detections': total_detections,
                'confidence_distribution': confidence_counts
            }
            return data
        except Exception as e:
            print(f"Error getting detection statistics: {e}")
            return {'total_detections': 0, 'confidence_distribution': []}

    def get_time_based_analysis(self) -> Dict[str, Any]:
        """获取基于时间的分析数据"""
        try:
            # 获取每小时的新闻发布数量
            hourly_counts = db.session.query(
                extract('hour', Newslist.ctime).label('hour'),
                func.count(Newslist.id).label('count')
            ).group_by(
                extract('hour', Newslist.ctime)
            ).order_by(
                extract('hour', Newslist.ctime)
            ).all()

            # 获取每周几的新闻发布数量
            weekday_counts = db.session.query(
                extract('dow', Newslist.ctime).label('weekday'),
                func.count(Newslist.id).label('count')
            ).group_by(
                extract('dow', Newslist.ctime)
            ).order_by(
                extract('dow', Newslist.ctime)
            ).all()

            # 格式化数据
            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            data = {
                'hourly': {
                    'hours': [item[0] for item in hourly_counts],
                    'counts': [item[1] for item in hourly_counts]
                },
                'weekly': {
                    'days': weekdays,
                    'counts': [0] * 7  # 初始化为0
                }
            }

            # 填充每周几的数据
            for weekday, count in weekday_counts:
                # PostgreSQL的星期天是0，其他天是1-6
                # 转换为我们需要的格式（0是周一，6是周日）
                idx = (weekday + 6) % 7
                data['weekly']['counts'][idx] = count

            return data
        except Exception as e:
            print(f"Error getting time-based analysis: {e}")
            return {
                'hourly': {'hours': [], 'counts': []},
                'weekly': {'days': [], 'counts': []}
            }

    def get_map_time_data(self) -> Dict[str, Any]:
        """获取地图时间数据"""
        try:
            # 获取最近30天的新闻地理分布数据
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # 按地区和时间统计新闻数量
            news_stats = db.session.query(
                Newslist.region,
                func.date(Newslist.ctime).label('date'),
                func.count(Newslist.id).label('count')
            ).filter(
                Newslist.ctime >= thirty_days_ago,
                Newslist.region.isnot(None)
            ).group_by(
                Newslist.region,
                func.date(Newslist.ctime)
            ).all()

            # 格式化数据
            result = {}
            for region, date, count in news_stats:
                if region not in result:
                    result[region] = []
                result[region].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'count': count
                })
            return result
        except Exception as e:
            print(f"Error getting map time data: {e}")
            return {}

    def get_topic_time_data(self) -> Dict[str, Any]:
        """获取主题时间数据"""
        try:
            # 获取最近30天的新闻主题分布数据
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # 按主题和时间统计新闻数量
            topic_stats = db.session.query(
                Newslist.topic,
                func.date(Newslist.ctime).label('date'),
                func.count(Newslist.id).label('count')
            ).filter(
                Newslist.ctime >= thirty_days_ago,
                Newslist.topic.isnot(None)
            ).group_by(
                Newslist.topic,
                func.date(Newslist.ctime)
            ).all()

            # 格式化数据
            result = {}
            for topic, date, count in topic_stats:
                if topic not in result:
                    result[topic] = []
                result[topic].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'count': count
                })
            return result
        except Exception as e:
            print(f"Error getting topic time data: {e}")
            return {}

    def get_theme_river_data(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """获取主题河流图数据"""
        try:
            # 获取最近30天的关键词趋势数据
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            result = []
            for keyword in keywords:
                # 按日期统计包含关键词的新闻数量
                keyword_stats = db.session.query(
                    func.date(Newslist.ctime).label('date'),
                    func.count(Newslist.id).label('count')
                ).filter(
                    Newslist.ctime >= thirty_days_ago,
                    Newslist.content.ilike(f'%{keyword}%')
                ).group_by(
                    func.date(Newslist.ctime)
                ).all()

                # 格式化数据
                for date, count in keyword_stats:
                    result.append({
                        'keyword': keyword,
                        'date': date.strftime('%Y-%m-%d'),
                        'count': count
                    })
            return result
        except Exception as e:
            print(f"Error getting theme river data: {e}")
            return []

    def get_middle_data(self, news_ids: List[int]) -> List[Dict[str, Any]]:
        """获取中间数据"""
        try:
            # 获取指定新闻的详细信息
            news_items = Newslist.query.filter(Newslist.id.in_(news_ids)).all()
            
            # 格式化数据
            result = [{
                'id': news.id,
                'title': news.title,
                'content': news.content,
                'source': news.source,
                'url': news.url,
                'ctime': news.ctime.strftime('%Y-%m-%d %H:%M:%S') if news.ctime else None,
                'fake_score': news.fake_score,
                'topic': news.topic,
                'region': news.region
            } for news in news_items]
            return result
        except Exception as e:
            print(f"Error getting middle data: {e}")
            return []

    def get_treemap_data(self, news_id: int) -> Dict[str, Any]:
        """获取树图数据"""
        try:
            # 获取指定新闻的详细信息
            news = Newslist.query.get(news_id)
            if not news:
                return {}

            # 获取相关新闻（同一主题或来源的新闻）
            related_news = Newslist.query.filter(
                Newslist.id != news_id,
                (Newslist.topic == news.topic) | (Newslist.source == news.source)
            ).limit(10).all()

            # 构建树图数据结构
            result = {
                'name': news.title,
                'children': [
                    {
                        'name': '相关新闻',
                        'children': [{
                            'name': related.title,
                            'value': related.fake_score or 0,
                            'id': related.id
                        } for related in related_news]
                    },
                    {
                        'name': '来源分析',
                        'children': [
                            {'name': '可信度', 'value': 1 - (news.fake_score or 0)},
                            {'name': '来源', 'value': 1, 'source': news.source}
                        ]
                    }
                ]
            }
            return result
        except Exception as e:
            print(f"Error getting treemap data: {e}")
            return {} 