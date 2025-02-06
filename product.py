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

st.markdown('<h1 class="main-title">ClAIMS ANALYSIS - PRODUCT VIEW</h1>', unsafe_allow_html=True)



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

df.rename(columns={'Employer Name': 'Client Name'}, inplace=True)

# Filter data by product
df_health = df[df['Product'] == 'Health Insurance']
df_proactiv = df[df['Product'] == 'ProActiv']

# Filter data by claim status
df_app = df[df['Claim Status'] == 'Approved']
df_dec = df[df['Claim Status'] == 'Declined']

# Scale factor for millions
scale = 1_000_000

# Calculate overall metrics
if not df.empty:
    total_claim_amount = (df["Claim Amount"].sum()) / scale
    average_claim_amount = (df["Claim Amount"].mean()) / scale
    average_approved_claim_amount = (df["Approved Claim Amount"].mean()) / scale

    total_clients = df["Client Name"].nunique()
    total_claims = df["Claim ID"].nunique()
    total_approved_claims = df_app["Claim ID"].nunique()
    total_declined_claims = df_dec["Claim ID"].nunique()

    total_approved_claim_amount = (df_app["Claim Amount"].sum()) / scale
    total_declined_claim_amount = (df_dec["Claim Amount"].sum()) / scale

    percent_approved = (total_approved_claims / total_claims) * 100 if total_claims != 0 else 0
    percent_declined = (total_declined_claims / total_claims) * 100 if total_claims != 0 else 0

# Calculate Health Insurance metrics
    total_health_claims = df_health["Claim ID"].nunique()
    total_health_approved_claims = df_health[df_health['Claim Status'] == 'Approved']["Claim ID"].nunique()
    total_health_declined_claims = df_health[df_health['Claim Status'] == 'Declined']["Claim ID"].nunique()

    total_health_claim_amount = (df_health["Claim Amount"].sum()) / scale
    total_health_approved_amount = (df_health[df_health['Claim Status'] == 'Approved']["Claim Amount"].sum()) / scale
    total_health_declined_amount = (df_health[df_health['Claim Status'] == 'Declined']["Claim Amount"].sum()) / scale

    health_approval_rate = (total_health_approved_claims / total_health_claims) * 100 if total_health_claims != 0 else 0
    health_decline_rate = (total_health_declined_claims / total_health_claims) * 100 if total_health_claims != 0 else 0

# Calculate ProActiv metrics
    total_proactiv_claims = df_proactiv["Claim ID"].nunique()
    total_proactiv_approved_claims = df_proactiv[df_proactiv['Claim Status'] == 'Approved']["Claim ID"].nunique()
    total_proactiv_declined_claims = df_proactiv[df_proactiv['Claim Status'] == 'Declined']["Claim ID"].nunique()

    total_proactiv_claim_amount = (df_proactiv["Claim Amount"].sum()) / scale
    total_proactiv_approved_amount = (df_proactiv[df_proactiv['Claim Status'] == 'Approved']["Claim Amount"].sum()) / scale
    total_proactiv_declined_amount = (df_proactiv[df_proactiv['Claim Status'] == 'Declined']["Claim Amount"].sum()) / scale

    proactiv_approval_rate = (total_proactiv_approved_claims / total_proactiv_claims) * 100 if total_proactiv_claims != 0 else 0
    proactiv_decline_rate = (total_proactiv_declined_claims / total_proactiv_claims) * 100 if total_proactiv_claims != 0 else 0

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


  
    # Display overall metrics
    st.markdown(f'<h2 class="custom-subheader">For all Claims in Numbers</h2>', unsafe_allow_html=True)
    cols1, cols2, cols3 = st.columns(3)
    display_metric(cols1, "Number of Clients", f"{total_clients:,.0f}")
    display_metric(cols2, "Number of Claims", f"{total_claims:,.0f}")
    display_metric(cols3, "Number of Approved Claims", f"{total_approved_claims:,.0f}")
    display_metric(cols1, "Number of Declined Claims", f"{total_declined_claims:,.0f}")
    display_metric(cols2, "Percentage Approved", f"{percent_approved:.0f} %")
    display_metric(cols3, "Percentage Declined", f"{percent_declined:.0f} %")

    # Display overall claim amounts
    st.markdown(f'<h2 class="custom-subheader">For all Claim Amounts</h2>', unsafe_allow_html=True)
    cols1, cols2, cols3 = st.columns(3)
    display_metric(cols1, "Total Claim Amount", f"{total_claim_amount:,.0f} M")
    display_metric(cols2, "Total Approved Claim Amount", f"{total_approved_claim_amount:,.0f} M")
    display_metric(cols3, "Total Declined Claim Amount", f"{total_declined_claim_amount:,.0f} M")
    display_metric(cols1, "Average Claim Amount Per Client", f"{average_claim_amount:,.0f} M")
    display_metric(cols2, "Average Approved Claim Amount Per Client", f"{average_approved_claim_amount:,.0f} M")

    # Display Health Insurance metrics
    st.markdown('<h3 class="custom-subheader">For Health Insurance</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    display_metric(col1, "Number of Claims", f"{total_health_claims:,.0f}")
    display_metric(col2, "Number of Approved Claims", f"{total_health_approved_claims:,.0f}")
    display_metric(col3, "Number of Declined Claims", f"{total_health_declined_claims:,.0f}")
    display_metric(col1, "Total Claim Amount", f"RWF {total_health_claim_amount:,.0f} M")
    display_metric(col2, "Approved Claim Amount", f"RWF {total_health_approved_amount:,.0f} M")
    display_metric(col3, "Declined Claim Amount", f"RWF {total_health_declined_amount:,.0f} M")
    display_metric(col1, "Percentage Approved", f"{health_approval_rate:.0f} %")
    display_metric(col2, "Percentage Declined", f"{health_decline_rate:.0f} %")

    # Display ProActiv metrics
    st.markdown('<h3 class="custom-subheader">For ProActiv</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    display_metric(col1, "Number of Claims", f"{total_proactiv_claims:,.0f}")
    display_metric(col2, "Number of Approved Claims", f"{total_proactiv_approved_claims:,.0f}")
    display_metric(col3, "Number of Declined Claims", f"{total_proactiv_declined_claims:,.0f}")
    display_metric(col1, "Total Claim Amount", f"RWF {total_proactiv_claim_amount:,.0f} M")
    display_metric(col2, "Approved Claim Amount", f"RWF {total_proactiv_approved_amount:,.0f} M")
    display_metric(col3, "Declined Claim Amount", f"RWF {total_proactiv_declined_amount:,.0f} M")
    display_metric(col1, "Percentage Approved", f"{proactiv_approval_rate:.0f} %")
    display_metric(col2, "Percentage Declined", f"{proactiv_decline_rate:.0f} %")

    st.dataframe(df)



    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

    col1, col2 = st.columns(2)

    with col1:
        # Total Claims and Approved Claim Amount Over Time
        area_chart_count = df.groupby(df["Claim Created Date"].dt.strftime("%Y-%m-%d")).size().reset_index(name='Count')

        area_chart_amount = df.groupby(df["Claim Created Date"].dt.strftime("%Y-%m-%d"))['Claim Amount'].sum().reset_index(name='Claim Amount')

        area_chart = pd.merge(area_chart_count, area_chart_amount, on='Claim Created Date').sort_values("Claim Created Date")

        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig1.add_trace(
            go.Scatter(
                x=area_chart['Claim Created Date'], 
                y=area_chart['Count'], 
                name="Number of Claims", 
                fill='tozeroy', 
                line=dict(color=custom_colors[1])), 
                secondary_y=False)
        
        fig1.add_trace(
            go.Scatter(
                x=area_chart['Claim Created Date'], 
                y=area_chart['Claim Amount'], 
                name="Claim Amount", fill='tozeroy', 
                line=dict(color=custom_colors[0])), 
                secondary_y=True)
        
        fig1.update_xaxes(
            title_text="Claim Created Date", 
            tickangle=45)
        
        fig1.update_yaxes(
            title_text="<b>Number of Claims</b>", 
            secondary_y=False)
        
        fig1.update_yaxes(
            title_text="<b>Approved Claim Amount</b>", 
            secondary_y=True)
        
        st.markdown('<h3 class="custom-subheader">Total Claims and Approved Claim Amount Over Time</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True)

    # Group data by "Year" and "Product" and calculate the average Claim Amount
    yearly_avg_claim = df.groupby(['Year', 'Product'])['Claim Amount'].sum().unstack().fillna(0)

    # Define custom colors
    with col2:
        # Create the grouped bar chart
        fig_yearly_avg_claim = go.Figure()

        # Add traces for each product
        for idx, product in enumerate(yearly_avg_claim.columns):
            fig_yearly_avg_claim.add_trace(go.Bar(
                x=yearly_avg_claim.index,  # Years on the x-axis
                y=yearly_avg_claim[product],  # Average claim amount for each product
                name=product,  # Product name as legend
                text=yearly_avg_claim[product].apply(lambda x: f"{x / 1_000_000:.1f}M"),  # Format values in millions
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        # Update layout
        fig_yearly_avg_claim.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Total Claim Amount (M)",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Yearly Claims by Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_claim, use_container_width=True)

    col1, col2 = st.columns(2)

    # Group data by "Month" and "Product" and calculate the average Claim Amount
    monthly_avg_claim = df.groupby(['Month', 'Product'])['Claim Amount'].mean().unstack().fillna(0)

    # Define custom colors
    with col1:
        # Create the grouped bar chart
        fig_monthly_avg_claim = go.Figure()

        # Add traces for each product
        for idx, product in enumerate(monthly_avg_claim.columns):
            fig_monthly_avg_claim.add_trace(go.Bar(
                x=monthly_avg_claim.index,  # Months on the x-axis
                y=monthly_avg_claim[product],  # Average claim amount for each product
                name=product,  # Product name as legend
                text=monthly_avg_claim[product].apply(lambda x: f"${x / 1_000_000:.1f}M"),  # Format values in millions
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        # Update layout
        fig_monthly_avg_claim.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Month",
            yaxis_title="Average Claim Amount (M)",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), tickangle=45),  # Rotate month labels for readability
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Monthly Claims by Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_avg_claim, use_container_width=True)

    # Group data by Product to calculate the number of claims and total claim amount
    claims_by_product = df.groupby("Product").agg(
        Number_of_Claims=("Claim ID", "nunique"),
        Total_Claim_Amount=("Claim Amount", "sum")
    ).reset_index()

    # Scale Total Claim Amount to millions for better readability
    claims_by_product["Total_Claim_Amount"] = claims_by_product["Total_Claim_Amount"] / 1_000_000

    with col2:

        # Create a grouped bar chart
        fig_grouped_bar = go.Figure()

        # Add trace for Number of Claims
        fig_grouped_bar.add_trace(go.Bar(
            x=claims_by_product['Product'], 
            y=claims_by_product['Number_of_Claims'], 
            name="Number of Claims", 
            text=claims_by_product['Number_of_Claims'], 
            textposition='outside', 
            marker_color=custom_colors[1]  # Use second color for number of claims
        ))

        # Add trace for Total Claim Amount
        fig_grouped_bar.add_trace(go.Bar(
            x=claims_by_product['Product'], 
            y=claims_by_product['Total_Claim_Amount'], 
            name="Total Claim Amount (M)", 
            text=claims_by_product['Total_Claim_Amount'].apply(lambda x: f"{x:.1f}M"), 
            textposition='outside', 
            marker_color=custom_colors[0]  # Use first color for total claim amount
        ))

        # Update layout for grouped bars
        fig_grouped_bar.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Product",
            yaxis_title="Count / Amount (M)",
            font=dict(color='Black', size=12),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), tickangle=45),  # Rotate product names for readability
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450,
            legend=dict(x=0.01, y=1.1, orientation="h")  # Place legend above the chart
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Number of Claims and Total Claim Amount by Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_grouped_bar, use_container_width=True)
        
    col1, col2 = st.columns(2)



    # Group by product and claim status
    product_claim_status = df.groupby(['Product', 'Claim Status'])['Claim ID'].nunique().unstack(fill_value=0).reset_index()

    with col1:

        # Create a stacked bar chart
        fig_claim_status_by_product = go.Figure()

        fig_claim_status_by_product.add_trace(go.Bar(
            x=product_claim_status['Product'],
            y=product_claim_status['Approved'],
            name='Approved Claims',
            marker_color=custom_colors[0]  # Use second color for approved claims
        ))

        fig_claim_status_by_product.add_trace(go.Bar(
            x=product_claim_status['Product'],
            y=product_claim_status['Declined'],
            name='Declined Claims',
            marker_color=custom_colors[1]  # Use fifth color for declined claims
        ))

        # Update layout
        fig_claim_status_by_product.update_layout(
            barmode='group',
            xaxis_title="Product",
            yaxis_title="Number of Claims",
            font=dict(color='Black'),
            margin=dict(l=0, r=0, t=50, b=50),
            height=500
        )
        st.markdown('<h3 class="custom-subheader">Approved vs Declined Claims by Product</h3>', unsafe_allow_html=True)

        st.plotly_chart(fig_claim_status_by_product, use_container_width=True)



    with col2:

        # Filter top providers by claim volume
        top_providers = df.groupby(['Product', 'Source'])['Claim Amount'].sum().reset_index(name='Claim Amount')


        # Create a grouped bar chart
        fig_top_providers = go.Figure()

        for product in top_providers['Product'].unique():
            product_data = top_providers[top_providers['Product'] == product]
            fig_top_providers.add_trace(go.Bar(
                x=product_data['Source'],
                y=product_data['Claim Amount'],
                name=product,
                marker_color=custom_colors[list(top_providers['Product'].unique()).index(product) % len(custom_colors)]  # Assign unique color per product
            ))

        # Update layout
        fig_top_providers.update_layout(
            barmode='group',
            xaxis_title="Provider Type",
            yaxis_title="Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(tickangle=45),
            margin=dict(l=0, r=0, t=50, b=50),
            height=500
        )
        st.markdown('<h3 class="custom-subheader">Provider Type Trend by Product</h3>', unsafe_allow_html=True)

        st.plotly_chart(fig_top_providers, use_container_width=True)


    with col1:

        # Filter top providers by claim volume
        top_providers = df.groupby(['Product', 'Claim Type'])['Claim Amount'].sum().reset_index(name='Claim Amount')


        # Create a grouped bar chart
        fig_top_providers = go.Figure()

        for product in top_providers['Product'].unique():
            product_data = top_providers[top_providers['Product'] == product]
            fig_top_providers.add_trace(go.Bar(
                x=product_data['Claim Type'],
                y=product_data['Claim Amount'],
                name=product,
                marker_color=custom_colors[list(top_providers['Product'].unique()).index(product) % len(custom_colors)]  # Assign unique color per product
            ))

        # Update layout
        fig_top_providers.update_layout(
            barmode='group',
            xaxis_title="Claim Type",
            yaxis_title="Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(tickangle=45),
            margin=dict(l=0, r=0, t=50, b=50),
            height=500
        )
        st.markdown('<h3 class="custom-subheader">Total Claim Amount and Claim Type Trend by Product</h3>', unsafe_allow_html=True)

        st.plotly_chart(fig_top_providers, use_container_width=True)

    with col2:

        # Filter top providers by claim volume
        top_providers = df.groupby(['Product', 'Diagnosis'])['Claim Amount'].sum().reset_index(name='Claim Amount')

        top_providers = top_providers.sort_values(by=['Product', 'Claim Amount'], ascending=[True, False]).groupby('Product').head(10)

        # Create a grouped bar chart
        fig_top_providers = go.Figure()

        for product in top_providers['Product'].unique():
            product_data = top_providers[top_providers['Product'] == product]
            fig_top_providers.add_trace(go.Bar(
                x=product_data['Diagnosis'],
                y=product_data['Claim Amount'],
                name=product,
                marker_color=custom_colors[list(top_providers['Product'].unique()).index(product) % len(custom_colors)]  # Assign unique color per product
            ))

        # Update layout
        fig_top_providers.update_layout(
            barmode='group',
            xaxis_title="Diagnosis",
            yaxis_title="Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(tickangle=45),
            margin=dict(l=0, r=0, t=50, b=50),
            height=500,
        )
        st.markdown('<h3 class="custom-subheader">Top 10 Diagnosis by Product</h3>', unsafe_allow_html=True)

        st.plotly_chart(fig_top_providers, use_container_width=True)

    with col1:

        # Filter top providers by claim volume
        top_providers = df.groupby(['Product', 'Provider Name'])['Claim Amount'].sum().reset_index(name='Total Claim Amount')

        # Sort by claim amount and limit to top 5 providers per product
        top_providers = top_providers.sort_values(by=['Product', 'Total Claim Amount'], ascending=[True, False]).groupby('Product').head(10)

        # Create a grouped bar chart for top providers
        fig_top_providers = go.Figure()

        for idx, product in enumerate(top_providers['Product'].unique()):
            product_data = top_providers[top_providers['Product'] == product]
            fig_top_providers.add_trace(go.Bar(
                x=product_data['Provider Name'],
                y=product_data['Total Claim Amount'],
                name=product,
                text=product_data['Total Claim Amount'].apply(lambda x: f"${x / 1_000_000:.1f}M"),  # Format as millions
                textposition='outside',
                marker_color=custom_colors[idx % len(custom_colors)]  # Assign unique color per product
            ))

        # Update layout
        fig_top_providers.update_layout(
            barmode='group',
            xaxis_title="Provider Name",
            yaxis_title="Total Claim Amount (M)",
            font=dict(color='Black', size=12),
            xaxis=dict(tickangle=45, title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), ticksuffix="M"),
            margin=dict(l=0, r=0, t=50, b=50),
            height=500
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Service Providers by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_top_providers, use_container_width=True)

    with col2:

        # Filter top clients by claim volume
        top_clients = df.groupby(['Product', 'Client Name'])['Claim Amount'].sum().reset_index(name='Total Claim Amount')

        # Sort by claim amount and limit to top 5 clients per product
        top_clients = top_clients.sort_values(by=['Product', 'Total Claim Amount'], ascending=[True, False]).groupby('Product').head(10)

        # Create a grouped bar chart for top clients
        fig_top_clients = go.Figure()

        for idx, product in enumerate(top_clients['Product'].unique()):
            product_data = top_clients[top_clients['Product'] == product]
            fig_top_clients.add_trace(go.Bar(
                x=product_data['Client Name'],
                y=product_data['Total Claim Amount'],
                name=product,
                text=product_data['Total Claim Amount'].apply(lambda x: f"${x / 1_000_000:.1f}M"),  # Format as millions
                textposition='outside',
                marker_color=custom_colors[idx % len(custom_colors)]  # Assign unique color per product
            ))

        # Update layout
        fig_top_clients.update_layout(
            barmode='group',
            xaxis_title="Client Name",
            yaxis_title="Total Claim Amount (M)",
            font=dict(color='Black', size=12),
            xaxis=dict(tickangle=45, title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), ticksuffix="M"),
            margin=dict(l=0, r=0, t=50, b=50),
            height=500
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Employer Group by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_top_clients, use_container_width=True)