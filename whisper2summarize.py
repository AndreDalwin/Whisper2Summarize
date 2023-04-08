import os
import torch  
import whisper 
import openai
import tqdm
import sys, argparse
from dotenv import load_dotenv


def transcribe(audio,model_type):
    class _CustomProgressBar(tqdm.tqdm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._current = self.n  
            
        def update(self, n):
            super().update(n)
            self._current += n
            
            print("Audio Transcribe Progress: " + str(round(self._current/self.total*100))+ "%")
            
    devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 
    model = whisper.load_model(model_type, device = devices)
    transcribe_module = sys.modules['whisper.transcribe']
    transcribe_module.tqdm.tqdm = _CustomProgressBar

    print("Beginning Transcribing Process...")
    result = model.transcribe(audio, verbose=None, fp16=False)
    transcribed = result["text"]
    with open("Transcript.txt", "w",encoding='utf-8') as text_file:
        text_file.write(transcribed)
        print("Saved Transcript to Transcript.txt")
    return transcribed

def gpt_process(transcript):
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_KEY')
    print("Processing Transcript with GPT...")
    n=1300
    split = transcript.split()
    snippet= [' '.join(split[i:i+n]) for i in range(0,len(split),n)]
    ## For managing token limit
    summary=""
    previous=""
    for i in range(0, len(snippet), 1):
        print("Summarizing Transcribed Snippet {} of {}".format(i+1,len(snippet)))
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "\"" + snippet[i] + "\"\n Rewrite the transcript above into notes. Do not summarize and keep every information. For additional context here is the previous rewritten message: \n " + previous }],
            temperature = 0.6,
        )
        previous = gpt_response['choices'][0]['message']['content']
        summary += gpt_response['choices'][0]['message']['content']

    with open("Summary.txt", "w",encoding='utf-8') as text_file:
        text_file.write(summary)
        print("Summarizing Completed.")
        print("Saved Summary to Summary.txt")



parser = argparse.ArgumentParser(description='Whisper2Summarize - a tool for summarizing audio files')
parser.add_argument('audio', type=str, help='the audio file to summarize')
parser.add_argument('--model', type=str, default='base', help='the summarization model to use (default: base)')

# parse the arguments
args = parser.parse_args()
audio = args.audio
model_type = args.model
text = transcribe(audio,model_type)
gpt_process(text)