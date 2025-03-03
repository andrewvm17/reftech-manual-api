from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Line, VanishingPointResponse 
from app.logic.manual_vanishing_point_detector import manual_vp

router = APIRouter()

@router.post("/manual-vanishing-point", response_model=VanishingPointResponse)
def compute_vanishing_point(lines: List[Line]):
    x_van, y_van = manual_vp(lines)
    return VanishingPointResponse(x_van=x_van, y_van=y_van) 