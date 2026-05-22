import cv2
import numpy as np
import streamlit as st

st.title("iPhone Compatible QR Scanner")

# 1. Initialize session state to track if we are actively scanning
if "scanning" not in st.session_state:
    st.session_state.scanning = False

# 2. Toggle button to control the camera UI
if not st.session_state.scanning:
    if st.button("Start Scanner"):
        st.session_state.scanning = True
        st.rerun()
else:
    if st.button("Close Scanner"):
        st.session_state.scanning = False
        st.rerun()

# 3. Secure camera widget for iOS
if st.session_state.scanning:
    # st.camera_input triggers native iOS camera integration smoothly
    img_file = st.camera_input("Position the QR code inside the frame")

    if img_file is not None:
        # Convert the picture to an OpenCV matrix
        bytes_data = img_file.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        # Detect and decode the QR code
        detector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

        if data:
            st.success("🎉 QR Code Detected Successfully!")
            st.write(f"**Decoded Content:** {data}")
            
            # Close camera automatically after successful reading
            st.session_state.scanning = False
            st.button("Scan Again")
        else:
            st.error("No valid QR code found in this photo. Please try again.")
