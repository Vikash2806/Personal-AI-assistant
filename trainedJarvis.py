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
import joblib

# Load the trained model and vectorizer
model = joblib.load('intent_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Function to predict intent with fallback
def predict_intent(query):
    query_vec = vectorizer.transform([query])
    intents_proba = model.predict_proba(query_vec)[0]
    max_proba_index = np.argmax(intents_proba)
    max_proba = intents_proba[max_proba_index]
    if max_proba < 0.3:  # Adjust the threshold as needed
        return 'unrecognized'
    else:
        return model.classes_[max_proba_index]


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

        intent = predict_intent(query)

        if intent == 'unrecognized':
            say("I didn't understand that command.")
            continue

        if intent == 'unlock_friday':
            say("Unlocking Friday in 5 seconds ...")
            camera_active = True
            camera_thread = threading.Thread(target=process_camera)
            camera_thread.start()

        elif intent == 'make_google_search':
            search_query = query.replace("make a google search of ", "").replace("search for ", "").replace("google ", "").replace("find ", "").replace("look up ", "")
            google_search(search_query)

        elif intent == 'unlock_jarvis':
            say("Unlocking Jarvis...")
            camera_active = False

        elif intent == 'open_youtube':
            say("Opening YouTube, Sir...")
            webbrowser.open("https://youtube.com")

        elif intent == 'open_google':
            say("Opening Google, Sir...")
            webbrowser.open("https://www.google.com/")

        elif intent == 'open_my_website':
            say("Opening your website, Sir...")
            webbrowser.open("https://vikash2806.github.io/Portfolio-Website/")

        elif intent == 'open_brave_browser':
            say("Opening Brave browser, Sir...")
            os.startfile(r"C:\Users\VIKASH\AppData\Local\BraveSoftware\Brave-Browser\Application\brave")

        elif intent == 'open_telegram':
            say("Opening Telegram, Sir...")
            os.startfile(r"C:\Users\VIKASH\AppData\Roaming\Telegram Desktop\Telegram")

        elif intent == 'open_chat':
            say("Opening ChatGPT, Sir..")
            webbrowser.open("https://chat.openai.com/")

        elif intent == 'open_college_website':
            say("Opening your college website, Sir...")
            webbrowser.open("https://sastra.edu/")

        elif intent == 'who_created_you':
            say("I am AI assistant created by Vikash")

        elif intent == 'who_is_vikash':
            say("He created me!")

        elif intent == 'how_are_you':
            say("I am awesome, what about you")

        elif intent == 'set_volume_maximum':
            set_volume_level("maximum")

        elif intent == 'increase_volume':
            set_volume(0.1)

        elif intent == 'decrease_volume':
            set_volume(-0.1)

        elif intent == 'increase_brightness':
            set_brightness(10)

        elif intent == 'decrease_brightness':
            set_brightness(-10)

        elif intent == 'set_volume_zero':
            set_volume_level("zero")

        elif intent == 'set_brightness_zero':
            set_brightness_level("zero")

        elif intent == 'set_brightness_maximum':
            set_brightness_level("maximum")

        elif intent == 'type_text':
            text_to_type = query.replace("type", "").strip()
            type_text(text_to_type)

        elif intent == 'get_time':
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            say(f"Sir, the time is {current_time}")

        elif intent == 'stop':
            say("Goodbye, Sir")
            break

        elif intent == 'go_to_search':
            say("Going to search bar")
            pyautogui.press('/')

        elif intent == 'delete_all':
            say("Deleting all text")
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')

        elif intent == 'hello':
            say("Hello Sir")

        elif 'paste' in query:
            say("Pasting from clipboard")
            pyautogui.hotkey('ctrl', 'v')

        elif 'undo' in query:
            say("Undoing last action")
            pyautogui.hotkey('ctrl', 'z')

        elif 'copy' in query:
            say("Undoing last action")
            pyautogui.hotkey('ctrl', 'c')

        else:
            print("Command not recognized")
