import json
import yaml
import os
from pathlib import Path
import click
import logging
from dotenv import find_dotenv, load_dotenv
import download_data as dw
import transform_data as trn
import export_data as exp
import functions as fnc



@click.command()
@click.option('--requesttype', prompt='Give the type of request', type=str)
@click.option('--datasetname', prompt='Give a name for thedataset', type=str)
def main(requesttype=None, datasetname=None):
    """ Runs data processing scripts to turn raw data from (../../data/raw) into
        cleaned data ready to be analyzed (saved in ../../data/processed).
    """


    requestUrl =  fnc.search_dict_from_list(requesttype, rapidpro_requests_types)
    if(requestUrl is None):
        logger.error("Error reading the config file: Type of request is not defined")
        return

    processedfile = os.path.join(project_dir, file_export_path, datasetname + "." + file_export_format)
    rawfile = os.path.join(project_dir, 'data', 'raw', datasetname + ".json")
    
    # Download the raw file
    dw.download_raw_data(requestUrl, rawfile)

    # Open the downloaded raw file
    try:
        with open(rawfile) as file:
            # Load the content of the file
            try:
                data_content = json.load(file)
            except Exception as e:
                logMsg = "Can't load JSON file : " + str(e)
                logger.error(logMsg)

            # Serialized Dataframe    
            serialized_df = trn.serialize_data(data_content, fields)
            
            # Normalize the 'urns' column for RapidPro Data
            if 'urns' in serialized_df.columns:
                for row in serialized_df.itertuples():
                    serialized_df.loc[row.Index, 'urns'] = str(row.urns).strip('[]') if len(row.urns) > 0 else None         
            
            # Export to file
            if file_export_is_enabled:
                exp.export_df_to_csv(processedfile, serialized_df)

            # Export to database
            if db_export_is_enabled:
                try:
                    db_credentials = {'DB_HOST': os.environ.get('DB_HOST'), 'DB_NAME': os.environ.get('DB_NAME'), 'DB_USER': os.environ.get('DB_USER'), 'DB_PASSWORD': os.environ.get('DB_PASSWORD')}
                except Exception as e:
                    logMsg = "Error reading the virtual environment variables : " + str(e)
                    logger.error()
                else:
                    exp.export_df_to_db(serialized_df, datasetname, db_credentials)

    except Exception as e:
        logMsg = "Cannot open file at:" + rawfile + "\n" + str(e)
        logger.error(logMsg)



if __name__ == "__main__":
    # Logger Configuration
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)

    # Root directory of the project
    project_dir = Path(__file__).resolve().parents[2]

    # Load up the .env entries as environment variables
    load_dotenv(os.path.join(project_dir, '.env'))

    # Load the config file settings
    try:                           
        with open(os.path.join(project_dir, 'config.yml'), 'r') as configfile:
            config = yaml.safe_load(configfile)
            fields = config['contact_fields']

            # Rapid Pro API Requests Types
            rapidpro_api_settings = config['rapidpro_api_settings']
            rapidpro_requests_types = fnc.search_dict_from_list("request_types", rapidpro_api_settings)
            
            # Load file export settings            
            data_export_settings = config['data_export_settings']
            file_export_settings = fnc.search_dict_from_list("export_to_file", data_export_settings)
            file_export_is_enabled = fnc.search_dict_from_list("export", file_export_settings)
            if file_export_is_enabled:
                file_export_path = fnc.search_dict_from_list("path", file_export_settings)
                file_export_format = fnc.search_dict_from_list("fileType", file_export_settings)

            # Load the DB export setting
            # For now only MySQL DB is supported
            # The DB credentials are defined in the .env file
            db_export_is_enabled = fnc.search_dict_from_list("export_to_database", data_export_settings)
            
    # In case there is an error in loading the settings an exception is raised
    except Exception as e:
        logger.info('Error reading the config file: ' + str(e))


    else:
        main()