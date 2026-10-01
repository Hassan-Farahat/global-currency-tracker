import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Page Setup
st.set_page_config(page_title="Global Currency Tracker", page_icon="🔱", layout="wide")

# Fetch Live Exchange Rates
@st.cache_data(ttl=300)
def fetch_exchange_rates():
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        rates = data.get('rates', {})
        df = pd.DataFrame(list(rates.items()), columns=['Currency', 'Rate_to_USD'])
        return df, True
    except Exception:
        fallback = pd.DataFrame([
            {'Currency': 'EUR', 'Rate_to_USD': 0.92},
            {'Currency': 'GBP', 'Rate_to_USD': 0.78},
            {'Currency': 'EGP', 'Rate_to_USD': 51.97},
            {'Currency': 'CAD', 'Rate_to_USD': 1.36},
            {'Currency': 'JPY', 'Rate_to_USD': 155.20},
            {'Currency': 'AUD', 'Rate_to_USD': 1.51},
            {'Currency': 'CHF', 'Rate_to_USD': 0.90},
            {'Currency': 'CNY', 'Rate_to_USD': 7.23}
        ])
        return fallback, False

# Helper for Safe Rate Lookup
def get_rate(df, currency_code, default=0.0):
    val = df[df['Currency'] == currency_code]['Rate_to_USD']
    return val.values[0] if not val.empty else default

# Header
st.title("🔱 Global Currency Tracker")
st.markdown("Live global exchange rates fetched directly from **Open Exchange Rates REST API**.")

df, is_live = fetch_exchange_rates()

# Status Banner
if is_live:
    st.success("🟢 **Data Source:** Live REST API Connected")
else:
    st.warning("🟡 **Data Source:** Using Local Fallback Dataset")

# Sidebar - USD Converter
st.sidebar.header("USD Converter")
usd_amount = st.sidebar.number_input("Amount in USD ($)", min_value=1.0, value=1.00, step=1.0)
target_currency = st.sidebar.selectbox("Select Target Currency:", df['Currency'], index=int(df[df['Currency']=='EGP'].index[0]) if 'EGP' in df['Currency'].values else 0)

target_rate = get_rate(df, target_currency)
converted_val = usd_amount * target_rate
st.sidebar.metric(f"Value in {target_currency}", f"{converted_val:,.2f}")

# Sidebar - Dev Tools
with st.sidebar.expander("⚙️ Settings"):
    if st.button("Clear App Cache"):
        st.cache_data.clear()
        st.rerun()

# Top Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Currencies Tracked", len(df))
col2.metric("EUR Rate", f"{get_rate(df, 'EUR'):.4f}")
col3.metric("GBP Rate", f"{get_rate(df, 'GBP'):.4f}")

# Chart
st.subheader("Selected Major Currencies vs USD")
major_currencies = ['EUR', 'GBP', 'EGP', 'CAD', 'AUD', 'CHF', 'CNY', 'AED']
chart_df = df[df['Currency'].isin(major_currencies)].sort_values(by='Rate_to_USD')

fig = px.bar(
    chart_df,
    x='Currency',
    y='Rate_to_USD',
    text_auto='.2f',  # Displays value numbers above each bar
    color='Rate_to_USD',
    color_continuous_scale='Blues',
    template='plotly_white',
    labels={'Rate_to_USD': 'Units per 1 USD'}
)
fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)

# Data Table
st.subheader("All Currency Rates")
st.dataframe(df, use_container_width=True)