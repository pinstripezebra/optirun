import dash
from dash import html, Dash, dcc, callback,Input, Output,dash_table, ctx
import pandas as pd
import dash_bootstrap_components as dbc
from dotenv import find_dotenv, load_dotenv
import os
import json
from utility.data_query import insert_user, search_address, validate_registration

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
    prevent_initial_call = True
)
def register_user_to_database(n_clicks, username, email, password1, password2, address):
    
    # extracting latitude/longitude from address
    latitude, longitude = search_address(address)
    registration_error = ""
    print([username, email, email, password1, password2, address])
    # If all fields have been entered and registration button pressed
    if None not in [username, email, email, password1, password2, address] and n_clicks > 0:
        # If passwords match
        if password1 == password2:
            registration_error = validate_registration(username, password1, latitude, longitude)
            print(registration_error)
            if registration_error == "no error":
                insert_user(username, password1, str(latitude), str(longitude))
                return html.Div([html.P(registration_error)]), html.Div([html.H3('Successfully Registered!')])
        else:
            registration_error = "passwords must match"
        
    #if registration_error == 'no error':
    #    registration_error = ""
    return html.Div([html.P(registration_error)]),  html.Div([])
'''
@callback(
Output("Intake-Form", 'children'),
Input("password-error-text", "text")
)

def intake_form_status(register_error):

    # if we've registered successfuly
    if register_error =="no error":
        print("here")
        return html.Div([
            html.H3('Registered Successfully!')
        ])

    else:
        return html.Div([
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
                    html.Br(),
                    html.Br(),
                    dbc.Button('Register', n_clicks=0,className="me-2", id='Register-button'),

                ],style = {'align-items':'center', 'justify-content':'center', })
'''
