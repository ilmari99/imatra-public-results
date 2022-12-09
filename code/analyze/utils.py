from functools import wraps
import pandas as pd
import re
from itertools import chain
import matplotlib.pyplot as plt
import statsmodels.api as sm
from matplotlib import animation
from _config import DATA_FOLDER,FIG_SIZE


def get_columns_that_match_regex(df : pd.DataFrame,
                                 regex : str, 
                                 get_year=True):
    """Returns a list of column headers that match the given regex.
    """
    headers = df.columns
    headers = [l for l in headers if re.match(regex, l) or (get_year and l == "vuosi")]
    return df.loc[:,headers]

def plot_model(model,x,y, show=True,save=None,has_constant=False):
    """ Plot a model alongside the data.
    Copies the x and y variables
    Checks if x variable has a column named 'const'
        If yes, drops the 'const' columns for easy plotting.
    Plots the x and y variables in a scatter plot.
    If the x variable had a 'const' column, or if has_constant is True,
        add a column of ones to the x variable.
    predict the y variable using the model and plot the predicted values.
    If save is not None, saves the plot to a file specified by the save variable.
    """
    assert len(x) == len(y)
    x,y = x.copy(),y.copy()
    if isinstance(x,pd.DataFrame) and "const" in x.columns:
        has_constant = True
        x.drop("const",axis=1,inplace=True)
    xname = x.columns[0] if isinstance(x,pd.DataFrame) else x.name
    yname = y.columns[0] if isinstance(y,pd.DataFrame) else y.name
    plt.figure()
    plt.scatter(x,y,label="data")
    plt.title(f"{xname} vs {yname}")
    plt.xlabel(xname)
    plt.ylabel(yname)
    if has_constant:
        x = sm.add_constant(x)
    ypred = model.predict(x)
    plt.plot(x.pop(xname),ypred,"r",label="prediction")
    plt.legend()
    if save is not None:
        plt.savefig(save)
    if show:
        plt.show()
    
    

def get_rows(df : pd.DataFrame,
             **kwargs):
    """ Returns the rows that match the given condition (currently only supports one argument).
    For example vuosi=[2018,2019] returns rows where vuosi is 2018 or 2019.
    """
    # Get the first kwargument name
    try:
        ind_column_label = list(kwargs.keys())[0]
    except IndexError:
        raise ValueError("No value provided")
    # Get the value of the kwargument
    ind = kwargs.get(ind_column_label)
    # Check if the value is a list or 'all'
    if not isinstance(ind,list) and ind != "all":
        raise TypeError("Argument must be list")
    if ind == "all":
        ind = list(df.loc[:,ind_column_label])
    # Get the rows, where the value of the column (kwarg key) matches the value of the kwargument
    data = df.loc[df[ind_column_label].isin(ind)]
    return data

        
def get_columns(df : pd.DataFrame,
                *args,dropnan=True):
    """Given lists of headers, returns a tuple of the corresponding dataframes.
    If dropnan is True, the dataframes are filtered to remove rows with NaN values.
    """
    for arg in args:
        if not isinstance(arg,list):
            raise TypeError("Arguments must be lists")
    as_combined_list = list(chain(*args))
    df = df.loc[:,as_combined_list]
    if dropnan:
        df.dropna(inplace=True)
    out = [df.loc[:,arg] for arg in args]
    return tuple(out)


def concat_clean_separate(*args):
    """Concatenates the given dataframes, drops NaN values, and returns the dataframes separated to a tuple
    """
    #args = [pd.DataFrame(data=a,columns=[a.columns if isinstance(a,pd.DataFrame) else a.Name]) for a in args]
    args = [pd.DataFrame(a) for a in args]
    try:
        headers = [df.columns for df in args]
    except AttributeError:
        raise AttributeError("All arguments must be dataframes")
    df = pd.concat(args,axis=1)
    df.dropna(inplace=True)
    dfs = [df.loc[:,h] for h in headers]
    return tuple(dfs)

def read_to_df(f = None, drop=[]):
    df = None
    drop.append("Unnamed: 0")
    try:
        df = pd.read_excel(f)
    except FileNotFoundError:
        msg = "File not found: {}\n See if the global variable 'DATA_FOLDER' is set correctly. ".format(f)
        raise FileNotFoundError(msg)
    df.drop(drop,axis=1,inplace=True,errors="ignore")
    return df

def value_to_line_end(ax,
                      df,
                      y_header,
                      x_header="vuosi",
                      offset=(0,0),
                      text="value",
                      text_kwargs={},
                      add_point=False,
                      point_kwargs={},
                      ):
    if text == "value":
        text = str(df.loc[len(df[y_header])-1,y_header])
    if "color" not in text_kwargs:
        text_kwargs["color"] = "blue"
    ax.text(
        df.loc[len(df[x_header])-1,x_header]+offset[0],
        df.loc[len(df[y_header])-1,y_header]+offset[1],
        text,
        **text_kwargs,
            )
    if add_point:
        if "color" not in point_kwargs:
            point_kwargs["color"] = "blue"
        if "s" not in point_kwargs:
            point_kwargs["s"] = 20
        ax.scatter(df.loc[len(df[x_header])-1,x_header],
                   df.loc[len(df[y_header])-1,y_header],
                   **point_kwargs,
                   )

def normed_dict(v,lb=None,ub=None):
    """"Normalizes values in the list v to the range [lb,ub] and returns a dictionary,
    with the values as keys and the normalized values as values.
    """
    if lb is None:
        lb = min(v)
    if ub is None:
        ub = max(v)
    n = [(x-lb)/(ub-lb) for x in v]
    return dict(zip(v,n))

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
    
def set_fig_ax(fig_ax,
                    title="",
                    xlabel="",
                    ylabel="",
                    facecolor="silver",
                    ylim=(),
                    xlim=(),
                    fig_size=(),
                    xrot=0,
                    yrot=45,
                    xlabel_coord=(1.05,-0.025),
                    ylabel_coord=(-0.025,1.05),
                    ):
    fig,ax = fig_ax
    ax.grid(True,axis="y")
    ax.set_xlabel(xlabel,rotation=0)
    ax.set_ylabel(ylabel,rotation=45)
    ax.set_title(title)
    fig.set_size_inches(fig_size if fig_size else FIG_SIZE)
    ax.legend()
    ax.set_facecolor(facecolor)
    ax.xaxis.set_label_coords(*xlabel_coord)
    ax.yaxis.set_label_coords(*ylabel_coord)
    if ylim:
        ax.set_ylim(ylim)
    if xlim:
        ax.set_xlim(xlim)
    return fig,ax

def save_figure(fun,*args,**kwargs):
    path_map = {
        "_vaesto_plots":"vaesto/",
        "_asunto_plots":"asuminen/",
        "_raha_plots":"talous_ja_tyollisyys/",
    }
    file = fun.__globals__["__file__"]
    modul = file.split("/")[-1].split(".")[0]
    res = fun(*args,**kwargs)
    name = fun.__name__.replace("plot_","")
    if len(res) == 3 and isinstance(res[2],animation.FuncAnimation):
        save_as = kwargs.get("save_as","results/animations/"+path_map[modul]+name+".gif")
        res[2].save(save_as,writer="imagemagick")
    else:
        save_as = kwargs.get("save_as","results/figures/"+path_map[modul]+name+".png")
        res[0].savefig(save_as)
    return res
