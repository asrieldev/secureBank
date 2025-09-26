#!/bin/sh
pip install setuptools
pip install --upgrade pip
pip install --upgrade wheel
pip install --upgrade setuptools
pip install --upgrade pip setuptools wheel
pip install --upgrade --target . -r requirements.txt