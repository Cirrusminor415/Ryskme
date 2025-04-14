import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LA Crime Risk Assessment", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("crime_data.csv")
    df = df[df['Vict Age'].notna() & df['LAT'].notna() & df['LON'].notna()]
    df['Vict Age'] = df['Vict Age'].astype(int)
    return df

df = load_data()

st.title("🔍 LA Crime Risk Assessment")
st.markdown("Estimate crime risk based on **victim demographics and location** using LAPD data (2020–present).")

# Sidebar filters
st.sidebar.header("Select Victim Info")
age = st.sidebar.slider("Age", 10, 90, 25)
gender = st.sidebar.selectbox("Gender", sorted(df['Vict Sex'].dropna().unique()))
descent = st.sidebar.selectbox("Descent", sorted(df['Vict Descent'].dropna().unique()))
location = st.sidebar.selectbox("Location (Area)", sorted(df['AREA NAME'].dropna().unique()))

# Filter logic
def calculate_risk_score(df, age, gender, descent, location):
    filtered = df[
        (df['Vict Sex'] == gender) &
        (df['Vict Descent'] == descent) &
        (df['AREA NAME'] == location) &
        (df['Vict Age'].between(age - 5, age + 5))
    ]
    total_incidents = df.shape[0]
    filtered_count = filtered.shape[0]
    score = int((filtered_count / total_incidents) * 1000)  # scaled score
    score = min(score, 100)
    return score, filtered

score, filtered_df = calculate_risk_score(df, age, gender, descent, location)

# Display score
st.subheader("🎯 Risk Score")
st.metric(label="Estimated Crime Risk", value=f"{score} / 100")

# Gauge-like bar
st.progress(score / 100)

# Top crimes
st.subheader("📊 Top 5 Crimes in Selected Group")
top_crimes = filtered_df['Crm Cd Desc'].value_counts().head(5)
st.bar_chart(top_crimes)

# Map
st.subheader("🗺️ Crime Locations Map")
st.map(filtered_df[['LAT', 'LON']].dropna().rename(columns={'LAT': 'lat', 'LON': 'lon'}))
