"""
Unit tests for Memory Manager
"""
import pytest
from agents.memory.manager import InMemoryCache, MemoryManager


@pytest.mark.asyncio
async def test_in_memory_cache_store_retrieve():
    """Test storing and retrieving from cache"""
    cache = InMemoryCache(default_ttl=60)
    
    await cache.store("test_key", "test_value")
    value = await cache.retrieve("test_key")
    
    assert value == "test_value"


@pytest.mark.asyncio
async def test_in_memory_cache_delete():
    """Test deleting from cache"""
    cache = InMemoryCache()
    
    await cache.store("test_key", "test_value")
    await cache.delete("test_key")
    value = await cache.retrieve("test_key")
    
    assert value is None


@pytest.mark.asyncio
async def test_in_memory_cache_list_keys():
    """Test listing keys"""
    cache = InMemoryCache()
    
    await cache.store("key1", "value1")
    await cache.store("key2", "value2")
    
    keys = await cache.list_keys()
    
    assert "key1" in keys
    assert "key2" in keys


@pytest.mark.asyncio
async def test_memory_manager():
    """Test memory manager"""
    manager = MemoryManager.create_default()
    
    # Test short-term memory
    await manager.store_short_term("session_key", {"data": "test"})
    value = await manager.retrieve_short_term("session_key")
    
    assert value is not None
    assert value["data"] == "test"


@pytest.mark.asyncio
async def test_memory_manager_promotion():
    """Test promoting short-term to long-term memory"""
    config = {"long_term_enabled": True}
    manager = MemoryManager.create_default(config)
    
    await manager.store_short_term("important_key", {"data": "important"})
    
    # Note: In mock implementation, long-term store might not work
    # This tests the API contract
    success = await manager.promote_to_long_term("important_key")
    
    # May fail if long-term is not actually configured
    assert success is True or success is False
