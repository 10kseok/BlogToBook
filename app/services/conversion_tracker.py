import asyncio
import uuid
import time
from typing import Dict, Optional, Any
from enum import Enum
import logging

from app.api.v1.model.enums import EBookFormat

logger = logging.getLogger("uvicorn")

class ConversionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversionTask:
    """전자책 변환 작업의 상태를 추적하기 위한 클래스"""
    
    def __init__(self, task_id: str, format: EBookFormat):
        self.task_id = task_id
        self.status = ConversionStatus.PENDING
        self.progress = 0
        self.message = "작업 대기 중..."
        self.result_path: Optional[str] = None
        self.error: Optional[str] = None
        self.created_at = time.time()
        self.updated_at = time.time()
        self.format = format  # 추가: 파일 형식 저장
        
    def update(self, status: Optional[ConversionStatus] = None, 
               progress: Optional[int] = None, 
               message: Optional[str] = None,
               result_path: Optional[str] = None,
               error: Optional[str] = None,):
        """작업 상태를 업데이트합니다"""
        if status is not None:
            self.status = status
        if progress is not None:
            self.progress = progress
        if message is not None:
            self.message = message
        if result_path is not None:
            self.result_path = result_path
        if error is not None:
            self.error = error
        self.updated_at = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """작업 정보를 딕셔너리 형태로 변환"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "result_path": self.result_path,
            "error": self.error,
            "format": self.format.value,  # format이 Enum인 경우 value 속성 사용
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class ConversionTracker:
    """변환 작업들을 관리하는 싱글톤 클래스"""
    
    _instance = None
    _tasks: Dict[str, ConversionTask] = {}
    _listeners: Dict[str, Dict[str, asyncio.Queue]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversionTracker, cls).__new__(cls)
        return cls._instance
    
    def create_task(self, format) -> str:
        """새로운 변환 작업을 생성하고 ID를 반환"""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = ConversionTask(task_id, format)
        self._listeners[task_id] = {}
        return task_id
    
    def get_task(self, task_id: str) -> Optional[ConversionTask]:
        """특정 ID의 작업 정보를 가져옴"""
        return self._tasks.get(task_id)
    
    async def update_task(self, task_id: str, **kwargs):
        """작업 상태를 업데이트하고 리스너들에게 알림"""
        if task_id in self._tasks:
            self._tasks[task_id].update(**kwargs)
            await self._notify_listeners(task_id)
        else:
            logger.warning(f"Task ID not found: {task_id}")
    
    async def register_listener(self, task_id: str, listener_id: str) -> asyncio.Queue:
        """특정 작업에 대한 리스너를 등록"""
        if task_id not in self._listeners:
            self._listeners[task_id] = {}
            
        queue = asyncio.Queue()
        self._listeners[task_id][listener_id] = queue
        
        # 현재 상태를 즉시 전송
        if task_id in self._tasks:
            await queue.put(self._tasks[task_id].to_dict())
            
        return queue
    
    def remove_listener(self, task_id: str, listener_id: str):
        """리스너 제거"""
        if task_id in self._listeners and listener_id in self._listeners[task_id]:
            del self._listeners[task_id][listener_id]
    
    async def _notify_listeners(self, task_id: str):
        """해당 작업의 모든 리스너에게 업데이트 전송"""
        if task_id not in self._listeners:
            return
            
        task_data = self._tasks[task_id].to_dict()
        for listener_queue in self._listeners[task_id].values():
            await listener_queue.put(task_data)
    
    def cleanup_old_tasks(self, max_age_seconds: int = 3600):
        """오래된 작업 정보 정리"""
        current_time = time.time()
        expired_tasks = []
        
        for task_id, task in self._tasks.items():
            if current_time - task.updated_at > max_age_seconds:
                expired_tasks.append(task_id)
                
        for task_id in expired_tasks:
            if task_id in self._tasks:
                del self._tasks[task_id]
            if task_id in self._listeners:
                del self._listeners[task_id]
