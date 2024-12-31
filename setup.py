from setuptools import setup, find_packages

setup(
    name="fluxion",
    version="0.3.7",
    description="A library for building flow-based agentic workflows.",
    author="Mitiku Yohannes",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "flytekit",
        "openai",
        "chromadb",
        "speechrecognition",
        "pyttsx3",
    ],
)
