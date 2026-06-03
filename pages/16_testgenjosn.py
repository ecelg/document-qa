import streamlit as st
import pandas as pd
import requests
import json
from io import StringIO
from datetime import datetime

# Function to wipe session data
def clear_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Helper function to extract only the TIME part from a datetime value (HH:MM)
def extract_time_part(date_val, default_time="00:00"):
    if pd.isna(date_val) or not date_val:
        return default_time
    try:
        dt = pd.to_datetime(date_val)
        return dt.strftime("%H:%M")
    except Exception:
        return default_time

st.set_page_config(layout="wide") # Use wide mode to fit Sector 1 and Sector 2 side-by-side cleanly
st.title("✈️ Flight Records Tracker & Itinerary Builder")

# --- 1. Sidebar Configuration & Credentials ---
uploaded_file = st.sidebar.file_uploader("Upload credentials.txt", type=["txt"])
if uploaded_file and 'creds' not in st.session_state:
    content = uploaded_file.read().decode("utf-8")
    creds = {}
    for line in content.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip()
    st.session_state['creds'] = creds
    st.sidebar.success("Credentials stored in session!")

# Load Data via REST endpoint
if 'creds' in st.session_state:
    if st.button("Login / Sync Data"):
        c = st.session_state['creds']
        baseurl = str(c.get('str'))
        token = str(c.get('token'))
        AUTH_HEADER = f"Basic {token}"
        headers = {'Authorization': AUTH_HEADER}

        # --- Fetch Unique Flight Numbers via Deduplicated SQL ---
        URL_FN = f"http://{baseurl}/csp/myrest/flight/flightnumber"
        try:
            res_fn = requests.get(URL_FN, headers=headers)
            if res_fn.status_code == 200:
                df_fn = pd.read_csv(StringIO(res_fn.text))
                st.session_state['df_flightnumber'] = df_fn
                st.success("Flight records synchronized successfully!")
            else:
                st.error(f"Failed to fetch Flight Numbers. Status: {res_fn.status_code}")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

# --- 2. Main Interface Tabs ---
tab1, tab2 = st.tabs(["📋 Multi-Sector Itinerary Builder", "⚙️ Session Diagnostics"])

# Tab 1: Multi-Sector Configuration & Dynamic JSON Generation
with tab1:
    if 'df_flightnumber' in st.session_state:
        df = st.session_state['df_flightnumber']
        flight_list = df['flightnumber'].dropna().unique().tolist()
        
        # Display global overview
        with st.expander("📊 View Synchronized Reference Database Rows"):
            st.dataframe(df, use_container_width=True)
        
        # --- Top Level: Booking Metadata ---
        st.subheader("📆 Global Booking Parameters")
        booking_date_picked = st.date_input("Select Booking Date:", value=datetime.today())
        formatted_booking_date = booking_date_picked.strftime("%d%b%Y")
        
        st.markdown("---")
        
        # --- Multi-Column Layout: Sector 1 vs Sector 2 ---
        sec_col1, sec_col2 = st.columns(2)
        
        sectors_payload = []
        global_airline = "" # Fallback global airline tracker
        
        # === SECTOR 1 CONFIGURATION ===
        with sec_col1:
            st.subheader("🛫 Sector 1 (Outbound)")
            sub_col1, sub_col2 = st.columns([3, 3])
            
            with sub_col1:
                s1_flight = st.selectbox("Flight Number (S1):", options=flight_list, key="s1_fl")
            
            if s1_flight:
                r1 = df[df['flightnumber'] == s1_flight].iloc[0]
                # Fallback default for departure date picker based on row values
                b_dept1 = pd.to_datetime(r1.get('departure')) if pd.notna(r1.get('departure')) else datetime.today()
                
                with sub_col2:
                    s1_date_picked = st.date_input("Flight Date (S1):", value=b_dept1.date(), key="s1_dd")
                
                # Extract clean time components
                t_dept1 = extract_time_part(r1.get('departure'), "20:05")
                t_arr1 = extract_time_part(r1.get('arrival'), "00:10")
                
                # Date string formatting using the single chosen flight date
                formatted_date_s1 = s1_date_picked.strftime('%d%b%Y')
                
                if 'airline' in r1:
                    global_airline = str(r1.get('airline'))
                
                sectors_payload.append({
                    "flightnumber": str(r1.get('flightnumber', '')),
                    "fromcity": str(r1.get('fromcity', '')),
                    "tocity": str(r1.get('tocity', '')),
                    "departure": f"{formatted_date_s1} {t_dept1}",
                    "arrival": f"{formatted_date_s1} {t_arr1}",  # Uses departure date picker string
                    "cabinclass": str(r1.get('cabinclass', '')),
                    "seat": str(r1.get('seat')) if pd.notna(r1.get('seat')) and r1.get('seat') != "" else "N/A",
                    "faretype": str(r1.get('faretype', '')),
                    "baggage": str(r1.get('baggage', ''))
                })

        # === SECTOR 2 CONFIGURATION ===
        with sec_col2:
            st.subheader("🛬 Sector 2 (Return)")
            sub_col3, sub_col4 = st.columns([3, 3])
            
            with sub_col3:
                s2_flight = st.selectbox("Flight Number (S2):", options=flight_list, key="s2_fl")
            
            if s2_flight:
                r2 = df[df['flightnumber'] == s2_flight].iloc[0]
                b_dept2 = pd.to_datetime(r2.get('departure')) if pd.notna(r2.get('departure')) else datetime.today()
                
                with sub_col4:
                    s2_date_picked = st.date_input("Flight Date (S2):", value=b_dept2.date(), key="s2_dd")
                
                # Extract clean time components
                t_dept2 = extract_time_part(r2.get('departure'), "20:55")
                t_arr2 = extract_time_part(r2.get('arrival'), "00:45")
                
                # Date string formatting using the single chosen flight date
                formatted_date_s2 = s2_date_picked.strftime('%d%b%Y')
                
                sectors_payload.append({
                    "flightnumber": str(r2.get('flightnumber', '')),
                    "fromcity": str(r2.get('fromcity', '')),
                    "tocity": str(r2.get('tocity', '')),
                    "departure": f"{formatted_date_s2} {t_dept2}",
                    "arrival": f"{formatted_date_s2} {t_arr2}",  # Uses departure date picker string
                    "cabinclass": str(r2.get('cabinclass', '')),
                    "seat": str(r2.get('seat')) if pd.notna(r2.get('seat')) and r2.get('seat') != "" else "N/A",
                    "faretype": str(r2.get('faretype', '')),
                    "baggage": str(r2.get('baggage', ''))
                })

        # --- Final JSON Assembly ---
        master_template = {
            "bookref": "NA",
            "bookingdate": formatted_booking_date,
            "bookingstatus": "OK",
            "airline": global_airline,
            "sectors": sectors_payload,
            "fare": {
                "currency": "SGD",
                "farenet": 254.0,
                "faretotal": 254.0,
                "taxtotal": 0.0,
                "subchargetotal": 0.0
            }
        }
        
        st.markdown("---")
        st.subheader("🛠️ Compiled Dynamic Multi-Sector JSON Codeblock")
        
        json_string = json.dumps(master_template, indent=4)
        editable_json = st.text_area(
            label="Freely modify or copy your multi-sector itinerary payload:",
            value=json_string,
            height=550
        )
        
        try:
            json.loads(editable_json)
            st.caption("✅ Valid JSON structure array syntax.")
        except Exception:
            st.caption("❌ Invalid JSON formatting structure syntax.")
            
    else:
        st.info("Please upload credentials and click 'Login / Sync Data' to display flights.")

# Tab 2: Event Creator Template Generator & API Submitter
with tab2:
    st.subheader("🗓️ Event Creator Template Generator")
    st.markdown("Fill out the details below to generate, edit, or submit your event payload.")

    # 1. Row-based UI Inputs using Streamlit Columns
    col_left, col_right = st.columns(2)

    with col_left:
        name_val = st.text_input("Name:", placeholder="e.g., HealthTechX Asia")
        
        # Date and Time Layout
        st.markdown("**Start Schedule**")
        c_sd, c_st = st.columns(2)
        with c_sd:
            s_date = st.date_input("Start Date:", value=datetime.today())
        with c_st:
            s_hour = st.selectbox(
                "Start Time:", 
                options=[f"{i:02d}:00:00" for i in range(24)], 
                index=9, 
                key="evt_sh"
            )

        status_val = st.selectbox(
            "Status:",
            options=['ongoing', 'planning', 'changed', 'cancelled', 'monitoring'],
            index=1
        )

    with col_right:
        descp_val = st.text_area("Description:", placeholder="Event details...", height=68)
        
        st.markdown("**End Schedule**")
        c_ed, c_et = st.columns(2)
        with c_ed:
            e_date = st.date_input("End Date:", value=datetime.today())
        with c_et:
            e_hour = st.selectbox(
                "End Time:", 
                options=[f"{i:02d}:00:00" for i in range(24)], 
                index=17, 
                key="evt_eh"
            )

        event_type_map = {'ISC': '1', 'Run': '2', 'Family': '3', 'Friend': '4'}
        type_val = st.selectbox("Type:", options=list(event_type_map.keys()))

    # 2. Combine Strings & Construct Dictionary Payload
    start_ts = f"{s_date.strftime('%Y-%m-%d')} {s_hour}"
    end_ts = f"{e_date.strftime('%Y-%m-%d')} {e_hour}"

    event_data = {
        "name": name_val,
        "descp": descp_val,
        "starttime": start_ts,
        "endtime": end_ts,
        "status": status_val,
        "eventtype": event_type_map[type_val]
    }

    st.markdown("---")
    st.subheader("🛠️ Compiled Event JSON Editor")

    # Convert dictionary into a formatted JSON text block string
    json_event_string = json.dumps(event_data, indent=4)
    
    # Output into an editable text area
    editable_event_json = st.text_area(
        label="Freely modify or copy your event payload before submitting:",
        value=json_event_string,
        height=300
    )

    # Simple validation flag tracking
    is_valid_json = False
    try:
        parsed_payload = json.loads(editable_event_json)
        st.caption("✅ Valid Event JSON structure ready.")
        is_valid_json = True
    except Exception:
        st.caption("❌ Invalid JSON formatting structure syntax. Submission blocked.")

    st.markdown("---")
    st.subheader("🚀 API Transmission Engine")

    # Target ID input and Action submission buttons layout row
    api_col1, api_col2, api_col3 = st.columns([2, 2, 2])

    with api_col1:
        target_id = st.text_input("Target ID:", placeholder="Required for Put (Update) actions")

    # Ensure authentication headers are available from active sessions
    if 'creds' in st.session_state:
        c = st.session_state['creds']
        baseurl = str(c.get('str'))
        token = str(c.get('token'))
        
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {token}"
        }
        API_BASE_URL = f"http://{baseurl}/csp/myrest/event"

        with api_col2:
            st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True) # Spacer alignment
            if st.button("Post Event (Create)", use_container_width=True, type="primary", disabled=not is_valid_json):
                url = f"{API_BASE_URL}/create"
                try:
                    response = requests.post(url, json=parsed_payload, headers=HEADERS)
                    if response.status_code in [200, 201]:
                        st.success(f"Success! Created successfully. Status: {response.status_code}")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Network error processing POST: {e}")

        with api_col3:
            st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True) # Spacer alignment
            # Disable button if target_id is empty or JSON is corrupted
            put_disabled = not is_valid_json or not target_id.strip()
            if st.button("Put Event (Update)", use_container_width=True, disabled=put_disabled):
                url = f"{API_BASE_URL}/update/{target_id.strip()}"
                try:
                    response = requests.put(url, json=parsed_payload, headers=HEADERS)
                    if response.status_code in [200, 201]:
                        st.success(f"Success! Updated ID {target_id} successfully. Status: {response.status_code}")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Network error processing PUT: {e}")
    else:
        st.warning("⚠️ API Submissions locked. Please authenticate via credentials first in the sidebar.")

# Reset / Clear Functionality (Preserved at the bottom of the script)
st.sidebar.markdown("---")
if st.sidebar.button("Clear All Session Data"):
    clear_session()
    st.rerun()