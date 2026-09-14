import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Global Seismic Trends",
    page_icon="🌎",
    layout="wide"
)
# Removing Deploying dropdown at the top right and header styling
st.markdown("""
<style>
/* Hide only the Deploy button */
[data-testid="stAppDeployButton"] {
    display: none;
}

/* Put the dashboard title in the top header area */
[data-testid="stHeader"]::before {
    content: "Global Seismic Trends";
    font-size: 38px;
    font-weight: 600;
    color: #1c83e1;
    position: absolute;
    text-align:center;
    left: 0px;
    right:0px;
    top: 10px; 
}
</style>
""", unsafe_allow_html=True)

# Dashboard title
st.markdown('<h3 style="font-size:36px; text-align:center; font-weight:400;">Analysis of global earthquake data from the past 5 years</h3>', anchors=False, unsafe_allow_html=True)
st.markdown('<p style="font-size:24px; font-weight:400;text-align:center;">🗓️ 2021 Sep to 2026 Sep</p>', unsafe_allow_html=True)

# MySQL connection
connection_url = URL.create(
    "mysql+pymysql",
    username="root",
    password="apple",
    host="localhost",
    port=3306,
    database="global_seismic_trends"
)
engine = create_engine(connection_url)

# Load earthquake data
query = "SELECT * FROM earthquakes"
df = pd.read_sql(query, engine)
#st.dataframe(df.head(10), use_container_width=True)

# Dashboard overview
# Calculate key metrics
total_earthquakes = len(df)
average_magnitude = df["mag"].mean()
maximum_magnitude = df["mag"].max()
tsunami_events = df["tsunami"].sum()
deep_earthquakes = (df["depth_km"] > 300).sum()

# Display metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Earthquakes",
        f"{total_earthquakes:,}",
         border=True
    )

with col2:
    st.metric(
        "Deep Earthquakes",
        f"{deep_earthquakes:,}",
        border=True
    )

with col3:
    st.metric(
        "Tsunami Events",
        f"{tsunami_events:,}",
        border=True
    )

with col4:
    st.metric(
        "Average Magnitude",
        f"{average_magnitude:.2f}",
        border=True
    )

with col5:
    st.metric(
        "Maximum Magnitude",
        f"{maximum_magnitude:.2f}",
        border=True
    )

# -----------------------------------
# Earthquake Trends
# -----------------------------------

col1, col2 = st.columns([3, 1])

# Earthquakes by year
with col1:
    yearly_data = (
        df.groupby("year")
        .size()
        .reset_index(name="earthquake_count")
    )
    fig = px.bar(
        yearly_data,
        x="year",
        y="earthquake_count",
        text="earthquake_count"
    )
    fig.update_traces(
        width=0.5,
        marker_color="#0068c9",
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Earthquakes",
        height=450,
    )
    with st.container(border=True):
        st.markdown('<p style="font-size:26px; font-weight:400;">Yearly Earthquake Trends</p>', unsafe_allow_html=True)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# Tsunami Distribution
with col2:
    tsunami_data = (
        df["tsunami"]
        .map({0: "No Tsunami", 1: "Tsunami"})
        .value_counts()
    )
    fig = px.pie(
        values=tsunami_data.values,
        names=tsunami_data.index,
        hole=0.5,
        color_discrete_sequence=[ "#83C9FF","#FF2B2B"]
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    with st.container(border=True):
        st.markdown('<p style="font-size:26px; font-weight:400;">Tsunami Impact</p>', unsafe_allow_html=True)

        st.plotly_chart(
            fig,
            use_container_width=True
        )
# -----------------------------------
# Magnitude Trend
# -----------------------------------
col1, col2 = st.columns([2, 2])
with col1:
    
    with st.container(border=True):
        st.markdown('<p style="font-size:26px; font-weight:400;">Magnitude Over Time</p>', unsafe_allow_html=True)
        magnitude_data = (
            df.groupby("year")["mag"]
            .mean()
            .reset_index(name="average_magnitude")
        )

        fig = px.line(
            magnitude_data,
            x="year",
            y="average_magnitude",
            markers=True,
            text="average_magnitude"
        )

        fig.update_traces(
            line_color="#0068c9",
            line_width=3,
            marker_size=8,
            texttemplate="%{text:.2f}",
            textposition="top center"
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Average Magnitude",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
# -----------------------------------
# Geographic Analysis
# -----------------------------------
with col2:
    
    with st.container(border=True):
        st.markdown('<p style="font-size:26px; font-weight:400;">Top 5 Earthquake Regions</p>', unsafe_allow_html=True)
        country_data = (
            df["country"]
            .value_counts()
            .head(5)
            .sort_values(ascending=True)
        )

        fig = px.bar(
            country_data,
            x=country_data.values,
            y=country_data.index,
            orientation="h",
            text=country_data.values
        )

        fig.update_traces(
            marker_color="#0068c9",
            width=0.5
        )

        fig.update_layout(
            xaxis_title="Number of Earthquakes",
            yaxis_title="Country",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# -----------------------------------
# SQL Problem Solutions
# -----------------------------------
st.markdown('<p style="font-size:28px; font-weight:400;">Data Analysis</p>', unsafe_allow_html=True)
# Magnitude & Depth
st.markdown('<p style="font-size:26px; font-weight:400;">Magnitude & Depth</p>', unsafe_allow_html=True)
problem = st.selectbox(
    "Choose Problem",
    [
        "Top 10 strongest earthquakes",
        "Top 10 deepest earthquakes",
        "Shallow earthquakes < 50 km and mag > 7.5",
        "Average magnitude per magnitude type"
    ]
)
if st.button("Run Query", key="Magnitude_query"):
    if problem == "Top 10 strongest earthquakes":
        query = """
            SELECT year as Year, mag as Magnitude, country as Country, depth_km as Earthquake_Depth
            FROM earthquakes
            ORDER BY mag DESC
            LIMIT 10;
        """
    elif problem == "Top 10 deepest earthquakes":

        query = """
            SELECT time as Time, depth_km as Earthquake_Depth, country as Country, mag as Magnitude
            FROM earthquakes
            ORDER BY depth_km DESC
            LIMIT 10;
        """
    elif problem == "Shallow earthquakes < 50 km and mag > 7.5":
    
        query = """
            SELECT time as Time, depth_km as Earthquake_Depth, mag as Magnitude, country as Country
            FROM earthquakes
            WHERE depth_km < 50 AND mag > 7.5;
        """
    elif problem == "Average magnitude per magnitude type":
        
        query = """
            SELECT magType as Magnitude_Type, avg(mag) as Average_magnitude
            FROM earthquakes
            GROUP BY magType;
        """
    
    result = pd.read_sql(query, engine)
    st.write("### Results")
    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )
# Time Analysis
st.markdown('<p style="font-size:26px; font-weight:400;">Time Analysis</p>', unsafe_allow_html=True)

problem = st.selectbox(
    "Choose Problem",
    [
        "Year with most earthquakes",
        "Month with highest number of earthquakes",
        "Day of week with most earthquakes",
        "Count of earthquakes per hour of day",
        "Most active reporting network"
    ]
)
if st.button("Run Query", key="Time_query"):
    if problem == "Year with most earthquakes":
        query = """
            SELECT Year as Year, COUNT(*) AS Earthquake_count
            FROM earthquakes
            GROUP BY year
            ORDER BY earthquake_count DESC
            LIMIT 1;
        """
    elif problem == "Month with highest number of earthquakes":
        query = """
            SELECT month as Month, COUNT(*) AS Earthquake_count
            FROM earthquakes
            GROUP BY month
            ORDER BY earthquake_count DESC
            Limit 1;
        """
    elif problem == "Day of week with most earthquakes":  
            query = """
                SELECT day_of_week, COUNT(*) AS earthquake_count
                FROM earthquakes
                GROUP BY day_of_week
                ORDER BY earthquake_count DESC
                LIMIT 1
            """
    elif problem == "Count of earthquakes per hour of day":    
        query = """
             SELECT
                HOUR(time) AS hour_of_day,
                COUNT(*) AS earthquake_count
            FROM earthquakes
            GROUP BY HOUR(time)
            ORDER BY hour_of_day;
        """
    elif problem == "Most active reporting network":    
            query = """
               SELECT net, COUNT(*) AS earthquake_count
                FROM earthquakes
                GROUP BY net
                ORDER BY earthquake_count DESC
                LIMIT 1
            """
    
    result = pd.read_sql(query, engine)
    st.write("### Results")
    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )
# Event Type & Quality Metrics
st.markdown('<p style="font-size:26px; font-weight:400;">Event Type & Quality Metrics</p>', unsafe_allow_html=True)
problem = st.selectbox(
    "Choose Problem",
    [
        "Count of reviewed vs automatic earthquakes",
        "Count by earthquake type",
        "Number of earthquakes by data type",
        "Events with high station coverage"
    ]
)
if st.button("Run Query", key="Quality_query"):
    if problem == "Count of reviewed vs automatic earthquakes":
        query = """
            SELECT status as Status, COUNT(*) AS Earthquake_count
            FROM earthquakes
            GROUP BY status
        """
    elif problem == "Count by earthquake type":
                
        query = """
            SELECT type as Event_Type, COUNT(*) AS Earthquake_count
            FROM earthquakes
            GROUP BY type
        """
    elif problem == "Number of earthquakes by data type":
                    
        query = """
            SELECT types as Types, COUNT(*) AS Earthquake_count
            FROM earthquakes
            GROUP BY types
        """
    elif problem == "Events with high station coverage":
                        
        query = """
            SELECT time as Time, country as Country, mag as Magnitude, nst as No_of_Seismic_Stations
            FROM earthquakes
            WHERE nst > 100
            ORDER BY nst DESC;
        """
    
    result = pd.read_sql(query, engine)
    st.write("### Results")
    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )
# Tsunamis & Alerts
st.markdown('<p style="font-size:26px; font-weight:400;">Tsunamis & Alerts</p>', unsafe_allow_html=True)
problem = st.selectbox(
    "Choose Problem",
    [
        "Number of tsunamis triggered per year",
        "Count earthquakes by alert levels"
    ]
)
if st.button("Run Query", key="tsunami_query"):
    if problem == "Number of tsunamis triggered per year":
        query = """
            SELECT year as Year, COUNT(*) AS No_of_Tsunamis
            FROM earthquakes WHERE tsunami = 1
            GROUP BY year
        """
    elif problem == "Count earthquakes by alert levels":
                
        query = """
            SELECT alert as Alert_Levels, COUNT(*) AS Count_of_Earthquakes
            FROM earthquakes
            GROUP BY alert
            ORDER BY alert
        """
    result = pd.read_sql(query, engine)
    st.write("### Results")
    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )
#Seismic Pattern & Trends Analysis.
st.markdown('<p style="font-size:26px; font-weight:400;">Seismic Pattern & Trends Analysis</p>', unsafe_allow_html=True)
problem = st.selectbox(
    "Choose Problem",
    [
        "Top 5 Countries by Avg Magnitude",
        "Countries with Shallow & Deep Quakes",
        "Year-over-Year Earthquake Growth",
        "Top 3 Seismically Active Regions"
    ]
)
if st.button("Run Query", key="Pattern_query"):
    if problem == "Top 5 Countries by Avg Magnitude":
        query = """
            SELECT country as Country, AVG(mag) AS Avg_magnitude
            FROM earthquakes
            GROUP BY country
            ORDER BY avg_magnitude DESC
            LIMIT 5;
        """
    elif problem == "Countries with Shallow & Deep Quakes":
                
        query = """
            SELECT country as Country, month as Month
            FROM earthquakes
            WHERE country IS NOT NULL
            GROUP BY country, month
            HAVING COUNT(DISTINCT depth_category) = 2
            LIMIT 20;
        """
    elif problem == "Year-over-Year Earthquake Growth":
                    
        query = """
            WITH yearly_counts AS (
                SELECT year, COUNT(*) AS Earthquake_count
                FROM earthquakes
                GROUP BY year
            )
    
            SELECT year as Year, Earthquake_count,
                LAG(Earthquake_count) OVER (ORDER BY year) AS Previous_year_count,
                ROUND(
                    (Earthquake_count - LAG(Earthquake_count) OVER (ORDER BY year))
                    / LAG(Earthquake_count) OVER (ORDER BY year) * 100,
                    2
                ) AS Yoy_growth_rate
            FROM yearly_counts
            ORDER BY year;
        """
    elif problem == "Top 3 Seismically Active Regions":
                        
        query = """
            SELECT country as Country, COUNT(*) AS Earthquake_count, ROUND(AVG(mag),2) AS Avg_magnitude
            FROM earthquakes
            GROUP BY country
            ORDER BY Earthquake_count DESC, Avg_magnitude DESC
            LIMIT 3;
        """
    
    result = pd.read_sql(query, engine)
    st.write("### Results")
    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )
#Depth, Location & Distance-Based  Analysis
st.markdown('<p style="font-size:26px; font-weight:400;">Depth, Location & Distance-Based  Analysis</p>', unsafe_allow_html=True)
problem = st.selectbox(
    "Choose Problem",
    [
        "Avg Depth Within ±5° Latitude",
        "Highest Shallow-to-Deep Ratio",
        "Tsunami vs Non-Tsunami Magnitude",
        "Lowest Data Reliability",
        "Top Deep-Focus Regions"
    ]
)
if st.button("Run Query", key="Location_query"):
    if problem == "Avg Depth Within ±5° Latitude":
        query = """
            SELECT country as Country, ROUND(AVG(depth_km),2) AS Average_depth
            FROM earthquakes
            WHERE latitude BETWEEN -5 and +5
            GROUP BY country  
        """
    elif problem == "Highest Shallow-to-Deep Ratio":
                
        query = """
            SELECT  country as Country,
            SUM(CASE WHEN depth_category = 'shallow' THEN 1 ELSE 0 END) AS Shallow_count,
            SUM(CASE WHEN depth_category = 'deep' THEN 1 ELSE 0 END) AS Deep_count,
            ROUND(
                SUM(CASE WHEN depth_category = 'shallow' THEN 1 ELSE 0 END)
                /
                NULLIF(SUM(CASE WHEN depth_category = 'deep' THEN 1 ELSE 0 END), 0),
                2
            ) AS Shallow_to_deep_ratio
            FROM earthquakes
            WHERE country IS NOT NULL
            GROUP BY country
            HAVING Deep_count > 0
            ORDER BY shallow_to_deep_ratio DESC
            LIMIT 20;
        """
    elif problem == "Tsunami vs Non-Tsunami Magnitude":
                    
        query = """
            SELECT
            ROUND(AVG(CASE WHEN tsunami = 1 THEN mag END), 2) AS Avg_mag_with_tsunami,
            ROUND(AVG(CASE WHEN tsunami = 0 THEN mag END), 2) AS Avg_mag_without_tsunami,
            ROUND(
                AVG(CASE WHEN tsunami = 1 THEN mag END) -
                AVG(CASE WHEN tsunami = 0 THEN mag END),
                2
            ) AS Average_magnitude_difference
            FROM earthquakes;
        """
    elif problem == "Lowest Data Reliability":  
        query = """
            SELECT country as Country, mag as Magnitude, depth_km as Earthquake_Depth, gap, rms,
            ROUND((gap + rms) / 2, 2) AS Average_error_margin
            FROM earthquakes
            WHERE gap IS NOT NULL
              AND rms IS NOT NULL
            ORDER BY Average_error_margin DESC
            LIMIT 10;
        """
    elif problem == "Top Deep-Focus Regions":  
            query = """
                SELECT country as Country, COUNT(*) AS Deep_focus_earthquakes
                FROM earthquakes
                WHERE depth_km > 300
                AND country IS NOT NULL
                GROUP BY country
                ORDER BY Deep_focus_earthquakes DESC
                LIMIT 10;
            """
    
    result = pd.read_sql(query, engine)
    st.write("### Results")
    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )
