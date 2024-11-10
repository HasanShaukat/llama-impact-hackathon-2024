import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Kosovo Municipality Complaints Dashboard", 
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Ensure light theme
st.markdown("""
    <script>
        var elements = window.parent.document.getElementsByTagName('html');
        elements[0].setAttribute('data-theme', 'light');
    </script>
    """, unsafe_allow_html=True)

# Custom CSS for light theme
st.markdown("""
    <style>
        .main {
            padding: 1rem 2rem;
            background-color: white;
        }
        .stMetric {
            background-color: #f8f9fa;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 5px solid #4CAF50;
            transition: transform 0.2s ease;
        }
        .stMetric:hover {
            transform: translateY(-2px);
        }
        .stMetric label {
            color: #495057;
            font-size: 0.875rem;
        }
        .stMetric .value {
            color: #212529;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .stPlotlyChart {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        }
        .stSelectbox, .stMultiSelect {
            background-color: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        }
        h1, h2, h3 {
            color: #212529;
        }
        .stSidebar {
            background-color: white;
            padding: 2rem 1rem;
            border-right: 1px solid #dee2e6;
        }
        .stDataFrame {
            background-color: #f8f9fa;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🏛️ Kosovo Municipality Complaints Dashboard")

# Create tabs
tab1, tab2 = st.tabs(["📊 Analytics Dashboard", "🤖 Q&A Interface"])

# Load data and initialize OpenAI
@st.cache_data
def load_data():
    df = pd.read_csv("sample_data.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_resource
def init_openai():
    return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

df = load_data()
client = init_openai()

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
    # Time series of complaints with trend (Daily)
    daily_complaints = filtered_df.groupby(pd.Grouper(key='date', freq='D')).size().reset_index(name='count')
    fig = px.line(daily_complaints, x='date', y='count',
                  title='Daily Complaints Trend Analysis',
                  labels={'count': 'Number of Complaints', 'date': 'Date'})
    
    # Update line color and thickness
    fig.update_traces(line=dict(color='#2E86C1', width=2))
    
    # Format x-axis to show dates properly
    fig.update_xaxes(
        tickformat="%Y-%m-%d",
        tickmode='auto',
        nticks=10
    )
    
    # Add trend line
    fig.add_trace(go.Scatter(
        x=daily_complaints['date'],
        y=daily_complaints['count'].rolling(window=7).mean(),
        name='7-day Moving Average',
        line=dict(color='#E74C3C', width=2, dash='dash')
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
    st.plotly_chart(fig, use_container_width=True, key="daily_complaints_1")

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
    st.plotly_chart(fig, use_container_width=True, key="category_dist_1")

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
    st.plotly_chart(fig, use_container_width=True, key="severity_dist_1")

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
    st.plotly_chart(fig, use_container_width=True, key="municipality_analysis_1")

# Tab 1 - Analytics Dashboard
with tab1:
    st.markdown("### Interactive Analytics Dashboard")
    
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
        # Time series of complaints with trend (Daily)
        daily_complaints = filtered_df.groupby(pd.Grouper(key='date', freq='D')).size().reset_index(name='count')
        fig = px.line(daily_complaints, x='date', y='count',
                    title='Daily Complaints Trend Analysis',
                    labels={'count': 'Number of Complaints', 'date': 'Date'})
        
        fig.update_traces(line=dict(color='#2E86C1', width=2))
        fig.update_xaxes(tickformat="%Y-%m-%d", tickmode='auto', nticks=10)
        
        fig.add_trace(go.Scatter(
            x=daily_complaints['date'],
            y=daily_complaints['count'].rolling(window=7).mean(),
            name='7-day Moving Average',
            line=dict(color='#E74C3C', width=2, dash='dash')
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
        st.plotly_chart(fig, use_container_width=True, key="daily_complaints_2")

    with col2:
        # Category distribution
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
        st.plotly_chart(fig, use_container_width=True, key="category_dist_2")

    # Row 2 - Severity distribution and municipality comparison
    col1, col2 = st.columns(2)

    with col1:
        # Severity distribution
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
        st.plotly_chart(fig, use_container_width=True, key="severity_dist_2")

    with col2:
        # Municipality comparison
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
        st.plotly_chart(fig, use_container_width=True, key="municipality_analysis_2")

    # Detailed complaints table
    st.subheader("Detailed Complaints")
    cols_to_show = ['date', 'municipality', 'category', 'severity_score', 'complaint_en']
    st.dataframe(
        filtered_df[cols_to_show].sort_values('date', ascending=False),
        use_container_width=True,
        height=400
    )

# Tab 2 - Q&A Interface
with tab2:
    st.markdown("### Chat with AI About the Complaints Data")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the complaints data"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Create context from filtered data
        context = f"""
        Analysis context:
        - Time period: {date_range[0]} to {date_range[1]}
        - Total complaints: {len(filtered_df)}
        - Categories: {', '.join(filtered_df['category'].unique())}
        - Municipalities: {', '.join(filtered_df['municipality'].unique())}
        - Average severity: {filtered_df['severity_score'].mean():.2f}
        
        Detailed complaints:
        {filtered_df[['date', 'municipality', 'category', 'severity_score', 'complaint_en']].to_string()}
        """

        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """You are an analyst for the Kosovo Municipality Complaints system.
                         Analyze the provided complaints data and answer questions clearly and concisely.
                         Focus on providing actionable insights and clear patterns in the data."""},
                        {"role": "user", "content": f"Based on this data:\n{context}\n\nQuestion: {prompt}"}
                    ],
                    temperature=0.3
                )
                response_content = response.choices[0].message.content
                st.markdown(response_content)
                
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_content})
