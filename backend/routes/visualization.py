from flask import Blueprint, jsonify, request
from routes.overviewbp.cache_manager import CacheManager
from routes.overviewbp.visualization_manager import VisualizationManager
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from models import Newslist, Newsread, db
import json
import copy
import os
from pathlib import Path
from routes.overviewdb.data_process.get_data_local import GetData
from routes.overviewdb.data_process.dataprocess import (
    Overview,
    flow_kew_words,
)

visualization_bp = Blueprint('visualization', __name__)
cache_manager = CacheManager()
vis_manager = VisualizationManager()



try:
    # 初始化读取数据库信息
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
    ) = GetData("E:/softwareInno/Defeat-All-Fake/backend/routes/overviewdb/database").creat()

    # 创建数据副本
    print("Creating data copies...")
    (
        copy_ori_data,
        copy_time,
        copy_influence,
        copy_users_info,
        copy_forward_info,
        copy_forward_users_info,
        copy_emotion,
        copy_topic,
        copy_commentusers,
        copy_fc2020,
        copy_fcemotion,
    ) = (
        copy.deepcopy(ori_data),
        copy.deepcopy(time),
        copy.deepcopy(influence),
        copy.deepcopy(users_info),
        copy.deepcopy(forward_info),
        copy.deepcopy(forward_users_info),
        copy.deepcopy(emotion),
        copy.deepcopy(topic),
        copy.deepcopy(commentusers),
        copy.deepcopy(fc2020),
        copy.deepcopy(fcemotion),
    )

    # 初始化数据
    print("Initializing overview data...")
    overview_data = Overview().creat(ori_data, users_info, time, topic)

    if not overview_data or len(overview_data) < 2:
        print("Warning: overview_data is not properly initialized")
        overview_data = [None, None]
    else:
        print("Overview data initialized successfully")
        print(f"Map data type: {type(overview_data[0])}")
        print(f"Topic data type: {type(overview_data[1])}")

except Exception as e:
    import traceback
    print(f"Error during initialization: {e}")
    print(traceback.format_exc())
    ori_data = []
    time = {}
    influence = {}
    users_info = {}
    forward_info = {}
    forward_users_info = {}
    emotion = {}
    topic = {}
    commentusers = {}
    fc2020 = {}
    fcemotion = {}
    overview_data = [None, None]

@visualization_bp.route('/news/source-distribution', methods=['GET'])
def get_news_source_distribution():
    """获取新闻来源分布"""
    try:
        # 尝试从缓存获取数据
        cache_key = 'vis_news_source_dist'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            return jsonify(cached_data)

        # 从数据库获取数据
        data = vis_manager.get_news_source_distribution()
        
        # 保存到缓存，设置过期时间为1小时
        cache_manager.save_to_cache(cache_key, data, 3600)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/news/daily-trend', methods=['GET'])
def get_daily_news_trend():
    """获取每日新闻趋势"""
    try:
        days = request.args.get('days', default=30, type=int)
        
        # 尝试从缓存获取数据
        cache_key = f'vis_daily_trend_{days}'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            return jsonify(cached_data)

        # 从数据库获取数据
        data = vis_manager.get_daily_news_trend(days)
        
        # 保存到缓存，设置过期时间为1小时
        cache_manager.save_to_cache(cache_key, data, 3600)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/news/fake-distribution', methods=['GET'])
def get_fake_news_distribution():
    """获取真假新闻分布"""
    try:
        # 尝试从缓存获取数据
        cache_key = 'vis_fake_news_dist'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            return jsonify(cached_data)

        # 从数据库获取数据
        data = vis_manager.get_fake_news_distribution()
        
        # 保存到缓存，设置过期时间为1小时
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

        # 尝试从缓存获取数据
        cache_key = f'vis_reading_habits_{username}'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            return jsonify(cached_data)

        # 从数据库获取数据
        data = vis_manager.get_user_reading_habits(username)
        
        # 保存到缓存，设置过期时间为1小时
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

        # 尝试从缓存获取数据
        cache_key = f'vis_user_interests_{username}'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            return jsonify(cached_data)

        # 从数据库获取数据
        data = vis_manager.get_user_interests(username)
        
        # 保存到缓存，设置过期时间为1小时
        cache_manager.save_to_cache(cache_key, data, 3600)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/detection/statistics', methods=['GET'])
def get_detection_statistics():
    """获取检测统计数据"""
    try:
        # 尝试从缓存获取数据
        cache_key = 'vis_detection_stats'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            return jsonify(cached_data)

        # 从数据库获取数据
        data = vis_manager.get_detection_statistics()
        
        # 保存到缓存，设置过期时间为1小时
        cache_manager.save_to_cache(cache_key, data, 3600)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/news/time-analysis', methods=['GET'])
def get_time_based_analysis():
    """获取基于时间的分析数据"""
    try:
        # 尝试从缓存获取数据
        cache_key = 'vis_time_analysis'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            return jsonify(cached_data)

        # 从数据库获取数据
        data = vis_manager.get_time_based_analysis()
        
        # 保存到缓存，设置过期时间为1小时
        cache_manager.save_to_cache(cache_key, data, 3600)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/map2time', methods=['GET'])
def get_map_time_data():
    """获取地图时间数据"""
    try:
        # 尝试从缓存获取数据
        cache_key = 'vis_map_time_data'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            print("Returning cached map data")
            return jsonify(cached_data)

        # 从本地数据获取
        if overview_data and len(overview_data) > 0 and overview_data[0]:
            print("Processing map data from overview_data")
            result = overview_data[0]
            # 保存到缓存
            cache_manager.save_to_cache(cache_key, result, 3600)
            return jsonify(result)
        else:
            print("No map data available")
            return jsonify({"error": "No data available"}), 404

    except Exception as e:
        print(f"Error getting map time data: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/time2topic', methods=['GET'])
def get_topic_time_data():
    """获取主题时间数据"""
    try:
        # 尝试从缓存获取数据
        cache_key = 'vis_topic_time_data'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            print("Returning cached topic data")
            return jsonify(cached_data)

        # 从本地数据获取
        if overview_data and len(overview_data) > 1 and overview_data[1]:
            print("Processing topic data from overview_data")
            result = overview_data[1]
            # 保存到缓存
            cache_manager.save_to_cache(cache_key, result, 3600)
            return jsonify(result)
        else:
            print("No topic data available")
            return jsonify({"error": "No data available"}), 404

    except Exception as e:
        print(f"Error getting topic time data: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/theme-river', methods=['POST'])
def get_theme_river_data():
    """获取主题河流图数据"""
    try:
        content_ids = request.json
        if not content_ids:
            return jsonify({'error': 'Content IDs are required'}), 400

        # 尝试从缓存获取数据
        cache_key = f'vis_theme_river_{"-".join(map(str, sorted(content_ids)))}'
        cached_data = cache_manager.load_from_cache(cache_key)
        
        if cached_data:
            return jsonify(cached_data)

        # 从本地数据获取
        key_words = flow_kew_words(content_ids, ori_data, copy_topic)
        if key_words:
            # 保存到缓存
            cache_manager.save_to_cache(cache_key, key_words, 3600)
            return jsonify(key_words)
        else:
            return jsonify({"error": "No data available"}), 404

    except Exception as e:
        print(f"Error getting theme river data: {e}")
        return jsonify({'error': str(e)}), 500
