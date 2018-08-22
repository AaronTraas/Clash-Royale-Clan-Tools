==================================================
Clash Royale Clan Tools
==================================================

This is a tool for creating a dashboard for clan participation in ClashRoyale. See https://developer.clashroyale.com to sign up for a developer account and create an API key to use with this.

==================================================
Syntax
==================================================

Python tools for creating a clan maagement dashboard for Clash Royale

usage: crtools [-h] [--api_key KEY] clan_id

Tools for creating a clan maagement dashboard for Clash Royale

positional arguments:
  clan_id        Clan ID from Clash Royale. If it starts with a '#', clan ID
                 must be quoted.

optional arguments:
  -h, --help     show this help message and exit
  --api_key KEY  API key for developer.clashroyale.com

==================================================
Optional config file
==================================================

crtools looks for a config file in your home directory called .crtools

This is an INI file. As of current version, there's only one possible parameter: api_key. The file should look like:

