# %%
from os.path import join, dirname

from bokeh.io import output_file, show, save, curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput
import numpy as np
import pandas as pd
import pandas_datareader.data as web

# %%


stock_code = 'AGL.AX'
file_path = join(dirname(__file__), 'data/ASXListed.csv')
symbol_df = pd.read_csv(file_path)


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
    # BOLLINGER BAND
    stock['MID_BAND'] = stock['Adj Close'].rolling(20).mean()
    stock['UPPER_BAND'] = stock['MID_BAND'] + \
        stock['Adj Close'].rolling(20).std().mul(2)
    stock['LOWER_BAND'] = stock['MID_BAND'] - \
        stock['Adj Close'].rolling(20).std().mul(2)
    stock['SMA50'] = stock['Adj Close'].rolling(50).mean()
    stock['SMA200'] = stock['Adj Close'].rolling(200).mean()
    stock['H14'] = stock['High'].rolling(14).max()
    stock['L14'] = stock['Low'].rolling(14).min()
    stock['%K'] = 100 * (stock['Close']-stock['L14']) / \
        (stock['H14']-stock['L14'])
    stock['%D'] = stock['%K'].rolling(3).mean()

    return stock

# %%


stock = get_stock(stock_code)
stock.reset_index(inplace=True)
day_offset = Slider(title='Day Prior', value=200, start=7, end=400, step=1)
default_stock = stock.iloc[-200:]
source = ColumnDataSource(default_stock)


# %%

def plot_stock(stock_code, value_type='Adj Close'):
    """plot stock values

    Args:

        value_type (String): specify which value is used to plot
    """

    tooltips = [
        ('Date', '@Date{%F}'),
        ('High', '@High'),
        ('Low', '@Low'),
        ('Upper', '@UPPER_BAND'),
        ('Lower', '@LOWER_BAND')
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
    price.line(x='Date', y='SMA50', source=source,
               line_color='black', legend='sma50')
    price.line(x='Date', y='SMA200', source=source,
               line_color='red', legend='sma200')
    price.line(x='Date', y='MID_BAND', source=source,
               line_color='pink', legend='bb(20,2)', line_dash='dashed')
    price.line(x='Date', y='UPPER_BAND', source=source,
               line_color='pink')
    price.line(x='Date', y='LOWER_BAND', source=source,
               line_color='pink')

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
    volume = figure(y_axis_label='Volume',
                    x_axis_type='datetime', plot_height=200)
    volume.vbar(x='Date', top='Volume', width=0.1, source=source)
    volume.line(x='Date', y='Volume', source=source, line_alpha=0.0)
    volume.yaxis[0].formatter = NumeralTickFormatter(format="0,0 a")
    volume.add_tools(hover)
    volume.grid.grid_line_alpha = 0.3

    so = figure(x_axis_type='datetime', plot_height=200,
                y_axis_location='right')
    so.line(x='Date', y='%K', source=source, legend='%k')
    so.line(x='Date', y='%D', source=source, line_dash='dashed', legend='%d')
    so.line(x='Date', y=80, source=source, line_color='black')
    so.line(x='Date', y=20, source=source, line_color='black')
    so.legend.location = 'top_left'
    return price, column(price, volume, so)


def update_day(attrname, old, new):
    offset = int(day_offset.value)
    new_stock = stock.iloc[-offset:]
    new_source = ColumnDataSource(new_stock)
    source.data = new_source.data


day_offset.on_change('value', update_day)

# %%

search_symbol = TextInput(title='Search Symbol:',
                          placeholder='Type company name')
plot, plot_layout = plot_stock(stock_code)

stock_symbol = TextInput(title='Stock Symbol:', value='AGL.AX')


def update_stock(attrname, old, new):
    plot.title.text = stock_symbol.value


stock_symbol.on_change('value', update_stock)

inputs = widgetbox(search_symbol, stock_symbol, day_offset)
curdoc().add_root(row(inputs, plot_layout))
curdoc().title = 'Stock board'
