#!/usr/local/bin/python3

import cal_manager
import google_cal

from kivy.app import App

from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.lang import Builder

from random import randint

theme_color = [0.31, 0.89, 0.76, 1]
white_color = [1, 1, 1, 1]
black_color = [0, 0, 0, 1]
yes_resp = ['OK. ', 'Got it. ', 'Sure. ', 'All right. ', '']
cancel_intents = ['cancel', 'never mind', 'forget it', 'quit', 'restart', 'start over']

cal = cal_manager.CalendarManager()

Builder.load_string('''
<ScrollableLabel>:
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
''')


class ScrollableLabel(ScrollView):
    text = StringProperty("Hello. Ask me to schedule an event.\n")


class ChatApp(App):

    user_last_msg = ""
    event_data = None
    info_requested = False
    request = None   # Field to check if info_requested

    def build(self):

        main_box_layout = BoxLayout(orientation='vertical',
                                    padding=20,
                                    spacing=10)

        in_box_layout = BoxLayout(orientation='horizontal',
                                  spacing=10,
                                  size_hint_y=0.08)

        chat_view = ScrollableLabel()

        text_field = TextInput(background_color=white_color,
                               foreground_color=black_color,
                               cursor_color=black_color,
                               hint_text="Enter your event details",
                               size_hint_x=0.8,
                               multiline=False)

        button = Button(text='Send',
                        size_hint_x=0.2,
                        background_color=theme_color,
                        color=white_color)

        def get_bot_response():
            if self.user_last_msg.lower().replace('.', '') in cancel_intents:
                update_chat("Canceling event creation.", confirm=True)
            else:
                if self.info_requested:
                    validate_user_response()
                else:
                    self.event_data = cal.send_query(self.user_last_msg)

                if validate_event_data():
                    create_event()
                else:
                    add_request_to_chat()

        def add_request_to_chat():
            if self.info_requested:
                if self.request == 'title':
                    update_chat("What would you like to name your event?", confirm=True)
                elif self.request == 'start_date':
                    if 'start_time' not in self.event_data:
                        update_chat("Tell me the date and time of your event.", confirm=True)
                    else:
                        update_chat("What day is your event?", confirm=True)
                elif self.request == 'start_time':
                    update_chat("What time is your event?", confirm=True)

        # Checks if essential event information is provided
        def validate_event_data():
            if self.event_data:
                if 'title' not in self.event_data:
                    request_data('title')
                elif 'start_date' not in self.event_data:
                    request_data('start_date')
                elif 'start_time' not in self.event_data:
                    request_data('start_time')
                else:
                    self.info_requested = False
            else:
                update_chat("I'm sorry. I don't understand.")
                return False

            return not self.info_requested

        # TODO: validate date/time and format for event creation
        def validate_user_response():
            if self.info_requested:
                if self.request == 'title':
                    self.event_data['title'] = self.user_last_msg.title()
                elif self.request == 'start_date':
                    # TODO: Might check for both date and time here
                    self.event_data['start_date'] = self.user_last_msg
                elif self.request == 'start_time':
                    self.event_data['start_time'] = self.user_last_msg

        def create_event():
            update_chat("Creating your event \"{}\".".format(self.event_data['title']), confirm=True)
            google_cal.create_event(self.event_data)
            for key, value in self.event_data.items():
                update_chat(key + ': ' + value)
            self.event_data = None

        def request_data(detail):
            self.request = detail
            self.info_requested = True

        def add_user_response(msg):
            self.user_last_msg = msg
            if msg == '':
                update_chat("Sorry, that's not a valid query.")
            else:
                update_chat(msg, is_user=True)
                text_field.text = ''
                get_bot_response()

        # string, bool, bool
        def update_chat(text, is_user=False, confirm=False):
            if is_user:
                chat_view.text += '> '
            elif confirm:
                chat_view.text += yes_resp[randint(0, len(yes_resp) - 1)]

            chat_view.text += text + '\n'

        button.bind(on_press=lambda x: add_user_response(text_field.text))
        text_field.bind(on_text_validate=lambda x: add_user_response(text_field.text))

        main_box_layout.add_widget(chat_view)
        main_box_layout.add_widget(in_box_layout)

        in_box_layout.add_widget(text_field)
        in_box_layout.add_widget(button)

        return main_box_layout


if __name__ == "__main__":
    ChatApp().run()
