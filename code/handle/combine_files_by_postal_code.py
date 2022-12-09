import os
import pandas as pd
import matplotlib.pyplot as plt
import re
imatra_files = [
    "./Imatra_ikarakenne/Imatra_ikarakenne_2013-2020.csv",
    "./Imatra_koulutusrakenne/Imatra_koulutusrakenne_2012-2020.csv",
    "./Imatra_paatoiminta/Imatra_paatoiminta_2012-2019.csv",
    "./Imatra_rahatulot/Imatra_rahatulot_2012-2020.csv",
    "./Imatra_rakennukset/Imatra_rakennukset_2013-2020.csv",
    "./Imatra_taloudet/Imatra_taloudet_2013-2020.csv",
    "./Imatra_talouksien_tulot/Imatra_talouksien_tulot_2012-2020.csv",
    "./Imatra_tyopaikat/Imatra_tyopaikat_2012-2019.csv",
    ]

def separate_postal_codes_from_combined_df(df):
    """ Takes in a combined dataframe (all data for 'ikärakenne' for example) and returns a list of dataframes,
    With one dataframe for each postal code.
    
    Args:
        df (dataframe): A dataframe that has combined data for all postal codes, in the format df["postinumero"] = "xxxxx (yyyy)"

    Returns:
        list (of dataframes): Returns a list of dataframes, with one dataframe for each postal code.
        The dataframes are in the same order as the postal codes in the input dataframe.
    """    
    pcode_frames = []
    for n,row in enumerate(df.iterrows()):
        row = pd.DataFrame(row[1]).T
        # The "postinumero" key contains the postal code and year in the format "xxxxx (yyyy)"
        postal = row["Postinumero"].iloc[0].split(" ")          # Split the postal code and year
        row.pop("Postinumero")
        year = postal.pop(1).strip("()")                        # Separate year
        postal = postal[0]                                      # Get the postal code
        pcodes = [df.Name for df in pcode_frames]               # Check if the postal code is already in the list
        if postal not in pcodes:
            # If the postal code is not in the list, create a new dataframe with "vuosi" as the first column
            df = pd.DataFrame(columns=df.columns[1:].insert(0,"vuosi"))
        else:
            # If the postal code is already in the list, get the dataframe for that postal code
            i = pcodes.index(postal)
            df = pcode_frames.pop(i)
        row["vuosi"] = int(year)
        df = pd.concat([df,row], ignore_index=True)             # Concatenate the new row to the dataframe
        df.Name = postal
        pcode_frames.append(df)
    return pcode_frames

def print_frame_names(dfs):
    print([df.Name for df in dfs])


def files_to_dict_of_lists(imatra_files):
    frames = {}
    for fname in imatra_files:
        categ = fname.split("/")
        categ = "_".join(categ[1].split("_")[1:])
        frames[categ] = separate_postal_codes_from_combined_df(pd.read_csv(fname,sep="\t"))
    categs = list(frames.keys())
    return frames,categs

def merge_by_postalcode(frames, categs):
    """Merge the dataframes for each postal code.
    So merge one dataframe (certain postal code) from each list of dataframes (certain category) 
    in to one dataframe and index by "vuosi"

    Args:
        frames (_type_): _description_
        categs (_type_): _description_

    Returns:
        _type_: _description_
    """    
    merged_dataframes = []


    for dfs in frames.pop(categs[0]):                                   # a list of dataframes
        merged = dfs
        name = dfs.Name
        print(f"Merging multiple dataframes for {merged.Name}...")
        for categ,df in frames.items():                                 #another list of data-frames
            print(categ)
            i = [d.Name for d in df].index(name)                        # Find index of postal code in the list
            merged = merged.merge(df.pop(i), how="outer", on="vuosi")   # Merge on "vuosi" column maintaining both frames' "vuosi" columns
        merged.set_index(["vuosi"], inplace=True)                       # Set index to "vuosi" and sort by "vuosi"
        merged.sort_index(inplace=True)
        merged.Name = name
        merged_dataframes.append(merged)
    return merged_dataframes

def write_by_postal_code(merged_dataframes):
    start_dir = os.getcwd()
    os.chdir("./Imatra_postialueittain")
    for mdf in merged_dataframes:
        with open(f"{mdf.Name}_tiedot.xlsx","wb") as f:
            mdf.to_excel(f)
    os.chdir(start_dir)

frames, categs = files_to_dict_of_lists(imatra_files)
merged_dataframes = merge_by_postalcode(frames, categs)
write_by_postal_code(merged_dataframes)


