from fastapi import APIRouter, HTTPException, File, UploadFile, status
import cv2
import numpy as np
from typing import Any, Dict
from fastapi.responses import JSONResponse
from app.models.schemas import VanishingPointResponse
from app.logic.semi_automated_detector import detector_v4

router = APIRouter()


@router.post("/semi-automated-vanishing-point")
async def get_vanishingpoint_compat(image_file: UploadFile = File(...)) -> JSONResponse:
    # 1. Validate file upload
    if not image_file:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "No file uploaded"}
        )
    # 2. Validate file type (similar to allowed_file(...) in Flask)
    ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg"}
    if image_file.content_type not in ALLOWED_TYPES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Unsupported file type"}
        )

    try:
        # 3. Convert the file for OpenCV
        file_bytes = await image_file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if cv_img is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Could not decode image"}
            )

        # 4. Run the same detector function
        vanishing_point = detector_v4(cv_img)

        # 5. If no vanishing point found, return empty list
        if vanishing_point is None:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"vanishing_point": []}
            )

        # 6. Otherwise, return the same JSON shape as the old Flask code
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "vanishing_point": {
                    "x": float(vanishing_point[0]),
                    "y": float(vanishing_point[1])
                }
            }
        )

    except Exception as e:
        # Log / handle any unexpected errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to process the image"}
        )