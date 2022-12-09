import pandas as pd
from ModelSet import ModelSet
import matplotlib.pyplot as plt
import cmasher as cmr
import analyze
import utils
import numpy as np
from matplotlib import animation
from matplotlib.colors import LinearSegmentedColormap
from _config import *


def _plot_tulojakauma_bars(f = "rahadata/tulokymmenys.xlsx",animate=True):
    """Tulojakauma tulokymmenyksittäin. Tuloluokat  1 : 0-10%, 2 : 10-20% .... 10 : 90-100%"""
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df,y_header="vuosi")
    cm = plt.cm.get_cmap("cmr.pepper_r")
    k_scaled = utils.normed_dict([m.params[0] for m in distr.models.values()])
    def update2(ax,xy,slpos,err_args):
        for i,row in xy.iterrows():
            scaled = k_scaled[distr.models[row.loc["label"]].params[0]]
            c = cm(scaled)
            eargs = {}
            if err_args:
                eargs = {"yerr":err_args["yerr"][i],"ecolor":err_args["ecolor"],"capsize":err_args["capsize"]}
            ax.bar(row["x"],row["y"],align="edge",color=c,**eargs)
        ax.grid(True)
        ax.set_title("Tulojakauma (10%) vuosittain")
        ax.set_ylabel("% väestöstä")
        ax.set_xlabel("Tuloluokka")
        ax.set_ylim(-1,df.max().max()+1)
        ax.legend()
    fig, ax, slider = analyze.plot_slider_fig(distr,slkwargs={"valstep":1},slider_update_func=update2)
    #ax.set_facecolor("black")
    fig.set_size_inches(*FIG_SIZE)
    if animate:
        def animate_func(i):
            slider.set_val(i)
        anim = animation.FuncAnimation(fig,
                                        animate_func,
                                        frames=range(slider.valmin,slider.valmax,slider.valstep),
                                        interval=100,
                                        blit=False)
        return fig, ax, anim
    return fig, ax, slider
    
def plot_tulojakauma_lines(f = "rahadata/tuloviidennes.xlsx"):
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df,y_header="vuosi")
    fig,ax = analyze.plot_as_lines(distr,show_trend=False,linewidth=2)
    df.drop(["vuosi"],axis=1,inplace=True)
    utils.set_fig_ax((fig,ax),
                     title="Tulo viidennekset (0-20% huonotuloisimmat, 80-100% korkea tuloisimmat)",
                     xlabel="Vuosi",
                     ylabel="% väestöstä",
                     ylim=(0,df.max().max()+1)
    )
    ax.title.set_size(17)
    ax.grid(True)
    return fig, ax

def plot_tulojakauma_stacked_bars(f = "rahadata/tuloviidennes.xlsx"):
    """ Tulojakauma tulokymmenyksittäin. Tuloluokat  1 : 0-10%, 2 : 10-20% .... 10 : 90-100%"""
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df,y_header="vuosi")
    fig,ax = analyze.plot_as_stacked_bars(distr,show_trend=True)
    utils.set_fig_ax((fig,ax),
                     title="Tulo viidennekset (0-20% huonotuloisimmat, 80-100% korkea tuloisimmat)",
                     xlabel="Vuosi",
                     ylabel="% väestöstä",
                     )
    ax.title.set_size(17)
    return fig, ax

if __name__ == "__main__":
    a = plot_tulojakauma_stacked_bars(f="rahadata/tuloviidennes.xlsx")
    b = plot_tulojakauma_lines(f="rahadata/tuloviidennes.xlsx")
    #b[0].savefig("results/figures/talous_ja_tyollisyys/tuloviidennes.png")
    plt.show()
