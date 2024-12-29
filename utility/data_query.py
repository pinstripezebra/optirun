from openmeteopy import OpenMeteo
from openmeteopy.hourly import HourlyForecast
from openmeteopy.daily import DailyForecast
from openmeteopy.options import ForecastOptions
from itertools import product
import pandas as pd
import os
from dotenv import find_dotenv, load_dotenv
from geopy.geocoders import Nominatim
import psycopg2



def return_single_point(latitude, longitude, forecast_days = 3):

    """
    returns weather data from a single latitude/longitude coordinate
    """

    hourly = HourlyForecast()
    # Extracting latitude and longtitude for call

    # Defining variables we want to return
    hourly = hourly.temperature_2m()
    hourly = hourly.cloudcover()
    hourly = hourly.windspeed_10m()

    # Selecting options
    options = ForecastOptions(latitude = latitude, 
                                longitude = longitude,
                                forecast_days=forecast_days,
                                timezone="America/Los_Angeles")
                                

    # Pulling Data
    client = OpenMeteo(options, hourly)

    # Download data
    sample = client.get_pandas()
    sample['latitude'] = latitude
    sample['longitude'] = longitude
    sample['location'] = str((latitude, longitude))
    return sample


def return_surrounding_weather(latitude, longitude, margin = 0.01, forecast_days = 3):
    
    """
    returns weather data for a central point + performs a gridsearch for points offset by
    a given margin
    """

    latitudes = [latitude, latitude + margin, latitude - margin]
    longitudes = [longitude, longitude + margin, longitude - margin]

    # all locations to query
    locations = list(product(latitudes, longitudes))
    output_data = []
    for location in locations:
        sample = return_single_point(location[0], location[1], forecast_days)
        output_data.append(sample)

    combined_weather_data = pd.concat(output_data)
    return combined_weather_data

def data_pipeline(repull_data, latitude, longitude):

    """
    Returns dataset for application either by querying the api or loading the latest downloaded dataset
    INPUT:
        repull_data: boolean,
            Whether to repull data or load
        latitude: float,
            latitude to pull data from
        longitude: float,
            longitude to pull data from
    OUTPUT:
        df: dataframe
            contains weather data
    """

    df = ""
    parent_path = str(os.path.dirname(os.path.dirname(__file__)))
    total_path = parent_path + '/Data/' 
    file_name = 'weather_data.csv'

    # repull data and save it
    if repull_data:
        df = return_single_point(latitude, longitude, forecast_days = 3)

        # converting to imperial
        df['temperature_F'] = df['temperature_2m'] * 1.8 + 32
        df['windspeed_MPH'] = df['windspeed_10m'] * 0.621371

        # rounding columns
        df.temperature_F = df.temperature_F.round(2)
        df.windspeed_MPH = df.windspeed_MPH.round(2)

        # writing output
        df.to_csv("Data/weather_data.csv")

    # if we want to load old data
    else:
        df = pd.read_csv('Data/weather_data.csv')
    return df

def read_file_into_string(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content

def retrieve_users():

    '''returns user login information for authentication purposes'''

    # retrieving query
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    filename = 'queries/retrieve_users.txt'
    query = read_file_into_string(filename)

    # retrieiving server + database information
    server = os.getenv("SERVER")
    db= os.getenv("DB_NAME")

    # defining connection string
    conn = psycopg2.connect(os.environ.get("POST_DB_LINK"), sslmode='require')

    #connection = conn.cursor() 
    df = pd.read_sql(query, conn) 

    return df


def validate_registration(name: str, password: str, latitude: str, longitude: str):

    """Checks to ensure user registration information meets requirements"""

    error = ""
    if len(name) < 6:
        error = "Username must be at least 6 characters"
    elif len(password) < 6:
        error = "password must be at least 6 characters"
    elif not any(char.isnumeric() for char in password):
        error = "password must contain a number"
    elif not any(char.isalpha() for char in password):
        error = "password must contain a letter"
    elif not any(not c.isalnum() for c in password):
        error = "password must contain a special character"
    else:
        error = "no error"
    return error

def insert_user(name: str, password: str, latitude: str, longitude: str):
    """
    Registers user to database
    """
    # retrieving query
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    filename = 'queries/add_user.txt'

    # Passing input parameters
    insertion = read_file_into_string(filename)
    insertion = insertion.format(name1 = "'" + name + "'" ,
                                    password1 = "'" + password + "'" ,
                                    latitude1 = "'" + latitude + "'" ,
                                    longitude1 = "'" + longitude + "'",
                                    admin_status1 = 0)
    print(insertion)
    # retrieiving server + database information
    server = os.getenv("SERVER")
    db= os.getenv("DB_NAME")

    # defining connection string
    conn = psycopg2.connect(os.environ.get("POST_DB_LINK"), sslmode='require')
        
    # defining cursor and executing insertion
    cursor = conn.cursor()
    cursor.execute(insertion)
    conn.commit()


def search_address(address):

    '''simple function for converting an address to latitude/longitude'''

    geolocator = Nominatim(user_agent="ram")
    location = geolocator.geocode(address, timeout=10000, language = 'en')
    if location:
        return location.latitude, location.longitude
    else:
        return 0, 0
    

def retrieve_user_from_db(username):

    '''returns login information for single user'''

    # retrieving query
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    filename = 'queries/retrieve_user.txt'
    query = read_file_into_string(filename).format(username = "'" + username + "'")

    # retrieiving server + database information
    server = os.getenv("SERVER")
    db= os.getenv("DB_NAME")

    # defining connection string
    conn = psycopg2.connect(os.environ.get("POST_DB_LINK"), sslmode='require')

    #connection = conn.cursor() 
    df = pd.read_sql(query, conn) 

    return df
