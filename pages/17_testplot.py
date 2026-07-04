import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
from io import StringIO

# --- 1. Global Setup & Mappings ---
st.set_page_config(layout="wide")
st.title("✈️ Global Flight Operations & Route Mapping")

AIRPORT_COORDS = {
    'SIN': [103.9910, 1.3644], 'HKG': [113.9145, 22.3080],
    'LHR': [-0.4543, 51.4700], 'DPS': [115.1664, -8.7482],
    'HND': [139.7811, 35.5494], 'NRT': [140.3929, 35.7720],
    'BKK': [100.7470, 13.6811],'SYD': [151.1770, -33.9461],
    'MEL': [144.8433, -37.6690], 'TPE': [121.2330, 25.0777]
}

# Function to wipe session data
def clear_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# --- 2. Sidebar Configuration & Credentials ---
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

# --- 3. Live API Login & Synchronization Engine ---
if 'creds' in st.session_state:
    if st.button("showcredential", type="primary"):
        c = st.session_state['creds']
        baseurl = str(c.get('str'))
        token = str(c.get('token'))
        
        URL = f"http://{baseurl}/csp/myrest/flight/all"
        AUTH_HEADER = f"Basic {token}"
        headers = {'Authorization': AUTH_HEADER}
        
        try:
            response = requests.get(URL, headers=headers)
            if response.status_code == 200:
                st.success(f"Success! Status Code: {response.status_code}")
                raw_text = response.text
                
                # Create the DataFrame from raw incoming CSV text stream
                df = pd.read_csv(StringIO(raw_text))
                df['departure'] = pd.to_datetime(df['departure'])
                df['arrival'] = pd.to_datetime(df['arrival'])
                
                # Cache into the target state variable
                st.session_state['bdf'] = df
            else:
                st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred during sync: {e}")

st.markdown("---")

# --- 4. Live Map Visualization Panel ---
if 'bdf' in st.session_state:
    # Safe decoupled copy to keep data manipulation clean
    df_map = st.session_state['bdf'].copy()
    
    if not df_map.empty:
        # 1. Calculate Route Frequency for line thickness
        df_map['route_id'] = df_map['fromcity'].astype(str) + "-" + df_map['tocity'].astype(str)
        route_counts = df_map.groupby('route_id').size().reset_index(name='frequency')
        df_map = df_map.merge(route_counts, on='route_id')

        # 2. Mapping Coordinates
        df_map['from_lon'] = df_map['fromcity'].map(lambda x: AIRPORT_COORDS.get(x, [0,0])[0])
        df_map['from_lat'] = df_map['fromcity'].map(lambda x: AIRPORT_COORDS.get(x, [0,0])[1])
        df_map['to_lon'] = df_map['tocity'].map(lambda x: AIRPORT_COORDS.get(x, [0,0])[0])
        df_map['to_lat'] = df_map['tocity'].map(lambda x: AIRPORT_COORDS.get(x, [0,0])[1])

        # Render Interface Layout
        st.subheader("📊 Flight Volume Visualization")
        st.write("Routes with more flights appear thicker and brighter.")

        tilt_logic = "index % 20 - 10" if "ID" not in df_map.columns else "ID % 20 - 10"

        # 3. PyDeck Graphics Mapping Execution
        arc_layer = pdk.Layer(
            "ArcLayer",
            data=df_map,
            get_source_position=["from_lon", "from_lat"],
            get_target_position=["to_lon", "to_lat"],
            get_source_color="[255, 165, 0, 140]",  # Source (Orange)
            get_target_color="[0, 150, 255, 140]",  # Target (Blue)
            get_tilt=tilt_logic, 
            get_width="1 + (frequency * 0.5)",
            pickable=True,
        )

        view_state = pdk.ViewState(latitude=20, longitude=90, zoom=2.5, pitch=45)

        st.pydeck_chart(pdk.Deck(
            layers=[arc_layer],
            initial_view_state=view_state,
            map_style="dark",
            tooltip={"text": "{airline}: {fromcity} to {tocity}\nTotal trips this route: {frequency}"}
        ))

        # Data Reference Table View 
        st.divider()
        st.subheader("📋 Full Flight History")
        st.dataframe(df_map.sort_values('departure', ascending=False), use_container_width=True)
    else:
        st.warning("The retrieved database contains no matching records.")
else:
    st.info("💡 Please upload credentials in the sidebar and click **'showcredential'** to synchronize flights and generate the routing map.")

# Reset / Clear Functionality
st.sidebar.markdown("---")
if st.sidebar.button("Clear All Session Data"):
    clear_session()
    st.rerun()