#!/usr/bin/bash
# Primarily for local development

# Update your Anaconda environment to latest version (optional)
# conda update -n base -c defaults conda

# Build Python virtual environment for Maestro
conda create -n maestro-conductor-service python~=3.9.1 -y

# Activate the environment
conda activate maestro-conductor-service

# Next, dependencies needed to project setup
pip install -r requirements.txt
