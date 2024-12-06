#!/bin/bash
set -e

conda create -n fluxion-env python=3.8 -y
conda init
source activate fluxion-env
which python
which pip
pip install -r requirements.txt --prefer-binary
pip install -r requirements-dev.txt --prefer-binary