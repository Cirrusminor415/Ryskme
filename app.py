import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# Set up OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="LA Crime Risk Assessment", layout="wide")

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv("crime_data.csv")
    df = df[df['Vict Age'].notna() & df['LAT'].notna() & df['LON'].notna()]
    df['Vict Age'] = df['Vict Age'].astype(int)
    df['DATE OCC'] = pd.to_datetime(df['DATE OCC'], errors='coerce')
    df['Hour'] = df['TIME OCC'] // 100

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
    df['Year'] = df['DATE OCC'].dt.year
    df['Month'] = df['DATE OCC'].dt.to_period('M').astype(str)
    return df

df = load_data()

# Sidebar filters with "All" options
st.sidebar.header("🔎 Select Victim Info")
age = st.sidebar.slider("Age", 10, 90, 25)
gender = st.sidebar.selectbox("Gender", ['All'] + sorted(df['Vict Sex'].dropna().unique()))
descent = st.sidebar.selectbox("Descent", ['All'] + sorted(df['Vict Descent'].dropna().unique()))
location = st.sidebar.selectbox("Location (Area)", ['All'] + sorted(df['AREA NAME'].dropna().unique()))
time_of_day = st.sidebar.selectbox("Time of Day", ['All', 'Morning', 'Afternoon', 'Evening', 'Late Night'])

# Risk calculation
def calculate_risk_score(df, age, gender, descent, location, time_of_day):
    filtered = df.copy()
    if gender != 'All':
        filtered = filtered[filtered['Vict Sex'] == gender]
    if descent != 'All':
        filtered = filtered[filtered['Vict Descent'] == descent]
    if location != 'All':
        filtered = filtered[filtered['AREA NAME'] == location]
    if time_of_day != 'All':
        filtered = filtered[filtered['Time of Day'] == time_of_day]
    filtered = filtered[filtered['Vict Age'].between(age - 5, age + 5)]

    total_incidents = df.shape[0]
    filtered_count = filtered.shape[0]
    score = int((filtered_count / total_incidents) * 1000)
    score = min(score, 100)
    return score, filtered

# AI-generated explanation
def generate_narrative(age, gender, descent, location, time_of_day, score, top_crimes):
    crimes_list = ', '.join(top_crimes.index.tolist())
    prompt = f"""
    Generate a short, plain-English summary of crime risk.

    Age: {age}
    Gender: {gender}
    Descent: {descent}
    Location: {location}
    Time of Day: {time_of_day}
    Risk Score: {score}/100
    Top Crimes: {crimes_list}

    Keep it concise, clear, and user-friendly. Mention the risk level and the common crimes.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI explanation failed: {str(e)}"

# Compute score and results
score, filtered_df = calculate_risk_score(df, age, gender, descent, location, time_of_day)

# UI
st.title("🔍 LA Crime Risk Assessment")
st.markdown("Estimate crime risk based on **victim demographics, location, and time of day** using LAPD data (2020–present).")

st.subheader("🎯 Risk Score")
st.metric(label="Estimated Crime Risk", value=f"{score} / 100")
st.progress(score / 100)

# AI Narrative
st.subheader("🧠 AI Insight")
top_crimes = filtered_df['Crm Cd Desc'].value_counts().head(5)
if not top_crimes.empty:
    explanation = generate_narrative(age, gender, descent, location, time_of_day, score, top_crimes)
    st.write(explanation)
else:
    st.write("Not enough data to generate an insight.")

# Top crimes
st.subheader("📊 Top 5 Crimes in Selected Group")
if not top_crimes.empty:
    st.bar_chart(top_crimes)
else:
    st.info("No crime data for this group.")

# Map
st.subheader("🗺️ Crime Locations Map")
if not filtered_df[['LAT', 'LON']].dropna().empty:
    st.map(filtered_df[['LAT', 'LON']].dropna().rename(columns={'LAT': 'lat', 'LON': 'lon'}))
else:
    st.info("No location data for selected criteria.")

# Historical trend
st.subheader("📈 Historical Trend of Similar Crimes (Monthly)")
if not filtered_df.empty:
    trend = filtered_df.groupby('Month').size().reset_index(name='Crime Count')
    trend = trend.sort_values('Month')
    fig = px.line(trend, x='Month', y='Crime Count', markers=True,
                  title='Crime Trend Over Time',
                  labels={'Month': 'Month', 'Crime Count': 'Number of Crimes'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available to show trend.")
