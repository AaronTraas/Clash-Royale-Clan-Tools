from argparse import ArgumentParser, RawDescriptionHelpFormatter
from configparser import SafeConfigParser
import os
from os.path import expanduser
import sys
from ._version import __version__

from .crtools import build_dashboard

def main():
    print("crtools {}".format(__version__))

    # prime API key to False for testing later
    api_key = False
    clan_id = False
    output_path = './crtools-out'
    favicon_path = False
    logo_path = False
    description_path = False
    canonical_url = False

    # Look for config file. If config file exists, load it, and try to extract API key from config file
    config_file_name = expanduser('~/.crtools')
    if os.path.isfile(config_file_name):
        with open(config_file_name) as f:
            parser = SafeConfigParser()
            parser.read(config_file_name)
            if parser.has_option('API', 'api_key'):
                api_key = parser.get('API', 'api_key')
            if parser.has_option('API', 'clan'):
                clan_id = parser.get('API', 'clan')
            if parser.has_option('Paths', 'out'):
                output_path = parser.get('Paths', 'out')
            if parser.has_option('Paths', 'favicon'):
                favicon_path = parser.get('Paths', 'favicon')
            if parser.has_option('Paths', 'clan_logo'):
                logo_path = parser.get('Paths', 'clan_logo')
            if parser.has_option('Paths', 'description_html'):
                description_path = parser.get('Paths', 'description_html')
            if parser.has_option('www', 'canonical_url'):
                canonical_url = parser.get('www', 'canonical_url')

    # if API key has not been set (is False), then API key needs to be specified as a command line argument
    api_key_required = clan_id_required = False  
    if api_key == False:
        api_key_required = True
    if clan_id == False:
        clan_id_required = True

    # parse command line arguments
    parser = ArgumentParser(prog        = "crtools",
                            description = """A tool for creating a dashboard for clan participation in 
                                             ClashRoyale. See https://developer.clashroyale.com to sign up 
                                             for a developer account and create an API key to use with this."""
                            )
    parser.add_argument("--api_key",
                        metavar  = "KEY",
                        help     = "API key for developer.clashroyale.com",
                        required = api_key_required)
    parser.add_argument("--clan",
                        help    = "Clan ID from Clash Royale. If it starts with a '#', clan ID must be quoted.",
                        required = clan_id_required)
    parser.add_argument("--out",
                        metavar  = "PATH",
                        help     = "Output path for HTML.")
    parser.add_argument("--favicon",
                        metavar  = "PATH",
                        help     = "Source path for favicon.ico. If provided, we will copy to the output directory.")
    parser.add_argument("--clan_logo",
                        metavar  = "PATH",
                        help     = "Source path for clan logo PNG. Recommended at least 64x64 pizels. If provided, we will copy to the output directory.")
    parser.add_argument("--description",
                        metavar  = "PATH",
                        help     = "Source path snippet of HTML to replace the clan description. Should not be a complete HTML document. Sample here: https://github.com/AaronTraas/crtools-agrassar-assets/blob/master/description.html\n\nIf provided, we will copy to the output directory.")
    parser.add_argument("--canonical_url",
                        metavar  = "URL",
                        help     = "Canonical URL for this site. Used for setting the rel=canonical link in the web site, as well as generating the robots.txt and sitemap.xml")

    args = parser.parse_args()

    # grab API key and clan ID from arguments if applicable
    if args.api_key:
        api_key = args.api_key
    if args.clan:
        clan_id = args.clan
    if args.out:
        output_path = args.out
    if args.favicon:
        favicon_path = args.out
    if args.clan_logo:
        logo_path = args.out
    if args.description:
        description_path = args.out
    if args.canonical_url:
        canonical_url = args.out
    
    # Build the dashboard
    build_dashboard(api_key, clan_id, logo_path, favicon_path, description_path, output_path, canonical_url)

