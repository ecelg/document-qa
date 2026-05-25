import io
import cv2
import numpy as np
import qrcode
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.title("QR Code Toolbox")

# Create the two tabs
tab1, tab2 = st.tabs(["🔍 QR Scanner", "✨ QR Generator"])

# ==========================================
# TAB 1: QR CODE SCANNER (Camera + Upload)
# ==========================================
with tab1:
    st.subheader("Scan or Upload QR Code")

    # --- SECTION A: File Uploader ---
    uploaded_file = st.file_uploader(
        "Upload a QR code image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        # Convert uploaded file to OpenCV format
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        cv2_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Decode
        detector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

        if data:
            st.success("🎉 QR Code Detected From Upload!")
            st.write(f"**Decoded Content:** {data}")
        else:
            st.error(
                "Could not find a valid QR code in this image. Make sure it is clear and unblurred."
            )

    st.divider()  # Visual separation between upload and live camera

    # --- SECTION B: Live Camera Scanner ---
    if "scanning" not in st.session_state:
        st.session_state.scanning = False

    if not st.session_state.scanning:
        if st.button("Open Live Camera Scanner", key="btn_start"):
            st.session_state.scanning = True
            st.rerun()
    else:
        if st.button("Close Live Camera", key="btn_stop"):
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
                st.success("🎉 Live QR Code Detected Successfully!")
                st.write(f"**Decoded Content:** {data}")
                st.session_state.scanning = False
                st.button("Scan Again", key="btn_again")
            else:
                st.error("No valid QR code found in camera frame. Try again.")


# ==========================================
# TAB 2: QR CODE GENERATOR (With Custom Text Size)
# ==========================================
with tab2:
    st.subheader("Generate QR Code")

    user_input = st.text_input(
        "Enter text or URL to convert into a QR code:",
        placeholder="https://",
        key="gen_input",
    )

    # Template Selection UI dropdown
    template_option = st.selectbox(
        "Choose a Template Frame:",
        options=[
            "QR Only",
            "Bottom Banner (SCAN ME)",
            "Top Speech Bubble (SCAN ME)",
            "Bottom Pointer Banner (SCAN ME)",
            "Watch Now Button",
            "Bottom Text (SCAN ME - Borderless)",
        ],
        key="template_select",
    )

    # --- ADDED: Font Size Control Slider ---
    text_size = st.slider("Adjust Text Size:", min_value=12, max_value=48, value=24, step=2)

    # --- UPDATED FONT LOADING BLOCK ---
    try:
        # Attempts to use standard local operating system fonts
        font = ImageFont.truetype("arial.ttf", size=text_size)
    except IOError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", size=text_size)
        except IOError:
            # FIX: Dynamically resizes Pillow's modern default vector engine font
            font = ImageFont.load_default(size=text_size)

    if st.button("Generate QR Code", key="btn_generate"):
        if user_input.strip() == "":
            st.warning("Please enter some text or a link first!")
        else:
            # 1. Generate the foundational raw QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=2,
            )
            qr.add_data(user_input)
            qr.make(fit=True)

            base_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            qr_w, qr_h = base_qr.size

            # --- UPDATED: Load a scalable font family ---
            try:
                # Attempts to use standard system fonts based on OS
                # Windows uses 'arial.ttf', macOS uses 'Arial.ttf', Linux often uses 'DejaVuSans.ttf'
                font = ImageFont.truetype("arial.ttf", size=text_size)
            except IOError:
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", size=text_size)
                except IOError:
                    # Fallback if custom fonts are missing from your current hosting machine
                    st.warning("Custom font not found. Using default system font (un-resizable).")
                    font = ImageFont.load_default()

            # 2. Process the image layout based on selection
            if template_option == "QR Only":
                final_img = base_qr

            elif template_option == "Bottom Banner (SCAN ME)":
                padding = 20
                # Dynamically scale banner height based on font size configuration
                banner_h = int(text_size * 2.2) 
                canvas_w = qr_w + (padding * 2)
                canvas_h = qr_h + (padding * 2) + banner_h

                final_img = Image.new("RGB", (canvas_w, canvas_h), "white")
                draw = ImageDraw.Draw(final_img)

                draw.rectangle([10, 10, canvas_w - 10, canvas_h - 10], outline="black", width=8)
                final_img.paste(base_qr, (padding, padding))
                draw.rectangle(
                    [10, canvas_h - 10 - banner_h, canvas_w - 10, canvas_h - 10],
                    fill="black",
                )
                draw.text(
                    (canvas_w // 2, canvas_h - 10 - (banner_h // 2)),
                    "SCAN ME",
                    fill="white",
                    font=font,
                    anchor="mm",
                )

            elif template_option == "Top Speech Bubble (SCAN ME)":
                bubble_h = int(text_size * 2.0)
                padding = 20
                canvas_w = qr_w + (padding * 2)
                canvas_h = qr_h + (padding * 2) + bubble_h

                final_img = Image.new("RGB", (canvas_w, canvas_h), "white")
                draw = ImageDraw.Draw(final_img)

                draw.rectangle(
                    [padding, padding + bubble_h, canvas_w - padding, canvas_h - padding],
                    outline="black",
                    width=6,
                )
                final_img.paste(base_qr, (padding, padding + bubble_h))

                b_left, b_top, b_right, b_bottom = (
                    padding + 10,
                    10,
                    canvas_w - padding - 10,
                    10 + bubble_h,
                )
                draw.rounded_rectangle(
                    [b_left, b_top, b_right, b_bottom], radius=10, fill="black"
                )
                draw.polygon(
                    [
                        (canvas_w // 2 - 10, b_bottom),
                        (canvas_w // 2 + 10, b_bottom),
                        (canvas_w // 2, b_bottom + 10),
                    ],
                    fill="black",
                )
                draw.text(
                    (canvas_w // 2, (b_top + b_bottom) // 2),
                    "SCAN ME",
                    fill="white",
                    font=font,
                    anchor="mm",
                )

            elif template_option == "Bottom Pointer Banner (SCAN ME)":
                padding = 20
                banner_h = int(text_size * 2.0)
                gap = 25
                canvas_w = qr_w + (padding * 2)
                canvas_h = qr_h + padding + gap + banner_h

                final_img = Image.new("RGB", (canvas_w, canvas_h), "white")
                draw = ImageDraw.Draw(final_img)

                draw.rectangle([padding, padding, canvas_w - padding, qr_h + padding], outline="black", width=6)
                final_img.paste(base_qr, (padding, padding))

                b_top = qr_h + padding + gap
                draw.rounded_rectangle(
                    [padding, b_top, canvas_w - padding, b_top + banner_h],
                    radius=8,
                    fill="black",
                )
                draw.polygon(
                    [
                        (canvas_w // 2 - 12, b_top),
                        (canvas_w // 2 + 12, b_top),
                        (canvas_w // 2, b_top - 12),
                    ],
                    fill="black",
                )
                draw.text(
                    (canvas_w // 2, b_top + (banner_h // 2)),
                    "SCAN ME",
                    fill="white",
                    font=font,
                    anchor="mm",
                )

            elif template_option == "Watch Now Button":
                padding = 20
                btn_h = int(text_size * 1.8)
                gap = 15
                canvas_w = qr_w + (padding * 2)
                canvas_h = qr_h + padding + gap + btn_h

                final_img = Image.new("RGB", (canvas_w, canvas_h), "white")
                draw = ImageDraw.Draw(final_img)

                draw.rectangle([padding, padding, canvas_w - padding, qr_h + padding], outline="black", width=6)
                final_img.paste(base_qr, (padding, padding))

                b_top = qr_h + padding + gap
                draw.rounded_rectangle(
                    [padding + 20, b_top, canvas_w - padding - 20, b_top + btn_h],
                    radius=20,
                    fill="black",
                )

                # Responsive icon geometry sizing offset points
                p_center_x = padding + 45
                p_center_y = b_top + (btn_h // 2)
                icon_scale = int(text_size * 0.35)
                draw.polygon(
                    [
                        (p_center_x - icon_scale, p_center_y - icon_scale),
                        (p_center_x + int(icon_scale * 1.2), p_center_y),
                        (p_center_x - icon_scale, p_center_y + icon_scale),
                    ],
                    fill="white",
                )
                draw.text(
                    (canvas_w // 2 + 10, b_top + (btn_h // 2)),
                    "WATCH NOW",
                    fill="white",
                    font=font,
                    anchor="mm",
                )

            elif template_option == "Bottom Text (SCAN ME - Borderless)":
                text_h = int(text_size * 2.0)
                canvas_w = qr_w
                canvas_h = qr_h + text_h

                final_img = Image.new("RGB", (canvas_w, canvas_h), "white")
                draw = ImageDraw.Draw(final_img)

                final_img.paste(base_qr, (0, 0))
                draw.text(
                    (canvas_w // 2, qr_h + (text_h // 2)),
                    "SCAN ME",
                    fill="black",
                    font=font,
                    anchor="mm",
                )

            # 3. Output logic
            buf = io.BytesIO()
            final_img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.image(byte_im, caption=f"Template: {template_option}", width=250)

            st.download_button(
                label="📥 Download Structured QR Image",
                data=byte_im,
                file_name=f"qr_{template_option.lower().replace(' ', '_')}.png",
                mime="image/png",
                key="download_templated_qr",
            )