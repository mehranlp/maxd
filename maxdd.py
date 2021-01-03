import yfinance as yf
import streamlit as st
from datetime import datetime
import plotly.express as px

from dateutil.relativedelta import relativedelta



"""
###   THIS VISUALIZATION REPRESTS YOUR WEALTH BEHAVIOUR IF YOU HAD INVEST IN S&P500 AT CERTAIN TIME AND ALSO SHOWS THE MAXIMUM [DRAWDOWN](https://www.investopedia.com/terms/d/drawdown.asp) IN YOUR WEALTH
#####    BY MEHRAN POORMALEK ([CODE REPOSITORY](https://github.com/mehranlp/maxd))
"""

# Create strart and end dates sidebar
start_date = st.sidebar.date_input(
    "Start date:", (datetime.now() - relativedelta(years=10)),
)
end_date = st.sidebar.date_input("End date:",
                                datetime.now())
# Create box to input amount of investment
amount = st.sidebar.number_input(label='HOW MUCH YOU WOULD INVEST AT THE TIME?',
                                min_value=0.0,max_value=1000000.00)


tickerSymbol='^GSPC'
#Get data of this ticker
tickerData=yf.Ticker(tickerSymbol)
#get historical data of each ticker
tickerDF=tickerData.history(period='1w',start=start_date, end=end_date)
tickerDF['Return1']=tickerDF['Close'].pct_change()


tickerDF=tickerDF.dropna(
                axis=0)
tickerDF['Wealth']=((1+
                    (tickerDF['Return1'])).cumprod())
tickerDF['Wealth']=tickerDF['Wealth']*amount
tickerDF=tickerDF.drop(
                    ['Open','High','Low','Close','Volume',
                    'Dividends','Stock Splits','Return1'],axis=1)

tickerDF['previous_peaks'] = tickerDF['Wealth'].cummax()
tickerDF['drawdown']=(tickerDF['Wealth']-tickerDF['previous_peaks'])/tickerDF['previous_peaks']

st.plotly_chart(
    px.line(tickerDF['Wealth']).update_layout(
    plot_bgcolor="white",
        yaxis_title="Your Wealth",
        legend_title_text="Wealth Index",width=900, height=600
    )
)

"""
### MAXIMUM DRADOWN
"""

st.plotly_chart(
    px.area(tickerDF['drawdown']).update_layout(
        yaxis_title="Drawdown", legend_title_text="Drawdown",
        width=900, height=600
    )
)
