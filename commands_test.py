SALT_TEMP = 700
SETPOINT1 = 700
ALARM2_TEMP = 750


def read_salt_temperature():
    return float(SALT_TEMP)


def write_setpoint1(temp):
    global SETPOINT1
    SETPOINT1 = temp
    return f"Setpoint temperature {temp} has been set"


def read_setpoint1():
    return float(SETPOINT1)


def turn_controller_to_standby_mode():
    pass


def turn_controller_from_standby_to_run_mode():
    pass


def reset_controller():
    return "Controller was reset"


def read_alarm2_temperature():
    return float(ALARM2_TEMP)


def change_alarm2_temperature(temp):
    global ALARM2_TEMP
    ALARM2_TEMP = temp
    return f"Alarm temperature {temp} has been set"


def send_custom_command(cmd):
    return send_command(cmd)


def send_command(cmd):
    pass
