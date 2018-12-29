==================================================
Clash Royale Clan Tools
==================================================

This is a tool for creating a dashboard for clan participation in ClashRoyale. See https://developer.clashroyale.com to sign up for a developer account and create an API key to use with this.

For an example dashboard created for the clan Agrassar (#JY8YVV), see: https://agrassar.com/

==================================================
Installation
==================================================

This requires Python 3 and setup tools installed on your machine. See https://packaging.python.org/tutorials/installing-packages/ for details.

Once setuptools is installed, run the following in your shell:

.. code:: 

  python3 setup.py install
  
==================================================
Syntax
==================================================

Python tools for creating a clan maagement dashboard for Clash Royale

usage: crtools [-h] [--clan CLAN] [--out OUTPUT-PATH] [--api_key KEY]

optional arguments:
  -h, --help         show this help message and exit
  --clan CLAN        Clan ID from Clash Royale. If it starts with a '#', clan
                     ID must be quoted.
  --out OUTPUT-PATH  Output path for HTML.
  --api_key KEY      API key for developer.clashroyale.com

==================================================
Optional config file
==================================================

crtools looks for a config file in your home directory called .crtools

This is an INI file. As of current version, there's only one possible parameter: api_key. The file should look like:

.. code:: ini

  [API]
  # API key provided for your account at https://developer.clashroyale.com
  # Note that the key is limited to a specific list of public IP addresses
  api_key=<YOUR-API-KEY>

  # Your clan tag
  clan=#JY8YVV

  [Paths]
  # your output path. Where you want the static website to live.
  out=/var/www/html

  # Path to the logo artwork for clan. Must be PNG. Recommended at least 64x64 pixels.
  favicon=~/myclan/logo.png

  # Path to the favicon file you want to use for this
  favicon=~/myclan/favicon.ico

  # Path to a file that contains arbitrary HTML for the site.
  description_html=~/myclan/body.html

For more details, see crtools.ini

==================================================
Suggested usage on a Linux web server
==================================================

Assuming root is going to be running the script:

1. Download and install this application
2. Install nginx or apache
3. Create :code:`/root/.crtools` file as specified above, and add your API key
4. Find your document root (e.g., :code:`/var/www/html`)
5. Create the following entry in your crontab:

.. code::

  0 * * * * crtools --out=[YOUR-DOC-ROOT] [YOUR-CLAN-TAG]
  
For example:

.. code::

  0 * * * * crtools --out=/var/www/html \#JY8YVV

Note the '\' character before the # -- that's important. A '#' is a comment in most shells/scripting languages. You need to escape it to run it.
