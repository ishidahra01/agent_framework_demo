"""
Memory Management System
Short-term and Long-term memory implementations
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Memory entry structure"""
    key: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ttl: Optional[int] = None  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl is None:
            return False
        expiry = self.timestamp + timedelta(seconds=self.ttl)
        return datetime.utcnow() > expiry


class BaseMemory(ABC):
    """Base class for memory providers"""
    
    @abstractmethod
    async def store(self, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict] = None) -> bool:
        """Store a value in memory"""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from memory"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value from memory"""
        pass
    
    @abstractmethod
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List all keys matching pattern"""
        pass


class InMemoryCache(BaseMemory):
    """In-process memory cache for short-term storage"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, MemoryEntry] = {}
        self.default_ttl = default_ttl
    
    async def store(self, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict] = None) -> bool:
        """Store value in cache"""
        try:
            entry = MemoryEntry(
                key=key,
                value=value,
                ttl=ttl or self.default_ttl,
                metadata=metadata or {}
            )
            self.cache[key] = entry
            logger.debug(f"Stored in cache: {key}")
            return True
        except Exception as e:
            logger.error(f"Error storing in cache: {str(e)}")
            return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from cache"""
        entry = self.cache.get(key)
        
        if entry is None:
            return None
        
        if entry.is_expired():
            await self.delete(key)
            return None
        
        logger.debug(f"Retrieved from cache: {key}")
        return entry.value
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Deleted from cache: {key}")
            return True
        return False
    
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List keys in cache"""
        keys = list(self.cache.keys())
        
        if pattern:
            # Simple pattern matching
            keys = [k for k in keys if pattern.replace("*", "") in k]
        
        return keys
    
    async def cleanup_expired(self):
        """Remove expired entries"""
        expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
        for key in expired_keys:
            await self.delete(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired entries")


class AzureAISearchMemory(BaseMemory):
    """Long-term memory using Azure AI Search"""
    
    def __init__(self, endpoint: str, api_key: str, index_name: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.index_name = index_name
    
    async def store(self, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict] = None) -> bool:
        """Store value in Azure AI Search"""
        try:
            # Mock implementation - in production, use Azure SDK
            logger.info(f"Storing in Azure AI Search: {key}")
            
            document = {
                "id": key,
                "content": json.dumps(value) if not isinstance(value, str) else value,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": json.dumps(metadata or {})
            }
            
            # Would call Azure AI Search API here
            return True
            
        except Exception as e:
            logger.error(f"Error storing in Azure AI Search: {str(e)}")
            return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from Azure AI Search"""
        try:
            # Mock implementation
            logger.info(f"Retrieving from Azure AI Search: {key}")
            return None  # Would query Azure AI Search here
            
        except Exception as e:
            logger.error(f"Error retrieving from Azure AI Search: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete value from Azure AI Search"""
        try:
            logger.info(f"Deleting from Azure AI Search: {key}")
            return True  # Would call Azure AI Search API here
            
        except Exception as e:
            logger.error(f"Error deleting from Azure AI Search: {str(e)}")
            return False
    
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List keys in Azure AI Search"""
        # Mock implementation
        return []
    
    async def search(self, query: str, top: int = 10) -> List[Dict[str, Any]]:
        """Semantic search in long-term memory"""
        try:
            logger.info(f"Searching in Azure AI Search: {query}")
            
            # Mock implementation - would use Azure AI Search vector search
            results = []
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching Azure AI Search: {str(e)}")
            return []


class MemoryManager:
    """
    Unified memory manager handling both short-term and long-term memory
    """
    
    def __init__(self, short_term: BaseMemory, long_term: Optional[BaseMemory] = None):
        self.short_term = short_term
        self.long_term = long_term
    
    async def store_short_term(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store in short-term memory"""
        return await self.short_term.store(key, value, ttl)
    
    async def retrieve_short_term(self, key: str) -> Optional[Any]:
        """Retrieve from short-term memory"""
        return await self.short_term.retrieve(key)
    
    async def store_long_term(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store in long-term memory"""
        if self.long_term is None:
            logger.warning("Long-term memory not configured")
            return False
        
        return await self.long_term.store(key, value, metadata=metadata)
    
    async def retrieve_long_term(self, key: str) -> Optional[Any]:
        """Retrieve from long-term memory"""
        if self.long_term is None:
            return None
        
        return await self.long_term.retrieve(key)
    
    async def search_long_term(self, query: str, top: int = 10) -> List[Dict[str, Any]]:
        """Search long-term memory"""
        if self.long_term is None or not hasattr(self.long_term, 'search'):
            return []
        
        return await self.long_term.search(query, top)
    
    async def promote_to_long_term(self, key: str) -> bool:
        """Promote short-term memory to long-term"""
        value = await self.retrieve_short_term(key)
        
        if value is None:
            return False
        
        return await self.store_long_term(key, value)
    
    @classmethod
    def create_default(cls, config: Optional[Dict[str, Any]] = None) -> 'MemoryManager':
        """Create memory manager with default configuration"""
        config = config or {}
        
        # Short-term memory (in-memory cache)
        short_term = InMemoryCache(
            default_ttl=config.get("short_term_ttl", 3600)
        )
        
        # Long-term memory (Azure AI Search)
        long_term = None
        if config.get("long_term_enabled", False):
            long_term = AzureAISearchMemory(
                endpoint=config.get("ai_search_endpoint", ""),
                api_key=config.get("ai_search_key", ""),
                index_name=config.get("ai_search_index", "agent-mem-long")
            )
        
        return cls(short_term=short_term, long_term=long_term)
