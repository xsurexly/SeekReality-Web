from models import Newslist, Newsread, db, ReadHistory, DetectionHistory, Record
from flask import Blueprint, jsonify, request
from routes.overviewbp.cache_manager import CacheManager
from routes.overviewbp.visualization_manager import VisualizationManager
from sqlalchemy import func
from models import Newslist, Newsread, db
import copy
from routes.overviewdb.data_process.get_data_local import GetData
from routes.overviewdb.data_process.dataprocess import (
    Overview,
    flow_kew_words,
)

visualization_bp = Blueprint('visualization', __name__)
cache_manager = CacheManager()
vis_manager = VisualizationManager()


# 初始化数据库信息
def initialize_database():
    try:
        print("Loading database...")
        (
            ori_data,
            time,
            influence,
            users_info,
            forward_info,
            forward_users_info,
            emotion,
            topic,
            commentusers,
            fc2020,
            fcemotion,
        ) = GetData("../backend/routes/overviewdb/database").creat()

        print("Creating data copies...")
        return copy.deepcopy(ori_data), copy.deepcopy(time), copy.deepcopy(influence), copy.deepcopy(
            users_info), copy.deepcopy(forward_info), copy.deepcopy(forward_users_info), copy.deepcopy(
            emotion), copy.deepcopy(topic), copy.deepcopy(commentusers), copy.deepcopy(fc2020), copy.deepcopy(fcemotion)

    except Exception as e:
        import traceback
        print(f"Error during initialization: {e}")
        print(traceback.format_exc())
        return None, None, None, None, None, None, None, None, None, None, None


# 初始化数据
ori_data, time, influence, users_info, forward_info, forward_users_info, emotion, topic, commentusers, fc2020, fcemotion = initialize_database()
overview_data = Overview().creat(ori_data, users_info, time, topic)

# 缓存 overview 数据
overview_cache_key = 'overview_data_cache'
cache_manager.save_to_cache(overview_cache_key, overview_data, 3600)  # 缓存1小时


@visualization_bp.route('/news/source-distribution', methods=['GET'])
def get_news_source_distribution():
    """获取新闻来源分布"""
    try:
        cache_key = 'vis_news_source_dist'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        data = vis_manager.get_news_source_distribution()
        cache_manager.save_to_cache(cache_key, data, 3600)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/news/daily-trend', methods=['GET'])
def get_daily_news_trend():
    """获取每日新闻趋势"""
    try:
        days = request.args.get('days', default=30, type=int)
        cache_key = f'vis_daily_trend_{days}'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        data = vis_manager.get_daily_news_trend(days)
        cache_manager.save_to_cache(cache_key, data, 3600)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/news/fake-distribution', methods=['GET'])
def get_fake_news_distribution():
    """获取真假新闻分布"""
    try:
        cache_key = 'vis_fake_news_dist'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        data = vis_manager.get_fake_news_distribution()
        cache_manager.save_to_cache(cache_key, data, 3600)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/user/reading-habits', methods=['GET'])
def get_user_reading_habits():
    """获取用户阅读习惯"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        cache_key = f'vis_reading_habits_{username}'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        data = vis_manager.get_user_reading_habits(username)
        cache_manager.save_to_cache(cache_key, data, 3600)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/user/interests', methods=['GET'])
def get_user_interests():
    """获取用户兴趣分布"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        cache_key = f'vis_user_interests_{username}'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        data = vis_manager.get_user_interests(username)
        cache_manager.save_to_cache(cache_key, data, 3600)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/detection/statistics', methods=['GET'])
def get_detection_statistics():
    """获取检测统计数据"""
    try:
        cache_key = 'vis_detection_stats'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        data = vis_manager.get_detection_statistics()
        cache_manager.save_to_cache(cache_key, data, 3600)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/news/time-analysis', methods=['GET'])
def get_time_based_analysis():
    """获取基于时间的分析数据"""
    try:
        cache_key = 'vis_time_analysis'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        data = vis_manager.get_time_based_analysis()
        cache_manager.save_to_cache(cache_key, data, 3600)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/map2time', methods=['GET'])
def get_map_time_data():
    """获取地图时间数据"""
    try:
        cache_key = 'vis_map_time_data'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        if overview_data and len(overview_data) > 0 and overview_data[0]:
            result = overview_data[0]
            cache_manager.save_to_cache(cache_key, result, 3600)
            return jsonify(result)
        else:
            return jsonify({"error": "No data available"}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/time2topic', methods=['GET'])
def get_topic_time_data():
    """获取主题时间数据"""
    try:
        cache_key = 'vis_topic_time_data'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        if overview_data and len(overview_data) > 1 and overview_data[1]:
            result = overview_data[1]
            cache_manager.save_to_cache(cache_key, result, 3600)
            return jsonify(result)
        else:
            return jsonify({"error": "No data available"}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/theme-river', methods=['POST'])
def get_theme_river_data():
    """获取主题河流图数据"""
    try:
        content_ids = request.json
        if not content_ids:
            return jsonify({'error': 'Content IDs are required'}), 400

        cache_key = f'vis_theme_river_{"-".join(map(str, sorted(content_ids)))}'
        cached_data = cache_manager.load_from_cache(cache_key)

        if cached_data:
            return jsonify(cached_data)

        key_words = flow_kew_words(content_ids, ori_data, copy_topic)
        if key_words:
            cache_manager.save_to_cache(cache_key, key_words, 3600)
            return jsonify(key_words)
        else:
            return jsonify({"error": "No data available"}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visualization_bp.route('/get-user-data', methods=['GET'])
def get_user_data():
    userid = request.args.get('userid')
    username = request.args.get('username')

    if not username or not userid:
        return jsonify({'success': False, 'message': '缺少 userid 或 username'}), 400

    # 尝试从缓存中获取 overview 数据
    cached_overview_data = cache_manager.load_from_cache(overview_cache_key)
    if cached_overview_data:
        overview_data = cached_overview_data
    else:
        overview_data = Overview().creat(ori_data, users_info, time, topic)  # 如果缓存失效，重新加载

    # 获取阅读历史
    read_histories = ReadHistory.query.filter_by(username=username).all()
    reading_time_distribution = {
        '<1min': 0,
        '1-3min': 0,
        '3-5min': 0,
        '5-10min': 0,
        '>10min': 0
    }

    for history in read_histories:
        if history.read_time < 60:
            reading_time_distribution['<1min'] += 1
        elif 60 <= history.read_time < 180:
            reading_time_distribution['1-3min'] += 1
        elif 180 <= history.read_time < 300:
            reading_time_distribution['3-5min'] += 1
        elif 300 <= history.read_time < 600:
            reading_time_distribution['5-10min'] += 1
        else:
            reading_time_distribution['>10min'] += 1

    # 获取检测历史
    detection_histories = DetectionHistory.query.filter_by(userid=userid).all()
    detection_results = {
        '真实': 0,
        '虚假': 0
    }

    detection_records = Record.query.filter_by(username=username).all()

    for detection in detection_histories:
        if detection.result == 1:
            detection_results['真实'] += 1
        else:
            detection_results['虚假'] += 1

    for record in detection_records:
        if record.result == 1:
            detection_results['真实'] += 1
        else:
            detection_results['虚假'] += 1

    # 获取每日阅读量趋势
    volume_trend = get_daily_reading_volume(username, userid)

    # 获取今日统计数据
    today_stats = get_today_statistics(username, userid)

    return jsonify({
        'success': True,
        'data': {
            'readingTimeDistribution': reading_time_distribution,
            'volumeTrendDates': volume_trend['dates'],
            'volumeTrendValues': volume_trend['values'],
            'detectionResults': detection_results,
            'todayChecks': today_stats['today_checks'],
            'todayReads': today_stats['today_reads'],
            'todayTime': today_stats['today_time'],
            'riskCount': today_stats['risk_count']
        }
    }), 200


def get_daily_reading_volume(username, userid):
    """
    获取用户过去30天的每日阅读量趋势
    :param user_id: 用户ID
    :return: 一个字典，包含日期列表和对应的阅读量列表
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func

    # 计算过去30天的日期范围
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=29)

    # 查询过去30天每天的阅读量
    reading_volumes = db.session.query(
        func.date(ReadHistory.created_at).label('date'),
        func.count(ReadHistory.id).label('count')
    ).filter(
        ReadHistory.username == username,
        ReadHistory.created_at >= start_date
    ).group_by(
        func.date(ReadHistory.created_at)
    ).all()

    # 将查询结果转换为字典，便于后续处理
    volume_dict = {date.isoformat(): count for date, count in reading_volumes}

    # 生成过去30天的日期列表
    dates = [(today - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]

    # 按日期顺序填充结果，未有阅读记录的日期填充为0
    values = [volume_dict.get(date, 0) for date in dates]

    return {
        'dates': dates,
        'values': values
    }


def get_today_statistics(username, userid):
    """
    获取用户今天的统计数据
    :param user_id: 用户ID
    :return: 一个字典，包含今日检测次数、今日阅读量、今日阅读时长和高风险内容数量
    """
    from datetime import datetime, timedelta

    # 获取今天的开始和结束时间
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # 今日检测次数
    today_checks = DetectionHistory.query.filter(
        DetectionHistory.userid == userid,
        DetectionHistory.created_at >= today_start,
        DetectionHistory.created_at < today_end
    ).count()

    # 今日阅读量
    today_reads = ReadHistory.query.filter(
        ReadHistory.username == username,
        ReadHistory.created_at >= today_start,
        ReadHistory.created_at < today_end,
        ReadHistory.read_time > 0,
    ).count()

    # 今日阅读时长（单位：分钟）
    today_time = db.session.query(func.sum(ReadHistory.read_time)).filter(
        ReadHistory.username == username,
        ReadHistory.created_at >= today_start,
        ReadHistory.created_at < today_end
    ).scalar() or 0 // 60

    # 高风险内容数量
    risk_count = DetectionHistory.query.filter(
        DetectionHistory.userid == userid,
        DetectionHistory.result == '疑似虚假',
        DetectionHistory.created_at >= today_start,
        DetectionHistory.created_at < today_end
    ).count()

    return {
        'today_checks': today_checks,
        'today_reads': today_reads,
        'today_time': today_time,
        'risk_count': risk_count
    }