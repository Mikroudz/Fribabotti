import httpx
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from models.course.model import CourseWeather
import math


async def get_current_fmi_weather(lat: float, lon: float) -> CourseWeather | dict:
    """
    Asynchronously fetches the current weather (temp, wind speed, wind direction, weather code)
    from the Finnish Meteorological Institute (FMI) for given coordinates.
    """
    # Fetch data from the last 1 hour to keep the XML payload small
    now = datetime.now(timezone.utc)
    start_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = (now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = "https://opendata.fmi.fi/wfs"
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "getFeature",
        # Using the Harmonie model (best for Scandinavia/Finland)
        "storedquery_id": "fmi::forecast::harmonie::surface::point::simple",
        "latlon": f"{lat},{lon}",
        # Note the different parameter names for forecasts
        "parameters": "Temperature,WindSpeedMS,WindDirection,WeatherSymbol3",
        "starttime": start_time,
        "endtime": end_time,
    }
    # Perform the async HTTP request
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()

    # Parse the FMI GML/XML response
    root = ET.fromstring(response.content)

    # FMI XML namespaces required for parsing
    namespaces = {
        "wfs": "http://www.opengis.net/wfs/2.0",
        "BsWfs": "http://xml.fmi.fi/schema/wfs/2.0",
    }

    weather_data_by_time = {}

    # Extract all parameters and group them by timestamp
    for member in root.findall("wfs:member", namespaces):
        element = member.find("BsWfs:BsWfsElement", namespaces)
        if element is not None:
            time_str = element.find("BsWfs:Time", namespaces).text
            param_name = element.find("BsWfs:ParameterName", namespaces).text
            param_value = element.find("BsWfs:ParameterValue", namespaces).text

            if time_str not in weather_data_by_time:
                weather_data_by_time[time_str] = {}

            # Handle missing data (FMI sometimes returns 'NaN' if a specific sensor is down)
            try:
                val = float(param_value)
            except ValueError:
                val = None

            weather_data_by_time[time_str][param_name] = val

    if not weather_data_by_time:
        return {"error": "No data found for this location/time."}

    closest_time = sorted(weather_data_by_time.keys())[0]
    closest_data = weather_data_by_time[closest_time]

    return CourseWeather(
        timestamp=closest_time,
        temperature_c=closest_data.get("Temperature"),
        wind_speed_ms=closest_data.get("WindSpeedMS"),
        wind_direction_deg=closest_data.get("WindDirection"),
        weather_code=closest_data.get("WeatherSymbol3"),
    )
