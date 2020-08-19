# ConversocialExporter
Automated selenium browser driver that authenticates and exports data from Conversocial, downloads, unzips and imports to BQ.

## Installation

1. $ `git clone https://github.com/zmacks/ConversocialExporter.git`
2. $ `virtualenv venv`
3. $ `pip install -r requirements.txt`
4. Create service account for GCP and [download credentials]("https://cloud.google.com/iam/docs/creating-managing-service-accounts") (ex: .json file)
5. Download Chromedriver for Selenium [here](https://chromedriver.storage.googleapis.com/index.html) Note: Save path to Chromedriver
6. `cd ConversocialExporter`
6. `touch .env` & add these environment variables 
```
USERNAME =
PASSWORD =
TEST_MODE = 1
GOOGLE_APPLICATION_CREDENTIALS=
BQ_DATASET =
BQ_TABLE =
CHROMEDRIVER_LOCATION =
```

  - Note: `USERNAME` is Conversocial username
  - Note: `PASSWORD` is Conversocial password
  - Note: `GOOGLE_APPLICATION_CREDENTIALS` is path for GCP credential file
  - Note: CHROMEDRIVER_LOCATION` is path for Chromedriver downloaded in step 5

## Usage
1. $ `cd ConversocialExporter`
2. $ `python main.py`
