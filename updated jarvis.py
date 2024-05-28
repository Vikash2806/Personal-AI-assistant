import cv2
import mediapipe as mp
import webbrowser
import speech_recognition as sr
import pyttsx3
import os
import datetime
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import wmi
import pyautogui
import threading

# Constants
BRAVE_PATH = r"C:\Users\VIKASH\AppData\Local\BraveSoftware\Brave-Browser\Application\brave"
TELEGRAM_PATH = r"C:\Users\VIKASH\AppData\Roaming\Telegram Desktop\Telegram"
WEBSITE_URL = "https://vikash2806.github.io/Portfolio-Website/"
COLLEGE_WEBSITE_URL = "https://sastra.edu/"
CHATGPT_URL = "https://chat.openai.com/"

# Initialize speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Flag to control camera activation
camera_active = False

# Functions for TTS and STT
def say(text):
    engine.say(text)
    engine.runAndWait()

def type_text(text):
    pyautogui.typewrite(text)
    pyautogui.press('enter')

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 0.6
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""

# Functions for volume and brightness control
def set_volume(change):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_volume = volume.GetMasterVolumeLevelScalar()
    new_volume = max(0.0, min(1.0, current_volume + change))
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    say(f"Volume set to {int(new_volume * 100)} percent")

def set_volume_level(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    if level == "zero":
        volume.SetMasterVolumeLevelScalar(0.0, None)
        say("Volume set to zero percent")
    elif level == "maximum":
        volume.SetMasterVolumeLevelScalar(1.0, None)
        say("Volume set to maximum percent")

def set_brightness(change):
    c = wmi.WMI(namespace='wmi')
    methods = c.WmiMonitorBrightnessMethods()[0]
    brightness = c.WmiMonitorBrightness()[0].CurrentBrightness
    new_brightness = max(0, min(100, brightness + change))
    methods.WmiSetBrightness(new_brightness, 0)
    say(f"Brightness set to {new_brightness} percent")

def set_brightness_level(level):
    if level == "zero":
        set_brightness(-100)
    elif level == "maximum":
        set_brightness(100)

def google_search(query):
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(search_url)
    say(f"Here are the search results for {query}")

def process_camera():
    global camera_active
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    cap = cv2.VideoCapture(0)

    while camera_active:
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                # Example gesture detection (simple vertical movement)
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                if index_finger_tip.y < middle_finger_tip.y:
                    print("Scroll up detected")
                    pyautogui.scroll(90)
                else:
                    print("Scroll down detected")
                    pyautogui.scroll(-90)

        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

def execute_command(query):
    global camera_active
    if "unlock friday" in query:
        say("Unlocking Friday in 5 seconds ...")
        camera_active = True
        camera_thread = threading.Thread(target=process_camera)
        camera_thread.start()

    elif "make a google search on" in query:
        search_query = query.replace("make a google search on ", "")
        google_search(search_query)

    elif "unlock jarvis" in query:
        say("Unlocking Jarvis...")
        camera_active = False

    elif "open youtube" in query:
        say("Opening YouTube, Sir...")
        webbrowser.open("https://youtube.com")

    elif "open google" in query:
        say("Opening Google, Sir...")
        webbrowser.open("https://www.google.com/")

    elif "open my website" in query:
        say("Opening your website, Sir...")
        webbrowser.open(WEBSITE_URL)

    elif "open brave browser" in query:
        say("Opening Brave browser, Sir...")
        os.startfile(BRAVE_PATH)

    elif "open telegram" in query:
        say("Opening Telegram, Sir...")
        os.startfile(TELEGRAM_PATH)

    elif "open chat" in query:
        say("Opening ChatGPT, Sir...")
        webbrowser.open(CHATGPT_URL)

    elif "open my college website" in query:
        say("Opening your college website, Sir...")
        webbrowser.open(COLLEGE_WEBSITE_URL)

    elif "who created you" in query or "who built you" in query:
        say("I am AI assistant created by Vikash")

    elif "who is vikas" in query:
        say("He created me!")

    elif "how are you" in query:
        say("I am awesome, what about you")

    elif "set volume to maximum" in query or "volume to maximum" in query:
        set_volume_level("maximum")

    elif "increase volume" in query:
        set_volume(0.1)

    elif "decrease volume" in query:
        set_volume(-0.1)

    elif "set volume to zero" in query or "volume to zero" in query:
        set_volume_level("zero")

    elif "increase brightness" in query:
        set_brightness(10)

    elif "decrease brightness" in query:
        set_brightness(-10)

    elif "set brightness to zero" in query or "brightness to zero" in query:
        set_brightness_level("zero")

    elif "set brightness to maximum" in query or "brightness to maximum" in query:
        set_brightness_level("maximum")

    elif "make a google search of" in query:
        search_query = query.replace("make a google search of ", "")
        google_search(search_query)

    elif "type" in query:
        text_to_type = query.replace("type", "").strip()
        type_text(text_to_type)

    elif "time" in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        say(f"Sir, the time is {current_time}")

    elif "stop" in query:
        say("Goodbye, Sir")
        return False

    elif "go to search" in query:
        say("Going to search bar")
        pyautogui.press('/')

    elif "delete all" in query:
        say("Deleting all text")
        pyautogui
