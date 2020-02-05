import argparse

def init():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", help="defines which port will be used by webserver for http", type=int, default=8080)
    parser.add_argument("--debug", "-d", help="debug mode - print out who access the server", type=bool, default=False)
    parser.add_argument("--ssl", help="enable ssl so https is available on port 443", type=bool, default=False)
    parser.add_argument("--sslport", help="defines which port will be used by webserver for https", type=int, default=8443)

    args = parser.parse_args()
