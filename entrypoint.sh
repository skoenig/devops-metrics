#!/usr/bin/env bash

git config --global --add safe.directory '*'
git config --global init.defaultBranch main

python pipeline-metrics.py
