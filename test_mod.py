#unit testing - test_mod.py
import covid_daily_briefing
from datetime import datetime
import json

date1 = datetime.strptime("2020-12-10", '%Y-%m-%d').date()
date2 = datetime.strptime("2020-12-04", '%Y-%m-%d').date()

with open('config.json', 'r') as f:
    config = json.load(f)
    keys = config["API-keys"]
    covid_daily_briefing.weather_key = keys["weather"]
    covid_daily_briefing.news_key = keys["news"]
    user_info = config["information"]
    covid_daily_briefing.city_name = user_info["city"]

def tests():

    assert covid_daily_briefing.seconds_between_dates(date1, date2) == (24 * 6 * 60 * 60)

    print("MATHS TESTS PASSED!")

    #api tests

    assert type(covid_daily_briefing.news_api()) == dict

    date, new_cases, total_cases, new_deaths, total_deaths = covid_daily_briefing.covid_statistics(covid_daily_briefing.covid_api())

    assert type(date) == str

    assert type(new_cases) == int

    assert type(total_cases) == int

    assert type(new_deaths) == int

    assert type(total_deaths) == int

    current_temperature, current_pressure, current_humidity, weather_description = covid_daily_briefing.weather_api()

    assert type(current_temperature) == float

    assert type(current_pressure) == int

    assert type(current_humidity) == int

    assert type(weather_description) == str

    print("API TESTS PASSED!")

    assert type(covid_daily_briefing.get_notifications()) == list

    assert type(covid_daily_briefing.filter_news(covid_daily_briefing.news_api()["articles"][0], "")) == dict

    print("DATA STRUCTURE TESTS PASSED!")

    print("The other functions can olny be tested using the website itself. You can access them by doing: '/', '/tts_request', and '/index'")


try:
    tests()
except AssertionError as message:
    print(message)
