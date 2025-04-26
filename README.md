# MCP Server: Weather

## Description

This is the mcp server written in python. It offers the following features:
* Get weather forecast data from OpenWeather API
* Get weather alerts from OpenWeather API

## Installation and quick start

1. Set up your OpenWeather API key:
Change the `OPENWEATHER_API_KEY` variable in `.env` to your API key.

2. Run the server:
See at: https://www.cnblogs.com/ryanzheng/p/18781666

## API Usage

The server provides two endpoints:
- `/forecast?location={city,country}` - Get weather forecast
- `/alerts?location={city,country}` - Get weather alerts

Example:
```bash
curl "http://localhost:8000/forecast?location=London,uk"
```

## Requirements

You need to sign up for a free OpenWeather API key at:
https://openweathermap.org/api