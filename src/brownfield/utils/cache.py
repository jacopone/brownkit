"""Caching utilities for performance optimization.

Provides in-memory and disk caching for expensive operations:
- Language detection results
- Metrics collection results
- File system scans
"""

import hashlib
import json
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from brownfield.config import BrownfieldConfig


class Cache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, ttl_seconds: int = 300):
        """Initialize cache with TTL.

        Args:
            ttl_seconds: Time-to-live in seconds (default: 5 minutes)
        """
        self._cache: dict[str, tuple[Any, float]] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, key: str) -> Any | None:
        """Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def invalidate(self, key: str) -> None:
        """Invalidate specific cache key.

        Args:
            key: Cache key to invalidate
        """
        self._cache.pop(key, None)


# Global in-memory cache
_memory_cache = Cache(ttl_seconds=300)


def cache_result(key_func: Callable | None = None, ttl_seconds: int = 300):
    """Decorator to cache function results in memory.

    Args:
        key_func: Optional function to generate cache key from args
        ttl_seconds: Time-to-live for cached results

    Usage:
        @cache_result(ttl_seconds=600)
        def expensive_operation(arg1, arg2):
            # ... expensive computation ...
            return result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: hash function name + args
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)

            # Check cache
            cached = _memory_cache.get(cache_key)
            if cached is not None:
                return cached

            # Execute function and cache result
            result = func(*args, **kwargs)
            _memory_cache.set(cache_key, result)
            return result

        wrapper.cache_clear = lambda: _memory_cache.clear()
        wrapper.cache_invalidate = lambda key: _memory_cache.invalidate(key)
        return wrapper

    return decorator


class DiskCache:
    """Disk-based cache for persistent storage."""

    def __init__(self, cache_dir: Path | None = None):
        """Initialize disk cache.

        Args:
            cache_dir: Directory for cache files (default: .specify/memory/cache)
        """
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            project_root = BrownfieldConfig.get_project_root()
            self.cache_dir = BrownfieldConfig.get_state_dir(project_root) / "cache"

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Hash key to avoid filesystem issues
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str, max_age_seconds: int | None = None) -> Any | None:
        """Get value from disk cache.

        Args:
            key: Cache key
            max_age_seconds: Maximum age in seconds (None = no expiry)

        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        # Check age if max_age specified
        if max_age_seconds:
            age = time.time() - cache_path.stat().st_mtime
            if age > max_age_seconds:
                cache_path.unlink()  # Delete expired cache
                return None

        try:
            with cache_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("value")
        except (json.JSONDecodeError, KeyError):
            # Corrupted cache file
            cache_path.unlink()
            return None

    def set(self, key: str, value: Any) -> None:
        """Set value in disk cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
        """
        cache_path = self._get_cache_path(key)

        data = {"value": value, "timestamp": time.time()}

        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def clear(self) -> None:
        """Clear all disk cache files."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

    def invalidate(self, key: str) -> None:
        """Invalidate specific cache key.

        Args:
            key: Cache key to invalidate
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()


def disk_cache_result(key_func: Callable, max_age_seconds: int = 3600):
    """Decorator to cache function results on disk.

    Args:
        key_func: Function to generate cache key from args
        max_age_seconds: Maximum age for cached results

    Usage:
        @disk_cache_result(
            key_func=lambda project_root, mode: f"metrics:{project_root}:{mode}",
            max_age_seconds=7200
        )
        def collect_metrics(project_root, mode):
            # ... expensive metrics collection ...
            return metrics
    """

    def decorator(func: Callable) -> Callable:
        cache = DiskCache()

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = key_func(*args, **kwargs)

            # Check cache
            cached = cache.get(cache_key, max_age_seconds)
            if cached is not None:
                return cached

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        wrapper.cache_clear = cache.clear
        wrapper.cache_invalidate = cache.invalidate
        return wrapper

    return decorator


def memoize_file_hash(file_path: Path) -> str:
    """Compute and cache file hash.

    Useful for detecting file changes without re-reading content.

    Args:
        file_path: Path to file

    Returns:
        SHA256 hash of file content
    """
    cache_key = f"file_hash:{file_path}"
    cached = _memory_cache.get(cache_key)

    if cached:
        # Check if file was modified
        current_mtime = file_path.stat().st_mtime
        cached_hash, cached_mtime = cached
        if current_mtime == cached_mtime:
            return cached_hash

    # Compute hash
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    file_hash = sha256.hexdigest()
    mtime = file_path.stat().st_mtime

    _memory_cache.set(cache_key, (file_hash, mtime))
    return file_hash
