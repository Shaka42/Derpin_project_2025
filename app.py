import streamlit as st
import pandas as pd
import plotly.express as px
import os
from functools import reduce

st.set_page_config(page_title="DERPIn Vulnerability Explorer", layout="wide")
st.title("DERPIn Community Vulnerability Explorer")

# --- Data Loading Functions ---
@st.cache_data
def load_merged_nutrients():
    try:
        df = pd.read_csv('merged_nutrients.csv')
        return df
    except Exception as e:
        st.error(f"Could not load merged_nutrients.csv: {e}")
        return None

@st.cache_data
def load_merged_index():
    try:
        df = pd.read_csv('merged_index.csv')
        return df
    except Exception as e:
        st.error(f"Could not load merged_index.csv: {e}")
        return None

nutrients = load_merged_nutrients()
index = load_merged_index()

# --- Sidebar Navigation ---
page = st.sidebar.radio(
    "Select Analysis",
    [
        "Composite Vulnerability",
        "Health System Vulnerability",
        "Food Security",
        "Climate Change Vulnerability",
        "Nutrient Table"
    ]
)

# --- Composite Vulnerability ---
if page == "Composite Vulnerability":
    st.header("Composite Vulnerability Index by Region")
    if index is not None and 'Composite Vulnerability Index' in index.columns:
        composite = index[['Region','Composite Vulnerability Index']].drop_duplicates(subset=['Region']).sort_values(by='Composite Vulnerability Index', ascending=False).reset_index(drop=True)
        fig = px.bar(
            composite,
            x="Region",
            y="Composite Vulnerability Index",
            color="Composite Vulnerability Index",
            title="Composite Vulnerability Index by Region"
        )
        fig.update_layout(xaxis_tickangle=-45, coloraxis_colorbar=dict(title="Vulnerability Index"))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(composite)
    else:
        st.warning("Composite Vulnerability Index data not available.")

# --- Health System Vulnerability ---
elif page == "Health System Vulnerability":
    st.header("Health System Vulnerability Index by Region")
    if index is not None and 'Health System Vulnerability Index' in index.columns:
        health = index[['Region','Health System Vulnerability Index']].drop_duplicates(subset=['Region']).sort_values(by='Health System Vulnerability Index', ascending=False).reset_index(drop=True)
        fig = px.scatter(
            health,
            x="Health System Vulnerability Index",
            y="Region",
            size="Health System Vulnerability Index",
            color="Health System Vulnerability Index",
            title="Health System Vulnerability Index by Region"
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(health)
    else:
        st.warning("Health System Vulnerability Index data not available.")

# --- Food Security ---
elif page == "Food Security":
    st.header("Nutrition Adequacy vs Food Consumption by Region")
    if index is not None and 'Mean Adequacy Ratio Index' in index.columns and 'Per Capita Food Consumption Index' in index.columns:
        food_sec = index[['Region','Mean Adequacy Ratio Index','Per Capita Food Consumption Index']].drop_duplicates(subset=['Region']).reset_index(drop=True)
        fig = px.scatter(
            food_sec,
            x='Per Capita Food Consumption Index',
            y='Mean Adequacy Ratio Index',
            color='Region',
            hover_data=['Region'],
            title='Nutrition Adequacy vs Food Consumption by Region'
        )
        fig.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=2, color='DarkSlateGrey')))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(food_sec)
    else:
        st.warning("Food security data not available.")

# --- Climate Change Vulnerability ---
elif page == "Climate Change Vulnerability":
    st.header("Vulnerability to Climate Change Index by Region")
    if index is not None and 'Vulnerability to Climate Change Index' in index.columns:
        climate = index[['Region','Vulnerability to Climate Change Index']].drop_duplicates(subset=['Region']).sort_values(by='Vulnerability to Climate Change Index', ascending=False).reset_index(drop=True)
        fig = px.bar(
            climate,
            x="Region",
            y="Vulnerability to Climate Change Index",
            color="Vulnerability to Climate Change Index",
            title="Vulnerability to Climate Change Index by Region"
        )
        fig.update_layout(xaxis_tickangle=-45, coloraxis_colorbar=dict(title="Vulnerability Index"))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(climate)
    else:
        st.warning("Climate Change Vulnerability Index data not available.")

# --- Nutrient Table ---
elif page == "Nutrient Table":
    st.header("Merged Nutrient Data Table")
    if nutrients is not None:
        st.dataframe(nutrients)
    else:
        st.warning("Nutrient data not available.")
