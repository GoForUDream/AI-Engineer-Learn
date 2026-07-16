from typing import Literal, Optional
from pydantic import BaseModel, Field


class WeatherRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100)


class WeatherCondition(BaseModel):
    temperature_c: float
    condition: str
    wind_kph: float


class WeatherReport(BaseModel):
    city: str
    country: str
    weather: WeatherCondition


class APIResult(BaseModel):
    status: Literal["success", "error"]
    payload: Optional[WeatherReport] = None
    error_message: Optional[str] = None
