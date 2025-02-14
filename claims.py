
import streamlit as st
import json
import bcrypt
import pandas as pd
import altair as alt
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime





st.set_page_config(
    page_title="Eden Care Claims Dashboard",
    page_icon=Image.open("logo.png"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load users from the JSON file
def load_users():
    with open('users.json', 'r') as file:
        return json.load(file)['users']

# Function to authenticate a user
def authenticate(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return True
    return False




# Main script: claims.py
if 'df' not in st.session_state:
    # Load your dataset here
    filepath_visits = "Claims.xlsx"
    sheet_name1 = "2023 claims"
    sheet_name2 = "2024 claims"

    # Read the Claims data
    dfc_2023 = pd.read_excel(filepath_visits, sheet_name=sheet_name1)
    dfc_2024 = pd.read_excel(filepath_visits, sheet_name=sheet_name2)

    # Read the visit logs
    df = pd.concat([dfc_2023, dfc_2024])
    st.session_state['df'] = df

# Calculate IQR-based bounds for outliers
column = 'Claim Amount'  # Replace with the appropriate column name
Q1 = st.session_state['df'][column].quantile(0.25)
Q3 = st.session_state['df'][column].quantile(0.75)
IQR = Q3 - Q1

# Define mild and extreme outlier bounds
mild_lower = Q1 - 1.5 * IQR
mild_upper = Q3 + 1.5 * IQR
extreme_lower = Q1 - 3 * IQR
extreme_upper = Q3 + 3 * IQR

# Store the bounds in session state
st.session_state['mild_lower'] = mild_lower
st.session_state['mild_upper'] = mild_upper
st.session_state['extreme_lower'] = extreme_lower
st.session_state['extreme_upper'] = extreme_upper

# Dictionary to map month names to their order
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}
current_date = datetime.now()
sorted_months = sorted(df['Month'].dropna().unique(), key=lambda x: pd.to_datetime(x, format='%B').month)


# Function to display the dashboard
def display_dashboard(username):
    # SIDEBAR FILTER
    logo_url = 'EC_logo.png'  
    st.sidebar.image(logo_url, use_column_width=True)

    page = st.sidebar.selectbox("Choose a dashboard", ["Home", "Overview", "Claims Analysis", "Claims Analysis - Fraud", "Claims Analysis - Loss Ratio", "Product View", "Claim Type View"])

    st.markdown(
        """
        <style>
        .reportview-container {
            background-color: #013220;
            color: white;
        }
        .sidebar .sidebar-content {
            background-color: #013220;
            color: white;
        }
        .main-title {
            color: #e66c37; /* Title color */
            text-align: center; /* Center align the title */
            font-size: 3rem; /* Title font size */
            font-weight: bold; /* Title font weight */
            margin-bottom: .5rem; /* Space below the title */
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1); /* Subtle text shadow */
        }
        div.block-container {
            padding-top: 2rem; /* Padding for main content */
        }
        .subheader {
            color: #e66c37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            display: inline-block;
        }
        .section-title {
            font-size: 1.75rem;
            color: #004d99;
            margin-top: 2rem;
            margin-bottom: 0.5rem;
        }
        .text {
            font-size: 1.1rem;
            color: #333;
            padding: 10px;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        .nav-item {
            font-size: 1.2rem;
            color: #004d99;
            margin-bottom: 0.5rem;
        }
        .separator {
            margin: 2rem 0;
            border-bottom: 2px solid #ddd;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if page == "Home":
        st.markdown('<h1 class="main-title">EDEN CARE CLAIMS MANAGEMENT DASHBOARD</h1>', unsafe_allow_html=True)
        st.image("Tiny doctor giving health insurance.jpg", caption='Eden Care Medical', use_column_width=True)
        st.markdown('<h2 class="subheader">Welcome to the Eden Care Claims Management Dashboard</h2>', unsafe_allow_html=True)

        # Introduction
        st.markdown(
            """
            <div class="text">
                This comprehensive tool provides a clear and insightful 
                overview of our claims management performance across several key areas: 
                <strong>Claims Overview, Claims Analysis, Fraud Detection, Loss Ratio Analysis, and Claim Type Insights</strong>. 
                <br><br>
                - The <strong>Claims Overview</strong> offers a high-level summary of all claims processed.
                - The <strong>Claims Analysis</strong> dives deeper into claim details, providing insights into trends and patterns.
                - The <strong>Fraud Detection</strong> section helps identify potential fraudulent claims using advanced analytics.
                - The <strong>Loss Ratio Analysis</strong> evaluates the financial performance of claims processing by analyzing the ratio of claims paid to premiums earned.
                - The <strong>Claim Type View</strong> categorizes claims by type, offering insights into common claim categories and their impact.
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

        # User Instructions
        st.markdown('<h2 class="subheader">User Instructions</h2>', unsafe_allow_html=True)
        st.markdown('<div class="text">1. <strong>Navigation:</strong> Use the menu on the left to navigate between visits, claims and Preauthorisation dashboards.</div>', unsafe_allow_html=True)
        st.markdown('<div class="text">2. <strong>Filters:</strong> Apply filters on the left side of each page to customize the data view.</div>', unsafe_allow_html=True)
        st.markdown('<div class="text">3. <strong>Manage visuals:</strong> Hover over the visuals and use the options on the top right corner of each visual to download zoom or view on fullscreen</div>', unsafe_allow_html=True)
        st.markdown('<div class="text">3. <strong>Manage Table:</strong> click on the dropdown icon (<img src="https://img.icons8.com/ios-glyphs/30/000000/expand-arrow.png"/>) on table below each visual to get a full view of the table data and use the options on the top right corner of each table to download or search and view on fullscreen.</div>', unsafe_allow_html=True)    
        st.markdown('<div class="text">4. <strong>Refresh Data:</strong> The data will be manually refreshed on the last week of every quarter. </div>', unsafe_allow_html=True)
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

        

    elif page == "Overview":
        exec(open("overview.py").read())
    elif page == "Claims Analysis":
        exec(open("claim_analysis.py").read())
    elif page == "Claims Analysis - Loss Ratio":
        exec(open("loss_ratio.py").read())
    elif page == "Product View":
        exec(open("product.py").read())
    elif page == "Claim Type View":
        exec(open("claim_type.py").read())
    elif page == "Claims Analysis - Fraud":
        exec(open("fraud.py", encoding="utf-8").read())   


# Streamlit app
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""

    if st.session_state['logged_in']:
        display_dashboard(st.session_state['username'])
    else:
        st.title("Login Page")

        username = st.text_input("Enter username")
        password = st.text_input("Enter password", type="password")
        
        st.markdown('<div class="text">Please double-click on the login or logout button </div>', unsafe_allow_html=True)
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Authentication successful")
                st.experimental_rerun()
            else:
                st.error("Authentication failed")

if __name__ == "__main__":
    main()
