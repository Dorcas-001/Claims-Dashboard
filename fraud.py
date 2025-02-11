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


df
df_outlier = df[df['Outlier Level'] == 'Extreme Outlier']
df_normal = df[df['Outlier Level'] == 'Normal']
df_mild = df[df['Outlier Level'] == 'Mild Outlier']

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
    total_claim_amount
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

    total_app_claim_amount = (df_app["Claim Amount"].sum())/scale
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

    total_outlier = (df_outlier["Claim Amount"].sum())/scale
    total_normal = (df_normal["Claim Amount"].sum())/scale
    total_mild = (df_mild["Claim Amount"].sum())/scale

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

    # Calculate key metrics
    st.markdown(f'<h2 class="custom-subheader">For all Claim Amounts ({filter_description.strip()})</h2>', unsafe_allow_html=True)    

    # Function to display a colored metric
    def display_colored_metric(column, title, value, color):
        column.markdown(
            f"""
            <div style="
                background-color: {color}; 
                padding: 10px; 
                border-radius: 10px; 
                text-align: center; 
                color: white; 
                font-size: 18px;">
                <b>{title}</b><br>
                {value}
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Define custom colors for Outlier levels

    normal_color = "#009DAE"  
    mild_outlier_color = "#e66c37"  
    outlier_color = "red"

    cols1,cols2, cols3 = st.columns(3)
    # Display metrics with colors
    display_colored_metric(cols1, "Total Normal Claim Amount", f"{total_normal:,.1f} M", normal_color)
    display_colored_metric(cols2, "Total Mild Outlier Claim Amount", f"{total_mild:,.1f} M", mild_outlier_color)
    display_colored_metric(cols3, "Total Extreme Outlier Claim Amount", f"{total_outlier:,.1f} M", outlier_color)

    st.dataframe(df)
    custom_colors = {
        "Normal": "#009DAE",          # Teal for Normal claims
        "Mild Outlier": "#461b09",    # Dark brown for Mild Outliers
        "Extreme Outlier": "red"      # Red for Extreme Outliers
    }

    # Mild outlier bounds
    mild_lower = Q1 - 1.5 * IQR
    mild_upper = Q3 + 1.5 * IQR

    # Extreme outlier bounds
    extreme_lower = Q1 - 3 * IQR
    extreme_upper = Q3 + 3 * IQR

    # Create two columns
    col1, col2 = st.columns(2)

    # --- 1️⃣ YEARLY CLAIM AMOUNT BY OUTLIER LEVEL ---
    with col1:
        yearly_outlier_summary = df.groupby(['Year', 'Outlier Level'])['Claim Amount'].sum().unstack().fillna(0)

        fig_yearly_outliers = go.Figure()
        for outlier_level in yearly_outlier_summary.columns:
            fig_yearly_outliers.add_trace(go.Bar(
                x=yearly_outlier_summary.index,
                y=yearly_outlier_summary[outlier_level],
                name=outlier_level,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors.get(outlier_level, "gray")
            ))

        fig_yearly_outliers.update_layout(
            barmode='group',
            xaxis_title="Year",
            yaxis_title="Total Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        st.markdown('<h3 class="custom-subheader">Yearly Claim Amount by Outlier Level</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_outliers, use_container_width=True)
        


    # Group data by "Product" and "Outlier Level" and sum the Claim Amount
    product_outliers = df.groupby(['Product', 'Outlier Level'])['Claim Amount'].sum().unstack().fillna(0)

    # Ensure all outlier levels are present in the columns (even if some products don't have certain levels)
    product_outliers = product_outliers.reindex(columns=["Normal", "Mild Outlier", "Extreme Outlier"], fill_value=0)

    with col1:
        fig_product_outliers = go.Figure()

        # Add traces for each Outlier Level
        for outlier_level in product_outliers.columns:
            fig_product_outliers.add_trace(go.Bar(
                x=product_outliers.index,
                y=product_outliers[outlier_level],
                name=outlier_level,
                text=product_outliers[outlier_level].apply(lambda x: f"${x/1e6:.1f}M" if x > 0 else ""),  # Format text as $X.M
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors.get(outlier_level, "gray")  # Assign color based on outlier level
            ))

        # Set layout for the Claim Amount by Product and Outlier Level chart
        fig_product_outliers.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Product",
            yaxis_title="Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the Claim Amount by Product and Outlier Level chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Outliers by Claim Amount and Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_product_outliers, use_container_width=True)

    # Group data by "Month" and "Outlier Level" and sum the Approved Claim Amount
    monthly_premium = df.groupby(['Month', 'Outlier Level'])['Claim Amount'].sum().unstack().fillna(0)

    # Group data by "Month" to count the number of claims
    monthly_sales_count = df.groupby(['Month']).size()

    with col2:
        fig_monthly_premium = go.Figure()

        # Add traces for each Outlier Level
        for idx, outlier_level in enumerate(monthly_premium.columns):
            fig_monthly_premium.add_trace(go.Bar(
                x=monthly_premium.index,
                y=monthly_premium[outlier_level],
                name=outlier_level,
                text=monthly_premium[outlier_level].apply(lambda x: f"${x/1e6:.1f}M" if x > 0 else ""),  # Format text as $X.M
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors.get(outlier_level, "gray")  # Assign color based on outlier level
            ))

        # Set layout for the Approved Claim Amount sum chart
        fig_monthly_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Month",
            yaxis_title="Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the Approved Claim Amount sum chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Monthly Claim Amount by Outlier Level</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

    # --- 2️⃣ BOX AND WHISKER PLOT FOR CLAIM AMOUNT ---
    with col2:

        
        # Define lower and upper bounds for outliers
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Create the box and whisker plot
        fig_boxplot = go.Figure()
        fig_boxplot.add_trace(go.Box(
            y=df[column],
            name="Claim Amount",
            boxpoints='outliers', 
            jitter=0.3, 
            pointpos=-1.8,     
            marker_color="#009DAE",
            line_color="#e66c37",
            fillcolor='rgba(93, 164, 214, 0.2)'
        ))
        
        fig_boxplot.update_layout(
            yaxis_title="Claim Amount",
            font=dict(color='Black'),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=50, b=50),
            height=450
        )
        
        st.markdown('<h3 class="custom-subheader">Claims Abnormalities by Outliers</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_boxplot, use_container_width=True)



    # Define lower and upper bounds for outliers
    lower_bound_mild = Q1 - 1.5 * IQR
    upper_bound_mild = Q3 + 1.5 * IQR
    lower_bound_extreme = Q1 - 3 * IQR
    upper_bound_extreme = Q3 + 3 * IQR

    # Categorize data into "Normal", "Mild Outlier", and "Extreme Outlier"
    df['Outlier Level'] = df[column].apply(
        lambda x: "Extreme Outlier" if x < extreme_lower or x > extreme_upper 
        else "Mild Outlier" if x < mild_lower or x > mild_upper 
        else "Normal"
    )
    # Group by Outlier Level and aggregate Claim Amount and Claim Count
    df_grouped = df.groupby(['Outlier Level']).agg({'Claim Amount': 'sum', 'Claim ID': 'count'}).reset_index()
    df_grouped.rename(columns={'Claim ID': 'Claim Count'}, inplace=True)

    # Define custom colors for each outlier level
    outlier_colors = {
        "Normal": "#009DAE",          # Blue for Normal claims
        "Mild Outlier": "#461b09",    # Orange for Mild Outliers
        "Extreme Outlier": "red"  # Dark Red for Extreme Outliers
    }


    # Assign colors to the grouped data
    df_grouped['Color'] = df_grouped['Outlier Level'].map(outlier_colors)

    with col1:
        # Create a dual-axis bar and line chart
        fig = go.Figure()

        # Add bar trace for Claim Amount (using color mapping)
        fig.add_trace(go.Bar(
            x=df_grouped['Outlier Level'],
            y=df_grouped['Claim Amount'],
            name='Claim Amount',
            text=[f'{value/1e6:.0f}M' for value in df_grouped['Claim Amount']],
            textposition='auto',
            marker_color=df_grouped['Color'],  # Apply color mapping
            yaxis='y1'
        ))

        # Add line trace for Claim Count (using color mapping)
        fig.add_trace(go.Scatter(
            x=df_grouped['Outlier Level'],
            y=df_grouped['Claim Count'],
            name='Claim Count',
            mode='lines+markers',
            marker=dict(color=df_grouped['Color'], size=8),  # Apply color mapping
            line=dict(color="gray"),  # Line color in gray for better distinction
            yaxis='y2'
        ))

        fig.update_layout(
            xaxis_title="Outlier Level",
            yaxis=dict(
                title="Claim Amount",
                title_font=dict(color="gray"),  # Correct property name
                tickfont=dict(color="gray")
            ),
            yaxis2=dict(
                title="Number of Claims",
                title_font=dict(color="gray"),  # Correct property name
                tickfont=dict(color="gray"),
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0, y=1.1, orientation='h'),
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Claim Amount and Number of Claims by Outlier Level</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)




    # Create two columns

    # --- Chart 1: Claim Type by Outlier Level ---
    # Group by Claim Type and Outlier Level, then sum the Claim Amount
    df_grouped = df.groupby(['Claim Type', 'Outlier Level'])['Claim Amount'].sum().reset_index()
    # Sort the df_grouped by Claim Amount in descending order
    claim_type_df = df_grouped.sort_values(by='Claim Amount', ascending=False)

    with col2:
        # Create the grouped bar chart
        fig_claim_type = go.Figure()

        # Add bars for each Outlier Level
        for outlier_level in claim_type_df['Outlier Level'].unique():
            outlier_level_data = claim_type_df[claim_type_df['Outlier Level'] == outlier_level]
            fig_claim_type.add_trace(go.Bar(
                x=outlier_level_data['Claim Type'],
                y=outlier_level_data['Claim Amount'],
                name=outlier_level,
                text=[f'{value/1e6:.0f}M' for value in outlier_level_data['Claim Amount']],
                textposition='auto',
                marker_color=custom_colors.get(outlier_level, "gray")  # Assign color based on outlier level
            ))

        # Set layout for the Claim Type chart
        fig_claim_type.update_layout(
            barmode='group',
            yaxis_title="Claim Amount",
            xaxis_title="Claim Type",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Claim Type Outlier Level by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_claim_type, use_container_width=True)

    # --- Chart 2: Provider Type by Outlier Level ---
    # Group by Source (Provider Type) and Outlier Level, then sum the Claim Amount
    df_grouped = df.groupby(['Source', 'Outlier Level'])['Claim Amount'].sum().reset_index()
    # Sort the df_grouped by Claim Amount in descending order
    provider_type_df = df_grouped.sort_values(by='Claim Amount', ascending=False)

    with col1:
        # Create the grouped bar chart
        fig_provider_type = go.Figure()

        # Add bars for each Outlier Level
        for outlier_level in provider_type_df['Outlier Level'].unique():
            outlier_level_data = provider_type_df[provider_type_df['Outlier Level'] == outlier_level]
            fig_provider_type.add_trace(go.Bar(
                x=outlier_level_data['Source'],
                y=outlier_level_data['Claim Amount'],
                name=outlier_level,
                text=[f'{value/1e6:.0f}M' for value in outlier_level_data['Claim Amount']],
                textposition='auto',
                marker_color=custom_colors.get(outlier_level, "gray")  # Assign color based on outlier level
            ))

        # Set layout for the Provider Type chart
        fig_provider_type.update_layout(
            barmode='group',
            yaxis_title="Claim Amount",
            xaxis_title="Provider Type",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Provider Type Outlier Level by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_provider_type, use_container_width=True)




    # --- Chart 1: Top 10 Diagnoses by Outlier Level ---
    # Group by Diagnosis and Outlier Level, then sum the Claim Amount
    df_grouped = df.groupby(['Diagnosis', 'Outlier Level'])['Claim Amount'].sum().reset_index()

    # Get the top 10 diagnoses by total Claim Amount
    top_10_diagnoses = df_grouped.groupby('Diagnosis')['Claim Amount'].sum().nlargest(10).reset_index()

    # Filter the original DataFrame to include only the top 10 diagnoses
    diagnosis_df = df_grouped[df_grouped['Diagnosis'].isin(top_10_diagnoses['Diagnosis'])]

    # Sort the diagnosis_df by Claim Amount in descending order
    diagnosis_df = diagnosis_df.sort_values(by='Claim Amount', ascending=False)

    with col2:
        # Create the grouped bar chart
        fig_diagnosis = go.Figure()

        # Add bars for each Outlier Level
        for outlier_level in diagnosis_df['Outlier Level'].unique():
            outlier_level_data = diagnosis_df[diagnosis_df['Outlier Level'] == outlier_level]
            fig_diagnosis.add_trace(go.Bar(
                x=outlier_level_data['Diagnosis'],
                y=outlier_level_data['Claim Amount'],
                name=outlier_level,
                text=[f'{value/1e6:.0f}M' for value in outlier_level_data['Claim Amount']],
                textposition='auto',
                marker_color=custom_colors.get(outlier_level, "gray")  # Assign color based on outlier level
            ))

        # Set layout for the Diagnosis chart
        fig_diagnosis.update_layout(
            barmode='group',
            yaxis_title="Claim Amount",
            xaxis_title="Diagnosis",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=10)),  # Adjust tick font size for readability
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Diagnoses by Outlier Level</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_diagnosis, use_container_width=True)

    # --- Chart 2: Top 10 ICD-10 Codes by Outlier Level ---
    # Group by ICD-10 Code and Outlier Level, then sum the Claim Amount
    df_grouped = df.groupby(['ICD-10 Code', 'Outlier Level'])['Claim Amount'].sum().reset_index()

    # Get the top 10 ICD-10 codes by total Claim Amount
    top_10_icd10 = df_grouped.groupby('ICD-10 Code')['Claim Amount'].sum().nlargest(10).reset_index()

    # Filter the original DataFrame to include only the top 10 ICD-10 codes
    icd10_df = df_grouped[df_grouped['ICD-10 Code'].isin(top_10_icd10['ICD-10 Code'])]

    # Sort the icd10_df by Claim Amount in descending order
    icd10_df = icd10_df.sort_values(by='Claim Amount', ascending=False)

    with col1:
        # Create the grouped bar chart
        fig_icd10 = go.Figure()

        # Add bars for each Outlier Level
        for outlier_level in icd10_df['Outlier Level'].unique():
            outlier_level_data = icd10_df[icd10_df['Outlier Level'] == outlier_level]
            fig_icd10.add_trace(go.Bar(
                x=outlier_level_data['ICD-10 Code'],
                y=outlier_level_data['Claim Amount'],
                name=outlier_level,
                text=[f'{value/1e6:.0f}M' for value in outlier_level_data['Claim Amount']],
                textposition='auto',
                marker_color=custom_colors.get(outlier_level, "gray")  # Assign color based on outlier level
            ))

        # Set layout for the ICD-10 chart
        fig_icd10.update_layout(
            barmode='group',
            yaxis_title="Claim Amount",
            xaxis_title="ICD-10 Code",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=10)),  # Adjust tick font size for readability
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 ICD-10 Codes by Outlier Level</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_icd10, use_container_width=True)


    # Group by Provider Name and Outlier Level, then sum the Claim Amount
    df_grouped = df.groupby(['Provider Name', 'Outlier Level'])['Claim Amount'].sum().reset_index()

    # Get the top 10 providers by total Claim Amount
    top_10_providers = df_grouped.groupby('Provider Name')['Claim Amount'].sum().nlargest(10).reset_index()

    # Filter the original DataFrame to include only the top 10 providers
    provider_df = df_grouped[df_grouped['Provider Name'].isin(top_10_providers['Provider Name'])]

    # Sort the provider_df by Claim Amount in descending order
    provider_df = provider_df.sort_values(by='Claim Amount', ascending=False)

    with col2:
        # Create the grouped bar chart
        fig_providers = go.Figure()

        # Add bars for each Outlier Level
        for outlier_level in provider_df['Outlier Level'].unique():
            outlier_level_data = provider_df[provider_df['Outlier Level'] == outlier_level]
            fig_providers.add_trace(go.Bar(
                x=outlier_level_data['Provider Name'],
                y=outlier_level_data['Claim Amount'],
                name=outlier_level,
                text=[f'{value/1e6:.0f}M' for value in outlier_level_data['Claim Amount']],
                textposition='auto',
                marker_color=custom_colors.get(outlier_level, "gray")  # Assign color based on outlier level
            ))

        # Set layout for the Provider Name chart
        fig_providers.update_layout(
            barmode='group',
            yaxis_title="Claim Amount",
            xaxis_title="Provider Name",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=10)),  # Adjust tick font size for readability
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(x=0, y=1.1, orientation='h')  # Place legend above the chart
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Service Providers by Outlier Level</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_providers, use_container_width=True)