import dash
from dash import html, Dash, dcc, callback,Input, Output,dash_table, ctx
import pandas as pd
import dash_bootstrap_components as dbc
from dotenv import find_dotenv, load_dotenv
import os
import json
from utility.data_query import insert_user, search_address, validate_registration, retrieve_user_from_db

# registering page
dash.register_page(__name__, path='/register')

# Loading json files containing registration pages style
REGISTER_STYLE = {}
with open('style/register_style.json') as f:
    REGISTER_STYLE = json.load(f)

# Defining page layout
layout = html.Div([
    dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Div([
                        dbc.Button('<-', href='/login'),
                    ],style = {'float': 'left'}),
                html.Div([
                    html.Img(
                        alt="Link to Github",
                        src="./assets/logo.png",
                        style={'height':'3%', 'width':'16%', 'margin': 'auto', "opacity": '0.8','display': 'inline'}
                    ),
                    html.H3('Optirun', style={'display': 'inline' }),
                    html.H1('Account Creation'),
                    html.H5('Username'),
                    dcc.Input(placeholder='Enter your username',
                                            type='text', id='register-uname-box'),
                    html.H5('Email'),
                    dcc.Input(placeholder='Enter your email',
                                            type='text', id='register-email-box'),
                    html.H5('Password'),
                    dcc.Input(placeholder='Enter your password',
                                type='password', id='register-pwd-box'),
                    html.H5('Confirm Password'),
                    dcc.Input(placeholder='Confirm your password',
                                type='password', id='register-pwd-box2'),
                    html.Div(id="password-error"),
                    html.H5('Address'),
                    dcc.Input(placeholder='Enter your Address',
                                type='text', id='address-box'),
                    html.H4('Weather Conditions'),
                    html.H5('Input your ideal running conditions:'),
                    html.P('Temperature'),
                    dcc.Slider(40, 100, value=65,
                            marks={
                                40: {'label': '40°F', 'style': {'color': '#77b0b1'}},
                                60: {'label': '60°F'},
                                80: {'label': '80°F'},
                                100: {'label': '100°F', 'style': {'color': '#f50'}}
                            },
                            included=False,
                            id = 'temp-slider'
                    ),
                    html.P('Precipitation'),
                    dcc.Slider(0, 100, value=0,
                            marks={
                                0: {'label': 'No Rain',},
                                50: {'label': 'Moderate Rain'},
                                100: {'label': 'Heavy Rain'}
                            },
                            included=False,
                            id = 'rain-slider'
                    ),
                    html.P('Cloud Cover'),
                    dcc.Slider(0, 100, value=0,
                            marks={
                                0: {'label': 'No Clouds',},
                                50: {'label': 'Moderate Clouds'},
                                100: {'label': 'Heavy Clouds'}
                            },
                            included=False,
                            id = 'cloud-slider'
                    ),
                    html.Br(),
                    html.Br(),
                    dbc.Button('Register', n_clicks=0,className="me-2", id='Register-button'),

                ],style = {'align-items':'center', 'justify-content':'center', }),
                html.Div(id = 'registration-message')
            ])
        ], className='text-center', style={"width": "25rem", 'background-color': 'rgba(245, 245, 245, 1)', 'opacity': '.8'}),
        width={"offset": 4},
    )
], style=REGISTER_STYLE)

# Callback for registering user
@callback(
    Output("password-error", "children"),
    Output("registration-message", "children"),
    Input("Register-button", "n_clicks"),
    Input("register-uname-box", "value"),
    Input("register-email-box", "value"),
    Input("register-pwd-box", "value"),
    Input("register-pwd-box2", "value"),
    Input('address-box', "value"),
    Input('temp-slider', 'value'),
    Input('rain-slider', 'value'),
    Input('cloud-slider', 'value'),
    prevent_initial_call = True
)
def register_user_to_database(n_clicks, username, email, password1, password2, address, temp, rain, cloud):
    
    # extracting latitude/longitude from address
    registration_error = ""

    # If button has been pressed
    if dash.callback_context.triggered_id == 'Register-button':
        # If all fields have been entered 
        if None not in [username, email, email, password1, password2, address]:
            print([username, email, email, password1, password2, address])
            check_username = retrieve_user_from_db(username)
            latitude, longitude = search_address(address)

            # If the username already exists notify user
            if len(check_username) > 0:
                registration_error = "Username already exists"

            # If the passwords dont match notify user
            elif password1 != password2:
                registration_error = "passwords must match"

            # Checking that passwords match
            else:
                registration_error = validate_registration(username, password1, latitude, longitude, temp, rain, cloud)
                print(registration_error)
                if registration_error == "no error":
                    insert_user(username, password1, str(latitude), str(longitude))
                    return html.Div([html.P(registration_error)]), html.Div([html.H3('Successfully Registered!')])

        
    if registration_error == 'no error':
        registration_error = ""
    
    return html.Div([html.P(registration_error)]),  html.Div([])
