#!/usr/local/bin/python3

import httplib2
import os
import config
import parsedatetime as pdt
from tzlocal import get_localzone
from datetime import datetime, timedelta

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# Global Constants
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Cal Scheduler'


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
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def create_event(event_data):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # Convert LUIS event data to Google Calendar format
    event = {}
    print(str(event_data))

    for key, value in event_data.items():
        if key == 'title':
            event['summary'] = value
        elif key == 'location':
            event['location'] = value

    # Convert start_date and start_time
    start = convert_to_datetime(event_data['start_date'] + ' at ' + event_data['start_time'])
    event['start'] = {
        'dateTime': convert_to_rfc3339(start),
        'timeZone': str(get_localzone())
    }

    # Convert end_date and end_time
    end_date = start + timedelta(hours=1)
    end_time = end_date  # default 1 hour

    if 'end_date' in event_data:
        end_date = event_data['end_date']

    if 'end_time' in event_data:
        end_time = event_data['end_time']
    elif 'duration' in event_data:
        end_time = convert_to_datetime(event_data['duration'] + ' from ' + str(start))

    end = convert_to_datetime(str(end_date) + ' at ' + str(end_time))

    event['end'] = {
        'dateTime': convert_to_rfc3339(end),
        'timeZone': str(get_localzone())
    }

    print(str(event))

    event = service.events().insert(calendarId=config.email, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


def convert_to_datetime(value):
    pdt_cal = pdt.Calendar()
    time_struct, parse_status = pdt_cal.parse(value)
    return datetime(*time_struct[:6])


# Returns in RFC 3339
def convert_to_rfc3339(d):
    return d.isoformat()
