#!/bin/bash
set -ex

# Update and install dependencies
apt-get update -y
apt-get install -y git curl apt-transport-https ca-certificates software-properties-common

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable and start Docker
systemctl enable docker
systemctl start docker

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Clone the repository
cd /home/ubuntu
git clone https://github.com/Bor-Code/Global-Climate-Socioeconomic-Impact.git
cd Global-Climate-Socioeconomic-Impact

# Create a basic .env file for the build
cp .env.example .env

# Build and start the docker compose stack
docker compose -f docker/docker-compose.yml up --build -d
