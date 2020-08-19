from selenium import webdriver
from bs4 import BeautifulSoup
import logging
import os
from dotenv import load_dotenv



logging.basicConfig(filename='main.log', filemode='w',format='%(asctime)s - %(message)s',
                        datefmt="%Y-%m-%d at %H:%M:%S %p", level=logging.DEBUG)


def is_test_mode():
    # TODO: Match the return statement conventions in this test with other tests
    load_dotenv(override=True,dotenv_path='.env')
    test_mode = int(os.getenv("TEST_MODE"))
    if test_mode > 0:
        logging.debug("TEST MODE ENABLED")
    else:
        logging.debug("TEST MODE DISABLED")
    return test_mode



def _path_is_none_type(path):
    """
    Returns True or False
    """
    if type(path).__name__ == 'NoneType':
        logging.debug("[TEST] Path is NoneType:\t\t{} ({})".format('True',type(path).__name__))
        return True
    else:
        logging.warning("[TEST] Path is NoneType: {} - ({})".format('False',type(path).__name__))
        return False




def test_primary_page(driver):
    EXPORT_HEADER = "Data Export - Conversocial"
    if driver.title == EXPORT_HEADER:
        logging.debug("[TEST] Outbound page loaded:\t{}".format("True"))
        return True
    else:
        logging.warning("[TEST] Outbound page loaded:\t{} (see: {})".format("False",driver.title))
        return False


def test_month_selector_visibility(title):
    YEAR = '2020' # TODO: choose now.year
    # after the title is clicked, expected format'YYYY'
    if YEAR == title.text:
        logging.debug("[TEST] Month picker open:\t{}".format("True"))
        return True
    else:
        logging.warning("[TEST] Month picker open:\t{} (see: {})".format("False",title.text))
        return False


def test_month_selected(title,target_month):
    YEAR = '2020' # TODO: choose now.year
    # after month selected, expected title includes target month
    if title.text == target_month + ' ' + YEAR:
        logging.debug("[TEST] Target month selected:\t{}".format('True'))
        return True
    else:
        logging.warning("[TEST] Target month selected:\t{} (see: {})".format('False',title.text))
        return False


def test_contains_bytelike_str(export):
    line = export.readline()
    if type(line).__name__ == 'bytes':
        logging.debug("[TEST] Bytes-like string:\t{}".format('True'))
        return True
    else:
        logging.warning("[TEST] Bytes-like string:\t{} see ({})".format('False',type(line).__name__))
        return False




def test_compare_paths(path,imported_path):
    if path == imported_path:
        logging.debug("[TEST] Import is export path: {}".format('True'))
        return True
    else:
        logging.warning("[TEST] Import is export path: {}".format('False'))
        _path_is_none_type(path)
        return False
