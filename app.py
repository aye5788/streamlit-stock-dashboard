import streamlit as st
import requests
import pandas as pd
import numpy as np
import mplfinance as mpf
from sklearn.cluster import KMeans
from datetime import datetime

# Set FMP API Key
FMP_API_KEY = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"

# Streamlit UI
st.title("📈 Real-Time Stock Support & Resistance Dashboard")
ticker = st.text_input("Enter a stock ticker (e.g., SPY, AAPL):", value="SPY")

if ticker:
    st.write(f"Fetching 5-minute chart for: **{ticker}**")

    # Fetch 5-minute interval data
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/5min/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        
        # Format DataFrame
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.sort_index()

        # Detect Support & Resistance with K-Means
        price_data = df[['high', 'low']].values.reshape(-1, 1)
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        kmeans.fit(price_data)
        support_resistance_levels = sorted(kmeans.cluster_centers_.flatten())

        # Plot Chart with Support & Resistance
        fig, ax = mpf.plot(df, type='candle', volume=True, returnfig=True)
        for level in support_resistance_levels:
            ax[0].axhline(y=level, color='red', linestyle='--', linewidth=1.5)
        
        st.pyplot(fig)
        
        # Display Detected Levels
        st.write("### 🔍 Identified Support & Resistance Levels:")
        st.write(support_resistance_levels)
        
    else:
        st.error("⚠️ Failed to fetch data. Please check the ticker or API key.")

