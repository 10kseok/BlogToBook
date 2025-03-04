from fastapi import HTTPException

class TaskException(HTTPException):
    """작업 관련 모든 예외의 베이스 클래스"""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class TaskNotFoundException(TaskException):
    def __init__(self, task_id: str):
        super().__init__(
            status_code=404,
            detail=f"Task ID not found: {task_id}"
        )

class TaskNotCompletedException(TaskException):
    def __init__(self, status: str):
        super().__init__(
            status_code=400,
            detail=f"Task is not completed yet. Current status: {status}"
        )

class ResultFileNotFoundException(TaskException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Result file not found"
        )

class InvalidRequestException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=400,
            detail=detail
        )

class ConversionException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            detail=detail
        )
