
from flask import Blueprint, jsonify, request
from cache_manager import RedisManager
from typing import Any

middle_bp = Blueprint('middle', __name__, url_prefix='/middle')


class MiddleBlueprint:
    def __init__(self, redis_manager: RedisManager, data_manager: Any):
        self.redis_manager = redis_manager
        self.data_manager = data_manager
        self.bp = middle_bp
        self._register_routes()

    def _register_routes(self):
        @self.bp.route('', methods=['POST'])
        def get_middle_level():
            content_ids = request.json
            if not content_ids:
                return jsonify({"error": "No content IDs provided"})

            cache_key = f"middle_level_{hash(str(content_ids))}"
            cached_data = self.redis_manager.load_from_cache(cache_key)

            if cached_data:
                return jsonify(cached_data)

            try:
                data = self.data_manager.get_middle_level_data(content_ids)
                if data:
                    self.redis_manager.save_to_cache(cache_key, data)
                return jsonify(data or [])
            except Exception as e:
                return jsonify({"error": str(e)})