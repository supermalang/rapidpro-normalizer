import pandas as pd
import logging


def serialize_data(raw_data, fields):
    """Serializes given raw data to pandas dataframe in order to 
        facilitate the export to CSV or Database
        We will keep only fields that are needed

    Args:
        raw_data (JsonReader): Data to serialize
        fields (list): Fields and sub-fields to keep and serialize through the iteration of the serialization

    Returns:
        DataFrame: Serialized data returned as a DataFrame
    """


    # Set up the loging configuration
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # Make sure raw_data is a DataFrame
    raw_data = pd.DataFrame(raw_data)

    # Dataframe to be returned
    returndf = pd.DataFrame()
    
    for field in fields:
        # For top level fields, we do not need to serialize, we just instert as a column
        # in the final dataframe
        if isinstance(field, str):
            returndf[field] = raw_data[field]

        # For sub fields, we normalize them and join them with top level fields
        elif isinstance(field, (dict, list, tuple)):
            # Key of the fied that have children items
            key = next(iter(field))
            
            # Sub-Fields
            subfields = field[key]

            # First we serialize the subfields
            normalized_sub_df = serialize_data(pd.json_normalize(raw_data[key]), subfields)
            
            # Then we append them to top level fields
            returndf = returndf.join(normalized_sub_df)
    
    return returndf
