#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color
CONDA_DEFAULT_ENV=fluxion-env

# Helper function for printing a status message
print_status() {
    echo -e "${YELLOW}[STATUS]${NC} $1"
}

# Print a header
echo -e "${GREEN}=================================="
echo -e "Running Fluxion Tests"
echo -e "==================================${NC}"

# Check for conda environment
if ! command -v conda &> /dev/null; then
    echo -e "${RED}[ERROR] Conda not found! Please install Anaconda or Miniconda.${NC}"
    exit 1
else 
    print_status "Conda is installed"
    print_status "Activating Conda environment: $CONDA_DEFAULT_ENV"
    source activate $CONDA_DEFAULT_ENV
fi

# Check if an environment is activated
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${RED}[ERROR] No Conda environment is active! Activate an environment and try again.${NC}"
    exit 1
else
    print_status "Using Conda environment: $CONDA_DEFAULT_ENV"
fi

# Check for pytest installation
if ! python -c "import pytest" &> /dev/null; then
    echo -e "${RED}[ERROR] Pytest is not installed in the current Conda environment! Install it using 'conda install pytest' or 'pip install pytest'.${NC}"
    exit 1
fi

# Run pytest with coverage
print_status "Running pytest..."
pytest --cov=src --disable-warnings tests/

# Print success message
echo -e "${GREEN}=================================="
echo -e "All tests completed successfully!"
echo -e "==================================${NC}"
