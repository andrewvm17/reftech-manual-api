from typing import List, Tuple
from fastapi import HTTPException
from app.models.schemas import Line
from itertools import combinations
import statistics


def calculate_intersection(lines: List[Line]) -> Tuple[float, float]:
    if len(lines) < 2:
        raise ValueError("Need at least two lines to compute intersection!")
    
    # Get all possible pairs of lines
    line_pairs = list(combinations(lines, 2))
    intersections: List[Tuple[float, float]] = []
    
    # Calculate intersection for each pair
    for line1, line2 in line_pairs:
        try:
            A1, B1, C1 = convert_line_to_abc(line1)
            A2, B2, C2 = convert_line_to_abc(line2)
            
            denominator = A1 * B2 - B1 * A2
            if abs(denominator) < 1e-9:
                continue  # Skip parallel lines instead of failing
                
            x = (B2 * C1 - B1 * C2) / denominator
            y = (A1 * C2 - A2 * C1) / denominator
            intersections.append((x, y))
            
        except Exception as e:
            continue  # Skip problematic pairs
    
    if not intersections:
        raise HTTPException(
            status_code=400,
            detail="No valid intersections found among the lines."
        )
    
    # Calculate average intersection point
    avg_x = statistics.mean(x for x, _ in intersections)
    avg_y = statistics.mean(y for _, y in intersections)
    
    return (avg_x, avg_y)


def convert_line_to_abc(line: Line) -> Tuple[float, float, float]:
    # Given two points (x1, y1) and (x2, y2):
    # A = y2 - y1
    # B = x1 - x2
    # C = A * x1 + B * y1
    A = line.y2 - line.y1
    B = line.x1 - line.x2
    C = A * line.x1 + B * line.y1
    return (A, B, C) 