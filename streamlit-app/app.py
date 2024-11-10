import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from together import Together
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Municipality Insights Hub", 
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Municipality Insights Hub - Powered by AI"
    }
)

# Ensure light theme
st.markdown("""
    <script>
        var elements = window.parent.document.getElementsByTagName('html');
        elements[0].setAttribute('data-theme', 'light');
    </script>
    """, unsafe_allow_html=True)

# Custom CSS for modern theme
st.markdown("""
    <style>
        /* Global Styles */
        .main {
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            padding: 2rem;
            font-family: 'Inter', sans-serif;
        }
        
        /* Header Styles */
        h1, h2, h3 {
            color: #2c4356;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        /* Metric Card Styles */
        .stMetric {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 5px 5px 15px #e8e9eb, -5px -5px 15px #ffffff;
            border: 1px solid rgba(255,255,255,0.18);
            border-left: 4px solid #2c4356;
            transition: all 0.3s ease;
        }
        .stMetric:hover {
            transform: translateY(-5px);
            box-shadow: 8px 8px 20px #e8e9eb, -8px -8px 20px #ffffff;
            border: 1px solid #2c4356;
            border-left: 4px solid #2c4356;
        }
        .stMetric label {
            color: #5b7a95;
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stMetric .value {
            color: #2c4356;
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 0.5rem;
        }
        
        /* Chart Styles */
        .stPlotlyChart {
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid rgba(255,255,255,0.18);
            margin: 1rem 0;
        }
        
        /* Sidebar Styles */
        .stSidebar {
            background: linear-gradient(180deg, #2c4356 0%, #435668 100%);
            padding: 2rem 1.5rem;
            color: white;
        }
        .stSidebar [data-testid="stMarkdownContainer"] {
            color: #ffffff;
        }
        .stSidebar .stSelectbox, .stSidebar .stMultiSelect {
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Input Elements */
        .stSelectbox, .stMultiSelect {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid #e9ecef;
        }
        
        /* DataFrame Styling */
        .stDataFrame {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            padding: 1rem;
        }
        
        /* Chat Interface Styling */
        .stChatMessage {
            background: white;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            padding: 1rem;
            margin: 0.5rem 0;
            border: 1px solid #e9ecef;
        }
        
        /* Button Styling */
        .stButton button {
            background: linear-gradient(135deg, #2c4356 0%, #435668 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(44,67,86,0.2);
        }
    </style>
""", unsafe_allow_html=True)

# Title with custom HTML
st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2c4356; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;'>
            🏛️ Municipality Insights Hub
        </h1>
        <p style='color: #5b7a95; font-size: 1.1rem; font-weight: 400;'>
            Transforming Municipal Feedback into Actionable Intelligence
        </p>
    </div>
""", unsafe_allow_html=True)

# Create tabs with modern naming
tab1, tab2 = st.tabs(["📊 Analytics Dashboard", "🤖 Complaint Copilot"])

# Load data and initialize OpenAI
@st.cache_data
def load_data():
    df = pd.read_csv("sample_data.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_resource
def init_together():
    return Together(api_key=os.getenv('TOGETHER_API_KEY'))

df = load_data()
client = init_together()

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


# Tab 1 - Analytics Dashboard
with tab1:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h3 style='color: #2c4356; font-size: 1.8rem; font-weight: 600;'>
                Interactive Analytics Dashboard
            </h3>
            <p style='color: #5b7a95; font-size: 1rem;'>
                Real-time insights and analysis of municipal feedback
            </p>
        </div>
    """, unsafe_allow_html=True)
    
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
    prompt = st.chat_input("Ask a question about the complaints data")
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h3 style='color: #2c4356; font-size: 1.8rem; font-weight: 600;'>
                Complaint Copilot
            </h3>
            <p style='color: #5b7a95; font-size: 1rem;'>
                Your AI-powered assistant for deep complaint analysis
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt:
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
                    model="meta-llama/Llama-3-8b-chat-hf",
                    messages=[
                        {"role": "system", "content": """You are an analyst for the Kosovo Municipality Complaints system.
                         Analyze the provided complaints data and answer questions clearly and concisely.
                         Focus on providing actionable insights and clear patterns in the data."""},
                        {"role": "user", "content": f"Based on this data:\n{context}\n\nQuestion: {prompt}"}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                response_content = response.choices[0].message.content
                st.markdown(response_content)
                
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_content})
