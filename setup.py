from setuptools import setup, find_packages

setup(
    name="mlmodelselect",
    version="0.1.0",
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
            "mlmodelselect=mlmodelselect.cli:main",
        ],
    },
)
