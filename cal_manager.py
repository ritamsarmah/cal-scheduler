#!/usr/local/bin/python3

import json
import requests
import config

# NOTE: key and appID are included in config file
BASE_URL = "https://westus.api.cognitive.microsoft.com"
CREATE_EVENT_INTENT = "builtin.intent.calendar.create_calendar_entry"


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
                    event_data['title'] = value.title()
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

    @staticmethod
    def print_output(event_data):
        for key, value in event_data.items():
            print(key + ": " + value)

    def __init__(self):
        pass
