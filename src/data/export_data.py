import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import sys
import logging

try:
    import urllib.parse as urlparse
except:
    from urlparse import urlparse


def export_df_to_csv(output_path, dataframe):
    """Exports given dataframe as csv file to the given output path

    Args:
        output_path ([type]): [description]
        dataframe (DataFrame): Dataframe to be exported
    """

    # Logger Configuration
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting export to CSV")

    # Start index at 1
    dataframe.index = np.arange( 1, len(dataframe) + 1)
    
    try:
        dataframe.to_csv(output_path, index_label='index')
    except Exception as e:
        logMsg = "Cannot export to CSV : " + str(e)
        logger.error(logMsg)
    else:
        logger.info("Export to CSV complete")


def export_df_to_db(dataframe, db_table, db_credentials):
    """Exports given dataframe to a Database table
    A new Table will be created if it does not exist
    If the table exists, current records will be updated and new rows will be added

    Args:
        dataframe (DataFrame): The dataframe to export
        db_table (str): The table in which the dataframe will be exported
        db_credentials (dict): The database credentials
    """

    
    # Logger Configuration
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)

    # Stagging table to temporarily store the dataframe.
    # Will be used to facilitate data update to the normal export table
    # This table will be flushed on every new export_df_to_db() call
    stagging_table = db_table + "_stagging"

    # Start index at 1
    dataframe.index = np.arange( 1, len(dataframe) + 1)

    db_password = urlparse.quote_plus(db_credentials.get('DB_PASSWORD'))

    # Build DB URL and connection
    database_url =  'mysql+pymysql://{0}:{1}@{2}/{3}?charset=utf8mb4'.\
        format(db_credentials.get('DB_USER'), db_password, \
            db_credentials.get('DB_HOST'), db_credentials.get('DB_NAME'))


    logger.info("Starting export to database")

    try:
        engine = create_engine(database_url)

        with engine.connect() as dbConnection:
            # Store the dataframe into the stagging table
            try:
                dataframe.to_sql(stagging_table, con=dbConnection, if_exists='replace')

            except Exception as e:
                logMsg = "Cannot export to the {0} table : \n".format(db_table) + str(e)
                logger.error(logMsg)

            # If the dataframe is successfully stored, we update the export table
            else:
                # Update the export table
                try:
                    # The REPLACE statement used here works with MySQL
                    # The REPLACE statement inserts a new row in the table or overwrites existing(conflicting) rows
                    update_query = "REPLACE INTO {0} SELECT * FROM {1}".format(db_table, stagging_table)
                    dbConnection.execute(update_query)

                except Exception as e:
                    # If the table does not exist, we create a new empty table and try to update again
                    if "doesn't exist" in str(e):
                        try:
                            logger.info("Creating {0} table".format(db_table))
                            
                            # Create the empty table
                            dataframe.loc[:-1].to_sql(db_table, con=dbConnection, if_exists='replace')
                            
                            # Add primary key to the table
                            add_pk_query = "ALTER TABLE `{0}` ADD PRIMARY KEY (`index`)".format(db_table)
                            dbConnection.execute(add_pk_query)

                            # Update the table with the stagging data
                            dbConnection.execute(update_query)

                        except Exception as e:
                            logMsg = "Cannot export to the {0} table : \n".format(db_table) + str(e)
                            logger.error(logMsg)
                        
                        else:
                            logger.info("Data successfully exported")

                    else:
                        logMsg = "Cannot export to the {0} table : \n".format(db_table) + str(e)

                # If the export table is successfully updated
                else:
                    logger.info("Data successfully exported")

    except Exception as e:
        logMsg = "Cannot initialize database connexion: " + str(e)
        logger.error(logMsg)
