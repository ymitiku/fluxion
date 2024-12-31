#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e
CONDA_DEFAULT_ENV=fluxion-env
source activate $CONDA_DEFAULT_ENV

# Define paths
DOCS_DIR="docs"
DOCS_SOURCE_DIR="${DOCS_DIR}/source"
BUILD_DIR="${DOCS_DIR}/_build"

# Check if Sphinx is installed
if ! command -v sphinx-build &> /dev/null
then
    echo "Sphinx is not installed. Installing Sphinx..."
    python -m pip install sphinx sphinx-rtd-theme
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf "${BUILD_DIR}"

# Build the documentation
echo "Building documentation..."
sphinx-build -b html "${DOCS_SOURCE_DIR}" "${BUILD_DIR}"

# Notify success
echo "Documentation successfully built!"
echo "You can view it by opening ${BUILD_DIR}/index.html in a browser."
