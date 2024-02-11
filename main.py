from datetime import datetime
import pandas as pd

import dash
import dash_bootstrap_components as dbc

from dash import Dash, dcc, html, Input, Output, State, callback
import plotly
import plotly.subplots

import dash_daq as daq


MODE = "TEST"  # "TEST" or "PROD"

if MODE == "TEST":
    from commands_test import (
        read_salt_temperature,
        write_setpoint1,
        read_setpoint1,
        change_alarm2_temperature,
        read_alarm2_temperature,
        reset_controller,
        turn_controller_from_standby_to_run_mode,
        turn_controller_to_standby_mode,
        send_custom_command,
    )
elif MODE == "PROD":
    from commands import (
        read_salt_temperature,
        write_setpoint1,
        read_setpoint1,
        change_alarm2_temperature,
        read_alarm2_temperature,
        reset_controller,
        turn_controller_from_standby_to_run_mode,
        turn_controller_to_standby_mode,
        send_custom_command,
    )

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
                    id="power-button", on=False, label="On/Off", color="#00cc96"
                ),
                html.Div(id="power-button-result"),
            ]
        ),
    ],
    align="center",
)

third_row = dbc.Row(
    [
        dbc.Col(
            html.Div(
                [
                    html.Div("Write setpoint1 temperature"),
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
                    html.Div("Write Alarm 2 temperature"),
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
                    html.Div("Reset the controller"),
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
        dcc.Interval(
            id="interval-component",
            interval=1 * 1000,  # in milliseconds
            n_intervals=0,
        ),
    ],
    fluid=True,
)


@callback(Output("power-button-result", "children"), Input("power-button", "on"))
def update_output(on):
    if on:
        turn_controller_from_standby_to_run_mode()
        mode = "running"
    else:
        turn_controller_to_standby_mode()
        mode = "on standby"

    return f"The controller is {mode} (not really cause not connected to anything)."


@callback(
    Output("container-button-set_temp", "children"),
    Input("submit-val-set_temp", "n_clicks"),
    State("input-on-submit-set_temp", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    write_setpoint1(int(value))
    return f" \n Setpoint temperature {int(value)} has been set"


@callback(
    Output("container-button-alarm2", "children"),
    Input("submit-val-alarm2", "n_clicks"),
    State("input-on-submit-alarm2", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    change_alarm2_temperature(int(value))
    return f" \n Alarm temperature {int(value)} has been set"


@callback(
    Output("container-button-reset", "children"),
    Input("submit-val-reset", "n_clicks"),
    prevent_initial_call=True,
)
def update_output(n_clicks):
    reset_controller()
    return f" \n Controller last reset: {datetime.now()}"


@callback(
    Output("container-button-custom", "children"),
    Input("submit-val-custom", "n_clicks"),
    State("input-on-submit-custom", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    return send_custom_command(value)


@callback(
    Output("container-button-export", "children"),
    Input("submit-val-export", "n_clicks"),
    State("input-on-submit-export", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    if not value:
        return "Please enter a valid filename"
    df = pd.DataFrame(
        {
            "time": data["time"],
            "Temp": data["Temp"],
            "setpoint": data["setpoint"],
            "alarm2": data["alarm2"],
        }
    )
    df.to_csv(value, index=False)

    return f" \n Data exported to {value}"


data = {"time": [], "Temp": [], "setpoint": [], "alarm2": []}


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
        fig["layout"]["legend"] = {"x": 0, "y": 1, "xanchor": "left"}
        fig.append_trace(
            {
                "x": data["time"],
                "y": data["Temp"],
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
                "y": data["setpoint"],
                "name": "Setpoint",
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
    salt_temp = read_salt_temperature()
    data["Temp"].append(salt_temp)
    data["setpoint"].append(read_setpoint1())
    data["alarm2"].append(read_alarm2_temperature())
    data["time"].append(time)

    figure["data"][0]["x"] = data["time"]
    figure["data"][0]["y"] = data["Temp"]
    figure["data"][1]["x"] = data["time"]
    figure["data"][1]["y"] = data["setpoint"]
    figure["data"][2]["x"] = data["time"]
    figure["data"][2]["y"] = data["alarm2"]
    return figure


@callback(
    Output("salt_temp_thermometer", "value"),
    Input("interval-component", "n_intervals"),
    prevent_initial_call=True,
)
def update_thermometer(n):
    return data["Temp"][-1]


if __name__ == "__main__":
    app.run(debug=True)
