from datetime import datetime
import pandas as pd

import dash
import dash_bootstrap_components as dbc

from dash import Dash, dcc, html, Input, Output, State, callback, ctx
import plotly
import plotly.subplots

import dash_daq as daq


MODE = "PROD"  # "TEST" or "PROD"

if MODE == "TEST":
    import commands_test as commands
elif MODE == "PROD":

    import commands as commands


DEFAULT_EXPORT_RATE = 30 * 60 * 1000  # in miliseconds
DEFAULT_READING_RATE = 5 * 1000  # in miliseconds

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])

first_row = dbc.Row(
    [
        dbc.Col(html.H1("Salt temperature feed"), width={"size": 6, "offset": 3}),
    ]
)
second_row = dbc.Row(
    [
        dbc.Col(dcc.Graph(id="live-update-graph"), width=8),
        dbc.Col(
            daq.Thermometer(
                id="salt_temp_thermometer",
                min=0,
                max=1000,
                value=None,
                showCurrentValue=True,
                units="C",
            )
        ),
        dbc.Col(
            [
                daq.PowerButton(
                    id="power-button",
                    on=False,
                    label="On/Off",
                    color="#00cc96",
                    size=100,
                ),
                html.Div(id="power-button-result"),
                html.Div(
                    [
                        dbc.Button(
                            "Reset",
                            id="submit-val-reset",
                            n_clicks=0,
                        ),
                        html.Div(
                            id="container-button-reset",
                        ),
                    ],
                    style={"margin-top": "15px"},
                ),
            ],
            style={"textAlign": "center"},
        ),
    ],
    align="center",
)

third_row = dbc.Row(
    [
        dbc.Col(
            html.Div(
                [
                    html.Div("Write Setpoint 1"),
                    html.Div(dbc.Input(id="input-on-submit-set_temp", type="text")),
                    dbc.Button("Submit", id="submit-val-set_temp", n_clicks=0),
                    html.Div(
                        id="container-button-set_temp",
                    ),
                ],
                style={"margin-top": "15px"},
            ),
            width=1,
        ),
        dbc.Col(
            html.Div(
                [
                    html.Div("Write Alarm 2"),
                    html.Div(
                        dbc.Input(id="input-on-submit-alarm2", type="text"),
                    ),
                    dbc.Button("Submit", id="submit-val-alarm2", n_clicks=0),
                    html.Div(
                        id="container-button-alarm2",
                    ),
                ],
                style={"margin-top": "15px"},
            ),
            width=1,
        ),
        dbc.Col(
            html.Div(
                [
                    html.Div("Write custom command"),
                    html.Div(dbc.Input(id="input-on-submit-custom", type="text")),
                    dbc.Button("Submit", id="submit-val-custom", n_clicks=0),
                    html.Div(
                        id="container-button-custom",
                    ),
                ],
                style={"margin-top": "15px"},
            ),
            width=1,
        ),
    ]
)

fourth_row = dbc.Row(
    [
        dbc.Col(
            html.Div(
                [
                    html.Div("Reading rate (seconds)"),
                    html.Div(dbc.Input(id="input-on-submit-reading_rate", type="text")),
                    dbc.Button("Submit", id="submit-val-reading_rate", n_clicks=0),
                    html.Div(
                        id="container-button-reading_rate",
                        children=f"\n Reading rate set to {DEFAULT_READING_RATE/1000} seconds",
                    ),
                ],
                style={"margin-top": "15px"},
            ),
            width=1,
        ),
        dbc.Col(
            html.Div(
                [
                    html.Div("Export rate (seconds)"),
                    html.Div(dbc.Input(id="input-on-submit-export_rate", type="text")),
                    dbc.Button("Submit", id="submit-val-export_rate", n_clicks=0),
                    html.Div(
                        id="container-button-export_rate",
                        children=f"\n Export rate set to {DEFAULT_EXPORT_RATE/1000} seconds",
                    ),
                ],
                style={"margin-top": "15px"},
            ),
            width=1,
        ),
        dbc.Col(
            html.Div(
                [
                    html.Div("Export data to csv"),
                    html.Div(
                        dbc.Input(
                            id="input-on-submit-export",
                            type="text",
                            placeholder="filename.csv",
                        )
                    ),
                    dbc.Button("Export", id="submit-val-export", n_clicks=0),
                    html.Div(
                        id="container-button-export",
                    ),
                ],
                style={"margin-top": "15px"},
            ),
            width=1,
        ),
    ]
)
app.layout = dbc.Container(
    [
        first_row,
        second_row,
        third_row,
        fourth_row,
        dcc.Interval(
            id="interval-component",
            interval=DEFAULT_READING_RATE,  # in milliseconds
            n_intervals=0,
        ),
        dcc.Interval(
            id="interval-component_export",
            interval=DEFAULT_EXPORT_RATE,  # in milliseconds
            n_intervals=0,
        ),
    ],
    fluid=True,
)


@callback(Output("power-button-result", "children"), Input("power-button", "on"))
def update_output(on):
    if on:
        commands.turn_controller_from_standby_to_run_mode()
        mode = "running"
    else:
        commands.turn_controller_to_standby_mode()
        mode = "on standby"

    return f"The controller is {mode} (not really cause not connected to anything)."


@callback(
    Output("container-button-set_temp", "children"),
    Input("submit-val-set_temp", "n_clicks"),
    State("input-on-submit-set_temp", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    commands.write_setpoint1(int(value))
    return f" \n Setpoint temperature {int(value)} has been set"


@callback(
    Output("container-button-alarm2", "children"),
    Input("submit-val-alarm2", "n_clicks"),
    State("input-on-submit-alarm2", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    commands.change_alarm2_temperature(int(value))
    return f" \n Alarm temperature {int(value)} has been set"


@callback(
    Output("container-button-reset", "children"),
    Input("submit-val-reset", "n_clicks"),
    prevent_initial_call=True,
)
def update_output(n_clicks):
    commands.reset_controller()
    return f" \n Controller last reset: {datetime.now()}"


@callback(
    Output("container-button-custom", "children"),
    Input("submit-val-custom", "n_clicks"),
    State("input-on-submit-custom", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    return commands.send_custom_command(value)


@callback(
    [
        Output("interval-component_export", "interval"),
        Output("container-button-export_rate", "children"),
    ],
    Input("submit-val-export_rate", "n_clicks"),
    State("input-on-submit-export_rate", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    new_interval = float(value) * 1000  # seconds to milliseconds
    return new_interval, f" \n Export rate set to {new_interval/1000} seconds"


@callback(
    [
        Output("interval-component", "interval"),
        Output("container-button-reading_rate", "children"),
    ],
    Input("submit-val-reading_rate", "n_clicks"),
    State("input-on-submit-reading_rate", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    new_interval = float(value) * 1000  # seconds to milliseconds
    return new_interval, f" \n Reading rate set to {new_interval/1000} seconds"


@callback(
    Output("container-button-export", "children"),
    [
        Input("submit-val-export", "n_clicks"),
        Input("interval-component_export", "n_intervals"),
    ],
    State("input-on-submit-export", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, n_intervals, value):
    triggered_id = (
        ctx.triggered_id
    )  # the the id of the input that triggered the callback
    if triggered_id == "interval-component_export":
        filename = f"exported_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    else:
        filename = value
        if not value or not value.endswith(".csv"):
            return "Please enter a valid filename"
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, mode="w+")

    return f" \n Data exported to {filename}"


data = {"time": [], "temp": [], "setpoint1": [], "alarm2": []}


@app.callback(
    Output("live-update-graph", "figure"),
    [Input("interval-component", "n_intervals")],
    [
        State("live-update-graph", "figure")
    ],  # using State here preserves the figure instead of recreating it from scratch
)
def update_graph_live(n_intervals, figure):
    if figure is None:
        fig = plotly.subplots.make_subplots(rows=1, cols=1, vertical_spacing=0.2)
        fig["layout"]["margin"] = {"l": 30, "r": 10, "b": 30, "t": 10}
        fig.append_trace(
            {
                "x": data["time"],
                "y": data["temp"],
                "name": "Temperature",
                "mode": "lines+markers",
                "type": "scatter",
            },
            1,
            1,
        )

        fig.append_trace(
            {
                "x": data["time"],
                "y": data["setpoint1"],
                "name": "Setpoint 1",
                "mode": "lines+markers",
                "type": "scatter",
            },
            1,
            1,
        )

        fig.append_trace(
            {
                "x": data["time"],
                "y": data["alarm2"],
                "name": "Alarm 2",
                "mode": "lines+markers",
                "type": "scatter",
            },
            1,
            1,
        )
        return fig
    time = datetime.now()
    salt_temp = commands.read_temperature()
    data["temp"].append(salt_temp)
    data["setpoint1"].append(commands.read_setpoint1())
    data["alarm2"].append(commands.read_alarm2_temperature())
    data["time"].append(time)

    figure["data"][0]["x"] = data["time"]
    figure["data"][0]["y"] = data["temp"]
    figure["data"][1]["x"] = data["time"]
    figure["data"][1]["y"] = data["setpoint1"]
    figure["data"][2]["x"] = data["time"]
    figure["data"][2]["y"] = data["alarm2"]
    return figure


@callback(
    Output("salt_temp_thermometer", "value"),
    Output("salt_temp_thermometer", "color"),
    Input("interval-component", "n_intervals"),
    prevent_initial_call=True,
)
def update_thermometer(n):
    value = data["temp"][-1]
    setpoint = data["setpoint1"][-1]

    if value == setpoint:
        colour = "#00cc96"
    elif value > setpoint:
        colour = "#ff4444"
    else:
        colour = "#3399ff"

    return value, colour


if __name__ == "__main__":
    app.run(debug=True)
