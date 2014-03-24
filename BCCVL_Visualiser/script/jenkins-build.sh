#!/bin/sh

if [ -z "$WORKSPACE" ]; then
	WORKSPACE=`pwd`
    echo "Guessing WORKSPACE is $WORKSPACE"
fi

VISUALISER_DIR="$WORKSPACE/BCCVL_Visualiser"
BIN_DIR="$VISUALISER_DIR/bin"

PIP="$BIN_DIR/pip"
PYTHON="$BIN_DIR/python"
BUILDOUT="$BIN_DIR/buildout"

echo "Using WORKSPACE $WORKSPACE"
cd $WORKSPACE

echo "Setting up virtualenv in $WORKSPACE"
curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.tar.gz
tar -xvzf virtualenv-1.9.tar.gz
cd virtualenv-1.9
python virtualenv.py -p /usr/bin/python2.7 "$VISUALISER_DIR"
cd "$VISUALISER_DIR"
source bin/activate

echo "Python version:"
"$PYTHON" --version

echo "Building Visualiser"

