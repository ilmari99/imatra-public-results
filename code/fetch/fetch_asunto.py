import requests
import pandas as pd
import json
import time
import re
import os
from utils import get_response, try_parse_labels


def read_asuntojen_hlot_query(query_file="code/fetch/querys/asuntojen_henkilot.json",
                              save_to="data/asuntodata/asunto_henkilot.xlsx",
                              house_type = "S",
                              alue = "KU153",
                              ):
    # House types are ["S", "1", "2", "3", "4"] refer to: https://pxweb2.stat.fi/PxWeb/pxweb/fi/StatFin/StatFin__asas/statfin_asas_pxt_116a.px/table/tableViewLayout1/
    with open(query_file) as f:
        query = json.load(f)
    assert house_type in ["S", "1", "2", "3", "4"], "House type must be one of the following: S, 1, 2, 3, 4"
    assert re.match("^KU[0-9]{3}$", alue), "Alue must be in the format 'KUXXX'"
    query["query"][0]["selection"]["values"] = [house_type]
    query["query"][1]["selection"]["values"] = [alue]
    resp = get_response("https://pxweb2.stat.fi:443/PxWeb/api/v1/fi/StatFin/asas/statfin_asas_pxt_116a.px",query)
    cv = {"vuosi": []}
    for d in resp["data"]:
        c = d["key"][3]
        c = int(c) if c.isdigit() else c
        v = float(d["values"][0])
        if c not in cv:
            cv[c] = []
        year = int(d["key"][0])
        if year not in cv["vuosi"]:
            cv["vuosi"].append(year)
        cv[c].append(v)
    df = pd.DataFrame(cv)
    print(df)
    if save_to:
        df.to_excel(save_to)
    return df

def read_asuntokunnan_vanhin_query(query_file="code/fetch/querys/asuntokunnan_vanhin.json",
                              save_to="data/asuntodata/asuntokunnan_vanhin_1.xlsx",
                              household = "1",
                              alue = "KU153",
                              ):
    with open(query_file,encoding="UTF-8") as f:
        query = json.load(f)
    assert re.match("^KU[0-9]{3}$", alue), "Alue must be in the format 'KUXXX'"
    query["query"][2]["selection"]["values"] = [household]
    query["query"][0]["selection"]["values"] = [alue]
    resp = get_response("https://statfin.stat.fi:443/PxWeb/api/v1/fi/StatFin/asas/statfin_asas_pxt_116d.px",query)
    cols = ["vuosi","alue","talo","koko"]
    df = None
    while resp["data"]:
        d = resp["data"][0]
        year = int(d["key"][2])
        row = [year,alue,"S",household]
        while year == int(d["key"][2]):
            d = resp["data"].pop(0)
            if d["key"][4] not in cols:
                cols.append(d["key"][4])    
            row.append(int(d["values"][0]))
            if not resp["data"]:
                break
            d = resp["data"][0]
        if df is None:
            df = pd.DataFrame(columns=cols)
        df.loc[len(df)] = row
    if save_to:
        df.to_excel(save_to)
    return df

if __name__ == "__main__":
    df = read_asuntokunnan_vanhin_query(save_to = "data/asuntodata/asuntokunnan_vanhin_4.xlsx",
                                        household = "4",)
    print(df)