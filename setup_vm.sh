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

# Install Python 3.7 (includes PyYAML 3.12)
apt-get update -y
apt install software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt install python3.7 -y
wget https://bootstrap.pypa.io/get-pip.py
python3.7 get-pip.py
update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.7 1
pip install google-cloud-bigquery

# Get codebox
gsutil -m rsync -r gs://mockcustomer-data-bucket/codebox /codebox