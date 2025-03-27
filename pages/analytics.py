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
import json
import time

dash.register_page(__name__, path='/analytic')

# loading environmental variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
api_key = os.getenv("ANTHROPIC_API_KEY")

# Loading json files containing component styles
CONTENT_STYLE= {}
with open('style/content_style.json') as f:
    CONTENT_STYLE = json.load(f)
kpi_card_body = {
    'color': 'black', 
    'opacity': '0.8',
    'background':'LightGray',
    'width':"36rem"
}

# defining header
header = html.Div([
        html.H3('Choosing the best time to be out and about.', style={'display': 'inline' }),
        html.Div([
            html.P('Imperial',style={'display': 'inline' }),
            html.Div([
                dbc.Checklist(
                        options=[
                            {"label": " ", "value": "Metric"},
                        ],
                        value=[1],
                        id="measurement-switch-analytic",
                        switch=True,
                        inline = True,
                        style={'display': 'inline' }
                ),
            ],style={'display': 'inline' ,
                 'margin-left': '12px'}),
            html.P('Metric',style={'display': 'inline' }),
        ],style={'display': 'inline' ,
                 'margin-left': '600px'}),
    ], style = {"background-color": "#DCDCDC",
                "width": "85%",
                "display": "flex",
                "margin-left": "18rem",
                'opacity': '80%',
                "border": "#090b0b"})

layout = html.Div([
    header,
        html.Div([
        html.H1('Running Outlook Today'),
        html.Div([], id = 'running-gauges'),
        html.Div([],style= {'width': '80%'}, id='best-times-forecast'),
        html.H3('Condition Overview'),
        dbc.Row([
            html.Div([], id = 'forecast-figure')
        ]),
        html.Br(),
    ], style = CONTENT_STYLE)
])


# callback for running gauges
@callback(
    Output(component_id='running-gauges', component_property='children'),
    Output(component_id='best-times-forecast', component_property='children'),
    Output(component_id='forecast-figure', component_property='children'),
    Input('stored-forecast', 'data'),
    Input('location-storage', 'data'),
    Input("measurement-switch-analytic", 'value')
)
def update_timeseries(df, location, switch):

    # reading in dataframe from store
    filtered_df = pd.read_json(df, orient='split')
    filtered_df['time'] = pd.to_datetime(filtered_df['time'])

    # determining optimal start/stop times
    next_12_hours = filtered_df.head(12)
    best_bucket = next_12_hours[next_12_hours['Forecast_Score'] == next_12_hours['Forecast_Score'].max()]
    start_time = best_bucket['time'].to_list()[0]
    end_time = start_time + timedelta(hours=1)

    # best forecast return
    best_forecast = draw_Text(html.P("The best expected running time today is between {start} and {end}.".format(start = start_time, end = end_time)), kpi_card_body ),

    gauges, forecast_return = "", ""
    # If we want to use metric
    if 'Metric' in switch:
        gauges = dbc.Row([
                    dbc.Col([
                            draw_Image(generate_run_plot(filtered_df, 'Forecast_Score')), 
                        ],  
                    width={"size": 6, "offset": 0}),
                    dbc.Col([
                            dbc.Row([
                                draw_Image(generate_gauge_plot(filtered_df, 'temperature_2m'), 200)
                            ]),
                            dbc.Row([
                                draw_Image(generate_gauge_plot(filtered_df, 'cloudcover'), 200)
                            ]),
                            dbc.Row([
                                draw_Image(generate_gauge_plot(filtered_df, 'windspeed_10m'), 200)
                            ]),
                        ]) 
                ])
        
        # forecast return
        forecast_return = draw_Text(query_condition_description(api_key, [best_bucket['temperature_2m'].to_list()[0],
                                                            best_bucket['windspeed_10m'].to_list()[0],
                                                            best_bucket['cloudcover'].to_list()[0]]), kpi_card_body )
        
    # if our units are imperial
    else:
        gauges = dbc.Row([
                    dbc.Col([
                            draw_Image(generate_run_plot(filtered_df, 'Forecast_Score')), 
                        ],  
                    width={"size": 6, "offset": 0}),
                    dbc.Col([
                            dbc.Row([
                                draw_Image(generate_gauge_plot(filtered_df, 'temperature_F'), 200)
                            ]),
                            dbc.Row([
                                draw_Image(generate_gauge_plot(filtered_df, 'cloudcover'), 200)
                            ]),
                            dbc.Row([
                                draw_Image(generate_gauge_plot(filtered_df, 'windspeed_MPH'), 200)
                            ]),
                        ]) 
                ])
        
        # forecast return
        forecast_return = draw_Text(query_condition_description(api_key, [best_bucket['temperature_F'].to_list()[0],
                                                            best_bucket['windspeed_MPH'].to_list()[0],
                                                            best_bucket['cloudcover'].to_list()[0]]),kpi_card_body )

    return  best_forecast, gauges, forecast_return