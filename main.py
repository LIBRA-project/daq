from datetime import datetime

import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import plotly
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
    )

app = Dash(__name__)
app.layout = html.Div(
    html.Div(
        [
            html.H4("Salt temperature feed"),
            html.Div(id="live-update-text"),
            dcc.Graph(id="live-update-graph"),
            html.Div(
                [
                    daq.PowerButton(
                        id="power-button", on=False, label="On/Off", color="#00cc96"
                    ),
                    html.Div(id="power-button-result"),
                ]
            ),
            daq.Thermometer(
                id="salt_temp_thermometer",
                min=0,
                max=1000,
                value=None,
                showCurrentValue=True,
                units="C",
            ),
            html.Div(
                [
                    html.Div(dcc.Input(id="input-on-submit-set_temp", type="text")),
                    html.Button("Submit", id="submit-val-set_temp", n_clicks=0),
                    html.Div(
                        id="container-button-set_temp",
                        children="Enter a set temperature and press submit",
                    ),
                ],
                style={"margin-top": "15px"},
            ),
            html.Div(
                [
                    html.Div(
                        dcc.Input(id="input-on-submit-alarm2", type="text"),
                    ),
                    html.Button("Submit", id="submit-val-alarm2", n_clicks=0),
                    html.Div(
                        id="container-button-alarm2",
                        children="Enter an alarm temp and press submit",
                    ),
                ],
                style={"margin-top": "15px"},
            ),
            html.Div(
                [
                    html.Button(
                        "Reset",
                        id="submit-val-reset",
                        n_clicks=0,
                    ),
                    html.Div(
                        id="container-button-reset",
                        children="Click to reset the controller",
                    ),
                ],
                style={"margin-top": "15px"},
            ),
            dcc.Interval(
                id="interval-component",
                interval=1 * 1000,  # in milliseconds
                n_intervals=0,
            ),
        ]
    )
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


data = {"time": [], "Temp": [], "setpoint": [], "alarm2": []}


@callback(
    Output("live-update-graph", "figure"), Input("interval-component", "n_intervals")
)
def update_graph_live(n):

    time = datetime.now()
    salt_temp = read_salt_temperature()
    data["Temp"].append(salt_temp)
    data["setpoint"].append(read_setpoint1())
    data["alarm2"].append(read_alarm2_temperature())
    data["time"].append(time)

    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=1, cols=1, vertical_spacing=0.2)
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


@callback(
    Output("salt_temp_thermometer", "value"), Input("interval-component", "n_intervals")
)
def update_graph_live(n):
    return data["Temp"][-1]


if __name__ == "__main__":
    app.run(debug=True)
