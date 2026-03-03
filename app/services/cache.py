"""
SEO AIOS 缓存服务
Caching Service
"""

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Optional
from functools import wraps


class CacheManager:
    """
    缓存管理器
    支持内存缓存和文件缓存
    """

    def __init__(self, cache_dir: str = None, ttl: int = 3600):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录（用于文件缓存）
            ttl: 默认缓存时间（秒）
        """
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'cache')
        self.ttl = ttl
        self._memory_cache = {}
        self._cache_timestamps = {}

        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, key: str, use_memory: bool = True) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键
            use_memory: 是否使用内存缓存

        Returns:
            缓存值，不存在返回None
        """
        # 优先从内存缓存获取
        if use_memory and key in self._memory_cache:
            if self._is_valid(key):
                return self._memory_cache[key]
            else:
                self._remove(key)

        # 从文件缓存获取
        cache_file = os.path.join(self.cache_dir, f"{self._generate_key(key)}.cache")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)

                # 检查是否过期
                if cached['expires_at'] > time.time():
                    # 同步到内存缓存
                    if use_memory:
                        self._memory_cache[key] = cached['value']
                        self._cache_timestamps[key] = cached['expires_at']
                    return cached['value']
                else:
                    os.remove(cache_file)
            except Exception:
                pass

        return None

    def set(self, key: str, value: Any, ttl: int = None):
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        """
        ttl = ttl or self.ttl
        expires_at = time.time() + ttl

        # 存入内存缓存
        self._memory_cache[key] = value
        self._cache_timestamps[key] = expires_at

        # 存入文件缓存
        cache_file = os.path.join(self.cache_dir, f"{self._generate_key(key)}.cache")
        cached = {
            'value': value,
            'created_at': time.time(),
            'expires_at': expires_at
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def delete(self, key: str):
        """删除缓存"""
        self._remove(key)

    def _remove(self, key: str):
        """移除缓存"""
        if key in self._memory_cache:
            del self._memory_cache[key]
        if key in self._cache_timestamps:
            del self._cache_timestamps[key]

        cache_file = os.path.join(self.cache_dir, f"{self._generate_key(key)}.cache")
        if os.path.exists(cache_file):
            os.remove(cache_file)

    def _is_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._cache_timestamps:
            return False
        return self._cache_timestamps[key] > time.time()

    def clear(self):
        """清空所有缓存"""
        self._memory_cache.clear()
        self._cache_timestamps.clear()

        # 清空文件缓存
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except Exception:
                    pass

    def get_stats(self) -> dict:
        """获取缓存统计"""
        valid_count = sum(1 for k in self._cache_timestamps if self._is_valid(k))

        return {
            'memory_cache_count': len(self._memory_cache),
            'valid_cache_count': valid_count,
            'cache_dir': self.cache_dir,
            'default_ttl': self.ttl
        }


# 全局缓存实例
_cache_manager = None


def get_cache() -> CacheManager:
    """获取全局缓存实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cached(key_prefix: str, ttl: int = 3600):
    """
    缓存装饰器

    Args:
        key_prefix: 缓存键前缀
        ttl: 过期时间（秒）

    Usage:
        @cached('article', ttl=1800)
        def get_article(article_id):
            return Article.query.get(article_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()

            # 生成缓存键
            cache_key = f"{key_prefix}:{':'.join(map(str, args))}"

            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


def invalidate_cache(key_prefix: str, *args):
    """
    清除指定缓存

    Args:
        key_prefix: 缓存键前缀
        *args: 参数
    """
    cache = get_cache()
    cache_key = f"{key_prefix}:{':'.join(map(str, args))}"
    cache.delete(cache_key)


# 预定义的缓存策略
CACHE_STRATEGIES = {
    'short': 300,      # 5分钟
    'medium': 1800,    # 30分钟
    'long': 3600,     # 1小时
    'day': 86400,     # 1天
    'week': 604800    # 1周
}
