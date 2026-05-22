import cv2
import numpy as np
import streamlit as st
from camera_input_live import camera_input_live

st.title("QR Code Scanner")

# 1. Initialize session state to track camera status
if "run_camera" not in st.session_state:
    st.session_state.run_camera = False

# 2. Add the toggle button
if st.session_state.run_camera:
    if st.button("Stop Camera"):
        st.session_state.run_camera = False
        st.rerun()
else:
    if st.button("Start Capture"):
        st.session_state.run_camera = True
        st.rerun()

# 3. Only run the camera if the state is True
if st.session_state.run_camera:
    detector = cv2.QRCodeDetector()
    image = camera_input_live()

    if image:
        bytes_data = image.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

        if data:
            st.success("QR Code Detected!")
            st.write(f"**Content:** {data}")
            
            # Optional: Stop camera automatically after a successful scan
            st.session_state.run_camera = False
            st.rerun()
        else:
            st.info("Place a QR code in front of the camera.")
else:
    st.info("Camera is turned off. Click 'Start Capture' to begin scanning.")
