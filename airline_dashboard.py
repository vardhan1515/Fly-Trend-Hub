# Importing libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# Load background image and encode it
if "background_image" not in st.session_state:
    with open("air_line.png", "rb") as img_file:
        st.session_state["background_image"] = base64.b64encode(img_file.read()).decode()

# Link the external CSS
with open("styles.css", "r") as css_file:
    css = css_file.read().replace("{background_image}", st.session_state["background_image"])
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Title and header
st.title("✈️ Airline Data Interactive Dashboard")
st.markdown("### Explore insights from airline data interactively.")

# Loading the data from the database
@st.cache_data
def load_data(db_path="airline_database_111.db"):
    try:
        conn = sqlite3.connect(db_path)
        passenger_df = pd.read_sql("SELECT PassengerID, Age, Gender, Nationality FROM Passenger;", conn)
        flight_df = pd.read_sql("""
            SELECT FlightID, AirportID, FlightStatus, DepartureMonth, DepartureYear
            FROM Flight WHERE DepartureYear = 2022;
        """, conn)
        airport_df = pd.read_sql("SELECT AirportID, AirportName, Continents FROM Airport;", conn)
        passenger_flight_df = pd.read_sql("""
            SELECT PassengerID, COUNT(*) AS FlightsTaken 
            FROM PassengerFlight 
            GROUP BY PassengerID;
        """, conn)
        conn.close()
        return passenger_df, flight_df, airport_df, passenger_flight_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Loading data
passenger_df, flight_df, airport_df, passenger_flight_df = load_data()

# Ensure dataframes are not empty
if passenger_df.empty or flight_df.empty or airport_df.empty or passenger_flight_df.empty:
    st.error("No data available to display. Please check your database.")
    st.stop()

# Merge airport data into flight data
flight_df = flight_df.merge(airport_df, on="AirportID", how="left")

# Merge passenger data with flight counts
passenger_summary = passenger_df.merge(passenger_flight_df, on="PassengerID", how="left").fillna(0)

# Sidebar filters
st.sidebar.header("Filters")
selected_flight_status = st.sidebar.multiselect(
    "Select Flight Status", 
    flight_df['FlightStatus'].unique(),
    default=flight_df['FlightStatus'].unique()
)
selected_age_range = st.sidebar.slider(
    "Select Age Range", 
    int(passenger_summary['Age'].min()),
    int(passenger_summary['Age'].max()), 
    (20, 60)
)
selected_continent = st.sidebar.selectbox(
    "Select Continent (Optional)", 
    options=["All"] + airport_df['Continents'].dropna().unique().tolist(),
    index=0
)
selected_airport_count = st.sidebar.slider("Number of Top Airports", 5, 10, 10)

# Applying filters
if selected_continent != "All":
    flight_df = flight_df[flight_df['Continents'] == selected_continent]

filtered_passenger = passenger_summary[
    (passenger_summary['Age'] >= selected_age_range[0]) & 
    (passenger_summary['Age'] <= selected_age_range[1])
]
filtered_flight = flight_df[flight_df['FlightStatus'].isin(selected_flight_status)]

# Displaying KPIs
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Passengers", len(passenger_summary))
col2.metric("Filtered Passengers", len(filtered_passenger))
col3.metric("Total Flights", len(filtered_flight))
col4.metric("Avg Passenger Age", round(filtered_passenger['Age'].mean(), 1) if not filtered_passenger.empty else 0)

# Delayed and canceled flight percentages
if len(filtered_flight) > 0:
    delayed_percentage = round((len(filtered_flight[filtered_flight['FlightStatus'] == "Delayed"]) / len(filtered_flight)) * 100, 2)
    cancelled_percentage = round((len(filtered_flight[filtered_flight['FlightStatus'] == "Cancelled"]) / len(filtered_flight)) * 100, 2)
else:
    delayed_percentage = 0
    cancelled_percentage = 0
col5, col6 = st.columns(2)
col5.metric("Delayed Flights (%)", f"{delayed_percentage}%")
col6.metric("Cancelled Flights (%)", f"{cancelled_percentage}%")

# Passenger age distribution
st.subheader("📈 Passenger Age Distribution")
if not filtered_passenger.empty:
    age_counts = filtered_passenger['Age'].value_counts().sort_index()
    fig1 = px.line(x=age_counts.index, y=age_counts.values, 
                   labels={"x": "Age", "y": "Number of Passengers"},
                   title="Age Distribution of Passengers")
    st.plotly_chart(fig1)
else:
    st.info("No passengers available in the selected age range.")

# Flight status by top airports
st.subheader("📊 Flight Status by Top Airports")
top_airports_status = (
    filtered_flight.groupby(['AirportName', 'FlightStatus'])
    .size()
    .reset_index(name="Count")
)

# Get the top N airports by total flight count
top_airports_overall = (
    top_airports_status.groupby('AirportName')['Count']
    .sum()
    .nlargest(selected_airport_count)
    .index
)

# Filter the data for top N airports
filtered_top_airports_status = top_airports_status[top_airports_status['AirportName'].isin(top_airports_overall)]

# Create the visualization
if not filtered_top_airports_status.empty:
    fig4 = px.bar(
        filtered_top_airports_status,
        x="AirportName",
        y="Count",
        color="FlightStatus",
        barmode="stack",
        title=f"Flight Status Distribution for Top {selected_airport_count} Airports",
        labels={"AirportName": "Airport", "Count": "Number of Flights"},
    )
    st.plotly_chart(fig4)
else:
    st.info("No data available for the selected filters.")

# Monthly flight trends
st.subheader("📉 Monthly Trends in Flight Departures")
if not filtered_flight.empty:
    monthly_trends = filtered_flight.groupby('DepartureMonth').size().reset_index(name="Count")
    fig5 = px.line(monthly_trends, x="DepartureMonth", y="Count", markers=True,
                   labels={"DepartureMonth": "Month", "Count": "Number of Departures"},
                   title="Monthly Trends in Flight Departures")
    st.plotly_chart(fig5)
else:
    st.info("No monthly flight trends available.")

# Flights by nationality
st.subheader("🌍 Flights Taken by Nationality")
if not passenger_summary.empty:
    flights_by_nationality = passenger_summary.groupby("Nationality")['FlightsTaken'].sum().sort_values(ascending=False).head(10)
    fig6 = px.bar(x=flights_by_nationality.index, y=flights_by_nationality.values, 
                  labels={"x": "Nationality", "y": "Flights Taken"}, title="Flights Taken by Nationality")
    st.plotly_chart(fig6)
else:
    st.info("No flight data by nationality available.")

# Footer
st.markdown("---")
st.markdown("**Dashboard Created by Vardhan Burande** | Powered by Streamlit 🚀")
