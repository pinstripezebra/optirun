import sys
sys.path.append("..")

import dash
from dash import html, Dash, dcc, callback,Input, Output,dash_table, ctx
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import datetime
import numpy as np
from utility.visualization import generate_run_plot, draw_Image, draw_Text, generate_timeseries_plot, draw_Text_With_Background, draw_table
from utility.measurement import find_optimal_window, return_nightimes, get_current_conditions, convert_to_am_pm
from utility.chatbot import query_condition_description
import dash_daq as daq
from suntime import Sun, SunTimeException
from dotenv import find_dotenv, load_dotenv
import os
import json

dash.register_page(__name__, path='/landing')

# Loading json files containing component styles
CONTENT_STYLE= {}
with open('style/content_style.json') as f:
    CONTENT_STYLE = json.load(f)

# loading environmental variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
api_key = os.getenv("ANTHROPIC_API_KEY")

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
                        id="measurement-switch",
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
                "width": "80%",
                "display": "flex",
                "margin-left": "18rem",
                'opacity': '80%',
                "border": "#090b0b"})


# Defining layout
layout = html.Div([
        header,
        html.Div([
        # Adding selector for overall forecast
            html.Div([
                html.Br(),
                html.Div([

                    # Top row with filters + KPIs
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Button('7-day-forecast', color = 'primary', id='forecast-click1',className="btn active", n_clicks=0),
                                dbc.Button('1-day-forecast', color = 'primary', id='forecast-click2',className="me-1", n_clicks=0),
                                ]),
                            html.Div(children= [
                            html.P('Choose the type of forecast', className = 'text'),
                            html.Div([
                                dbc.Button('Overall Forecast', color = 'primary', id='overall-click',className="btn active", n_clicks=0),
                                dbc.Button('temp',  color = 'primary', id='temp-click',className="me-1", n_clicks=0),
                                dbc.Button('wind',  color = 'primary', id='wind-click',className="me-1", n_clicks=0),
                                dbc.Button('cloud',  color = 'primary', id='cloud-click',className="me-1", n_clicks=0)
                            ])

                            ])
                        ], style = {"display":"inline-block"}),

                    ])

                ])
            ]),
        # Adding filter for forecast period
        html.Div([
                    dbc.Row([
                        dbc.Col([
                            
                            html.Div(children= [
                                html.H3('Running Condition Forecast'),
                            ]),
                        ]),
                    ]),
        html.Div([
                    dbc.Row([ 
                            # Div for forecast
                            dbc.Col([
                                #html.Div([], id='test-forecast-out')
                                dcc.Graph(id='test-forecast-out')

                            ]),
                            dbc.Col([
                                html.Div([
                                    html.H3(id = 'kpi-time'),
                                ], style={'text-indent': '80px'}),
                                # Div for kpis
                                html.Div([], id='kpi-indicators'),
                                html.Div(html.H3('Placeholder'))#[draw_Text(query_condition_description(api_key, 
                                                                #                [df1['temperature_2m'][0],
                                                                #                df1['windspeed_10m'][0],
                                                                #               df1['cloudcover'][0]]))])
                            ])
                        ]) ,

                        
                    ])
            ]),
        ], style=CONTENT_STYLE)
])



# callback for weekly forecast for individual series(temp, wind, etc)
@callback(
    Output(component_id='test-forecast-out', component_property='figure'),
    Input('forecast-click1', 'n_clicks'),
    Input('forecast-click2', 'n_clicks'),
    Input('temp-click', 'n_clicks'),
    Input('wind-click', 'n_clicks'),
    Input('cloud-click', 'n_clicks'),
    Input('overall-click', 'n_clicks'),
    Input("measurement-switch", 'value'),
    Input('stored-forecast', 'data'),


)
def update_timeseries(button1, button2, button3, button4, button5, button6, switch, df1):

    filtered_df = pd.read_json(df1, orient='split')
    filtered_df ['time'] = pd.to_datetime(filtered_df['time'])


    # if we're filtering for only 1 day
    if "forecast-click2" == ctx.triggered_id:
        filtered_df = filtered_df[filtered_df['time'].dt.date <  filtered_df['time'].dt.date.min() + datetime.timedelta(days=1)]
    time_fig = ""
    forecast_type = "temperature_2m"

    if 'wind-click'== ctx.triggered_id:
        if 'Metric' in switch:
            forecast_type = ['windspeed_10m']
        else:
            forecast_type = ['windspeed_MPH']
    elif 'cloud-click' == ctx.triggered_id:
        forecast_type = ['cloudcover']
    elif 'temp-click' == ctx.triggered_id:
        if 'Metric' in switch:
            forecast_type = ['temperature_2m']
        else:
            forecast_type = ['temperature_F']
    
    # If none of the above then show all data
    else:
        if 'Metric' in switch:
            forecast_type = ['Forecast_Score', 'windspeed_10m', 'cloudcover', 'temperature_2m']
        else:
            forecast_type = ['Forecast_Score', 'windspeed_MPH', 'cloudcover', 'temperature_F']

    # Creating graph figure
    timezone_offset = 8
    s1, s2 = return_nightimes(filtered_df, timezone_offset)
    time_fig = generate_timeseries_plot(filtered_df, 'time', forecast_type, s1, s2)

    return time_fig
    
    

# callback for kpi's
@callback(
    Output(component_id='kpi-indicators', component_property='children'),
    Input('forecast-click1', 'n_clicks'),
    Input('forecast-click2', 'n_clicks'),
    Input("measurement-switch", 'value'),
    Input('test-forecast-out', 'hoverData'),
    Input('stored-forecast', 'data'),
    Input('optimal-conditions', 'data')
)

def update_kpi(val1, val2, switch, hoverData, df1, optimalconditions):


    filtered_df = pd.read_json(df1, orient='split')
    filtered_df ['time'] = pd.to_datetime(filtered_df['time'])

    time_selected = filtered_df['time'].min()
    # if data has been selected update hilter point
    if hoverData is not None:
        time_selected = hoverData['points'][0]['x']
    
    temp, wind, cloud, prec = "", "", "", ""
    temp_trailer, wind_trailer = "", ""
    if 'Metric' in switch:
        filtered_df = get_current_conditions(filtered_df, 'temperature_2m', 'windspeed_10m', time_selected)
        temp = filtered_df['temperature_2m']
        wind = filtered_df['windspeed_10m']
        temp_trailer = 'C'
        wind_trailer = 'KPH'
    else:
        filtered_df = get_current_conditions(filtered_df, 'temperature_F','windspeed_MPH', time_selected)
        temp = filtered_df['temperature_F']
        wind = filtered_df['windspeed_MPH']
        temp_trailer = 'F'
        wind_trailer = 'MPH'
    
    cloud = filtered_df['cloudcover']
    prec = filtered_df['precipitation_probability']

    # Extracting optimal conditions from user preference
    ideal_temp = optimalconditions['temperature_2m']
    ideal_wind = optimalconditions['windspeed_10m']
    ideal_cloud = optimalconditions['cloudcover']
    ideal_prec = optimalconditions['precipitation_probability']

    return dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            draw_Text_With_Background(int(temp), ideal_temp, chr(176) + temp_trailer, "./assets/temperature.png", 150)
                        ], width=4),
                        dbc.Col([
                                draw_Text_With_Background(int(wind), ideal_wind,wind_trailer, "./assets/wind.png", 150)
                        ], width=4)
                    ], style = {'margin-left': '0px',
                            "width": "80%",
                            "padding": "0rem 0rem"}),
                    dbc.Row([
                        dbc.Col([
                                draw_Text_With_Background(int(cloud),ideal_cloud, '%', "./assets/clouds.png", 150)
                        ], width=4),
                        dbc.Col([
                                draw_Text_With_Background(int(prec),ideal_prec, '%', "./assets/rain.png", 150)
                        ], width=4)
                    ], style = {'margin-left': '0px',
                            "width": "80%",
                            "padding": "0rem 0rem"})
                ], 
)


# callback for kpi time
@callback(
    Output(component_id='kpi-time', component_property='children'),
    Input('test-forecast-out', 'hoverData')
)

def update_kpi(hoverData):

    date, am_pm = 0, 'pm'
    # If hoverdata is not none use this for date/time
    if hoverData is not None:
        time_selected = hoverData['points'][0]['x']
        hours = time_selected[-5:][:2]

        # converting 00 - 24 to am_pm format
        am_pm = convert_to_am_pm(hours)

        date = time_selected[5:10]
    return 'Forecast {time}'.format(time = str(date) + ", " + am_pm)
    
    

@callback(
    [Output("forecast-click1", "className"), 
     Output("forecast-click2", "className")],
    [Input("forecast-click1", "n_clicks"),
     Input("forecast-click2", "n_clicks") ],
)
def set_active_forecast_window(*args):
    ctx = dash.callback_context

    if not ctx.triggered or not any(args):
       return ["btn active"] + ["btn" for _ in range(1, 2)] 
    # get id of triggering button
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return [
        "btn active" if button_id == "forecast-click1" else "btn",
        "btn active" if button_id == "forecast-click2" else "btn" 
    ]

@callback(
    [Output("overall-click", "className"), 
     Output("temp-click", "className"),
     Output("wind-click", "className"),
     Output("cloud-click", "className")],
    [Input("overall-click", "n_clicks"),
     Input("temp-click", "n_clicks"),
     Input("wind-click", "n_clicks"),
     Input("cloud-click", "n_clicks")] ,
)
def set_active_forecast_type(*args):
    ctx = dash.callback_context
    if not ctx.triggered or not any(args):
       return ["btn"] + ["btn active"] + ["btn" for _ in range(1, 2)] 

    # get id of triggering button
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return [
        "btn active" if button_id == "overall-click" else "btn",
        "btn active" if button_id == "temp-click" else "btn", 
        "btn active" if button_id == "wind-click" else "btn",
        "btn active" if button_id == "cloud-click" else "btn"
    ]
