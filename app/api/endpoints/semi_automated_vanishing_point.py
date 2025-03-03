from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Line, VanishingPointResponse
from app.logic.semi_automated_detector import detector_v4

router = APIRouter()

@router.post('/semi-automated-vanishing-point', response_model=VanishingPointResponse)
def compute_vanishing_point(lines: List[Line]):
    x_van, y_van = detector_v4(lines)
    return VanishingPointResponse(x_van=x_van, y_van=y_van)