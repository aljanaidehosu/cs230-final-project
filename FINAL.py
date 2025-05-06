
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import requests
from shapely.geometry import shape, MultiPolygon
import json

# import seaborn as sns


st.title("The Housing Market of New York")
st.header("Provides You With Essential Information !")
df = pd.read_csv('NY-House-Dataset.csv')

data = {}

all_rows=df
data['No Selection'] = all_rows

#[DA1] Clean or manipulate data and [DA4] Filter data by one condition
manhattan_rows = df[df['STATE'].apply(lambda x: '100' in x[-5:-2])]
data['Manhattan'] = manhattan_rows

brooklyn_rows = df[df['STATE'].apply(lambda x: '112' in x[-5:-2])]
data['Brooklyn'] = brooklyn_rows

queens_rows = df[df['STATE'].apply(lambda x: '110' in x[-5:-2] or '111' in x[-5:-2] or '113' in x[-5:-2] or
                 '114' in x[-5:-2] or '115' in x[-5:-2])]
data['Queens'] = queens_rows

bronx_rows = df[df['STATE'].apply(lambda x: '104' in x[-5:-2])]
data['Bronx'] = bronx_rows

staten_island_rows = df[df['STATE'].apply(lambda x: '103' in x)]
data['Staten Island'] = staten_island_rows
#[DA1] Clean or manipulate data and [DA4] Filter data by one condition

# map New York [SE1]
#[DA9] Add a new column or perform calculations on DataFrame columns
df["log_price"] = np.log(df["PRICE"].clip(lower=1))
# end [DA9] Add a new column or perform calculations on DataFrame columns
min_log = df["log_price"].min()
max_log = df["log_price"].max()
df["color_intensity"] = ((df["log_price"] - min_log) / (max_log - min_log) * 255).astype(int)
#[DA7] Add/drop/select/create new/group columns
df["color_red"] = df["color_intensity"]
df["color_green"] = 255 - df["color_intensity"]
# end [DA7] Add/drop/select/create new/group columns
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[LONGITUDE, LATITUDE]',
    get_color='[color_red, color_green, 0, 160]',  # color changes with price
    get_radius=25,
    pickable=True,
    tooltip=True
)

view_state = pdk.ViewState(
    latitude=40.7826,
    longitude=-73.9656,
    zoom=12,
    pitch=0
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{ADDRESS}\nPrice: {PRICE}$"}
)

st.pydeck_chart(r)
# end map New York [SE1] and [ST4]
#[PY4] A dictionary where you write code to access its keys, values, or items
Data_Visualizations_Options = st.sidebar.selectbox(
    "Wanted Data Visulizations",

    ["None", "Map Filtered By Square Footage","NYC Borough Boundaries Map","Price Correlation by Property Feature"])

if Data_Visualizations_Options == "Map Filtered By Square Footage":
 st.header("Map Filtered By Square Footage")

    # Folium map [FOLIUM 1]
 m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

 min_price = st.number_input("Enter minimum square footage", min_value=0, value=100)
 max_price = st.number_input("Enter maximum square footage", min_value=0, value=500)

 if min_price > max_price:
     st.error("Your minimum value exceeds your maximum value")
 filtered_df = df[(df['PROPERTYSQFT'] >= min_price) & (df['PROPERTYSQFT'] <= max_price)]
 for idx, row in filtered_df.iterrows():
     folium.Marker(
         location=[row['LATITUDE'], row['LONGITUDE']],
         popup=f"{row['ADDRESS']}: {row['PRICE']}",
         tooltip=row['ADDRESS'],
         icon=folium.Icon(color="blue", icon="info-sign")
     ).add_to(m)
 st_data = st_folium(m, width=700, height=500)
# end of folium map [FOLIUM 1]
elif Data_Visualizations_Options == "NYC Borough Boundaries Map":
 st.header("NYC Borough Boundaries Map")
# [FOLIUM 2]
 geojson_url = "https://data.cityofnewyork.us/resource/gthc-hcne.json" # using external API to get our data
 borough_geo = requests.get(geojson_url).json()

 nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

 color_map = {
     "Manhattan": "blue",
     "Brooklyn": "green",
     "Staten Island": "yellow",
     "Bronx": "black",
     "Queens": "purple",
 }

 for borough in borough_geo:
    borough_name = borough['boroname']
    folium.GeoJson(
        borough["the_geom"],
        name=borough_name,
        tooltip=borough_name,
        style_function=lambda x, name=borough_name: {
            'fillColor': 'none',
            'color': color_map.get(name),
            'weight': 3
        }
    ).add_to(nyc_map)

# Add a layer control and display
 folium.LayerControl().add_to(nyc_map)
 st_data = st_folium(nyc_map, width=700, height=500)
# [FOLIUM 2]
elif Data_Visualizations_Options == "Price Correlation by Property Feature":
 st.header("Price Correlation by Property Feature")

    # Correlation chart + scatterplot
 st.title("Scatter Plot with Linear Regression")
 select_columns = ["BEDS", "BATH", "PROPERTYSQFT"]

 x_col = st.selectbox("Select X-axis", [col for col in select_columns if col in df.columns])
 y_col = "log_price"

# Plotting
 fig, ax = plt.subplots()
 sns.regplot(data=df, x=x_col, y=y_col, ax=ax)
 ax.set_title(f'{y_col} vs {x_col} with Linear Regression Line')

 st.pyplot(fig)
# end of scatterplot

borough= st.selectbox("Select a Borough",list(data.keys()))
# end [PY4] A dictionary where you write code to access its keys, values, or items
#Code for fixed usage of.keys function is based on code from ChatGPT. See 1st section of accompanying document.

borough_rows=(data[borough])
#[PY1] A function with two or more parameters and [PY2] A function that returns more than one value
def get_pricerange(borough_rows,level):
 q1=borough_rows['PRICE'].quantile(1/3)
 q2=borough_rows['PRICE'].quantile(2/3)
 # Code for how to find quantiles is based on code from ChatGPT. See 2nd section of accompanying document.

 if level=='Low':
     return borough_rows['PRICE'].min(),q1
 elif level=='Medium':
     return q1,q2
 elif level=='High':
     return q2,borough_rows['PRICE'].max()
 else:
     return borough_rows['PRICE'].min(),borough_rows['PRICE'].max()

#[PY3] Lists and [ST1]
Select_Price_Level= st.selectbox("Select Your Price Level: ",['All','Low', 'Medium', 'High'])
# end [PY3] Lists and [ST1]

min_price,max_price= get_pricerange(borough_rows,Select_Price_Level)
# end [PY1] A function with two or more parameters and [PY2] A function that returns more than one value

st.write("Enter a Custom Range")

selected_min=int(min_price)
selected_max=int(max_price)


default_min=min_price
default_max=max_price

#[ST2] Numeric input widget
custom_min=st.number_input("Minimum Price: ",value=default_min)
custom_max=st.number_input("Maximum Price: ",value=default_max)
#End [ST2] Numeric input widget

if custom_min !=default_min or custom_max !=default_max:
    if custom_min>=custom_max:
        st.write("Error: Minimum Price Must Be Smaller Than Maximum")
    elif int(custom_min)<int(min_price) or int(custom_max)>int(max_price):
        st.write(f"Error: Range must be between {round(min_price,2)} - {round(max_price,2)}")
    else:
        selected_min,selected_max=int(custom_min),int(custom_max)

#[ST3] Slider
price_range = st.slider("Select Price Range", int(min_price), int(max_price), (int(selected_min),int(selected_max)))
# end [ST3] Slider
#[EXTRA] [DA5] Filter data by two or more conditions with AND or OR and [EXTRA] [DA2] Sort data in ascending or descending order, by one or more columns,
filtered_data=borough_rows[(borough_rows['PRICE'] >= price_range[0]) & (borough_rows['PRICE'] <= price_range[1])].sort_values(by='PRICE', ascending=True)
#end [EXTRA] [DA5] Filter data by two or more conditions with AND or OR and [EXTRA] [DA2] Sort data in ascending or descending order, by one or more columns,

#Code for fixed  filtered data  based on code from ChatGPT. See 3rd section of accompanying document.
#Code for sorting chart based on code from ChatGPT. See 4th section of accompanying document.

st.dataframe(filtered_data)
# Sidebar chart selection

# [ST4] Customized page design features (sidebar) to choose the visualization
chart_option = st.sidebar.selectbox(
    "📊 Choose a chart to display:",
    ["None","Housing Type Distribution", "Average Price per SqFt", "Average Beds & Baths"]
)
# end [ST4] Customized page design features (sidebar) to choose the visualization

# [CHART1] PIE CHART - Housing Type Distribution with grouped "Other" category
if chart_option == "Housing Type Distribution":
    if 'TYPE' in filtered_data.columns:
        # Count housing types
        type_counts = filtered_data['TYPE'].value_counts()
        total = type_counts.sum()
        threshold = 0.03 * total

        major_types = type_counts[type_counts >= threshold]
        minor_types = type_counts[type_counts < threshold]

        # Group "Other" types
        grouped_counts = major_types.copy()
        if not minor_types.empty:
            grouped_counts['Other'] = minor_types.sum()

        legend_labels = grouped_counts.index.tolist()
        if 'Other' in grouped_counts:
            other_details = ", ".join(minor_types.index.tolist())
            legend_labels = [
                label if label != 'Other' else f"Other ({other_details})"
                for label in legend_labels
            ]
# end [CHART1] PIE CHART - Housing Type Distribution with grouped "Other" category

        fig1, ax1 = plt.subplots()
        ax1.pie(grouped_counts, labels=grouped_counts.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        plt.legend(legend_labels, title="Housing Types", bbox_to_anchor=(1, 1))

        st.subheader("🏘️ Housing Type Distribution")
        st.pyplot(fig1)
    else:
        st.warning("No 'TYPE' column found in the dataset.")



# [CHART2] BAR CHART - Avg Price per SqFt by Square Footage Range
elif chart_option == "Average Price per SqFt":
    if 'PROPERTYSQFT' in filtered_data.columns:
        filtered_data['PROPERTYSQFT'] = pd.to_numeric(filtered_data['PROPERTYSQFT'], errors='coerce')
        filtered_data['PROPERTYSQFT'] = filtered_data['PROPERTYSQFT'].replace(0, np.nan)
        filtered_data = filtered_data.dropna(subset=['PRICE', 'PROPERTYSQFT'])
        filtered_data['PRICE_PER_SQFT'] = filtered_data['PRICE'] / filtered_data['PROPERTYSQFT']

        bins = [0, 1000, 2000, 3000, 5000, 10000, float('inf')]
        labels = ['0–1000', '1001–2000', '2001–3000', '3001–5000', '5001–10000', '10000+']
        filtered_data['SQFT_RANGE'] = pd.cut(filtered_data['PROPERTYSQFT'], bins=bins, labels=labels)
        avg_prices = filtered_data.groupby('SQFT_RANGE')['PRICE_PER_SQFT'].mean().dropna()
        st.subheader("💲 Average Price per SqFt by Square Footage")
        st.bar_chart(avg_prices)
    else:
        st.warning("No 'PROPERTYSQFT' column found in the dataset.")
# end [CHART2] BAR CHART - Avg Price per SqFt by Square Footage Range


# BAR CHART - Average Beds and Baths
elif chart_option == "Average Beds & Baths":
    avg_beds = filtered_data['BEDS'].mean() if 'BEDS' in filtered_data.columns else 0
    avg_baths = filtered_data['BATH'].mean() if 'BATH' in filtered_data.columns else 0
    st.subheader("🛏️ Average Beds and Baths")

    fig4, ax4 = plt.subplots()
    ax4.bar(['Beds', 'Baths'], [avg_beds, avg_baths], color=['skyblue', 'lightcoral'], width=0.4)
    ax4.set_ylabel('Average Count')
    ax4.set_ylim(0, max(avg_beds, avg_baths) + 1)
    st.pyplot(fig4)

Most_Expensive_Listing = st.sidebar.selectbox(
    "Display Most Expensive Listings",

    ["No", "Yes"])
#[EXTRA][DA3] Find Top largest or smallest values of a column

if Most_Expensive_Listing=="Yes":
 top5 = filtered_data.sort_values(by='PRICE', ascending=False).head(5)
 st.write("Top 5 Most Expensive Listings:")
 st.dataframe(top5)

 # end [EXTRA] [DA3] Find Top largest or smallest values of a column
#Code for fixed usage of.keys function is based on code from ChatGPT. See 5th section of accompanying document.
