import requests
import pandas as pd
import json
import time
import re
import os
from utils import get_response, try_parse_labels

def read_tulokymmenys_query(query_file="code/fetch/querys/tulokymmenys_query.json",
                            save_to="data/rahadata/tulokymennys.xlsx",
                            alue = "SK093",
                            ):
    """"Reads the query from the specified location(/default) and sends the query to the API.
    Prints the result and saves it to the specified location(/default)
    """
    assert re.match("^SK*",alue)
    with open(query_file) as f:
        query = json.load(f)
    if alue != "SK093":
        raise NotImplementedError("Only SK093 is supported")
    query = query["query"][1]["selection"]["values"] = [alue]
    resp = get_response("https://pxweb2.stat.fi:443/PxWeb/api/v1/fi/StatFin/tjt/statfin_tjt_pxt_12hi.px",query)
    cv = {"vuosi": []}
    for d in resp["data"]:
        c = d["key"][1]
        c = int(c) if c.isdigit() else c
        v = float(d["values"][0])
        if c not in cv:
            cv[c] = []
        year = int(d["key"][0])
        if year not in cv["vuosi"]:
            cv["vuosi"].append(year)
        cv[c].append(v)
    df = pd.DataFrame(cv)
    df.drop(["SS"], axis=1,inplace=True)
    print(df)
    if save_to:
        df.to_excel(save_to,index=False)
    return df

if __name__ == "__main__":
    read_tulokymmenys_query()