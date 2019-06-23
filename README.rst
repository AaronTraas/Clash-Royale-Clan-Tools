==================================================
crtools - Clash Royale Clan Dashboard generator
==================================================

This is a tool for creating a dashboard for clan participation in ClashRoyale.
See https://developer.clashroyale.com to sign up for a developer account and
create an API key to use with this.

For an example dashboard created for the clan Agrassar (#JY8YVV), see: https://agrassar.com/

This tool is a static site generator -- it generates static HTML, JavaScript,
and CSS used to render the dashboard. If you wish to use this, you should set
it up to run once per hour on your web server.

==================================================
Installation
==================================================

This requires Python 3 and pip on your machine. To install, use

.. code::

  pip3 install crtools

If you have an older version installed, to upgrade to the latest version, run:

.. code::

  pip3 install -U crtools


==================================================
Syntax
==================================================

Usage:

.. code::

  crtools [-h] [--locale LOCALE] [--config CONFIG-FILE] [--api_key KEY]
          [--clan TAG] [--out PATH] [--favicon PATH] [--clan_logo PATH]
          [--description PATH] [--canonical_url URL] [--debug]
          [--version]

optional arguments:
  -h, --help           show this help message and exit
  --locale LOCALE      Locale if language other than English is desired. Currently, only "fr" is valid.
  --config FILE        configuration file for this app.
  --api_key KEY        API key for developer.clashroyale.com
  --clan CLAN          Clan ID from Clash Royale. If it starts with a '#', clan ID must be quoted.
  --out PATH           Output path for HTML.
  --favicon PATH       Source path for favicon.ico. If provided, we will copy to the output directory.
  --clan_logo PATH     Source path for clan logo PNG. Recommended at least 64x64 pizels. If provided, we will copy to the output directory.
  --description PATH   Source path snippet of HTML to replace the clan description. Should not be a complete HTML document. Sample here: https://github.com/AaronTraas/crtools-agrassar-assets/blob/master/description.html If provided, we will copy to the output directory.
  --canonical_url URL  Canonical URL for this site. Used for setting the rel=canonical link in the web site, as well as generating the robots.txt and sitemap.xml
  --debug              Turns on debug mode
  --version            List the version of crtools.

==================================================
Optional config file
==================================================

crtools looks for a config file in your home directory called .crtools

This is an INI file. As of current version, there's only one possible
parameter: api_key. The file should look like:

.. code:: ini

  [API]
  # API key provided for your account at https://developer.clashroyale.com
  # Note that the key is limited to a specific list of public IP addresses
  api_key=<YOUR-API-KEY>

  # Your clan tag
  clan_id=#JY8YVV

  [Paths]
  # your output path. Where you want the static website to live.
  out=/var/www/html

  # Path to the logo artwork for clan. Must be PNG. Recommended at
  # least 64x64 pixels.
  clan_logo=~/myclan/logo.png

  # Path to the favicon file you want to use for this
  favicon=~/myclan/favicon.ico

  # Path to a file that contains arbitrary HTML for the site.
  description_html=~/myclan/body.html

  [www]
  # Canonical URL for this site. Used for setting the rel=canonical
  # link in the web site, as well as generating the robots.txt
  # and sitemap.xml
  canonical_url=https://yourclan.com/

For more details, see `samples/crtools.ini <https://github.com/AaronTraas/Clash-Royale-Clan-Tools/blob/master/samples/crtools.ini>`_

==================================================
Using the ClashRoyale Official Fan Kit
==================================================

The design of this site is optionally enhanced by the fan kit provided by
Supercell here. To enable automated downloading of the fan kit, add:

.. code::

  use_fankit=True

To the :code:`[Paths]` section of your config file.

NOTE: This requires about 5GB free in your temp forlder on the machine that
crtools runs on. It will take 10-15 minutes to download and extract, but only
the first time you run with the fankit enabled.

If you have problems, you can manually install the fan kit. See
`Fan Kit Manual Install Instructions <https://github.com/AaronTraas/Clash-Royale-Clan-Tools/blob/master/fankit-manual-install.md>`_

==================================================
Other languages/locales
==================================================

Crtools currently supports English and French. If you'd like to use French,
add the following switch on the command line:

.. code::

  --locale=fr

If you wish for crtools to be available in another languages, reach out to
me. I'm unable to do the translation myself (I speak only English), but I can
help you provide a translation for this.

==================================================
Suggested usage on a Linux web server
==================================================

This tool is a static site generator -- it generates static HTML, JavaScript,
and CSS used to render the dashboard. If you wish to use this, you should set
it up to run once per hour on your web server using :code:`cron` or similar.
Below is an example setup on Linux.

Assuming root is going to be running the script:

1. Install this application via pip
2. Install nginx or apache
3. Find your document root (e.g., :code:`/var/www/html`)
4. Create :code:`/root/.crtools` file as specified above, and add your
   API key (from https://developer.clashroyale.com), output path (the
   document root), and clan tag
5. Create the following entry in your crontab:

.. code::

  0 * * * * crtools

==================================================
Development links
==================================================

This project uses SonarQube for static analysis. The results of analysis
are at `SonarCloud <https://sonarcloud.io/dashboard?id=AaronTraas_Clash-Royale-Clan-Tools>`_.
The code quality and test coverage are a work in progress.

==================================================
Support
==================================================

If you need help getting this up and running, feel free to hop on the
`crtools discord <https://discord.gg/K2UDCXU>`_.

Keep in mind, this is a command-line utility that expects a working Python 3
environment. It also assumes you will know how to configure a web server to
serve up HTML, as well as cron or similar on your given platform. There is no
install wizard, GUI of any kind, etc.

==================================================
Contributors
==================================================

All of the non-code contributors are listed in
`CONTRIBUTORS.rst <https://github.com/AaronTraas/Clash-Royale-Clan-Tools/blob/master/CONTRIBUTORS.rst>`_

==================================================
Image rights
==================================================

All images except the flags included in this repository were created by the
team, and are included in the GPL license. The SVGs were all created in
Inkscape.

The flags included are from http://www.famfamfam.com/lab/icons/flags/, which
as of 5/27/2019 stated it required no attribution or license. We are
interpreting this to mean these are available in the public domain.

It was important to us to make sure the entirety of this application is
open source, and not subject to takedown request. We will not ever
extract assets from the game or from any other web properties.

Optionally, crtools can download the official Clash Royale fan kit and use
some of the content contained. This is not the default behavior, and no
works copywritten by Supercell are contained within this code.

This content is not affiliated with, endorsed, sponsored, or specifically
approved by Supercell and Supercell is not responsible for it. For more
information see Supercell's Fan Content Policy: https://supercell.com/en/fan-content-policy/
