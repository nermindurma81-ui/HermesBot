import httpx


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _geocode(location: str):
    resp = httpx.get(
        GEOCODE_URL,
        params={"name": location, "count": 1, "language": "en", "format": "json"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results") or []
    if not results:
        return None
    r = results[0]
    return {
        "name": r.get("name"),
        "country": r.get("country"),
        "latitude": r.get("latitude"),
        "longitude": r.get("longitude"),
        "timezone": r.get("timezone"),
    }


def run(location: str):
    if not location or not location.strip():
        return "❌ Weather skill error: location je obavezna."

    place = _geocode(location.strip())
    if not place:
        return f"❌ Ne mogu pronaći lokaciju: {location}"

    resp = httpx.get(
        FORECAST_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "auto",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    current = data.get("current", {})

    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind = current.get("wind_speed_10m")
    code = current.get("weather_code")
    time = current.get("time")

    return (
        f"🌤 Vrijeme za {place['name']}, {place['country']} ({place['timezone']})\n"
        f"- Vrijeme mjerenja: {time}\n"
        f"- Temperatura: {temp}°C\n"
        f"- Vlažnost: {humidity}%\n"
        f"- Vjetar: {wind} km/h\n"
        f"- Weather code: {code}"
    )
