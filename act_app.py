import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pydeck as pdk
import plotly.express as px
#pip install plotly

st.title("Exploratory Data Analysis on ACT Scores")
st.sidebar.title("EDA on ACT Scores")
st.sidebar.subheader("By [Meral Balik](https://github.com/Meralbalik)")
st.sidebar.markdown("[![View on GitHub](https://img.shields.io/badge/GitHub-View_on_GitHub-blue?logo=GitHub)](https://github.com/Meralbalik/ACTstreamlit)")
st.markdown("This application is a Streamlit dashboard that visualizes exploratory analysis on ACT scores of high schools in CA. The ACT test is designed to assess high school students' general educational development and their ability to complete college-level work. ACT test covers four subject areas: English, mathematics, reading, and science. Each subject area test receives a score ranging from 1 to 36. ")
st.sidebar.markdown("This application is a Streamlit dashboard that visualizes exploratory analysis on ACT scores of high schools in CA.")

@st.cache(persist=True)
def load_data():
    data = pd.read_csv('data.csv')
    data.rename({'Dname': 'District', 'Cname': 'County', 'Lat': 'lat', 'Lon':'lon'}, axis=1, inplace=True)
    data['AvgScr'] = data.loc[: , 'AvgScrEng':'AvgScrSci'].mean(axis=1)
    return data

data = load_data()

if st.sidebar.checkbox("Show Raw Data", False):
    st.sidebar.text('Showing the first 10 rows of the data.')
    st.subheader('Raw Data')
    st.write(data.head(10))
#------------------------------------------------------------------------------------------------------------------

# Histogram of the scores
st.subheader("Distribution of the Scores in Five Years")
st.text("Select a school year and a test subject from the dropdown menu on the left.")
st.sidebar.subheader("Distribution of the Scores in Five Years")
select = st.sidebar.selectbox("Select a School Year", ['2013-14', '2014-15','2015-16','2016-17','2017-18'], key="1")
choice = st.sidebar.selectbox("Visualization Type", ['Histogram', 'Pie Chart'], key="2")
filtered = data[['Year','Sname', 'AvgScr']]

# Histogram
def histogram(year):
    hist = np.histogram(filtered[filtered.Year==year]['AvgScr'], bins=36, range=(0,36))[0]
    chart_data = pd.DataFrame({'scores': range(0,36),'number of schools': hist})
    fig = px.bar(chart_data, x='scores', y='number of schools', hover_data = ['scores', 'number of schools'], height=400, width= 780)
    return st.write(fig)

def piechart(year):
    df = filtered[filtered.Year == year]
    percentiles = np.array([0,2.5,25,50,75,97.5,100])
    perct = np.percentile(df['AvgScr'],percentiles)
    labels = {i: f'{percentiles[i]}% to {percentiles[i+1]}%' for i in range(0, 6)}
    score_range = {i: f'{perct[i]} to {perct[i+1]}' for i in range(0, 6)}
    df['Bin'] = pd.cut(df['AvgScr'], perct, labels=False)
    a = df.groupby('Bin')['Sname'].count()
    a = pd.DataFrame({"Score Range":a.index, "# of Schools":a.values.flatten()})
    a['Score Range'] = a["Score Range"].map(score_range)
    fig = px.pie(a, values="# of Schools", names="Score Range",height=400, width= 800)
    return st.write(fig)

def select_year(function):
    if select == '2013-14':
        function(2014)
    if select == '2014-15':
        function(2015)
    if select == '2015-16':
        function(2016)
    if select == '2016-17':
        function(2017)
    if select == '2017-18':
        function(2018)

if choice == 'Pie Chart':
    select_year(piechart)

if choice == 'Histogram':
    select_year(histogram)

#------------------------------------------------------------------------------------------------------------------

# Breakdown scores by subject
st.subheader("Breakdown Scores by Subject")
st.text("Select a school year and a test subject from the dropdown menu on the left.")
st.sidebar.subheader("Breakdown Scores by Subject")
select = st.sidebar.selectbox("Select a School Year", ['2013-14', '2014-15','2015-16','2016-17','2017-18'], key="3")
filtered = data[['Year','AvgScrEng','AvgScrRead', 'AvgScrMath', 'AvgScrSci']]
subject = ['AvgScrEng','AvgScrRead', 'AvgScrMath', 'AvgScrSci']
choice = st.sidebar.multiselect("Pick Subject(s)", subject, default=["AvgScrEng"])


def subjects(year):
   df = filtered[filtered.Year == year]
   df = df[['AvgScrEng','AvgScrRead', 'AvgScrMath', 'AvgScrSci']]
   if len(choice) > 0:
       chosen_data = df[choice]
       fig = px.histogram(chosen_data, height=400, width= 800)
       st.write(fig)

select_year(subjects)

#--------------------------------------------------------------------------------------------
# Map
st.subheader("Where are the schools located based on their scores?")
st.text("Select a score range from the slider on the left.")
st.sidebar.subheader("Where are the schools located based on their scores?")
scores = st.sidebar.slider("Select a score range", 14, 31, [20,25], key='1')
st.write(f"Showing the average ACT scores in the range {scores[0], scores[1]}.")
map_data = data.groupby('gsId')['AvgScr'].mean().reset_index()
map_data = map_data.merge(data[['gsId', 'lat','lon']], on='gsId', how='left').drop_duplicates()
st.map(map_data.query("@scores[0] <= AvgScr <= @scores[1]")[['lat','lon']].dropna(how="any"))

#------------------------------------------------------------------------------------------------------------------
# 3D Map
st.subheader("Number of schools at each location?")
st.text("Select a score range from the slider on the left.")
st.sidebar.subheader("Number of schools at each location?")
scores = st.sidebar.slider("Select a score range", 14, 31, [20,25], key='2')
st.write(f"Showing the average ACT scores in the range {scores[0], scores[1]}.")
new_data = map_data[(map_data.AvgScr >= scores[0]) & (map_data.AvgScr <= scores[1])]
new_data = new_data[['lat', 'lon']]

layer = pdk.Layer("HexagonLayer", new_data, get_position="[lon, lat]", auto_highlight=True, elevation_scale=50,
radius=3000, pickable=True, elevation_range=[0, 3000], extruded=True, coverage=1,)

# Set the viewport location
view_state = pdk.ViewState(longitude=-119.417931, latitude=36.778259, zoom=5.5, min_zoom=5, max_zoom=15,
pitch=40.5, bearing=-27.36)

# Combined all of it and render a viewport
map_3d = pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",  layers=[layer], initial_view_state=view_state,
    tooltip={"html": "<b>Elevation Value:</b> {elevationValue}", "style": {"color": "white"}})
st.write(map_3d)
#------------------------------------------------------------------------------------------------------------------
