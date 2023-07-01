import asyncio
import speech_recognition as sr
import json
import threading
import time
from pynput import keyboard
from bot_openai import Bot

## TODO: Make line 55 reference a global variable higher up for easier changing of which button is pressed to activate recording
## Implement token checking. "If Bot.chat_history's token is reaching too high a number, start deleting entries"

## Program flow: 
# Player presses shift, or can change button on line 55, should maybe make it a constant higher up for easier changing?
# After recording, sends to Bot.send_msg to send a message to OpenAI
# After receiving the message back, will save only the most recent message to file (Not needed, need to remove)
# After saving, will read the message out loud. Uses gTTS to create the message and python-vlc to read the message



## Globals

player_two = Bot("player_two.txt", "You are a helpful player two, answering questions about a range of topics in a short and succinct manner")

def player_one_file_write(file, data_to_write):
    file_to_write = file
    data_to_write = json.dumps(data_to_write)
    with open(file_to_write, 'w+') as f:
        f.write(data_to_write)

############################################################################################################
# Area for audio input, starting recording and stopping,
# Transcribe to text, Speech to text
############################################################################################################

def start_recording():
    global player_two
    r = sr.Recognizer()
    transcription = "Not yet"
    with sr.Microphone() as source:
        print("Recording started")
        audio = r.listen(source)  # Capture the audio input

    try:
        transcription = r.recognize_google(audio)  # Perform the speech-to-text transcription
        print("Transcription:", transcription)
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request speech recognition results; {0}".format(e))

    while transcription == "Not yet":
        time.sleep(1)

    # give out the output
    to_send = {}
    to_send['role'] = 'user'
    to_send['content'] = transcription
    print(to_send)
    player_two.send_msg(to_send)


def on_key_release(key):
    if key == keyboard.Key.shift:
        start_recording()


############################################################################################################
# 
############################################################################################################

# Start the listener for the keyboard input.
def start_listener():
    with keyboard.Listener(on_release=on_key_release) as listener:
        listener.join()

async def main():
    print("This is main!")
    listener_thread = threading.Thread(target=start_listener)
    listener_thread.start()

############################################################################################################
# "if __name__ == "__main__""
############################################################################################################

if __name__ == "__main__":
    asyncio.run(main())