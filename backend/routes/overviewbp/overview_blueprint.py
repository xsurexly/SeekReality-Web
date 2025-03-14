# src/api/blueprints/overview_blueprint.py
from flask import Blueprint, jsonify, request
from cache_manager import RedisManager
from typing import Dict, Any

overview_bp = Blueprint('overview', __name__, url_prefix='/overview')


class OverviewBlueprint:
    def __init__(self, redis_manager: RedisManager, data_manager: Any):
        self.redis_manager = redis_manager
        self.data_manager = data_manager
        self.bp = overview_bp
        self._register_routes()

    def _register_routes(self):
        @self.bp.route('/<data_type>')
        def get_overview(data_type: str):
            cache_key = f"overview_{data_type}"
            cached_data = self.redis_manager.load_from_cache(cache_key)

            if cached_data:
                return jsonify(cached_data)

            try:
                if data_type == "time2topic":
                    data = self.data_manager.get_time2topic_data()
                elif data_type == "map2time":
                    data = self.data_manager.get_map2time_data()
                else:
                    return jsonify({"error": f"Invalid data type: {data_type}"})

                if data:
                    self.redis_manager.save_to_cache(cache_key, data)
                    return jsonify(data)
                return jsonify({"error": "No data available"})

            except Exception as e:
                return jsonify({"error": str(e)})

        @self.bp.route('/theme-river', methods=['POST'])
        def get_river_data():
            content_ids = request.json
            if not content_ids:
                return jsonify({"error": "No content IDs provided"})

            cache_key = f"river_data_{hash(str(content_ids))}"
            cached_data = self.redis_manager.load_from_cache(cache_key)

            if cached_data:
                return jsonify(cached_data)

            try:
                data = self.data_manager.get_river_data(content_ids)
                if data:
                    self.redis_manager.save_to_cache(cache_key, data)
                return jsonify(data or {})
            except Exception as e:
                return jsonify({"error": str(e)})