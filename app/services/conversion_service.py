import os
import logging
from app.services.factory import ConverterFactory
from app.services.conversion_tracker import ConversionTracker, ConversionStatus

logger = logging.getLogger("uvicorn")

async def process_conversion(task_id: str, book_title: str, format, links: list):
    """
    백그라운드에서 실행되는 변환 함수
    진행 상태를 추적하고 업데이트하는 역할을 담당
    
    Args:
        task_id: 변환 작업 식별자
        book_title: 생성할 전자책 제목
        format: 출력 파일 형식 (EBookFormat)
        links: 변환할 블로그 포스트 URL 목록
    """
    tracker = ConversionTracker()
    
    try:
        # 변환 시작 알림
        await tracker.update_task(
            task_id,
            status=ConversionStatus.PROCESSING,
            progress=5,
            message="변환 작업을 시작합니다..."
        )
        
        # 컨버터 생성
        converter = ConverterFactory.create_converter(format)
        
        # 컨텐츠 수집 시작
        await tracker.update_task(
            task_id,
            progress=10,
            message="블로그 포스트에서 콘텐츠를 수집 중입니다..."
        )
        
        # 실제 변환 작업 - 진행 상태에 따라 업데이트
        # 컨텐츠 추출 완료
        await tracker.update_task(
            task_id,
            progress=30,
            message="이미지 처리 중입니다..."
        )
        
        # 이미지 처리 완료
        await tracker.update_task(
            task_id,
            progress=50,
            message="문서 구조화 중입니다..."
        )
        
        # 최종 파일 생성
        await tracker.update_task(
            task_id,
            progress=75,
            message=f"{format.value.upper()} 파일 생성 중입니다..."
        )
        
        # 실제 변환 작업 수행
        output_path = await converter.convert(links, book_title)
        
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"변환된 파일을 찾을 수 없습니다: {output_path}")
        
        # 완료 알림
        await tracker.update_task(
            task_id,
            status=ConversionStatus.COMPLETED,
            progress=100,
            message="변환이 완료되었습니다!",
            result_path=output_path
        )
    
    except Exception as e:
        logger.error(f"Error in background conversion: {str(e)}", exc_info=True)
        
        # 오류 발생 알림
        await tracker.update_task(
            task_id,
            status=ConversionStatus.FAILED,
            progress=0,
            message="변환 중 오류가 발생했습니다",
            error=str(e)
        )
