import streamlit as st
from datetime import datetime
import yfinance as yf
# import pandas as pd
import numpy as np
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
from streamlit_option_menu import option_menu
# from PIL import Image

# image = Image.open('STONKS_GUY.png')

default_start_date = datetime(datetime.today().year - 1, datetime.today().month, datetime.today().day)
default_end_date = datetime.today()

st.title("Stock Dashboard")
ticker = st.sidebar.text_input('Ticker', 'MSFT')
start_date = st.sidebar.date_input('Start date', default_start_date)
end_date = st.sidebar.date_input('End date', default_end_date)

data = yf.download(ticker, start=start_date, end=end_date)
fig = px.line(data, x=data.index, y=data['Adj Close'], title=ticker)
st.plotly_chart(fig)
# st.image(image, caption='W STONKS GUYYYYYY')

pricing_data, fundamentel_data, news = st.tabs(
    ["Pricing Data", "Fundamentel Data", "News"])

with pricing_data:
    st.header("Pricing Movements")
    data2 = data
    data2.dropna(inplace=True)
    data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
    st.write(data2)
    annual_return = data2['% Change'].mean() * 252 * 100
    st.write('annual_return is', annual_return, '%')
    stdev = np.std(data2['% Change']) * np.sqrt(252)
    st.write('Standard deviation is', stdev * 100, '%')
    st.write('Risk Adj. Return is', annual_return / (stdev * 100))

with fundamentel_data:
    key = '4UUN1D33JVIJ1NQ0'
    fd = FundamentalData(key, output_format='pandas')
    st.subheader("Balance Sheet")
    balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
    bs = balance_sheet.T[2:]
    bs.columns = list(balance_sheet.T.iloc[0])
    st.write(bs)
    st.subheader("Income Statement")
    income_statement = fd.get_income_statement_annual(ticker)[0]
    is1 = income_statement.T[2:]
    is1.columns = list(income_statement.T.iloc[0])
    st.write(is1)
    st.subheader("Cash Flow Statement")
    cash_flow = fd.get_cash_flow_annual(ticker)[0]
    cf = cash_flow.T[2:]
    cf.columns = list(cash_flow.T.iloc[0])
    st.write(cf)
