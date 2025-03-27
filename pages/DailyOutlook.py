import dash
import os
from dash import html, dcc, callback, Input, Output,dash_table
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
import plotly.express as px

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
        html.Div([
            dbc.Button("Download Data", id="btn_csv", outline=True, color="primary"),
            dcc.Download(id="download-dataframe-csv"),
        ],style={'display': 'inline' ,
                 'margin-left': '10px'})
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
        html.Div([ 
            dbc.Row([
                html.Div([], id='weather-row')
            ]),
            dbc.Row([
                html.Div([], id='table-row')
            ])
        ]),
        html.Br(),
    ], style = CONTENT_STYLE)
])

# callback for graph row
@callback(
    Output('weather-row', 'children'),
    Input('measurement-switch', 'value'),
    Input('stored-forecast', 'data')
)
def update_weather_row(measurement_switch, data):

    df = pd.read_json(data, orient='split')
    graph1 = px.bar(df, x='time', y='temperature_2m', title='Temperature', labels={'temperature':'Temperature (°F)'})
    graph2 = px.bar(df, x='time', y='humidity', title='Humidity', labels={'humidity':'Humidity (%)'})
    graph3 = px.bar(df, x='time', y='wind_speed', title='Wind Speed', labels={'wind_speed':'Wind Speed (mph)'})

    return dbc.Row([
        dbc.Col(html.Div(dcc.Graph(graph1)), width=4),
        dbc.Col(html.Div(dcc.Graph(graph2)), width=4),
        dbc.Col(html.Div(dcc.Graph(graph3)), width=4)
    ])


# callback for table row
@callback(
        Output('table-row', 'children'),
        Input('measurement-switch', 'value'),
        Input('stored-forecast', 'data')
)
def update_table_row(measurement_switch, data):
    df = pd.read_json(data, orient='split')
    return dbc.Row([
        dash_table.DataTable(
                data = df.to_dict('records'),columns =  [{"name": i, "id": i} for i in df.columns],
                style_table={'width': '100%'}
            )
    ])