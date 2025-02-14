from pydantic import BaseModel

class Line(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    slope: float


class VanishingPointResponse(BaseModel):
    x_van: float
    y_van: float 