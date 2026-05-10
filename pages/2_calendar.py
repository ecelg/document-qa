import streamlit as st
import pandas as pd
import requests
from io import StringIO # Don't forget this import!

# Function to wipe session data
def clear_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

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

if 'creds' in st.session_state:
    if st.button("showcredential"):
        c = st.session_state['creds']
        baseurl=str(c.get('str'))
        token=str(c.get('token'))
        #URL = f"http://{baseurl}/csp/myrest/event/7"
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
                st.success(f"Success! Status Code: {response.status_code}")
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
                st.success(f"Success! Status Code: {response.status_code}")
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
                st.success(f"Success! Status Code: {response.status_code}")
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
                st.success(f"Success! Status Code: {response.status_code}")
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
                st.success(f"Success! Status Code: {response.status_code}")
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
                st.success(f"Success! Status Code: {response.status_code}")
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

if 'bdf' in st.session_state:
    st.dataframe(st.session_state['bdf'])
if 'bdf_ww' in st.session_state:
    st.dataframe(st.session_state['bdf_ww'])
if 'edf_isc' in st.session_state:
    st.dataframe(st.session_state['edf_isc'])
if 'edf_run' in st.session_state:
    st.dataframe(st.session_state['edf_run'])
if 'edf_isc' in st.session_state:
    st.dataframe(st.session_state['edf_friend'])
if 'edf_run' in st.session_state:
    st.dataframe(st.session_state['edf_family'])

# 4. Clear everything
if st.sidebar.button("Clear All Session Data"):
    clear_session()
    st.rerun()

st.sidebar.info("Note: All session data is automatically destroyed when the browser tab is closed.")