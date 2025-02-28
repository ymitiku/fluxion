from setuptools import setup, find_packages

setup(
    name="fluxion-ai-python",
    version="1.1.1",
    author="Mitiku Yohannes",
    author_email="se.mitiku.yohannes@gmail.com",
    description="A framework for orchestrating flow-based agentic workflows using LLMs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ymitiku/fluxion",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "chromadb==0.3.25",
        "docstring_parser==0.16",
        "faiss-cpu==1.8.0",
        "flytekit==1.13.15",
        "Pillow==10.4.0",
        "speechrecognition==3.8.1",
        "gtts",
        "playsound",
        "numpy==1.26.0",
        "graphviz==0.20.3"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    include_package_data=True,
    license="Apache License 2.0"
)
