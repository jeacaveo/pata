""" Global configurations for pata. """
from logging import (
    config as loggingConfig,
    getLogger,
    )
from os import path
from typing import Dict

from sqlalchemy.ext.declarative import declarative_base


BASE = declarative_base()

DATABASES = {
    "sqlite": {
        "engine": "sqlite",  # required
        "driver": "",
        "username": "",
        "password": "",
        "host": "",
        "port": "",
        "database": "db.sqlite",
        },
    }

CURRENT_DIR = path.dirname(path.abspath(__file__))
loggingConfig.fileConfig(
    path.join(CURRENT_DIR, "logging.conf"),
    defaults={"logfilename": path.join(CURRENT_DIR, "../log")})
LOGGER = getLogger("pata")
ROOT_LOGGER = getLogger("root")


def get_database_url(data: Dict[str, str]) -> str:
    """
    Create connection string based con configuration.

    Parameters
    ----------
    data : dict
        Configuration for connection

    Result
    ------
    str

    Example
    -------
    input:
        {
            "engine": "",  # required
            "driver": "",
            "username": "",
            "password": "",
            "host": "",
            "port": "",
            "database": "",
        }

    output:

        engine+driver://username:password@host:port/database

    """
    if "engine" not in data.keys():
        return ""

    driver = f"+{data['driver']}" if data.get('driver') else ""
    username = f"{data['username']}" if data.get('username') else ""
    password = f":{data['password']}" if data.get('password') else ""
    host = f"@{data['host']}" if data.get('host') else ""
    port = f":{data['port']}" if data.get('port') else ""
    database = f"/{data['database']}" if data.get('database') else ""

    return (
        f"{data['engine']}{driver}://"
        f"{username}{password}"
        f"{host}{port}{database}"
        )
