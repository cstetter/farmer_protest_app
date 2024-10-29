# %%writefile ../protest_app/code.py

import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_bootstrap_components as dbc  # Ensure dbc is imported
import dash

# Load the selected data
selected_data = pd.read_csv('selected_data.csv')

# Create a pandas DataFrame
df = pd.DataFrame(selected_data)
df['all_protests'] = 1

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Calculate time steps
time_steps = len(df['week_year'].unique())

# Define the layout of the app using Bootstrap components
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Overview map of Farm Protests in Europe 2023-2024 by Protest Reasons"), className="mb-4 text-left")),

    # Dropdown menu aligned to the left
    dbc.Row(dbc.Col(dcc.Dropdown(
        id='variable-dropdown',
        options=[       
            {'label': 'All Protests', 'value': 'all_protests'},
            {'label': 'Opposition to Foreign Agricultural Imports', 'value': 'Opposition_to_Foreign_Agricultural_Imports'},
            {'label': 'Environmental Regulations and Agricultural Standards', 'value': 'Environmental_Regulations_and_Agricultural_Standards'},
            {'label': 'Subsidy Cuts', 'value': 'Subsidy_Cuts'},
            {'label': 'Bureaucratic Constraints', 'value': 'Bureaucratic_Constraints'},
            {'label': 'Rising Production Costs', 'value': 'Rising_Production_Costs'},
            {'label': 'National and Local State Support', 'value': 'National_and_Local_State_Support'},
            {'label': 'Fair Compensation and Market Practices', 'value': 'Fair_Compensation_and_Market_Practices'},
            {'label': 'Climate and Natural Disaster Relief', 'value': 'Climate_and_Natural_Disaster_Relief'},
            {'label': 'Economic Struggles and Agricultural Livelihoods', 'value': 'Economic_Struggles_and_Agricultural_Livelihoods'},
            {'label': 'Labor and Social Conditions', 'value': 'Labor_and_Social_Conditions'},
            {'label': 'Opposition to EU Free-Trade Agreements', 'value': 'Opposition_to_EU_Free-_Trade_Agreements'},
            {'label': 'Solidarity Movements', 'value': 'Solidarity_Movements'},
            {'label': 'Livestock and Animal Welfare Protests', 'value': 'Livestock_and_Animal_Welfare_Protests'},
            {'label': 'Miscellaneous Agriculture-Related Protests', 'value': 'Miscellaneous_Agriculture-_Related_Protests'},
            {'label': 'Infrastructure and Transport Policies', 'value': 'Infrastructure_and_Transport_Policies'},
            {'label': 'Opposition to Non-Traditional Products', 'value': 'Opposition_to_Non-_Traditional_Products'},
            {'label': 'Opposition to Renewable Energy Projects', 'value': 'Opposition_to_Renewable_Energy_Projects'},
            {'label': 'Consumer Awareness Initiatives', 'value': 'Consumer_Awareness_Initiatives'}
        ],
        value='all_protests',  # Default value
        style={'width': '100%'}
    ), width=8)),  # Keep the width setting if you want to control the size

    # Time slider aligned to the left below the dropdown
dbc.Row([
    dbc.Col([
        dbc.Label("Select Year-Week", html_for="time-slider"),  # Title for the slider
        dcc.Slider(
            id='time-slider',
            min=1,
            max=time_steps,
            step=1,
            value=1,  # Default starting value for the slider
            marks={i + 1: f"{week.split('-')[0]}<br>Week {week.split('-')[1]}" for i, week in enumerate(df["week_year"].unique())}
        )
    ], width=10)  # Width setting for the column
])

    # Play button aligned to the left
    dbc.Row(dbc.Col(
        html.Button('Play', id='play-button', n_clicks=0, className='btn btn-primary'),
        width='auto',
        className='mb-4'
    )),

    # Graph to display the map with dots, aligned to the left
    dbc.Row(dbc.Col(
        dcc.Graph(id='map-graph'),
        width=10  # Set width to allow proper layout
    )),

    # Interval component to update the slider automatically
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0, disabled=True)  # Default: disabled

], fluid=True)  # Use fluid for full-width container

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
            showscale=False
        ),
        hoverinfo='text',  # Show only the text on hover
        hovertext=filtered_df['notes_wrapped']  # Display event_date on hover
    ))

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",  # Use an empty background
            zoom=3.5,  # Adjust zoom level
            center={"lat": 47.5260, "lon": 5.2551},  # Center on Europe
        ),
        showlegend=False,
        height=600,
        width=1200,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
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
