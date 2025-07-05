import yfinance as yf
import streamlit as st
from datetime import datetime
import plotly.express as px

from dateutil.relativedelta import relativedelta
"""
As of today, January 7, 2021, the stock market has been climbing and set a record higher almost every day. If you are following the Financial Twitter feed, you will find a GENIUS who beat the market and made
a 30-40% return in a day or week! The market timing is practically impossible and no one could tell what will happen in 1 day, let alone one week or year! But you may hear about "Long Term Return" which is on average 7% per year for S&p 500, that basically
means if you have a long-term view, you should not worry about investment at any point, because the market always goes up in long term! Well, the purpose of this application is to give you a better sense of what you would have expected if you invest your money in the past,
and how much your account could go down at any point in time when the market collapse. You can learn more about  [maximum drawdown here](https://www.investopedia.com/terms/d/drawdown.asp).
As you can try with this application, if you would invest in the S&P 500 in April 2000, you had to wait almost 13 years to get your initial investment back!!!Of course, this doesn't mean you should avoid investing 
or try to time the market (again it is impossible!). It only means you must rely on your investment philosophy, asset diversification, and the company you want to invest in for
return, not on the general market movements, and buy any stock you heard about on Twitter or Motley .....
"""
"""
BY MEHRAN POORMALEK ([CODE REPOSITORY](https://github.com/mehranlp/maxd))
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


tickerSymbol='SPY'
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
tickerDF = tickerDF.drop(['Open','High','Low','Close','Volume','Dividends','Stock Splits','Return1'], axis=1, errors='ignore')

tickerDF['previous_peaks'] = tickerDF['Wealth'].cummax()
tickerDF['drawdown']=(tickerDF['Wealth']-tickerDF['previous_peaks'])/tickerDF['previous_peaks']

st.plotly_chart(
    px.line(tickerDF['Wealth']).update_layout(
    plot_bgcolor="white",
        yaxis_title="Your Wealth all in S&P 500",
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
