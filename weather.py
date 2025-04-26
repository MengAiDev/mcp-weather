from typing import Any
import httpx
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY environment variable is required")

async def make_ow_request(endpoint: str, params: dict = None) -> dict[str, Any] | None:
    """Make a request to the OpenWeather API with proper error handling."""
    if params is None:
        params = {}
    params["appid"] = API_KEY
    params["units"] = "metric"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(location: str) -> str:
    """Get weather alerts for a location.

    Args:
        location: City name and country code (e.g. "London,uk")
    """
    url = f"{OPENWEATHER_API_BASE}/weather"
    data = await make_ow_request(url, {"q": location})

    if not data:
        return "Unable to fetch weather data for this location."

    # OpenWeather doesn't provide detailed alerts in free tier
    # So we'll return current weather warnings if any
    if "weather" not in data:
        return "No weather alerts for this location."

    alerts = []
    for weather in data["weather"]:
        if weather["main"] in ["Thunderstorm", "Tornado", "Hurricane"]:
            alert = f"""
Severe Weather Alert: {weather['main']}
Description: {weather['description']}
"""
            alerts.append(alert)

    if not alerts:
        return "No active weather alerts for this location."

    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(location: str) -> str:
    """Get weather forecast for a location.

    Args:
        location: City name and country code (e.g. "London,uk")
    """
    url = f"{OPENWEATHER_API_BASE}/forecast"
    data = await make_ow_request(url, {"q": location})

    if not data:
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