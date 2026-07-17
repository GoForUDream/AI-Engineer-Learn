import httpx
import asyncio
import time
from services.async_weather import fetch_weather


async def get_weather():
    print("=== Production-Grade Weather Engine ===")

    cities = []
    while len(cities) < 3:
        city = input(f"Enter city #{len(cities) + 1}: ").strip()
        if not city:
            print("❌ Input cannot be empty. Please provide a valid location name.")
            continue
        cities.append(city)

    print("\n⚡ Initializing concurrent queries...")

    start_time = time.perf_counter()

    async with httpx.AsyncClient() as client:
        # Create a list of async coroutine tasks
        tasks = [fetch_weather(client, city) for city in cities]
        results = await asyncio.gather(*tasks)

    end_time = time.perf_counter()

    print("\n" + "─" * 65)
    print(
        f"{'REQUESTED CITY':20} | {'RESOLVED LOCATION':20} | {'TEMP':6} | {'STATUS / DESC'}"
    )
    print("─" * 65)

    for res in results:
        if res.success and res.data:
            loc_str = f"{res.data.city}, {res.data.country}"
            print(
                f"✓ {res.city_requested:18} | {loc_str:20} | {res.data.weather.temperature_c:4}°C | {res.data.weather.condition}"
            )
        else:
            print(
                f"❌ {res.city_requested:18} | {'N/A':20} | {'N/A':6} | Error: {res.error_message}"
            )

    print("─" * 65)
    print(f"Completed concurrently in {end_time - start_time:.4f} seconds.\n")


if __name__ == "__main__":
    asyncio.run(get_weather())
