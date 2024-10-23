import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np


selected_data = pd.read_csv('../protest_app/selected_data.csv')





# Create a pandas DataFrame
df = pd.DataFrame(selected_data)
df['all_protests'] = 1

# Initialize the Dash app
app = dash.Dash(__name__)

# Calculate time steps
time_steps = len(df['week_year'].unique())

# Define the layout of the app
app.layout = html.Div([
    html.H1("OpenStreetMap with Time Slider and Variable Selection"),

    # Dropdown menu to select the variable to display (var1 or var2)
    dcc.Dropdown(
        id='variable-dropdown',
        options=[
            {'label': 'Rising Production Costs', 'value': 'Subsidy_Cuts'},
            {'label': 'Opposition to EU Free-Trade Agreements', 'value': 'Climate_and_Natural_Disaster_Relief'},
            {'label': 'All Protests', 'value': 'all_protests'},
        ],
        value='all_protests',  # Default value
        style={'width': '50%'}
    ),

    # Slider to select the time step
    html.Div(dcc.Slider(
                id='time-slider',
                min=1,
                max=time_steps,
                step=1,
                value=1,  # Default value for the slider
                marks={i+1: week for i, week in enumerate(df["week_year"].unique())},
                ), style={'width': '50%'}
    ),

    # Play/Pause button
    html.Button('Play', id='play-button', n_clicks=0),

    # Interval component to update the slider automatically
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0, disabled=True),  # Default: disabled

    # Graph to display the map with dots
    dcc.Graph(id='map-graph')
])

# Define the callback to update the map based on the slider and dropdown values
@app.callback(
    Output('map-graph', 'figure'),
    [Input('time-slider', 'value'),
     Input('variable-dropdown', 'value')]
)
def update_map(selected_time, selected_variable):
    # Filter the data for the selected time step and selected variable where its value is 1
    filtered_df = df[(df['time'] == selected_time) & (df[selected_variable] == 1)]

    # Create the figure with the map and dots
    fig = go.Figure(go.Scattermapbox(
        lat=filtered_df['lat'],
        lon=filtered_df['lon'],
        mode='markers',
        marker=dict(
            size=8,
            color="red",
            showscale=True
        )
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",  # Use an empty background
            zoom=4.3,  # Adjust zoom level
            center={"lat": 47.5260, "lon": 5.2551},  # Center on Europe
        ),
        width=1600,  # Adjust the width of the plot (in pixels)
        height=1200,  # Adjust the height of the plot (in pixels)
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return fig

# Callback to play/pause the time slider
@app.callback(
    [Output('interval-component', 'disabled'),
     Output('play-button', 'children')],
    [Input('play-button', 'n_clicks')],
    [State('interval-component', 'disabled')]
)
def play_pause(n_clicks, interval_disabled):
    if n_clicks % 2 == 1:  # If button clicked odd number of times, play (enable interval)
        return False, 'Pause'
    else:  # If button clicked even number of times, pause (disable interval)
        return True, 'Play'

# Callback to automatically update the slider's value when interval is active
@app.callback(
    Output('time-slider', 'value'),
    [Input('interval-component', 'n_intervals')],
    [State('time-slider', 'value')]
)
def update_slider(n_intervals, current_value):
    if current_value < time_steps:
        return current_value + 1  # Increment slider value
    else:
        return 1  # Reset slider to the beginning after reaching the end

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
