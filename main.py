#!/usr/local/bin/python3

import cal_manager

from kivy.app import App

from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.lang import Builder

from random import randint
import parsedatetime as pdt

theme_color = [0.31, 0.89, 0.76, 1]
white_color = [1,1,1,1]
black_color = [0,0,0,1]
yes_resp = ['OK. ', 'Got it. ', 'Sure. ', 'All right. ', '']

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
    text = StringProperty("Ask me to schedule any event.\n")


class ChatApp(App):

    user_last_msg = ""
    event_data = None
    info_requested = False

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
                               hint_text='Type in a question',
                               size_hint_x=0.8,
                               multiline=False)

        button = Button(text='Send',
                        size_hint_x=0.2,
                        background_color=theme_color,
                        color=white_color)

        def get_bot_response():
            if self.info_requested:
                # TODO: Check if valid datetime
                chat_view.text += yes_resp[randint(0, 3)] + "Creating your event.\n"
                self.info_requested = False
                # TODO: Parse using python datetime recognizer
                # TODO: Add valid datetime to event_data
                for key, value in self.event_data.items():
                    chat_view.text += key + ': ' + value + '\n'
            else:
                event_data = cal.send_query(self.user_last_msg)
                if event_data:
                    self.event_data = event_data
                    if 'start_date' not in event_data:
                        if 'start_time' not in event_data:
                            chat_view.text += yes_resp[randint(0,3)] + "Tell me the date and time of your event.\n"
                        else:
                            chat_view.text += yes_resp[randint(0, 3)] + "What day is your event?\n"
                        self.info_requested = True
                    elif 'start_time' not in event_data:
                        chat_view.text += yes_resp[randint(0, 3)] + "What time is your event?\n"
                        self.info_requested = True
                    else:
                        chat_view.text += yes_resp[randint(0, 3)] + "Creating your event.\n"
                        for key, value in self.event_data.items():
                            chat_view.text += key + ': ' + value + '\n'
                        self.info_requested = False
                else:
                    chat_view.text += "I'm sorry. I don't understand.\n"

        def update_chat(msg):
            self.user_last_msg = msg
            if msg == '':
                chat_view.text += "That is not a valid query.\n"
            else:
                chat_view.text += '> ' + msg + '\n'
                text_field.text = ''
                get_bot_response()

        button.bind(on_press=lambda x: update_chat(text_field.text))
        text_field.bind(on_text_validate=lambda x: update_chat(text_field.text))

        main_box_layout.add_widget(chat_view)
        main_box_layout.add_widget(in_box_layout)

        in_box_layout.add_widget(text_field)
        in_box_layout.add_widget(button)

        return main_box_layout


def convert_datetime(user_input):
    pdt_cal = pdt.Calendar()
    return pdt_cal.parse(user_input)


if __name__ == "__main__":
    ChatApp().run()

print(convert_datetime("tomorrow at 7pm"))