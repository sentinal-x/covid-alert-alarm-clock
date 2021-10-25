# COVID-19 Daily Briefing Tool

## Introduction

Hello! Welcome to the README for the 'COVID-19 Daily Briefing' tool. Since the
outbreak of COVID-19 the day-to-day routine for many people has been disrupted
and the instability of daily living means we have to be adaptable to current
events. Keeping up-to date with the rapidly changing infection rates and
regularly updated government guidelines has become a daily challenge for many,
as well as keeping track of the weather and plans that are often changed at
short notice. This is where the 'COVID-19 Daily Briefing' tool comes in...

This tool allows users to host a webpage with displays clear, concise, and
up-to date information on coronavirus. From this website, users can schedule
'alarms' which at a selected time alert the user of a given input message as
well as the latest COVID-19 information. They can also request the local
weather and the top headlines which are also displayed in a 'notifications'
section on the webpage. The notifications refresh every 30 minutes
(1800 seconds) allowing for the latest weather and news to be displayed to
the user. The user can also cancel alarms and remove notifications to their
liking.

## Prerequisites

Python 3.9 was used for the development of this project.

You will need two API keys. The NEWS API from 'http://newsapi.org' and the
WEATHER API from 'http://api.openweathermap.org'. Register and copy your
private API keys into the 'config.json' file.

Also in the 'config.json' file, there is a variable called 'city'. Here you can
enter the name of your nearby city for local weather information. It is by
default set to 'Exeter' but you can change it to your local city in the format
'London' or 'Southampton' etc. 

## Installation and Requirements

You will need to add your API keys to the 'config.json' file.

You will need top install a few modules using pip install. These modules are
'flask', 'pyttsx3', and 'uk_covid19'.

The pip install module commands are as such:
pip install -U Flask
pip install pyttsx3
pip install uk-covid19 

The uk_covid19 module requires Python 3.7+.

## Getting Started

To get started with the 'COVID-19 Daily Briefing' tool, simply run the
'covid_daily_briefing.py' file. Then connect to the given URL - which should
be 'http://127.0.0.1:5000/'. This will show the webpage which the user can
then use to schedule alarms and read weather and news notifications.

## Testing

To run and test the code, use the supplied 'test_mod.py' file. This runs unit
testing for the program using 'assert' and imports the main program as a
module to do so.

Some functions cannot be tested this way and can only be tested by using the
appropriate urls on the website. Further information is displayed when running
the 'test_mod.py' file.

If you come across an issue with the program, the 'pysys.log' file stores a log
of all inputs to the webpage.

## Metadata

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


## License

MIT License

Copyright (c) 2020 Simon James Puttock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.