# SETUP

## Python install
python --version 

## Virtual environment create
python -m venv venv 

## Virtual env activate
venv\Scripts\activate 

## Install relvent libraries
pip install requests networkx boto3 pytest matplotlib 

# SOMETIME AN ERROR IS OCCUR LETS FIX IT

## pip upgrade
python -m pip install --upgrade pip 

## Correct way to install ALL required librarie
pip install requests networkx boto3 pytest matplotlib python-dateutil

## Confirm the installation
pip list 

# RUN # -------------------------------------------------

## Virtual env activate
venv\Scripts\activate 

## Pipeline run
python main.py 


# DATASET VERIFY

## CSV file
output/dataset/metrics_dataset.csv 

## JSON lines file
output/dataset/metrics_dataset.jsonl 

## Raw Prometheus dumps
output/raw/ 

# RUN TESTS

## All tests folder run
pytest -q 
