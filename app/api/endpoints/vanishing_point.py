from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Line, VanishingPointResponse
from app.logic.intersection import calculate_intersection

router = APIRouter()

@router.post("/vanishing-point", response_model=VanishingPointResponse)
def compute_vanishing_point(lines: List[Line]):
    x_van, y_van = calculate_intersection(lines)
    return VanishingPointResponse(x_van=x_van, y_van=y_van) 