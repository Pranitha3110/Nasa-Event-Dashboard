import streamlit as st
import pandas as pd
import requests
import plotly.express as px


# This dashboard was developed with assistance from Gemini. 
# AI was used to structure the  multi-page navigation logic.

def get_nasa_data():
    url = "https://eonet.gsfc.nasa.gov/api/v2.1/events?source=InciWeb,EO"
    try:
        response = requests.get(url)
        data = response.json()
        events = []
        for e in data['events']:
            events.append({
                "Title": e['title'],
                "Category": e['categories'][0]['title'],
                "Lat": e['geometries'][0]['coordinates'][1],
                "Lon": e['geometries'][0]['coordinates'][0],
            })
        return pd.DataFrame(events)
    except Exception as e:
        st.error(f"Error fetching live data: {e}")
        return pd.DataFrame()


st.set_page_config(page_title="NASA Event Tracker", layout="wide")
df = get_nasa_data()


page = st.sidebar.radio("Navigation", ["Global Map", "Data Analytics"])

if page == "Global Map":
    st.title("NASA Live Event Map")
    
    categories = df['Category'].unique().tolist()
    selected_cat = st.multiselect("Filter by Event Type", categories, default=categories)
    filtered_df = df[df['Category'].isin(selected_cat)]
    
    
    fig = px.scatter_map(
        filtered_df, 
        lat="Lat", 
        lon="Lon", 
        hover_name="Title", 
        color="Category", 
        zoom=1
    )
    fig.update_layout(map_style="open-street-map", height=600)
    
    
    st.plotly_chart(fig, width='stretch')

else:
    st.title("Event Analytics")
    
    
    if not df.empty:
        counts = df['Category'].value_counts().reset_index()
        fig_bar = px.bar(counts, x='Category', y='count', title="Current Events by Category")
        st.plotly_chart(fig_bar, width='stretch')
        
        
        st.subheader("Event Registry")
        st.dataframe(df, width='stretch')
    else:
        st.write("No data available to analyze.")