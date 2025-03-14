import json
from typing import Any, Optional
from datetime import timedelta
import logging
from threading import Lock
import time

class CacheManager:
    _instance = None
    _lock = Lock()
    _memory_cache = {}
    _memory_cache_ttl = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            logging.info("In-memory cache initialized")

    def save_to_cache(self, key: str, data: Any, expire_time: int = 3600) -> bool:
        """
        将数据保存到内存缓存
        :param key: 缓存键
        :param data: 要缓存的数据
        :param expire_time: 过期时间（秒），默认1小时
        :return: 是否成功保存
        """
        try:
            with self._lock:
                self._memory_cache[key] = data
                self._memory_cache_ttl[key] = time.time() + expire_time
            return True
        except Exception as e:
            logging.error(f"Error saving data to cache: {e}")
            return False

    def load_from_cache(self, key: str) -> Optional[Any]:
        """
        从内存缓存加载数据
        :param key: 缓存键
        :return: 缓存的数据，如果不存在则返回None
        """
        try:
            with self._lock:
                if key in self._memory_cache:
                    if time.time() < self._memory_cache_ttl[key]:
                        return self._memory_cache[key]
                    else:
                        del self._memory_cache[key]
                        del self._memory_cache_ttl[key]
                return None
        except Exception as e:
            logging.error(f"Error loading data from cache: {e}")
            return None

    def delete_cache(self, key: str) -> bool:
        """
        删除指定的缓存
        :param key: 缓存键
        :return: 是否成功删除
        """
        try:
            with self._lock:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    del self._memory_cache_ttl[key]
                    return True
                return False
        except Exception as e:
            logging.error(f"Error deleting cache: {e}")
            return False

    def clear_all_cache(self) -> bool:
        """
        清除所有缓存
        :return: 是否成功清除
        """
        try:
            with self._lock:
                self._memory_cache.clear()
                self._memory_cache_ttl.clear()
            return True
        except Exception as e:
            logging.error(f"Error clearing cache: {e}")
            return False

    def get_cache_with_pattern(self, pattern: str) -> dict:
        """
        使用模式获取缓存（简单的字符串匹配）
        :param pattern: 缓存键模式
        :return: 匹配的所有缓存数据
        """
        try:
            result = {}
            with self._lock:
                current_time = time.time()
                for key in list(self._memory_cache.keys()):
                    if pattern in key and current_time < self._memory_cache_ttl[key]:
                        result[key] = self._memory_cache[key]
            return result
        except Exception as e:
            logging.error(f"Error getting cache with pattern: {e}")
            return {}

    def set_cache_with_ttl(self, key: str, data: Any, ttl: timedelta) -> bool:
        """
        设置带有TTL的缓存
        :param key: 缓存键
        :param data: 要缓存的数据
        :param ttl: 过期时间（timedelta对象）
        :return: 是否成功设置
        """
        try:
            return self.save_to_cache(key, data, int(ttl.total_seconds()))
        except Exception as e:
            logging.error(f"Error setting cache with TTL: {e}")
            return False

    def get_cache_ttl(self, key: str) -> Optional[int]:
        """
        获取缓存的剩余TTL
        :param key: 缓存键
        :return: 剩余时间（秒），如果key不存在则返回None
        """
        try:
            with self._lock:
                if key in self._memory_cache_ttl:
                    remaining = self._memory_cache_ttl[key] - time.time()
                    return int(remaining) if remaining > 0 else None
                return None
        except Exception as e:
            logging.error(f"Error getting cache TTL: {e}")
            return None