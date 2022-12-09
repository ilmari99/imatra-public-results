import requests
import pandas as pd
import json
import time
import re
import os
from utils import get_response, try_parse_labels, convert_kunta
FOLDER = "data/vaestodata/"
    
def read_vaestomuutokset_query(query_file="code/fetch/querys/vaestomuutokset.json",
                              save_to="vaestomuutokset.xlsx",
                              alue = "KU153",
                              time_period = "year"):
    with open(query_file) as f:
        query = json.load(f)
    assert re.match("^KU[0-9]{3}$", alue), "Alue must be in the format 'KUXXX'"
    assert time_period in ["year","month"], "Time period must be one of the following: 'year', 'month'"
    query["query"][0]["selection"]["values"] = [alue]
    urls = {"year":"https://pxweb2.stat.fi:443/PxWeb/api/v1/fi/StatFin/kuol/statfin_kuol_pxt_12au.px",
            "month":"https://pxweb2.stat.fi:443/PxWeb/api/v1/fi/StatFin/kuol/statfin_kuol_pxt_12as.px"}
    url = urls[time_period]
    resp = get_response(url,query)
    cols = resp.pop("columns")
    labels = [d["text"].replace(" (ennuste 2021)","").lower() for d in cols]
    data = []
    for d in resp["data"]:
        values = [int(d["key"][0]),str(d["key"][1])]
        values = values + [int(v) for v in d["values"]]
        data.append(values)
    out = pd.DataFrame(data, columns=labels)
    if save_to:
        out.to_excel(FOLDER + save_to, index=False)
    return out


def read_vaennuste_query(query_file="code/fetch/querys/vaestoennusteet.json",
                              save_to="vaestoennuste.xlsx",
                              sukupuoli = "SSS",
                              alue = "KU153"):
    with open(query_file) as f:
        query = json.load(f)
    assert sukupuoli in ["1","2","SSS"], "Sukupuoli must be one of the following: '1', '2', 'SSS'"
    assert re.match("^KU[0-9]{3}$", alue), "Alue must be in the format 'KUXXX'"
    query["query"][1]["selection"]["values"] = [sukupuoli]
    query["query"][0]["selection"]["values"] = [alue]
    resp = get_response("https://pxweb2.stat.fi:443/PxWeb/api/v1/fi/StatFin/vaenn/statfin_vaenn_pxt_139g.px",query)
    cols = resp.pop("columns")
    labels = [d["text"].replace(" (ennuste 2021)","").lower() for d in cols]
    print(labels)
    data = []
    for d in resp["data"]:
        values = [str(d["key"][0]),int(d["key"][1]),str(d["key"][2])]
        values = values + [int(v) for v in d["values"]]
        data.append(values)
    out = pd.DataFrame(data, columns=labels)
    if save_to:
        out.to_excel(FOLDER + save_to, index=False)
    return out


def _read_ikajakauma_ennuste_query(query_file="code/fetch/querys/ikajakauma_ennuste.json",
                              save_to="ikajakauma_ennuste.xlsx",
                              alue = "KU153",
                              sukupuoli = "SSS",
                              ):
    with open(query_file,encoding="UTF-8") as f:
        query = json.load(f)
    assert re.match("^KU[0-9]{3}$", alue), "Alue must be in the format 'KUXXX'"
    assert sukupuoli in ["1","2","SSS"], "Sukupuoli must be one of the following: '1', '2', 'SSS'"
    query["query"][0]["selection"]["values"] = [alue]
    query["query"][1]["selection"]["values"] = [sukupuoli]
    resp = get_response("https://statfin.stat.fi:443/PxWeb/api/v1/fi/StatFin/vaenn/statfin_vaenn_pxt_139f.px",query)
    labels = ["alue","vuosi","sukupuoli"]
    data = []
    iadd = 0
    breakall = False
    for i,_ in enumerate(resp["data"]):
        d = resp["data"][i+iadd]
        values = [str(d["key"][0]),int(d["key"][1]),str(d["key"][2])]
        year = values[1]
        while int(d["key"][1]) == year:
            label = d["key"][3]
            if label not in labels:
                labels.append(label)
            values.append(int(d["values"][0]))
            iadd = iadd + 1
            try:
                d = resp["data"][i+iadd]
            except IndexError:
                breakall = True
                break
        iadd = iadd - 1
        data.append(values)
        #print(data)
        if breakall:
            break
    out = pd.DataFrame(data, columns=labels)
    print(out)
    if save_to:
        out.to_excel(FOLDER + save_to, index=False)
    return out


def _read_ikajakauma_query(query_file="code/fetch/querys/ikajakauma_pitka.json",
                              save_to="ikajakauma_toteutunut_SSS.xlsx",
                              sukupuoli = "SSS",
                              alue = "KU153"):
    with open(query_file,encoding="UTF-8") as f:
        query = json.load(f)
    assert sukupuoli in ["1","2","SSS"], "Sukupuoli must be one of the following: '1', '2', 'SSS'"
    assert re.match("^KU[0-9]{3}$", alue), "Alue must be in the format 'KUXXX'"
    query["query"][0]["selection"]["values"] = [alue]
    query["query"][2]["selection"]["values"] = [sukupuoli]
    resp = get_response("https://statfin.stat.fi:443/PxWeb/api/v1/fi/StatFin/vaerak/statfin_vaerak_pxt_11re.px",query)
    labels = ["alue","vuosi","sukupuoli"]
    data = []
    iadd = 0
    breakall = False
    out = pd.DataFrame(columns=labels)
    for i,_ in enumerate(resp["data"]):
        d = resp["data"][i+iadd]
        age = d["key"][1]
        yv = {}
        while d["key"][1] == age:
            year = int(d["key"][3])
            val = int(d["values"][0])
            yv[year] = val
            iadd = iadd + 1
            try:
                d = resp["data"][i+iadd]
            except IndexError:
                breakall = True
                break
        iadd = iadd - 1
        if len(out["vuosi"].values) == 0:
                out["vuosi"] = list(yv.keys())
                out["alue"] = [alue] * len(out["vuosi"].values)
                out["sukupuoli"] = [sukupuoli] * len(out["vuosi"].values)
        out[age] = list(yv.values())
        if breakall:
            break
    print(out)
    if save_to:
        out.to_excel(FOLDER + save_to, index=False)
    return out

def read_full_ikajakauma(save_to="ikajakauma.xlsx",
                         sukupuoli = "SSS",
                         alue = "KU153"):
    
    ikajak = _read_ikajakauma_query(save_to=False,sukupuoli=sukupuoli,alue=alue)
    ika_ennuste = _read_ikajakauma_ennuste_query(save_to=False,sukupuoli=sukupuoli,alue=alue)
    df = pd.concat([ikajak,ika_ennuste],axis=0)
    df.drop_duplicates(subset=["vuosi"],keep="last",inplace=True)
    if save_to:
        df.to_excel(FOLDER + save_to,index=False)
    
def read_tulo_muutto_kunnittain(
                    query_file="code/fetch/querys/sisaan_muutot.json",
                    save_to="sisaan_muutot_SSS.xlsx",
                    sukupuoli = "SSS",
                    alue = "KU153"):
    with open(query_file,encoding="UTF-8") as f:
        query = json.load(f)
    assert sukupuoli in ["1","2","SSS"], "Sukupuoli must be one of the following: '1', '2', 'SSS'"
    assert re.match("^KU[0-9]{3}$", alue), "Alue must be in the format 'KUXXX'"
    query["query"][0]["selection"]["values"] = [alue]
    query["query"][2]["selection"]["values"] = [sukupuoli]
    resp = get_response("https://statfin.stat.fi:443/PxWeb/api/v1/fi/StatFin/muutl/statfin_muutl_pxt_11a1.px",query)
    labels = ["Tulo","sukupuoli","vuosi"]
    out = pd.DataFrame(columns=labels)
    data = resp.pop("data")
    print(resp)
    kv = None
    while data:
        if kv is None:
            kv = data.pop(0)
            k,v = kv["key"],kv["values"]
        lahto = k[1]
        vals = []
        while lahto == k[1]:
            vuosi = int(k[3])
            if vuosi not in out["vuosi"].values:
                out.loc[len(out)] = [alue,sukupuoli,vuosi]
            vals.append(int(v[0]))
            if not data:
                break
            kv = data.pop(0)
            k,v = kv["key"],kv["values"]
        if lahto not in out.columns:
            out = out.reindex(columns=out.columns.tolist() + [lahto])
        out[lahto] = vals
    out.rename(columns={old:new for old,new in zip(out.columns,convert_kunta(*out.columns.tolist()))},inplace=True)
    print(out)
    if save_to:
        out.to_excel(FOLDER + save_to, index=False)
    return out

def read_pois_muutto_kunnittain(
                    query_file="code/fetch/querys/pois_muutot.json",
                    save_to="pois_muutot_SSS.xlsx",
                    sukupuoli = "SSS",
                    alue = "KU153"):
    with open(query_file,encoding="UTF-8") as f:
        query = json.load(f)
    assert sukupuoli in ["1","2","SSS"], "Sukupuoli must be one of the following: '1', '2', 'SSS'"
    assert re.match("^KU[0-9]{3}$", alue), "Alue must be in the format 'KUXXX'"
    query["query"][1]["selection"]["values"] = [alue]
    query["query"][2]["selection"]["values"] = [sukupuoli]
    resp = get_response("https://statfin.stat.fi:443/PxWeb/api/v1/fi/StatFin/muutl/statfin_muutl_pxt_11a1.px",query)
    labels = ["Tulo","sukupuoli","vuosi"]
    out = pd.DataFrame(columns=labels)
    data = resp.pop("data")
    print(data[0:10])
    kv = None
    while data:
        if kv is None:
            kv = data.pop(0)
            k,v = kv["key"],kv["values"]
        lahto = k[0]
        vals = []
        while lahto == k[0]:
            vuosi = int(k[3])
            if vuosi not in out["vuosi"].values:
                out.loc[len(out)] = [alue,sukupuoli,vuosi]
            vals.append(int(v[0]))
            if not data:
                break
            kv = data.pop(0)
            k,v = kv["key"],kv["values"]
        if lahto not in out.columns:
            out = out.reindex(columns=out.columns.tolist() + [lahto])
        out[lahto] = vals
    out.rename(columns={old:new for old,new in zip(out.columns,convert_kunta(*out.columns.tolist()))},inplace=True)
    print(out)
    if save_to:
        out.to_excel(FOLDER + save_to, index=False)
    return out
    
if __name__ == "__main__":
    a = read_full_ikajakauma(save_to = "ikajakauma_2.xlsx",
                             sukupuoli="2")
    