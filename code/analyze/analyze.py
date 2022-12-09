import pandas as pd
import sys  ###
import os
import matplotlib.pyplot as plt
import matplotlib
import cmasher as cmr
# Add the main directory to path to use packages from 'code' directory
#sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils import concat_clean_separate,get_columns_that_match_regex,get_columns,get_rows,plot_model
import PostalArea as pa
from ModelSet import ModelSet
import statsmodels.api as sm

def fit_model(df,y_header="ra_asrak",add_constant=True):
    """Create an OLS model. Input is a dataframe with the dependent variables and the independent variables.
    y_header is the name of the dependent variable.
    """
    df = df.copy()
    y = df.pop(y_header)
    x,y = concat_clean_separate(df,y)
    if add_constant:
        x = sm.add_constant(x)
    model = sm.OLS(y,x).fit()
    return model

def plot_slider_fig(modelSet,alpha=0.05, slkwargs={}, slider_update_func=None,iv_fun=lambda x : int(x)):
    # Create the distribution plot and return the figure, axes and the bar container
    fig,ax = plt.subplots()
    plt.subplots_adjust(bottom=0.22)
    # Get the data for the plot
    og = modelSet.get_row_or_prediction([iv_fun(2010)])
    # Remove the independent variable column from the dataframe
    og.drop(modelSet.y_header,axis=1,inplace=True)
    # Set the x-axis labels
    xt = list(range(len(og.columns)))
    plt.xticks(xt,list(og.columns),rotation=-60)
    # Default values for the slider if not specified
    default_slkwargs = {"ax":plt.axes([0.2,0.1,0.65,0.03]),
        "valmin":modelSet.df.loc[:,modelSet.y_header].min(),
        "valmax":modelSet.df.loc[:,modelSet.y_header].max(),
        "label":"slider",
        }
    for k in default_slkwargs:
        if k not in slkwargs:
            slkwargs[k] = default_slkwargs[k]
    # Create slider object
    slider = plt.Slider(
        **slkwargs
    )
    # the default callback function, that is called when the slider is moved
    # slider_update_func is a custom function that is ALSO called when the slider is moved
    def update(slpos):
        val = iv_fun(slpos)       # Get the value of the slider: REQUIRED AS FIRTS POSITIONAL ARGUMENT
        # Get the predictions or actual values
        df = modelSet.get_row_or_prediction([val],get_ci=True,alpha=alpha)
        # Remove the independent variable column from the dataframe
        df.drop(modelSet.y_header,axis=1,inplace=True)
        bar_labels = list(df.columns)
        # Set the axes
        x = list(range(len(df.columns)))
        y = df.values.tolist()[0]
        err_args = {}
        if df.shape[0] > 1:
            yerr = df.iloc[1,:] - df.iloc[0,:]      # Prediction error is symmetrical, ie. prediction is at the center of lower nad upper bound
            yerr = yerr.abs().values.tolist()       # Take the absolute value of the error to denote the length of the error bar
            err_args = {"yerr":yerr,
                        "ecolor":"red",
                        "capsize":5,
                        }
        ax.clear()
        ax.set_xticks(x)                                # Set the x ticks
        ax.set_xticklabels(bar_labels,rotation=-60)     # Change the x tick labels
        ax.set_title("Distribution of values at {} = {}".format(modelSet.y_header,slpos))
        ax.bar(x,y,align="edge",color="blue",**err_args)
        ax.plot([0,len(x)],[0,0],color="black")
        xy = pd.DataFrame({"x":x,"y":y,"label":bar_labels})
        slider_update_func(ax,xy,slpos,err_args)
        fig.canvas.draw_idle()
        return
    update(slider.valmin)
    slider.on_changed(update)
    return fig, ax, slider
    
def plot_as_lines(modelSet,color_map="default",show_trend=False,color_normalization_intrvl=[0,1],fig_ax=(None,None),linestyle="solid",linewidth=2):
    if None in fig_ax:
        fig_ax = plt.subplots()
    fig,ax = fig_ax
    df = modelSet.df.copy()
    ax.set_xticks(df.loc[:,modelSet.y_header])
    ax.set_xticklabels(df.loc[:,modelSet.y_header],rotation=-60)
    normalizer = lambda x : (color_normalization_intrvl[1]-color_normalization_intrvl[0])*(x/(len(df.columns) - 1)) + color_normalization_intrvl[0]
    if isinstance(color_map,str):
        if any([t in color_map for t in ["default","tab","Pastel","Set1","Set2","Set3","Dark2"]]):
            color_map = lambda x : f"C{x}"
        else:
            cm = plt.get_cmap(color_map)
            color_map = lambda x : cm(normalizer(x))
    if isinstance(color_map,matplotlib.colors.Colormap):
        cm = color_map
        color_map = lambda x : cm(normalizer(x))
        
    for i,col in enumerate(df.columns):
        if col == modelSet.y_header:
            continue
        c = color_map(i)
        ax.plot(df.loc[:,modelSet.y_header],
                df.loc[:,col],
                color=c,
                label=col,
                linestyle=linestyle,
                linewidth=linewidth)
        if show_trend:
            m = modelSet.models[col]
            x = sm.add_constant(df.loc[:,modelSet.y_header])
            pred = m.predict(x)
            ax.plot(df.loc[:,modelSet.y_header],
                    pred,
                    color=c,
                    linestyle="dashed")
    return fig, ax


def plot_vars(deps,indep):
    """Plot variables and their models against a single independent variable."""
    x,df = concat_clean_separate(indep,deps)
    x = sm.add_constant(x)
    for k in df.columns:
        y = df.loc[:,k].to_frame()
        m = sm.OLS(y,x).fit()
        plot_model(m,x,y)


def plot_as_stacked_bars(modelSet,color_map="default",show_trend=False,color_normalization_intrvl=[0,1]):
    fig, ax = plt.subplots()
    df = modelSet.df.copy()
    print(df)
    indep = df.pop(modelSet.y_header)
    col_sums = df.sum(axis=0)
    col_sums.sort_values(ascending=False,inplace=True)
    df = pd.concat([df.loc[:,col_sums.index],indep],axis=1)
    print(df)
    ax.set_xticks(df.loc[:,modelSet.y_header])
    ax.set_xticklabels(df.loc[:,modelSet.y_header],rotation=-60)
    normalizer = lambda x : (color_normalization_intrvl[1]-color_normalization_intrvl[0])*(x/(len(df.columns) - 1)) + color_normalization_intrvl[0]
    if isinstance(color_map,str):
        if any([t in color_map for t in ["default","tab","Pastel","Set1","Set2","Set3","Dark2"]]):
            color_map = lambda x : f"C{x}"
        else:
            cm = plt.get_cmap(color_map)
            color_map = lambda x : cm(normalizer(x))
    if isinstance(color_map,matplotlib.colors.Colormap):
        cm = color_map
        color_map = lambda x : cm(normalizer(x))
    
    for i,col in enumerate(df.columns):
        if col == modelSet.y_header:
            continue
        c = color_map(i)
        x = df.loc[:,modelSet.y_header]
        y = df.loc[:,col]
        ax.bar(x,y,
                color=c,
                label=col)
        
        if show_trend:
            m = modelSet.models[col]
            x = sm.add_constant(df.loc[:,modelSet.y_header])
            pred = m.predict(x)
            ax.plot(df.loc[:,modelSet.y_header],
                    pred,
                    color=c,
                    linestyle="dashed")
    return fig, ax
    


if __name__ == "__main__":
    pass