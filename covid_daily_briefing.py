from flask import Flask
from flask import request
from flask import render_template
from datetime import datetime
import time_conversions
import pyttsx3
import time
import sched
import json
from pip._vendor import requests
from uk_covid19 import Cov19API
import logging

app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)
list_of_alarms = []
safe_news = []
notifications = []
last_refresh = datetime.now()

with open('config.json', 'r') as f:
    config = json.load(f)
    keys = config["API-keys"]
    weather_key = keys["weather"]
    news_key = keys["news"]
    user_info = config["information"]
    city_name = user_info["city"]


@app.route('/tts_request') 
def tts_request(announcement:str="Text to speech example announcement!"):
    engine = pyttsx3.init()
    engine.say(announcement)
    engine.runAndWait()
    return announcement

@app.route('/index')
def index():
    """

This section is the main section of the code. It is where the user's inputs get processed.

"""
    s.run(blocking=False)
    add_alarms =  True
    now = datetime.now()
    current_date = now.date()
    current_time = now.strftime("%H:%M:%S")
    td_dates = now - last_refresh
    print(td_dates.total_seconds())
    if td_dates.total_seconds() > 1800:
        refresh_notifications()
    if request.args.get("alarm_item"):
        alarm_to_delete = request.args.get("alarm_item")
        delete_alarm(alarm_to_delete, True)
    if request.args.get("notif"):
        notif_to_delete = request.args.get("notif")
        delete_news(notif_to_delete)
    if request.args.get("alarm"):
        alarm = request.args.get("alarm")
        alarm_text = request.args.get("two")
        weather = request.args.get("weather")
        news = request.args.get("news")
        alarm_date = datetime.strptime(alarm.split("T")[0], '%Y-%m-%d').date()
        alarm_time = alarm.split("T")[1]
        if alarm_time:
            tts_request("Alarm set.")
            print(alarm_date)
            print(alarm_time)
            print(current_date)
            print(current_time)
            alarm_text = alarm_text + "... " + safe_news[0]["title"] + " " + safe_news[0]["briefing"] + "."
            if weather == "weather":
                alarm_text = alarm_text + "! Today's current weather: " + safe_news[1]["briefing"] + "."
            if news == "news":
                alarm_text = alarm_text + " Today's top Covid-19 headlines: "
                print(safe_news)
                for headline in range(2, len(safe_news)):
                    alarm_text = alarm_text + " " + safe_news[headline]["title"] + ". " + safe_news[headline]["content"] + "."
            if alarm_date == current_date:
                delay = time_conversions.hhmm_to_seconds(alarm_time) - time_conversions.hhmmss_to_seconds(current_time)
                print(delay)
                if delay < 1:
                    tts_request("This is an ALARM! " + alarm_text)
                    add_alarms =  False
                else:
                    s.enter(int(delay),1,tts_request,("This is an ALARM! " + alarm_text,))
                    s.enter(int(delay),1,delete_alarm,(request.args.get("two"), False,))
            else:
                delay = seconds_between_dates(alarm_date, current_date) + (time_conversions.hhmm_to_seconds(alarm_time) - time_conversions.hhmmss_to_seconds(current_time))
                print(delay)
                s.enter(int(delay),1,tts_request,("This is an ALARM! " + alarm_text))
                s.enter(int(delay),1,delete_alarm,(request.args.get("two"), False,))
            if add_alarms == True:
                this_alarm = dict()
                this_alarm["title"] = request.args.get("two")
                this_alarm["content"] = str(alarm_time) + " " + str(alarm_date)
                print(this_alarm)
                list_of_alarms.append(this_alarm)
                print(s.queue)
    return hello()


@app.route('/')
def hello():
    """

This is the defult bit of the code first accessed by users before they enter an input...

"""
    print(last_refresh)
    return render_template('template.html', alarms=list_of_alarms, notifications=notifications, image='logo.jpg')

def delete_alarm(alarm_name:str, cross_pressed:bool):
    """

This function deletes alarms. This happens either when the user presses the cross on the alarm on the webpage or when the alarm goes off, hence the 'crossed_pressed' variable.

"""
    for alarms in list_of_alarms:
        if alarms["title"] == alarm_name:
            location = list_of_alarms.index(alarms)
            location = location * 2
            list_of_alarms.remove(alarms)
            if cross_pressed == True:
                s.cancel(s.queue[location])
                s.cancel(s.queue[location])
    return hello()

def delete_news(news_name):
    """

This function deletes notifications when the user presses the notification's cross.

"""
    for notification in notifications:
        if notification["title"] == news_name:
            notifications.remove(notification)
    return hello()

def refresh_notifications():
    """

This function calls the function get_notifications().

"""
    safe_news = get_notifications()
    notifications = get_notifications()
    return index()

def seconds_between_dates(date1, date2):
    """

Calculates the number of seconds between tweo given dates...

"""
    delay = (date1-date2).days * 86400
    return int(delay)

def filter_news(article, keyword: str):
    """

Filters news articles for a given 'keyword'.

"""
    notification = dict()
    if keyword in str(article['title']).lower():
        notification["title"] = (article['title'])
        notification["content"] = (article['description'])
    elif keyword in str(article['description']).lower():
        notification["title"] = (article['title'])
        notification["content"] = (article['description'])
    elif keyword in str(article['content']).lower():
        notification["title"] = (article['title'])
        notification["content"] = (article['description'])
    return notification

def get_notifications():
    """

This function creates new notifications.

"""
    fetched_notifications = []
    news = news_api()
    weather = dict()
    covid_data = dict()
    date, new_cases, total_cases, new_deaths, total_deaths = covid_statistics(covid_api())
    covid_data["title"] = "Covid-19 Information for " + str(date)
    covid_data["content"] = ("New Cases: " + str(new_cases) + "\n Total Cases: " + str(total_cases) + " \n" +
	    "Deaths in last 24 hours: " + str(new_deaths) + " Total Fatalities: " + str(total_deaths) + " \n"+
	    "Fatality Rate: " + str(round(((total_deaths/total_cases) * 100), 2)) + "%.") 
    covid_data["briefing"] = ("There are " + str(new_cases) + " new cases of Covid-19 in England in the last 24 hours, bringing the total up to " + str(total_cases) + " total cases. \n" +
	    "There have been " + str(new_deaths) + " deaths in England due to Covid-19 in the last 24 hours, bringing the total fatalities to " + str(total_deaths) + "... \n"+
	    "The current fatality rate of Covid-19 in England is " + str(round(((total_deaths/total_cases) * 100), 2)) + "%.") 
    fetched_notifications.append(covid_data)
    current_temperature, current_pressure, current_humidity, weather_description = weather_api()
    weather["title"] = "Current weather in " + city_name + ": " + str(weather_description)
    weather["content"] = ("Current Temperature: " + str(current_temperature) + "°C" +
	    "\n Atmospheric pressure: " + str(current_pressure) + " hPa \n Humidity: " + str(current_humidity) + "% \n ")
    weather["briefing"] = ("The current weather in " + city_name + " is " + str(weather_description) + ", with a temperature of " + str(current_temperature) + " degrees Celcius. The Atmospheric pressure is " +
                           str(current_pressure) + " Hectopascals. The humidity is approximately " + str(current_humidity) + "%")
    fetched_notifications.append(weather)
    articles = news["articles"]
    for article in articles:
        matching_article = filter_news(article, "covid")
        fetched_notifications.append(matching_article)
    fetched_notifications = [x for x in fetched_notifications if x]
    return fetched_notifications

def covid_statistics(x):
    """

Takes data from latest call of COVID-19 API and sorts it into variables which are returned...

"""
    y = x["data"]
    past_24_hours = y[0]
    date = past_24_hours["date"]
    new_cases = past_24_hours["newCasesByPublishDate"]
    total_cases = past_24_hours["cumCasesByPublishDate"]
    new_deaths = past_24_hours["newDeathsByDeathDate"]
    if new_deaths == None:
        new_deaths = y[1]["newDeathsByDeathDate"]
    total_deaths = past_24_hours["cumDeathsByDeathDate"]
    if total_deaths == None:
        total_deaths = y[1]["cumDeathsByDeathDate"]

    print(str(date) + " " + str(new_cases) + " " + str(total_cases) + " " + str(new_deaths) + " " + str(total_deaths))
    return date, new_cases, total_cases, new_deaths, total_deaths


def weather(x):
    """

Takes data from latest call of WEATHER API and sorts it into variables which are returned...

"""
    y = x["main"]
    current_temperature = y["temp"]
    current_temperature = round((current_temperature - 273.15), 2)
    current_pressure = y["pressure"]
    current_humidiy = y["humidity"]
    z = x["weather"]
    weather_description = z[0]["description"]
    return current_temperature, current_pressure, current_humidiy, weather_description

def news_api():
    """

Calls the NEWS API (newsapi.org) and returns it's data as a json file.

"""
    base_url = "https://newsapi.org/v2/top-headlines?"
    country = "gb"
    complete_url = base_url + "country=" + country + "&apiKey=" + news_key
    response = requests.get(complete_url)
    return(response.json())
    #filter_news(response.json(), "")
    #filter_news(response.json(), "covid")
    #filter_news(response.json(), "exeter")

def weather_api():
    """

Calls the WEATHER API (api.openweathermap.org) and returns the weather function of it's data as a variable.

"""
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + weather_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    return weather(x)

def covid_api():
    """

Calls the COVID API from the uk_covid19 module. It returns it's data as a json file.

"""
    england_only = ['areaType=nation', 'areaName=England',]
    #exeter = ['areaType=region', 'areaName=Exeter']
    cases_and_deaths = {
    "date": "date",
    "areaName": "areaName",
    "areaCode": "areaCode",
    "newCasesByPublishDate": "newCasesByPublishDate",
    "cumCasesByPublishDate": "cumCasesByPublishDate",
    "newDeathsByDeathDate": "newDeathsByDeathDate",
    "cumDeathsByDeathDate": "cumDeathsByDeathDate"
}
    apivid = Cov19API(filters=england_only, structure=cases_and_deaths)
    covid_data = apivid.get_json()
    return covid_data
    
if __name__ == '__main__':
    safe_news = get_notifications()
    notifications = get_notifications()
    logging.basicConfig(filename='pysys.log',level=logging.INFO)
    app.run()
    
