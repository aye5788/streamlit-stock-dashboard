import streamlit as st
import requests
import pandas as pd
import numpy as np
import mplfinance as mpf
from sklearn.cluster import KMeans
from datetime import datetime, timedelta

# Set FMP API Key
FMP_API_KEY = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"

# Streamlit UI
st.title("📈 Real-Time Stock Support & Resistance Dashboard")

# User Input
ticker = st.text_input("Enter a stock ticker (e.g., SPY, AAPL):", value="SPY")
analyze_button = st.button("Analyze")  # Add a button

if analyze_button:  # Only fetch data when the button is clicked
    st.write(f"Fetching **current session** 5-minute chart for: **{ticker}**")

    # Fetch 5-minute interval data
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/5min/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Keep only necessary columns and format correctly
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.sort_index()

        # Filter only today's session data
        today = datetime.now().date()
        df = df[df.index.date == today]

        # Ensure we have data for today
        if df.empty:
            st.error("⚠️ No data available for today's session. The market might be closed.")
        else:
            # Detect Support & Resistance with K-Means (Better Optimization)
            num_clusters = min(5, len(df) // 10)  # Adjust cluster count dynamically
            price_data = df[['high', 'low']].values.reshape(-1, 1)
            kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
            kmeans.fit(price_data)
            support_resistance_levels = sorted(kmeans.cluster_centers_.flatten())

            # Round the detected levels for better readability
            support_resistance_levels = [round(level, 2) for level in support_resistance_levels]

            # Plot Chart with Support & Resistance
            fig, ax = mpf.plot(df, type='candle', volume=True, returnfig=True)
            for level in support_resistance_levels:
                ax[0].axhline(y=level, color='red', linestyle='--', linewidth=1.5)

            st.pyplot(fig)

            # Display Detected Levels in a Clear Format
            st.write("### 🔍 Identified Support & Resistance Levels:")
            st.write(support_resistance_levels)
    else:
        st.error("⚠️ Failed to fetch data. Please check the ticker or API key.")

