#!/bin/bash

chmod a+x /files/app.py
cdk diff -a /files/app.py --require-approval never RIV-Simple
cdk deploy -a /files/app.py --require-approval never RIV-Simple
