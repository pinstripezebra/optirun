import dash
import os
from dash import html, dcc, callback, Input, Output,dash_table
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
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
                html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(id = 'temp-fig'), width=4),
            dbc.Col(dcc.Graph(id ='precipitation-fig'), width=4),
            dbc.Col(dcc.Graph(id = 'wind-fig'), width=4)
        ])
    ])
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
    Output('temp-fig', 'figure'),
    Output('precipitation-fig', 'figure'),
    Output('wind-fig', 'figure'),
    Input('measurement-switch', 'value'),
    Input('stored-forecast', 'data')
)
def update_weather_row(measurement_switch, data):

    print(measurement_switch)
    df = pd.read_json(data, orient='split').head(24)
    temp_measure, windspeed_measure = '', ''
    if 'Metric' in measurement_switch:
        temp_measure = 'temperature_2m'
        windspeed_measure = 'windspeed_10m'
    else:
        temp_measure = 'temperature_F'
        windspeed_measure = 'windspeed_MPH'

    # generating graphs
    graph1 = px.line(df, x='time', y=temp_measure, title='Temperature')
    graph2 = px.line(df, x='time', y='precipitation_probability', title='Rain')
    graph3 = px.line(df, x='time', y=windspeed_measure, title='Wind Speed')   
    graph1.update_traces(mode="markers+lines", hovertemplate=None)
    graph2.update_traces(mode="markers+lines", hovertemplate=None)
    graph3.update_traces(mode="markers+lines", hovertemplate=None)
    graph1.update_layout(hovermode="x unified")
    graph2.update_layout(hovermode="x unified")
    graph3.update_layout(hovermode="x unified")

    return graph1, graph2, graph3

# callback for table row
@callback(
        Output('table-row', 'children'),
        Input('measurement-switch', 'value'),
        Input('stored-forecast', 'data'),
        Input('wind-fig', 'hoverData') 
)
def update_table_row(measurement_switch, data, hover_data_wind):
    df = pd.read_json(data, orient='split').head(24)
    cols_of_interest = ['time', 'temperature_2m', 'precipitation_probability', 'windspeed_10m', 'cloudcover', 'Forecast_Score']
    hovered_time = ''
    if hover_data_wind:
        hovered_time = hover_data_wind['points'][0]['x'] 
    df = df[cols_of_interest]
    return dbc.Row([
        dash_table.DataTable(
                data = df.to_dict('records'),columns =  [{"name": i, "id": i} for i in df.columns],
                page_action='none',
                style_table={'height': '450px', 'overflowY': 'auto'},
                style_data_conditional=[{
                        'if': {'filter_query': '{time} datestartswith {hovered_time}'},
                        'backgroundColor': '#85144b',
                        'color': 'white'
                    }],
                style_cell={
                    'width': '100px',
                    'minWidth': '100px',
                    'maxWidth': '100px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
                page_size=20
                    )
                ])