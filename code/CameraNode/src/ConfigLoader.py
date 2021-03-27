import configparser


def loadConfig():
    defaultDeviceName = "UNKNOWN_NAME"
    defaultServerIP = "192.168.1.10"
    defaultServerPort = "8080"

    parser = configparser.SafeConfigParser()
    parser.read('src/nodeValuesConfig.txt')

    deviceName = parser.get('main', 'deviceName', fallback=str(defaultDeviceName))

    serverIP = parser.get('server', 'defaultServerIP', fallback=str(defaultServerIP))
    serverPort = parser.get('server', 'defaultServerPort', fallback=str(defaultServerPort))

    return deviceName, serverIP, serverPort
