# Whisper2Summarize

Whisper2Summarize is an application that uses Whisper for audio processing and GPT for summarization. It generates summaries of audio transcripts quickly and accurately, making it ideal for a variety of use cases such as note-taking, research, and content creation.

## Setup

I used Python 3.10.11 to build this application, but OpenAI's Whisper and GPT is expected to be compatible with Python 3.8-3.10. The code depends on a few Python packages, notably OpenAI's Whisper and GPT, their dependencies, a torch verison that supports CUDA, and rust.

`**(If you do not have an NVIDIA GPU, skip this step.)**` You want to install a different version of torch that supports CUDA.

```
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116
```

You also need to install OpenAI's Whisper and GPT.

```
pip install -U openai-whisper openai
```

Additionally, it also requires the command-line tool `ffmpeg` to be installed on your system, which is available from most package managers:

```
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```

**NOTE:** To install Whisper, might need `rust` install as well in case you don't have pre-built wheel for your platform.

```
pip install setuptools-rust
```

Lastly, you need to clone this repository.

```
git clone https://github.com/AndreDalwin/Whisper2Summarize.git
cd Whisper2Summarize
```

## Getting Started

Ensure you create a `.env` file in the directory containing your OpenAI API Key, you will need it to run this program.

### Command Line Usage

The followinc command will transcribe audio files, using Whisper's `medium` model:

```shell
python whisper2summarize.py audio.mp3 --model medium
```

The default setting (which selects Whisper's `base` model) works well with CPU for transcribing English. I recommend using other models when trying out multilingual audio snippets.

Here is the full list of available Whisper models:

```
tiny, small, base, medium, large-v2
```

To see the requirements to run these different models, check out [OpenAI's Whisper Github](https://github.com/openai/whisper#available-models-and-languages) to learn more.
