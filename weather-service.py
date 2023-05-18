import argparse
import json
import sys
from os import system
from configparser import ConfigParser
from urllib import error, parse, request

BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

def __get_api_key():
    """Fetch the api key from a config file called Secrets.ini"""
    config = ConfigParser()
    config.read('secrets.ini')
    return config['openweather']['api_key']

def read_user_cli_args():
    """Accepts user inputs and expects a City to be entered"""
    parser = argparse.ArgumentParser(
        description="Gets weather and temperature info for a named city"
    )
    parser.add_argument(
        "City", nargs="+", type=str, help="enter the city name"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="Display the temperature in imperial units",
    )
    return parser.parse_args()

def build_weather_query(city_input, imperial=False):
    """Builds an URL request with the city input from the args"""
    api_key = __get_api_key()
    city_name = " ".join(city_input)
    url_encoded_cityname = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (f"{BASE_WEATHER_API_URL}?q={url_encoded_cityname}"
           f"&units={units}&appid={api_key}"
        ) 
    return url

def get_weather_data(query_url):
    """Makes a query to the API using the URL Query and returns a Python object with data"""
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't seem to find weather data for this particular city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")
    
    data = response.read()
    try: 
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response!")

def display_weather_info(weather_data, imperial=False):
    """Clears the screen and Displays formated output for Selected City"""
    system('clear')
    city = weather_data['name']
    weather = weather_data['weather'][0]['description']
    temp = weather_data['main']['temp']

    print(f"{city}: ", end="")
    print(f"\t{weather.title()}", end=" ")
    print(f"\t({temp}° {'F' if imperial else 'C'})")




if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.City, user_args.imperial)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data, user_args.imperial)
    
