import time
import math
# import asyncio
# import threading
import os
from queue import Queue
# import llm
from gtts import gTTS
import vlc
import openai
import json
# locally made
from OBS_Websocket import OBSWebsocketsManager
import sounddevice as sd
import numpy as np

import random

TEXT_DIR = ""
TTS_DIR = "outputs"
openai.api_key = os.getenv("OPENAI_API_KEY")

SCENE_NAME = "ingame"
ELEMENT_NAME = "CultistGary"

SAMPLE_RATE = 44100
CHUNK_SIZE = int(SAMPLE_RATE * 0.1)
DURATION = 1.0

MOVEMENT_MULTIPLIER = 500

def write_to_file(file, data_to_write):
    file_to_write = file
    data_to_write = json.dumps(data_to_write)
    print("Writing to: " + file_to_write)
    with open(file_to_write, "w+") as f:
        f.write(data_to_write)

def normalise_dir(dir):
    current_dir = os.getcwd()
    normalised_dir = os.path.normpath(os.path.join(current_dir, dir))
    return normalised_dir

class Bot():
    tts_enabled = True
    model = "gpt-3.5-turbo" # Choose which chat model to go with
    
    voice_name = "en-US-DavisNeural" 
    
    user_message = "test message"
    bot_file = None
    input_queue = Queue()
    input = None
    chat_message = {}

    def __init__(self, bot_file, system_message):

        self.obs_websocketmanager = OBSWebsocketsManager()

        self.voice_style = "shouting" # This and the one below are for using tts with AzureAI when choosing/changing voice
        self.chat_history = []
        path = normalise_dir(TEXT_DIR)
        self.bot_file = os.path.join(path,bot_file)
        temp_system_message = {}
        temp_system_message["role"] = "system"
        temp_system_message["content"] = system_message
        self.chat_history.append(temp_system_message)
        self.total_tokens = 0

        # Audio normalisation variables
        self.audio_peak_level = 0

        # "I am alive!"
        print("Bot initialised, name: " + self.bot_file) # Might do something with this later. For now this is proving that the bot initialised. (Used to be name. Will use name later)
        print("Sorry, system message: ")
        print(temp_system_message)

    def audio_callback(self, indata, frames, time, status):
        rms = np.sqrt(np.mean(indata**2))

        if rms > self.audio_peak_level:
            self.audio_peak_level = rms

        if time.inputBufferAdcTime >= DURATION:

            loudness = self.audio_peak_level * MOVEMENT_MULTIPLIER
            self.obs_websocketmanager.shake(SCENE_NAME, ELEMENT_NAME, loudness)

            self.audio_peak_level = 0.0

    def read_message(self, msg):
        msgAudio = gTTS(text=msg, lang="en", slow=False)
        filename = "_Msg" + str(hash(msg)) + ".wav"
        normalised_dir = normalise_dir(TTS_DIR)
        
        # Where is the file?
        msg_file_path = os.path.join(normalised_dir, filename)
        msgAudio.save(msg_file_path)

        # Start playing!
        p = vlc.MediaPlayer(msg_file_path)
        p.audio_output_device_get()
        p.play()

        # Make visible
        self.obs_websocketmanager.set_source_visibility(SCENE_NAME, ELEMENT_NAME, True)
        
        while p.get_state() != vlc.State.Ended:

            with sd.InputStream(device=27, channels=2, samplerate=SAMPLE_RATE, callback=self.audio_callback, blocksize=CHUNK_SIZE):
                sd.sleep(int(DURATION * 1000))

            time.sleep(0.1)

        # Return to flat then turn invisible
        self.obs_websocketmanager.shake(SCENE_NAME, ELEMENT_NAME, 0)
        self.obs_websocketmanager.set_source_visibility(SCENE_NAME, ELEMENT_NAME, False)

        time.sleep(0.1)
        
        duration = p.get_length() / 1000
        print("duration: " + str(duration))
        #3:02:40

    def load_from_file(self):
        with open(self.bot_file, 'r') as f:
            data = json.load(f)        
        self.chat_history = data
        print(self.chat_history)

    def send_msg(self, data_to_give):
        print("ready to send message")
        normalised_dir = normalise_dir(TEXT_DIR)
        print("normalised dir: " + normalised_dir)
        file_to_handle = os.path.join(normalised_dir, self.bot_file)
        print("File to handle: " + file_to_handle)

        print(data_to_give)
        self.chat_message = data_to_give

        print("chat message is: ")
        print(data_to_give)
        self.chat_history.append(self.chat_message)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.chat_history,
                temperature=0.6,
            )
        except Exception as e:
            print("An exception occurred:", str(e))
            response = {'role': 'Assistant', 'content': 'Sorry, there was an exception. '+str(e)}

        # data_to_give is the data received from the previous LLM
        # content_to_write is the data to be written to the file, that has been returned by the LLM
        
        bot_response = {}
        bot_response["role"] = response["choices"][0]["message"]["role"]
        bot_response["content"] = response["choices"][0]["message"]["content"]
        self.chat_history.append(bot_response)
        
        print("chat_history for: " + self.bot_file)
        print(self.chat_history)
        self.read_message(bot_response["content"])

        write_to_file(file_to_handle, self.chat_history)

# Experiment if I decide to read the content from the file
# instead of passing content via params
def read_file():
    bot_file = "dm.txt"
    normalised_dir = normalise_dir(TEXT_DIR)
    #
    file_to_read = os.path.join(normalised_dir, bot_file)
    with open(file_to_read, "r") as f:
        data_to_give = f.read()
    data_received = eval(data_to_give)
    print(type(data_received))
    print(data_received)

if __name__ == "__main__":
    to_print = "Hello, this is a test?"
    print(to_print)
    # print(sd.query_devices())
    player_two = Bot("player_two.txt", "You are Gary, a lonely cultist who is attempting to romance eldritch beings beyond your comprehension. Your responses are very short, generally one or two sentences.")
    player_two.read_message("I spend my days studying forbidden texts. aaaaaaeeeeeeeeeeee gagagagagaga waffle waffle waffle waffle cheese steak")
    # read_file()