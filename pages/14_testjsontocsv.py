import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="JSON to CSV Form Converter", layout="wide")
st.title("Advanced JSON & CSV Data Utility")

# Initialize session state to store form data dynamically
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

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
        # Render standard input field first
        string_val = str(value)
        user_input = st.text_input(label, value=string_val, key=unique_id)
        
        # HL7 URL Context Detection
        if label.lower() == "system" and "http://terminology.hl7.org/CodeSystem/" in user_input:
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

# Create the two tabs
tab1, tab2 = st.tabs(["Create CSV from JSON", "Upload & View CSV"])

# ==========================================
# TAB 1: CREATE CSV FROM JSON
# ==========================================
with tab1:
    st.header("Generate Form from Complex JSON")
    
    # Pre-populated example showing nested structure containing target HL7 values
    sample_json = {
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
    uploaded_file = st.file_uploader("Choose your modified CSV file", type=["csv"], key="uploader")
    
    if uploaded_file is not None:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
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
            st.error(f"Error processing file or reconstructing JSON: {e}")
