from typing import List, Tuple
from fastapi import HTTPException
from app.models.schemas import Line


def calculate_intersection(lines: List[Line]) -> Tuple[float, float]:
    if len(lines) < 2:
        raise ValueError("Need at least two lines to compute intersection!")
    
    A1, B1, C1 = convert_line_to_abc(lines[0])
    A2, B2, C2 = convert_line_to_abc(lines[1])
    
    denominator = A1 * B2 - B1 * A2
    if abs(denominator) < 1e-9:
        raise HTTPException(
            status_code=400,
            detail="Lines do not intersect or are nearly parallel."
        )
    
    x = (B2 * C1 - B1 * C2) / denominator
    y = (A1 * C2 - A2 * C1) / denominator
    return (x, y)


def convert_line_to_abc(line: Line) -> Tuple[float, float, float]:
    # Given two points (x1, y1) and (x2, y2):
    # A = y2 - y1
    # B = x1 - x2
    # C = A * x1 + B * y1
    A = line.y2 - line.y1
    B = line.x1 - line.x2
    C = A * line.x1 + B * line.y1
    return (A, B, C) 