# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import requests


def get_beijing_weather():
    api_key = "YOUR_API_KEY"  # 替换为你的和风天气API Key
    city = "Beijing"
    weather_url = f"https://devapi.qweather.com/v7/weather/now?location={city}&key={api_key}"

    response = requests.get(weather_url)
    data = response.json()

    if response.status_code == 200 and data["code"] == "200":
        weather_info = data["now"]
        temperature = weather_info["temp"]
        text = weather_info["text"]
        wind_dir = weather_info["windDir"]
        wind_scale = weather_info["windScale"]
        humidity = weather_info["humidity"]

        print(f"Current weather in Beijing: {text}, Temperature: {temperature}°C")
        print(f"Wind: {wind_dir} {wind_scale} level")
        print(f"Humidity: {humidity}%")
    else:
        print("Failed to fetch weather data.")


if __name__ == "__main__":
    get_beijing_weather()
