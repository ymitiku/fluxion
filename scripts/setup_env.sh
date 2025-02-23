#!/bin/bash
set -e

is_ubuntu () {
    if [ -f /etc/os-release ]; then
        grep -q "NAME=\"Ubuntu\"" /etc/os-release
        return $?
    else
        return 1
    fi
}

is_macos () {
    if [ "$(uname)" == "Darwin" ]; then
        return 0
    else
        return 1
    fi
}

# Install prerequisites
if is_ubuntu; then
    sudo apt install portaudio19-dev graphviz
elif is_macos; then
    brew install portaudio graphviz
else
    echo "Unsupported OS. Currently only Ubuntu and MacOS are supported."
    exit 1
fi

conda create -n fluxion-env python=3.11 -y
conda init
source activate fluxion-env
which python
which pip
pip install -r requirements.txt --prefer-binary
pip install -r requirements-dev.txt --prefer-binary
pip install -r requirements-extra.txt --prefer-binary