import configparser

def config_parser(filename:str) -> dict:
    """ini config 파일을 읽어서 설정정보를 return하는 함수

    Args:
        filename (str): config file full path

    Returns:
        dict: config정보를 dictionary타입으로 return
    """
    config = configparser.ConfigParser()
    configs = config.read(filename)
    return configs