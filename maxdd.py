import yfinance as yf
import streamlit as st
from datetime import datetime
import plotly.express as px
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Drawdown Visualizer", layout="wide")

# --- Sidebar inputs ---
st.sidebar.title("Investment Parameters")
start_date = st.sidebar.date_input("Start date:", datetime.now() - relativedelta(years=10))
end_date = st.sidebar.date_input("End date:", datetime.now())
amount = st.sidebar.number_input("Annual Investment Amount ($)", min_value=100.0, max_value=1_000_000.0, value=1000.0)

# Define investment options
asset_options = {
    "S&P 500 (SPY)": "SPY",
    "NASDAQ-100 (QQQ)": "QQQ",
    "Global Equity (VXUS)": "VXUS",
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Gold (GLD)": "GLD"
}
asset_name = st.sidebar.selectbox("Investment Asset", list(asset_options.keys()))
tickerSymbol = asset_options[asset_name]

# --- App header ---
st.title("Wealth & Drawdown Tracker")
st.markdown(f"""
Visualize **cumulative wealth** and **maximum drawdowns** when investing **${amount:,.0f} annually** in **{asset_name}** from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.
""")

# --- Get historical data ---
@st.cache_data
def get_data(ticker, start, end):
    df = yf.Ticker(ticker).history(start=start, end=end, interval='1wk')
    df = df[['Close']].dropna()
    df = df.reset_index()
    return df

df = get_data(tickerSymbol, start_date, end_date)

if df.empty:
    st.error("No data found for selected period.")
else:
    df['Return'] = df['Close'].pct_change()
    df.dropna(inplace=True)

    # --- Simulate annual investments ---
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    invest_month = df['Month'].min()  # use earliest month in data for consistency
    annual_invest_dates = df[df['Month'] == invest_month].copy()
    annual_invest_dates['Investment'] = amount

    df['Wealth'] = 0
    units = 0
    total_value = []

    for i, row in df.iterrows():
        if row['Date'].month == invest_month and row['Date'].year in annual_invest_dates['Year'].values:
            units += amount / row['Close']
        total_value.append(units * row['Close'])

    df['Wealth'] = total_value
    df['PreviousPeak'] = df['Wealth'].cummax()
    df['Drawdown'] = (df['Wealth'] - df['PreviousPeak']) / df['PreviousPeak']

    # --- Plot Wealth ---
    fig1 = px.line(df, x='Date', y='Wealth', title=f"Wealth Over Time: {asset_name}",
                   labels={"Wealth": "Portfolio Value ($)"})
    fig1.update_traces(line_color='green')
    fig1.update_layout(plot_bgcolor="white", width=900, height=500)

    # --- Plot Drawdown ---
    fig2 = px.area(df, x='Date', y='Drawdown', title=f"Drawdown Over Time: {asset_name}",
                   labels={"Drawdown": "Drawdown (fraction)"})
    fig2.update_traces(line_color='red', fillcolor='rgba(255,0,0,0.3)')
    fig2.update_layout(yaxis_tickformat=".0%", width=900, height=500)

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

    # --- Show max drawdown info ---
    max_dd = df['Drawdown'].min()
    st.markdown(f"### 📉 Maximum Drawdown: **{max_dd:.2%}**")
