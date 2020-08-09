import logging
import requests
import os
import json
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

def download_raw_data(requesturl, filename):
    """Download raw data (mostly json) from the given request URL and save in the ../../data/raw path

    Args:
        requesturl (str): URL of the endpoint from which we will download data
        filename (str): Filename of the downloaded raw data file
    """


    # Logger parameters
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)


    # find .env automatically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())
    RAPIDPRO_TOKEN = os.environ.get("RAPIDPRO_TOKEN")


    # Request Header
    headers = {'Authorization': 'Token ' + RAPIDPRO_TOKEN}

    requestsNumber = 0
    data = {}

    logger.info('Downloading data')

    # Get Contacts from RapifPro
    while True:
        # Build the request URL to get the first page
        if requestsNumber == 0:
            requestsNumber += 1

        # Build the request to get the next page (2nd, 3rd, 4th, etc)
        elif data.get('next') is not None:
            requesturl = data.get('next')
            requestsNumber += 1

        # If there is no next page we stop the loop
        else:
            logger.info('Download complete')
            break

        # Send the request and save the response into a variable
        response = requests.get(requesturl, headers=headers)
        data = json.loads(response.text)

        # For first page, we save the JSON response into a new file
        if requestsNumber <= 1:
            with open(filename, "w+", encoding='utf8') as file:
                json.dump(data.get('results'), file, indent=4, sort_keys=True)

        # For next pages, we append the new response to the old response and overwrite the file
        else:
            with open(filename, "r+", encoding='utf8') as file:
                try:
                    # Open the file
                    file_content = json.load(file)
                    # Append the new response to the old response
                    file_content.extend(data['results'])
                    # Place the cursor on top of file and overwrite with the file_content value
                    file.seek(0)
                    json.dump(file_content, file, indent=4, sort_keys=True)
                    file.truncate()

                # In case of exception, log into the logger
                except json.decoder.JSONDecodeError as e:
                    logMsg = 'Download failed : ' + e
                    logger.error(logMsg)