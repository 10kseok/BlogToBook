import time
import functools
import logging
from typing import Callable, Any
import asyncio

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='\033[95m%(name)s\033[0m: %(asctime)s - %(message)s'
)
logger = logging.getLogger("PERFORMANCE")


class TimingDecorator:
    """함수 실행 시간을 측정하는 데코레이터 클래스"""
    
    def __init__(self, name: str = None):
        """
        Args:
            name: 로그에 표시할 함수 설명 (없으면 함수명 사용)
        """
        self.name = name
        
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            """동기 함수 wrapper"""
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            self._log_execution_time(func, start_time, end_time)
            return result
            
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            """비동기 함수 wrapper"""
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            self._log_execution_time(func, start_time, end_time)
            return result
            
        # 비동기 함수인지 검사하여 적절한 래퍼 반환
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
        
    def _log_execution_time(self, func: Callable, start_time: float, end_time: float) -> None:
        """실행 시간을 로그에 기록"""
        elapsed_time = end_time - start_time
        display_name = self.name or func.__name__
        logger.info(f"⏱️ {display_name}: {elapsed_time:.4f}초")


# 간편한 사용을 위한 함수형 인터페이스
def measure_time(name: str = None):
    """함수 실행 시간 측정 데코레이터
    
    Args:
        name: 함수 설명 (없으면 함수명 사용)
        
    Returns:
        데코레이터 인스턴스
    
    사용 예:
        @measure_time("데이터 처리")
        def process_data(data):
            # 처리 로직
            
        @measure_time()
        async def fetch_url(url):
            # 비동기 처리 로직
    """
    return TimingDecorator(name)
