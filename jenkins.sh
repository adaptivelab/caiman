#!/bin/sh

if [ -d ".env" ]; then
 echo "**> virtualenv exists"
else
 echo "**> creating virtualenv"
 virtualenv .env
 mkdir -p $HOME/pip-cache
 .env/bin/pip install --download-cache $HOME/pip-cache pytest-cov coverage pep8 pylint clonedigger
 .env/bin/pip install -q fudge==1.0.3 pytest==2.3.4
fi

. .env/bin/activate
.env/bin/python setup.py install
py.test -q --cov caiman --cov-report=xml --cov-report=term-missing --junitxml=nosetests.xml .
coverage xml
pep8 caiman | tee pep8.out
pylint -f parseable -d I0011,R0801 caiman | tee pylint.out
clonedigger --cpd-output caiman
