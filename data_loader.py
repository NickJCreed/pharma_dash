import streamlit as st
import pandas as pd

def load_data():
    # If uploaded file exists in session_state, use it
    if 'uploaded_df' in st.session_state:
        df = st.session_state['uploaded_df']
        # Ensure datetime conversion if needed
        if 'month_year' in df.columns:
            df['month_year'] = pd.to_datetime(df['month_year'], errors='coerce')
        return df
    else:
        # Fallback to default CSV if nothing uploaded
        df = pd.read_csv('pharma_data_aggregated.csv')
        if 'month_year' in df.columns:
            df['month_year'] = pd.to_datetime(df['month_year'], errors='coerce')
        return df
