import pandas as pd
from random import randint
from suntime import Sun, SunTimeException
from datetime import datetime, timedelta, timezone
from dotenv import find_dotenv, load_dotenv
import os



def makelist(count):
    return [randint(1, 100) for _ in range(count)]

test_optimal = {'temperature_2m': 20,
        'cloudcover': 5,
        'windspeed_10m': 0}

test_forecast = {'temperature_2m':makelist(200),
                 'cloudcover': makelist(200),
                 'windspeed_10m': makelist(200)
}

def measure_running_conditions(optimal_values, forecasted_values):

    '''helper function to measure difference between two lists, one containing
    forecasted conditions and one containing actual conditions. Returns MAPE scaled to 0-10 range'''

    score = sum([(abs(float(i) - float(j))/i)*10 for i, j in zip(optimal_values, forecasted_values)])/len(optimal_values)
    return score


def find_optimal_window(optimal_conditions, forecasted_conditions, max_window):

    '''takes forecasts of temperature and returns tuples cotnaining the optimal indices to go on a run
    ranked from best to worst

    INPUT:
        optimal_conditions: dict
            contains (feature: optimal_condition) pair where feature is wind, temp, etc in int form
        forecasted_conditions: dict
            contains (feature: forecast) pair where feature is wind, temp, etc and forecast is a list
        
    RETURNS:
        ranked_windows: list
            list of tupples containing the start/stop time for optimal runs
            ex. [(start1, stop1), (start2, stop2),...,(startn, stopn)]
    
    '''

    ranking_indice, ranking = [],[]
    
    factor_keys = list(optimal_conditions.keys())
    optimal_values = [optimal_conditions[i] for i in factor_keys]
    # Iterating through all indices and evaluating score
    for indice in range(len(forecasted_conditions[factor_keys[0]])):

        # returning forecasted values at current timestep
        forecasted_values = [forecasted_conditions[i][indice] for i in factor_keys]

        # evaulating quality at current indice
        current_score = measure_running_conditions(optimal_values, forecasted_values)
        ranking_indice.append(indice)
        ranking.append(current_score)

    # normalizing score to 1-10 scale
    min_val = min(ranking)
    max_val = max(ranking)
    normalized_score = [1 + 9 * (x - min_val) / (max_val - min_val) for x in ranking]
    score_df = pd.DataFrame({'Indice': ranking_indice,
                             'Score': normalized_score})
    return score_df



# Testing function
#score = find_optimal_window(test_optimal, test_forecast, 1000)
#print(score)

def return_nightimes(df, x):

    """takes input series of dates and returns a series two lists
    one of daytime start and one of nightime start to span series"""

    # loading environmental variables
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    LATITUDE = float(os.getenv("LATITUDE"))
    LONGITUDE = float(os.getenv("LONGITUDE"))
    df = df.sort_values(by = 'time', ascending = True)
    
    # sunrise/sunset times
    sun = Sun(LATITUDE, LONGITUDE)
    today_sr = sun.get_sunrise_time()
    today_ss = sun.get_sunset_time()
    test = df['time'].to_list()[0]
    test_localized = test.tz_localize('America/Los_Angeles')
    delta = (test_localized - today_sr).days

    # unique_dates
    df['time_mod'] = df['time'].dt.date
    unique_dates = df['time_mod'].unique()
    # calculating start and end series
    start_series = [today_sr + timedelta(days = delta + i) for i in range(len(unique_dates)+2)]
    end_series = [today_ss + timedelta(days = delta + i) for i in range(len(unique_dates)+2)]

    # note above series are in utc, need to subract x hours for time zone conversion
    start_series = [i - timedelta(hours=x) for i in start_series]
    end_series = [i - timedelta(hours=x) for i in end_series]

    return start_series, end_series



def get_current_conditions(df: pd.DataFrame, temp_col: str, wind_col: str, time: str) -> dict:

    '''Takes input dataframe of ourly weather data, and outputs the weather conditions at the specified time'''

    filtered_df = df[df['time'] == time].reset_index(drop = True)
    output = {
        temp_col: filtered_df[temp_col][0],
        wind_col: filtered_df[wind_col][0],
        'cloudcover': filtered_df['cloudcover'][0],
        'precipitation_probability': filtered_df['precipitation_probability'][0]
    }
    return output

def convert_to_am_pm(hour: str):

    """Converts 24-hour time to 12-hour AM/PM format."""

    # removing leading 0 and converting to int
    hour_converted = hour
    if hour[0] == "0":
        hour_converted = int(hour[1])
    else:
        hour_converted = int(hour)


    if 0 < hour_converted <= 12:
        return f"{hour_converted} AM"
    elif hour == 0:
        return "12 AM"
    else:
        return f"{hour_converted - 12} PM"


