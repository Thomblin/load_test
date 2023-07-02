import configparser

def load_section(name):
    config = configparser.RawConfigParser()
    config.read('config.ini')

    return config[name]



