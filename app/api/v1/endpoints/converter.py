from fastapi import APIRouter, HTTPException
from app.api.v1.model.dto import ConvertRequest
from app.services.factory import ConverterFactory
from fastapi.responses import FileResponse
import os
from app.api.v1.model.enums import EBookFormat

router = APIRouter()


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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
