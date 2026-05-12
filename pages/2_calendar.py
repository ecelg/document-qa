import streamlit as st
import pandas as pd
import requests
from io import StringIO # Don't forget this import!
from streamlit_calendar import calendar
import holidays

# Function to wipe session data
def clear_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# uploaded credential
uploaded_file = st.sidebar.file_uploader("Upload credentials.txt", type=["txt"])
if uploaded_file and 'creds' not in st.session_state:
    content = uploaded_file.read().decode("utf-8")
    creds = {}
    for line in content.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip()
    st.session_state['creds'] = creds
    st.success("Credentials stored in session!")

# load data
if 'creds' in st.session_state:
    if st.button("Login"):
        c = st.session_state['creds']
        baseurl=str(c.get('str'))
        token=str(c.get('token'))
        URL = f"http://{baseurl}/csp/myrest/flight/all"
        AUTH_HEADER = f"Basic {token}" # Replace with your actual encoded credentials
        try:
            headers = {
                'Authorization': AUTH_HEADER
            }
            response = requests.get(URL, headers=headers)
            # Check if request was successful
            if response.status_code == 200:
                # Display result in a large text area
                #st.success(f"Success! Status Code: {response.status_code}")
                # 2. Create the DataFrame
                raw_text = response.text
                # FIX: Wrap the text in StringIO so pandas doesn't think it's a filename
                df = pd.read_csv(StringIO(raw_text))
                df['departure'] = pd.to_datetime(df['departure'])
                df['arrival'] = pd.to_datetime(df['arrival'])
                st.session_state['bdf']=df
            else:
                st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")

        URL = f"http://{baseurl}/csp/myrest/flight/ww/all"
        AUTH_HEADER = f"Basic {token}" # Replace with your actual encoded credentials
        try:
            headers = {
                'Authorization': AUTH_HEADER
            }
            response = requests.get(URL, headers=headers)
            # Check if request was successful
            if response.status_code == 200:
                # Display result in a large text area
                #st.success(f"Success! Status Code: {response.status_code}")
                #st.text_area("Response Result:", value=response.text, height=400)
                # 2. Create the DataFrame
                raw_text = response.text
                # FIX: Wrap the text in StringIO so pandas doesn't think it's a filename
                df = pd.read_csv(StringIO(raw_text))
                df['departure'] = pd.to_datetime(df['departure'])
                df['arrival'] = pd.to_datetime(df['arrival'])
                st.session_state['bdf_ww']=df
            else:
                st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
        
        URL = f"http://{baseurl}/csp/myrest/events/filter?type=ISC"
        AUTH_HEADER = f"Basic {token}" # Replace with your actual encoded credentials
        try:
            headers = {
                'Authorization': AUTH_HEADER
            }
            response = requests.get(URL, headers=headers)
            # Check if request was successful
            if response.status_code == 200:
                # Display result in a large text area
                #st.success(f"Success! Status Code: {response.status_code}")
                #st.text_area("Response Result:", value=response.text, height=400)
                # 2. Create the DataFrame
                raw_text = response.text
                # FIX: Wrap the text in StringIO so pandas doesn't think it's a filename
                df = pd.read_csv(StringIO(raw_text))
                df['starttime'] = pd.to_datetime(df['starttime'])
                df['endtime'] = pd.to_datetime(df['endtime'])
                st.session_state['edf_isc']=df
            else:
                st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
        URL = f"http://{baseurl}/csp/myrest/events/filter?type=Run"
        AUTH_HEADER = f"Basic {token}" # Replace with your actual encoded credentials
        try:
            headers = {
                'Authorization': AUTH_HEADER
            }
            response = requests.get(URL, headers=headers)
            # Check if request was successful
            if response.status_code == 200:
                # Display result in a large text area
                #st.success(f"Success! Status Code: {response.status_code}")
                #st.text_area("Response Result:", value=response.text, height=400)
                # 2. Create the DataFrame
                raw_text = response.text
                # FIX: Wrap the text in StringIO so pandas doesn't think it's a filename
                df = pd.read_csv(StringIO(raw_text))
                df['starttime'] = pd.to_datetime(df['starttime'])
                df['endtime'] = pd.to_datetime(df['endtime'])
                st.session_state['edf_run']=df
            else:
                st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
        URL = f"http://{baseurl}/csp/myrest/events/filter?type=Friend"
        AUTH_HEADER = f"Basic {token}" # Replace with your actual encoded credentials
        try:
            headers = {
                'Authorization': AUTH_HEADER
            }
            response = requests.get(URL, headers=headers)
            # Check if request was successful
            if response.status_code == 200:
                # Display result in a large text area
                #st.success(f"Success! Status Code: {response.status_code}")
                #st.text_area("Response Result:", value=response.text, height=400)
                # 2. Create the DataFrame
                raw_text = response.text
                # FIX: Wrap the text in StringIO so pandas doesn't think it's a filename
                df = pd.read_csv(StringIO(raw_text))
                df['starttime'] = pd.to_datetime(df['starttime'])
                df['endtime'] = pd.to_datetime(df['endtime'])
                st.session_state['edf_friend']=df
            else:
                st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
        URL = f"http://{baseurl}/csp/myrest/events/filter?type=Family"
        AUTH_HEADER = f"Basic {token}" # Replace with your actual encoded credentials
        try:
            headers = {
                'Authorization': AUTH_HEADER
            }
            response = requests.get(URL, headers=headers)
            # Check if request was successful
            if response.status_code == 200:
                # Display result in a large text area
                #st.success(f"Success! Status Code: {response.status_code}")
                #st.text_area("Response Result:", value=response.text, height=400)
                # 2. Create the DataFrame
                raw_text = response.text
                # FIX: Wrap the text in StringIO so pandas doesn't think it's a filename
                df = pd.read_csv(StringIO(raw_text))
                df['starttime'] = pd.to_datetime(df['starttime'])
                df['endtime'] = pd.to_datetime(df['endtime'])
                st.session_state['edf_family']=df
            else:
                st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# preview data
#if 'bdf' in st.session_state:
#    st.dataframe(st.session_state['bdf'])
#if 'bdf_ww' in st.session_state:
#    st.dataframe(st.session_state['bdf_ww'])
#if 'edf_isc' in st.session_state:
#    st.dataframe(st.session_state['edf_isc'])
#if 'edf_run' in st.session_state:
#    st.dataframe(st.session_state['edf_run'])
#if 'edf_isc' in st.session_state:
#    st.dataframe(st.session_state['edf_friend'])
#if 'edf_run' in st.session_state:
#    st.dataframe(st.session_state['edf_family'])

# --- 3. Sidebar Configuration ---
st.sidebar.header("Data Filters")

# Flight Filter (from previous steps)
show_flights = st.sidebar.checkbox("Show Flights", value=True)
show_ww_flights = st.sidebar.checkbox("Show WW Flights", value=True)

# Holiday Filters
st.sidebar.subheader("Public Holidays")
show_sg = st.sidebar.checkbox("Singapore 🇸🇬", value=True)
show_hk = st.sidebar.checkbox("Hong Kong 🇭🇰", value=True)

# Event Filters
st.sidebar.subheader("Events")
show_ev_isc = st.sidebar.checkbox("ISC Event", value=True)
show_ev_run = st.sidebar.checkbox("Running Event", value=True)
show_ev_friend = st.sidebar.checkbox("Friend Event", value=True)
show_ev_family = st.sidebar.checkbox("Family Event", value=True)

# --- 3. Sidebar Filters ---
## fix in later version

# --- 2. Build Event List ---
calendar_events = []

# A. Add Flights (if enabled)
if show_flights:
    if 'bdf' in st.session_state:
        for _, row in st.session_state['bdf'].iterrows():
            # Handle the null faretype by checking if it's null/NaN
            # We use pd.isna() or a simple 'if' check
            fare_type_val = row['faretype'] if pd.notna(row['faretype']) else "N/A"
            
            calendar_events.append({
                "title": f"✈️ {row['flightnumber']}",
                "start": row['departure'].isoformat(),
                "end": row['arrival'].isoformat(),
                "resourceId": "flight",
                "color": "#1E90FF",  # Dodger Blue
                "extendedProps": {
                    "type": "flight",
                    # This is what our tooltip will display
                    "description": f"----FareType: {fare_type_val}\n ----Airline: {row['airline']}",
                    "route": f"{row['fromcity']} to {row['tocity']}\n (Departure:{row['departure']} Arrival:{row['arrival']})",
                    "bookref": row['bookref'],
                    "fare": row['fareavgsgd'],
                    "currency": f"SGD",
                }
            })
# A1. Add WW Flights (if enabled)
if show_ww_flights:
    if 'bdf_ww' in st.session_state:
        for _, row in st.session_state['bdf_ww'].iterrows():
            calendar_events.append({
                "title": f"✈️ {row['flightnumber']}",
                "start": row['departure'].isoformat(),
                "end": row['arrival'].isoformat(),
                "resourceId": "flight",
                "color": "#434809FC",  # Yellow
                "extendedProps": {
                    "type": "flight",
                    # This is what our tooltip will display
                    "description": f"This is WW's Flight Schedule, please make sure don't overlap the booking with him",
                    "route": f"{row['fromcity']} to {row['tocity']}\n (Departure:{row['departure']} Arrival:{row['arrival']})",
                    "bookref": row['bookref'],
                    "fare": row['bookingprice'],
                    "currency": row['bookingcurrency']
                }
            })

# B. Add Singapore Holidays (if enabled)
if show_sg:
    sg_holidays = holidays.Singapore(years=[2025,2026,2027])
    for date, name in sg_holidays.items():
        calendar_events.append({
            "title": f"🇸🇬 {name}",
            "start": date.isoformat(),
            "allDay": True,
            "resourceId": "holiday",
            "color": "#e63946",  # Red-ish
            "extendedProps": {"type": "holiday"}
        })

# C. Add Hong Kong Holidays (if enabled)
if show_hk:
    hk_holidays = holidays.HongKong(years=[2025,2026,2027])
    for date, name in hk_holidays.items():
        calendar_events.append({
            "title": f"🇭🇰 {name}",
            "start": date.isoformat(),
            "allDay": True,
            "resourceId": "holiday",
            "color": "#ffb703",  # Gold/Yellow
            "extendedProps": {"type": "holiday"}
        })

# D. Add ISC event (if enabled)
if show_ev_isc:
    if 'edf_isc' in st.session_state:
        for _, row in st.session_state['edf_isc'].iterrows():
            calendar_events.append({
                "title": f"{row['eventtype']}: {row['name']}",
                "start": row['starttime'].isoformat(),
                "end": row['endtime'].isoformat(),
                "resourceId": "iscevent",
                "color": "#ff03c8",  # Gold/Yellow
                "extendedProps": {
                    "type": "event",
                    "eventid": row['ID'],
                    "eventtype" : row['eventtype'],
                    "status": row['status'],
                    "description":f"**INFO:** {row['descp']}"
                }
            })
        
# E. Add Run event (if enabled)
if show_ev_run:
    if 'edf_run' in st.session_state:
        for _, row in st.session_state['edf_run'].iterrows():
            calendar_events.append({
                "title": f"{row['eventtype']}: {row['name']}",
                "start": row['starttime'].isoformat(),
                "end": row['endtime'].isoformat(),
                "resourceId": "iscevent",
                "color": "#ff9e03",  # Gold/Yellow
                "extendedProps": {
                    "type": "event",                
                    "eventid": row['ID'],
                    "eventtype" : row['eventtype'],
                    "status": row['status'],
                    "description":f"**INFO:** {row['descp']}"
                }
            })
# F. Add Friend event (if enabled)
if show_ev_friend:
    if 'edf_friend' in st.session_state:
        for _, row in st.session_state['edf_friend'].iterrows():
            calendar_events.append({
                "title": f"{row['eventtype']}: {row['name']}",
                "start": row['starttime'].isoformat(),
                "end": row['endtime'].isoformat(),
                "resourceId": "friendevent",
                "color": "#03ffcd",  # Gold/Yellow
                "extendedProps": {
                    "type": "event",
                    "eventid": row['ID'],
                    "eventtype" : row['eventtype'],
                    "status": row['status'],
                    "description":f"**INFO:** {row['descp']}"
                }
            })

# F. Add Family event (if enabled)
if show_ev_family:
    if 'edf_family' in st.session_state:
        for _, row in st.session_state['edf_family'].iterrows():
            calendar_events.append({
                "title": f"{row['eventtype']}: {row['name']}",
                "start": row['starttime'].isoformat(),
                "end": row['endtime'].isoformat(),
                "resourceId": "familyevent",
                "color": "#d503ffb3",  # Gold/Yellow
                "extendedProps": {
                    "type": "event",
                    "eventid": row['ID'],
                    "eventtype" : row['eventtype'],
                    "status": row['status'],
                    "description":f"**INFO:** {row['descp']}"
                }
            })

# --- 3. Calendar View Logic ---
calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,listWeek",
    },
    "initialView": "dayGridMonth",
    "selectable": True,
    "editable": True,
    "resourceGroupField": "eventtype",
    "resources": [
        {"id":"flight","eventtype":"flight event","title":"On flight"},
        {"id":"holiday","eventtype":"holiday","title":"Public Holiday"},
    ],
}

custom_css = """
    .fc-event-main:hover::after {
        content: attr(title); /* This grabs the title attribute */
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background-color: #333;
        color: #fff;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        white-space: pre-wrap;
        z-index: 1000;
        width: 200px;
        display: block;
    }
"""

# Now pass this custom_css to the calendar

st.title(" ✈️ Travel & Holiday Planner")
state = calendar(events=calendar_events, options=calendar_options,custom_css=custom_css)


# --- Tooltip Display (On Click) ---
if state.get("eventClick"):
    event = state["eventClick"]["event"]
    # We find the matching row in our DataFrame to show even more detail
    title = event.get('title')
    
    with st.expander("📝 View Flight Details", expanded=True):
        st.write(f"### {title}")
        props = event.get("extendedProps", {})
        if props.get("type") == "flight":
            st.write(f"**Booking Reference:** {props.get('bookref', 'N/A')}")
            st.write(f"**Route:** {props.get('route')}")
            st.write(f"**Price:** {props.get('currency')} {props.get('fare')}")
            st.info(f"**Note:** {props.get('description')}")
        if props.get("type") == "holiday":
            st.write("This is a public holiday.")
        if props.get("type") == "event":
            st.write(f"This is a {props.get('eventtype', 'N/A')} Event with event ID --{props.get('eventid', 'N/A')}--. **Status:** {props.get('status', 'N/A')}")
            st.info(f"**Note:** {props.get('description')}")


# 4. Clear everything
if st.sidebar.button("Clear All Session Data"):
    clear_session()
    st.rerun()

st.sidebar.info("Note: All session data is automatically destroyed when the browser tab is closed.")