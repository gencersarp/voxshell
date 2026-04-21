import os
from setuptools import setup, find_packages

def get_version():
    init = os.path.join(os.path.dirname(__file__), "voxshell", "__init__.py")
    with open(init, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="voxshell",
    version=get_version(),
    description="Transform any CLI tool into a voice-enabled agent with local TTS, STT, and smart summarization.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="gencersarp",
    packages=find_packages(),
    install_requires=[
        "click",
        "piper-tts",
        "faster-whisper",
        "pyaudio",
        "numpy",
        "requests",
        "ollama",
        "pydantic"
    ],
    entry_points={
        "console_scripts": [
            "voxshell=voxshell.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
