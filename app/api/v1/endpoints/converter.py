from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, StreamingResponse
from app.api.v1.model.dto import ConvertRequest, TaskStatusResponse
from app.services.conversion_tracker import ConversionTracker, ConversionStatus
from app.services.conversion_service import process_conversion
import os
import uuid
import asyncio
import logging
import json

router = APIRouter()
logger = logging.getLogger("uvicorn")

@router.post("/convert")
async def convert_to_ebook(request: ConvertRequest, background_tasks: BackgroundTasks):
    """
    전자책 변환을 비동기적으로 시작하고 상태를 추적할 수 있는 작업 ID를 반환
    """
    try:
        # 새로운 변환 작업 생성 및 ID 발급 (format 정보 포함)
        tracker = ConversionTracker()
        task_id = tracker.create_task(format=request.format)

        # 백그라운드 작업으로 변환 프로세스 등록
        background_tasks.add_task(
            process_conversion,
            task_id=task_id,
            book_title=request.book_title,
            format=request.format,
            links=request.links
        )

        # 작업 ID와 초기 상태 반환
        task = tracker.get_task(task_id)
        return TaskStatusResponse(**task.to_dict())

    except ValueError as e:
        logger.error(f"Invalid request parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting conversion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/convert/status/{task_id}/stream")
async def stream_conversion_status(task_id: str, request: Request):
    """
    SSE를 통해 변환 작업의 실시간 상태 업데이트를 스트리밍
    """
    try:
        tracker = ConversionTracker()
        task = tracker.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task ID not found: {task_id}")
        
        async def event_generator():
            # 고유한 리스너 ID 생성
            listener_id = str(uuid.uuid4())
            
            # 이벤트 큐 등록
            queue = await tracker.register_listener(task_id, listener_id)
            
            try:
                while True:
                    # 클라이언트 연결 확인
                    if await request.is_disconnected():
                        break
                    
                    # 큐에서 이벤트 가져오기 (최대 30초 대기)
                    try:
                        data = await asyncio.wait_for(queue.get(), timeout=30.0)
                        yield f"data: {json.dumps(data)}\n\n"
                        
                        # 작업이 완료되었거나 실패했다면 스트림 종료
                        if data["status"] in [ConversionStatus.COMPLETED.value, ConversionStatus.FAILED.value]:
                            break
                    except asyncio.TimeoutError:
                        # 30초 동안 업데이트가 없으면 핑 이벤트 전송
                        yield f"event: ping\ndata: {json.dumps({'time': str(asyncio.get_event_loop().time())})}\n\n"
            finally:
                # 리스너 제거
                tracker.remove_listener(task_id, listener_id)
                
        return StreamingResponse(
            event_generator(), 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Nginx에서 버퍼링 비활성화
            }
        )
        
    except Exception as e:
        logger.error(f"Error in SSE stream: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/convert/status/{task_id}", response_model=TaskStatusResponse)
async def get_conversion_status(task_id: str):
    """
    변환 작업의 현재 상태를 확인 (폴백용)
    """
    try:
        tracker = ConversionTracker()
        task = tracker.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task ID not found: {task_id}")
            
        return TaskStatusResponse(**task.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/convert/result/{task_id}")
async def get_conversion_result(task_id: str):
    """
    완료된 변환 작업의 결과 파일을 다운로드
    """
    try:
        tracker = ConversionTracker()
        task = tracker.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task ID not found: {task_id}")
            
        if task.status != ConversionStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Task is not completed yet. Current status: {task.status}"
            )
            
        if not task.result_path or not os.path.exists(task.result_path):
            raise HTTPException(status_code=404, detail="Result file not found")
            
        filename = os.path.basename(task.result_path)
            
        return FileResponse(
            path=task.result_path,
            filename=filename,
            media_type=task.format.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversion result: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
