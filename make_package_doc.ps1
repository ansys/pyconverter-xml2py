#! /bin/sh

deactivate
cd .\package\
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .[doc]
.\doc\make.bat html
.\doc\_build\html\index.html