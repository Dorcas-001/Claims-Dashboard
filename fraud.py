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

st.markdown('<h2 class="main-title">CLAIMS ANALYSIS - ABNORMALITIES</h2>', unsafe_allow_html=True)



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

column = 'Claim Amount'
# Compute Q1, Q3, and IQR
Q1 = df[column].quantile(0.25)
Q3 = df[column].quantile(0.75)
IQR = Q3 - Q1

# Define thresholds
mild_upper = Q3 + 1.5 * IQR
extreme_upper = Q3 + 3 * IQR

# Categorize claims
def classify_outlier(value):
    if value > extreme_upper:
        return "Extreme Outlier"
    elif value > mild_upper:
        return "Mild Outlier"
    else:
        return "Normal"

df['Outlier Level'] = df[column].apply(classify_outlier)
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
outlier = st.sidebar.multiselect("Select Outlier Level", options=df['Outlier Level'].unique())
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
if 'Outlier Level' in df.columns and outlier:
    df = df[df['Outlier Level'].isin(outlier)]
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
if outlier:
     filter_description += f"{', '.join(map(str, outlier))} "
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


# Filter data by product type
df_health = df[df['Product'] == 'Health Insurance']
df_proactiv = df[df['Product'] == 'ProActiv']

# Filter data by claim status
df_app = df[df['Claim Status'] == 'Approved']
df_dec = df[df['Claim Status'] == 'Declined']

if not df.empty:
    scale = 1_000_000  # For millions
    scaling = 1000  # For thousands

    # General Metrics
    total_claim_amount = (df["Claim Amount"].sum()) / scale
    average_amount = (df["Claim Amount"].mean()) / scaling
    average_app_amount = (df["Approved Claim Amount"].mean()) / scaling

    total_app_claim_amount = (df_app["Approved Claim Amount"].sum()) / scale
    total_dec_claim_amount = (df_dec["Claim Amount"].sum()) / scaling

    total_app = df_app["Claim ID"].nunique()
    total_dec = df_dec["Claim ID"].nunique()

    total_clients = df["Employer Name"].nunique()
    total_claims = df["Claim ID"].nunique()

    approval_rate = (total_app / total_claims) * 100 if total_claims > 0 else 0
    denial_rate = (total_dec / total_claims) * 100 if total_claims > 0 else 0

    # Fraud-Specific Metrics (IQR-Based)
    Q1 = df['Claim Amount'].quantile(0.25)
    Q3 = df['Claim Amount'].quantile(0.75)
    IQR = Q3 - Q1
    mild_upper = Q3 + 1.5 * IQR
    extreme_upper = Q3 + 3 * IQR

    def classify_outlier(value):
        if value > extreme_upper:
            return "Extreme Outlier"
        elif value > mild_upper:
            return "Mild Outlier"
        else:
            return "Normal"

    df['Outlier Level'] = df['Claim Amount'].apply(classify_outlier)

    total_mild_outliers = (df['Outlier Level'] == 'Mild Outlier').sum()
    total_extreme_outliers = (df['Outlier Level'] == 'Extreme Outlier').sum()
    total_normal_outliers = (df['Outlier Level'] == 'Normal').sum()

    # High-Frequency Providers/Members
    top_providers = df.groupby('Provider Name')['Claim ID'].count().nlargest(5).reset_index()
    top_members = df.groupby('Member Name')['Claim ID'].count().nlargest(5).reset_index()

    # Discrepancies Between Requested and Approved Amounts
    df['Amount Discrepancy'] = abs(df['Claim Amount'] - df['Approved Claim Amount'])
    avg_discrepancy = df['Amount Discrepancy'].mean()
    high_discrepancy_claims = df[df['Amount Discrepancy'] > avg_discrepancy * 2]['Claim ID'].nunique()  # Claims with discrepancies > 2x average

    # Define CSS for the styled boxes and tooltips
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

    # Display general metrics
    st.markdown('<h2 class="custom-subheader">General Metrics</h2>', unsafe_allow_html=True)
    cols1, cols2, cols3 = st.columns(3)
    display_metric(cols1, "Number of Clients", total_clients)
    display_metric(cols2, "Number of Claims", f"{total_claims:,}")
    display_metric(cols3, "Total Claim Amount", f"{total_claim_amount:,.0f} M")
    display_metric(cols1, "Approval Rate", f"{approval_rate:.2f} %")
    display_metric(cols2, "Denial Rate", f"{denial_rate:.2f} %")
    display_metric(cols3, "Average Claim Amount", f"{average_amount:,.1f} K")

    # Display fraud-specific metrics
    st.markdown('<h2 class="custom-subheader">Fraud Detection Metrics</h2>', unsafe_allow_html=True)
    cols1, cols2, cols3, cols4 = st.columns(4)

    display_metric(cols1, "Normal Claims", total_normal_outliers)
    display_metric(cols2, "Mild Outliers", total_mild_outliers)
    display_metric(cols3, "Extreme Outliers", total_extreme_outliers)
    display_metric(cols4, "High Discrepancy Claims", high_discrepancy_claims)


    custom_colors = ["#009DAE", "#e66c37", "#461b09", "#f8a785", "#9ACBD0","#CC3636"]

    col1, col2 = st.columns(2)

    # Group data by Claim Created Date and Outlier Level, and count occurrences
    outlier_count = (
        df.groupby([df["Claim Created Date"].dt.strftime("%Y-%m-%d"), "Outlier Level"])
        .size()
        .reset_index(name="Count")
    )

    # Pivot the data for plotting (Outlier Level as columns)
    pivot_outlier = outlier_count.pivot(
        index="Claim Created Date", columns="Outlier Level", values="Count"
    ).fillna(0)

    # Sort the data by date
    pivot_outlier = pivot_outlier.sort_index()

    with col1:
        # Create the stacked area chart
        fig_outlier_time = go.Figure()

        # Add traces for each Outlier Level
        for i, outlier_level in enumerate(pivot_outlier.columns):
            fig_outlier_time.add_trace(
                go.Scatter(
                    x=pivot_outlier.index,
                    y=pivot_outlier[outlier_level],
                    mode="lines",
                    stackgroup="one",  # This creates a stacked area chart
                    name=outlier_level,
                    line=dict(width=0.5, color=custom_colors[i % len(custom_colors)]),
                    hoverinfo="x+y+name",
                    fillcolor=custom_colors[i % len(custom_colors)],
                )
            )

        # Update layout
        fig_outlier_time.update_layout(
            xaxis_title="Claim Created Date",
            yaxis_title="Number of Claims",
            font=dict(color="Black"),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), tickangle=45),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation="h"),  # Place legend above the chart
            height=450,
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Outlier Distribution Over Time</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_outlier_time, use_container_width=True)

    # Filter claims with high discrepancies
    high_discrepancy_data = df[df["Amount Discrepancy"] > avg_discrepancy * 2]

    # Group data by Provider Name to calculate total discrepancy
    provider_discrepancy = (
        high_discrepancy_data.groupby("Provider Name")["Amount Discrepancy"]
        .sum()
        .reset_index()
    )

    # Sort providers by total discrepancy
    provider_discrepancy = provider_discrepancy.sort_values(by="Amount Discrepancy", ascending=False).head(10)

    with col2:

        # Create the bar chart
        fig_discrepancy = go.Figure()

        fig_discrepancy.add_trace(
            go.Bar(
                x=provider_discrepancy["Provider Name"],
                y=provider_discrepancy["Amount Discrepancy"],
                text=[f"{value / 1e3:.0f}K" for value in provider_discrepancy["Amount Discrepancy"]],
                textposition="inside",
                textfont=dict(color="white"),
                hoverinfo="x+y",
                marker_color="#009DAE",
            )
        )

        # Update layout
        fig_discrepancy.update_layout(
            xaxis_title="Provider Name",
            yaxis_title="Total Discrepancy ()",
            font=dict(color="Black"),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), tickangle=45),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=50, b=50),
            height=500,
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Discrepancy Between Requested and Approved Amounts</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_discrepancy, use_container_width=True)

    # Group by Outlier Level and sum the Claim Amount
    outlier_claim_amount = (
        df.groupby("Outlier Level")["Claim Amount"]
        .sum()
        .reset_index(name="Total Claim Amount")
    )

    # Sort by Total Claim Amount in descending order
    outlier_claim_amount = outlier_claim_amount.sort_values(by="Total Claim Amount", ascending=False)

    cols1, cols2 = st.columns(2)

    with cols1:
        # Create the bar chart for outliers by claim amount
        fig_outlier_claim_amount = go.Figure()

        # Add traces for each Outlier Level
        for i, outlier_level in enumerate(outlier_claim_amount["Outlier Level"]):
            fig_outlier_claim_amount.add_trace(
                go.Bar(
                    x=[outlier_level],  # Outlier Level as x-axis
                    y=outlier_claim_amount.loc[outlier_claim_amount["Outlier Level"] == outlier_level, "Total Claim Amount"],
                    name=outlier_level,
                    text=[
                        f"{value / 1e6:.1f}M"
                        for value in outlier_claim_amount.loc[
                            outlier_claim_amount["Outlier Level"] == outlier_level, "Total Claim Amount"
                        ]
                    ],  # Format text as X.M
                    textposition="inside",
                    textfont=dict(color="white"),
                    hoverinfo="x+y+name",
                    marker_color=custom_colors[i % len(custom_colors)],  # Assign color based on index
                )
            )

        # Set layout for the Outliers by Claim Amount chart
        fig_outlier_claim_amount.update_layout(
            barmode="stack",  # Stacked bar chart
            xaxis_title="Outlier Level",
            yaxis_title="Total Claim Amount ()",
            font=dict(color="Black"),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=500,
            legend=dict(x=0, y=1.1, orientation="h"),  # Place legend above the chart
        )

        # Display the Outliers by Claim Amount chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Outliers by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_outlier_claim_amount, use_container_width=True)

    # Group data by "Product" and "Outlier Level" and count the number of claims
    product_outliers = df.groupby(['Product', 'Outlier Level'])['Claim ID'].count().unstack().fillna(0)
    # Ensure all outlier levels are present in the columns (even if some products don't have certain levels)
    product_outliers = product_outliers.reindex(columns=["Normal", "Mild Outlier", "Extreme Outlier"], fill_value=0)

    with cols2:
        fig_product_outliers = go.Figure()

        # Add traces for each Outlier Level
        for i, outlier_level in enumerate(product_outliers.columns):
            fig_product_outliers.add_trace(go.Bar(
                x=product_outliers.index,
                y=product_outliers[outlier_level],
                name=outlier_level,
                text=product_outliers[outlier_level].apply(lambda x: f"{x}" if x > 0 else ""),  # Show raw count
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[i % len(custom_colors)],
            ))

        # Set layout for the Number of Claims by Product and Outlier Level chart
        fig_product_outliers.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Product",
            yaxis_title="Number of Claims",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the Number of Claims by Product and Outlier Level chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Outliers by Number of Claims and Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_product_outliers, use_container_width=True)


    # Group data by Month and Outlier Level to count occurrences
    monthly_outliers = (
        df.groupby(["Month", "Outlier Level"])["Claim ID"]
        .count()
        .reset_index(name="Count")
    )

    # Define the correct order of months
    sorted_months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Convert the 'Month' column to a categorical type with the specified order
    monthly_outliers['Month'] = pd.Categorical(
        monthly_outliers['Month'], categories=sorted_months, ordered=True
    )

    # Sort by the 'Month' column
    monthly_outliers = monthly_outliers.sort_values(by="Month")

    cols1, cols2 = st.columns(2)

    # Create the grouped bar chart for monthly outliers
    with cols2:
        fig_monthly_outliers = go.Figure()

        # Add trace for each Outlier Level
        for i, outlier_level in enumerate(monthly_outliers["Outlier Level"].unique()):
            filtered_data = monthly_outliers[monthly_outliers["Outlier Level"] == outlier_level]
            fig_monthly_outliers.add_trace(
                go.Bar(
                    x=filtered_data["Month"],
                    y=filtered_data["Count"],
                    name=outlier_level,
                    text=[f"{value}" for value in filtered_data["Count"]],
                    textposition="inside",
                    textfont=dict(color="white"),
                    hoverinfo="x+y+name",
                    marker_color=custom_colors[i % len(custom_colors)],  # Assign color based on index
                )
            )

        # Set layout for the chart
        fig_monthly_outliers.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Month",
            yaxis_title="Number of Outliers",
            font=dict(color="Black"),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=50, b=50),
            height=500,
            legend=dict(title="Outlier Level"),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Number of Monthly Outliers</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_outliers, use_container_width=True)

    # Group data by Year and Outlier Level to count occurrences
    yearly_outliers = (
        df.groupby(["Year", "Outlier Level"])["Claim ID"]
        .count()
        .reset_index(name="Count")
    )

    # Sort by Year
    yearly_outliers = yearly_outliers.sort_values(by="Year")

    # Create the grouped bar chart for yearly outliers
    with cols1:
        fig_yearly_outliers = go.Figure()

        # Add trace for each Outlier Level
        for i, outlier_level in enumerate(yearly_outliers["Outlier Level"].unique()):
            filtered_data = yearly_outliers[yearly_outliers["Outlier Level"] == outlier_level]
            fig_yearly_outliers.add_trace(
                go.Bar(
                    x=filtered_data["Year"],
                    y=filtered_data["Count"],
                    name=outlier_level,
                    text=[f"{value}" for value in filtered_data["Count"]],
                    textposition="inside",
                    textfont=dict(color="white"),
                    hoverinfo="x+y+name",
                    marker_color=custom_colors[i % len(custom_colors)],  # Assign color based on index
                )
            )

        # Set layout for the chart
        fig_yearly_outliers.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Number of Outliers",
            font=dict(color="Black"),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=50, b=50),
            height=500,
            legend=dict(title="Outlier Level"),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Number of Yearly Outliers</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_outliers, use_container_width=True)

    col1, col2 = st.columns(2)

    # Group by Claim Type and Outlier Level, then count the number of claims
    claim_type_count = (
        df.groupby(['Claim Type', 'Outlier Level'])['Claim ID']
        .count()
        .reset_index(name="Count")
    )

    # Pivot the data for plotting (Outlier Level as columns)
    pivot_claim_type = claim_type_count.pivot(
        index="Claim Type", columns="Outlier Level", values="Count"
    ).fillna(0)

    # Ensure all outlier levels are present in the columns
    pivot_claim_type = pivot_claim_type.reindex(columns=["Normal", "Mild Outlier", "Extreme Outlier"], fill_value=0)

    with col1:
        fig_claim_type = go.Figure()

        # Add traces for each Outlier Level
        for i, outlier_level in enumerate(pivot_claim_type.columns):
            fig_claim_type.add_trace(
                go.Bar(
                    x=pivot_claim_type.index,
                    y=pivot_claim_type[outlier_level],
                    name=outlier_level,
                    text=[f"{value}" for value in pivot_claim_type[outlier_level]],  # Show raw count
                    textposition="inside",
                    textfont=dict(color="white"),
                    hoverinfo="x+y+name",
                    marker_color=custom_colors[i % len(custom_colors)],  # Assign color based on index
                )
            )

        # Set layout for the Claim Type chart
        fig_claim_type.update_layout(
            barmode='group',
            yaxis_title="Number of Claims",
            xaxis_title="Claim Type",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Number of Outliers by Claim Type </h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_claim_type, use_container_width=True)
 

    # Group by Source and Outlier Level, then count the number of claims
    source_count = (
        df.groupby(['Source', 'Outlier Level'])['Claim ID']
        .count()
        .reset_index(name="Count")
    )

    # Pivot the data for plotting (Outlier Level as columns)
    pivot_source = source_count.pivot(
        index="Source", columns="Outlier Level", values="Count"
    ).fillna(0)

    # Ensure all outlier levels are present in the columns
    pivot_source = pivot_source.reindex(columns=["Normal", "Mild Outlier", "Extreme Outlier"], fill_value=0)

    with col2:
        fig_source = go.Figure()

        # Add traces for each Outlier Level
        for i, outlier_level in enumerate(pivot_source.columns):
            fig_source.add_trace(
                go.Bar(
                    x=pivot_source.index,
                    y=pivot_source[outlier_level],
                    name=outlier_level,
                    text=[f"{value}" for value in pivot_source[outlier_level]],  # Show raw count
                    textposition="inside",
                    textfont=dict(color="white"),
                    hoverinfo="x+y+name",
                    marker_color=custom_colors[i % len(custom_colors)],  # Assign color based on index
                )
            )

        # Set layout for the Source chart
        fig_source.update_layout(
            barmode='group',
            yaxis_title="Number of Claims",
            xaxis_title="Source",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Number of Outliers by Provider Type</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_source, use_container_width=True)


    cols1, cols2 = st.columns(2)


    # Group data by Provider Name and Outlier Level to count the number of claims
    provider_outlier_count = (
        df.groupby(["Employer Name", "Outlier Level"])["Claim ID"]
        .count()
        .reset_index(name="Count")
    )

    # Pivot the data for plotting (Outlier Level as columns)
    pivot_provider_outlier = provider_outlier_count.pivot(
        index="Employer Name", columns="Outlier Level", values="Count"
    ).fillna(0)

    # Sort providers by total number of claims
    pivot_provider_outlier["Total"] = pivot_provider_outlier.sum(axis=1)
    pivot_provider_outlier = (
        pivot_provider_outlier.sort_values(by="Total", ascending=False).head(10).drop(columns=["Total"])
    )

    with cols1:
        fig_provider_outliers = go.Figure()

        # Add traces for each Outlier Level
        for i, outlier_level in enumerate(pivot_provider_outlier.columns):
            fig_provider_outliers.add_trace(
                go.Bar(
                    x=pivot_provider_outlier.index,
                    y=pivot_provider_outlier[outlier_level],
                    name=outlier_level,
                    text=[f"{value}" for value in pivot_provider_outlier[outlier_level]],  # Show raw count
                    textposition="inside",
                    textfont=dict(color="white"),
                    hoverinfo="x+y+name",
                    marker_color=custom_colors[i % len(custom_colors)],
                )
            )

        # Set layout for the Number of Claims by Provider (Outlier Highlighted) chart
        fig_provider_outliers.update_layout(
            barmode="stack",  # Stacked bar chart
            xaxis_title="Employer Name",
            yaxis_title="Number of Claims",
            font=dict(color="Black"),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), tickangle=45),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=500,
            legend=dict(x=0, y=1.1, orientation="h"),
        )

        # Display the Number of Claims by Provider (Outlier Highlighted) chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Employer Groups by Outlier and Claim Count </h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_provider_outliers, use_container_width=True)


    # Group data by Provider Name and Outlier Level to count the number of claims
    provider_outlier_count = (
        df.groupby(["Provider Name", "Outlier Level"])["Claim ID"]
        .count()
        .reset_index(name="Count")
    )

    # Pivot the data for plotting (Outlier Level as columns)
    pivot_provider_outlier = provider_outlier_count.pivot(
        index="Provider Name", columns="Outlier Level", values="Count"
    ).fillna(0)

    # Sort providers by total number of claims
    pivot_provider_outlier["Total"] = pivot_provider_outlier.sum(axis=1)
    pivot_provider_outlier = (
        pivot_provider_outlier.sort_values(by="Total", ascending=False).head(10).drop(columns=["Total"])
    )

    with cols2:
        fig_provider_outliers = go.Figure()

        # Add traces for each Outlier Level
        for i, outlier_level in enumerate(pivot_provider_outlier.columns):
            fig_provider_outliers.add_trace(
                go.Bar(
                    x=pivot_provider_outlier.index,
                    y=pivot_provider_outlier[outlier_level],
                    name=outlier_level,
                    text=[f"{value}" for value in pivot_provider_outlier[outlier_level]],  # Show raw count
                    textposition="inside",
                    textfont=dict(color="white"),
                    hoverinfo="x+y+name",
                    marker_color=custom_colors[i % len(custom_colors)],
                )
            )

        # Set layout for the Number of Claims by Provider (Outlier Highlighted) chart
        fig_provider_outliers.update_layout(
            barmode="stack",  # Stacked bar chart
            xaxis_title="Provider Name",
            yaxis_title="Number of Claims",
            font=dict(color="Black"),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), tickangle=45),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=500,
            legend=dict(x=0, y=1.1, orientation="h"),
        )

        # Display the Number of Claims by Provider (Outlier Highlighted) chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Providers by Outlier and Claim Count </h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_provider_outliers, use_container_width=True)

