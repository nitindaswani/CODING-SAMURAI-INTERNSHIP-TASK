import os
from typing import Any, Dict

import requests

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str, unit_system: str, api_key: str) -> Dict[str, Any]:
    params = {
        "q": city,
        "appid": api_key,
        "units": unit_system,
    }

    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def format_weather(data: Dict[str, Any], unit_choice: str) -> str:
    unit_symbol = "C" if unit_choice == "c" else "F"
    speed_unit = "m/s" if unit_choice == "c" else "mph"

    city_name = data.get("name", "Unknown")
    country = data.get("sys", {}).get("country", "")
    weather = data.get("weather", [{}])[0].get("description", "N/A").title()

    main = data.get("main", {})
    temperature = main.get("temp", "N/A")
    humidity = main.get("humidity", "N/A")

    wind_speed = data.get("wind", {}).get("speed", "N/A")

    return (
        f"\nWeather in {city_name}, {country}\n"
        f"{'-' * 35}\n"
        f"Condition   : {weather}\n"
        f"Temperature : {temperature} deg {unit_symbol}\n"
        f"Humidity    : {humidity}%\n"
        f"Wind Speed  : {wind_speed} {speed_unit}\n"
    )


def resolve_api_key() -> str:
    env_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if env_key:
        return env_key

    return input("Enter your OpenWeather API key: ").strip()


def main() -> None:
    print("Weather Application (OpenWeatherMap API)")
    print("Type 'exit' as city name to close the app.\n")

    api_key = resolve_api_key()
    if not api_key:
        print("API key is required. Set OPENWEATHER_API_KEY or enter it when prompted.")
        return

    while True:
        city = input("Enter city name: ").strip()
        if not city:
            print("City name cannot be empty. Please try again.\n")
            continue
        if city.lower() == "exit":
            print("Goodbye!")
            break

        unit_choice = input("Choose unit - C for Celsius, F for Fahrenheit [C/F]: ").strip().lower()
        if unit_choice not in {"c", "f"}:
            print("Invalid unit choice. Defaulting to Celsius.")
            unit_choice = "c"

        unit_system = "metric" if unit_choice == "c" else "imperial"

        try:
            data = get_weather(city, unit_system, api_key)
            print(format_weather(data, unit_choice))
        except requests.exceptions.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code == 401:
                print("Invalid API key. Please verify your key and try again.\n")
            elif status_code == 404:
                print("City not found. Please check spelling and try again.\n")
            else:
                print(f"API request failed with status code {status_code}.\n")
        except requests.exceptions.ConnectionError:
            print("Network error. Check your internet connection and try again.\n")
        except requests.exceptions.Timeout:
            print("Request timed out. Please try again.\n")
        except requests.exceptions.RequestException as exc:
            print(f"Unexpected request error: {exc}\n")
        except (KeyError, TypeError, ValueError):
            print("Received unexpected data format from API. Please try again.\n")


if __name__ == "__main__":
    main()
