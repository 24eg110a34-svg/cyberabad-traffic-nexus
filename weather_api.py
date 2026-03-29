"""
CYBERABAD TRAFFIC NEXUS - Weather API Integration
Fetches real weather data and calculates traffic impact
"""

import requests
import json
import random
from datetime import datetime
from database import save_weather, log_event

# OpenWeatherMap API (free tier)
# Get your API key from: https://openweathermap.org/api
WEATHER_API_KEY = "demo_key"  # Replace with actual API key
CITY = "Hyderabad,IN"

def get_weather_from_api():
    """Fetch weather from OpenWeatherMap API"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": CITY,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 10000) / 1000,
                "rain_probability": data.get("rain", {}).get("1h", 0),
                "source": "OpenWeatherMap"
            }
    except Exception as e:
        log_event("ERROR", "WeatherAPI", f"API fetch failed: {str(e)}")
    
    return None

def get_simulated_weather():
    """Get simulated weather for Hyderabad based on time of year"""
    month = datetime.now().month
    
    # Hyderabad weather patterns
    if month in [6, 7, 8, 9]:  # Monsoon
        conditions = ["Rain", "Heavy Rain", "Light Rain", "Cloudy", "Storm"]
        weights = [0.3, 0.2, 0.25, 0.2, 0.05]
        base_temp = random.uniform(24, 28)
        rain_prob = random.uniform(0.6, 1.0)
    elif month in [3, 4, 5]:  # Summer
        conditions = ["Clear", "Hot", "Partly Cloudy", "Haze"]
        weights = [0.4, 0.3, 0.2, 0.1]
        base_temp = random.uniform(32, 42)
        rain_prob = random.uniform(0, 0.2)
    else:  # Winter
        conditions = ["Clear", "Fog", "Cloudy", "Cool"]
        weights = [0.5, 0.2, 0.2, 0.1]
        base_temp = random.uniform(15, 26)
        rain_prob = random.uniform(0, 0.15)
    
    condition = random.choices(conditions, weights=weights)[0]
    
    humidity = random.uniform(40, 85) if "Rain" not in condition else random.uniform(75, 95)
    wind_speed = random.uniform(5, 25)
    visibility = 10 if condition == "Clear" else random.uniform(2, 6) if "Fog" in condition else random.uniform(4, 8)
    
    return {
        "condition": condition,
        "description": get_condition_description(condition),
        "temperature": round(base_temp, 1),
        "humidity": round(humidity, 1),
        "wind_speed": round(wind_speed, 1),
        "visibility": round(visibility, 1),
        "rain_probability": round(rain_prob, 2),
        "source": "Simulated"
    }

def get_condition_description(condition):
    """Get weather condition description"""
    descriptions = {
        "Clear": "Clear skies",
        "Rain": "Light rain",
        "Heavy Rain": "Heavy rainfall",
        "Storm": "Thunderstorm",
        "Cloudy": "Overcast clouds",
        "Fog": "Dense fog",
        "Hot": "High temperature",
        "Haze": "Dust haze",
        "Partly Cloudy": "Partly cloudy",
        "Cool": "Cool temperature"
    }
    return descriptions.get(condition, "Unknown")

def calculate_weather_impact(weather_data):
    """Calculate weather impact on traffic"""
    condition = weather_data.get("condition", "Clear")
    rain_prob = weather_data.get("rain_probability", 0)
    visibility = weather_data.get("visibility", 10)
    wind_speed = weather_data.get("wind_speed", 10)
    
    impact_score = 1.0
    
    # Rain impact
    if "Rain" in condition:
        if condition == "Heavy Rain":
            impact_score *= 1.4
        elif condition == "Storm":
            impact_score *= 1.6
        else:
            impact_score *= 1.2
        impact_score *= (1 + rain_prob * 0.3)
    
    # Visibility impact
    if visibility < 2:
        impact_score *= 1.3
    elif visibility < 5:
        impact_score *= 1.15
    
    # Wind impact
    if wind_speed > 20:
        impact_score *= 1.1
    
    # Hot weather impact
    if condition == "Hot" and weather_data.get("temperature", 25) > 38:
        impact_score *= 1.15
    
    return round(impact_score, 2)

def get_traffic_recommendation(weather_data):
    """Get traffic recommendations based on weather"""
    condition = weather_data.get("condition", "Clear")
    temp = weather_data.get("temperature", 25)
    
    recommendations = []
    
    if "Rain" in condition:
        recommendations.append({
            "type": "warning",
            "message": "Reduced speed advised due to rain",
            "speed_reduction": "20-30%"
        })
        recommendations.append({
            "type": "info",
            "message": "Increased congestion expected",
            "congestion_increase": "15-25%"
        })
    
    if condition == "Fog":
        recommendations.append({
            "type": "warning",
            "message": "Low visibility - use fog lights",
            "speed_reduction": "40-50%"
        })
    
    if temp > 40:
        recommendations.append({
            "type": "info",
            "message": "Extreme heat - check vehicle cooling systems",
            "speed_reduction": "10-15%"
        })
    
    if not recommendations:
        recommendations.append({
            "type": "info",
            "message": "Normal driving conditions",
            "speed_reduction": "0%"
        })
    
    return recommendations

def get_weather_for_display():
    """Get weather data for dashboard display"""
    # Try API first, fall back to simulation
    weather = get_weather_from_api()
    
    if not weather:
        weather = get_simulated_weather()
        log_event("INFO", "Weather", "Using simulated weather data")
    
    impact = calculate_weather_impact(weather)
    weather["impact_score"] = impact
    weather["impact_description"] = get_impact_description(impact)
    weather["recommendations"] = get_traffic_recommendation(weather)
    
    # Save to database
    try:
        save_weather(
            weather["condition"],
            weather["temperature"],
            weather["humidity"],
            weather["wind_speed"],
            weather["visibility"],
            weather["rain_probability"],
            impact,
            weather["source"]
        )
    except Exception as e:
        log_event("ERROR", "Weather", f"Failed to save weather: {str(e)}")
    
    return weather

def get_impact_description(impact_score):
    """Get human-readable impact description"""
    if impact_score >= 1.5:
        return "Severe Impact - Major delays expected"
    elif impact_score >= 1.3:
        return "High Impact - Significant delays"
    elif impact_score >= 1.15:
        return "Moderate Impact - Some delays"
    elif impact_score >= 1.0:
        return "Normal Impact - Standard conditions"
    else:
        return "Low Impact - Better than normal"

# Test weather module
if __name__ == "__main__":
    weather = get_weather_for_display()
    print(json.dumps(weather, indent=2))
