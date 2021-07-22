import streamlit as st
import pandas as pd
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import pydeck as pdk
from collections import defaultdict


# call the data and clean it by dropping unnecessary or unusable rows and columns
st.title("Welcome to the city of New York")
def crs():

    cars= pd.read_csv("nyc_veh_crash_sample.csv")
    todrop = ['UNIQUE KEY', 'DATE', 'LOCATION', 'ON STREET NAME', 'CROSS STREET NAME', 'OFF STREET NAME',
              'VEHICLE 3 TYPE', 'VEHICLE 4 TYPE', 'VEHICLE 5 TYPE', 'VEHICLE 1 FACTOR', 'VEHICLE 2 FACTOR',
              'VEHICLE 3 FACTOR', 'VEHICLE 4 FACTOR', 'VEHICLE 5 FACTOR']
    cars.drop(todrop, inplace=  True, axis = 1)
    cars.dropna(subset=['BOROUGH'], inplace=True)
    cars.dropna(subset=['LATITUDE'], inplace=True)
    cars.dropna(subset=['VEHICLE 1 TYPE'], inplace=True)
    return cars

#create dictionary to collect data about cities
crashes = defaultdict(int)
for index, row in crs().iterrows():
    if row['BOROUGH'] not in crashes:
        crashes[row['BOROUGH']] = 1
    else:
        crashes[row['BOROUGH']] +=1

#create a piechart based on cities exploding out most accidents using the data collected
def pie(crashes):
    explode_value = 0.15
    keys = []
    for k, a in crashes.items():
        if a == 0:
            keys.append(k)

    [crashes.pop(key) for key in keys]
#set the location of the explode
    large = max(crashes, key = crashes.get)
    keys = list(crashes.keys())
    values = list(crashes.values())
    place = keys.index(large)
    explode = [0]*len(keys)
    explode[place] = explode_value

# design the colors, font size, location, and title of the piechart
    fig = plt.figure(1, figsize=(10,10))
    ax = fig.add_subplot(111)
    ax.axis('equal')
    colors=('b', 'g', 'r', 'c', 'm', 'y', 'burlywood', 'w')
    plt.pie(values, explode = explode, colors = colors, labels=keys, autopct='%1.2f%%')
    plt.legend(loc = "lower left")
    plt.title("percentage of accidents by city", loc = "center", fontsize = 15, fontfamily = 'monospace', color = 'blue')
    plt.show()
    return plt


# create a map chart using specific latitude and longitude data

city = pd.read_csv("nyc_veh_crash_sample.csv",usecols=['LATITUDE','LONGITUDE'])
city.dropna(subset=['LATITUDE'], inplace=True)

def mapcrash(which = city):
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=40.730610,
            longitude=-73.935242,
            zoom=9.5,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
               'HexagonLayer',
               data=which,
               get_position='[LONGITUDE, LATITUDE]',
               radius=200,
               elevation_scale=4,
               elevation_range=[0, 1000],
               pickable=True,
               extruded=True,
            ),
        ],
    ))

# create a function with select box to show city specific data in the map
def cities():
    st.subheader("choose a map to see car accidents")
    # Add a selectbox :
    delivery = st.selectbox(
        'Maps: ',('Hide maps', 'All cities', 'My city'))

    if delivery == 'Hide maps':
        st.write("choose statistical charts from the side bar")
    elif delivery == 'All cities':
        st.markdown("Car accidents in New York")

        mapcrash()
    else:
        size = st.radio("Select your city: ", (list(crashes.keys())))

        city = pd.read_csv("nyc_veh_crash_sample.csv",usecols=['BOROUGH', 'LATITUDE','LONGITUDE'])
        city.dropna(subset=['LATITUDE'], inplace=True)

        other= city[city['BOROUGH'] == size]
        data = other.drop(columns = 'BOROUGH')
        mapcrash(data)


# function to map out crashes through out the day depending on what time of the day
# the data is divided into morning, afternoon, evening, and midnight
def crashtime():
    hour = {'Morning': 0, 'Afternoon': 0, 'Evening': 0, 'Midnight': 0}
    for index, row in crs().iterrows():
        stamp = datetime.strptime(row['TIME'], "%H:%M")

        if stamp.hour < 6:
            hour['Midnight'] +=1
        elif stamp.hour >= 6 and stamp.hour < 12:
            hour['Morning'] +=1
        elif stamp.hour >= 12 and stamp.hour < 18:
            hour['Afternoon'] +=1
        elif stamp.hour >= 18 and stamp.hour < 24:
            hour['Evening'] +=1

    df = pd.DataFrame.from_dict(hour, orient = 'index', columns = ["Number of accidents"])
    st.title('Crashes during the day')
    st.bar_chart(df)

# function to add buttons to the sidebar
def side():
    citycrash = st.sidebar.button("accidents by city")
    timecrash = st.sidebar.button("accidents by time")
    Vehicle = st.sidebar.button("Vehicles")

    if citycrash:
        st.pyplot(pie(crashes))
    elif timecrash:
        crashtime()
    elif Vehicle:
        vehicles = defaultdict(int)
        damages = defaultdict(int)
        for index, row in crs().iterrows():
            if row['VEHICLE 1 TYPE'] not in vehicles:
                vehicles[row['VEHICLE 1 TYPE']] = 1
                damages[row['VEHICLE 1 TYPE']] = sum(row[5:12])


            else:
                vehicles[row['VEHICLE 1 TYPE']] +=1
                damages[row['VEHICLE 1 TYPE']] += sum(row[6:13])


        st.title("number of accident and injuries by vehicle type")
        def2= pd.DataFrame([damages], index = {"People injured"})
        df = pd.DataFrame([vehicles], index = {"number of accidents"})
        frames = [df, def2]
        result = pd.concat(frames)
        st.table(result)


# main function to call tie up the functions

def main():
    cities()
    side()
main()


