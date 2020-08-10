import pandas as pd
import logging


def serialize_data(raw_data, fields, prefix=None):
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
        # For top level fields, we do not need to normalize, we just insert as a column
        # in the final dataframe
        if isinstance(field, str):
            field = str(prefix) + "_" + field if prefix is not None else field
            returndf[field] = raw_data[field]

        # For sub-fields, we normalize them and join them with top level fields
        elif isinstance(field, (dict, list, tuple)):
            # Key of the field that have children items
            key = next(iter(field))
            
            # Normalized sub-fieds
            subfields = []
            
            # Sub-fields
            _subfields = field[key]

            # Let's make a list of normalized sub-fields
            for subfield in _subfields:
                if isinstance(subfield, (dict, list, tuple)):
                    subfields.extend(make_normalizable_column_names(value=subfield))
                else:
                    subfields.append(subfield)
            
            # First we serialize the subfields
            normalized_sub_df = serialize_data(pd.json_normalize(raw_data[key]), subfields)
            
            # Then we append them to top level fields
            returndf = returndf.join(normalized_sub_df, how='right', rsuffix=key)
    
    return returndf



def make_normalizable_column_names(key=None, value=None):
    """Generates columns names that can be used in a dataframe normalized with json_normalize()

    Args:
        key (str, optional): top level field. Defaults to None.
        value (dict, optional): sub-fields to be normalized. Defaults to None.

    Returns:
        list: List of normalized column names
    """


    # normalized column names
    column_names = []


    if isinstance(value, str):
        column_names.append( key + "." + value ) if key is not None else column_names.append(value)

    elif isinstance(value, (dict, list, tuple)):
        # Local dictionary top sub-field
        _key = next(iter(value))

        for _value in value.get(_key):
            if key is not None:
                _column_names = make_normalizable_column_names(key + "." + _key, _value)
            else:
                _column_names = make_normalizable_column_names(_key, _value)

            column_names.extend(_column_names)

    return column_names
