from argparse import ArgumentParser, RawDescriptionHelpFormatter
import os
import sys

from ._version import __version__
from .crtools import build_dashboard
from .config import load_config_file


def main():
    # parse command line arguments
    parser = ArgumentParser(prog        = "crtools",
                            description = """A tool for creating a dashboard for clan participation in
                                             ClashRoyale. See https://developer.clashroyale.com to sign up
                                             for a developer account and create an API key to use with this.""")
    parser.add_argument("--config",
                        metavar  = "CONFIG-FILE",
                        help     = "configuration file for this app.")
    parser.add_argument("--api_key",
                        metavar  = "KEY",
                        help     = "API key for developer.clashroyale.com")
    parser.add_argument("--clan",
                        metavar  = "TAG",
                        help    = "Clan ID from Clash Royale. If it starts with a '#', clan ID must be quoted.")
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
                        help     = "Canonical URL for this site. Used for setting the rel=\"canonical\" link in the web site, as well as generating the robots.txt and sitemap.xml")
    parser.add_argument("--debug",
                        action   = 'store_true',
                        help     = "Turns on debug mode")

    args = parser.parse_args()

    if args.config:
        config_file_name = args.config
        os.path.expanduser(config_file_name)
        if os.path.isfile(config_file_name) == False:
            print("Config file specified {} not found")
            exit(-1)
    else:
        config_file_name = os.path.expanduser('~/.crtools')

    config = load_config_file(config_file_name)

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
    if args.debug:
        config['crtools']['debug'] = True

    # Build the dashboard
    build_dashboard(config)
