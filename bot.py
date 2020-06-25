#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
<one line to give the program's name and a brief idea of what it does.>
Copyright (C) <2020>  <Abdeladim S.>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

from __future__ import print_function

import time
import random
import pyautogui
import clipboard
import urllib.request
import speech_recognition as sr
from pydub import AudioSegment
from pynput import keyboard


class Element:

    def __init__(self, name: str, img_path: str):
        self.name = name
        self.img_path = img_path
        self.x = None
        self.y = None


class Bot:

    def __init__(self):
        pyautogui.FAILSAFE = True  # abort the program by movingthe mouse to the upper-left corner
        self.delay = 2  # delay between actions
        self.captcha_box = Element('captcha_box', './images/captcha_box.png')
        self.ok = Element('ok', './images/ok.png')

    @staticmethod
    def find_automatically(element: Element):
        element_location = pyautogui.locateCenterOnScreen(element.img_path)
        if element_location is not None:
            element.x, element.y = element_location
            return True
        else:
            return False

    @staticmethod
    def find_manually(element: Element):
        pyautogui.alert("Couldn't find the element, navigate to the center of the element and press CTRL")

        def on_press(key):
            if key == keyboard.Key.ctrl:
                element.x, element.y = pyautogui.position()
                return False

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def find(self, element: Element):
        if element.x is not None:
            return
        if self.find_automatically(element):
            pass
        else:
            self.find_manually(element)
        print(element.name + ' at: {}, {}'.format(element.x, element.y))

    def goto(self, delta_x, delta_y):
        x = self.captcha_box.x + delta_x
        y = self.captcha_box.y + delta_y
        self.human_behaviour_click(x, y)
        time.sleep(self.delay)

    def download_audio_and_recognize(self):
        print('Clicking the download button ...')
        # 167 * 50 -> download
        self.goto(167, 50)

        print('Downloading audio ...')
        self.copy_url()
        url = clipboard.paste()
        print(url)
        urllib.request.urlretrieve(url, 'cache/audio.mp3')
        audio_text = self.recognize_audio()
        return audio_text

    @staticmethod
    def copy_url():
        # select url
        pyautogui.press('f6')
        # copy
        pyautogui.hotkey('ctrl', 'c')
        # close tab
        pyautogui.hotkey('ctrl', 'w')

    @staticmethod
    def recognize_audio():
        sound = AudioSegment.from_mp3('cache/audio.mp3')
        sound.export('cache/audio.wav', format="wav")
        AUDIO_FILE = 'cache/audio.wav'
        # use the audio file as the audio source
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)  # read the entire audio file

        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            output = r.recognize_google(audio)
            print("Google Speech Recognition thinks the audio is saying: " + output)
            return output
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return None

    @staticmethod
    def human_behaviour_click(x, y):
        tween_list = [pyautogui.easeInQuad, pyautogui.easeOutQuad, pyautogui.easeInOutQuad, pyautogui.easeInBounce,
                      pyautogui.easeInElastic]
        pyautogui.moveTo(x, y, duration=0.5, tween=random.choice(tween_list))
        pyautogui.click()

    def run(self):
        time.sleep(self.delay)
        print("Searching for the captcha box ... ")
        self.find(self.captcha_box)
        self.human_behaviour_click(self.captcha_box.x, self.captcha_box.y)
        time.sleep(self.delay)

        print('Clicking the audio button ...')
        self.goto(105, 265)

        audio_text = self.download_audio_and_recognize()

        # loop till getting a recognizable challenge
        while audio_text is None:
            # press refresh to get another challenge
            print("Couldn't recognize the audio, get another one!")
            print("Clicking the refresh button ... ")
            # 59 * 11 -> refresh button
            self.goto(59, 11)
            audio_text = self.download_audio_and_recognize()

        print("Clicking the text field ...")
        # 160 * 0 -> text field
        self.goto(160, 0)

        # write the text
        pyautogui.write(audio_text)

        print("Clicking the verify button ...")
        # 249 * 111 -> verify
        self.goto(249, 111)

        # checking for ok
        print("Checking for OK!")
        if self.find_automatically(self.ok):
            print('DONE!')
        else:
            print('Something went wrong :(')


if __name__ == '__main__':
    bot = Bot()
    bot.run()