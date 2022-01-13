# Google SDK installed by default on GCP VMs. Choose ubuntu 18.04 LTS as base image.
sudo su
# Make directories
mkdir /root/codebox
mkdir /root/input
mkdir /root/output
mkdir /root/custom_code
mkdir /root/repo
mkdir /root/logs

# Install Python 3.7 (includes PyYAML 3.12)
apt-get update -y
apt install software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt install python3.7 -y
wget https://bootstrap.pypa.io/get-pip.py
python3.7 get-pip.py
update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.7 1


# Get codebox
gsutil -m rsync -r gs://mockcustomer-data-bucket/codebox /root/codebox