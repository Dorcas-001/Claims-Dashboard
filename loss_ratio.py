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

st.markdown('<h1 class="main-title">CLAIMS ANAYSIS - LOSS RATIO VIEW</h1>', unsafe_allow_html=True)

# Filepaths and sheet names
filepath_premiums = "JAN-NOV 2024 GWP.xlsx"
sheet_name_new_business = "2023"
sheet_name_endorsements = "2024"

filepath_claims = "Claims.xlsx"
sheet_name1 = "2023 claims"
sheet_name2 = "2024 claims"

# Read premium data
df_2023 = pd.read_excel(filepath_premiums, sheet_name=sheet_name_new_business)
df_2024 = pd.read_excel(filepath_premiums, sheet_name=sheet_name_endorsements)

# Read claims data
dfc_2023 = pd.read_excel(filepath_claims, sheet_name=sheet_name1)
dfc_2024 = pd.read_excel(filepath_claims, sheet_name=sheet_name2)

# Premiums
df_2023['Start Date'] = pd.to_datetime(df_2023['Start Date'])
df_2023['End Date'] = pd.to_datetime(df_2023['End Date'])
df_2024['Start Date'] = pd.to_datetime(df_2024['Start Date'])
df_2024['End Date'] = pd.to_datetime(df_2024['End Date'])

filepath_visits = "Claims.xlsx"
sheet_name1 = "2023 claims"
sheet_name2 = "2024 claims"

# Read the Claims data
dfc_2023 = pd.read_excel(filepath_visits, sheet_name=sheet_name1)
dfc_2024 = pd.read_excel(filepath_visits, sheet_name=sheet_name2)


df_2023['Year'] = 2023
df_2024['Year'] = 2024
dfc_2023['Year'] = 2023
dfc_2024['Year'] = 2024

dfc_2023.rename(columns={'Employer Name': 'Client Name'}, inplace=True)
dfc_2024.rename(columns={'Employer Name': 'Client Name'}, inplace=True)

df_premiums = pd.concat([df_2023, df_2024])

def prioritize_cover_types(group):
    if 'Renewal' in group['Cover Type'].values:
        return group[group['Cover Type'] == 'Renewal']
    elif 'New' in group['Cover Type'].values:
        return group[group['Cover Type'] == 'New']
    else:
        return group

# Apply prioritization
premiums_grouped = df_premiums.groupby(['Client Name', 'Product', 'Year']).apply(prioritize_cover_types).reset_index(drop=True)

endorsements = premiums_grouped[premiums_grouped['Cover Type'] == 'Endorsement']

# Merge endorsements with prioritized premiums
merged_endorsements = pd.merge(
    endorsements,
    premiums_grouped[premiums_grouped['Cover Type'].isin(['New', 'Renewal'])],
    on=['Client Name', 'Product', 'Year'],
    suffixes=('_endorsement', '_prioritized')
)

# Filter valid endorsements
valid_endorsements = merged_endorsements[
    (merged_endorsements['Start Date_endorsement'] >= merged_endorsements['Start Date_prioritized']) &
    (merged_endorsements['End Date_endorsement'] <= merged_endorsements['End Date_prioritized'])
]

# Aggregate endorsement premiums
endorsement_grouped = valid_endorsements.groupby(['Client Name', 'Product', 'Year']).agg({
    'Total_endorsement': 'sum'
}).reset_index().rename(columns={'Total_endorsement': 'Endorsement Premium'})

# Merge endorsement premiums back into prioritized premiums
final_premiums = pd.merge(
    premiums_grouped,
    endorsement_grouped,
    on=['Client Name', 'Product', 'Year'],
    how='left'
)

# Calculate total premium
final_premiums['Total Premium'] = (
    final_premiums['Total'] + 
    final_premiums['Endorsement Premium'].fillna(0)
)

current_date = pd.Timestamp.now()

# Group by client-product-year
client_product_data = final_premiums.groupby(['Client Name', 'Product', 'Year']).agg({
    'Start Date': 'min',
    'End Date': 'max',
    'Total Premium': 'sum'
}).reset_index()

# Compute days since start and days on cover
client_product_data['Days Since Start'] = (current_date - client_product_data['Start Date']).dt.days
client_product_data['days_on_cover'] = (client_product_data['End Date'] - client_product_data['Start Date']).dt.days

# Calculate earned premium
client_product_data['Earned Premium'] = (
    client_product_data['Total Premium'] * 
    client_product_data['Days Since Start'] / 
    client_product_data['days_on_cover']
)

# Read the visit logs
df_claims = pd.concat([dfc_2023, dfc_2024])


df_claims['Claim Created Date'] = pd.to_datetime(df_claims['Claim Created Date'], errors='coerce')

claims_aggregated = df_claims.groupby(['Client Name', 'Product', 'Year']).agg({
    'Claim Amount': 'sum'
}).reset_index().rename(columns={'Claim Amount': 'Total Claims'})

matched_data = pd.merge(
    claims_aggregated,
    client_product_data[['Client Name', 'Product', 'Year', 'Earned Premium']],
    on=['Client Name', 'Product', 'Year'],
    how='outer'
)

# Fill missing values
matched_data['Total Claims'] = matched_data['Total Claims'].fillna(0)
matched_data['Earned Premium'] = matched_data['Earned Premium'].fillna(0)

matched_data


df['Client Name'] = df['Client Name'].astype(str)
df["Client Name"] = df["Client Name"].str.upper()


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

# Sort months based on their order
sorted_months = sorted(df['month'].dropna().unique(), key=lambda x: month_order[x])

df['Quarter'] = "Q" + df['Start Date'].dt.quarter.astype(str)


# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
quarter = st.sidebar.multiselect("Select Quarter", options=sorted(df['Quarter'].dropna().unique()))
product = st.sidebar.multiselect("Select Product", options=df['Product'].unique())
cover = st.sidebar.multiselect("Select Cover Type", options=df['Cover Type'].unique())
# segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
client_names = sorted(df['Client Name'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=client_names)

# Apply filters to the DataFrame
if 'Year' in df.columns and year:
    df = df[df['Year'].isin(year)]
if 'Product' in df.columns and product:
    df = df[df['Product'].isin(product)]
if 'Month' in df.columns and month:
    df = df[df['Month'].isin(month)]
if 'Cover Type' in df.columns and cover:
    df = df[df['Cover Type'].isin(cover)]
# if 'Client Segment' in df.columns and segment:
#     df = df[df['Client Segment'].isin(segment)]
if 'Client Name' in df.columns and client_name:
    df = df[df['Client Name'].isin(client_name)]

# Determine the filter description
filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if cover:
    filter_description += f"{', '.join(map(str, cover))} "
if product:
     filter_description += f"{', '.join(map(str, product))} "
if month:
    filter_description += f"{', '.join(month)} "
if not filter_description:
    filter_description = "All data"


# Get minimum and maximum dates for the date input
startDate = df["Start Date"].min()
endDate = df["End Date"].max()

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
    date1 = pd.to_datetime(display_date_input(col1, "Start Date", startDate, startDate, endDate))

with col2:
    date2 = pd.to_datetime(display_date_input(col2, "End Date", endDate, startDate, endDate))




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


df_new = df[df['Cover Type'] == 'New']
df_renew = df[df['Cover Type'] == 'Renewal']
df_combined = df[df['Cover Type'].isin(['New', 'Renewal'])]

df_endorsements = df[df['Cover Type']=='Endorsement']

if not df.empty:

    scale=1_000_000  # For millions



    total_claim_amount = (df["Claim Amount"].sum())/scale
    average_amount =(df["Claim Amount"].mean())/scale
    average_app_amount =(df["Approved Claim Amount"].mean())/scale

    total_clients = df["Client Name"].nunique()
    total_claims = df["Claim ID"].nunique()

    total_new = (df_new["Total"].sum())/scale
    total_renew = (df_renew["Total"].sum())/scale
    total_pre = total_new +total_renew
    total_endorsements_amount = df_endorsements["Total"].sum()/scale
    total_app_claim_amount= df["Approved Claim Amount"].sum()/scale

    total_clients = df["Client Name"].nunique()
    total_endorsements = df_endorsements["Client Name"].count()
    num_new = df_new["Client Name"].nunique()
    num_renew = df_renew["Client Name"].nunique()
    num_visits = df["Claim ID"].nunique()


    # total_new_premium = (df["Total Premium_new"].sum())/scale
    # total_endorsement = (df["Total Premium_endorsements"].sum())/scale
    total_premium = (df["Total"].sum())/scale
    total_days = df["Days Since Start"].sum()
    total_days_on_cover = df['days_on_cover'].sum()
    total_claim_amount = (df["Claim Amount"].sum())/scale
    average_pre = (df["Total"].mean())/scale
    average_days = df["Days Since Start"].mean()

    percent_app = (total_app_claim_amount/total_claim_amount) *100
    percent_app
    earned_premium = (total_premium * total_days)/total_days_on_cover
    loss_ratio_amount = total_app_claim_amount / earned_premium
    loss_ratio= (total_app_claim_amount / earned_premium) *100

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

    st.dataframe(df)

    # Function to display metrics in styled boxes with tooltips
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)


    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">For all Sales in Numbers</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Number of Clients", total_clients)
    display_metric(cols2, "Number of New Business", num_new)
    display_metric(cols3, "Number of Renewals", num_renew)
    display_metric(cols1, "Number of Endorsements",total_endorsements)
    display_metric(cols2, "Number of Claims", f"{num_visits:,.0f}")

    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">For all Sales Amount</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Total Premium", f"{total_premium:,.0f} M")
    display_metric(cols2, "Total New Business Premium", f"{total_new:,.0f} M")
    display_metric(cols3, "Total Renewal Premium", f"{total_renew:,.0f} M")
    display_metric(cols1, "Total Endorsement Premium", f"{total_endorsements_amount:,.0f} M")
    display_metric(cols2, "Total Claim Amount", f"{total_claim_amount:,.0f} M")
    display_metric(cols3, "Total Approved Claim Amount", f"{total_app_claim_amount:,.0f} M")
    display_metric(cols1, "Average Premium per Client", f"{average_pre:,.0f} M")
    display_metric(cols2, "Percentage Approved", f"{percent_app:,.0f} %")
    
    # Calculate key metrics
    st.markdown(f'<h2 class="custom-subheader">For all Claim Amounts ({filter_description.strip()})</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Total Claims", total_claims)
    display_metric(cols2, "Total Claim Amount", f"{total_claim_amount:,.0f} M")
    display_metric(cols3, "Total Approved Claim Amount", f"{total_app_claim_amount:,.0f} M")
    display_metric(cols1, "Average Claim Amount Per Client", F"{average_amount:,.0F} M")
    display_metric(cols2, "Average Claim Amount Per Client", F"{average_app_amount: ,.0F} M")

    st.markdown('<h2 class="custom-subheader">For Loss Ratio</h2>', unsafe_allow_html=True)    
  
    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Days Since  Premium Start", f"{total_days:,.0f} days")
    display_metric(cols2, "Premium Duration (Days)", f"{total_days_on_cover:,.0f} days")
    display_metric(cols3, "Average Days Since  Premium Start per Client", f"{average_days:,.0f} days")
    display_metric(cols1, "Earned Premium", f"{earned_premium:,.0f} M")
    display_metric(cols2, "Loss Ratio", f"{loss_ratio_amount:,.0f} M")
    display_metric(cols3, "Percentage Loss Ratio", f"{loss_ratio: .0f} %")



    # Ensure 'Start Date' is in datetime format
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')


    df['earned_premium'] = (total_premium * df["Days Since Start"].sum()) / total_days_on_cover

    df['Loss Ratio'] = (total_app_claim_amount / earned_premium)

 
    # Sidebar styling and logo
    st.markdown("""
        <style>
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .sidebar .sidebar-content h3 {
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

    cols1, cols2 = st.columns(2)

    custom_colors = ["#009DAE", "#e66c37", "#461b09", "#f8a785", "#CC3636"]



    # Group by day and sum the totals for combined new and renewals, and endorsements
    area_chart_combined = df_combined.groupby(df_combined["Start Date"].dt.strftime("%Y-%m-%d"))['Total'].sum().reset_index(name='Total Combined')
    area_chart_endorsement = df_endorsements.groupby(df_endorsements["Start Date"].dt.strftime("%Y-%m-%d"))['Total'].sum().reset_index(name='Total Endorsements')

    with cols1:
        # Merge the data frames on the 'Start Date'
        area_chart = pd.merge(area_chart_combined, area_chart_endorsement, on='Start Date', how='outer')

        # Fill NaN values with 0
        area_chart = area_chart.fillna(0)

        # Create the time series chart using Plotly
        fig = go.Figure()

        # Add Total Combined trace
        fig.add_trace(go.Scatter(
            x=area_chart['Start Date'],
            y=area_chart['Total Combined'],
            mode='lines',
            name='Total Premium (New & Renewals)',
            line=dict(color='#009DAE', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 157, 174, 0.5)'
        ))

        # Add Total Endorsements trace
        fig.add_trace(go.Scatter(
            x=area_chart['Start Date'],
            y=area_chart['Total Endorsements'],
            mode='lines',
            name='Total Endorsements',
            line=dict(color='#e66c37', width=2),
            fill='tozeroy',
            fillcolor='rgba(230, 108, 55, 0.5)'
        ))

        # Update layout
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Amount',
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), type='category'),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Rotate x-axis labels for better readability
        fig.update_xaxes(tickangle=45)

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Combined Premium and Total Endorsements Over Time</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)



    # Group data by 'Year' and calculate the sum of Total Premium and Total Endorsements
    yearly_data_combined = df_combined.groupby('Year')['Total'].sum().reset_index(name='Total Premium')
    yearly_data_endorsements = df_endorsements.groupby('Year')['Total'].sum().reset_index(name='Total Endorsements')

    # Merge the data frames on the 'Year'
    yearly_data = pd.merge(yearly_data_combined, yearly_data_endorsements, on='Year', how='outer')

    with cols2:
        # Fill NaN values with 0
        yearly_data = yearly_data.fillna(0)

        # Define custom colors
        custom_colors = ['#009DAE', '#e66c37']

        # Create the grouped bar chart for Total Premium and Endorsements
        fig_yearly_avg_premium = go.Figure()

        # Add Total Premium bar trace
        fig_yearly_avg_premium.add_trace(go.Bar(
            x=yearly_data['Year'],
            y=yearly_data['Total Premium'],
            name='Total Premium',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0]
        ))

        # Add Total Endorsements bar trace
        fig_yearly_avg_premium.add_trace(go.Bar(
            x=yearly_data['Year'],
            y=yearly_data['Total Endorsements'],
            name='Total Endorsements',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1]
        ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Total Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), type='category'),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Yearly Distribution of Total Premium and Endorsements</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)


    cols1, cols2 = st.columns(2)

    # Group data by 'Year' and calculate the sum of Total Premium and Loss Ratio
    yearly_data = df.groupby('Year')[['Total', 'Approved Claim Amount sum']].sum().reset_index()

    with cols1:
        # Create the grouped bar chart for Total Premium and Loss Ratio
        fig_yearly_avg_premium = go.Figure()

        # Add Total Premium bar trace
        fig_yearly_avg_premium.add_trace(go.Bar(
            x=yearly_data['Year'],
            y=yearly_data['Total'],
            name='Total Premium',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0]
        ))

        # Add Loss Ratio bar trace
        fig_yearly_avg_premium.add_trace(go.Bar(
            x=yearly_data['Year'],
            y=yearly_data['Approved Claim Amount sum'],
            name='Approved Claim Amount',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1]
        ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Approved Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), type='category'),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Yearly Distribution of Total Premium and Approved Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)



    # Group data by 'Year' and calculate the sum of Total Premium and Loss Ratio
    yearly_data = df.groupby('Month')[['Total', 'Approved Claim Amount sum']].sum().reset_index()



    with cols2:
        # Create the grouped bar chart for Total Premium and Loss Ratio
        fig_yearly_avg_premium = go.Figure()

        # Add Total Premium bar trace
        fig_yearly_avg_premium.add_trace(go.Bar(
            x=yearly_data['Month'],
            y=yearly_data['Total'],
            name='Total Premium',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0]
        ))

        # Add Loss Ratio bar trace
        fig_yearly_avg_premium.add_trace(go.Bar(
            x=yearly_data['Month'],
            y=yearly_data['Approved Claim Amount sum'],
            name='Approved Claim Amount',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1]
        ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Month",
            yaxis_title="Approved Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), type='category'),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Monthly Distribution of Total Premium and Approved Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)


    cols1, cols2 = st.columns(2)

    # Sort the DataFrame by Loss Ratio in descending order and select the top 10 clients
    top_10_clients = df.sort_values(by='Loss Ratio', ascending=False).head(10)

    # Convert Loss Ratio to percentage
    top_10_clients['Loss Ratio (%)'] = top_10_clients['Loss Ratio'] * 100

    # Define a single color for all bars
    single_color = '#009DAE'

    with cols1:
        # Create the bar chart for Loss Ratio by Client Name
        fig = go.Figure()

        # Add bars for each Client Name
        fig.add_trace(go.Bar(
            x=top_10_clients['Client Name'],
            y=top_10_clients['Loss Ratio (%)'],
            name='Loss Ratio (%)',
            text=[f'{value:.1f}%' for value in top_10_clients['Loss Ratio (%)']],
            textposition='auto',
            marker_color=single_color  # Use a single color for all bars
        ))

        fig.update_layout(
            barmode='group',
            yaxis_title="Loss Ratio (%)",
            xaxis_title="Client Name",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Clients by Loss Ratio (%)</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)




    # Sort the DataFrame by Loss Ratio in descending order and select the top 10 clients
    top_10_clients = df.sort_values(by='Approved Claim Amount sum', ascending=False).head(10)

    # Define a single color for all bars
    single_color = '#009DAE'

    with cols2:
        # Create the bar chart for Loss Ratio by Client Name
        fig = go.Figure()

        # Add bars for each Client Name
        fig.add_trace(go.Bar(
            x=top_10_clients['Client Name'],
            y=top_10_clients['Approved Claim Amount sum'],
            name='Approved Claim Amount',
            text=[f'{value:.2f}' for value in top_10_clients['Approved Claim Amount sum']],
            textposition='auto',
            marker_color=single_color 
        ))

        fig.update_layout(
            barmode='group',
            yaxis_title="Approved Claim Amount",
            xaxis_title="Client Name",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Clients by Approved Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 =st.columns(2)


    # Sort the DataFrame by Loss Ratio in descending order and select the top 10 clients
    top_10_clients = df.sort_values(by='Total', ascending=False).head(10)

    # Define a single color for all bars
    single_color = '#009DAE'

    with cl1:
        # Create the bar chart for Loss Ratio by Client Name
        fig = go.Figure()

        # Add bars for each Client Name
        fig.add_trace(go.Bar(
            x=top_10_clients['Client Name'],
            y=top_10_clients['Total'],
            name='Premium amount',
            text=[f'{value:.2f}' for value in top_10_clients['Total']],
            textposition='auto',
            marker_color=single_color 
        ))

        fig.update_layout(
            barmode='group',
            yaxis_title="Total Premium",
            xaxis_title="Client Name",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Clients by Premium</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)




 # Calculate the Total Premium by Client Segment
    int_owner = df.groupby("Cover Type")["Total"].sum().reset_index()
    int_owner.columns = ["Cover Type", "Total Premium"]    

    with cl2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Sales by Cover Type</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Cover Type", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)





