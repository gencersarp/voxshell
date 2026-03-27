from setuptools import setup, find_packages

setup(
    name="voxshell",
    version="0.1.0",
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
