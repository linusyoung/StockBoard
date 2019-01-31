# %%
from os.path import join, dirname

from bokeh.io import output_file, show, save, curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter, AutocompleteInput
from bokeh.models.widgets import Slider, TextInput, Button, Dropdown
import numpy as np
import pandas as pd
import pandas_datareader.data as web

# %%

file_path = join(dirname(__file__), "data/ASXListed.csv")
symbol_df = pd.read_csv(file_path)
symbol_list = symbol_df['ASX code'].tolist()
# %%


def get_stock(stock_code, start=None, end=None):
    """get stock data from yahoo finance daily
    Args:
        stock_code (string): valid yahoo stock code
        start (datetime): data start date
        end (datetime): data end date
    Returns:
        df (DataFrame): dataframe with daily stock
    """

    stock = web.DataReader(stock_code, "yahoo", start=start, end=end)
    # BOLLINGER BAND
    stock["MID_BAND"] = stock["Adj Close"].rolling(20).mean()
    stock["UPPER_BAND"] = stock["MID_BAND"] + \
        stock["Adj Close"].rolling(20).std().mul(2)
    stock["LOWER_BAND"] = stock["MID_BAND"] - \
        stock["Adj Close"].rolling(20).std().mul(2)
    stock["SMA50"] = stock["Adj Close"].rolling(50).mean()
    stock["SMA200"] = stock["Adj Close"].rolling(200).mean()
    stock["H14"] = stock["High"].rolling(14).max()
    stock["L14"] = stock["Low"].rolling(14).min()
    stock["%K"] = 100 * (stock["Close"]-stock["L14"]) / \
        (stock["H14"]-stock["L14"])
    stock["%D"] = stock["%K"].rolling(3).mean()

    # MACD
    stock["12EMA"] = stock["Adj Close"].ewm(com=12).mean()
    stock["26EMA"] = stock["Adj Close"].ewm(com=26).mean()
    stock["MACD"] = stock["12EMA"] - stock["26EMA"]
    # signal line
    stock["9EMA"] = stock["MACD"].ewm(com=9).mean()
    stock["MACD_HIST"] = stock["MACD"] - stock["9EMA"]

    return stock

# %%


stock_code = "AGL.AX"

stock = get_stock(stock_code)
stock.reset_index(inplace=True)
day_offset = Slider(title="Day Prior", value=200, start=7, end=400, step=1)
default_stock = stock.iloc[-200:]
source = ColumnDataSource(default_stock)


# %%

def plot_stock(stock_code, value_type="Adj Close"):
    """plot stock values

    Args:

        value_type (String): specify which value is used to plot
    """

    tooltips = [
        ("Date", "@Date{%F}"),
        ("High", "@High"),
        ("Low", "@Low"),
        ("Upper", "@UPPER_BAND"),
        ("Lower", "@LOWER_BAND")
    ]
    formatters = {
        "Date": "datetime"
    }

    hover = HoverTool(tooltips=tooltips, formatters=formatters,
                      mode="vline")

    price = figure(y_axis_label="Stock value", x_axis_type="datetime",
                   plot_height=500, plot_width=1200, title=stock_code)

    adj_close = price.line(x="Date", y=value_type, source=source,
                           line_color="blue", legend="adj_close")
    price.line(x="Date", y="SMA50", source=source,
               line_color="lightsteelblue", legend="sma50")
    price.line(x="Date", y="SMA200", source=source,
               line_color="darkblue", legend="sma200")
    price.line(x="Date", y="MID_BAND", source=source,
               line_color="dimgray", legend="bb(20,2)", line_dash="dashed")
    price.line(x="Date", y="UPPER_BAND", source=source,
               line_color="dimgray")
    price.line(x="Date", y="LOWER_BAND", source=source,
               line_color="dimgray")

    price.grid.grid_line_alpha = 0.3
    hover.renderers = [adj_close]
    price.add_tools(hover)

    price.legend.location = "top_left"
    price.legend.orientation = "horizontal"
    price.legend.background_fill_alpha = 0.0
    price.legend.border_line_alpha = 0.0

    price.toolbar.logo = None

    tooltips = [
        ("Date", "@Date{%F}"),
        ("Volume", "@Volume{0.0 a}")
    ]
    formatters = {
        "Date": "datetime"
    }
    hover = HoverTool(tooltips=tooltips, formatters=formatters)
    # volume plot
    volume = figure(x_axis_type="datetime", plot_height=200,
                    plot_width=380, title="Volume")
    volume.vbar(x="Date", top="Volume", width=0.1, source=source)
    volume.line(x="Date", y="Volume", source=source, line_alpha=0.0)
    volume.yaxis[0].formatter = NumeralTickFormatter(format="0,0 a")
    volume.add_tools(hover)
    volume.grid.grid_line_alpha = 0.3
    volume.toolbar.logo = None
    volume.toolbar_location = None
    # stochatic plot
    stochastic = figure(x_axis_type="datetime",
                        plot_height=200, plot_width=380, title="Stochastic")
    stochastic.line(x="Date", y="%K", source=source, legend="%k")
    stochastic.line(x="Date", y="%D", source=source,
                    line_dash="dashed", legend="%d")
    stochastic.line(x="Date", y=80, source=source, line_color="black")
    stochastic.line(x="Date", y=20, source=source, line_color="black")
    stochastic.xgrid.grid_line_alpha = 0.0
    stochastic.ygrid.grid_line_alpha = 0.0
    stochastic.legend.location = "top_left"
    stochastic.legend.orientation = "horizontal"
    stochastic.legend.background_fill_alpha = 0.0
    stochastic.legend.border_line_alpha = 0.0

    stochastic.toolbar.logo = None
    stochastic.toolbar_location = None

    # MACD plot
    macd = figure(x_axis_type="datetime",
                  plot_height=200, plot_width=380, title="MACD")
    macd.line(x="Date", y="MACD", source=source, legend="macd")
    macd.line(x="Date", y="9EMA", source=source,
              legend="macd", line_color="black")
    macd.vbar(x="Date", top="MACD_HIST", width=0.1, source=source)

    macd.xgrid.grid_line_alpha = 0.0
    macd.legend.location = "top_left"
    macd.legend.orientation = "horizontal"
    macd.legend.background_fill_alpha = 0.0
    macd.legend.border_line_alpha = 0.0

    macd.toolbar.logo = None
    macd.toolbar_location = None

    return price, column(price, row(volume, stochastic, macd))


# %%
search_symbol = AutocompleteInput(
    title="Query Symbol", completions=symbol_list)


plot, plot_layout = plot_stock(stock_code)

stock_symbol = TextInput(title="Stock Symbol:", value="AGL.AX")

porfolio_list = [("AGL.AX", "AGL.AX"), ("AIZ.AX", "AIZ.AX"),
                 ("IFN.AX", "IFN.AX"), ("NAB.AX", "NAB.AX")]
porfolio = Dropdown(label="Select from porfolio",
                    button_type="primary", menu=porfolio_list)


def update_day(attrname, old, new):
    offset = int(day_offset.value)
    new_stock = stock.iloc[-offset:]
    new_source = ColumnDataSource(new_stock)
    source.data = new_source.data


def update_stock(attrname, old, new):
    global stock
    new_stock_symbol = stock_symbol.value
    plot.title.text = new_stock_symbol
    stock = get_stock(new_stock_symbol)
    offset = int(day_offset.value)
    new_stock = stock.iloc[-offset:]
    new_source = ColumnDataSource(new_stock)
    source.data = new_source.data


def update_symbol(attrname, old, new):
    stock_symbol.value = porfolio.value


def add_stock():
    global porfolio_list, porfolio
    new_stock_symbol = search_symbol.value + '.AX'
    porfolio_list.append((new_stock_symbol, new_stock_symbol))
    porfolio.menu = porfolio_list
    print(porfolio_list)


stock_symbol.on_change("value", update_stock)
porfolio.on_change("value", update_symbol)
day_offset.on_change("value", update_day)

add_to_profolio = Button(label="Add to my profolio", button_type="success")
add_to_profolio.on_click(add_stock)

inputs = column(row(search_symbol, stock_symbol, day_offset),
                row(add_to_profolio, porfolio))
curdoc().add_root(column(inputs, plot_layout))
curdoc().title = "Stock board"
