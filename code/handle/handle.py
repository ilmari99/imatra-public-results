from curses.ascii import isdigit
import pandas as pd
from collections import Counter
import sys
import os

def monthly_population_to_annual(df):
    """Convert monthly data, to annual data bu taking the average of the 12 month period."""
    # Check that each year has 12 measurements
    new_columns = [c.split("M")[0] for c in df.columns]
    count = Counter(new_columns)
    for h,c in count.items():
        if h != "Alue":
            assert c == 12, f"{h} has {c} columns, but it should have 12."
    # Remove the "M[xy]" ending from te dataframe column names
    df.rename(columns={c:new_columns[i] for i,c in enumerate(df.columns)},inplace=True)
    print(df.head())
    h = df.columns.unique().to_list()
    print(h)
    area = df.pop("Alue")
    df = df.groupby(axis=1,level=0).sum()
    df = df.apply(lambda x: round(x/12,0),axis=1)
    df.insert(0,"Alue",area)
    return df

def combine_to_single_df(dfs):
    """Combine multiple dataframes into one dataframe."""
    # add parent directory to path
    sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    print(sys.path)
    from code.analyze import PostalArea as pa
    dfs = []
    for d in pa.p_objs:
        dfs.append(d.get_dataframe())
    avg_vars = ["hr_ktu","hr_mtu","tr_ktu", "tr_mtu"]       # Variables that should be averaged, not summed
    df = dfs.pop(0)
    og_size = df.shape
    sz = len(dfs)
    for d in dfs:
        d.pop("vuosi")
        for c in d.columns:
            df[c] += d[c]
    # Average the variables that deserve it
    for v in avg_vars:
        df[v] = df[v]/sz
    assert og_size == df.shape, "The dataframes were not combined correctly."
    df.to_excel("data/Imatra_postinumeroittain/Imatra_tiedot.xlsx")
    return df

def combine_house_types():
    paths = [("data/asuntodata/kerrostalo_henkilot.xlsx","kerrostalo"),
             ("data/asuntodata/omakoti_henkilot.xlsx","omakotitalo"),
             ("data/asuntodata/rivitalo_henkilot.xlsx","rivitalo")]
    outdf = pd.DataFrame()
    for p in paths:
        df = pd.read_excel(p[0])
        df.drop("Unnamed: 0",axis=1,inplace=True)
        sum_df = pd.DataFrame(columns=["vuosi","yht"])
        for i,r in df.iterrows():
            year = r["vuosi"]
            cols = df.columns.to_list()[1:]
            yht = [c*r[c] for c in cols]
            yht = sum(yht)
            sum_df = pd.concat([sum_df,pd.DataFrame(data={"vuosi":year,"yht":yht},index=[i])],axis = 0)
        sum_df.rename(columns={"yht":p[1]},inplace=True)
        if "vuosi" in outdf.columns:
            sum_df.drop("vuosi",axis=1,inplace=True)
        outdf = pd.concat([outdf,sum_df],axis=1)
    outdf.to_excel("data/asuntodata/mahd_asukkaat_asuntotyypeittäin.xlsx")

def combine_vakiluku_vakienn():
    vaenn = pd.read_excel("data/vaestoennuste_yht.xlsx")
    vakiluk = pd.read_excel("data/vaestomuutokset.xlsx")
    vaenn.rename(columns={"väestö 31.12.":"väkiluku"},inplace=True)
    same_cols = ["vuosi","alue","luonnollinen väestönlisäys", "väkiluku"]
    df = pd.concat([vaenn,vakiluk],axis=0)
    for c in df.columns:
        if c not in same_cols:
            df.drop(c,axis=1,inplace=True)
    df.sort_values(by="vuosi",inplace=True)
    df.drop_duplicates(subset=["vuosi"],keep="last",inplace=True)
    df.to_excel("data/vakiluku_yhdiste.xlsx",index=False)

def combine_ikajakauma_ennuste():
    ikajakauma = pd.read_excel("data/ikajakauma.xlsx")
    ika_ennuste = pd.read_excel("data/ikajakauma_ennuste.xlsx")
    df = pd.concat([ikajakauma,ika_ennuste],axis=0)
    df.drop_duplicates(subset=["vuosi"],keep="last",inplace=True)
    df.to_excel("data/ikajakauma_yhdiste.xlsx",index=False)
    
def convert_to_change_matrix(df,non_numeric_cols=[]):
    """Converts a dataframe to a change matrix.
    The dataframe is converted to a change matrix by subtracting the previous row from the current row.
    The non_numeric_cols list specifies the columns that should not be converted to numeric.
    """
    df = df.copy()
    pdf = pd.DataFrame(df.loc[:,non_numeric_cols].values,columns=non_numeric_cols)
    for col in df.columns:
        if col in non_numeric_cols:
            continue
        sdf = df.loc[:,col]
        values = [None]
        for i in range(1,len(sdf)):
            if sdf.iloc[i-1] in [0,None] or sdf.iloc[i] in [0,None]:
                ch = None
            else:
                ch = (sdf.iloc[i] - sdf.iloc[i-1])/sdf.iloc[i-1]
            values.append(ch)
        pdf[col] = values
    return pdf

def create_ikajakauma_change_matrix(save_to="data/vaestodata/ikajakauma_muutosmatriisi_SSS.xlsx"):
    df = pd.read_excel("data/vaestodata/ikajakauma_yhdiste_SSS.xlsx")
    df.drop(["alue","sukupuoli"],axis=1,inplace=True)
    df = convert_to_change_matrix(df,["vuosi"])
    print(df)
    if save_to:
        df.to_excel(save_to,index=False)
        
def group_age_matrix(f = "data/vaestodata/ikajakauma_yhdiste_SSS.xlsx",
                     save_to="data/vaestodata/ikajakauma_2kymmenittäin.xlsx"):
    df = pd.read_excel(f)
    df.drop(["alue","sukupuoli","SSS"],axis=1,inplace=True)
    out = pd.DataFrame()
    out["vuosi"] = df.pop("vuosi")
    new_cols = ["0-19","20-39","40-59","60-79","80-"]
    for nc in new_cols:
        if nc == "80-":
            out[nc] = df.iloc[0:].sum(axis=1)
            break
        else:
            out[nc] = df.iloc[:,0:20].sum(axis=1)
        df.drop(df.columns[0:20],axis=1,inplace=True)
    if save_to:
        out.to_excel(save_to,index=False)
    
def group_income_matrix(f = "data/rahadata/tulokymmenys.xlsx",
                     save_to="data/rahadata/tuloviidennes.xlsx"):
    df = pd.read_excel(f)
    print(df)
    #df.drop(["alue","sukupuoli","SSS"],axis=1,inplace=True)
    out = pd.DataFrame()
    out["vuosi"] = df.pop("vuosi")
    new_cols = ["0-20%","20-40%","40-60%","60-80%","80-100%"]
    for nc in new_cols:
        out[nc] = df.iloc[:,0:2].sum(axis=1)
        df.drop(df.columns[0:2],axis=1,inplace=True)
    if save_to:
        out.to_excel(save_to,index=False)
    print(out)
    
    

if __name__ == "__main__":
    group_income_matrix()