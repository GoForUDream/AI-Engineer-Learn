import httpx
from pydantic import ValidationError
from config import API_BASE_URL, API_TIMEOUT_SECONDS
from schemas.weather import WeatherTaskResult, WeatherReport, WeatherCondition


async def fetch_weather(client: httpx.AsyncClient, city: str) -> WeatherTaskResult:
    url = f"{API_BASE_URL}/{city}?format=j1"

    try:
        response = await client.get(url, timeout=API_TIMEOUT_SECONDS)
        response.raise_for_status()
        raw_data = response.json()

        current = raw_data["current_condition"][0]
        area = raw_data["nearest_area"][0]

        returned_region = area["region"][0]["value"]
        returned_city = area["areaName"][0]["value"]
        returned_country = area["country"][0]["value"]
        api_search_query = raw_data["request"][0]["query"]

        if (
            city.lower() not in api_search_query.lower()
            and city.lower() not in returned_city.lower()
            and city.lower() not in returned_country.lower()
            and city.lower() not in returned_region.lower()
        ):
            return WeatherTaskResult(
                city_requested=city,
                success=False,
                error_message=f"Location mismatch. API matched '{returned_city}, {returned_country}' for request '{city}'.",
            )

        display_city = returned_city
        if city.lower() not in returned_city.lower() and (
            city.lower() in returned_region.lower()
            or city.lower() in api_search_query.lower()
        ):
            display_city = f"{returned_city} ({city.title()})"
        elif city.lower() not in returned_city.lower() and returned_region:
            display_city = f"{returned_city}, {returned_region}"

        report = WeatherReport(
            city=display_city,
            country=returned_country,
            weather=WeatherCondition(
                temp_C=float(current["temp_C"]),
                condition=current["weatherDesc"][0]["value"],
            ),
        )

        return WeatherTaskResult(city_requested=city, success=True, data=report)

    except httpx.TimeoutException:
        return WeatherTaskResult(
            city_requested=city,
            success=False,
            error_message="Network connection timed out.",
        )
    except httpx.HTTPStatusError as e:
        return WeatherTaskResult(
            city_requested=city,
            success=False,
            error_message=f"HTTP Server error ({e.response.status_code}).",
        )
    except httpx.RequestError as e:
        return WeatherTaskResult(
            city_requested=city,
            success=False,
            error_message=f"Network transport error: {str(e)}",
        )
    except (ValidationError, KeyError, IndexError, ValueError):
        return WeatherTaskResult(
            city_requested=city,
            success=False,
            error_message="API response parsing error.",
        )
    except Exception:
        return WeatherTaskResult(
            city_requested=city,
            success=False,
            error_message="An internal application error occurred.",
        )
