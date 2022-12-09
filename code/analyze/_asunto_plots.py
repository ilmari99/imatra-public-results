""" This file is for plotting data from .data/vaestodata folder.
"""
import pandas as pd
from ModelSet import ModelSet
import matplotlib.pyplot as plt
import cmasher as cmr
import analyze
import utils
from matplotlib import animation
from _config import FIG_SIZE, DATA_FOLDER
import numpy as np

def _plot_asuntokunnat_bars(f = "asuntodata/asunto_henkilot.xlsx", animate=True):
    """ Asuntokuntien määrä yhteensä vuosittain, jaoteltuna asuntokuntien kokoihin.
    """
    df = utils.read_to_df(DATA_FOLDER + f)          # Read alread fetched data from excel to dataframe
    distr = ModelSet(df,y_header="vuosi")           # Create a ModelSet object from the dataframe
    cm = plt.cm.get_cmap("cmr.pepper_r")            # Get a colormap
    k_scaled = utils.normed_dict([m.params[0] for m in distr.models.values()])  # Scale the slope of the fitted lines
                                                                                # to 0-1 for coloring the bars
    # Create a function for updating the plot
    def update2(ax,xy,slpos,err_args):
        for i,row in xy.iterrows():
            scaled = k_scaled[distr.models[row.loc["label"]].params[0]]         # Get the scaled slope of the fitted line
            c = cm(scaled)                                 # Get the color for the bar
            # The err_args dictionary is not empty if the year selected with the slider is not a measured year
            eargs = {}
            if err_args:
                eargs = {"yerr":err_args["yerr"][i],"ecolor":err_args["ecolor"],"capsize":err_args["capsize"]}
            ax.bar(row["x"],row["y"],align="edge",color=c,**eargs)  # Plot the bar
        ax.grid(True)
        ax.set_title("Asuntokuntien koko jakauma vuosittain")
        ax.set_ylabel("Asuntokuntien määrä")
        ax.set_xlabel("Asunnon koko")
        ax.legend()
        ax.set_ylim(-1,df.max().max()+1)                             # Set the y-axis limits for a better illustration
    fig, ax,slider = analyze.plot_slider_fig(distr,
                                             slkwargs={"valstep":1},
                                             slider_update_func = update2) # Create the plot
    fig.set_size_inches(*FIG_SIZE)
    # If animate is True, automatically change the slider value to the next year
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

def _plot_asuntokunnat_omakotitalo_bars(f = "asuntodata/omakoti_henkilot.xlsx",animate=True):
    """ Omakotitalossa asuvien asuntokuntien määrä jaoteltuna koottain, ja vuosittain. """
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
        ax.set_title("Omakotitalossa asuvien asuntokuntien koko jakauma")
        ax.set_ylabel("Asuntokuntien määrä")
        ax.set_xlabel("Asuntokunnan koko")
        ax.legend()
        ax.set_ylim(-1,df.max().max()+1)
    fig, ax,slider = analyze.plot_slider_fig(distr,slkwargs={"valstep":1},slider_update_func = update2)
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

def _plot_asuntokunnat_kerrostalo_bars(f = "asuntodata/kerrostalo_henkilot.xlsx", animate=True):
    """ Kerrostalossa asuvien asuntokuntien määrä jaoteltuna koottain, ja vuosittain. """
    df = utils.read_to_df(DATA_FOLDER + f)      # Read alread fetched data from excel to dataframe
    distr = ModelSet(df,y_header="vuosi")       # Create a ModelSet object from the dataframe
    cm = plt.cm.get_cmap("cmr.pepper_r")        # Get a colormap
    k_scaled = utils.normed_dict([m.params[0] for m in distr.models.values()])  # Scale the slope of the fitted lines for coloring
    def update2(ax,xy,slpos,err_args):
        for i,row in xy.iterrows():
            scaled = k_scaled[distr.models[row.loc["label"]].params[0]]
            c = cm(scaled)
            eargs = {}
            if err_args:
                eargs = {"yerr":err_args["yerr"][i],"ecolor":err_args["ecolor"],"capsize":err_args["capsize"]}
            ax.bar(row["x"],row["y"],align="edge",color=c,**eargs)
        ax.grid(True)
        ax.set_title("Kerrostaloissa asuvien asuntokuntien koko jakauma")
        ax.set_ylabel("Asuntokuntien määrä")
        ax.set_xlabel("Asuntokunnan koko")
        ax.legend()
        ax.set_ylim(-1,df.max().max()+1)
    fig, ax,slider = analyze.plot_slider_fig(distr,slkwargs={"valstep":1},slider_update_func = update2)
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

def _plot_vakiluku_asuntotyypeittain_bars(f = "asuntodata/mahd_asukkaat_asuntotyypeittäin.xlsx",as_percent=False, animate=True):
    """ Ihmisten määrä jaoteltuna asuntotyypeittäin (approksimaatio, koska suurempia asuntokuntia kuin 7 ei ole jaoteltu)."""
    df = utils.read_to_df(DATA_FOLDER + f)
    if as_percent:
        cols = df.columns
        for i,r in df.iterrows():
            rowsum = sum(r.iloc[1:])
            for c in cols:
                if c != "vuosi":
                    df.loc[i,c] = (df.loc[i,c]/rowsum)*100
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
        ax.set_title("Asuntojen määrä*koko jaoteltuna tyypeittäin")
        ax.set_ylabel("Asuntojen määrä")
        ax.set_xlabel("Asunnon koko")
        ax.set_ylim(-1,df.max().max()+1)
        ax.legend()
    fig, ax,slider = analyze.plot_slider_fig(distr,slkwargs={"valstep":1},slider_update_func = update2)
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

def plot_asuntokunnat_lines(f = "asuntodata/asunto_henkilot.xlsx"):
    """ Asuntokuntien määrä jaoteltuna koottain, ja vuosittain.
    """
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df,y_header="vuosi")
    fig,ax = analyze.plot_as_lines(distr,show_trend=False)
    utils.set_fig_ax((fig,ax),
                title="Asuntokuntien määrä eriteltynä koottain",
                xlabel="Vuosi",
                ylabel="Asuntokuntien määrä",
                )
    text_analysis_asuntokunnat(f)
    return fig, ax

def plot_asuntokunnat_stacked_bars(f = "asuntodata/asunto_henkilot.xlsx"):
    """ Asuntokuntien määrä jaoteltuna koottain, ja vuosittain. """
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df,y_header="vuosi")
    fig, ax = analyze.plot_as_stacked_bars(distr,show_trend=True)
    utils.set_fig_ax((fig,ax),
                    title="Asuntokuntien koko jakauma vuosittain",
                    xlabel="Vuosi",
                    ylabel="Asuntokuntien määrä",
                    )
    text_analysis_asuntokunnat(f)
    return fig, ax

def text_analysis_asuntokunnat(f = "asuntodata/asunto_henkilot.xlsx"):
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df.copy(),y_header="vuosi")
    aika = (int(df.loc[:,"vuosi"].min()),int(df.loc[:,"vuosi"].max()))
    out = f"Asuntokuntien kokonaismäärä vuosina {aika} hajotettuna koottain."
    k_taul = pd.DataFrame(columns = ["Keskimääräinen muutos [hlö/vuosi]"],
                          data=[m.params[1] for m in distr.models.values()],
                          index = [k for k in distr.models.keys()])
    out += f"\n{k_taul}\n"
    return out

def plot_asuntokunnat_kerrostalo_lines(f = "asuntodata/kerrostalo_henkilot.xlsx"):
    """ Kerrostalossa asuvien asuntokuntien määrä jaoteltuna koottain, ja vuosittain. """
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df,y_header="vuosi")
    fig,ax = analyze.plot_as_lines(distr,show_trend=False)
    utils.set_fig_ax((fig,ax),
                     title="Kerrostalossa asuvien asuntokuntien määrä vuosittain",
                     xlabel="Vuosi",
                     ylabel="Asuntokuntien määrä",
                     )
    return fig, ax

def plot_asuntokunnat_kerrostalo_stacked_bars(f = "asuntodata/kerrostalo_henkilot.xlsx"):
    """ Kerrostalossa asuvien asuntokuntien määrä jaoteltuna koottain, ja vuosittain. """
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df,y_header="vuosi")
    fig, ax = analyze.plot_as_stacked_bars(distr,show_trend=False)
    utils.set_fig_ax((fig,ax),
                     title="Kerrostalossa asuvien asuntokuntien määrä vuosittain",
                     xlabel="Vuosi",
                     ylabel="Asuntokuntien määrä",
                     )
    return fig, ax
    

def plot_asuntokunnat_omakotitalo_lines(f = "asuntodata/omakoti_henkilot.xlsx"):
    """ Omakotitalossa asuvien asuntokuntien määrä jaoteltuna koottain, ja vuosittain. """
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df,y_header="vuosi")
    fig,ax = analyze.plot_as_lines(distr,show_trend=False)
    utils.set_fig_ax((fig,ax),
                     title="Omakotitalossa asuvien asuntokuntien määrä vuosittain",
                     xlabel="Vuosi",
                     ylabel="Asuntokuntien määrä",
                     )
    return fig, ax

def plot_asuntokunnat_omakotitalo_stacked_bars(f = "asuntodata/omakoti_henkilot.xlsx"):
    """ Omakotitalossa asuvien asuntokuntien määrä jaoteltuna koottain, ja vuosittain. """
    df = utils.read_to_df(DATA_FOLDER + f)
    distr = ModelSet(df,y_header="vuosi")
    fig, ax = analyze.plot_as_stacked_bars(distr,show_trend=False)
    utils.set_fig_ax((fig,ax),
                     title="Omakotitalossa asuvien asuntokuntien määrä vuosittain",
                     xlabel="Vuosi",
                     ylabel="Asuntokuntien määrä",
                     )
    return fig, ax


def plot_vakiluku_asuntotyypeittain_lines(f="asuntodata/mahd_asukkaat_asuntotyypeittäin.xlsx",as_percent=False):
    """ Ihmisten määrä jaoteltuna asuntotyypeittäin (approksimaatio, koska suurempia asuntokuntia kuin 7 ei ole jaoteltu)."""
    df = utils.read_to_df(DATA_FOLDER + f)
    if as_percent:
        cols = df.columns
        for i,r in df.iterrows():
            rowsum = sum(r.iloc[1:])
            for c in cols:
                if c != "vuosi":
                    df.loc[i,c] = (df.loc[i,c]/rowsum)*100
    distr = ModelSet(df,y_header="vuosi")
    fig, ax = analyze.plot_as_lines(distr,show_trend=True)
    df.drop(columns=["vuosi"],inplace=True)
    utils.set_fig_ax((fig,ax),
                     title="Eri asuntotyypeissä asuvien ihmisten määrä" + (" (% väkiluvusta)" if as_percent else ""),
                     xlabel="Vuosi",
                     ylabel="Ihmisten määrä" + (" (%)" if as_percent else ""),
                     ylim=(0,df.max().max()+1)
                     )
    if as_percent:
        ax.title.set_size(17)
    return fig, ax

def plot_vakiluku_asuntotyypeittain_stacked_bars(f = "asuntodata/mahd_asukkaat_asuntotyypeittäin.xlsx", as_percent=False):
    """ Ihmisten määrä jaoteltuna asuntotyypeittäin (approksimaatio, koska suurempia asuntokuntia kuin 7 ei ole jaoteltu)."""
    df = utils.read_to_df(DATA_FOLDER + f)
    if as_percent:
        cols = df.columns
        for i,r in df.iterrows():
            rowsum = sum(r.iloc[1:])
            for c in cols:
                if c != "vuosi":
                    df.loc[i,c] = (df.loc[i,c]/rowsum)*100
    distr = ModelSet(df,y_header="vuosi")
    fig, ax = analyze.plot_as_stacked_bars(distr,show_trend=False)
    utils.set_fig_ax((fig,ax),
                     title="Väkiluku jaoteltuna asuntotyypeittäin",
                     xlabel="Vuosi",
                     ylabel="Ihmisten määrä" if not as_percent else "Ihmisten määrä (% väkiluvusta)",
                     ylabel_coord=(-0.03,1)
                     )
    return fig, ax


def plot_asuntokunnat_stacked_bars(f = "asuntodata/asunto_henkilot.xlsx", as_percent=False):
    """ Plot the total amount of households, broken down by size of the household """
    df = utils.read_to_df(DATA_FOLDER + f)
    if as_percent:
        cols = df.columns
        for i,r in df.iterrows():
            rowsum = sum(r.iloc[1:])
            for c in cols:
                if c != "vuosi":
                    df.loc[i,c] = (df.loc[i,c]/rowsum)*100
    distr = ModelSet(df,y_header="vuosi")
    fig, ax = analyze.plot_as_stacked_bars(distr)
    utils.set_fig_ax((fig,ax),
                     title="Asuntokuntien määrä vuosittain" if not as_percent else "Asuntokuntien määrä vuosittain prosentteina",
                     xlabel="Vuosi",
                     ylabel="Asuntokuntien määrä"+(" (%)" if as_percent else "")
                     )
    return fig, ax

def _plot_asuntokunnat_vanhin_lines(f="asuntodata/asuntokunnan_vanhin_1.xlsx",show_trend=False):
    sz = f.split("/")[-1].split(".")[0][-1]
    titles = {"1":"Yhden hengen asuntokuntien määrä, asuntokunnan vanhimman mukaan",
              "2":"Kahden hengen asuntokuntien määrä, asuntokunnan vanhimman mukaan",
              "3":"Kolmen hengen asuntokuntien määrä, asuntokunnan vanhimman mukaan",
              "4":"Yli kolmen hengen asuntokuntien määrä, asuntokunnan vanhimman mukaan"}
    df = utils.read_to_df(DATA_FOLDER + f,drop=["alue","talo","koko","SSS"])
    print(df)
    distr = ModelSet(df,y_header="vuosi")
    df.drop("vuosi",axis=1,inplace=True)
    fig, ax = analyze.plot_as_lines(distr,show_trend=show_trend,linewidth=2)
    utils.set_fig_ax((fig,ax),
                     title=titles[sz],
                     xlabel="Vuosi",
                     ylabel="Asuntokuntien määrä",
                     ylim=(0,df.max().max()+1),
                     ylabel_coord=(-0.033,1.05)
                     )
    ax.title.set_size(18)
    ax.grid(True,axis="both")
    print(text_analyze_asuntokunnat_vanhin(f))
    return fig, ax

def _plot_asuntokunnat_vanhin_stacked_bars(f="asuntodata/asuntokunnan_vanhin_1.xlsx",show_trend=False):
    sz = f.split("/")[-1].split(".")[0][-1]
    titles = {"1":"Yhden hengen asuntokuntien määrä, asuntokunnan vanhimman mukaan",
              "2":"Kahden hengen asuntokuntien määrä, asuntokunnan vanhimman mukaan",
              "3":"Kolmen hengen asuntokuntien määrä, asuntokunnan vanhimman mukaan",
              "4":"Yli kolmen hengen asuntokuntien määrä, asuntokunnan vanhimman mukaan"}
    df = utils.read_to_df(DATA_FOLDER + f,drop=["alue","talo","koko","SSS"])
    distr = ModelSet(df,y_header="vuosi")
    fig, ax = analyze.plot_as_stacked_bars(distr,show_trend=show_trend)
    fig, ax = utils.set_fig_ax((fig,ax),
                               title=titles[sz],
                               xlabel="Vuosi",
                               ylabel="Asuntokuntien määrä",
                               ylim=(0,df.max().max()+1))
    return fig, ax

def text_analyze_asuntokunnat_vanhin(f="asuntodata/asuntokunnan_vanhin_1.xlsx"):
    df = utils.read_to_df(DATA_FOLDER + f,drop=["alue","talo","koko"])
    sz = f.split("/")[-1].split(".")[0][-1]
    if sz == "4":
        sz = "4+"
    distr = ModelSet(df.copy(),y_header="vuosi")
    latest = utils.get_rows(df,vuosi=[df["vuosi"].max()])
    out = f"Vuonna {latest['vuosi'].values[0]}: {sz} hengen asuntokuntien määrä oli {latest['SSS'].values[0]}.\n"
    latest_perc = latest.applymap(lambda x: round(x/latest['SSS'].sum()*100,2))
    latest_perc.drop(["vuosi","SSS"],axis=1,inplace=True)
    out += f"{sz} hengen asuntokunnissa vanhimman henkilön ikä oli jakautunut seuraavasti:\n"
    out += f"|Ikä|% asuntokunnista|\n|---|---|\n"
    for c in latest_perc.columns:
        out += f"|{c}| {latest_perc[c].values[0]}|\n"
    return out

def plot_tyhjat_asunnot_lines(f="asuntodata/Imatra_asunnot_kayttotilanne.xlsx",
                              as_percent=False,):
    df = utils.read_to_df(DATA_FOLDER + f,drop=["alue","talo","koko","SSS","Vakinaisesti asuttu"])
    if as_percent:
        df["Ei vakinaisesti asuttu"] = (df["Ei vakinaisesti asuttu"]/df["Kaikki asunnot"])*100
    df.drop("Kaikki asunnot",axis=1,inplace=True)
    distr = ModelSet(df,y_header="vuosi")
    fig, ax = analyze.plot_as_lines(distr,linewidth=2,show_trend=False)
    fig.set_size_inches(*FIG_SIZE)
    utils.value_to_line_end(ax,
                            df,
                            y_header="Ei vakinaisesti asuttu",
                            text_kwargs={"color":"blue"},
                            offset=(0,40),
                            add_point=True,
                            point_kwargs={"color":"blue","s":40})
    utils.set_fig_ax((fig,ax),
            title="Tyhjien asuntojen määrä vuosittain" + (" (% kaikista asunnoista)" if as_percent else ""),
            xlabel="Vuosi",
            ylabel="Tyhjien asuntojen määrä" + (" (%)" if as_percent else ""),
            ylim=(0,df["Ei vakinaisesti asuttu"].max().max()+0.1*df["Ei vakinaisesti asuttu"].max().max()),
            )
    ax.grid(True,axis="both")
    return fig, ax

def plot_vakiluku_asuntotyypeittain_perc_lines():
    return plot_vakiluku_asuntotyypeittain_lines(as_percent=True)

def plot_asuntokunnat_perc_stacked_bars(f = "asuntodata/asunto_henkilot.xlsx"):
    """ Kertoo kuinka monta prosenttia asuntokunnista, on minkäkin kokoisia."""
    return plot_asuntokunnat_stacked_bars(f,as_percent=True)

def plot_vakiluku_asuntotyypeittain_perc_stacked_bars(f = "asuntodata/mahd_asukkaat_asuntotyypeittäin.xlsx"):
    """ Kertoo kuinka monta prosenttia väkiluvusta, asuu minkälaisissa asunnoissa."""
    return plot_vakiluku_asuntotyypeittain_stacked_bars(f,as_percent=True)

def plot_asuntokunnat_vanhin_1_lines(f="asuntodata/asuntokunnan_vanhin_1.xlsx"):
    return _plot_asuntokunnat_vanhin_lines(f)
def plot_asuntokunnat_vanhin_2_lines(f="asuntodata/asuntokunnan_vanhin_2.xlsx"):
    return _plot_asuntokunnat_vanhin_lines(f)
def plot_asuntokunnat_vanhin_3_lines(f="asuntodata/asuntokunnan_vanhin_3.xlsx"):
    return _plot_asuntokunnat_vanhin_lines(f)
def plot_asuntokunnat_vanhin_4_lines(f="asuntodata/asuntokunnan_vanhin_4.xlsx"):
    return _plot_asuntokunnat_vanhin_lines(f)
    

if __name__ == "__main__":
    #a = plot_asuntokunnat_vanhin_stacked_bars(f = "asuntodata/asuntokunnan_vanhin_1.xlsx")
    #a[0].savefig("results/figures/asuntokunnan_vanhin_1.png")
    #print(text_analyze_asuntokunnat_vanhin(f = "asuntodata/asuntokunnan_vanhin_1.xlsx"))
    #a[0].savefig("results/figures/asuminen/tyhjat_asunnot_lines.png")
    utils.save_figure(plot_vakiluku_asuntotyypeittain_perc_lines)
    plt.show()
    