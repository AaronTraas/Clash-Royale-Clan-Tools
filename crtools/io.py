import codecs
from datetime import datetime, date, timezone, timedelta
from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
import json
import logging
import os
import shutil

from ._version import __version__

logger = logging.getLogger(__name__)

HISTORY_FILE_NAME = 'history.json'

CLAN_LOG_FILENAME = 'clan_logo.png'
FAVICON_FILENAME = 'favicon.ico'

def write_object_to_file(file_path, obj):
    """ Writes contents of object to file. If object is a string, write it
    directly. Otherwise, convert it to JSON first """

    # open file for UTF-8 output, and write contents of object to file
    with codecs.open(file_path, 'w', 'utf-8') as f:
        if isinstance(obj, str):
            string = obj
        else:
            string = json.dumps(obj, indent=4)
        f.write(string)

def get_previous_history(output_dir):
    """ grab history, if it exists, from output paths """

    if not output_dir:
        return None

    history_path = os.path.join(output_dir, HISTORY_FILE_NAME)
    if not os.path.isfile(history_path):
        return None

    with open(history_path, 'r') as myfile:
        return json.loads(myfile.read())

def copy_static_assets(tempdir, clan_logo_path, favicon_path):
    # copy static assets to output path
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'static'), os.path.join(tempdir, 'static'))

    # copy user-provided assets to the output path
    shutil.copyfile(clan_logo_path, os.path.join(tempdir, CLAN_LOG_FILENAME))
    shutil.copyfile(favicon_path, os.path.join(tempdir, FAVICON_FILENAME))


def parse_templates(config, history, tempdir, clan, members, former_members, current_war, recent_wars, suggestions, scoring_rules): # pragma: no coverage
    # Create environment for template parser
    env = Environment(
        loader=PackageLoader('crtools', 'templates'),
        autoescape=select_autoescape(['html', 'xml']),
        undefined=StrictUndefined
    )

    dashboard_html = env.get_template('page.html.j2').render(
        version           = __version__,
        config            = config,
        strings           = config['strings'],
        update_date       = datetime.now().strftime('%c'),
        members           = members,
        clan              = clan,
        clan_hero         = config['paths']['description_html_src'],
        current_war       = current_war,
        recent_wars       = recent_wars,
        suggestions       = suggestions,
        scoring_rules     = scoring_rules,
        former_members    = former_members
    )

    write_object_to_file(os.path.join(tempdir, 'index.html'), dashboard_html)
    write_object_to_file(os.path.join(tempdir, HISTORY_FILE_NAME), history)

    # If canonical URL is provided, also render the robots.txt and
    # sitemap.xml
    if config['www']['canonical_url'] != False:
        lastmod = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        sitemap_xml = env.get_template('sitemap.xml.j2').render(
                url     = config['www']['canonical_url'],
                lastmod = lastmod
            )
        robots_txt = env.get_template('robots.txt.j2').render(
                canonical_url = config['www']['canonical_url']
            )
        write_object_to_file(os.path.join(tempdir, 'sitemap.xml'), sitemap_xml)
        write_object_to_file(os.path.join(tempdir, 'robots.txt'), robots_txt)

def dump_debug_logs(tempdir, objects_to_dump):
    """ archive outputs of API and other objects for debugging """
    log_path = os.path.join(tempdir, 'log')
    os.makedirs(log_path)
    for name, obj in objects_to_dump.items():
        write_object_to_file(os.path.join(log_path, name+'.json'), obj)

def move_temp_to_output_dir(tempdir, output_dir):
    if os.path.exists(output_dir):
        # remove contents of output directory to cleanup.
        try:
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
        except PermissionError as e:
            logger.error('Permission error: could not delete: \n\t{}'.format(e.filename))
    else:
        # Output directory doesn't exist. Create it.
        logger.debug('Output directory {} doesn\'t exist. Creating it.'.format(output_dir))
        try:
            os.mkdir(output_dir)
        except PermissionError as e: # pragma: no coverage
            logger.error('Permission error: could create output folder: \n\t{}'.format(e.filename))

    # Copy all contents of temp directory to output directory
    # NOTE: not in try/catch block because if the above executed, we already
    # have sufficient privileges to write to the output directory
    for file in os.listdir(tempdir):
        file_path = os.path.join(tempdir, file)
        file_out_path = os.path.join(output_dir, file)
        if os.path.isfile(file_path):
            shutil.copyfile(file_path, file_out_path)
        elif os.path.isdir(file_path):
            shutil.copytree(file_path, file_out_path)
