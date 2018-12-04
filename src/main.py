# %%
from bokeh.io import output_file, show, save
import bokeh
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter
import numpy as np
import pandas as pd
import pandas_datareader.data as web

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

    stock = web.DataReader(stock_code, 'yahoo', start=start, end=end)
    stock['MA50'] = stock['Adj Close'].rolling(50).mean()
    stock['MA200'] = stock['Adj Close'].rolling(200).mean()

    return stock

# %%


def plot_stock(df, stock_code, value_type='Adj Close'):
    """plot stock values

    Args:

        df (DataFrame): historical stock data
        value_type (String): specify which value is used to plot
    """

    output_file('../output/test.html')

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

    adj_close = price.line(x='Date', y=value_type,
                           source=source, legend='adj_close')
    price.line(x='Date', y='MA50', source=source,
               line_color='black', legend='ma50')
    price.line(x='Date', y='MA200', source=source,
               line_color='red', legend='ma200')
    price.grid.grid_line_alpha = 0.3
    price.xaxis.visible = False
    hover.renderers = [adj_close]
    price.add_tools(hover)

    price.legend.location = "top_left"

    tooltips = [
        ('Date', '@Date{%F}'),
        ('Volume', '@Volume{0.0 a}')
    ]
    formatters = {
        'Date': 'datetime'
    }
    hover = HoverTool(tooltips=tooltips, formatters=formatters)
    volume = figure(x_axis_label='Date', y_axis_label='Volume',
                    x_axis_type='datetime', plot_height=200)
    volume.vbar(x='Date', top='Volume', width=0.1, source=source)
    volume.line(x='Date', y='Volume', source=source)
    volume.yaxis[0].formatter = NumeralTickFormatter(format="0,0 a")
    volume.add_tools(hover)
    volume.grid.grid_line_alpha = 0.3

    layout = column(children=[price, volume])
    save(layout)


# %%
stock_code = 'AGL.AX'
stock = get_stock(stock_code)
stock.reset_index(inplace=True)
plot_stock(stock, stock_code)
