#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from __future__ import annotations
import sys
import json
from ipaddress import ip_network
import logging
from mysql.connector import MySQLConnection


# IP addresses are stored in the database in decimal format
# Some addresses have negative values
# To make them positive it is necessary to add them to the value below
COEFFICIENT: int = 4294967296
# Query for getting ip addresses that are not marked for deletion
QUERY: str = f"""SELECT INET_NTOA(IF(ip < 0, ip + {COEFFICIENT}, ip))
FROM ip_groups WHERE is_deleted=0"""


def get_config(filename: str = "config.json") -> dict:
    """
    Function returns contents of config file

    :param filename: Config filename
    :type filename: str

    :returns: Dictionary with config file contents
    :rtype: Dict
    """
    config: dict = {}
    if sys.platform.startswith("win32"):
        full_name: str = sys.path[0] + "\\" + filename
    else:
        full_name: str = sys.path[0] + "/" + filename
    try:
        with open(full_name) as file:
            config = json.load(file)
    except Exception as err:
        logging.error("Error in config file or file does not exist.")
        logging.error(err)
    return config


def connect() -> MySQLConnection:
    """
    Function connects to a database using parameters
    from config file and returns a connection

    :returns: Reference to an object representing a database connection
    :rtype: MySQLConnection
    """
    db_config: dict = get_config()["database"]
    if db_config:
        try:
            conn = MySQLConnection(**db_config)
            if conn.is_connected():
                return conn
            else:
                logging.error("Could not connect to the database.")
        except Exception as err:
            logging.error("Unable to raise database connection.")
            logging.error(err)
    else:
        logging.error("Could not get database configuration.")


def get_ips() -> list:
    """
    Function returns list of ip addresses

    :returns: List of ip addresses
    :rtype: List[str]
    """
    ips: list[str] = []
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(QUERY)
            data = cursor.fetchall()
            if len(data) > 0:
                for ip in data:
                    ips.append(ip[0])
                conn.close()
                return ips
            else:
                logging.error("Could not find any address in the database.")
        except Exception as err:
            logging.error("Unable to fetch addresses from database.")
            logging.error(err)


def get_names() -> list:
    """
    Function returns list of names

    :returns: List of names
    :rtype: List[str]
    """
    names: list = []
    servers: list[dict] = get_config()["servers"]
    if servers:
        for server in servers:
            names.append(server["name"])
    return names


def get_types(name: str) -> list:
    """
    Function returns list of types

    :param name: Server name
    :type name: str

    :returns: List of types
    :rtype: List[str]
    """
    types: list = []
    servers: list[dict] = get_config()["servers"]
    if servers:
        for server in servers:
            if server["name"] == name:
                subnets = server["nets"]
                if subnets:
                    for subnet in subnets:
                        types.append(subnet["type"])
                break
    return list(set(types))


def get_subnets(name: str, type: str) -> list:
    """
    Function returns list of subnets

    :param name: Server name
    :type name: str

    :param type: Ip address type
    :type type: str

    :returns: List of subnets
    :rtype: List[str]
    """
    subnets: list[str] = []
    servers: list[dict] = get_config()["servers"]
    if servers:
        for server in servers:
            if server["name"] == name:
                nets: list[dict] = server["nets"]
                for net in nets:
                    if net["type"] == type:
                        subnets = net["subnets"]
    return subnets


def get_free_ip(name: str, type: str) -> str:
    """
    Function returns free ip address for the given server

    :param name: Server name
    :type name: str

    :param type: Ip address type
    :type type: str

    :returns: Ip address
    :rtype: str
    """
    free_ip: str = ''
    ips: list[str] = get_ips()
    exceptions: list[str] = get_config()["exceptions"]
    subnets = get_subnets(name, type)
    if ips and subnets:
        for subnet in subnets:
            hosts = ip_network(subnet).hosts()
            if hosts:
                for ip in hosts:
                    ip = str(ip)
                    if ip not in ips and ip not in exceptions:
                        free_ip = ip
                        break
    return free_ip
