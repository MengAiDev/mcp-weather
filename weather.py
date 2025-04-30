from typing import Any
import httpx
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
from const import OPEN_WEATHER_API_KEY
API_KEY = OPEN_WEATHER_API_KEY
if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY environment variable is required")

async def make_ow_request(endpoint: str, params: dict = None) -> dict[str, Any] | None:
    """Make a request to the OpenWeather API with proper error handling."""
    if params is None:
        params = {}
    params["appid"] = API_KEY
    params["units"] = "metric"
    url = f"{OPENWEATHER_API_BASE}{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def get_forecast(location: str) -> str:
    """Get weather forecast for a location.

    Args:
        location: City name and country code (e.g. "London,uk")
    """
    data = await make_ow_request("/forecast", {"q": location})

    if not data or "list" not in data:
        return "Unable to fetch forecast data for this location."

    # Format the forecast data
    forecasts = []
    for forecast in data["list"][:5]:  # Only show next 5 forecasts (every 3 hours)
        dt = forecast["dt_txt"]
        temp = forecast["main"]["temp"]
        desc = forecast["weather"][0]["description"]
        wind_speed = forecast["wind"]["speed"]
        
        forecast_str = f"""
{dt}:
Temperature: {temp}°C
Conditions: {desc}
Wind Speed: {wind_speed} m/s
"""
        forecasts.append(forecast_str)

    return "\n---\n".join(forecasts)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')