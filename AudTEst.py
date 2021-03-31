# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 12:38:59 2021

@author: jayes
"""

from win32com.client import Dispatch

def speak(str):
    speak = Dispatch(("SAPI.SpVoice"))
    speak.Speak(str)

if __name__ == '__main__':
    speak("Hello JAyesh Audio Modual testing ")