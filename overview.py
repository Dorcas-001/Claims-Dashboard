import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import chain
from matplotlib.ticker import FuncFormatter
from datetime import datetime


# Centered and styled main title using inline styles
st.markdown('''
    <style>
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
    </style>
''', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">OVERVIEW</h1>', unsafe_allow_html=True)



filepath_visits = "Claims.xlsx"
sheet_name1 = "2023 claims"
sheet_name2 = "2024 claims"

# Read the Claims data
dfc_2023 = pd.read_excel(filepath_visits, sheet_name=sheet_name1)
dfc_2024 = pd.read_excel(filepath_visits, sheet_name=sheet_name2)

# Read the visit logs
df = pd.concat([dfc_2023, dfc_2024])


df['Claim Created Date'] = pd.to_datetime(df['Claim Created Date'], errors='coerce')

df["Employer Name"] = df["Employer Name"].str.upper()
df["Provider Name"] = df["Provider Name"].str.upper()

# Inspect the merged DataFrame

# Sidebar styling and logo
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content h2 {
        color: #007BFF; /* Change this color to your preferred title color */
        font-size: 1.5em;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-title {
        color: #e66c37;
        font-size: 1.2em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-header {
        color: #e66c37; /* Change this color to your preferred header color */
        font-size: 2.5em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-multiselect {
        margin-bottom: 15px;
    }
    .sidebar .sidebar-content .logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content .logo img {
        max-width: 80%;
        height: auto;
        border-radius: 50%;
    }
            
    </style>
    """, unsafe_allow_html=True)




# Dictionary to map month names to their order
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}
df = df[df['Month'].isin(month_order)]


# Sort months based on their order
sorted_months = sorted(df['Month'].dropna().unique(), key=lambda x: pd.to_datetime(x, format='%B').month)

df['Source'] =df['Source'].astype(str)

df['Quarter'] = "Q" + df['Claim Created Date'].dt.quarter.astype(str)

# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
quarter = st.sidebar.multiselect("Select Quarter", options=sorted(df['Quarter'].dropna().unique()))
product = st.sidebar.multiselect("Select Product", options=df['Product'].unique())
type = st.sidebar.multiselect("Select Claim Type", options=sorted(df['Claim Type'].unique()))
status = st.sidebar.multiselect("Select Claim Status", options=df['Claim Status'].unique())
source = st.sidebar.multiselect("Select Claim Provider Type", options=sorted(df['Source'].unique()))
code = st.sidebar.multiselect("Select Diagnosis Code", options=df['ICD-10 Code'].unique())
client_name = st.sidebar.multiselect("Select Employer Name", options=sorted(df['Employer Name'].dropna().unique()))
prov_name = st.sidebar.multiselect("Select Provider Name", options=sorted(df['Provider Name'].dropna().unique()))

# Apply filters to the DataFrame
if 'Year' in df.columns and year:
    df = df[df['Year'].isin(year)]
if 'Month' in df.columns and month:
    df = df[df['Month'].isin(month)]
if 'Quarter' in df.columns and quarter:
    df = df[df['Quarter'].isin(quarter)]
if 'Product' in df.columns and product:
    df = df[df['Product'].isin(product)]
if 'Claim Type' in df.columns and type:
    df = df[df['Claim Type'].isin(type)]
if 'Claim Status' in df.columns and status:
    df = df[df['Claim Status'].isin(status)]
if 'Source' in df.columns and source:
    df = df[df['Source'].isin(source)]
if 'ICD-10 Code' in df.columns and code:
    df = df[df['ICD-10 Code'].isin(code)]
if 'Employer Name' in df.columns and client_name:
    df = df[df['Employer Name'].isin(client_name)]
if 'Provider Name' in df.columns and prov_name:
    df = df[df['Provider Name'].isin(prov_name)]


# Determine the filter description
filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if type:
     filter_description += f"{', '.join(map(str, type))} "
if product:
     filter_description += f"{', '.join(map(str, product))} "
if month:
    filter_description += f"{', '.join(month)} "
if quarter:
    filter_description += f"{', '.join(quarter)} "
if not filter_description:
    filter_description = "All data"





# Get minimum and maximum dates for the date input
startDate = df["Claim Created Date"].min()
endDate = df["Claim Created Date"].max()

# Define CSS for the styled date input boxes
st.markdown("""
    <style>
    .date-input-box {
        border-radius: 10px;
        text-align: left;
        margin: 5px;
        font-size: 1.2em;
        font-weight: bold;
    }
    .date-input-title {
        font-size: 1.2em;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)


# Create 2-column layout for date inputs
col1, col2 = st.columns(2)


# Function to display date input in styled boxes
def display_date_input(col, title, default_date, min_date, max_date):
    col.markdown(f"""
        <div class="date-input-box">
            <div class="date-input-title">{title}</div>
        </div>
        """, unsafe_allow_html=True)
    return col.date_input("", default_date, min_value=min_date, max_value=max_date)

# Display date inputs
with col1:
    date1 = pd.to_datetime(display_date_input(col1, "First Claim Created Date", startDate, startDate, endDate))

with col2:
    date2 = pd.to_datetime(display_date_input(col2, "Last Claim Created Date", endDate, startDate, endDate))


# Handle non-finite values in 'Start Year' column
df['Year'] = df['Year'].fillna(0).astype(int)  # Replace NaN with 0 or any specific value

# Handle non-finite values in 'Start Month' column
df['Month'] = df['Month'].fillna('Unknown')

# Create a 'Month-Year' column
df['Month-Year'] = df['Month'] + ' ' + df['Year'].astype(str)

# Function to sort month-year combinations
def sort_key(month_year):
    month, year = month_year.split()
    return (int(year), month_order.get(month, 0))  # Use .get() to handle 'Unknown' month

# Extract unique month-year combinations and sort them
month_years = sorted(df['Month-Year'].unique(), key=sort_key)

# Select slider for month-year range
selected_month_year_range = st.select_slider(
    "Select Month-Year Range",
    options=month_years,
    value=(month_years[0], month_years[-1])
)

# Filter DataFrame based on selected month-year range
start_month_year, end_month_year = selected_month_year_range
start_month, start_year = start_month_year.split()
end_month, end_year = end_month_year.split()

start_index = (int(start_year), month_order.get(start_month, 0))
end_index = (int(end_year), month_order.get(end_month, 0))

# Filter DataFrame based on month-year order indices
df = df[
    df['Month-Year'].apply(lambda x: (int(x.split()[1]), month_order.get(x.split()[0], 0))).between(start_index, end_index)
]





df_out = df[df['Claim Type'] == 'Outpatient']
df_dental = df[df['Claim Type'] == 'Dental']
df_wellness = df[df['Claim Type'] == 'Wellness']
df_optical = df[df['Claim Type'] == 'Optical']
df_phar = df[df['Claim Type'] == 'Pharmacy']
df_mat = df[df['Claim Type'] == 'Maternity']
df_pro = df[df['Claim Type'] == 'ProActiv']
df_in = df[df['Claim Type'] == 'Inpatient']

df_health = df[df['Product'] == 'Health Insurance']
df_proactiv = df[df['Product'] == 'ProActiv']

df_app = df[df['Claim Status'] == 'Approved']
df_dec = df[df['Claim Status'] == 'Declined']

if not df.empty:

    scale=1_000_000  # For millions

    total_claim_amount = (df["Claim Amount"].sum())/scale
    average_amount =(df["Claim Amount"].mean())/scale
    average_app_amount =(df["Approved Claim Amount"].mean())/scale

    total_out = (df_out['Claim Amount'].sum())/scale
    total_dental = (df_dental['Claim Amount'].sum())/scale
    total_wellness = (df_wellness['Claim Amount'].sum())/scale
    total_optical = (df_optical['Claim Amount'].sum())/scale
    total_in = (df_in['Claim Amount'].sum())/scale
    total_phar = (df_phar['Claim Amount'].sum())/scale
    total_pro = (df_pro['Claim Amount'].sum())/scale
    total_mat = (df_mat['Claim Amount'].sum())/scale

    total_app_claim_amount = (df["Approved Claim Amount"].sum())/scale
    total_dec_claim_amount = (df_dec["Claim Amount"].sum())/scale

    total_app = df_app["Claim ID"].nunique()
    total_dec = df_dec["Claim ID"].nunique()

    total_health_claim_amount = (df_app["Claim Amount"].sum())/scale
    total_pro_claim_amount = (df_dec["Claim Amount"].sum())/scale

    total_health = df_health["Claim ID"].nunique()
    total_proactiv = df_proactiv["Claim ID"].nunique()

    total_clients = df["Employer Name"].nunique()
    total_claims = df["Claim ID"].nunique()


    total_app_per = (total_app/total_claims)*100
    total_dec_per = (total_dec/total_claims)*100


    percent_app = (total_app_claim_amount/total_claim_amount) *100


    # Create 4-column layout for metric cards# Define CSS for the styled boxes and tooltips
    st.markdown("""
        <style>
        .custom-subheader {
            color: #e66c37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            display: inline-block;
        }
        .metric-box {
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin: 10px;
            font-size: 1.2em;
            font-weight: bold;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            border: 1px solid #ddd;
            position: relative;
        }
        .metric-title {
            color: #e66c37; /* Change this color to your preferred title color */
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 1em;
        }

        </style>
        """, unsafe_allow_html=True)



    # Function to display metrics in styled boxes with tooltips
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)


   # Calculate key metrics
    st.markdown(f'<h2 class="custom-subheader">For all Claims in Numbers ({filter_description.strip()})</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Number of Clients", total_clients)
    display_metric(cols2, "Number of Claims", total_claims)
    display_metric(cols3, "Number of Approved Claims", total_app)
    display_metric(cols1, "Number of Declined Claims",total_dec)
    display_metric(cols2, "Percentage Approved", F"{total_app_per: .0F} %")
    display_metric(cols3, "Percentage Declined", F"{total_dec_per: .0F} %")

    # Calculate key metrics
    st.markdown(f'<h2 class="custom-subheader">For all Claim Amounts ({filter_description.strip()})</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Total Claims", total_claims)
    display_metric(cols2, "Total Claim Amount", f"{total_claim_amount:,.0f} M")
    display_metric(cols3, "Total Approved Claim Amount", f"{total_app_claim_amount:,.0f} M")
    display_metric(cols1, "Total Declined Claim Amount", f"{total_dec_claim_amount:,.0f} M")
    display_metric(cols2, "Average Claim Amount Per Client", F"{average_amount:,.0F} M")
    display_metric(cols3, "Average Claim Amount Per Client", F"{average_app_amount: ,.0F} M")

 

    st.markdown(f'<h2 class="custom-subheader">For Claim Amounts by Claim Type ({filter_description.strip()})</h2>', unsafe_allow_html=True)    
  
    cols1,cols2, cols3 = st.columns(3)
    display_metric(cols1, "Total Claim Amount", F"{total_app_claim_amount:,.0F} M")
    display_metric(cols2, "Claim Amount for Outpatient", f"{total_out:,.0f} M")
    display_metric(cols3, "Claim Amount for Dental", f"{total_dental:,.0f} M")
    display_metric(cols1, "Claim Amount for Optical", f"{total_optical:,.0f} M")
    display_metric(cols2, "Claim Amount for Inpatient", f"{total_in:,.0f} M")
    display_metric(cols3, "Claim Amount for Wellness", f"{total_wellness:,.0f} M")
    display_metric(cols1, "Claim Amount for Maternity", f"{total_mat:,.0f} M")
    display_metric(cols2, "Claim Amount for Pharmacy", f"{total_phar:,.0f} M")
    display_metric(cols3, "Claim Amount for ProActiv", f"{total_pro:,.0f} M")
