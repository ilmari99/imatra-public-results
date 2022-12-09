import random
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import datetime
rloc = "./data/kartta/RAKENNUKSET.TAB"
ploc = "./data/kartta/Postinumeroalueet.shp"
def get_empty_houses(gdf):
    """ Get all houses, that are meant for living (total of over 100 persons living in such houses), and currently have 0 residents"""
    print(gdf)
    asrak = {}
    for i,r in gdf.iterrows():
        if r["C_KAYTTARK_SELITE"] not in asrak:
            asrak[r["C_KAYTTARK_SELITE"]] = 0
        asrak[r["C_KAYTTARK_SELITE"]] += r["I_ASUKKAITA"]   # Add the number of people to the dictionary of building types
    house_types = []
    for k,v in asrak.items():   # Find each building type that has atleast 100 people living in it
            if v > 100:
                house_types.append(k)
    # Select all building types in which there are more than 100 residents in Imatra
    # And which are currently empty (I_ASUKKAITA == 0)
    #out = gdf[gdf["C_KAYTTARK_SELITE"].isin(house_types) and gdf["I_ASUKKAITA"] == 0]
    print(house_types)
    out = gdf[gdf["C_KAYTTARK_SELITE"].isin(house_types)][gdf["I_ASUKKAITA"] == 0]
    return out

def merge_areas_and_data():
    """ Merge the shapefile areas and the xlsx data on 'postialue' """
    gdf = gpd.read_file(ploc)
    gdf.rename(columns={"posti_alue":"postialue"},inplace=True)
    latest_data = pd.read_excel("./data/postinumeroittain/viimeisimmat_tiedot_muok.xlsx")
    new_gdf = gdf.merge(latest_data,on="postialue")
    new_gdf.to_file("./data/kartta/postinumeroalueet_viimeisimmät_tiedot.geojson",index=False)

if __name__ == "__main__":
    gdf = gpd.read_file(rloc)
    gdf["I_ASUKKAITA"] = gdf["I_ASUKKAITA"].apply(lambda x : float(random.randint(0,5)))
    print(gdf)
    og_cols = list(gdf.columns)
    gdf["valmistumisvuosi"] = [pvm.year for pvm in gdf["C_VALMPVM"]]
    gdf["rak_ika"] = 2022 - gdf["valmistumisvuosi"]
    og_cols.insert(1,"valmistumisvuosi")
    og_cols.insert(1,"rak_ika")
    gdf = gdf[og_cols]

    print(gdf)
    gdf.to_file("./data/kartta/satunnaiset-asukkaat.TAB")
    tyhjat = get_empty_houses(gdf)
    tyhjat.to_file("./data/kartta/satunnaiset-asukkaat-tyhjat.TAB")
    print(tyhjat)