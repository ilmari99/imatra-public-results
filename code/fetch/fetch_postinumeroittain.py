from time import sleep
import urllib.parse
import urllib.request
import pandas as pd
import json
import requests
import TilkeskQuery as tq
import os
__start_directory = os.getcwd()

def new_format_labels(response_json):
    """For a newer format where the labels are in the "columns" key"""
    labels = {}
    # The labels for the data are in the resp_json["columns"]["code"] keys
    # Skip the postal code label
    for header in response_json["columns"][1:]:
        labels[header["code"].strip().lower()] = header["text"] + \
                                    header["comment"].strip().replace(
                                        "\n", " ")  # Create dictionary for labels
    return labels

def old_format_labels(response_json):
    """For an older format where the labels are in the "comments" key"""
    labels = {}
    for header in response_json["comments"]:
        labels[header["value"].strip().lower()] = header["comment"].strip().replace(
            "\n", " ")  # Create dictionary for labels
    return labels

def modify_df(df, file_prefix, year):
    if "paatoiminta" in file_prefix:
        try:
            df.drop(["pt_tyovy","pt_tyovu"], axis=1, inplace=True)
        except KeyError:
            pass
    elif "taloudet" in file_prefix:
        try:
            df.drop(["te_yks","te_yhlap"],axis=1, inplace=True)
        except KeyError:
            pass
    elif "rakennukset" in file_prefix:
        try:
            df.drop(["ra_muu_as"],axis=1, inplace=True)
        except KeyError:
            pass
    elif "ikarakenne" in file_prefix and int(year)>=2018:
        lb = list(df.columns)
        lb[1] = "he_naiset"
        lb[2] = "he_miehet"
        df = df.reindex(columns=lb)
    return df



def read_to_df(url, query, year="", file_prefix="data",ret_descriptions=False):
    """Does a POST request to the Paavo API URL, with the specified query and returns the results in a dataframe.

    Args:
        url (string): The URL to the Paavo API.
        query (dict): The POST request query.
        year (str, optional): If specified, adds the year to end of the dataframe name. Defaults to ().
        file_prefix (str, optional): How to name the dataframe. Defaults to "data".

    Returns:
        df (dataframe): The result of the POST request. The dataframe is named after the file_prefix and year.
        The dataframe has the postal codes and years as rows and the data as columns with short code words as column names.
        
        description (dict): If ret_descriptions is True, returns a dictionary with the data descriptions of the short ids.
    """
    while 1:
        resp = requests.post(url, data=json.dumps(query))       # Response object from website
        resp_json = resp.json()                                 # Response object as JSON
        # If response is not ready, wait and try again
        if "error" not in resp_json:
            break
        print("error in response:", resp_json["error"],"\nWaiting for 5 seconds...")
        sleep(5)
    
    # Get the labels for the data
    labels = old_format_labels(resp_json)
    if not labels:                                              # If data is in new format, then labels are empty but no error is raised in 'old_format_labels()'
        labels = new_format_labels(resp_json)
    f = resp_json["data"]
    data = {}
    # Extract the data from the response
    for d in f:
        key = "".join([d["key"][0], " (", year, ")"])
        if key in data.keys():
            data[key].append(float(d["values"][0]))         # If the key already exists, append the value to the list
            continue
        # If in newer format 2018 ->
        if len(d["values"]) > 1:                            # If key doesn't exist, create a new list
            data[key] = [float(_) for _ in d["values"]]
        # Older format
        else:
            data[key] = [float(d["values"][0])]
    df = pd.DataFrame(data).T
    df.columns = list(labels.keys())                            # Make the short codes the column names
    df.index.name = "Postinumero"
    df = modify_df(df, file_prefix, year)                       # Check if some data needs to be modified or removed
    df.Name = file_prefix + year
    if ret_descriptions:
        return (df, labels)
    return df


def urls_to_dfs(single_file_prefix, urls, query):
    """ Use this to read multiple urls with the same query and file prefix.

    Args:
        single_file_prefix (string): This is needed to name the dataframes and later files
        urls (list of tuples): A list of tuples with url ad year. As in [(year, url), (year, url), ...]
        query (dict): a query dictionary to be used in the POST request

    Raises:
        ValueError: Labels don't match between the dataframes.
        ValueError: Sizes of the dataframes don't match.

    Returns:
        dfs (list of Dataframes): A list where there is a dataframe for each year.
        description (dict): A dictionary with the data descriptions of the short ids.
    """    
    dfs = []
    label_check = []
    size_check = []
    data_description = {}
    for url in urls:
        df,data_description = read_to_df(url[1], query, year=url[0],
                    file_prefix=single_file_prefix,ret_descriptions=True)
        if not label_check:
            label_check = list(df.columns)
            size_check = df.size
        labels = list(df.columns)
        if label_check != labels:
            print(label_check,"\n",labels)
            raise ValueError(f"Labels in dataframe {single_file_prefix} do not match the labels of the previous dataframe!")
        if size_check != df.size:
            raise ValueError(f"Dataframe {single_file_prefix} size does not match the size of the previous dataframe!")
        dfs.append(df)
    return dfs, data_description

def dfs_to_file(dfs, file_names, sep="\t",make_dir="name",overwrite=True):
    if make_dir != "name":
        change_to_dir(make_dir,overwrite=overwrite)
    for df, fname in zip(dfs, file_names):
        with open(fname, "wb") as f:  # Excel requires binary writing
            ftype = fname.split(".")[-1]
            if ftype == "csv":
                df.to_csv(f, sep=sep)
            elif ftype == "xlsx":
                df.to_excel(f)
    global __start_directory
    os.chdir(__start_directory)
    return

# TODO: make this a decorator
def change_to_dir(name, overwrite=True):
    global __start_directory
    dir_exists = name in os.listdir(__start_directory)
    if not overwrite and dir_exists:
        raise ValueError("Directory already exists!")
    if not dir_exists:
        os.mkdir(name)
    os.chdir(name)
    print(os.getcwd())
    return 1


queries = tq.queries
#queries = [tq.ikarakenneQuery]# te_yks, te_yhlap
for query in queries:
    single_file_prefix = query.file_prefix
    combined_file_prefix = query.combined_file_prefix
    urls = query.url_year_pair
    q = query.query
    dfs,variable_descriptions = urls_to_dfs(single_file_prefix, urls, q)
    
    dfs_to_file(dfs, [df.Name+".csv" for df in dfs], sep="\t",make_dir=query.name)
    comb = pd.concat(dfs)
    dfs_to_file([comb], [combined_file_prefix+".xlsx"], sep="\t",make_dir=query.name)
    dfs_to_file([comb], [combined_file_prefix+".csv"], sep="\t",make_dir=query.name)
    change_to_dir(query.name)
    with open(single_file_prefix+"kuvaukset.txt", "w") as f:
        for key, value in variable_descriptions.items():
            f.write(key+": "+value+"\n")
    os.chdir(__start_directory)