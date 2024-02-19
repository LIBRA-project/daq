SALT_TEMP = 21
SETPOINT1 = 700
ALARM2_TEMP = 750
MODE = "STANDBY"


def read_temperature():
    global SALT_TEMP
    if MODE == "RUNNING":
        SALT_TEMP = SETPOINT1
    else:
        SALT_TEMP = 21
    return float(SALT_TEMP)


def write_setpoint1(temp):
    global SETPOINT1
    SETPOINT1 = temp
    return f"Setpoint temperature {temp} has been set"


def read_setpoint1():
    return float(SETPOINT1)


def turn_controller_to_standby_mode():
    global MODE
    MODE = "STANDBY"
    global SALT_TEMP
    SALT_TEMP = 21
    return "Controller is on standby"


def turn_controller_from_standby_to_run_mode():
    global MODE
    MODE = "RUNNING"
    global SALT_TEMP
    SALT_TEMP = SETPOINT1
    return "Controller is running"


def reset_controller():
    return "Controller was reset"


def read_alarm2_temperature():
    return float(ALARM2_TEMP)


def change_alarm2_temperature(temp):
    global ALARM2_TEMP
    ALARM2_TEMP = temp
    return f"Alarm temperature {temp} has been set"


def send_custom_command(cmd):
    print(f"Custom command {cmd} has been sent")
    return send_command(cmd)


def send_command(cmd):
    return "Dummy response"
