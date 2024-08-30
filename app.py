import os
import warnings
warnings.filterwarnings("ignore")

import json
import random
import pyttsx3
import speech_recognition as sr
from time import sleep

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from promts import prompt_template

from dotenv import load_dotenv
load_dotenv()
from termcolor import colored


class LLMChatbot:
    def __init__(self):
        self.HUGGINGFACEHUB_API_TOKEN = os.getenv("HF_TOKEN")
        self.repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
        self.chain = self.setup_chain()
        self.name = "TeacherX"

    def setup_chain(self):
        prompt = PromptTemplate(input_variables=["history", "input", "name"], template=prompt_template)
        self.memory = ConversationBufferWindowMemory(k=6, input_key="history")
        llm = HuggingFaceEndpoint(repo_id=self.repo_id, max_new_tokens=2000, streaming=True, temperature=0.005, top_k=30, repetition_penalty=1.03, huggingfacehub_api_token=self.HUGGINGFACEHUB_API_TOKEN)
        chain = LLMChain(llm=llm, prompt=prompt, verbose=False, memory=self.memory)
        return chain

    def respond(self, response_text):
        resp = f"{self.name}: " + response_text
        print(colored(resp, "light_yellow"))
        self.engine.say(response_text)
        self.engine.runAndWait()

    def listen_for_command(self):
        r = sr.Recognizer()
        # with sr.Microphone(device_index=2) as source:
        with sr.Microphone() as source:
            print('Listening...')
            r.adjust_for_ambient_noise(source, duration=1) 
            r.pause_threshold = 0.6
            audio = r.listen(source)
            
            try:
                Query = r.recognize_google(audio, language='en-in')
                inp = "You: " + Query
                print(colored(inp, "light_blue"))
            except Exception as e:
                print(e)
                print(colored(f"{self.name}: I couldn't understand, Please say that again", "red"))
                return "None"
            return Query

    def clean_text(self, text):
        if text.endswith("</s>"):
            text = text[:-4]      
        if "* " in text:
            text = text.replace("* ", "- ")        
        text = text.strip()                       
        return text

    def run(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 155)
        self.engine.setProperty('volume', 1.0)

        while True:
            query = self.listen_for_command().lower()
            # query = input("You:").lower()
            
            if query == "none" or query == "":
                continue
            if "exit" in query:
                self.respond("Goodbye!")
                self.memory.clear()
                break
            
            else:
                print(f"{self.name} is typing...")                   
                
                response = self.chain.run(input=query, name=self.name)
                response = self.clean_text(response)                
                self.respond(response)

if __name__ == '__main__':
    print("Ready!")
    chatbot = LLMChatbot()
    chatbot.run()
