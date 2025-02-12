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

st.markdown('<h1 class="main-title">CLAIMS ANALYSIS</h1>', unsafe_allow_html=True)



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

    custom_colors = ["#009DAE", "#e66c37", "#461b09", "#f8a785", "#CC3636","#9ACBD0"]

    cols1, cols2 = st.columns(2)

   
    # Group by day and count the occurrences
    area_chart_count = df.groupby(df["Claim Created Date"].dt.strftime("%Y-%m-%d")).size().reset_index(name='Count')
    area_chart_amount = df.groupby(df["Claim Created Date"].dt.strftime("%Y-%m-%d"))['Claim Amount'].sum().reset_index(name='Claim Amount')

    # Merge the count and amount data
    area_chart = pd.merge(area_chart_count, area_chart_amount, on='Claim Created Date')

    # Sort by the PreAuth Created Date
    area_chart = area_chart.sort_values("Claim Created Date")

    with cols1:
        # Create the dual-axis area chart
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig2.add_trace(
            go.Scatter(x=area_chart['Claim Created Date'], y=area_chart['Count'], name="Number of Claims", fill='tozeroy', line=dict(color='#e66c37')),
            secondary_y=False,
        )

        fig2.add_trace(
            go.Scatter(x=area_chart['Claim Created Date'], y=area_chart['Claim Amount'], name="Claim Amount", fill='tozeroy', line=dict(color='#009DAE')),
            secondary_y=True,
        )



        # Set x-axis title
        fig2.update_xaxes(title_text="Claim Created Date", tickangle=45)  # Rotate x-axis labels to 45 degrees for better readability

        # Set y-axes titles
        fig2.update_yaxes(title_text="<b>Number Of Claims</b>", secondary_y=False)
        fig2.update_yaxes(title_text="<b>Claim Amount</b>", secondary_y=True)

        st.markdown('<h3 class="custom-subheader">Number of Claims and Claim Amount Over Time</h3>', unsafe_allow_html=True)

        st.plotly_chart(fig2, use_container_width=True)



    # Group data by "Start Month Year" and "Claim Type" and calculate the average Approved Claim Amount
    yearly_avg_premium = df.groupby(['Year', 'Claim Status'])['Claim Amount'].sum().unstack().fillna(0)

    # Define custom colors

    with cols2:
        # Create the grouped bar chart
        fig_yearly_avg_premium = go.Figure()

        for idx, Client_Segment in enumerate(yearly_avg_premium.columns):
            fig_yearly_avg_premium.add_trace(go.Bar(
                x=yearly_avg_premium.index,
                y=yearly_avg_premium[Client_Segment],
                name=Client_Segment,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Average Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Yearly Claim Amount by Claim Status per Employer Group</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)

    # Group data by "Start Month" and "Channel" and sum the Approved Claim Amount sum
    monthly_premium = df.groupby(['Month', 'Claim Status'])['Claim Amount'].mean().unstack().fillna(0)

    # Group data by "Start Month" to count the number of sales
    monthly_sales_count = df.groupby(['Month']).size()



    # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls2:

        fig_monthly_premium = go.Figure()

        for idx, Client_Segment in enumerate(monthly_premium.columns):
                fig_monthly_premium.add_trace(go.Bar(
                    x=monthly_premium.index,
                    y=monthly_premium[Client_Segment],
                    name=Client_Segment,
                    textposition='inside',
                    textfont=dict(color='white'),
                    hoverinfo='x+y+name',
                    marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                ))


            # Set layout for the Approved Claim Amount sum chart
        fig_monthly_premium.update_layout(
                barmode='group',  # Grouped bar chart
                xaxis_title="Month",
                yaxis_title="Average Claim Amount",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50),
            )

            # Display the Approved Claim Amount sum chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Avearge Monthly Claim Amount by Claim Status</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

 # Group data by month
    monthly_visits = df.groupby('Month').size().reset_index(name='Number of Claims')
    monthly_amount = df.groupby('Month')['Claim Amount'].sum().reset_index(name='Claim Amount')

    # Merge monthly data for combined visualization
    monthly_data = pd.merge(monthly_visits, monthly_amount, on='Month')

    # Create a dual-axis bar chart for monthly visits and total amount
    fig_monthly = go.Figure()

    # First y-axis (Number of Visits)
    fig_monthly.add_trace(go.Bar(
        x=monthly_data['Month'],
        y=monthly_data['Number of Claims'],
        name='Number of Claims',
        marker_color='#e66c37',
        yaxis='y1'
    ))

    # Second y-axis (Total Visit Amount)
    fig_monthly.add_trace(go.Bar(
        x=monthly_data['Month'],
        y=monthly_data['Claim Amount'],
        name='Total Claim Amount',
        marker_color='#009DAE',
        yaxis='y2'
    ))

    fig_monthly.update_layout(
        xaxis=dict(title="Month", tickangle=45),
        yaxis=dict(title="Number of Claims", side='left'),
        yaxis2=dict(title="Total Claim Amount", overlaying='y', side='right', showgrid=False),
        barmode='group',
        margin=dict(l=0, r=0, t=30, b=50),
        height=450
    )
    # Display Monthly Chart
    with cls1:
        st.markdown('<h3 class="custom-subheader">Monthly Claims & Total Claim Amount Distribution</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly, use_container_width=True)

 


    # Create the layout columns
    cls1, cls2 = st.columns(2)
    
    # Calculate the Approved Claim Amount by Client Segment
    int_owner = df.groupby("Claim Type")["Claim Amount"].sum().reset_index()
    int_owner.columns = ["Claim Type", "Claim Amount"]    

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Claim Amount by Claim Type</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Claim Type", values="Claim Amount", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

# Calculate the Approved Claim Amount by Client Segment
    int_owner = df.groupby("Product")["Claim Amount"].sum().reset_index()
    int_owner.columns = ["Product", "Claim Amount"]    

    with cls2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Claim Amount by Product</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Product", values="Claim Amount", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)


    # Create the layout columns
    cls1, cls2 = st.columns(2)

    # Group by Diagnosis: Sum Claim Amount & Count Claims
    df_grouped_diag = df.groupby('Diagnosis').agg({'Claim Amount': 'sum', 'ICD-10 Code': 'count'}).nlargest(10, 'Claim Amount').reset_index()
    df_grouped_diag.rename(columns={'ICD-10 Code': 'Number of Claims'}, inplace=True)

    # Group by ICD-10 Code: Sum Claim Amount & Count Claims
    df_grouped_icd = df.groupby('ICD-10 Code').agg({'Claim Amount': 'sum', 'Diagnosis': 'count'}).nlargest(10, 'Claim Amount').reset_index()
    df_grouped_icd.rename(columns={'Diagnosis': 'Number of Claims'}, inplace=True)

    # Function to create a dual-axis chart
    def create_dual_axis_chart(df, x_col, y1_col, y2_col, x_title):
        fig = go.Figure()

        # Bar chart for Claim Amount
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y1_col],
            text=[f'{value/1e6:.0f}M' for value in df[y1_col]],
            textposition='auto',
            marker_color="#009DAE",
            name="Claim Amount",
            yaxis="y1"
        ))

        # Line chart for Number of Claims
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y2_col],
            mode='lines+markers',
            name="Number of Claims",
            yaxis="y2",
            line=dict(color="red", width=2),
            marker=dict(size=8, symbol="circle-open")
        ))

        fig.update_layout(
            xaxis_title=x_title,
            yaxis=dict(title="Claim Amount", side="left", showgrid=False),
            yaxis2=dict(title="Number of Claims", side="right", overlaying="y", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        return fig

    # Diagnosis Chart
    with cls1:
        st.markdown('<h3 class="custom-subheader">Top 10 Diagnoses by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(create_dual_axis_chart(df_grouped_diag, "Diagnosis", "Claim Amount", "Number of Claims", "Diagnosis"), use_container_width=True)

    # ICD-10 Chart
    with cls2:
        st.markdown('<h3 class="custom-subheader">Top 10 ICD-10 Codes by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(create_dual_axis_chart(df_grouped_icd, "ICD-10 Code", "Claim Amount", "Number of Claims", "ICD-10 Code"), use_container_width=True)


    # Group by Source and calculate the total number of claims and total claim amount
    df_source_grouped = df.groupby('Source').agg(
        Total_Claims=pd.NamedAgg(column='Claim ID', aggfunc='count'),
        Total_Claim_Amount=pd.NamedAgg(column='Claim Amount', aggfunc='sum')
    ).reset_index()

    # Sort the df_source_grouped by Total_Claims in descending order to find the most popular provider type
    df_source_grouped = df_source_grouped.sort_values(by='Total_Claims', ascending=False)

    # Get the most popular provider type
    most_popular_provider = df_source_grouped.iloc[0]['Source'] if not df_source_grouped.empty else "No Data"

    # Format Claim Amount with millions
    df_source_grouped['Claim_Amount_Formatted'] = df_source_grouped['Total_Claim_Amount'].apply(lambda x: f'{x/1e6:.0f}M')

    # Create the grouped bar chart
    with cls1:
        fig1 = go.Figure()

        # Add bars for Total Claims
        fig1.add_trace(go.Bar(
            x=df_source_grouped['Source'],
            y=df_source_grouped['Total_Claims'],
            name='Number of Claims',
            text=df_source_grouped['Total_Claims'],
            textposition='auto',
            marker_color="#e66c37"
        ))

        # Add bars for Total Claim Amount
        fig1.add_trace(go.Bar(
            x=df_source_grouped['Source'],
            y=df_source_grouped['Total_Claim_Amount'],
            name='Claim Amount',
            text=df_source_grouped['Claim_Amount_Formatted'],  # Use formatted text
            textposition='auto',
            marker_color="#009DAE"
        ))

        # Update layout for the grouped bar chart
        fig1.update_layout(
            barmode='group',  # Grouped bar chart
            yaxis_title="Value",
            xaxis_title="Provider Type",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=500,
            legend=dict(title="Metrics")
        )

        # Display the chart in Streamlit
        st.markdown(f'<h3 class="custom-subheader">Most Popular Provider Type: {most_popular_provider}</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True)


    # Group by Employer Name and Claim Status, then sum the Claim Amount
    df_grouped = df.groupby(['Employer Name', 'Claim Status'])['Claim Amount'].sum().reset_index()

    # Get the top 15 employers by total Claim Amount
    top_15_clients = df_grouped.groupby('Employer Name')['Claim Amount'].sum().nlargest(15).reset_index()

    # Filter the original DataFrame to include only the top 15 employers
    client_df = df_grouped[df_grouped['Employer Name'].isin(top_15_clients['Employer Name'])]

    # Sort the client_df by Claim Amount in descending order
    client_df = client_df.sort_values(by='Claim Amount', ascending=False)

    with cls2:
        # Create the stacked bar chart
        fig = go.Figure()

        # Add bars for each Claim Status
        for idx, claim_status in enumerate(client_df['Claim Status'].unique()):
            claim_status_data = client_df[client_df['Claim Status'] == claim_status]
            fig.add_trace(go.Bar(
                x=claim_status_data['Employer Name'],
                y=claim_status_data['Claim Amount'],
                name=claim_status,
                text=[f'{value/1e6:.0f}M' for value in claim_status_data['Claim Amount']],
                textposition='auto',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through colors
            ))

        fig.update_layout(
            barmode='stack',
            yaxis_title="Claim Amount",
            xaxis_title="Employer Name",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Clients by Claim Amount and Claim Status</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    # Group by ICD-10 Code and sum the Claim Amount
    df_icd_grouped = df.groupby('ICD-10 Code')['Claim Amount'].sum().nlargest(10).reset_index()

    # Sort the df_icd_grouped by Claim Amount in descending order
    df_icd_grouped = df_icd_grouped.sort_values(by='Claim Amount', ascending=False)

    with cls1:
        # Create the bar chart
        fig1 = go.Figure()

        # Add bars for each ICD-10 Code
        fig1.add_trace(go.Bar(
            x=df_icd_grouped['ICD-10 Code'],
            y=df_icd_grouped['Claim Amount'],
            text=[f'{value/1e6:.0f}M' for value in df_icd_grouped['Claim Amount']],
            textposition='auto',
            marker_color="#009DAE"
        ))

        fig1.update_layout(
            yaxis_title="Claim Amount",
            xaxis_title="ICD-10 Code",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 ICD-10 Codes by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True)




    # Group by Provider Name and Source, then sum the Claim Amount
    df_grouped = df.groupby(['Provider Name', 'Source'])['Claim Amount'].sum().reset_index()

    # Get the top 15 providers by total Claim Amount
    top_15_providers = df_grouped.groupby('Provider Name')['Claim Amount'].sum().nlargest(15).reset_index()

    # Filter the original DataFrame to include only the top 15 providers
    client_df = df_grouped[df_grouped['Provider Name'].isin(top_15_providers['Provider Name'])]

    # Sort the client_df by Claim Amount in descending order
    client_df = client_df.sort_values(by='Claim Amount', ascending=False)

    with cls2:
        # Create the stacked bar chart
        fig = go.Figure()

        # Add bars for each Source
        for idx, source in enumerate(client_df['Source'].unique()):
            source_data = client_df[client_df['Source'] == source]
            fig.add_trace(go.Bar(
                x=source_data['Provider Name'],
                y=source_data['Claim Amount'],
                name=source,
                text=[f'{value/1e6:.0f}M' for value in source_data['Claim Amount']],
                textposition='auto',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through colors
            ))

        fig.update_layout(
            barmode='stack',
            yaxis_title="Claim Amount",
            xaxis_title="Provider Name",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Providers by Claim Amount and Source</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    # Group by Employer Name and sum the Claim Amount
    df_grouped = df.groupby('Employer Name')['Claim Amount'].sum().nlargest(10).reset_index()

    # Sort the df_grouped by Claim Amount in descending order
    df_grouped = df_grouped.sort_values(by='Claim Amount', ascending=False)

    with cls1:
        # Create the bar chart
        fig = go.Figure()

        # Add bars for each Employer
        fig.add_trace(go.Bar(
            x=df_grouped['Employer Name'],
            y=df_grouped['Claim Amount'],
            text=[f'{value/1e6:.0f}M' for value in df_grouped['Claim Amount']],
            textposition='auto',
            marker_color="#009DAE"  # Use custom colors
        ))

        fig.update_layout(
            yaxis_title="Claim Amount",
            xaxis_title="Employer Name",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Employer Groups by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)


    # Group by Client Name and sum the Total Amount
    df_grouped = df.groupby('Provider Name')['Claim Amount'].sum().nlargest(10).reset_index()

    # Sort the client_df by Total Amount in descending order
    client_df = df_grouped.sort_values(by='Claim Amount', ascending=False)

    with cls2:
            # Create the bar chart
            fig = go.Figure()

            # Add bars for each Client
            fig.add_trace(go.Bar(
                x=client_df['Provider Name'],
                y=client_df['Claim Amount'],
                text=[f'{value/1e6:.0f}M' for value in client_df['Claim Amount']],
                textposition='auto',
                marker_color="#009DAE"
            ))

            fig.update_layout(
                yaxis_title="Claim Amount",
                xaxis_title="Provider Name",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )


            # Display the chart in Streamlit
            st.markdown('<h3 class="custom-subheader">Top 10 Popular Service Providers by Claim Amount</h3>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)