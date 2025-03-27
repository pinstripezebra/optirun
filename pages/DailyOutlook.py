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

