from fastapi import APIRouter, HTTPException
from app.services.epub_converter import EPUBConverter
from fastapi.responses import FileResponse
import os

router = APIRouter()
converter = EPUBConverter()

@router.post("/convert")
async def convert_to_epub(url: str):
    try:
        epub_path = await converter.convert_url_to_epub(url)
        
        # 파일이 존재하는지 확인
        if not os.path.exists(epub_path):
            raise HTTPException(status_code=500, detail="EPUB file was not created")
            
        # 파일명 추출
        filename = os.path.basename(epub_path)
        
        # EPUB 파일을 응답으로 반환
        return FileResponse(
            path=epub_path,
            filename=filename,
            media_type="application/epub+zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 