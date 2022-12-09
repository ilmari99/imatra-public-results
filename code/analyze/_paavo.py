from PostalArea import PostalArea, p_objs
import utils
import pandas as pd
from ModelSet import ModelSet

def calc_percent_col(df,base_h,other_h,add_year=True,rename_to=""):
    """Calculate a percentage column from a dataframe. Divides the other_h column by the base_h column and returns the result column"""
    cols = [df.loc[:,base_h],df.loc[:,other_h]]
    if add_year:
        cols.insert(0,df.loc[:,"vuosi"])
    a = list(utils.concat_clean_separate(*cols))
    a[-1] = a[-1].div(a[1].values).apply(lambda x: x*100)
    a[-1].rename(columns={other_h:f"{other_h}_%" if not rename_to else rename_to},inplace=True)
    return pd.concat([a[0],a[-1]],axis=1)

def perc_table(df,base_other=None):
    if not base_other:
        base_other = [
        ("he_vakiy","pt_tyott"),  # Työttömyys %
        ("he_vakiy","pt_elakel"), # Eläkeläis %
        ("te_taly","te_laps"),   # lapsitaloudet % (talouksista)
        ("tp_tyopy","tp_palv_gu"),# palvelualan työntekijöiden % (työntekijöistä)
        ("tp_tyopy","tp_c_teol"), # Teollisuuden työpaikat % (työntekijöistä)
        ]
    out = pd.DataFrame()
    out["vuosi"] = list(range(2012,2021))
    for i,bo in enumerate(base_other):
        base,other = bo
        a = calc_percent_col(df,base,other,add_year=True)
        out = out.merge(a,how="outer",on="vuosi")
    out.Name = "perc_table"
    return out

def perc_table_latest(tb,base_other=None):
    """ Create a percentage table with (base/other) columns for the latest data."""
    assert isinstance(tb,pd.DataFrame), "perc_table_latest needs a dataframe (perc_table or original)"
    if not hasattr(tb,"Name") or tb.Name != "perc_table":
        tb = perc_table(tb,base_other=base_other)
    lt = utils.get_rows(tb,vuosi=[2020]).dropna(axis=1).drop("vuosi",axis=1)
    lt.rename(columns={old:new for old,new in zip(lt.columns,[c+" (2020)" for c in lt.columns])},inplace=True)
    col2020 = [c.split(" (2020)")[0] for c in lt.columns]
    lt2019 = utils.get_rows(tb,vuosi=[2019]).dropna(axis=1).drop("vuosi",axis=1)
    for c in list(lt2019.columns):
        if c not in col2020:
            lt[c + " (2019)"] = lt2019[c].values[0]
    lt.reset_index(drop=True,inplace=True)
    return lt

def trend_table(tb,dep,indep="vuosi"):
    if not isinstance(dep,list):
        dep = [dep]
    ms = ModelSet(tb.loc[:,dep+[indep]],y_header=indep)
    data = {h+"_trend":v.params[indep] for h,v in ms.models.items()}
    df = pd.DataFrame(data,index=[0])
    return df
    
def new_latest_data(inplace=True):
    base_other = [
        ("he_vakiy","pt_tyott"),  # Työttömyys %
        ("he_vakiy","pt_elakel"), # Eläkeläis %
        ("te_taly","te_laps"),   # lapsitaloudet % (talouksista)
        ("tp_tyopy","tp_palv_gu"),# palvelualan työntekijöiden % (työntekijöistä)
        ("tp_tyopy","tp_c_teol"), # Teollisuuden työpaikat % (työntekijöistä)
        ]
    trend_vars = ["he_vakiy","tp_tyopy"]
    frames = []
    for p in p_objs.values():
        latest = p.latest_data
        perc_latest = perc_table_latest(p.get_dataframe(),base_other=base_other)
        tt = trend_table(p.get_dataframe(),dep=trend_vars)
        tb = pd.concat([latest,perc_latest,tt],axis=1)
        if inplace:
            p.latest_data = tb
        else:
            tb.Name = p.postal_code
        frames.append(tb)
    out = pd.concat(frames,axis=0)
    out.insert(0,"postialue",[t.Name for t in frames])
    return out

def save_latest_data(path="data/postinumeroittain/viimeisimmat_tiedot_muok.xlsx"):
    df = new_latest_data(inplace=False)
    df.to_excel(path,index=False)
    return df

def employment_perc():
    for area,ob in p_objs.items():
        print(f"{area} työttömyys %: ",end="")
        df = ob.get_dataframe()
        yr = df.loc[df["vuosi"] == 2019]
        base = yr[["he_18_19","he_20_24","he_25_29","he_30_34","he_35_39","he_40_44","he_45_49","he_50_54","he_55_59","he_60_64"]].sum(axis=1) - yr[["pt_opisk","pt_muut"]].sum(axis=1)
        other = yr["pt_tyott"].values[0]
        print(100*(other/base))
        
if __name__ == "__main__":
    pass
    