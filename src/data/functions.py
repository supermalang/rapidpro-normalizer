def search_dict_from_list(key, dictionary_list):
    """Search and return the first dictionary item that has the given key

    Args:
        key (string): The key of the dictionary
        dictionary_list (list): The list of dictionary we are searching from

    Returns:
        dict: The first dictionary item that is found
    """

    return next((item.get(key) for item in dictionary_list if item.get(key) is not None), None)
