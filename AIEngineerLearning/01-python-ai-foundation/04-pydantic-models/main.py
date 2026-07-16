from pydantic import ValidationError
from schemas.weather import WeatherRequest
from services.weather_service import get_weather


def main():
    user_input = "Hanoi"

    try:
        request_data = WeatherRequest(city=user_input)
    except ValidationError as e:
        print(f"Invalid city name format: {e}")
        return

    result = get_weather(city=request_data.city)

    if result.status == "success" and result.payload is not None:
        report = result.payload
        print(f"🌍 Weather in {report.city}, {report.country}:")
        print(f"• Condition: {report.weather.condition}")
        print(f"• Temperature: {report.weather.temperature_c}°C")
    else:
        print(f"❌ Failed to fetch weather data. Reason: {result.error_message}")


if __name__ == "__main__":
    main()
