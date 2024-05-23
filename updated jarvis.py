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

def takeCommand():
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
    if level == "zero":
        set_volume(-1)
    elif level == "maximum":
        set_volume(1)

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

# Function to process camera input and detect gestures
def process_camera():
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
                    # Perform scroll up action
                    pyautogui.scroll(90)  # Scroll up by 10 units
                else:
                    print("Scroll down detected")
                    # Perform scroll down action
                    pyautogui.scroll(-90)  # Scroll down by 10 units

        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    say("Hello, I am Jarvis AI")

    while True:
        query = takeCommand()

        if not query:
            continue

        if "unlock friday" in query:
            say(" Unlocking Friday in 5 seconds ...")
            camera_active = True
            camera_thread = threading.Thread(target=process_camera)
            camera_thread.start()

        elif "make a google search on" in query:
            search_query = query.replace("make a google search of ", "")
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
            webbrowser.open("https://vikash2806.github.io/Portfolio-Website/")



        elif "open brave browser" in query:
            say("Opening Brave browser, Sir...")
            os.startfile(r"C:\Users\VIKASH\AppData\Local\BraveSoftware\Brave-Browser\Application\brave")

        elif "open telegram" in query:
            say("Opening Telegram, Sir...")
            os.startfile(r"C:\Users\VIKASH\AppData\Roaming\Telegram Desktop\Telegram")

        elif "open chat" in query:
            say("Opening ChatGPT, Sir..")
            webbrowser.open("https://chat.openai.com/")


        elif "open my college website" in query:
            say("Opening your college website, Sir...")
            webbrowser.open("https://sastra.edu/")

        elif "who created you" in query or "who built you" in query:
            say("I am AI assistant created by Vikash")

        elif "who is vikas" in query:
            say("He created me!")

        elif "how are you" in query:
            say("I am awesome  , what about you")


        elif "increase volume" in query:
            set_volume(0.1)

        elif "decrease volume" in query:
            set_volume(-0.1)

        elif "increase brightness" in query:
            set_brightness(10)

        elif "decrease brightness" in query:
            set_brightness(-10)

        elif "set volume to zero" in query:
            set_volume_level("zero")

        elif "set volume to maximum" in query:
            set_volume_level("maximum")

        elif "set brightness to zero" in query:
            set_brightness_level("zero")

        elif "set brightness to maximum" in query:
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
            break

        elif "go to search" in query:
            say("Going to search bar")
            pyautogui.press('/')

        elif "delete all" in query:
            say("Deleting all text")
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')

        elif "hello" in query:
            say("Hello Sir")


        else:
            print("Command not recognized")
