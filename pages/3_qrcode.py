import io
import cv2
import numpy as np
import qrcode
import streamlit as st

st.title("QR Code Toolbox")

# Create the two tabs
tab1, tab2 = st.tabs(["🔍 QR Scanner", "✨ QR Generator"])

# ==========================================
# TAB 1: QR CODE SCANNER (iPhone Compatible)
# ==========================================
with tab1:
    st.subheader("Scan QR Code")

    if "scanning" not in st.session_state:
        st.session_state.scanning = False

    if not st.session_state.scanning:
        if st.button("Start Scanner", key="btn_start"):
            st.session_state.scanning = True
            st.rerun()
    else:
        if st.button("Close Scanner", key="btn_stop"):
            st.session_state.scanning = False
            st.rerun()

    if st.session_state.scanning:
        img_file = st.camera_input("Position the QR code inside the frame")

        if img_file is not None:
            bytes_data = img_file.getvalue()
            cv2_img = cv2.imdecode(
                np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR
            )

            detector = cv2.QRCodeDetector()
            data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

            if data:
                st.success("🎉 QR Code Detected Successfully!")
                st.write(f"**Decoded Content:** {data}")
                st.session_state.scanning = False
                st.button("Scan Again", key="btn_again")
            else:
                st.error("No valid QR code found. Please try again.")

# ==========================================
# TAB 2: QR CODE GENERATOR
# ==========================================
with tab2:
    st.subheader("Generate QR Code")

    # User input field
    user_input = st.text_input(
        "Enter text or URL to convert into a QR code:", placeholder="https://"
    )

    if st.button("Generate QR Code", key="btn_generate"):
        if user_input.strip() == "":
            st.warning("Please enter some text or a link first!")
        else:
            # Configure and generate the QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(user_input)
            qr.make(fit=True)

            # Create PIL image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert PIL image to bytes so Streamlit can display/download it
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            # Display the generated QR code
            st.image(byte_im, caption="Your Generated QR Code", width=250)

            # Add a button allowing users to download the image
            st.download_button(
                label="📥 Download QR Code Image",
                data=byte_im,
                file_name="generated_qrcode.png",
                mime="image/png",
            )