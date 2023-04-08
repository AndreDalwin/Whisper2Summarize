import threading
import customtkinter as ctk
import tkinter as tk
import torch  
import whisper 
import openai
import tqdm
import sys
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("900x700")
        self.title("Whisper 2 Summarize")
        self.resizable(False,False)

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.titlelabel = ctk.CTkLabel(self, text="What would you want to transcribe?", font=ctk.CTkFont(family="Verdana", size=30,weight="bold"))
        self.titlelabel.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.audiobutton = ctk.CTkButton(self, command=self.select_audio, height=50, text="Select Audio File", font=ctk.CTkFont(family="Verdana", size=16,weight="bold"))
        self.audiobutton.grid(row=1, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.modelselect = ctk.CTkComboBox(self, values=["tiny", "base","small","medium","large"], variable= ctk.StringVar(value="Select the Whisper Model"))
        self.modelselect.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.apitext = ctk.CTkEntry(self,placeholder_text="Enter your OpenAI API Key here.")
        self.apitext.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        self.transcribebutton = ctk.CTkButton(self, command=self.transcribe_button, height=50, text="Transcribe with Whisper", font=ctk.CTkFont(family="Verdana", size=16,weight="bold"))
        self.transcribebutton.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        self.summarybutton = ctk.CTkButton(self, command=self.summary_button, height=50, text="Summarize with GPT", font=ctk.CTkFont(family="Verdana", size=16,weight="bold"))
        self.summarybutton.grid(row=3, column=1, padx=20, pady=10, sticky="nsew")

        self.console = ctk.CTkTextbox(self)
        self.console.grid(row=4, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="nsew")

    def write(self,*message, end = "\n", sep = " "):
        text = ""
        for item in message:
            text += "{}".format(item)
            text += sep
        text += end
        self.console.insert("insert", text)

    def select_audio(self):
        self.audio = tk.filedialog.askopenfilename(initialdir='C:/Users/', title="Select Audio",filetypes=(("Open an audio file", "*.mp3"), ("All files", "*.*")))
        self.audiofilename = os.path.basename(self.audio)
        self.audiobutton.configure(text="Selected " + self.audiofilename)

    def transcribe_button(self):
        threading.Thread(target=self.transcribe).start()

    def summary_button(self):
        threading.Thread(target=self.gpt_process).start()
    
    def transcribe(self):
        class _CustomProgressBar(tqdm.tqdm):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._current = self.n  
                
            def update(self, n):
                super().update(n)
                self._current += n
                
                app.write("Audio Transcribe Progress: " + str(round(self._current/self.total*100))+ "%")
                
        devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 
        model = whisper.load_model(self.modelselect.get(), device = devices)
        transcribe_module = sys.modules['whisper.transcribe']
        transcribe_module.tqdm.tqdm = _CustomProgressBar

        self.write("Beginning Transcribing Process...")
        result = model.transcribe(self.audio, verbose=True, fp16=False)
        transcribed = result["text"]
        with open(self.audiofilename+"_Transcript.txt", "w",encoding='utf-8') as text_file:
            text_file.write(transcribed)
            self.transcript = transcribed
            self.write("Saved Transcript to " +self.audiofilename+ "_Transcript.txt")

    def gpt_process(self):
        openai.api_key = self.apitext.get()
        self.write("Processing Transcript with GPT...")
        n=1300
        split = self.transcript.split()
        snippet= [' '.join(split[i:i+n]) for i in range(0,len(split),n)]
        ## For managing token limit
        summary=""
        previous=""
        for i in range(0, len(snippet), 1):
            self.write("Summarizing Transcribed Snippet {} of {}".format(i+1,len(snippet)))
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "\"" + snippet[i] + "\"\n Rewrite the transcript above into notes. Do not summarize and keep every information. For additional context here is the previous rewritten message: \n " + previous }],
                temperature = 0.6,
            )
            previous = gpt_response['choices'][0]['message']['content']
            summary += gpt_response['choices'][0]['message']['content']

        with open(self.audiofilename+"_Summary.txt", "w",encoding='utf-8') as text_file:
            text_file.write(summary)
            self.write("Summarizing Completed.")
            self.write("Saved Summary to "+self.audiofilename+ "_Summary.txt")

    

if __name__ == "__main__":
    app = App()
    app.mainloop()