from argparse import ArgumentParser
from configparser import SafeConfigParser
import os
from os.path import expanduser
import sys

from .crtools import build_dashboard

def main():

    # prime API key to False for testing later
    api_key = False
    clan_id = False
    output_path = './crtools-out'
    favicon_path = False
    logo_path = False
    description_path = False

    # Look for config file. If config file exists, load it, and try to extract API key from config file
    config_file_name = expanduser('~/.crtools')
    if os.path.isfile(config_file_name):
        with open(config_file_name) as f:
            parser = SafeConfigParser()
            parser.read(config_file_name)
            if parser.has_option('API', 'api_key'):
                api_key = parser.get('API', 'api_key')
                print("CRTools Config: found API key: [not shown]")
            if parser.has_option('API', 'clan'):
                clan_id = parser.get('API', 'clan')
                print("CRTools Config: found clan ID: '{}'".format(clan_id))
            if parser.has_option('Paths', 'out'):
                output_path = parser.get('Paths', 'out')
                print("CRTools Config: found output path: '{}'".format(output_path))
            if parser.has_option('Paths', 'favicon'):
                favicon_path = parser.get('Paths', 'favicon')
                print("CRTools Config: found favicon path: '{}'".format(favicon_path))
            if parser.has_option('Paths', 'clan_logo'):
                logo_path = parser.get('Paths', 'clan_logo')
                print("CRTools Config: found logo path: '{}'".format(logo_path))
            if parser.has_option('Paths', 'description_html'):
                description_path = parser.get('Paths', 'description_html')
                print("CRTools Config: found description HTML file: '{}'".format(description_path))

    # if API key has not been set (is False), then API key needs to be specified as a command line argument
    api_key_required = clan_id_required = False  
    if api_key == False:
        api_key_required = True
    if clan_id == False:
        clan_id_required = True

    # parse command line arguments
    parser = ArgumentParser(prog        = "crtools",
                            description = "Tools for creating a clan maagement dashboard for Clash Royale")
    parser.add_argument("--clan",
                        help    = "Clan ID from Clash Royale. If it starts with a '#', clan ID must be quoted.",
                        required = clan_id_required)
    parser.add_argument("--out",
                        metavar  = "OUTPUT-PATH",
                        help     = "Output path for HTML.")
    parser.add_argument("--api_key",
                        metavar  = "KEY",
                        help     = "API key for developer.clashroyale.com",
                        required = api_key_required)

    args = parser.parse_args()

    # grab API key and clan ID from arguments if applicable
    if args.api_key:
        api_key = args.api_key
    if args.clan:
        clan_id = args.clan
    if args.out:
        output_path = args.out
    
    # Build the dashboard
    build_dashboard(api_key, clan_id, logo_path, favicon_path, description_path, output_path)

