from flask import Blueprint, jsonify
from cache_manager import RedisManager
from typing import Any

tree_bp = Blueprint('tree', __name__, url_prefix='/treemap')


class TreeBlueprint:
    def __init__(self, redis_manager: RedisManager, data_manager: Any):
        self.redis_manager = redis_manager
        self.data_manager = data_manager
        self.bp = tree_bp
        self._register_routes()

    def _register_routes(self):
        @self.bp.route('/<content_id>')
        def get_tree_map(content_id: str):
            cache_key = f"tree_map_{content_id}"
            cached_data = self.redis_manager.load_from_cache(cache_key)

            if cached_data:
                return jsonify(cached_data)

            try:
                data = self.data_manager.get_tree_map_data(content_id)
                if data:
                    self.redis_manager.save_to_cache(cache_key, data)
                return jsonify(data or [])
            except Exception as e:
                return jsonify({"error": str(e)})