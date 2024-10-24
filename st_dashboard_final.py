################################################ CITIBIKES DASHBOARD ###########################################################

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
from datetime import datetime as dt
from PIL import Image
from numerize import numerize

############################################ INITIAL SETTINGS FOR THE DASHBOARD ##################################################

st.set_page_config(page_title='CitiBike Strategy Dashboard', layout='wide')
st.title('CitiBike Strategy Dashboard')

### DEFINE SIDE BAR
st.sidebar.title('Aspect Selector')
page = st.sidebar.selectbox(
    'Select an aspect of the analysis',
    ['Intro page',
     'Weather component and bike usage',
     'Most popular stations',
     'Interactive map with aggregated bike trips',
     'Classic versus electric bikes',
     'Recommendations'])

################################################# IMPORT DATA #####################################################################

df = pd.read_csv('nyciti_subset.csv')

############################################ DEFINE THE PAGES #####################################################################

### INTRO PAGE

if page == 'Intro page':
    st.markdown('This dashboard aims to provide helpful insights on the expansion problems NY CitiBikes currently faces...')
    st.markdown('#### Overall Approach:')
    st.markdown('1. Define Objective')
    st.markdown('2. Source Data')
    st.markdown('3. Geospatial Plot')
    st.markdown('4. Interactive Visualizations')
    st.markdown('5. Dashboard Creation')
    st.markdown('6. Findings and Recommendations')
    st.markdown('#### Dashboard Sections:')
    st.markdown('- Weather component and bike usage')
    st.markdown('- Most popular stations')
    st.markdown('- Interactive map with aggregated bike trips')
    st.markdown('- Classic versus electric bikes')
    st.markdown('- Recommendations')

    # Open and display the image properly aligned with the block
    myImage = Image.open("Citi_bike_cycles.jpg")  # source: https://nycdotbikeshare.info/news_events_page
    st.image(myImage)

### LINE CHART PAGE: WEATHER COMPONENT AND BIKE USAGE

elif page == 'Weather component and bike usage':

    # Aggregate the data by datetime
    df_aggregated = df.groupby('date').agg({
        'bike_rides_daily': 'mean',
        'avgTemp': 'mean'
    }).reset_index()

    # Create the figure
    fig2 = go.Figure()

    # Primary Y-axis (Bike rides)
    fig2.add_trace(
        go.Scatter(
            x=df_aggregated['date'],
            y=df_aggregated['bike_rides_daily'],
            name='Daily Bike Rides',
            yaxis='y1',
            line=dict(color='blue')
        )
    )

    # Secondary Y-axis (Avg Temp)
    fig2.add_trace(
        go.Scatter(
            x=df_aggregated['date'],
            y=df_aggregated['avgTemp'],
            name='Daily Temperature',
            yaxis='y2',
            line=dict(color='red')
        )
    )

    # Customize the chart layout
    fig2.update_layout(
        title='Temperature vs Rides in NYC 2022',
        xaxis_title='Date',
        yaxis=dict(
            title='Daily Total Bike Rides',
            titlefont=dict(color='blue'),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title='Daily Avg Temperature',
            titlefont=dict(color='red'),
            tickfont=dict(color='red'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            x=0,
            y=1.1,
            orientation='h'
        )
    )

    # Show the plot
    st.plotly_chart(fig2, use_container_width=True)

### BAR CHART PAGE: MOST POPULAR STATIONS

elif page == 'Most popular stations':

    # Create the filter on the side bar
    with st.sidebar:
        season_filter = st.multiselect(
            label='Select the season', 
            options=df['season'].unique(),
            default=df['season'].unique()
        )

    df1 = df.query('season == @season_filter')

    # Define the total rides
    total_rides = float(df1['bike_rides_daily'].count())
    st.metric(label='Total Bike Rides', value=numerize.numerize(total_rides))

    # Create the chart
    df1['value'] = 1
    df_groupby_bar = df1.groupby('start_station_name', as_index=False).agg({'value': 'sum'})
    top20 = df_groupby_bar.nlargest(20, 'value')

    fig = go.Figure(
        go.Bar(
            x=top20['start_station_name'],
            y=top20['value'],
            marker={'color': top20['value'], 'colorscale': 'Blues'}
        )
    )

    fig.update_layout(
        title='Top 20 Most Popular Bike Stations in NYC 2022',
        xaxis_title='Start Stations',
        yaxis_title='Sum of Trips',
        width=900, height=600
    )

    st.plotly_chart(fig, use_container_width=True)

### MAP PAGE: INTERACTIVE MAP WITH AGGREGATED BIKE TRIPS

elif page == 'Interactive map with aggregated bike trips':

    path_to_html = "Citi Bike Trips Aggregated.html"

    # Read file and keep in variable
    with open(path_to_html, 'r') as f:
        html_data = f.read()

    # Show in webpage
    st.header('Aggregated Bike Trips in NYC 2022')
    st.components.v1.html(html_data, height=1000)

### HISTOGRAMS: CLASSIC VERSUS ELECTRIC BIKES

elif page == 'Classic versus electric bikes':

    # Filter DataFrame by category
    classic_bike = df[df['rideable_type'] == 'classic_bike']
    electric_bike = df[df['rideable_type'] == 'electric_bike']

    # Create histograms for each category
    hist_data_A = go.Histogram(x=classic_bike['avgTemp'], name='Classic Bike', marker=dict(color='blue'))
    hist_data_B = go.Histogram(x=electric_bike['avgTemp'], name='Electric Bike', marker=dict(color='lightblue'))

    # Create layout
    layout = go.Layout(
        title='Classic vs Electric Bike Rentals by Temperature',
        xaxis=dict(title='Average Temperature'),
        yaxis=dict(title='Frequency'),
        barmode='overlay'
    )

    # Create the figure
    fig3 = go.Figure(data=[hist_data_A, hist_data_B], layout=layout)

    # Display the figure
    st.plotly_chart(fig3)

### CONCLUSIONS PAGE: RECOMMENDATIONS

else:

    st.header('Conclusions and Recommendations')
    bikes = Image.open('Citi_Bike_Rider.jpg')  # https://nycdotbikeshare.info/news_events_page
    st.image(bikes)
    st.markdown('Source: https://nycdotbikeshare.info/news-and-events/citi-bike-launch-nyc')
    st.markdown('### Our analysis has shown that NY CitiBikes should focus on the following objectives moving forward:')
    st.markdown('- There is a clear correlation between temperature and bike trips. I recommend ensuring that stations are fully stocked during the warmer months in order to meet the higher demand, but to provide a lower supply in winter and late autumn to reduce cost.')
    st.markdown('- There is a clear popularity among the stations along the water and around Central Park. I recommend adding bikes and bike parking to these locations.')
    st.markdown('- Classic bikes are rented over 2.5 times more often than electric bikes due to limited electric bike availability. I recommend incorporating more electric bikes into circulation when new bikes are added.')
