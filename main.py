from helper import *
from dotenv import load_dotenv
import logging


load_dotenv(override=True,dotenv_path='.env')
test_mode = is_test_mode()
log = logging.getLogger(__name__)

logging.basicConfig(filename='main.log', filemode='w',format='%(asctime)s - %(message)s',
                        datefmt="%Y-%m-%d at %H:%M:%S %p", level=logging.DEBUG)

def build():
    """
    Logs into Conversocial and exports a zipped Excel file. Once downloaded, the file is
    unzipped and formatted before being imported into BigQuery.
    """

    conversocial = Conversocial()
    conversocial.login()
    conversocial.export()
    conversocial.scrape()
    conversocial.close()
    conversocial.download_and_unzip()
    ExecuteImporter(source=conversocial.target_file)

try:
    file = build()
except Exception:
    log.exception("Fatal error in main loop")
