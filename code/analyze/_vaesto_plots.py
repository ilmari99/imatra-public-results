import pandas as pd
import matplotlib.pyplot as plt
import cmasher as cmr
import analyze
import utils
from ModelSet import ModelSet
import numpy as np
from matplotlib import animation,transforms
from matplotlib.colors import LinearSegmentedColormap
from _config import *


def text_analyze_age_distribution(f = "vaestodata/ikajakauma_yhdiste_SSS.xlsx", tops=10, time=10):
    df = _get_age_trend(f=f,time=time)
    df.drop(["SSS"],axis=1,inplace=True)
    df = df.T
    df.sort_values(by="slope",ascending=True,inplace=True)
    string = "Viimeisen {} vuoden väestömuutokset:\n".format(time)
    string += "Nopeiten vähenevät iät [hlö/vuosi] (top {}):\n".format(tops)
    for i,r in df.head(tops).iterrows():
        string += f"|{i}| {r['slope']:.2f}|\n"
    #string += df.head(tops).to_string()
    string += "\nNopeiten kasvavat iät [hlö/vuosi] (top {}):\n".format(tops)
    #string += df.tail(tops).reindex(df.tail(tops).index[::-1]).to_string()
    for i,r in df.tail(tops).reindex(df.tail(tops).index[::-1]).iterrows():
        string += f"|{i}| {r['slope']:.2f}|\n"
    print(string,"\n")
    return string

def text_analyze_age_distribution_perc(f = "vaestodata/ikajakauma_muutosmatriisi_SSS.xlsx", tops=10, time=10):
    df = _get_age_trend(f=f,time=time).T
    print(df)
    df.sort_values(by="slope",ascending=True,inplace=True)
    string = "Viimeisen {} vuoden väestömuutokset:\n".format(time)
    string += "Nopeiten vähenevät iät [%] (top {}):\n".format(tops)
    string += df.head(tops).to_string()
    string += "\nNopeiten kasvavat iät [%] (top {}):\n".format(tops)
    string += df.tail(tops).reindex(df.tail(tops).index[::-1]).to_string()
    print(string,"\n")
    return string


def text_analyze_vakiluku(f = "vaestodata/ikajakauma_yhdiste_SSS.xlsx",time=None):
    muutosfile = "vaestodata/ikajakauma_muutosmatriisi_SSS.xlsx"
    df = pd.read_excel(DATA_FOLDER + f)
    df_perc = pd.read_excel(DATA_FOLDER + muutosfile)
    df = df.loc[:,["vuosi","SSS"]]
    df_perc = df_perc.loc[:,["vuosi","SSS"]]
    time = (2021 - time) if time else df.loc[:,"vuosi"].min()
    df = utils.get_rows(df,vuosi=list(range(time,2022)))
    df_perc = utils.get_rows(df_perc,vuosi=list(range(time,2022)))
    distr = ModelSet(df.copy(),y_header="vuosi")
    slope = distr.models["SSS"].params["vuosi"]
    #utils.plot_model(distr.models["SSS"], df.loc[:,"vuosi"], df.loc[:,"SSS"],show=True)
    distr = df_perc.loc[:,["vuosi","SSS"]][df_perc.loc[:,"vuosi"]<=2021]
    out = f"Imatran väkiluku {time}-{df['vuosi'].max()} on vähentynyt keskimäärin {slope:.2f} henkilöä/vuosi.\n"
    out += f"Imatran väkiluku {time}-{df['vuosi'].max()} on vähentynyt keskimäärin {100*distr.loc[:,'SSS'].mean():.2f} % /vuosi."
    return out

def _get_age_trend(f="",time=7):
    df = utils.read_to_df(DATA_FOLDER + f)
    df.rename({c:n for c,n in zip(df.columns,[n.lstrip("0") if n != "000" else "0" for n in df.columns])},axis=1,inplace=True)
    #df = df.loc[:,[c for c in df.columns if not c.startswith("9") and c != "100-"]]
    df = utils.get_rows(df,vuosi = list(range(2021-time+1,2021+1)))
    df.drop(["alue","sukupuoli"],axis=1,inplace=True,errors="ignore")
    #df.drop(["vuosi"],axis=1,inplace=True)
    if "muutos" in f:
        df = df.applymap(lambda x : 100*x if x <100 else x)
    distr = ModelSet(df.copy(),y_header="vuosi")
    trends = pd.DataFrame({k:m.params["vuosi"] for k,m in distr.models.items()},index=["slope"])
    return trends

def _plot_ikajakauma_bars(f="vaestodata/ikajakauma_yhdiste_SSS.xlsx",animate=True):
    """Animaatio, jossa näytetään vuosittainen ikäjakauma 0 - 100+ vuotiaille.
    Tolppien väri kertoo, mihin suuntaan vastaavan ikäluokan määrä on muuttunut viime vuodesta.
    Vihreä: Kasvanut viime vuodesta, Punainen: Vähentynyt viime vuodesta.
    
    Punaiset virherajat tolppien yläpäässä, kertovat, että väkiluku on ennuste (2021 - 2040). Virherajat eivät ole todellisia rajoja.
    """
    df = utils.read_to_df(DATA_FOLDER + f,drop=["alue","sukupuoli","SSS"])
    df.rename({c:n for c,n in zip(df.columns,[n.lstrip("0") if n != "000" else "0" for n in df.columns])},axis=1,inplace=True)
    if "muutos" in f:
        df = df.applymap(lambda x : 100*x if x < 100 else x)
    print(df)
    distr = ModelSet(df.copy(),y_header="vuosi")
    # https://cmasher.readthedocs.io/user/sequential/pepper.html
    cm = plt.cm.get_cmap("cmr.pepper_r")
    if "muutos" in f:
        cm = lambda x : "g" if x>=0 else "r"
    def create_norma(kmax,kmin):
        if "muutos" in f:
            return lambda x : x
        k = kmax-kmin
        y0 = abs(kmin)/k
        return lambda x : k*x + y0
    kmax = 0.5
    kmin = -0.5
    norma = create_norma(kmax,kmin)
    df.drop("vuosi",axis=1,inplace=True)
    if "muutos" in f:
        ylims = (-10,80)
    else:
        ylims = (-1,df.max().max()+1)
    def update2(ax,xy,slpos,err_args):
        prev_row = None
        for i,row in xy.iterrows():
            if prev_row is None:
                prev_row = row
                continue
            if "muutos" not in f:
                k = (row["y"]-prev_row["y"])/prev_row["y"]
            else:
                k = row["y"]
            scaled = norma(k)
            c = cm(scaled)
            eargs = {}
            if slpos >= 2022 and "muutos" not in f:
                eargs = {"yerr":8,"ecolor":"red","capsize":5}
                if err_args:
                    eargs = {"yerr":err_args["yerr"][i],"ecolor":err_args["ecolor"],"capsize":err_args["capsize"]}
            ax.bar(row["x"],row["y"],align="edge",color=c,**eargs)
        ax.grid(True,axis="y")
        ax.set_title("Imatran ikäjakauma vuosittain, HUOM. Virheet eivät ole oikein, vaan ne kertovat ennustusten alkamisesta")
        ax.set_ylabel("Lukumäärä")
        ax.set_xlabel("Ikä")
        ax.set_ylim(*ylims)
        #ax.legend()
    fig, ax, slider = analyze.plot_slider_fig(distr,slkwargs={"valstep":1},slider_update_func=update2)
    ax.set_facecolor("grey")
    fig.set_size_inches(*FIG_SIZE)
    if animate:
        def animate_func(i):
            slider.set_val(i)
        anim = animation.FuncAnimation(fig,
                                        animate_func,
                                        frames=range(slider.valmin,slider.valmax,slider.valstep),
                                        interval=100,
                                        blit=False)
        #anim.save("results/animations/ikajakauma_muutokset.gif",writer="imagemagick")
        return fig, ax, anim
    return fig, ax, slider

def _plot_current_age_trend(percent = True,tops=10,time=7,f=None):
    f = f if f else "vaestodata/ikajakauma_yhdiste_SSS.xlsx"
    if percent:
        f = "vaestodata/ikajakauma_muutosmatriisi_SSS.xlsx"
    df = _get_age_trend(f=f,time=time)
    if not percent:
        df.drop(["SSS"],axis=1,inplace=True)
    fig, ax = plt.subplots()
    ages = df.columns
    vals = df.values.flatten()
    ax.set_xticks(range(len(ages)))
    ax.set_xticklabels(ages,rotation=-60)
    for a,v in zip(ages,vals):
        ax.bar(a,v,color="g" if float(v)>0 else "r")
    utils.set_fig_ax((fig,ax),
                     title=f"Viimeisen {time} vuoden ajalta keskimääräinen vuosittainen väestömuutos iän mukaan" + (" (%)" if percent else " (hlö)"),
                     xlabel="Ikä",
                     ylabel=f"Muutos {'(%)' if percent else '(hlö)'}",
                     )
    ax.title.set_size(16)
    ax.set_xticks(range(0,len(ages),5))
    return fig, ax

def _plot_muutot_lines(f = "",tops=5,title="",total=True):
    if not f:
        raise Exception("No file given")
    df = pd.read_excel(DATA_FOLDER + f)
    drops = ["sukupuoli","Tulo"]
    if not total:
        drops.append("KOKO MAA")
    df.drop(drops,axis=1,inplace=True)
    total_df = df.sum(axis=0)
    top = total_df.sort_values(ascending=False).index[:tops+1]
    distr = ModelSet(df.loc[:,top],y_header="vuosi")
    fig, ax = analyze.plot_as_lines(distr)
    utils.value_to_line_end(ax,df,top[1],add_point=True,offset=(0.1,0.1))
    utils.set_fig_ax((fig,ax),
                     title=title,
                     xlabel="Vuosi",
                     ylabel="Muuttojen määrä",
                     )
    return fig,ax

def plot_vakiluku_yhdiste(f = "vaestodata/ikajakauma_yhdiste_SSS.xlsx",fig_ax=(None,None),color="b"):
    df = pd.read_excel(DATA_FOLDER + f).loc[:,["vuosi","SSS"]]
    if None in fig_ax:
        fig_ax = plt.subplots()
        fig_ax[0].set_size_inches(*FIG_SIZE)
        fig_ax[1].set_ylim(0,df.loc[:,"SSS"].max()+1)
        fig_ax[1].set_xlim(df.loc[:,"vuosi"].min()-1,df.loc[:,"vuosi"].max()+1)
    ax = fig_ax[1]
    fig = fig_ax[0]
    ax.plot([2021,2021],[0,df.loc[:,"SSS"].max()+1],color="r",label=None)
    actual = df.loc[df.loc[:,"vuosi"]<=2021,"SSS"]
    ax.plot(df.loc[:,"vuosi"],df.loc[:,"SSS"],color=color,linestyle="dashed")
    label = "Väkiluku"
    title = f"Imatran väkiluku {df['vuosi'].min()}-{df['vuosi'].max()}"
    if "1" in f:
        label = "Miehet"
    elif "2" in f:
        label = "Naiset"
    if label != "Väkiluku":
        title = f"Imatran väkiluku sukupuolittain {df['vuosi'].min()}-{df['vuosi'].max()}"
    ax.plot(df.loc[df.loc[:,"vuosi"]<=2021,"vuosi"],actual,color=color,label=label)
    utils.set_fig_ax((fig,ax),
                     title=title,
                     xlabel="Vuosi",
                     ylabel="Väkiluku",
                     )
    return fig,ax

def plot_vakiluku_muutos_yhdiste(f = "vaestodata/ikajakauma_muutosmatriisi_SSS.xlsx"):
    """Väkiluvun muutos edelliseen vuoteen 1972-2021"""
    df = pd.read_excel(DATA_FOLDER + f)
    fig,ax = plt.subplots()
    df = df.applymap(lambda x : 100*x if x < 100 else x)
    ax.plot([2021,2021],[-100,100],color="r")
    ax.plot(df.loc[:,"vuosi"],df.loc[:,"SSS"],color="b",label="Ennuste",linestyle="dashed")
    ax.plot(df.loc[df.loc[:,"vuosi"]<=2021,"vuosi"],df.loc[df.loc[:,"vuosi"]<=2021,"SSS"],color="b",label="Toteutunut")
    ax.plot([df.loc[:,"vuosi"].min()-1,df.loc[:,"vuosi"].max()+1],[0,0],color="green")
    utils.set_fig_ax((fig,ax),
                     title=f"Imatran väkiluvun muutos {df['vuosi'].min()}-{df['vuosi'].max()}",
                     xlabel="Vuosi",
                     ylabel="Muutos edellisestä vuodesta [%]",
                     ylim=(df.loc[:,"SSS"].min()-0.1,df.loc[:,"SSS"].max()+0.1),
                     xlim=(df.loc[:,"vuosi"].min()-1,df.loc[:,"vuosi"].max()+1),
                     ylabel_coord=(-0.03,1)
                     )
    return fig, ax

def plot_vakiluku_ikaryhmittain_lines(f = "vaestodata/ikajakauma_2kymmenittäin.xlsx"):
    """ Imatran väkiluku 20 vuoden ikäryhmittain """
    df = pd.read_excel(DATA_FOLDER + f)
    df_act = df.loc[df.loc[:,"vuosi"]<=2021]
    df_pred = df.loc[df.loc[:,"vuosi"]>=2021]
    distr = ModelSet(df_act,y_header="vuosi")
    fig, ax = analyze.plot_as_lines(distr,show_trend=False)
    utils.set_fig_ax((fig,ax),
                     title=f"Imatran väkiluku ikäryhmittain {df['vuosi'].min()}-{df['vuosi'].max()}",
                     xlabel="Vuosi",
                     ylabel="Väkiluku",
                     xlim=(df.loc[:,"vuosi"].min()-1,df.loc[:,"vuosi"].max()+1),
                     ylim=(0,df.max().max()+1),
                     )
    fig, ax = analyze.plot_as_lines(ModelSet(df_pred,y_header="vuosi"),show_trend=False,fig_ax=(fig,ax),linestyle="dashed")
    ax.set_xticks(range(df.loc[:,"vuosi"].min(),df.loc[:,"vuosi"].max()+1,5))
    ax.set_xticklabels(range(df.loc[:,"vuosi"].min(),df.loc[:,"vuosi"].max()+1,5))
    ax.plot([2021,2021],[0,df.max().max()],color="r")
    return fig, ax    

def _plot_muutot_stacked_bars(f ="",tops=5,title="",total=True):
    if not f:
        raise Exception("No file given")
    df = pd.read_excel(DATA_FOLDER + f)
    drops = ["sukupuoli","Tulo"]
    if not total:
        drops.append("KOKO MAA")
    df.drop(drops,axis=1,inplace=True)
    total_df = df.sum(axis=0)
    top = total_df.sort_values(ascending=False).index[:tops+1]
    distr = ModelSet(df.loc[:,top],y_header="vuosi")
    fig, ax = analyze.plot_as_stacked_bars(distr)
    utils.set_fig_ax((fig,ax),
                     title=title,
                     xlabel="Vuosi",
                     ylabel="Muuttojen määrä",
                     )
    return fig,ax

def plot_2021_sukupuolittain_perc(vuosi=2021):
    w = utils.read_to_df(DATA_FOLDER+"vaestodata/ikajakauma_2.xlsx",drop=["sukupuoli","alue"])
    m = utils.read_to_df(DATA_FOLDER+"vaestodata/ikajakauma_1.xlsx",drop=["sukupuoli","alue"])
    s = utils.read_to_df(DATA_FOLDER+"vaestodata/ikajakauma_yhdiste_SSS.xlsx",drop=["sukupuoli","alue"])
    w = utils.get_rows(w,vuosi=[vuosi])
    m = utils.get_rows(m,vuosi=[vuosi])
    s = utils.get_rows(s,vuosi=[vuosi])
    wp = w/s
    mp = m/s
    sp = s/s
    pp = pd.concat([wp,mp,sp],axis=0)
    pp.rename({c:n for c,n in zip(pp.columns,[n.lstrip("0").rstrip("-") if n != "000" else "0" for n in pp.columns])},axis=1,inplace=True)
    pp = pp.T
    pp.columns = ["Naiset","Miehet","Yht"]
    pp.insert(0,"ikä",pp.index)
    pp.drop(["vuosi","SSS"],axis=0,inplace=True)
    pp.reset_index(drop=True,inplace=True)
    fig,ax = plt.subplots()
    ax.set_xticks(range(0,len(pp.index),5))
    print(pp)
    pp = pp.applymap(lambda x : 100*x if isinstance(x,float) and x <= 1 else x)
    ax.bar(pp.loc[:,"ikä"],pp.loc[:,"Miehet"],color="r",label="Miehet")
    ax.plot([int(pp.loc[:,"ikä"].min()),int(pp.loc[:,"ikä"].max())],[50,50],color="b",label="50%")
    utils.set_fig_ax((fig,ax),
                     title="Miesten osuus kokonaisväestöstä vuonna 2021 jaoteltuna iättäin",
                     xlabel="Ikä",
                     ylabel="Miesten osuus (%)",
                     ylim=(0,100),
                     )
    return fig,ax

def plot_2021_ikäpyramidi(vuosi=2021):
    w = utils.read_to_df(DATA_FOLDER+"vaestodata/ikajakauma_2.xlsx",drop=["sukupuoli","alue","SSS"])
    m = utils.read_to_df(DATA_FOLDER+"vaestodata/ikajakauma_1.xlsx",drop=["sukupuoli","alue","SSS"])
    w = utils.get_rows(w,vuosi=[vuosi]).drop("vuosi",axis=1)
    m = utils.get_rows(m,vuosi=[vuosi]).drop("vuosi",axis=1)
    w.rename({c:int(n) for c,n in zip(w.columns,[n.lstrip("0").rstrip("-") if n != "000" else "0" for n in w.columns])},axis=1,inplace=True)
    m.rename({c:int(n) for c,n in zip(m.columns,[n.lstrip("0").rstrip("-") if n != "000" else "0" for n in m.columns])},axis=1,inplace=True)
    fig,ax = plt.subplots()
    base = plt.gca().transData
    trans = transforms.Affine2D().rotate_deg(90)
    ax.bar(w.columns.to_list(),w.values.flatten(),transform=trans + base,label="Naiset",color="r")
    ax.bar(m.columns.to_list(),[-_ for _ in m.values.flatten()],transform=trans+base,label="Miehet",color="b")
    utils.set_fig_ax((fig,ax),
                     title="Imatran ikäpyramidi sukupuolittain vuonna 2021",
                     xlabel="Väkiluku",
                     ylabel="Ikä",
                     )
    ax.grid(True,axis="x")
    return fig,ax
    
    

def plot_current_age_trend_perc(tops=10,time=7):
    """ Kuvaajassa näkyy kunkin ikäluokan  7 vuoden keskimääräinen vuosittainen muutos suhteessa viime vuoden määrään [%/vuosi].
    """
    return _plot_current_age_trend(percent=True,tops=tops,time=time)

def plot_current_age_trend(tops=10,time=7):
    """ Kuvaajassa näkyy kunkin ikäluokan 7 vuoden keskimääräinen vuosittainen muutos [hlö/vuosi]."""
    return _plot_current_age_trend(percent=False,tops=tops,time=time)

def plot_sisaanmuutot_total_stacked_bars(f = "vaestodata/sisaan_muutot_SSS.xlsx",tops=5,total=True):
    """ Kuvaaja näyttää 5 suurinta kuntaa, joista muutot tulevat.
    Aineiston kantalukuna on henkilön MUUTTO, ei siis välttämättä pysyvä muutto.    
    """
    return _plot_muutot_stacked_bars(f,tops=tops,title="Muutot Imatralle",total=total)

def plot_poismuutot_total_stacked_bars(f = "vaestodata/pois_muutot_SSS.xlsx",tops=5,total=True):
    """ Kuvaaja näyttää 5 suurinta kuntaa, mihin muutot suuntautuvat.
    Aineiston kantalukuna on henkilön MUUTTO, ei siis välttämättä pysyvä muutto. 
    """
    return _plot_muutot_stacked_bars(f,tops=tops,title="Muutot POIS Imatralta",total=total)

def plot_poismuutot_stacked_bars():
    """ Kuvaaja näyttää 5 suurinta kuntaa, mihin muutot suuntautuvat."""
    return plot_poismuutot_total_stacked_bars(total=False)

def plot_sisaanmuutot_stacked_bars():
    """ Kuvaaja näyttää 5 suurinta kuntaa, joista muutot tulevat."""
    return plot_sisaanmuutot_total_stacked_bars(total=False)

def plot_sisaanmuutot_total_lines(f = "vaestodata/sisaan_muutot_SSS.xlsx",
                      tops=5,total=True):
    """ top 5 kuntaa, joista muutot tulevat."""
    return _plot_muutot_lines(f,tops,"Muutot Imatralle",total=total)

def plot_poismuutot_total_lines(f = "vaestodata/pois_muutot_SSS.xlsx",
                      tops=5,total=True):
    """ Top 5 kuntaa, joihin muutot suuntautuvat."""
    return _plot_muutot_lines(f,tops,"Muutot POIS Imatralta",total=total)

def plot_poismuutot_lines(f="vaestodata/pois_muutot_SSS.xlsx",tops=5):
    """ Top 5 kuntaa, joihin muutot suuntautuvat."""
    return plot_poismuutot_total_lines(f,tops,total=False)

def plot_sisaanmuutot_lines(f="vaestodata/sisaan_muutot_SSS.xlsx",tops=5):
    """ Top 5 kuntaa, joista muutot tulevat."""
    return plot_sisaanmuutot_total_lines(f,tops,total=False)

def plot_vakiluku_sukupuolittain():
    a = plot_vakiluku_yhdiste(f="vaestodata/ikajakauma_2.xlsx",color="r")
    a = plot_vakiluku_yhdiste(f="vaestodata/ikajakauma_1.xlsx",fig_ax=a)
    return a


if __name__ == "__main__":
    #a = plot_current_age_trend()
    #a[0].savefig("results/figures/current_age_trend.png")
    utils.save_figure(plot_current_age_trend)
    plt.show()