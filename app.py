import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LA Crime Risk Assessment", layout="wide")

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv("crime_data.csv")
    
    # Clean and filter necessary fields
    df = df[df['Vict Age'].notna() & df['LAT'].notna() & df['LON'].notna()]
    df['Vict Age'] = df['Vict Age'].astype(int)
    df['DATE OCC'] = pd.to_datetime(df['DATE OCC'], errors='coerce')
    df['Hour'] = df['TIME OCC'] // 100

    # Time of Day bucket
    def get_time_of_day(hour):
        if 0 <= hour < 6:
            return 'Late Night'
        elif 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        else:
            return 'Evening'

    df['Time of Day'] = df['Hour'].apply(get_time_of_day)
    return df

df = load_data()

# UI
st.title("🔍 LA Crime Risk Assessment")
st.markdown("Estimate crime risk based on **victim demographics, location, and time of day** using LAPD data (2020–present).")

# Sidebar filters
st.sidebar.header("Select Victim Info")
age = st.sidebar.slider("Age", 10, 90, 25)
gender = st.sidebar.selectbox("Gender", sorted(df['Vict Sex'].dropna().unique()))
descent = st.sidebar.selectbox("Descent", sorted(df['Vict Descent'].dropna().unique()))
location = st.sidebar.selectbox("Location (Area)", sorted(df['AREA NAME'].dropna().unique()))
time_of_day = st.sidebar.selectbox("Time of Day", ['Morning', 'Afternoon', 'Evening', 'Late Night'])

# Risk score logic
def calculate_risk_score(df, age, gender, descent, location, time_of_day):
    filtered = df[
        (df['Vict Sex'] == gender) &
        (df['Vict Descent'] == descent) &
        (df['AREA NAME'] == location) &
        (df['Time of Day'] == time_of_day) &
        (df['Vict Age'].between(age - 5, age + 5))
    ]
    total_incidents = df.shape[0]
    filtered_count = filtered.shape[0]
    score = int((filtered_count / total_incidents) * 1000)  # scaled score
    score = min(score, 100)
    return score, filtered

# Compute and display results
score, filtered_df = calculate_risk_score(df, age, gender, descent, location, time_of_day)

st.subheader("🎯 Risk Score")
st.metric(label="Estimated Crime Risk", value=f"{score} / 100")
st.progress(score / 100)

# Crime breakdown
st.subheader("📊 Top 5 Crimes in Selected Group")
top_crimes = filtered_df['Crm Cd Desc'].value_counts().head(5)
st.bar_chart(top_crimes)

# Map
st.subheader("🗺️ Crime Locations Map")
if not filtered_df[['LAT', 'LON']].dropna().empty:
    st.map(filtered_df[['LAT', 'LON']].dropna().rename(columns={'LAT': 'lat', 'LON': 'lon'}))
else:
    st.info("No crimes found for the selected criteria.")


