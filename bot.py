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


class Bot:

    def __init__(self):
        pyautogui.FAILSAFE = True # abort the program by moving the mouse to the upper-left corner
        self.captcha_box_X = 0
        self.captcha_box_Y = 0

    def setup(self):
        if not self.find_captcha_box():
            print("Couldn't find the captcha box")
            pyautogui.alert('You have 3 seconds to move the cursor manually to the top left corner')
            t_end = time.time() + 4
            while time.time() < t_end:
                self.captcha_box_X, self.captcha_box_Y = pyautogui.position()
                print(self.captcha_box_X, self.captcha_box_Y)

    def find_captcha_box(self):
        print('searching for the captcha box ... (This may take a while!)')
        captcha = pyautogui.locateOnScreen('images/captcha.png')
        if captcha is not None:
            self.captcha_box_X = captcha.left + 15
            self.captcha_box_Y = captcha.top + 15
            print('Found captcha at: {}, {}'.format(self.captcha_box_X, self.captcha_box_Y))
            return True
        return False

    @staticmethod
    def find(path):
        element_location = pyautogui.locateCenterOnScreen(path)
        if element_location is not None:
            return element_location.left, element_location.top
        else:
            return False

    def click_captcha_box(self):
        x = self.captcha_box_X + random.randint(5, 20)  # add some random number in case if there is any mouse behaviour detection
        y = self.captcha_box_Y + random.randint(5, 30)
        self.human_behaviour_click(x, y)

    @staticmethod
    def recognize_audio():
        sound = AudioSegment.from_mp3('./cache/audio.mp3')
        sound.export('cache/audio.wav', format="wav")
        AUDIO_FILE = 'cache/audio.wav'
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)
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

    @staticmethod
    def check_for_ok():
        print('Checking for OK ... (This may take a while!)')
        ok_location = pyautogui.locateOnScreen('images/ok.png')
        if ok_location is not None:
            print('OK! DONE :)')
            return True
        else:
            print("Not OK! What a bad luck!")
            return False

    def run(self) -> None:
        print('running ...')
        self.click_captcha_box()
        time.sleep(3)

        # Check if it is OK, maybe! who knows ;)
        if self.check_for_ok():
            return
        print("No worries, let's hack it!")
        # clicking the audio icon
        x = self.captcha_box_X + 115
        y = self.captcha_box_Y + 282
        self.human_behaviour_click(x, y)
        time.sleep(3)

        audio_text = None
        # while audio_text is None:
        # right click the download button to copy the url of the audio
        x = self.captcha_box_X + 183
        y = self.captcha_box_Y + 60
        pyautogui.rightClick(x, y)
        x = x + 37
        y = y + 130
        self.human_behaviour_click(x, y)

        # download the audio file to the cache dir
        url = clipboard.paste()
        print(url)
        urllib.request.urlretrieve(url, 'cache/audio.mp3')
        audio_text = self.recognize_audio()
        if audio_text is None:
            # press get another challenge
            print("Couldn't recognize the audio, get another one!")
            x = self.captcha_box_X + 74
            y = self.captcha_box_Y + 138
            pyautogui.rightClick(x, y, duration=1)

        # write down the output from the recognizer
        x = x - 66
        y = y - 188
        self.human_behaviour_click(x, y)
        pyautogui.write(audio_text)

        # click verify
        x = x + 98
        y = y + 110
        self.human_behaviour_click(x, y)
        time.sleep(3)

        # recheck
        if self.check_for_ok():
            return


if __name__ == '__main__':
    bot = Bot()
    bot.setup()
    bot.run()
