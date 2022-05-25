#!/bin/bash

# Google SDK installed by default on GCP VMs. Choose ubuntu 18.04 LTS as base image.
# Make directories
mkdir /codebox
mkdir /user_workarea

# Install unzip
apt-get install unzip

# Install requirements for LightGBM (OSError: libgomp.so.1: cannot open shared object file: No such file or directory)
apt-get update -y
apt-get install -y --no-install-recommends apt-utils
apt-get -y install curl
apt-get install libgomp1

# Install Python pip
apt-get update -y
apt install software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
wget https://bootstrap.pypa.io/get-pip.py
python3.8 get-pip.py
update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.8 1
pip install google-cloud-bigquery

# Get codebox
gsutil -m rsync -r gs://aix-data-stocks-bucket/codebox /codebox