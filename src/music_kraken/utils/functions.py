import os

def clear_console():
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')