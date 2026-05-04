# AI was used to troubleshoot the multi-page sidebar navigation, and ensure compatibility with the latest Streamlit and Plotly syntax.

import streamlit as st
import pandas as pd
import plotly.express as px
import requests


st.set_page_config(page_title="NASA Global Event Tracker", layout="wide")


@st.cache_data
def fetch_nasa_events():
    url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        events = []
        for event in data['events']:
            # Extract basic info
            title = event['title']
            category = event['categories'][0]['title']
            # Get latest geometry (coordinates)
            if event['geometry']:
                latest_geo = event['geometry'][0]
                lon = latest_geo['coordinates'][0]
                lat = latest_geo['coordinates'][1]
                date = latest_geo['date']
                events.append({
                    "Title": title,
                    "Category": category,
                    "Lat": lat,
                    "Lon": lon,
                    "Date": date
                })
        return pd.DataFrame(events)
    else:
        st.error("Failed to fetch data from NASA API")
        return pd.DataFrame()


df = fetch_nasa_events()


st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Global Map", "Data Analytics", "Project Information"])


st.sidebar.markdown("---")
st.sidebar.header("Filters")
if not df.empty:
    categories = df['Category'].unique().tolist()
    selected_cats = st.sidebar.multiselect("Select Event Categories", options=categories, default=categories)
    filtered_df = df[df['Category'].isin(selected_cats)]
else:
    filtered_df = df


if page == "Global Map":
    st.title(" NASA Live Event Tracker")
    st.markdown("This map displays real-time environmental events captured by NASA's Earth Observatory.")
    
    if not filtered_df.empty:
        
        fig = px.scatter_map(
            filtered_df, 
            lat="Lat", 
            lon="Lon", 
            hover_name="Title", 
            color="Category", 
            zoom=1,
            height=600
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("No data available for the selected filters.")


elif page == "Data Analytics":
    st.title("Event Distribution & Raw Data")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Events by Category")
        if not filtered_df.empty:
            
            cat_counts = filtered_df['Category'].value_counts().reset_index()
            cat_counts.columns = ['Category', 'Count']
            fig_bar = px.bar(cat_counts, x='Category', y='Count', color='Category', title="Active Event Count")
            st.plotly_chart(fig_bar, width='stretch')
        
    with col2:
        st.subheader("Recent Event Registry")
        
        st.dataframe(filtered_df[['Date', 'Title', 'Category']], height=400)


elif page == "Project Information":
    st.title("About This Project")
    st.markdown("""
    ### Project Narrative
    Our planet is constantly changing. This dashboard utilizes the **NASA EONET (Earth Observatory Natural Event Tracker)** 
    to provide a unified story of current environmental activity. By monitoring everything from wildfires to 
    sea ice changes, we can better understand the frequency and location of major natural occurrences.

    ### Data Source
    - **API:** NASA EONET API v3
    - **Tools:** Streamlit, Plotly, Pandas
    """)
