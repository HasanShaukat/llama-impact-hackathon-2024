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
            background-color: #f8f9fa;
        }
        .stMetric {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            border-left: 5px solid #4CAF50;
        }
        .stMetric label {
            color: #666;
            font-size: 0.875rem;
        }
        .stMetric .value {
            color: #2c3e50;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .stPlotlyChart {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }
        .stSelectbox, .stMultiSelect {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .stSidebar {
            background-color: #f8f9fa;
            padding: 2rem 1rem;
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

# Category filter with "Select All" option
all_categories = sorted(df['category'].unique())
if st.sidebar.checkbox("Select All Categories", value=True):
    categories = all_categories
else:
    categories = st.sidebar.multiselect(
        "Select Categories",
        options=all_categories,
        default=[]
    )

# Municipality filter with "Select All" option  
all_municipalities = sorted(df['municipality'].unique())
if st.sidebar.checkbox("Select All Municipalities", value=True):
    municipalities = all_municipalities
else:
    municipalities = st.sidebar.multiselect(
        "Select Municipalities", 
        options=all_municipalities,
        default=[]
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
    # Time series of complaints with trend
    daily_complaints = filtered_df.groupby('date').size().reset_index(name='count')
    fig = px.line(daily_complaints, x='date', y='count',
                  title='Daily Complaints Trend Analysis',
                  labels={'count': 'Number of Complaints', 'date': 'Date'})
    
    # Add trend line
    fig.add_trace(go.Scatter(
        x=daily_complaints['date'],
        y=daily_complaints['count'].rolling(window=7).mean(),
        name='7-day Moving Average',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        height=400,
        template='plotly_white',
        hovermode='x unified',
        title_x=0.5,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Category distribution with better styling
    category_counts = filtered_df['category'].value_counts()
    fig = px.pie(values=category_counts.values,
                 names=category_counts.index,
                 title='Complaint Categories Distribution',
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Set3)
    
    fig.update_layout(
        height=400,
        template='plotly_white',
        title_x=0.5,
        legend=dict(orientation="h", y=-0.2)
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

# Row 2 - Severity distribution and municipality comparison
col1, col2 = st.columns(2)

with col1:
    # Enhanced severity distribution
    fig = px.histogram(filtered_df, x='severity_score',
                      title='Severity Score Distribution Analysis',
                      labels={'severity_score': 'Severity Score', 'count': 'Number of Complaints'},
                      nbins=20,
                      color_discrete_sequence=['#3498db'])
    
    fig.add_vline(x=filtered_df['severity_score'].mean(), 
                  line_dash="dash", 
                  line_color="red",
                  annotation_text=f"Mean: {filtered_df['severity_score'].mean():.2f}")
    
    fig.update_layout(
        height=400,
        template='plotly_white',
        title_x=0.5,
        bargap=0.1,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Enhanced municipality comparison
    municipality_stats = filtered_df.groupby('municipality').agg({
        'severity_score': ['mean', 'count']
    }).reset_index()
    municipality_stats.columns = ['municipality', 'avg_severity', 'complaint_count']
    municipality_stats = municipality_stats.sort_values('avg_severity', ascending=True)

    fig = px.bar(municipality_stats, 
                 x='avg_severity',
                 y='municipality',
                 title='Municipality Severity Analysis',
                 labels={'avg_severity': 'Average Severity Score', 'municipality': 'Municipality'},
                 orientation='h',
                 color='complaint_count',
                 color_continuous_scale='Viridis')
    
    fig.update_layout(
        height=400,
        template='plotly_white',
        title_x=0.5,
        coloraxis_colorbar_title="Number of Complaints"
    )
    st.plotly_chart(fig, use_container_width=True)

# Detailed complaints table
st.subheader("Detailed Complaints")
cols_to_show = ['date', 'municipality', 'category', 'severity_score', 'complaint_en']
st.dataframe(
    filtered_df[cols_to_show].sort_values('date', ascending=False),
    use_container_width=True,
    height=400
)
