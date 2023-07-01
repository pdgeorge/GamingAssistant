import time
# import asyncio
# import threading
import os
from queue import Queue
# import llm
from gtts import gTTS
import vlc
import openai
import json

TEXT_DIR = ""
TTS_DIR = "outputs"
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def read_message(msg):
    msgAudio = gTTS(text=msg, lang="en", slow=False)
    filename = "_Msg" + str(hash(msg)) + ".wav"
    normalised_dir = normalise_dir(TTS_DIR)
    
    # Where is the file?
    msg_file_path = os.path.join(normalised_dir, filename)
    msgAudio.save(msg_file_path)

    # Start playing!
    p = vlc.MediaPlayer(msg_file_path)
    p.play()
    time.sleep(0.1)
    duration = p.get_length() / 1000
    print(duration)
    time.sleep(duration)
    #3:02:40

class Bot():
    tts_enabled = True
    model = "gpt-3.5-turbo" # Choose which chat model to go with
    #
    voice_style = "shouting" # This and the one below are for using tts with AzureAI when choosing/changing voice
    voice_name = "en-US-DavisNeural" 
    #
    user_message = "test message"
    bot_file = None
    input_queue = Queue()
    input = None
    chat_message = {}

    def __init__(self, bot_file, system_message):
        self.chat_history = []
        path = normalise_dir(TEXT_DIR)
        self.bot_file = os.path.join(path,bot_file)
        temp_system_message = {}
        temp_system_message["role"] = "system"
        temp_system_message["content"] = system_message
        self.chat_history.append(temp_system_message)
        print("Bot initialised, name: " + self.bot_file) # Might do something with this later. For now this is proving that the bot initialised. (Used to be name. Will use name later)
        print("Sorry, system message: ")
        print(temp_system_message)

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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.chat_history,
            temperature=0.6,
        )

        # data_to_give is the data received from the previous LLM
        # content_to_write is the data to be written to the file, that has been returned by the LLM
        
        bot_response = {}
        bot_response["role"] = response["choices"][0]["message"]["role"]
        bot_response["content"] = response["choices"][0]["message"]["content"]
        self.chat_history.append(bot_response)
        
        print("chat_history for: " + self.bot_file)
        print(self.chat_history)
        read_message(bot_response["content"])

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
    # read_file()