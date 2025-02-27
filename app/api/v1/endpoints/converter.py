from fastapi import APIRouter, HTTPException
from app.api.v1.model.dto import ConvertRequest
from app.services.factory import ConverterFactory
from fastapi.responses import FileResponse
import os
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn")

@router.post("/convert")
async def convert_to_ebook(request: ConvertRequest):
    try:
        converter = ConverterFactory.create_converter(request.format)
        output_path = await converter.convert(request.links, request.book_title)

        if not os.path.exists(output_path):
            raise HTTPException(
                status_code=500,
                detail=f"{request.format.value.upper()} file was not created",
            )

        filename = os.path.basename(output_path)

        return FileResponse(
            path=output_path, filename=filename, media_type=request.format.mime_type
        )

    except ValueError as e:
        logger.error(f"Invalid request parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during ebook conversion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
