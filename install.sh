#!/bin/sh

root=`eval echo ~/.local/share/mangrove/venv`

env python3.12 -m venv ${root}
"${root}/bin/pip" install git+https://github.com/nia11720/mangrove@main
