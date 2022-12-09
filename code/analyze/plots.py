import pandas as pd
import matplotlib.pyplot as plt
import cmasher as cmr
import analyze
import utils
from _config import *
from ModelSet import ModelSet
import numpy as np
#import _asunto_plots as asunto
#import _raha_plots as raha
#import _vaesto_plots as vaesto
from _vaesto_plots import *
from _asunto_plots import *
from _raha_plots import *
from matplotlib import animation
from matplotlib.colors import LinearSegmentedColormap
from itertools import chain
import matplotlib as mpl

""" FUNCTIONS: 
'plot_asunto_henkilot_bars' : Plot the size of households as a bar animation
'plot_asunto_henkilot_lines' : Plot the size of households
'plot_asuntokunnat_stacked_bars' : Plot the size of households as a stacked bar graph (BEST)
'plot_asuntotyypeittain_bars' : Plot the amount of people living in each type of household
'plot_asuntotyypeittain_stacked_bars' : Plot the amount of people living in each type of household as a stacked bar graph (BEST)
'plot_asuntotyypeittain_lines',
'plot_kerrostalo_henkilot_bars',
'plot_kerrostalo_henkilot_lines',
'plot_omakotitalo_henkilot_bars',
'plot_omakotitalo_henkilot_lines',
'plot_tulojakauma_bars',
'plot_tulojakauma_lines',
'plot_current_age_trend',
'plot_ikajakauma_bars',
'plot_poismuutot_lines',
'plot_sisaanmuutot_lines'
"""
    

if __name__ == "__main__":
    print()
    funs = {}
    locs = list(locals().items())
    print(locs)
    path_map = {
        "_vaesto_plots":"vaesto/",
        "_asunto_plots":"asuminen/",
        "_raha_plots":"talous_ja_tyollisyys/",
    }
    for k,f in locs:
        if callable(f) and k.startswith("plot_"):
            funs[k] = f
    for f in funs.items():
        res = f[1]()
        fun = f[1]
        fun_name = f[0]
        if True:
            print("From module:", fun.__module__)
            print("Function:",fun_name)
            print("DOCS:   ",fun.__doc__)
            plt.show()
            continue
        utils.save_figure()