import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)

site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),
    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Success Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        pie_data = filtered_df['class'].value_counts().reset_index()
        pie_data.columns = ['class_outcome', 'count']
        pie_data['class_outcome'] = pie_data['class_outcome'].replace({1: 'Success', 0: 'Failure'})

        fig = px.pie(
            pie_data,
            names='class_outcome',
            values='count',
            title=f'Total Success vs Failure for site {entered_site}'
        )
    return fig
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f"Correlation between Payload and Success for {'All Sites' if site == 'ALL' else site}"
    )
    return fig

if __name__ == '__main__':
    app.run()
