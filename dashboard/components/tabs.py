from dash import dcc

def get_tabs():
    return dcc.Tabs(
        id="tabs",
        value="overview",
        children=[
            dcc.Tab(label="Overview", value="overview"),
            dcc.Tab(label="Sensitivity", value="sensitivity"),
            dcc.Tab(label="Forecast", value="forecast"),
            dcc.Tab(label="Scenarios", value="scenario"),
        ],
        style={'margin-left': '22%'}
    )
