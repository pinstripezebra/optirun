import dash
from dash import html, Dash, dcc, callback,Input, Output,dash_table, ctx, State
import pandas as pd
import dash_bootstrap_components as dbc
from dotenv import find_dotenv, load_dotenv
import os
import json

# registering page
dash.register_page(__name__, path='/logout')

# Loading json files containing registration pages style
LOGOUT_STYLE = {}
with open('style/logout_style.json') as f:
    LOGOUT_STYLE = json.load(f)


# Defining page layout
layout = html.Div([
    dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Img(
                        alt="Link to Github",
                        src="./assets/logo.png",
                        style={'height':'3%', 'width':'16%', 'margin': 'auto', "opacity": '0.8','display': 'inline'}
                    ),
                    html.H3('Optirun', style={'display': 'inline' }),
                html.Div([
                    html.H2('You have been logged out - Please login'),
                    dbc.Button(children='Login', href='/login'),

                ],style = {'align-items':'center', 'justify-content':'center', })
            ])
        ], className='text-center', style={"width": "25rem", 'background-color': 'rgba(245, 245, 245, 1)', 'opacity': '.8'}),
        width={"offset": 4},
    )
], style=LOGOUT_STYLE)
