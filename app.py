'''
Used online resources to help me create the dropdown and option menus in a streamlit application. Also used 
online resources to help me find ways to display data in graphs and tables) and use creatin apis such as 
yahoo finance, alpha vantage, and plotly.

Some videos I used:
Streamlit STOCK dashboard using Python 🔴 by Financial Programming with Ritvik, CFA
https://www.youtube.com/watch?v=fdFfpEtv5BU

The EASIEST way to insert a NAVIGATION into your Streamlit app by Coding is Fun 
https://www.youtube.com/watch?v=hEPoto5xp3k&t=39s

Build A Stock Prediction Web App In Python by Patrick Loeber
https://www.youtube.com/watch?v=0E_31WqVzCY
'''

#imports for thee general web app
import streamlit as st
from datetime import datetime
import yfinance as yf
from streamlit_option_menu import option_menu

#imports for the stock prediction model page
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

#imports for the stock dashboard page 
# import pandas as pd
import numpy as np
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData



#horizontal menu w/ custom menu
EXAMPLE_NO = 3

def streamlit_menu(example=3):
    if example == 3:
        
        selected = option_menu(
            menu_title=None,  
            options=["Stock Prediction", "Stock Dashboard"],  
            icons=["house", "book", "envelope"],  
            menu_icon="cast",  
            default_index=0,  
            orientation="horizontal",
            styles={ #styling of the menu
                "container": {"padding": "0!important", "background-color": "#0E1117"},
                "icon": {"color": "#FF4B4B", "font-size": "25px"},
                "nav-link": {
                    "font-size": "25px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#262730",
                },
                "nav-link-selected": {"background-color": "#262730"},
            },
        )
        return selected 


selected = streamlit_menu(example=EXAMPLE_NO)

if selected == "Stock Prediction": #first tab of the web app, the stock prediction tab
    START = "2015-01-01"
    TODAY = datetime.today().strftime("%Y-%m-%d")
    #start and end dates to be used later on

    st.title("Stock Prediction App") #displays the title of the tab

    # selected_stock = st.text_input("Enter stock ticker:", "MSFT") 
    # this could be another way to write this without the use of a list
    stocks = ["GME", "AAPL", "GOOG", "MSFT"] #list of stock tickers that user can chose from to get data and a prediction on 
    selected_stock = st.sidebar.selectbox("Select stock for prediction", stocks) #how the user selects the stock in a dropdown menu

    n_years = st.sidebar.slider("Prediction years", 1, 4)
    period = n_years * 365 #how many years into the future to predict the price of the stock --> years converted into days

    #downloading data of the ticker the user choose using the start and end dates defined above
    @st.cache
    def load_data(TICKER):
        data = yf.download(TICKER, START, TODAY)  
        data.reset_index(inplace=True)
        return data

    #data load statements and function definition
    data_load_state = st.text("Load data...")
    data = load_data(selected_stock)
    data_load_state = st.text("Loading data...done")

    #first data table, shows the last few datapoints in the dataframe in a table format
    st.subheader('Raw Data')
    st.write(data.tail())


    def plot_raw_data():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open'))
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'],
                            name='stock_close'))
        fig.layout.update(title_text="Time Series Data",
                        xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)

    #plotting the stocks daily opeen and close prices  in a graph 
    plot_raw_data()

    #training the prediction model using various metrics such as close price, date, and previous data 
    df_train = data[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

    #predicting future pricee of the stock
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)

    #shows the last few datapoints in the prediction in a table format 
    st.subheader('Forecast Data')
    st.write(forecast.tail())

    #plots the prediction data in a graph
    st.write("Forecast Data")
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)

    #shows graphs of components of the prediction model
    st.write("Forecast Components")
    fig2 = m.plot_components(forecast)
    st.write(fig2)



if selected == "Stock Dashboard": #second tab of the web app, the stock dashboard tab
    default_start_date = datetime(datetime.today().year - 1, datetime.today().month, datetime.today().day)
    default_end_date = datetime.today()
    #default start and end dates that is inputted into the box to start

    st.title("Stock Dashboard") #displays the title of the tab
    stocks = ["GME", "AAPL", "GOOG", "MSFT"] #list of stock tickers the user can choose 
    ticker = st.sidebar.selectbox("Select stock for prediction", stocks) #how the user selects the stock in a dropdown menu

    # ticker = st.sidebar.text_input('Ticker', 'MSFT')
    #another way to writee the same code without the use of a list

    start_date = st.sidebar.date_input('Start date', default_start_date)
    end_date = st.sidebar.date_input('End date', default_end_date)
    #start and end dates to be used later on, user inputs 

    #downloading data of the ticker the user choose using the start and end dates defined above
    @st.cache
    def load_data(TICKER):
        data = yf.download(TICKER, start_date, end_date)
        data.reset_index(inplace=True)
        return data

    #data load statements and function definition 
    data_load_state = st.text("Load data...")
    data = load_data(ticker)
    data_load_state = st.text("Loading data...done")

    #data from the previous function is plotteed in a graph
    fig = px.line(data, x=data.index, y=data['Adj Close'], title=ticker)
    st.plotly_chart(fig)

    #tabs are made to show two different types of company data 
    pricing_data, fundamentel_data = st.tabs(
        ["Pricing Data", "Fundamentel Data"])

    #defines whats in the prcing data tab
    with pricing_data:
        st.header("Pricing Movements") #title for the table
        data2 = data
        data2.dropna(inplace=True)
        data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
        st.write(data2) #a table is shown using the data 
        #various metrics are calculated and displayed on the screen
        annual_return = data2['% Change'].mean() * 252 * 100
        st.write('annual_return is', annual_return, '%')
        stdev = np.std(data2['% Change']) * np.sqrt(252)
        st.write('Standard deviation is', stdev * 100, '%')
        st.write('Risk Adj. Return is', annual_return / (stdev * 100)) 

    #defines whats in the fundamental data tab
    with fundamentel_data:
        key = '1YGHNI79XNHHGDWL' #Alpha vantage api key which allows to make calls to get stock data 
        fd = FundamentalData(key, output_format='pandas')
        st.subheader("Balance Sheet") #title for the table
        balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
        bs = balance_sheet.T[2:]
        bs.columns = list(balance_sheet.T.iloc[0])
        st.write(bs) #balance sheet data is used to make a table
        st.subheader("Income Statement") #title for the table
        income_statement = fd.get_income_statement_annual(ticker)[0]
        is1 = income_statement.T[2:]
        is1.columns = list(income_statement.T.iloc[0])
        st.write(is1) #data about the companies income is used to make a table