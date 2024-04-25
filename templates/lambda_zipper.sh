#!/bin/bash

# Validate script usage
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <functionName>"
    exit 1
fi

# Configuration
function_name=$1
base_dir=$(cd "$(dirname "$0")" && pwd)  # Robust way to get the absolute path
timestamp=$(date +"%Y%m%d-%H%M%S")
artifacts_path="$base_dir/../artifacts"
venv_path="$artifacts_path/venv"
zip_file="${function_name}${timestamp}.zip"
function_dir="$base_dir/../functions/$function_name"
zip_path="$artifacts_path/$zip_file"

# Ensure the artifacts directory exists
mkdir -p "$artifacts_path"

echo "Creating virtual environment in $venv_path..."
python3 -m venv "$venv_path"
source "$venv_path/bin/activate"

echo "Installing dependencies from $function_dir/requirements.txt..."
pip install -r "$function_dir/requirements.txt"

echo "Zipping site-packages..."
cd "$venv_path/lib/python3.9/site-packages" || exit 1
zip -r9 "$zip_path" . 

echo "Adding function file to the zip..."
cd $function_dir
zip -g "$zip_path" "lambda_function.py"

echo "Cleaning up virtual environment..."
deactivate
rm -rf "$venv_path"

echo "Zip file created at $zip_path"
