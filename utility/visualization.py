
#import plotly.plotly as py
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, callback,Input, Output,dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

kpi_card_style = {
    'color': 'black', 
    'opacity': '0.8',
    'background':'LightGray'
}

graph_card_style = {
    'color': 'black', 
    'background':'LightGray'
}

def generate_run_plot(df, target_col):

    '''takes input dictionary and displays next 12 hours of values on a clock'''

    filtered = df.head(12)
    r = filtered[target_col].tolist()
    theta = np.arange(0,365,30) + 15
    width = [30]*12

    # hour markers to show on radius of clock
    ticktexts = [12 if i == 0 else i for i in np.arange(12)]

    fig = go.Figure(go.Barpolar(
        r=r,
        theta=theta,
        width=width,
        marker_color=df[target_col],
        marker_colorscale='Blues',
        marker_line_color="white",
        marker_line_width=2,
        opacity=0.8
    ))

    fig.update_layout(
        template=None,
        polar=dict(
            hole=0.4,
            bgcolor='rgb(223, 223,223)',
            radialaxis=dict(
                showticklabels=False,
                ticks='',
                linewidth=2,
                linecolor='white',
                showgrid=False,
            ),
            angularaxis=dict(
                tickvals=np.arange(0,360,30),
                ticktext=ticktexts,
                showline=True,
                direction='clockwise',
                period=12,
                linecolor='white',
                gridcolor='white',
                showticklabels=True,
                ticks=''
            )
        )
    )
    return fig

def draw_Image(input_figure, height = 450):
    '''draw images returns a graph inside a card and div component'''

    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(figure=input_figure.update_layout(template='ggplot2', height=height)
                    ) 
                ])
            , style = graph_card_style),  
        ])

def draw_table(input_figure):
    '''draw images returns a graph inside a card and div component'''

    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    input_figure
                ])
            ,),  
        ])

def draw_Text(input_text):

    return html.Div([
            dbc.Card(
                dbc.CardBody([
                        html.Div([
                            html.P(input_text),
                        ], style={'textAlign': 'center'}) 
                ])
            ,style = kpi_card_style),
        ])

def draw_Text_With_Background(input_val, ideal_val, trailer, input_img):

    '''
    input_val: float value containing condition measurement
    ideal_val: float value containing ideal measurement
    trailer: text to append to end of input for display purposes (i.e. kmp, C, F, etc.)
    input_img: image to use as background
    '''

    display_color = 'green'
    if abs(float(input_val) - float(ideal_val)) > 10:
        display_color = 'orange'
    if abs(float(input_val) - float(ideal_val)) > 20:
        display_color = 'red'

    return html.Div([dbc.Card(
    [
        dbc.CardImg(
            src=input_img,
            top=True,
            style={"opacity": 0.3},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H3(str(input_val) + trailer, className="card-title"),
                ],style = {"display": "block", "text-align": "left", "margin-right": 0,"margin-left": 0, "width": "max-content", }
            ),
        ),
    ],color = display_color
)])

def generate_timeseries_plot(df, x:str, y:str, s1: list, s2: list):


    time_fig = px.line(df, x = 'time', y = y,
                            title = '{type} Forecast'.format(type = y), 
                           markers=True)
    i = 0
    # Finding min/max times from forecast series to align with day/night series
    min_time = df['time'].min().tz_localize('UTC')
    max_time = df['time'].max().tz_localize('UTC')
    while i < len(s1)-1:

        # start is todays sunset
        start = s2[i]
        # end is tomorrows sunrise
        end = s1[i]

        # If both night start/end are within our forecast series
        if (start > min_time) and (end < max_time):
            # add shaded region
            time_fig.add_vrect(
                x0=start,
                x1=end,
                fillcolor="black",
                opacity=0.5,
                line_width=1
            )
        # If its a left edgecase
        elif (start < min_time) and (end > min_time):
            start = min_time
            time_fig.add_vrect(
                x0=start,
                x1=end,
                fillcolor="black",
                opacity=0.5,
                line_width=1
            )
        
        # If its a right edgecase
        elif ( start < max_time) and (end > max_time):
            end = max_time
            time_fig.add_vrect(
                x0=start,
                x1=end,
                fillcolor="black",
                opacity=0.5,
                line_width=1,
            )
        
        i += 1
    time_fig.update_layout(xaxis=dict(
        range=[min_time, max_time],  # Set the range of the x-axis
        side='bottom'  # Set the position of the x-axis to the bottom
        ))
    return time_fig



def generate_geographic_plot(df1, response_variable):
    '''
    Takes input dataframe and response variable, generates geographic plot
    of response variable
    '''
    fig = px.density_mapbox(df1.sort_values(by = 'time'), 
                        radius=100,
                        opacity=0.7,
                        lat=df1.latitude, 
                        lon = df1.longitude, 
                        z = df1[response_variable],
                        hover_data=response_variable,
                        animation_frame='time',
                        zoom=9, 
                        mapbox_style="open-street-map")
    fig.update_layout( height = 1000, width = 1200, 
                  mapbox_style="carto-darkmatter",
                  margin={"r":0,"t":0,"l":0,"b":0},
                  
       )
    
    return fig


def generate_gauge_plot(df, response_val):

    '''takes input dataframe with 1 row and generates a gauge plot'''

    value = df[response_val].to_list()[0]
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': response_val}))
    return fig