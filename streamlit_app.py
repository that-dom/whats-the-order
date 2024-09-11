import random
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import json

# Streamlit app title in the main body
st.title("Team Update Order Generator (Based on Geolocation)")

st.write("### Instructions:")
st.write("""
- Add team members by entering their names and locations in the sidebar.
- You can upload previously saved team data in JSON format via the sidebar.
- After adding team members, click the **Generate Random Update Order** button to display the order based on one of the geographic flows (East to West, West to East, North to South, South to North).
""")

# Initialize the session state for storing team data
if 'team' not in st.session_state:
    st.session_state.team = {}

# Initialize state variables to avoid continuous rerun loops
if 'upload_triggered' not in st.session_state:
    st.session_state.upload_triggered = False

# Initialize the geolocator with a unique user agent
geolocator = Nominatim(user_agent="team_member_sort_order")

def get_coordinates(location, retries=3):
    """Fetch latitude and longitude for a given location using Nominatim, with retry logic."""
    try:
        loc = geolocator.geocode(location, timeout=10)
        if loc:
            return (loc.latitude, loc.longitude)
        else:
            return None
    except GeocoderTimedOut:
        if retries > 0:
            time.sleep(2)  # Wait for 2 seconds before retrying
            return get_coordinates(location, retries - 1)
        else:
            return None

# Function to get East to West order (based on longitude)
def east_to_west_order(team):
    return sorted(team.items(), key=lambda x: x[1][1][1], reverse=True)  # Sort by longitude

# Function to get West to East order (based on longitude, reversed)
def west_to_east_order(team):
    return sorted(team.items(), key=lambda x: x[1][1][1])

# Function to get North to South order (based on latitude)
def north_to_south_order(team):
    return sorted(team.items(), key=lambda x: x[1][1][0], reverse=True)  # Sort by latitude

# Function to get South to North order (based on latitude, reversed)
def south_to_north_order(team):
    return sorted(team.items(), key=lambda x: x[1][1][0])

# Function to display the order
def display_order(order, flow_name):
    st.subheader(f"Selected Flow: {flow_name}")
    st.write("Team update order:")
    for i, (name, coordinates) in enumerate(order, 1):
        st.write(f"{i}. {name} (Latitude: {coordinates[1][0]}, Longitude: {coordinates[1][1]})")

# Sidebar for adding team members and handling file upload/download
st.sidebar.header("Team Management")

# Form for adding team members in the sidebar
with st.sidebar.form(key="team_form"):
    st.write("### Add Team Members")
    name = st.text_input("Enter team member's name", key="name_input")
    location = st.text_input("Enter team member's location (e.g., 'Dayton, OH, USA')", key="location_input")
    add_member = st.form_submit_button("Add Team Member")

    if add_member and name and location:
        coordinates = get_coordinates(location)
        if coordinates:
            st.session_state.team[name] = (location, coordinates)
            st.sidebar.success(f"Added {name} from {location} (Lat: {coordinates[0]}, Lon: {coordinates[1]})")
        else:
            st.sidebar.error(f"Could not find coordinates for '{location}'. Please try again with more details like 'City, State, Country'.")

# Function to download the team data as a JSON file in the sidebar
def download_team_data():
    team_data = json.dumps(st.session_state.team, indent=4)
    st.sidebar.download_button(label="Download Team Data as JSON", 
                               data=team_data, 
                               file_name="team_data.json", 
                               mime="application/json")

# Function to upload a JSON file to load team data
def upload_team_data():
    uploaded_file = st.sidebar.file_uploader("Upload a JSON file", type="json")
    if uploaded_file:
        team_data = json.load(uploaded_file)
        st.session_state.team = {name: tuple(data) for name, data in team_data.items()}
        st.sidebar.success("Team data uploaded successfully!")

# Option to reset the team list in the sidebar
if st.sidebar.button("Reset Team"):
    st.session_state.team.clear()  # Clears all team members
    st.sidebar.success("Team list reset.")
    st.rerun()

# Add functionality for downloading team data in the sidebar
st.sidebar.write("### Save/Load Team Data")
download_team_data()

# Add functionality for uploading team data from a JSON file in the sidebar
upload_team_data()

# Display the list of added team members with city and coordinates in the main body
st.subheader("Current Team Members")
if st.session_state.team:
    for name, (location, coordinates) in st.session_state.team.items():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"- {name} ({location}): Lat: {coordinates[0]}, Lon: {coordinates[1]}")
        with col2:
            if st.button(f"Remove", key=f"remove_{name}"):
                del st.session_state.team[name]
else:
    st.write("No team members added yet.")

# Option to generate random order in the main body
if st.button("Generate Random Update Order"):
    if not st.session_state.team:
        st.error("Please add team members before generating an order.")
    else:
        # Directional flow options
        flows = {
            1: ("East to West", east_to_west_order),
            2: ("West to East", west_to_east_order),
            3: ("North to South", north_to_south_order),
            4: ("South to North", south_to_north_order)
        }

        # Randomly select a flow
        selected_flow = random.choice(list(flows.keys()))
        flow_name, flow_function = flows[selected_flow]

        # Generate the update order
        order = flow_function(st.session_state.team)

        # Display the generated order
        display_order(order, flow_name)
