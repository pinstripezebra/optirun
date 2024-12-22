import dash
from utility.visualization import generate_geographic_plot, draw_Image
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, Dash, dcc, callback,Input, Output,dash_table, ctx


dash.register_page(__name__, path='/map')


# Note will need to pass these in from app
df1 = pd.read_csv("Data/test_multi.csv")
df1['time'] = pd.to_datetime(df1['time'])

# defining variables that can be filtered for
filter_vars = ['temperature_2m','cloudcover','windspeed_10m']

# Creating layout
layout = html.Div([
    html.H1('This is our maps page'),
    html.Div([

        # Row for map-plot filter
        dbc.Row([
            html.Div([
                dcc.Dropdown(
                    id = 'response_var_filter',
                    options = [{"label": i, "value": i} for i in filter_vars],
                    value = filter_vars[0])
             
            ], style = {"width": "30%"})
        ]),

        # Row for map-plot
        dbc.Row([
            html.Div([
                html.H3('map-plot'),
                # Div for geographic plot
                html.Div([], id='geo_plot')

            ])
        ])

    ])
])

# callback for weekly forecast for individual series(temp, wind, etc)
@callback(
    Output(component_id='geo_plot', component_property='children'),
    Input('response_var_filter', 'value'),


)
def update_timeseries(filter_var):

    filtered_df = df1
    geo_fig = generate_geographic_plot(filtered_df, filter_var)
    map_height = 800
    return draw_Image(geo_fig, map_height)