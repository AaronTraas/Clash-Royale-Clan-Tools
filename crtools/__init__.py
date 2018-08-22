from argparse import ArgumentParser
from ConfigParser import SafeConfigParser
import os
from os.path import expanduser
import sys

import crtools

def main():

    # prime API key to False for testing later
    api_key = False

    # Look for config file. If config file exists, load it, and try to extract API key from config file
    config_file_name = expanduser('~/.crtools')
    if os.path.isfile(config_file_name):
        with open(config_file_name) as f:
            parser = SafeConfigParser()
            parser.read(config_file_name)
            api_key = parser.get('API', 'api_key')

    # if API key has not been set (is False), then API key needs to be specified as a command line argument
    api_key_required = False  
    if api_key == False:
        api_key_required = True

    # parse command line arguments
    parser = ArgumentParser(prog        = "crtools",
                            description = "Tools for creating a clan maagement dashboard for Clash Royale")
    parser.add_argument("clan_id",
                        help    = "Clan ID from Clash Royale. If it starts with a '#', clan ID must be quoted.")
    parser.add_argument("--api_key",
                        metavar  = "KEY",
                        help     = "API key for developer.clashroyale.com",
                        required = api_key_required)

    args = parser.parse_args()

    # grab API key and clan ID from arguments if applicable
    if args.api_key:
        api_key = args.api_key
    clan_id = args.clan_id

    # Build the dashboard
    crtools.build_dashboard( api_key, clan_id )

