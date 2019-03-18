from argparse import ArgumentParser, RawDescriptionHelpFormatter
import codecs
import json
from pprint import pprint
import os
import sys

def write_object_to_file(file_path, obj):
    with codecs.open(file_path, 'w', 'utf-8') as f:
        f.write(json.dumps(obj, indent=4))

parser = ArgumentParser(prog        = 'clean_history',
                        description = 'A tool for cleaning up issues with the history file, resulting from bugs in older versions.')
parser.add_argument('history',
                    metavar  = 'HISTORY-FILE',
                    help     = 'history file to clean')

args = parser.parse_args()

history_path = os.path.expanduser(args.history)

if os.path.isfile(history_path):
    with open(history_path, 'r') as myfile:
        history = json.loads(myfile.read())

        for tag, member in history['members'].items():
            last_event = None
            new_events = []
            for event in member['events']:
                event_copy = event.copy()
                if last_event:
                    if last_event['event'] == 'quit' and event['event'] == 'quit':
                        member['events'].remove(event)
                        print("Duplicate quit event found for member {}".format(tag))
                    else:
                        new_events.append(event_copy)
                else:
                    new_events.append(event_copy)
                last_event = event_copy
            history['members'][tag]['events'] = new_events

        write_object_to_file(history_path, history)
        #pprint(history)


