from argparse import ArgumentParser
from ConfigParser import SafeConfigParser
import os
from os.path import expanduser
import sys

import crtools

def main():
    api_key = False

    config_file_name = expanduser('~/.crtools')
    if os.path.isfile(config_file_name):
        with open(config_file_name) as f:
            parser = SafeConfigParser()
            parser.read(config_file_name)
            api_key = parser.get('API', 'api_key')

    api_key_required = False  
    if api_key == False:
        api_key_required = True

    """Entry point for the application script"""
    parser = ArgumentParser(prog        = "crtools",
                            description = "Tools for creating a clan maagement dashboard for Clash Royale")
    parser.add_argument("clan_id",
                        help    = "Clan ID from Clash Royale. If it starts with a '#', clan ID must be quoted.")
    parser.add_argument("--api_key",
                        metavar  = "KEY",
                        help     = "API key for developer.clashroyale.com",
                        required = api_key_required)

    args = parser.parse_args()

    #api_key = 
    clan_id = args.clan_id

    crtools.make_request( api_key, clan_id )

