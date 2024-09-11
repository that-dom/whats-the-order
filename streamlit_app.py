import random
import streamlit as st

# Streamlit app title
st.title("Team Update Order Generator")

# Session state to store the list of team members
if 'team' not in st.session_state:
    st.session_state.team = {}

# Function to get East to West order
def east_to_west_order(team):
    return sorted(team.items(), key=lambda x: x[1])  # Placeholder sorting by location alphabetically

# Function to get West to East order
def west_to_east_order(team):
    return sorted(team.items(), key=lambda x: x[1], reverse=True)  # Placeholder sorting reverse alphabetically

# Function to get North to South order
def north_to_south_order(team):
    return sorted(team.items(), key=lambda x: len(x[1]))  # Placeholder sorting by length of location name

# Function to get South to North order
def south_to_north_order(team):
    return sorted(team.items(), key=lambda x: len(x[1]), reverse=True)  # Reverse sorting by length of location name

# Function to display the order
def display_order(order, flow_name):
    st.subheader(f"Selected Flow: {flow_name}")
    st.write("Team update order:")
    for i, (name, location) in enumerate(order, 1):
        st.write(f"{i}. {name} ({location})")

# Form for adding team members
with st.form(key="team_form"):
    name = st.text_input("Enter team member's name")
    location = st.text_input("Enter team member's location")
    add_member = st.form_submit_button("Add Team Member")

    if add_member and name and location:
        st.session_state.team[name] = location
        st.success(f"Added {name} from {location}")

# Display the list of added team members
st.subheader("Current Team Members")
if st.session_state.team:
    for name, location in st.session_state.team.items():
        st.write(f"- {name} ({location})")
else:
    st.write("No team members added yet.")

# Button to generate the random order
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

# Option to reset the list
if st.button("Reset Team"):
    st.session_state.team = {}
    st.success("Team list reset.")
