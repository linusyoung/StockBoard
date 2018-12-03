# %%
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool
import numpy as np
import pandas as pd
import pandas_datareader.data as web


def get_stock(stock_code, start=None, end=None):
    """get stock data from yahoo finance daily
    Args:
        stock_code (string): valid yahoo stock code
        start (datetime): data start date
        end (datetime): data end date
    Returns:
        df (DataFrame): dataframe with daily stock
    """

    stock = web.DataReader(stock_code, 'yahoo', start=start, end=end)

    return stock

# %%


def plot_stock(df, stock_code, value_type='Adj Close'):
    """plot stock values

    Args:

        df (DataFrame): historical stock data
        value_type (String): specify which value is used to plot
    """
    source = ColumnDataSource(df)
    tooltips = [
        ('Date', '@Date{%F}'),
        ('High', '@High'),
        ('Low', '@Low')
    ]
    formatters = {
        'Date': 'datetime'
    }

    hover = HoverTool(tooltips=tooltips, formatters=formatters,
                      mode='vline')

    price = figure(y_axis_label='Stock value',
                   plot_height=500, title=stock_code)
    price.line(x='Date', y=value_type, source=source)
    price.grid.grid_line_alpha = 0.3
    price.xaxis.visible = False
    price.add_tools(hover)

    tooltips = [
        ('Date', '@Date{%F}'),
        ('Volume', '@Volume')
    ]
    formatters = {
        'Date': 'datetime'
    }
    hover = HoverTool(tooltips=tooltips, formatters=formatters)
    volume = figure(x_axis_label='Date', y_axis_label='Volume',
                    x_axis_type='datetime', plot_height=200)
    volume.vbar(x='Date', top='Volume', width=0.1, source=source)
    volume.line(x='Date', y='Volume', source=source)
    volume.add_tools(hover)
    layout = column(children=[price, volume])
    show(layout)


# %%
stock_code = 'IFN.AX'
ifn = get_stock(stock_code)
# print(ifn.info())
plot_stock(ifn, stock_code)
