# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
import google.auth
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import os
import zipfile
import io
import datetime
from time import time, sleep
from dotenv import load_dotenv
from tests import *
import pandas as pd
import numpy as np
import pandas_gbq
import logging


logging.basicConfig(filename='main.log', filemode='w',format='%(asctime)s - %(message)s',
                        datefmt="%Y-%m-%d at %H:%M:%S %p", level=logging.DEBUG)



class Conversocial():

    def __init__(self):
        self.url = 'https://app.conversocial.com/login/?next=/page/all/export/'
        self.links = []
        self.driver = webdriver.Chrome(os.getenv("CHROMEDRIVER_LOCATION"))
        self.target_file = os.path.join(os.getcwd(), 'downloads/')


    def login(self):
        logging.info("============LOGGINGIN==============")
        load_dotenv(override=True, dotenv_path='.env')
        # Login and go to Export page
        USERNAME = os.getenv("USERNAME")
        logging.debug(f"Conversocial username val: {USERNAME}")
        PASSWORD = os.getenv("PASSWORD")
        # SessionNotCreatedException fix: download updated driver https://chromedriver.storage.googleapis.com/index.html
        logging.debug("Open Chrome driver and log in")
        # TODO: Consider moving this chromedriver file to the project folder
        # TODO: Download latest chromedriver if this exception is thrown SessionNotCreatedException
        #driver = webdriver.Chrome('/Users/user/Developer/resource/chromedriver')
        self.driver.get(self.url)
        trusty_sleep(3)
        self.driver.find_element_by_name('username').send_keys(USERNAME)
        self.driver.find_element_by_name('password').send_keys(PASSWORD)
        self.driver.find_element_by_class_name('button').click()
        #return driver


    def export(self):
        target_day, target_month = GetTargetDate()
        self.driver = OpenDateFromPicker(self.driver)
        self.driver = OpenMonthSelector(self.driver)
        cal, title = FindPageElements(self.driver)
        if int(target_day) < 28:
            _visible = test_month_selector_visibility(title)
            if _visible:
                self.driver = ChooseTargetMonth(self.driver, target_month)
                _selected = test_month_selected(title, target_month)
                if _selected:
                    self.driver = ChooseTargetDay(self.driver, cal, target_day)
                    ClickExportButton(self.driver)
                    #return driver
        else:
            logging.warning("Unable to run exporter. Retry later.")
            logging.info("Calendar Date Picker automation can be unstable on the 29th, 30th, or 31st.")
            return None


    def scrape(self):
        waiting = True
        self.links = ScrapeLinks(self.driver)
        latest_url = self.links[0]
        while waiting:
            trusty_sleep(30)  # wait for 30 seconds
            if latest_url == self.links[0]:
                logging.info("============REFRESHING===============")
                self.driver.refresh()
                trusty_sleep(5)  # help page load during refresh
                logging.info("============RESCRAPING===============")
                self.links = ScrapeLinks(self.driver)
            else:
                waiting = False


    def close(self):
        self.driver.close()


    def download_and_unzip(self):
        # Download and save zipped Excel file from Conversocial's AWS bucket
        try:
            r = DowndloadZipFile(self.links)
        except Exception:
            logging.exception("Fatal error downloading zipped file")

        # Unzip Excel sheet and save target file path
        try:
            self.target_file = UnzipFile(r)
        except Exception:
            logging.exception("Fatal error unzipping file")

        if type(self.target_file).__name__ == 'NoneType':
            logging.warning("No file accessible for import")
        else:
            logging.debug(f"Executing import on file: {self.target_file}")

# helpers for Conversocial class


def GetTargetDate():
    # determine target date_from month and day
    month_ref = { 1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
                 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    d = datetime.date.today() - datetime.timedelta(days=1) # yesterday
    target_day = d.day
    target_month = month_ref[d.month]
    return target_day,target_month



def OpenDateFromPicker(driver):
    logging.info("============NAVIGATING==============")
    logging.debug("Open 'Date From' date picker")
    form = driver.find_element_by_xpath("/html/body//form")
    logging.debug("Found:\t\t\tpage form")
    logging.debug("Clicking:\t\tcalendar element")
    form.find_element_by_class_name('date-css3').click() # open the Date From date picker
    trusty_sleep(3)
    return driver



def FindPageElements(driver):
    cal = driver.find_element_by_class_name('calendar-datepicker')
    title = cal.find_element_by_class_name('title')
    return cal, title



def OpenMonthSelector(driver):
    cal, title = FindPageElements(driver)
    title.click()  # opens month selector
    trusty_sleep(3)
    return driver



def ChooseTargetMonth(driver, target_month):
    logging.info("============SELECTINGMONTH===============")
    logging.debug("Locating target month")
    # Selects the target month and day from the date picker
    months = driver.find_elements_by_class_name('month')
    for month in months:
        if month.text == target_month:
            logging.debug('Found:\t\t\t{}'.format(month.text))
            trusty_sleep(3)
            logging.debug('Clicking:\t\t{}'.format(month.text))
#            driver.execute_script("arguments[0].click();", month) # alt click option
            month.click()
    return driver



def ChooseTargetDay(driver,cal,target_day):
    logging.info("============SELECTINGDAY===============")
    logging.debug("Locating target day")
    # Isolate column's in date picker
    days = cal.find_elements_by_tag_name('td')
    # Loops through columns, act on desired date
    for day in days:
        if day.text == str(target_day):
            logging.debug('Found:\t\t\t{}'.format(day.text))
            trusty_sleep(3)
            logging.debug('Clicking:\t\t{}'.format(day.text))
            day.click()
    return driver



def ClickExportButton(driver):
    logging.info("============EXPORTING===============")
    trusty_sleep(2)
    driver.find_element_by_name('export').click()
    trusty_sleep(2)



def DowndloadZipFile(links):
    if type(links).__name__ != 'NoneType':
        logging.info("============DOWNLOADING===============")
        zip_file_url = links[0] # example download url below
        # 'https://s3.amazonaws.com/conversocial/reports/9abbaa84-e0a2-43ab-b267-c5c8e659d49e/mailchimp-messages-created-may-26-2020---may-27-2020.zip'
        logging.debug("Make request with:\n{}".format(zip_file_url))
        r = requests.get(zip_file_url)
        logging.debug("Download success:\t{}".format(r.ok)) # prints status of request
        return r
    else:
        logging.warning("No file present to download")
        return None



def UnzipFile(r):
    if type(r).__name__ != 'NoneType':
        logging.info("============UNZIPPING===============")
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.printdir() # print contents of zip file before changing name
        name = z.namelist()[0] # inbound.xlsx
        info = z.getinfo(name)
        # add unique naming strategy here
        cwd = os.getcwd()
        now = str(datetime.datetime.today().strftime("%Y-%m-%d at %H.%M.%S %p"))
        info.filename = 'Export {}.xlsx'.format(now)
        target_dest = os.path.join(cwd, 'downloads/')
        target_file = os.path.join(target_dest, info.filename)
        logging.debug("Open and save file:\t{}".format(name))
        with z.open(info) as export:
            _bytes_like = test_contains_bytelike_str(export)
            z.extract(info,path=target_dest)

        trusty_sleep(4)
        return target_file
    else:
        logging.warning("No file present to unzip")
        return None



def ScrapeLinks(driver):
    # TODO: Handle driver exceptions by catching with automated login
    logging.info("============SCRAPING===============")
    # gets all the download url's
    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'html.parser')
    html_links = soup.select('.inset')
    all_links = [iso['href'] for iso in html_links]
    return all_links



# general helpers


def trusty_sleep(n):
    logging.debug("sleeping...")
    start = time()
    while (time() - start < n):
        sleep(n - (time() - start))
    # https://realpython.com/python-sleep/
    # Note: In Python 3.5, the core developers changed the behavior
    # of time.sleep() slightly. The new Python sleep() system call will
    # last at least the number of seconds you’ve specified, even if the
    # sleep is interrupted by a signal. This does not apply if the
    # signal itself raises an exception, however.



#####
# helpers for Importer
#####


def DropCols(df,include=None):
    """Gracefully drops only columns listed in cols"""
    cols = ['Unnamed: 19','Unnamed: 20','Unnamed: 21','Unnamed: 22','Unnamed: 23','Unnamed: 24',
        'Unnamed: 25','Unnamed: 26']
    cols = cols + include
    delete_cols = []
    for col in cols:
        if col in df.columns:
            delete_cols.append(col)
    df = df.drop(delete_cols, axis=1)
    return df

def TransformCols(df,drop):
    df = DropCols(df,include=drop)
    df['Sentiment'] = df['Sentiment'].fillna(0).astype(np.int64)
    df['Followers'] = df['Followers'].fillna(0).astype(np.int64)
    return df

def RenameCols(df):
    # match the column names in bq
    cols = df.columns.values
    new_cols = []
    for col in list(cols):
        col = col.replace(" ", "_")
        new_cols.append(col)
    df.columns = new_cols
    return df



# def ImplicitAuth():
#     #GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
#     #load_dotenv(override=True,dotenv_path='.env')
#     credentials, project = google.auth.default()
#     return credentials, project


def get_staging_dataset_name(dataset_name):
    return f"{dataset_name}_staging"



def get_dataset_name():
    load_dotenv(override=True, dotenv_path='.env')
    BQ_DATASET = os.getenv("BQ_DATASET")
    BQ_TABLE = os.getenv("BQ_TABLE")
    return f"{BQ_DATASET}.{BQ_TABLE}"



def ExecuteImporter(source):
    try:
        if type(source).__name__ != 'NoneType':
            # TODO: Turn this into a Class
            logging.info("============LOADING===============")
            credentials, PROJECT_ID = google.auth.default()
            pandas_gbq.context.credentials = credentials

            CONVERSOCIAL_DATASET_ID = get_dataset_name()
            # CONVERSOCIAL_STAGING_DATASET_ID = get_staging_dataset_name(CONVERSOCIAL_DATASET_ID)

            if_exists = 'append'
            file = open(source,'rb')
            drop = [] # if we want to drop more columns from export, we can add them here
            opts = {'project':PROJECT_ID, 'destination':CONVERSOCIAL_DATASET_ID, 'if_exists':if_exists}

            if file:
                logging.debug("Making DataFrame...")
                df = pd.read_excel(file.name,dtype={'From ID':str})
                # TODO: Consider GreatExpectations for data validation
                logging.debug("Formatting data for import...")
                df = TransformCols(df,drop)
                df = RenameCols(df)
                logging.debug("Importing {}...".format(str(file.name)))
                logging.debug(f"BigQuery Dataset ID destination: {opts['destination']}")
                # More on pandas_gbq.to_gbq - https://pandas-gbq.readthedocs.io/en/latest/api.html#pandas_gbq.to_gbq
                pandas_gbq.to_gbq(df, opts['destination'], project_id=opts['project'], if_exists=opts['if_exists'])
                logging.debug(f"Import to {PROJECT_ID}.{CONVERSOCIAL_DATASET_ID} complete!")
                return source

        else:
            logging.warning("Import skipped. No file found.")
            return None

    except Exception:
        logging.exception("Fatal error during import")
