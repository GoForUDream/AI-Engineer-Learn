import requests


def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an HTTPError if the response status code is not 200

    except requests.exceptions.Timeout:
        print(
            f"❌ Error: The request for '{city}' timed out. Please check your network connection."
        )
        return

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP Error occurred: {http_err}")
        print(f"Please verify that the city name '{city}' is spelled correctly.")
        return

    except requests.exceptions.RequestException as req_err:
        print(f"❌ A critical network error occurred: {req_err}")
        return

    try:
        data = response.json()

        current_condition = data["current_condition"][0]
        nearest_area = data["nearest_area"][0]
        temp_c = current_condition["temp_C"]
        humidity = current_condition["humidity"]
        desc = current_condition["weatherDesc"][0]["value"]
        resolved_city = nearest_area["areaName"][0]["value"]
        country = nearest_area["country"][0]["value"]

    except (KeyError, IndexError):
        print("❌ Error: The API returned data in an unexpected format.")
        return

    print("─" * 40)
    print(f"🌍 Weather Summary for: {resolved_city}, {country}")
    print("─" * 40)
    print(f"• Condition:   {desc}")
    print(f"• Temperature: {temp_c}°C")
    print(f"• Humidity:    {humidity}%")
    print("─" * 40)


if __name__ == "__main__":
    # Test Case 1: Success path
    print("Testing valid city...")
    get_weather("Tokyo")

    # Test Case 2: Success path
    print("Testing valid city...")
    get_weather("Hanoi")

    # Test Case 3: Simulating an invalid city parameter lookup
    print("\nTesting malformed or uncommon city entry...")
    get_weather("NonExistentCityXYZ")
