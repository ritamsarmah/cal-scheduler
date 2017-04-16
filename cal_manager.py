#!/usr/local/bin/python3

import json, requests, httplib2
import os
import config

# NOTE: key and appID are included in config file
base_url = "https://westus.api.cognitive.microsoft.com"
create_event_intent = "builtin.intent.calendar.create_calendar_entry"

class CalendarManager:

    # Returns event_data
    def send_query(self, query):
        url = base_url + "/luis/v2.0/apps/" + config.appID + "?subscription-key=" + config.key + "&q=" + query
        response = requests.get(url)
        response.raise_for_status()

        results = json.loads(response.text)
        intent = results['topScoringIntent']
        if intent['intent'] == create_event_intent:
            event_data = {}  # Dictionary with type:value (e.g. start_time:7pm)

            for entity in results['entities']:
                entity_type = entity['type']

                if entity_type == 'builtin.calendar.title':
                    event_data['title'] = entity['entity']
                elif entity_type == 'builtin.calendar.start_time' or entity_type == 'builtin.calendar.original_start_time':
                    resolution = entity['resolution']
                    for k, v in resolution.items():
                        if k == 'time':
                            event_data['start_time'] = v
                        elif k == 'duration':
                            event_data['duration'] = v
                elif entity_type == 'builtin.calendar.end_time':
                    resolution = entity['resolution']
                    for k, v in resolution.items():
                        if k == 'time':
                            event_data['end_time'] = v
                        elif k == 'duration':
                            event_data['duration'] = v
                elif entity_type == 'builtin.calendar.start_date':
                    event_data['start_date'] = entity['resolution']['date']
                elif entity_type == 'builtin.calendar.end_date':
                    event_data['end_date'] = entity['resolution']['date']
                elif entity_type == 'builtin.calendar.implicit_location':
                    event_data['location'] = entity['entity']
                elif entity_type == 'builtin.calendar.destination_calendar':
                    event_data['dest_cal'] = entity['entity']

            self.print_output(event_data)
            return event_data
        else:
            return None

    def print_output(self, event_data):
        for key, value in event_data.items():
            print(key + ": " + value)

    def __init__(self):
        pass
