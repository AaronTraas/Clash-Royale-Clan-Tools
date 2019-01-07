from argparse import ArgumentParser, RawDescriptionHelpFormatter
from configparser import SafeConfigParser
from jinja2 import Environment, PackageLoader, select_autoescape
import os
import sys

from ._version import __version__
from .crtools import build_dashboard

def main():
    # Create config dict with defaults
    config = {
        'api' : {
            'api_key' :             False,
            'clan_id' :             False,
        },
        'paths' : {
            'out' :                 './crtools-out',
            'favicon' :             False,
            'clan_logo' :           False,
            'description_html' :    False,
            'temp_dir_name' :       'crtools'
        },
        'www' : {
            'canonical_url' :       False,
        },
        'score' : {
            'min_clan_size' :       46,
            'war_good' :            20,
            'war_ok' :              1,
            'war_bad' :             -30,
            'war_na' :              -1,
            'min_donations_daily' : 12,
            'donations_zero' :      -40,
            'threshold_promote' :   160,
            'threshold_warn' :      30
        },
        'env' :                     Environment(
                                        loader=PackageLoader('crtools', 'templates'),
                                        autoescape=select_autoescape(['html', 'xml'])
                                    )
    }

    # Look for config file. If config file exists, load it, and try to 
    # extract API key from config file
    config_file_name = os.path.expanduser('~/.crtools')
    if os.path.isfile(config_file_name):
        parser = SafeConfigParser()
        parser.read(config_file_name)

        # Map the contents of the ini file with the structure for the config object found above.
        for section in parser.sections():
            section_key = section.lower()
            if section_key in config:
                for (key, value) in parser.items(section):
                    if key in config[section_key]:
                        # if the value represents an integer, convert from string to int
                        try: 
                            config[section_key][key] = int(value)
                        except ValueError:
                            config[section_key][key] = value


    # if API key has not been set (is False), then API key needs to be 
    # specified as a command line argument
    api_key_required = clan_id_required = False  
    if config['api']['api_key'] == False:
        api_key_required = True
    if config['api']['clan_id'] == False:
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
        config['api']['api_key'] = args.api_key
    if args.clan:
        config['api']['clan_id'] = args.clan
    if args.out:
        config['paths']['out'] = args.out
    if args.favicon:
        config['paths']['favicon'] = args.out
    if args.clan_logo:
        config['paths']['clan_logo'] = args.out
    if args.description:
        config['paths']['description_html'] = args.out
    if args.canonical_url:
        config['www']['canonical_url'] = args.out

    #import pprint; pprint.pprint(config); return
    
    # Build the dashboard
    build_dashboard(config)

