import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import chain
from matplotlib.ticker import FuncFormatter


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

st.markdown('<h1 class="main-title">Eden Care Claims View</h1>', unsafe_allow_html=True)

filepath="ALL 2024 CLAIMS.xlsx"

# Read all sheets into a dictionary of DataFrames
df = pd.read_excel(filepath)



# Ensure the 'Start Date' column is in datetime format if needed
df["Start Date"] = pd.to_datetime(df["Claim Created Date"], errors='coerce')
# Get minimum and maximum dates for the date input
startDate = df["Start Date"].min()
endDate = df["Start Date"].max()

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

# Filter DataFrame based on the selected dates
df = df[(df["Start Date"] >= date1) & (df["Start Date"] <= date2)].copy()


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



month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}
# Sort months based on their order
sorted_months = sorted(df['Month'].dropna().unique(), key=lambda x: month_order[x])
# Sidebar for filters
st.sidebar.header("Filters")
month = st.sidebar.multiselect("Select Month", options=sorted_months)
claim_type = st.sidebar.multiselect("Select Claim Type", options=df['Claim Type'].unique())
status = st.sidebar.multiselect("Select Status", options=df['Claim Status'].unique())
em_group = st.sidebar.multiselect("Select Employer Group", options=df['Employer Name'].unique())
prov_name = st.sidebar.multiselect("Select Service Provider", options=df['Provider Name'].unique())



# Apply filters to the DataFrame
if month:
    df = df[df['Month'].isin(month)]
if claim_type:
    df = df[df['Claim Type'].isin(claim_type)]
if status:
    df = df[df['Product_name'].isin(status)]
if em_group:
    df = df[df['Employer Name'].isin(em_group)]
if prov_name:
    df = df[df['Provider Name'].isin(prov_name)]



# Determine the filter description

df['Year'] = df['Year'].astype(int)

# Create a 'Month-Year' column
df['Month-Year'] = df['Month'] + ' ' + df['Year'].astype(str)


# Function to sort month-year combinations
def sort_key(month_year):
    month, year = month_year.split()
    return (int(year), month_order[month])

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

start_index = (int(start_year), month_order[start_month])
end_index = (int(end_year), month_order[end_month])

# Filter DataFrame based on month-year order indices
df = df[
    df['Month-Year'].apply(lambda x: (int(x.split()[1]), month_order[x.split()[0]])).between(start_index, end_index)
]

# Assuming the column name for the premium is 'Total Premium'

if not df.empty:
     # Calculate metrics
    scale=1_000_000  # For millions

    total_claims = (df["Claim Amount"].sum())/scale
    total_sp = df["Provider Name"].nunique()
    total_em = df["Employer Name"].nunique()
    app_claims = (df["Approved Claim Amount"].sum())/scale




    # Create 4-column layout for metric cards
    col1, col2, col3 = st.columns(3)

    # Define CSS for the styled boxes
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
        }
        .metric-title {
            color: #e66c37; /* Change this color to your preferred title color */
            font-size: 1em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 1.5em;
        }
        </style>
        """, unsafe_allow_html=True)

    # Function to display metrics in styled boxes
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    # Display metrics
    display_metric(col1, "Total Claims", value=f"RWF {total_claims:.0f} M")
    display_metric(col2, "Total Approved Claims", value=f"RWF {app_claims:.0f} M")
    display_metric(col3, "Total Employer Group", total_em)
    display_metric(col4, "Total Service Provider", total_sp)



   
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
    
    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

    st.markdown('<h2 class="custom-subheader">Number of Claims and Claim Amount Over Time</h2>', unsafe_allow_html=True)

  
    # Group by day and count the occurrences
    area_chart_count = df.groupby(df["Start Date"].dt.strftime("%Y-%m-%d")).size().reset_index(name='Count')
    area_chart_amount = df.groupby(df["Start Date"].dt.strftime("%Y-%m-%d"))['Claim Amount'].sum().reset_index(name='Total Amount')

    # Merge the count and amount data
    area_chart = pd.merge(area_chart_count, area_chart_amount, on='Start Date')

    # Sort by the PreAuth Created Date
    area_chart = area_chart.sort_values("Start Date")

    # Create the dual-axis area chart
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig2.add_trace(
        go.Scatter(
            x=area_chart['Start Date'], 
            y=area_chart['Count'], 
            name="Number of Claims", 
            fill='tozeroy', 
            line=dict(color='#e66c37')),
            secondary_y=False,
    )

    fig2.add_trace(
        go.Scatter(
            x=area_chart['Start Date'], 
            y=area_chart['Total Amount'], 
            name="Total Claim Amount", 
            fill='tozeroy', 
            line=dict(color='#009DAE')),
            secondary_y=True,
    )



    # Set x-axis title
    fig2.update_xaxes(
        title_text="Day of the Month", 
        tickangle=45)  # Rotate x-axis labels to 45 degrees for better readability

    # Set y-axes titles
    fig2.update_yaxes(
        title_text="<b>Number Of Claims</b>", 
        secondary_y=False)
    fig2.update_yaxes(
        title_text="<b>Total Claim Amount</b>", 
        secondary_y=True)

    st.plotly_chart(fig2, use_container_width=True)

    # Expander for Combined Data Table
    with st.expander("Claims Data Table", expanded=False):
        st.dataframe(area_chart.style.background_gradient(cmap='YlOrBr'))

    # Group data by "Start Month Year" and "Client Segment" and calculate the average Total Premium
    yearly_avg_premium = df.groupby(['Month', 'Claim Type'])['Claim Amount'].mean().unstack().fillna(0)

    # Define custom colors
    cols1, cols2 = st.columns(2)

    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]


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
            xaxis_title="Month",
            yaxis_title="Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Monthly Claim Amount by Claim Type per Member</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)

   # Group data by "Intermediary name" and sum the Total Premium
    premium_by_intermediary = df.groupby('Month')['Claim Amount'].mean().reset_index()

    # Calculate the number of sales by "Intermediary name"
    sales_by_intermediary = df.groupby('Month').size().reset_index(name='Number of Claims')

    # Merge the premium and sales data
    merged_data = premium_by_intermediary.merge(sales_by_intermediary, on='Month')


    with cols1:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for Total Premium
        fig_premium_by_intermediary.add_trace(go.Bar(
            x=merged_data['Month'],
            y=merged_data['Claim Amount'],
            text=merged_data['Claim Amount'],
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y',
            marker_color='#009DAE',
            name='Average Claim Amount'
        ))


        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            yaxis=dict(
                title="Average Claim Amount",
                titlefont=dict(color="grey"),
                tickfont=dict(color="grey")
            ),

            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Monthly Claim Amount per Member</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)


   # Create the layout columns
    cls1, cls2 = st.columns(2)

    int_owner = df.groupby("Claim Type")["Claim Amount"].sum().reset_index()
    int_owner.columns = ["Claim Type", "Claim Amount"]    

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Claim Amount by Channel</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Claim Type", values="Claim Amount", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    # Donut chart for PreAuth by Status
    status_counts = df["Claim Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    with cls2:
        st.markdown('<h2 class="custom-subheader">Number of Claims By Status</h2>', unsafe_allow_html=True)    
    # Define custom colors
        custom_colors = ["#006E7F", "#e66c37","#461b09","#f8a785", "#CC3636" ] 

        fig = px.pie(status_counts, names="Status", values="Count", hole=0.5, template = "plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='percent+value')
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))
        st.plotly_chart(fig, use_container_width=True, height = 200)

    cols1, cols2 = st.columns((2))
    # bar chart for PreAuth by Specialisation
    diagnosis_count = df.groupby("Diagnosis").size().reset_index(name='Number of Claims')
    diagnosis_count = diagnosis_count.sort_values(by='Number of Claims', ascending=False)

    top_10_specialisations = diagnosis_count.sort_values(by='Number of Claims', ascending=False).head(15)

    with cols1:
        st.markdown('<h2 class="custom-subheader">Numbers of Claims By Diagnosis</h2>', unsafe_allow_html=True)    
        # Define custom colors
        custom_colors = ["#009DAE"] 
        
        # Create the bar chart with custom colors
        fig = px.bar(top_10_specialisations, x="Diagnosis", y="Number of Claims", template="seaborn",
                    color_discrete_sequence=custom_colors)
        
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400) 
        
        st.plotly_chart(fig, use_container_width=True)

    # bar chart for PreAuth by Specialisation
    diagnosis_count = df.groupby("ICD-10 Code").size().reset_index(name='Number of Claims')
    diagnosis_count = diagnosis_count.sort_values(by='Number of Claims', ascending=False)

    top_10_specialisations = diagnosis_count.sort_values(by='Number of Claims', ascending=False).head(15)

    with cols2:
        st.markdown('<h2 class="custom-subheader">Numbers of Claims By ICD-10 Code</h2>', unsafe_allow_html=True)    
        # Define custom colors
        custom_colors = ["#009DAE"] 
        
        # Create the bar chart with custom colors
        fig = px.bar(top_10_specialisations, x="ICD-10 Code", y="Number of Claims", template="seaborn",
                    color_discrete_sequence=custom_colors)
        
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400) 
        
        st.plotly_chart(fig, use_container_width=True)


    # Get the top 15 employers by Claim Amount
    top_15_employers = df.nlargest(15, 'Claim Amount')

    # Sort the top 15 employers by Claim Amount in descending order
    sorted_df = top_15_employers.sort_values(by='Claim Amount', ascending=False)


    with cols1:

        # Create the bar chart
        fig = go.Figure()

        # Add bars for each employer
        fig.add_trace(go.Bar(
            x=sorted_df['Provider Name'],
            y=sorted_df['Claim Amount'],
            text=[f'{value/1e3:.0f}K' for value in sorted_df['Claim Amount']],
            textposition='auto',
            marker_color="#009DAE"  # Custom color
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
        st.markdown('<h3 class="custom-subheader">Top 15 Service Providers by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    # Group data by "Intermediary name" and sum the Total Premium
    premium_by_intermediary_name = df.groupby('Employer Name')['Claim Amount'].sum().nlargest(15).reset_index()
    # Calculate the number of sales by "Intermediary name"
    sales_by_intermediary = df.groupby('Employer Name').size().reset_index(name='Number of Claims')

    # Merge the premium and sales data
    merged = premium_by_intermediary_name.merge(sales_by_intermediary, on='Employer Name')

   # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls1:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for Total Premium
        fig_premium_by_intermediary.add_trace(go.Bar(
            x=merged['Employer Name'],
            y=merged['Claim Amount'],
            text=merged['Claim Amount'],
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y',
            marker_color='#009DAE',
            name='Claim Amount'
        ))


        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Employer Group",
            yaxis=dict(
                title="Total Claim Amount",
                titlefont=dict(color="#009DAE"),
                tickfont=dict(color="#009DAE")
            ),

            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Employer Groups by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)

    # Group data by "Intermediary name" and sum the Total Premium
    premium_by_intermediary_name = df.groupby('Provider Name')['Claim Amount'].sum().nlargest(15).reset_index()
    # Calculate the number of sales by "Intermediary name"
    sales_by_intermediary = df.groupby('Provider Name').size().reset_index(name='Number of Claims')

    # Merge the premium and sales data
    merged_df = premium_by_intermediary_name.merge(sales_by_intermediary, on='Provider Name')


    with cls2:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for Total Premium
        fig_premium_by_intermediary.add_trace(go.Bar(
            x=merged_df['Provider Name'],
            y=merged_df['Claim Amount'],
            text=merged_df['Claim Amount'],
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y',
            marker_color='#009DAE',
            name='Claim Amount'
        ))


        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Service Provider",
            yaxis=dict(
                title="Total Claim Amount",
                titlefont=dict(color="#009DAE"),
                tickfont=dict(color="#009DAE")
            ),

            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Service Providers by Claim Amount</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)


    cl1, cl2 =st.columns(2)

    with cl1:
        with st.expander("Total Claims by Employer Group"):
            st.dataframe(merged.style.format(precision=2))

    with cl2:
        with st.expander("Total Claims by Service Provider"):
            st.dataframe(merged_df.style.format(precision=2))