# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 10:05:33 2020

@author: Sean
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# We want to look at the continental US only.
# These will help us identify valid entries,
# if only latitude/longitude are available

latitude_bounds = [23.731583, 49.996020]
longitude_bounds = [-127.375204, -65.024923]

# Loading in the specifics of the current network - 2020
chargers = pd.read_csv('../product_analysis/product_analysis/charging_networks/superchargers.csv')
chargers = chargers.loc[~chargers['state'].isin(['PR'])]

# Clean up the lat/lon data
chargers[['lat', 'lon']] = chargers['lat_lon'].str.split(expand=True)
chargers['lat'] = chargers['lat'].apply(lambda x: x.replace(',','')).astype(float)
chargers['lon'] = chargers['lon'].apply(lambda x: x.replace(',','')).astype(float)
chargers = chargers.drop(columns=['lat_lon'])

chargers['is_open'] = chargers['status'].str.contains('OPEN').astype(int)

# Group by state and count the number of open stalls
state_stalls = chargers.groupby(
    ['state', 'is_open'])['num_stalls'].sum().to_frame().reset_index()
state_stalls = state_stalls.sort_values(by='num_stalls', ascending=False)

fig = px.bar(state_stalls, x="state", y="num_stalls", color="is_open", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Tesla Supercharging Locations'),
 
    html.Div(children='''
        Investigating the current status of supercharging locations across the continental U.S.
    '''),

    dcc.Graph(
        id='Charging Stall Status by State',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)