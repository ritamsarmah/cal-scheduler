#!/usr/local/bin/python3

import json, requests, httplib2
import os
import config
import time

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# For Google Calendar API
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# Global Constants
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Cal Scheduler'

# NOTE: key and appID are included in config file
BASE_URL = "https://westus.api.cognitive.microsoft.com"
CREATE_EVENT_INTENT = "builtin.intent.calendar.create_calendar_entry"


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


class CalendarManager:

    # Returns event_data
    def send_query(self, query):
        url = BASE_URL + "/luis/v2.0/apps/" + config.appID + "?subscription-key=" + config.key + "&q=" + query
        response = requests.get(url)
        response.raise_for_status()

        results = json.loads(response.text)
        intent = results['topScoringIntent']
        if intent['intent'] == CREATE_EVENT_INTENT:
            event_data = {}  # Dictionary with type:value (e.g. start_time:7pm)

            print(results)

            for entity in results['entities']:
                entity_type = entity['type']
                value = entity['entity']

                if entity_type == 'builtin.calendar.title':
                    event_data['title'] = value
                elif entity_type == 'builtin.calendar.start_time':
                    event_data['start_time'] = value
                elif entity_type == 'builtin.calendar.end_time':
                    event_data['end_time'] = value
                elif entity_type == 'builtin.calendar.duration':
                    event_data['duration'] = value
                elif entity_type == 'builtin.calendar.start_date':
                    event_data['start_date'] = value
                elif entity_type == 'builtin.calendar.end_date':
                    event_data['end_date'] = value
                elif entity_type == 'builtin.calendar.implicit_location':
                    event_data['location'] = value
                elif entity_type == 'builtin.calendar.destination_calendar':
                    event_data['dest_cal'] = value

            self.print_output(event_data)
            return event_data
        else:
            return None

    def create_event(self, event_data):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        event = {}  # Converts LUIS event data to Google Calendar format

        for key, value in event_data.items():
            if key == 'title':
                event['summary'] = value
            elif key == 'location':
                event['location'] = value
            elif key == 'start_time':
                event['start'] = {'dateTime': value}
            elif key == 'end_time':
                event['end'] = {'dateTime': value}

        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    @staticmethod
    def print_output(event_data):
        for key, value in event_data.items():
            print(key + ": " + value)

    def __init__(self):
        pass
