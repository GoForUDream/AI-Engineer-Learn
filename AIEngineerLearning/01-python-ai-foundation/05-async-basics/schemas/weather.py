from pydantic import BaseModel, Field
from typing import Optional


class WeatherCondition(BaseModel):
    temperature_c: float = Field(..., alias="temp_C")
    condition: str


class WeatherReport(BaseModel):
    city: str
    country: str
    weather: WeatherCondition


class WeatherTaskResult(BaseModel):
    city_requested: str
    success: bool
    data: Optional[WeatherReport] = None
    error_message: Optional[str] = None
