# EndoPheno Project Repository
Repository for EndoPheno, a rule-based classification system to aid in phenotyping endometriosis cases versus controls for large-scale genomic research. 

Contains a Python project that reads a CSV from an input directory and
outputs a CSV to an output directory, suitable for an analysis workflow on Pennsieve.

Docker commands:
docker-compose build  
docker-compose up EndoPheno

To be added later: web app interface with input page for people to either upload a file of patient data OR fill out a form where they sequentially provide symptoms values. Once they hit a "submit" button, shows progress bar where it says "classifying..." and then changes to a landing page with maybe a simple graph showing the classification output between cases and controls, and then option to download the data with the classifications.

Use this template to create your own GitHub repository by clicking the green
`Use this template` button towards the top-right of this page.

### Setup
Install the following:
- `python3` (latest)
- `pip` (or `pip3`, latest)

Then, run the following
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Running the application
```
python3 app/main.py [--filename]
```

### Testing the application
```
pytest
```
