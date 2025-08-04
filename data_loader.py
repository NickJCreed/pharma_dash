import streamlit as st
import pandas as pd

def load_data():
    if 'uploaded_df' in st.session_state:
        df = st.session_state['uploaded_df']
        if 'month_year' in df.columns:
            df['month_year'] = pd.to_datetime(df['month_year'], errors='coerce')
        return df
    else:
        try:
            df = pd.read_csv('pharma_data_aggregated.csv')
            if 'month_year' in df.columns:
                df['month_year'] = pd.to_datetime(df['month_year'], errors='coerce')
            return df
        except FileNotFoundError:
            # No fallback file found — just return None gracefully
            return None
