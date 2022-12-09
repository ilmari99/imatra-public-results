import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import utils

class PostalArea:
    """Create an object for each postal code.
    The object only contains postal area specific data.
    """
    postal_code = ""            # Postal code as string
    data_file_path = ""   # Relative path to the postal area data file
    df = None           # Dataframe containing the data for the postal area
    area_m2 = None
    area_name = ""
    latest_data = pd.DataFrame()
    
    def __init__(self, postal_code, file_path,area_m2=None, area_name=""):
        self.postal_code = postal_code
        self.data_file_path = file_path
        self.df = self.get_dataframe(file_path)
        self.area_m2 = area_m2
        self.area_name = area_name
        self.latest_data = self.create_latest_data()
    
    
    def get_dataframe(self,path=None,force=False):
        """Creates a dataframe from the objects file path, or from the specified path.

        Args:
            path (string, optional): Alternative path to the file to be read. Defaults to objects own file_path attribute.
            force (bool, optional): If True, creates a new dataframe object, even if an old dataframe exists. Defaults to False.

        Returns:
            dataframe: The dataframe containing the data for the postal area.
        """        
        if self.df is not None and not force:
            return self.df.copy()
        fpath = self.data_file_path
        if path is not None:
            fpath = path
        df = pd.read_excel(fpath)
        df.Name = self.postal_code
        self.df = df.copy() 
        return df
    

    def create_latest_data(self):
        """Creates a dataframe containing the latest data for the postal area.
        """
        latest_data = utils.get_rows(self.get_dataframe(force=True),vuosi=[2020]).dropna(axis=1).drop("vuosi",axis=1)
        latest_data.rename(columns={old:new for old,new in zip(latest_data.columns,[c+" (2020)" for c in latest_data.columns])},inplace=True)
        cols_2020 = [c.split(" (2020)")[0] for c in latest_data.columns]
        data_2019 = utils.get_rows(self.get_dataframe(force=True),vuosi=[2019]).dropna(axis=1).drop("vuosi",axis=1)
        for c in list(data_2019.columns):
            if c not in cols_2020:
                latest_data[c + " (2019)"] = data_2019[c].values[0]
        latest_data.reset_index(drop=True,inplace=True)
        self.latest_data = latest_data
        return latest_data

p_objs = {
    "55100": PostalArea("55100", "./data/postinumeroittain/55100_tiedot.xlsx",96124901,"Imatran keskus"),
    "55120": PostalArea("55120", "./data/postinumeroittain/55120_tiedot.xlsx",5382409,"Mansikkala-Tuulikallio"),
    "55400": PostalArea("55400", "./data/postinumeroittain/55400_tiedot.xlsx",7012969,"Tainionkoski-Mustalampi"),
    "55420": PostalArea("55420", "./data/postinumeroittain/55420_tiedot.xlsx",18408828,"Karhumäki-Karhukallio"),
    "55510": PostalArea("55510", "./data/postinumeroittain/55510_tiedot.xlsx",1549200,"Sienimäki"),
    "55610": PostalArea("55610", "./data/postinumeroittain/55610_tiedot.xlsx",25054645,"Rajapatsas-Teppanala"),
    "55700": PostalArea("55700", "./data/postinumeroittain/55700_tiedot.xlsx",6827884,"Vintteri-Virasoja"),
    "55800": PostalArea("55800", "./data/postinumeroittain/55800_tiedot.xlsx",93462850,"Vuoksenniska-Saarlampi"),
    "55910": PostalArea("55910", "./data/postinumeroittain/55910_tiedot.xlsx",20726495,"Rautio-Kurkvuori"),
}

imatra_alue = sum([p_objs[key].area_m2 for key in p_objs.keys()])
p_objs["imatra"] = PostalArea("Imatra", "./data/postinumeroittain/Imatra_tiedot.xlsx",imatra_alue)