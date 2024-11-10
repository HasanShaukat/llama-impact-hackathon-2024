import streamlit as st
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Complaint Management System",
    page_icon="📝",
    layout="wide"
)

# Title and description
st.title("Complaint Management System")
st.markdown("A simple system to manage and track complaints")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Submit Complaint", "View Complaints"])

if page == "Submit Complaint":
    st.header("Submit a New Complaint")
    
    # Complaint form
    with st.form("complaint_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Email")
        category = st.selectbox(
            "Complaint Category",
            ["Product", "Service", "Staff", "Other"]
        )
        severity = st.select_slider(
            "Severity Level",
            options=["Low", "Medium", "High", "Critical"]
        )
        description = st.text_area("Complaint Description")
        
        submitted = st.form_submit_button("Submit Complaint")
        
        if submitted:
            # Create a new complaint entry
            new_complaint = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "name": name,
                "email": email,
                "category": category,
                "severity": severity,
                "description": description,
                "status": "New"
            }
            
            # Load existing complaints or create new DataFrame
            try:
                df = pd.read_csv("complaints.csv")
            except FileNotFoundError:
                df = pd.DataFrame(columns=new_complaint.keys())
            
            # Append new complaint
            df = pd.concat([df, pd.DataFrame([new_complaint])], ignore_index=True)
            df.to_csv("complaints.csv", index=False)
            
            st.success("Complaint submitted successfully!")

else:  # View Complaints page
    st.header("View Complaints")
    
    try:
        # Load and display complaints
        df = pd.read_csv("complaints.csv")
        
        # Filters
        st.subheader("Filters")
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.multiselect(
                "Filter by Category",
                options=df['category'].unique()
            )
        with col2:
            severity_filter = st.multiselect(
                "Filter by Severity",
                options=df['severity'].unique()
            )
        
        # Apply filters
        filtered_df = df.copy()
        if category_filter:
            filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
        if severity_filter:
            filtered_df = filtered_df[filtered_df['severity'].isin(severity_filter)]
        
        # Display complaints
        st.dataframe(filtered_df)
        
    except FileNotFoundError:
        st.info("No complaints submitted yet.")
