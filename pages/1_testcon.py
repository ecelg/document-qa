import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

# Function to wipe session data
def clear_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

uploaded_file = st.file_uploader("Upload credentials.txt", type=["txt"])
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
        constr=str(c.get('str'))
        st.write(constr)
        engine = create_engine(constr)
        sql_query = """
        SELECT
            ID, airline->name as airline, flightnumber, arrival, bookref, departure, fromcity->code as fromcity, tocity->code as tocity,
            faretype->code as faretype, bookingprice->avgfaretotalsgd AS fareavgsgd
        FROM flight_trans.booking
        order by departure desc
        """
        df = pd.read_sql(sql_query, engine)
        engine.dispose()

# 4. Clear everything
if st.button("Clear All Session Data"):
    clear_session()
    st.rerun()

st.info("Note: All session data is automatically destroyed when the browser tab is closed.")