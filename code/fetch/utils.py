import requests
import json
import time

def convert_kunta(*kunta):
    """Converts a list of kunta kodes to a list of kunta names"""
    kunta_names = []
    conv_dict = json.load(fp=open("code/fetch/kuntakonversio.json"))
    for k in kunta:
        kunta_names.append(conv_dict.get(k, k))
    return kunta_names

def print_nested_dict(d, indent=0):
    for key, value in d.items():
        if isinstance(value, dict):
            print('\t' * indent + str(key))
            print_nested_dict(value, indent+1)
        else:
            print('\t' * indent + str(key) + ": " + str(value))

def get_response(url, query):
    while 1:
        resp = requests.post(url, data=json.dumps(query))       # Response object from website
        resp_json = resp.json()                                 # Response object as JSON
        # If response is not ready, wait and try again
        if "error" not in resp_json:
            break
        print("error in response:", resp_json["error"],"\nWaiting for 5 seconds...")
        time.sleep(5)
    return resp_json

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

def try_parse_labels(resp_json):
    """Tries to parse the labels from the response_json."""
    try:
        labels = old_format_labels(resp_json)
        if not labels:                                              # If data is in new format, then labels are empty but no error is raised in 'old_format_labels()'
            labels = new_format_labels(resp_json)
    except:
        labels = {}
    return labels