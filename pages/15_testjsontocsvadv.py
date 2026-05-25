import streamlit as st
import pandas as pd
import json
import requests
from io import StringIO

st.set_page_config(page_title="JSON to CSV Form Converter", layout="wide")
st.title("Advanced JSON & CSV Data Utility")

# ==========================================
# SIDEBAR: DYNAMIC CREDENTIAL UPLOADER
# ==========================================
def clear_session():
    """Wipes all session state parameters cleanly."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Persistent file uploader tracking across application context
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

if st.sidebar.button("Clear App Session", on_click=clear_session):
    st.sidebar.info("Session state wiped clean.")

# Initialize form structure state 
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

# ==========================================
# CALLBACK FUNCTION FOR TAB-TO-TAB TRANSFER
# ==========================================
def transfer_json_to_form(json_payload):
    """Callback that guarantees data is safely injected into Tab 1 state before a rerun."""
    # 1. Clear old form sub-widget cache keys to prevent UI ghosting
    for key in list(st.session_state.keys()):
        if key.startswith("root.") or key.startswith("Observation.") or key.startswith("Patient.") or "." in key or "[" in key:
            del st.session_state[key]
            
    # 2. Inject fresh payload data
    st.session_state.form_data = json_payload
    st.session_state["json_input_area"] = json.dumps(json_payload, indent=2)
    st.toast("🎯 Payload transferred to Tab 1! Switch to 'Create CSV from JSON' to edit.")

# ==========================================
# HELPER FUNCTIONS FOR RENDERING & PARSING
# ==========================================
def render_dynamic_inputs(data, parent_key=""):
    """Recursively renders form inputs for nested dictionaries and arrays."""
    updated_structure = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                st.markdown(f"##### 📦 Group: **{key.upper()}**")
                with st.container():
                    st.write("---")
                    updated_structure[key] = render_dynamic_inputs(value, full_key)
                    st.write("---")
            elif isinstance(value, list):
                st.markdown(f"##### 📋 List: **{key.upper()}**")
                updated_structure[key] = render_dynamic_inputs(value, full_key)
            else:
                updated_structure[key] = render_input_field(full_key, key, value)
                
    elif isinstance(data, list):
        updated_list = []
        for index, item in enumerate(data):
            full_key = f"{parent_key}[{index}]"
            if isinstance(item, (dict, list)):
                st.markdown(f"**Item #{index + 1}**")
                updated_list.append(render_dynamic_inputs(item, full_key))
            else:
                label = f"Item {index + 1}"
                updated_list.append(render_input_field(full_key, label, item))
        return updated_list

    return updated_structure

def render_input_field(unique_id, label, value):
    """Renders individual input field based on data type and provides contextual HL7 linking."""
    if isinstance(value, int):
        return st.number_input(label, value=value, step=1, key=unique_id)
    elif isinstance(value, float):
        return st.number_input(label, value=value, key=unique_id)
    elif isinstance(value, bool):
        return st.checkbox(label, value=value, key=unique_id)
    else:
        string_val = str(value)
        user_input = st.text_input(label, value=string_val, key=unique_id)
        
        if label.lower() == "system" and "http://hl7.org" in user_input:
            st.markdown(
                f"🔗 **HL7 Reference Found:** [Browse CodeSystem Properties ↗]({user_input.strip()})  \n"
                f"*Use this reference to explore acceptable codes for validation.*"
            )
            
        return user_input

def flatten_json(y):
    """Flattens nested JSON dictionaries into a single level for CSV export."""
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

def unflatten_json(flat_dict):
    """Converts a flattened dictionary back into a nested JSON structure."""
    result = {}
    for key, value in flat_dict.items():
        if pd.isna(value):
            value = None
            
        parts = key.split('_')
        current = result
        
        for i, part in enumerate(parts[:-1]):
            next_part = parts[i+1]
            is_next_digit = next_part.isdigit()
            
            if part.isdigit():
                idx = int(part)
                while len(current) <= idx:
                    current.append([] if is_next_digit else {})
                current = current[idx]
            else:
                if part not in current:
                    current[part] = [] if is_next_digit else {}
                current = current[part]
                
        last_part = parts[-1]
        if last_part.isdigit():
            idx = int(last_part)
            while len(current) <= idx:
                current.append(None)
            current[idx] = value
        else:
            current[last_part] = value
            
    return result

# Create the three main tabs
tab1, tab2, tab3, tab4 = st.tabs(["Create CSV from JSON", "Upload & View CSV", "Fetch FHIR Resources", "PUT/POST FHIR Resources"])

# ==========================================
# TAB 1: CREATE CSV FROM JSON
# ==========================================
with tab1:
    st.header("Generate Form from Complex JSON")
    
    sample_json = sample_json = {
        "address": {
            "city": "Jakarta",
            "country": "ID",
            "line": [
                "Gd. Prof. Dr. Sujudi Lt.5, Jl. H.R. Rasuna Said Blok X5 Kav. 4-9 Kuningan"
            ],
            "postalCode": "12950",
            "use": "work"
        },
        "description": "Ruang 1A, Poliklinik Bedah Rawat Jalan Terpadu, Lantai 2, Gedung G",
        "id": "dc01c797-547a-4e4d-97cd-4ece0630e380",
        "identifier": [
            {
                "system": "http://sys-ids.kemkes.go.id/location/1000001",
                "value": "G-2-R-1A"
            }
        ],
        "managingOrganization": {
            "reference": "Organization/10000004"
        },
        "mode": "instance",
        "name": "Ruang 1A IRJT",
        "physicalType": {
            "coding": [
                {
                    "code": "ro",
                    "display": "Room",
                    "system": "http://terminology.hl7.org/CodeSystem/location-physical-type"
                }
            ]
        },
        "resourceType": "Location",
        "status": "active",
        "telecom": [
            {
                "system": "phone",
                "use": "work",
                "value": "2328"
            },
            {
                "system": "email",
                "value": "second.wing@admissions.org"
            },
            {
                "system": "url",
                "use": "work",
                "value": "http://sampleorg.com/southwing"
            }
        ]
    }
    
    # Check if a custom value has been loaded via Tab 3's callback
    default_text = json.dumps(sample_json, indent=2)
    if "json_input_area" in st.session_state:
        default_text = st.session_state["json_input_area"]

    json_input = st.text_area(
        "Paste your complex JSON object here:", 
        height=200,
        value=json.dumps(sample_json, indent=2),
        key="json_input_area"
    )
    
    if st.button("Generate Form"):
        try:
            parsed_json = json.loads(json_input)
            if isinstance(parsed_json, dict):
                st.session_state.form_data = parsed_json
                st.success("Form generated successfully!")
            else:
                st.error("Please provide a valid JSON object starting with curly braces {}.")
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {e}")

    if st.session_state.form_data:
        st.subheader("Modify Data Fields")
        
        with st.form(key="dynamic_nested_form"):
            current_form_state = render_dynamic_inputs(st.session_state.form_data)
            submit_form = st.form_submit_button("Lock Changes")
            
        if submit_form:
            st.session_state.form_data = current_form_state
            st.toast("Changes locked in!")

        flattened_data = flatten_json(st.session_state.form_data)
        df_export = pd.DataFrame([flattened_data])
        
        st.subheader("Preview of flattened data for CSV export:")
        st.dataframe(df_export)
        
        csv_bytes = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export Result to CSV",
            data=csv_bytes,
            file_name="complex_generated_data.csv",
            mime="text/csv"
        )

# ==========================================
# TAB 2: UPLOAD & VIEW CSV
# ==========================================
with tab2:
    st.header("Upload and Display CSV")
    uploaded_file_csv = st.file_uploader("Choose your modified CSV file", type=["csv"], key="uploader")
    
    if uploaded_file_csv is not None:
        try:
            df_uploaded = pd.read_csv(uploaded_file_csv)
            st.success("File uploaded successfully!")
            
            st.subheader("DataFrame View")
            st.dataframe(df_uploaded, use_container_width=True)
            
            st.subheader("Reconstructed JSON Output")
            
            records = df_uploaded.to_dict(orient="records")
            reconstructed_json_list = [unflatten_json(row) for row in records]
            
            json_string = json.dumps(reconstructed_json_list, indent=2)
            st.json(reconstructed_json_list)
            
            st.download_button(
                label="Download Reconstructed JSON",
                data=json_string,
                file_name="reconstructed_data.json",
                mime="application/json"
            )
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")

# ==========================================
# TAB 3: FETCH FHIR RESOURCES FROM SESSION CREDS
# ==========================================
with tab3:
    st.header("Fetch Current Resources from FHIR Repo")
    
    # Check if configurations exist inside the global tracking object
    if 'creds' not in st.session_state:
        st.warning("⚠️ Please upload a valid `credentials.txt` file in the sidebar to authenticate.")
    else:
        c = st.session_state['creds']
        baseurl = str(c.get('baseurl', ''))
        token = str(c.get('token', ''))
        hostname = str(c.get('str', ''))

        # Visual indicator showing current active profile parameters
        with st.expander("Active Connection Info"):
            st.write(f"**Base URL:** `{baseurl}`")
            st.write(f"**Hostname:** `{hostname}`")
            st.write(f"**Token Length:** {len(token)} characters")

        # Query Formulation Inputs
        res_type = st.text_input("Resource Type", value="Patient", help="Example: Patient, Observation, Practitioner")
        res_id = st.text_input("Resource ID (Optional)", value="", help="Leave empty to retrieve a list of this type")

        # New search parameters section
        st.markdown("### 🔍 Search Filters (Optional)")
        st.caption("Filters are ignored if a specific Resource ID is provided above.")

        # Columns for Parameter 1
        p_col1_key, p_col1_val = st.columns(2)
        with p_col1_key:
            param1_key = st.text_input("Parameter 1 Key", value="", placeholder="e.g., gender")
        with p_col1_val:
            param1_val = st.text_input("Parameter 1 Value", value="", placeholder="e.g., female")

        # Columns for Parameter 2
        p_col2_key, p_col2_val = st.columns(2)
        with p_col2_key:
            param2_key = st.text_input("Parameter 2 Key", value="", placeholder="e.g., _count")
        with p_col2_val:
            param2_val = st.text_input("Parameter 2 Value", value="", placeholder="e.g., 10")
        
        if "last_fetched_json" not in st.session_state:
            st.session_state.last_fetched_json = None

        if st.button("Fetch Target Resource"):
            if not baseurl or not token:
                st.error("Invalid configuration profiles detected. Ensure `baseurl` and `token` exist in the file.")
            else:
                # Construct target endpoint following clean URL formatting rules
                clean_base = baseurl.rstrip('/')
                URL = f"{clean_base}/{res_type.strip()}"

                # Setup parameters dictionary
                search_params = {}

                if res_id.strip():
                    URL += f"/{res_id.strip()}"
                else:
                    # Append query key-values dynamically if provided
                    if param1_key.strip() and param1_val.strip():
                        search_params[param1_key.strip()] = param1_val.strip()
                    if param2_key.strip() and param2_val.strip():
                        search_params[param2_key.strip()] = param2_val.strip()

                # Match authorization layout used by your server specification
                headers = {
                    'Authorization': f"Basic {token}",
                    'Accept': 'application/fhir+json'
                }

                with st.spinner(f"Querying endpoint: {URL}..."):
                    try:
                        response = requests.get(URL, headers=headers, params=search_params, timeout=10)
                        
                        if response.status_code == 200:
                            st.session_state.last_fetched_json = response.json()
                            st.success(f"Success! Status Code: 200")
                        else:
                            st.session_state.last_fetched_json = None
                            st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                            st.text_area("Server Response Context", value=response.text, height=150)
                    except Exception as e:
                        st.session_state.last_fetched_json = None
                        st.error(f"Connectivity error: {e}")
                
                # Render data and transfer action options if data exists
                if st.session_state.last_fetched_json is not None:
                    st.json(st.session_state.last_fetched_json)
                    # FIXED: Uses args and an explicit callback to mutate session state safely before the app reruns
                    st.button("Load this payload directly into Tab 1",
                              on_click=transfer_json_to_form,
                              args=(st.session_state.last_fetched_json,)
                              )


# ==========================================
# TAB 4: PUT/POST FHIR RESOURCES
# ==========================================
with tab4:
    st.header("Submit FHIR Resources (PUT/POST)")

    if 'creds' not in st.session_state:
        st.warning("⚠️ Please upload a valid `credentials.txt` file in the sidebar to authenticate.")
    else:
        c = st.session_state['creds']
        baseurl = str(c.get('baseurl', ''))
        token = str(c.get('token', ''))
        hostname = str(c.get('str', ''))

        # Visual indicator showing current active profile parameters
        with st.expander("Active Connection Info"):
            st.write(f"**Base URL:** `{baseurl}`")
            st.write(f"**Hostname:** `{hostname}`")
            st.write(f"**Token Length:** {len(token)} characters")
            
        # Action layout configurations
        col_method, col_res_type, col_res_id = st.columns(3)
        with col_method:
            http_method = st.selectbox("HTTP Method", ["POST", "PUT"], key="tab4_method_select")
        with col_res_type:
            payload_res_type = st.text_input("FHIR Resource Type", value="Patient", key="tab4_res_type")
        with col_res_id:
            payload_res_id = st.text_input(
                "FHIR Resource ID", 
                value="", 
                disabled=(http_method == "POST"), 
                help="Required for PUT operations.",
                key="tab4_res_id"
            )

        # Build dynamic URL target endpoint
        if http_method == "POST":
            target_url = f"{baseurl}/{payload_res_type}"
        else:
            target_url = f"{baseurl}/{payload_res_type}/{payload_res_id}" if payload_res_id else f"{baseurl}/{payload_res_type}"

        st.info(f"🚀 Target Endpoint: `{target_url}`")

        # JSON Input Area
        fhir_payload_string = st.text_area(
            "FHIR Resource JSON Payload", 
            value="{\n  \"resourceType\": \"" + payload_res_type + "\"\n}", 
            height=300,
            key="tab4_json_payload"
        )

        # Submission Execution Button
        if st.button("Submit to FHIR Server", type="primary", key="tab4_submit_btn"):
            if http_method == "PUT" and not payload_res_id:
                st.error("❌ Resource ID is strictly required for PUT updates.")
            else:
                try:
                    json_payload = json.loads(fhir_payload_string)
                    
                    # Core target headers
                    # Match authorization layout used by your server specification
                    headers = {
                        'Authorization': f"Basic {token}",
                        "Content-Type": "application/fhir+json",
                        'Accept': 'application/fhir+json'
                    }

                    with st.spinner(f"Sending {http_method} request..."):
                        if http_method == "POST":
                            response = requests.post(target_url, json=json_payload, headers=headers)
                        else:
                            response = requests.put(target_url, json=json_payload, headers=headers)

                    # Handle response validation status code window
                    if response.status_code in [200, 201, 204]:
                        st.success(f"✅ Success! Server returned HTTP Status {response.status_code}")
                    else:
                        st.error(f"❌ Server Error! Returned HTTP Status {response.status_code}")
                        st.caption("Review the server error details returned below:")

                    # Render text output directly if HTML is returned instead of JSON
                    try:
                        st.json(response.json())
                    except ValueError:
                        st.code(response.text, language="html")

                except json.JSONDecodeError as je:
                    st.error(f"❌ Invalid JSON format payload: {str(je)}")
                except Exception as e:
                    st.error(f"❌ Connection pipeline failure: {str(e)}")
