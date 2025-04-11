#!/bin/bash

set -e

# SSH setup
if [ -d ~/.ssh ]; then
  chmod 700 ~/.ssh
  chmod 600 ~/.ssh/id_rsa*
  ssh-keyscan -H github.com >> ~/.ssh/known_hosts
  echo "SSH configurations complete; keys copied into devcontainer"
else
  echo "Skipping SSH configuration; no keys found."
fi

# Create target directories for Bazel
mkdir -p /workspaces/option_pricing_grpc_client/proto/finance/options

# Copy generated files from the Dockerfile's temporary location
if [ -d "/tmp/proto" ] && [ "$(ls -A /tmp/proto)" ]; then
  echo "Copying .proto from temporary location..."
  cp -r /tmp/proto/* /workspaces/option_pricing_grpc_client/proto/finance/options/
  echo ".proto files copied successfully"
else
  echo "Error: .proto files not found in /tmp/proto"
  exit 1
fi

# Activate VENV
source /home/vscode/venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Compile PB and GRPC files
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. --proto_path="/workspaces/option_pricing_grpc_client/proto/finance/options/" black_scholes.proto