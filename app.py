import dash
from dash import Dash, dcc, html, callback, dash_table, ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os 
import numpy as np
from dotenv import find_dotenv, load_dotenv
import json
from utility.data_query import data_pipeline, retrieve_users, retrieve_user_from_db
import dash_auth
import flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import time

# Importing utility functions
from utility.measurement import find_optimal_window
from utility.user import User

# loading environmental variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# Loading json files containing component styles
SIDEBAR_STYLE , CONTENT_STYLE, LOGIN_STYLE = {}, {}, {}
with open('style/sidebar_style.json') as f:
    SIDEBAR_STYLE = json.load(f)
with open('style/content_style.json') as f:
    CONTENT_STYLE = json.load(f)
with open('style/login_style.json') as f:
    LOGIN_STYLE = json.load(f)


# defining and Initializing the app
server = flask.Flask(__name__)
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY], assets_folder='assets', assets_url_path='/assets/', server = server)

# updating the Flask Server configuration with Secret Key to encrypt the user session cookie
server.config.update(SECRET_KEY=os.getenv('SECRET_KEY'))

# login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

@ login_manager.user_loader
def load_user(username):
    ''' This function loads the user by user id. It takes our username and looks up the users credentials
    from the database before returning a user object created with those credentials
    '''

    # retrieving user information from database
    user_df = retrieve_user_from_db(username)
    latitude, longitude = float(user_df['latitude'].to_list()[0]), float(user_df['longitude'].to_list()[0])
    password = user_df['password'].to_list()[0]
    optimal_conditions = {'temperature_2m': float(user_df['temperature'].to_list()[0]),
                          'cloudcover': float(user_df['cloud'].to_list()[0]),
                          'windspeed_10m': float(user_df['wind'].to_list()[0]),
                          'precipitation_probability': float(user_df['rain'].to_list()[0]),
                          'daylight_required': int(user_df['daylight_required'].to_list()[0])}
    
    return User(username,password, latitude, longitude, optimal_conditions)

# login using login.py
login = register = logout =  html.Div([
                dash.page_container         
        ])

# Failed Login
failed = html.Div([html.Div([html.H2('Log in Failed. Please try again.'),
                             html.Br(),
                             html.Div([login]),
                             dcc.Link('Home', href='/')
                             ])  
                   ])  

# error page
error404 = html.Div([html.Div(html.H2('Error 404 - page not found')),
                   html.Br(),
                   dcc.Link('Login', href='/login')
                   ])  

app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Location(id='redirect', refresh=True),
        dcc.Store(id='login-status', storage_type='local'),
        dcc.Store(id='stored-forecast', storage_type='local'), # for storing weather forecast in dataframe
        dcc.Store(id='optimal-conditions', storage_type='local'), # for storing optimal conditions in dictionary
        dcc.Store(id='location-storage', storage_type='local'), # for storing latitude/longitude in dictionary
        html.Div(id='page-content'),

])

# defining popup modal for adjusting user preferences
preference_modal = html.Div(
    [
        dbc.Button("Change Preferences", id="open", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("User Preferences")),
                html.Div([html.H5('Input your ideal running conditions:'),
                    html.P('Temperature'),
                    dcc.Slider(40, 100, value=65,
                            marks={
                                40: {'label': '40°F', 'style': {'color': '#77b0b1'}},
                                60: {'label': '60°F'},
                                80: {'label': '80°F'},
                                100: {'label': '100°F', 'style': {'color': '#f50'}}
                            },
                            included=False,
                            id = 'temp-slider-change'
                    ),
                    html.P('Precipitation'),
                    dcc.Slider(0, 100, value=0.1,
                            marks={
                                0.1: {'label': 'No Rain',},
                                50: {'label': 'Moderate Rain'},
                                100: {'label': 'Heavy Rain'}
                            },
                            included=False,
                            id = 'rain--change'
                    ),
                    html.P('Cloud Cover'),
                    dcc.Slider(0, 100, value=0.1,
                            marks={
                                0.1: {'label': 'No Clouds',},
                                50: {'label': 'Moderate Clouds'},
                                100: {'label': 'Heavy Clouds'}
                            },
                            included=False,
                            id = 'cloud-slider-change'
                    ),]),
                dbc.ModalFooter(
                    dbc.Button(
                        "Save", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            size="sm",
            is_open=False,
        ),
    ]
)

sidebar = html.Div(children = [
            html.Img(
                        alt="Link to Github",
                        src="./assets/logo.png",
                        style={'height':'10%', 'width':'40%', 'margin': 'auto', "opacity": '0.8','display': 'inline' }
                    ),
            html.H2('Optirun', style={'display': 'inline' }),
            html.Br(),
            html.Div([
                html.H2(id = "welcome-user-id")]
            ),

            html.Div([
                dcc.Link('Logout', href='/logout'),
            ]),
            preference_modal,
            html.H3("Pages"),
            html.Hr(),
            html.Div([   
                dbc.Nav([
                    dbc.NavLink(f"{page['name']}", href = page["relative_path"]) for page in dash.page_registry.values() if page["relative_path"] != '/register' and page["relative_path"] != '/login' and page["relative_path"] != '/logout'
                ], vertical=True)

            ]),
            html.H3("Description"),
            html.P(
                "Your custom running companion allowing you to plan out your perfect time to run ensuring you never miss a workout.", className="text"
            ),
            html.H3("Model"
            ),
            html.P(
                "This project uses machine learning to forecast running conditions and provides a personalized running reccommendation time based on user preferences.", className="text"
            ),

            html.A(
                href="https://github.com/pinstripezebra/optirun",
                children=[
                    html.Img(
                        alt="Link to Github",
                        src="./assets/github_logo.png",
                        style={'height':'3%', 'width':'8%'}
                    )
                ],
                style = {'color':'black'}
            ),
        ], style=SIDEBAR_STYLE
    )


home_page = html.Div([
        sidebar,
        html.Div([
                dash.page_container
        ])
    ])


# Callback function to login the user, or update the screen if the username or password are incorrect
@callback(
    [Output('url_login', 'pathname'), 
     Output('output-state', 'children'), 
     Output('stored-forecast', 'data'),
     Output('optimal-conditions', 'data'),
     Output('location-storage', 'data')], 
    [Input('login-button', 'n_clicks')], [State('uname-box', 'value'), State('pwd-box', 'value')])
def login_button_click(n_clicks, username, password):
    if n_clicks > 0:

        # Returning user information from database
        user_df = retrieve_user_from_db(username)
        if username in user_df['username'].to_list() and password == user_df[user_df['username']== username]['password'].values:

            # Extracting latitude/longitude from db query
            latitude, longitude = float(user_df['latitude'].to_list()[0]), float(user_df['longitude'].to_list()[0])

            # Extracting optimal conditions from db query
            optimal_conditions = {'temperature_2m': float(user_df['temperature'].to_list()[0]),
                                  'cloudcover': float(user_df['cloud'].to_list()[0]),
                                  'windspeed_10m': float(user_df['wind'].to_list()[0]),
                                  'precipitation_probability': float(user_df['rain'].to_list()[0]),
                                  'daylight_required': int(user_df['daylight_required'].to_list()[0])}


            # logging user in
            user = User(username, password, latitude, longitude, optimal_conditions)
            login_user(user)

            # Logging forecast to store for consumption in other pages
            repull_data = True
            df1 = data_pipeline(repull_data, user.latitude, user.longitude)
            df1['time'] = df1.index
            df1.reset_index(drop = True)
            df1['time'] = pd.to_datetime(df1['time'])
            forecasted_conditions = {'temperature_2m': df1['temperature_2m'].to_list(),
                                     'cloudcover': df1['cloudcover'].to_list(),
                                      'windspeed_10m': df1['windspeed_10m'].to_list(),
                                      'precipitation_probability': df1['precipitation_probability'].to_list()}

            # Rating weather conditions and adding overall score to dataframe
            conditions = find_optimal_window(optimal_conditions, forecasted_conditions, latitude, longitude)
            df1['Forecast_Score'] = conditions['Score'].to_list()
            location = {'latitude': user.latitude,
                        'longitude': user.longitude}
            
            # navigate to landing page if logged in successfully 
            return '/landing', '', df1.to_json(date_format='iso', orient='split'), optimal_conditions, location
        else:
            return '/login', 'Incorrect username or password', 'incorrect username', '', ''

    return dash.no_update, dash.no_update, '', '' # Return a placeholder to indicate no update


# Main router
@callback(Output('page-content', 'children'), 
          Output('redirect', 'pathname'),
          Input('url', 'pathname'))
def display_page(pathname):
    ''' callback to determine layout to return '''
    # We need to determine two things for everytime the user navigates:
    # Can they access this page? If so, we just return the view
    # Otherwise, if they need to be authenticated first, we need to redirect them to the login page
    # So we have two outputs, the first is which view we'll return
    # The second one is a redirection to another page is needed
    # In most cases, we won't need to redirect. Instead of having to return two variables everytime in the if statement
    # We setup the defaults at the beginning, with redirect to dash.no_update; which simply means, just keep the requested url
    view = None
    url = dash.no_update
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if pathname == '/' and current_user.is_authenticated:
        view = home_page
        url = '/landing'
    elif pathname == '/':
        view = login
        url = '/login'

    elif pathname == '/login':
        view = login

    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            view = logout
        else:
            view = login
            url = '/login'
    
    # if we're logged in and want to view one of the pages
    elif pathname == '/analytic' or pathname == '/landing' or pathname == '/map':
        if current_user.is_authenticated:
            view = home_page
        else:
            view = 'Redirecting to login...'
            url = '/login'
    
    # if we're not logged in and want to register
    elif pathname == '/register':
        view = register

    else:
        view = error404
    return view, url

# callback to display username on sidebar
@callback( Output('welcome-user-id', 'children'), 
          [Input('url', 'pathname')],
          suppress_callback_exceptions=True)
def login_status(url):
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated: 
        return html.H4("Welcome, {id}".format(id = current_user.id),style = {'display':'inline'})
    else:
        return html.Div([""])
    
# modal callback to allow user to adjust weather preferences + repull data
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open



# Running the app
if __name__ == '__main__':
    app.run_server(debug=True)



