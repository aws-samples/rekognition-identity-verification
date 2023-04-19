#!/bin/bash

chmod a+x /files/app.py
cdk diff -a /files/app.py --require-approval never
cdk deploy -a /files/app.py --require-approval never
