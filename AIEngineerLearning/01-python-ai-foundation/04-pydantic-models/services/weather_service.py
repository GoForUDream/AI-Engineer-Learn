import requests
from pydantic import ValidationError
from schemas.weather import APIResult


def get_weather(city: str) -> APIResult:
    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        raw_data = response.json()

        # Structure the raw API response to match our Pydantic expectation
        formatted_data = {
            "status": "success",
            "payload": {
                "city": raw_data["nearest_area"][0]["areaName"][0]["value"],
                "country": raw_data["nearest_area"][0]["country"][0]["value"],
                "weather": {
                    "temperature_c": float(raw_data["current_condition"][0]["temp_C"]),
                    "condition": raw_data["current_condition"][0]["weatherDesc"][0][
                        "value"
                    ],
                    "wind_kph": float(
                        raw_data["current_condition"][0]["windspeedKmph"]
                    ),
                },
            },
        }

        return APIResult.model_validate(formatted_data)

    except requests.exceptions.RequestException as e:
        return APIResult(status="error", error_message=f"Network error: {str(e)}")
    except (ValidationError, KeyError, IndexError) as e:
        return APIResult(
            status="error",
            error_message=f"Data parsing or validation failure: {str(e)}",
        )
