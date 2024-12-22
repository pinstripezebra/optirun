import dash
import os
from dash import html, dcc, callback, Input, Output
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
from utility.visualization import generate_run_plot
from utility.visualization import generate_run_plot, draw_Image, draw_Text, generate_gauge_plot
from dotenv import find_dotenv, load_dotenv
from utility.measurement import find_optimal_window, return_nightimes
from utility.chatbot import query_condition_description

dash.register_page(__name__, path='/analytic')

# Note will need to pass these in from app
df1 = pd.read_csv("Data\\weather_data.csv")
df1['time'] = pd.to_datetime(df1['time'])

# loading environmental variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
api_key = os.getenv("ANTHROPIC_API_KEY")
optimal_conditions = {'temperature_2m': float(os.getenv("OPTIMAL_TEMP")),
                      'cloudcover': float(os.getenv("OPTIMAL_CLOUD")),
                      'windspeed_10m': float(os.getenv("OPTIMAL_WIND"))}
forecasted_conditions = {'temperature_2m': df1['temperature_2m'].to_list(),
                         'cloudcover': df1['cloudcover'].to_list(),
                         'windspeed_10m': df1['windspeed_10m'].to_list()}

# Rating weather conditions
max_window = len(df1['temperature_2m'].to_list())
conditions = find_optimal_window(optimal_conditions, forecasted_conditions, max_window)

# Adding forecast to dataframe
df1['Forecast_Score'] = conditions['Score']

# determining optimal start/stop times
next_12_hours = df1.head(12)
best_bucket = next_12_hours[next_12_hours['Forecast_Score'] == next_12_hours['Forecast_Score'].max()]
start_time = best_bucket['time'].to_list()[0]
end_time = start_time + timedelta(hours=1)


layout = html.Div([
    html.H1('Running Outlook Today'),
    html.Div([
    draw_Text(html.P("The best expected running time today is between {start} and {end}.".format(start = start_time, end = end_time))),

    ],style= {'width': '50%'}),
    html.H3('Condition Overview'),
    dbc.Row([
        html.Div([
            draw_Text(query_condition_description(api_key, [best_bucket['temperature_2m'].to_list()[0],
                                                        best_bucket['windspeed_10m'].to_list()[0],
                                                        best_bucket['cloudcover'].to_list()[0]]))
        ])
    ]),
    html.Br(),

   # Generates a graph of the forecast
    html.Div([
        dbc.Row([
            dbc.Col([
                    draw_Image(generate_run_plot(df1, 'Forecast_Score')), 
                ],  
            width={"size": 6, "offset": 0}),
            dbc.Col([
                    dbc.Row([
                        draw_Image(generate_gauge_plot(df1, 'temperature_2m'), 200)
                    ]),
                    dbc.Row([
                        draw_Image(generate_gauge_plot(df1, 'cloudcover'), 200)
                    ]),
                    dbc.Row([
                        draw_Image(generate_gauge_plot(df1, 'windspeed_10m'), 200)
                    ]),

                 ]) 
        ])
            
    ])
])


