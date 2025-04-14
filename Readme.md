# 🔍 LA Crime Risk Assessment App

This open-access Streamlit web app uses LAPD crime data to estimate the **relative risk of victimization** based on selected victim demographics and location.

🚨 Powered by real-time crime data from [data.lacity.org](https://data.lacity.org/Public-Safety/Crime-Data-from-2020-to-Present/2nrs-mtv8)

---

## 🎯 Features

- Select victim **age**, **gender**, **descent**, and **location**
- See a **risk score (0–100)** based on similar past incidents
- View top 5 crime types in your demographic group
- Visualize crime clusters on a map

---

## 🚀 How It Works

1. The app loads over 1M+ crime records from 2020 to present
2. Filters records based on your input
3. Calculates a normalized risk score based on matching incidents
4. Displays a visual breakdown and heatmap of crime activity

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/)
- LA Crime dataset from the City of LA Open Data Portal

---

## 📦 Installation (for local testing)

```bash
git clone https://github.com/your-username/la-crime-risk-app.git
cd la-crime-risk-app
pip install -r requirements.txt
streamlit run app.py
