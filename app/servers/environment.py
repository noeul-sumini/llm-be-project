import os

def get_server_env():
    server_env = os.environ.get('S_ENV', 'DEV')
    return server_env