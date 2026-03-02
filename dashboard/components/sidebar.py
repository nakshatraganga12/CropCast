from dash import dcc, html

def get_sidebar(state_list):
    return html.Div(
        [
            html.H2("CropCast", style={'margin-bottom':'20px'}),

            html.Label("State"),
            dcc.Dropdown(
                id="state-select",
                options=[{"label": s, "value": s} for s in state_list],
                value="Bihar",
                clearable=False,
                style={'margin-bottom': '20px'}
            ),

            html.Label("Rainfall Shock (%)"),
            dcc.Slider(
                id="shock-slider",
                min=-40, max=40, step=5, value=0,
                marks={i: f"{i}%" for i in range(-40, 41, 20)}
            ),
        ],
        style={
            'width':'20%',
            'padding':'20px',
            'background':'#f5f5f5',
            'position':'fixed',
            'height':'100vh',
            'border-right':'1px solid #ddd'
        }
    )
