import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Kosovo Municipality Complaints Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            padding: 0rem 1rem;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        .stPlotlyChart {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🏛️ Kosovo Municipality Complaints Dashboard")
st.markdown("Interactive analytics dashboard for monitoring and analyzing public complaints")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("sample_data.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['date'].min(), df['date'].max()],
    min_value=df['date'].min(),
    max_value=df['date'].max()
)

# Category filter
categories = st.sidebar.multiselect(
    "Select Categories",
    options=sorted(df['category'].unique()),
    default=sorted(df['category'].unique())
)

# Municipality filter
municipalities = st.sidebar.multiselect(
    "Select Municipalities",
    options=sorted(df['municipality'].unique()),
    default=sorted(df['municipality'].unique())
)

# Apply filters
mask = (
    (df['date'].dt.date >= date_range[0]) & 
    (df['date'].dt.date <= date_range[1]) &
    (df['category'].isin(categories)) &
    (df['municipality'].isin(municipalities))
)
filtered_df = df[mask]

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Complaints", len(filtered_df))
with col2:
    avg_severity = round(filtered_df['severity_score'].mean(), 2)
    st.metric("Average Severity", avg_severity)
with col3:
    high_severity = len(filtered_df[filtered_df['severity_score'] >= 7])
    st.metric("High Severity Cases", high_severity)
with col4:
    municipalities_count = filtered_df['municipality'].nunique()
    st.metric("Municipalities", municipalities_count)

# Charts
st.subheader("Complaint Analytics")

# Row 1 - Time series and category distribution
col1, col2 = st.columns(2)

with col1:
    # Time series of complaints
    daily_complaints = filtered_df.groupby('date').size().reset_index(name='count')
    fig = px.line(daily_complaints, x='date', y='count',
                  title='Daily Complaints Over Time',
                  labels={'count': 'Number of Complaints', 'date': 'Date'})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Category distribution
    category_counts = filtered_df['category'].value_counts()
    fig = px.pie(values=category_counts.values, 
                 names=category_counts.index,
                 title='Complaints by Category')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Row 2 - Severity distribution and municipality comparison
col1, col2 = st.columns(2)

with col1:
    # Severity distribution
    fig = px.histogram(filtered_df, x='severity_score',
                      title='Distribution of Severity Scores',
                      labels={'severity_score': 'Severity Score'},
                      nbins=20)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Municipality comparison
    municipality_avg_severity = filtered_df.groupby('municipality')['severity_score'].mean().sort_values(ascending=True)
    fig = px.bar(x=municipality_avg_severity.values,
                 y=municipality_avg_severity.index,
                 title='Average Severity by Municipality',
                 labels={'x': 'Average Severity Score', 'y': 'Municipality'},
                 orientation='h')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Detailed complaints table
st.subheader("Detailed Complaints")
cols_to_show = ['date', 'municipality', 'category', 'severity_score', 'complaint_en']
st.dataframe(
    filtered_df[cols_to_show].sort_values('date', ascending=False),
    use_container_width=True,
    height=400
)
