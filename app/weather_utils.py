import os
import socket
import logging

from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
from flask import redirect

load_dotenv()


def get_data(user_city_input):
    API_KEY = os.getenv('API_KEY')
    if API_KEY is None:
        print("API_KEY Error!!!!!")
    url = f'https://api.openweathermap.org/data/2.5/weather?q={user_city_input}&units=metric&appid={API_KEY}'

    try:
        req = requests.get(url)
    except:
        return "API Error"

    if req.status_code == 200:  # request from api succeed
        data = req.json()  # method to pars the json file
        code = data['cod']
        country = data['sys']['country']
        city = data['name']
        lon = data['coord']['lon']
        lat = data['coord']['lat']
        forecast = get_weather(lon, lat)
        if forecast == "API Error":
            return "API Error"
        return {      # Returns dictionary of values to the HTML file
            "code": code,
            "host_name": socket.gethostname(),
            "country": country,
            "city": city,
            "forecast": forecast
        }
    return req.status_code


def get_weather(lon, lat):
    # create a list of days names when the first element is the correct day
    dt = datetime.now().date()
    day_of_week = [(dt + timedelta(days=i)).strftime('%A') for i in range(7)]

    url = (f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude='
           f'{lon}&hourly=temperature_2m,relative_humidity_2m&timezone=auto')

    try:
        req = requests.get(url)
    except:
        return "API Error"

    if req.status_code == 200:  # request from api succeed
        data = req.json()  # method to pars the json file
        # print(data)
        dict_value_of_hourly_key = data['hourly']
        time = dict_value_of_hourly_key['time']
        humidity = dict_value_of_hourly_key['relative_humidity_2m']
        temperature = dict_value_of_hourly_key['temperature_2m']
        hour_counter = 6  # sampleing data at 06:00 am & +12 (pm)
        day_counter = 0
        list_of_dict_of_week = []
        # the loop runs thrue the lists of data (168 sempels of time, temp &humidity)
        while hour_counter < 168:  # The data divided to 168 hours of 7 days
            day = {"time": time[hour_counter], "day_of_week": day_of_week[day_counter],
                   "temperature_m": temperature[hour_counter], "temperature_e": temperature[hour_counter + 12],
                   "humidity": humidity[hour_counter]}
            list_of_dict_of_week.append(day)
            day_counter += 1
            hour_counter += 24
        return list_of_dict_of_week
    return req.status_code
