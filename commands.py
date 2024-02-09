import socket

# find this information in the manual of the controller
HOST = "192.168.1.200"  # The remote host
PORT = 2000  # The same port as used by the server
REC_CHAR = "*"
EOL = "\r"


def read_salt_temperature():
    data = send_command(HOST, PORT, "X01")
    data = data.replace("b'X01", "")
    data = data.replace(r".\r'", "")
    print("Received", float(data))
    return float(data)


def write_setpoint1(temp):
    temp_hex = "{:04x}".format(temp).upper()
    cmd = f"W0110{temp_hex}"
    data = send_command(HOST, PORT, cmd)
    print("Received", data)
    return data


def read_setpoint1():
    cmd = "R01"
    data = send_command(HOST, PORT, cmd)
    data = data.replace(r"\r'", "")
    setpoint_temp = data[-4:]
    setpoint_temp = int(setpoint_temp, 16)
    print("Received", setpoint_temp)
    return setpoint_temp


def turn_controller_to_standby_mode():
    pass


def turn_controller_from_standby_to_run_mode():
    pass


def reset_controller():
    cmd = "Z02"
    data = send_command(HOST, PORT, cmd)
    print("Received", data)
    return data


def read_alarm2_temperature():
    cmd = "R16"
    data = send_command(HOST, PORT, cmd)
    data = data.replace(r"\r'", "")
    alarm_temp = data[-4:]
    alarm_temp = int(alarm_temp, 16)
    print("Received", alarm_temp)
    return alarm_temp


def change_alarm2_temperature(temp):
    temp_hex = "{:04x}".format(temp).upper()
    cmd = f"W1610{temp_hex}"
    data = send_command(HOST, PORT, cmd)
    print("Received", data)
    return data


def send_custom_command(cmd):
    data = send_command(HOST, PORT, cmd)
    print("Received", data)
    return data


def send_command(HOST, PORT, cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        try:
            s.connect((HOST, PORT))
            print("Sending", cmd)
            s.sendall(bytes(REC_CHAR + cmd + EOL, "utf-8"))
            data = s.recv(1024)
            data = repr(data)
        except socket.timeout:
            print("Timeout, sending dummy data")
            data = 100
    return data
