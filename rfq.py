import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF
import tempfile
import os
from PIL import Image
import io

# --- App Configuration ---
st.set_page_config(
    page_title="RFQ Generator",
    page_icon="🏭",
    layout="wide"
)

# --- PDF Generation Function (Handles both RFQ types) ---
def create_advanced_rfq_pdf(data):
    """
    Generates a professional RFQ document for either Item or Storage Infrastructure.
    """
    class PDF(FPDF):
        def create_cover_page(self, data):
            logo1_data = data.get('logo1_data')
            logo1_w = data.get('logo1_w', 35); logo1_h = data.get('logo1_h', 20)
            if logo1_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo1_data); tmp.flush()
                    self.image(tmp.name, x=self.l_margin, y=20, w=logo1_w, h=logo1_h)
                    os.remove(tmp.name)
            self.set_y(40); self.set_x(self.l_margin); self.set_font('Arial', 'B', 14); self.set_text_color(255, 0, 0)
            self.cell(0, 10, 'CONFIDENTIAL'); self.set_text_color(0, 0, 0)
            logo2_data = data.get('logo2_data')
            logo2_w = data.get('logo2_w', 42); logo2_h = data.get('logo2_h', 20)
            if logo2_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo2_data); tmp.flush()
                    logo2_path = tmp.name
                x_pos = self.w - self.r_margin - logo2_w
                self.image(logo2_path, x=x_pos, y=20, w=logo2_w, h=logo2_h)
                os.remove(logo2_path)
            self.set_y(60); self.set_font('Arial', 'B', 30); self.cell(0, 15, 'Request for Quotation', 0, 1, 'C'); self.ln(5)
            self.set_font('Arial', '', 18); self.cell(0, 8, 'For', 0, 1, 'C'); self.ln(3)
            self.set_font('Arial', 'B', 22); self.cell(0, 8, data['Type_of_items'], 0, 1, 'C'); self.ln(5)
            self.set_font('Arial', '', 18); self.cell(0, 8, 'for', 0, 1, 'C'); self.ln(3)
            self.set_font('Arial', 'B', 22); self.cell(0, 8, data['Storage'], 0, 1, 'C'); self.ln(5)
            self.set_font('Arial', '', 18); self.cell(0, 8, 'At', 0, 1, 'C'); self.ln(3)
            self.set_font('Arial', 'B', 24); self.cell(0, 10, data['company_name'], 0, 1, 'C'); self.ln(3)
            self.set_font('Arial', '', 22); self.cell(0, 10, data['company_address'], 0, 1, 'C')

        def header(self):
            if self.page_no() == 1: return
            logo1_data = data.get('logo1_data')
            logo1_w, logo1_h = data.get('logo1_w', 35), data.get('logo1_h', 20)
            if logo1_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo1_data); tmp.flush()
                    self.image(tmp.name, x=self.l_margin, y=10, w=logo1_w, h=logo1_h)
                    os.remove(tmp.name)
            logo2_data = data.get('logo2_data')
            logo2_w, logo2_h = data.get('logo2_w', 42), data.get('logo2_h', 20)
            if logo2_data:
                x_pos = self.w - self.r_margin - logo2_w
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo2_data); tmp.flush()
                    self.image(tmp.name, x=x_pos, y=10, w=logo2_w, h=logo2_h)
                    os.remove(tmp.name)
            self.set_y(12); self.set_font('Arial', 'B', 16); self.cell(0, 10, 'Request for Quotation (RFQ)', 0, 1, 'C')
            self.set_font('Arial', 'I', 10); self.cell(0, 6, f"For: {data['Type_of_items']}", 0, 1, 'C'); self.ln(15)

        def footer(self):
            self.set_y(-25)
            footer_name, footer_addr = data.get('footer_company_name'), data.get('footer_company_address')
            if footer_name or footer_addr:
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y()); self.ln(3); self.set_text_color(128)
                if footer_name: self.set_font('Arial', 'B', 14); self.cell(0, 5, footer_name, 0, 1, 'C')
                if footer_addr: self.set_font('Arial', '', 8); self.cell(0, 5, footer_addr, 0, 1, 'C')
                self.set_text_color(0)
            self.set_y(-15); self.set_font('Arial', 'I', 8); self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

        def section_title(self, title):
            self.set_font('Arial', 'B', 12); self.set_fill_color(230, 230, 230); self.cell(0, 8, title, 0, 1, 'L', fill=True); self.ln(4)

    pdf = PDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.create_cover_page(data)
    pdf.add_page()

    pdf.section_title('REQUIREMENT BACKGROUND')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, data['purpose'], border=0, align='L')
    pdf.ln(5)

    pdf.section_title('TECHNICAL SPECIFICATION')

    if data['rfq_type'] == 'Item':
        pdf.set_font('Arial', 'B', 11); pdf.cell(0, 8, 'BIN DETAILS', 0, 1, 'L');
        bin_headers = ["Type\nof Bin", "Bin Outer\nDimension (MM)", "Bin Inner\nDimension (MM)", "Conceptual\nImage", "Qty Bin"]
        bin_col_widths = [36, 38, 38, 44, 34]
        row_height = 32
        header_height = 16
        pdf.set_font('Arial', 'B', 10)
        y_start_header = pdf.get_y()
        line_height_header = 6
        current_x_header = pdf.l_margin
        for i, header in enumerate(bin_headers):
            pdf.rect(current_x_header, y_start_header, bin_col_widths[i], header_height)
            num_lines = header.count('\n') + 1
            y_text_header = y_start_header + (header_height - num_lines * line_height_header) / 2
            pdf.set_xy(current_x_header, y_text_header)
            pdf.multi_cell(bin_col_widths[i], line_height_header, header, align='C')
            current_x_header += bin_col_widths[i]
        pdf.set_y(y_start_header + header_height)
        pdf.set_font('Arial', '', 10)
        line_height_row = 6
        bin_df = data['bin_details_df']
        num_bin_rows = len(bin_df) if not bin_df.empty else 4
        for i in range(num_bin_rows):
            row_y_start = pdf.get_y()
            if pdf.get_y() + row_height > pdf.page_break_trigger: pdf.add_page()
            row_data = bin_df.iloc[i] if i < len(bin_df) else {}
            row_contents = [
                str(row_data.get('Type of Bin', '')), str(row_data.get('Bin Outer Dimension (MM)', '')),
                str(row_data.get('Bin Inner Dimension (MM)', '')), '', str(row_data.get('Qty Bin', ''))
            ]
            current_x = pdf.l_margin
            text_y = row_y_start + (row_height - line_height_row) / 2
            for j, content in enumerate(row_contents):
                width = bin_col_widths[j]
                pdf.rect(current_x, row_y_start, width, row_height)
                if j == 3:
                    image_data = row_data.get('image_data_bytes')
                    if isinstance(image_data, bytes):
                        try:
                            img = Image.open(io.BytesIO(image_data))
                            img_w, img_h = img.size; aspect_ratio = img_w / img_h
                            padding = 1; cell_inner_w = width - 2 * padding; cell_inner_h = row_height - 2 * padding
                            img_display_w = cell_inner_w; img_display_h = img_display_w / aspect_ratio
                            if img_display_h > cell_inner_h:
                                img_display_h = cell_inner_h; img_display_w = img_display_h * aspect_ratio
                            img_x = current_x + (width - img_display_w) / 2; img_y = row_y_start + (row_height - img_display_h) / 2
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                                img.save(tmp.name, format='PNG'); pdf.image(tmp.name, x=img_x, y=img_y, w=img_display_w, h=img_display_h)
                                os.remove(tmp.name)
                        except Exception: pass
                else:
                    pdf.set_xy(current_x, text_y); pdf.multi_cell(width, line_height_row, content, align='C')
                current_x += width
            pdf.set_y(row_y_start + row_height)
        pdf.ln(8)

        def add_bullet_point(key, value):
            if value and str(value).strip() and value not in ['N/A', '']:
                if pdf.get_y() + 12 > pdf.page_break_trigger: pdf.add_page()
                start_y = pdf.get_y(); pdf.set_x(pdf.l_margin); pdf.set_font('Arial', '', 12); pdf.cell(5, 6, chr(127))
                pdf.set_font('Arial', 'B', 12); pdf.cell(55, 6, f"{key}:")
                key_end_y = pdf.get_y() + 6; value_start_x = pdf.l_margin + 60; value_width = pdf.w - pdf.r_margin - value_start_x
                pdf.set_xy(value_start_x, start_y); pdf.set_font('Arial', '', 12); pdf.multi_cell(value_width, 6, str(value), 0, 'L')
                value_end_y = pdf.get_y(); pdf.set_y(max(key_end_y, value_end_y)); pdf.ln(1)

        add_bullet_point('Color', data.get('color'))
        add_bullet_point('Weight Carrying Capacity', f"{data.get('capacity', 0):.2f} KG" if data.get('capacity') else None)
        add_bullet_point('Lid Required', data.get('lid'))
        label_info = f"{data['label_space']} (Size: {data['label_size']})" if data.get('label_space') == 'Yes' else data.get('label_space')
        add_bullet_point('Space for Label', label_info)
        add_bullet_point('Stacking - Static', data.get('stack_static'))
        add_bullet_point('Stacking - Dynamic', data.get('stack_dynamic'))
        pdf.ln(5)

    elif data['rfq_type'] == 'Storage Infrastructure':
        pdf.set_font('Arial', 'B', 11); pdf.cell(0, 8, 'RACK DETAILS', 0, 1, 'L')
        rack_headers = ["Types of \nRack", "Rack \nDimension(MM)", "Level/Rack", "Type of \nBin", "Bin \nDimension(MM)", "Level/Bin"]
        rack_col_widths = [34, 34.5, 29.5, 30, 34.5, 27.5]
        header_height = 16
        line_height_header = 6
        pdf.set_font('Arial', 'B', 10)
        y_start_header = pdf.get_y()
        current_x_header = pdf.l_margin
        for i, header in enumerate(rack_headers):
            pdf.rect(current_x_header, y_start_header, rack_col_widths[i], header_height)
            num_lines = header.count('\n') + 1
            y_text_header = y_start_header + (header_height - num_lines * line_height_header) / 2
            pdf.set_xy(current_x_header, y_text_header)
            pdf.multi_cell(rack_col_widths[i], line_height_header, header, align='C', border=0)
            current_x_header += rack_col_widths[i]
        pdf.set_y(y_start_header + header_height)
        pdf.set_font('Arial', '', 10)
        
        rack_df = data['rack_details_df']
        if not rack_df.empty:
            for _, row_data in rack_df.iterrows():
                if pdf.get_y() + 10 > pdf.page_break_trigger: pdf.add_page()
                pdf.cell(rack_col_widths[0], 10, str(row_data.get('Types of Rack', '')), border=1, align='C')
                pdf.cell(rack_col_widths[1], 10, str(row_data.get('Rack Dimension (MM)', '')), border=1, align='C')
                pdf.cell(rack_col_widths[2], 10, str(row_data.get('Level/Rack', '')), border=1, align='C')
                pdf.cell(rack_col_widths[3], 10, str(row_data.get('Type of Bin', '')), border=1, align='C')
                pdf.cell(rack_col_widths[4], 10, str(row_data.get('Bin Dimension (MM)', '')), border=1, align='C')
                pdf.cell(rack_col_widths[5], 10, str(row_data.get('Level/Bin', '')), border=1, align='C', ln=1)
        else:
            pdf.cell(sum(rack_col_widths), 10, "No rack details provided.", border=1, align='C', ln=1)
        pdf.ln(8)
        
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 8, 'Key Inputs:', 0, 1, 'L'); pdf.ln(2)
        key_inputs_df = data['key_inputs_df']
        if not key_inputs_df.empty:
            for index, row in key_inputs_df.iterrows():
                if not row['Input Text']: continue
                if pdf.get_y() + 20 > pdf.page_break_trigger: pdf.add_page()
                pdf.set_font('Arial', 'B', 11)
                pdf.multi_cell(0, 6, f"{index + 1}. {row['Input Text']}", 0, 'L')
                pdf.ln(3)
                image_data = row.get('image_data_bytes')
                if isinstance(image_data, bytes):
                    try:
                        img = Image.open(io.BytesIO(image_data)); img_w, img_h = img.size
                        aspect_ratio = img_h / img_w
                        available_width = pdf.w - pdf.l_margin - pdf.r_margin
                        img_display_w = available_width
                        img_display_h = img_display_w * aspect_ratio
                        
                        max_img_height = (pdf.h - pdf.t_margin - pdf.b_margin) * 0.45 
                        if img_display_h > max_img_height:
                            img_display_h = max_img_height
                            img_display_w = img_display_h / aspect_ratio
                        
                        safety_margin = 5
                        if pdf.get_y() + img_display_h + safety_margin > pdf.page_break_trigger:
                            pdf.add_page()

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                            img.save(tmp.name, format='PNG')
                            pdf.image(tmp.name, x=pdf.l_margin, y=pdf.get_y(), w=img_display_w, h=img_display_h)
                            os.remove(tmp.name)
                        pdf.set_y(pdf.get_y() + img_display_h + 8)
                    except Exception: pdf.ln(5)
                else: pdf.ln(5)
        
    timeline_data = [("Date of RFQ Release", data['date_release']),("Query Resolution Deadline", data['date_query']),("Negotiation & Vendor Selection", data['date_selection']),("Delivery Deadline", data['date_delivery']),("Installation Deadline", data['date_install'])]
    if data.get('date_meet') and pd.notna(data['date_meet']): timeline_data.append(("Face to Face Meet", data['date_meet']))
    if data.get('date_quote') and pd.notna(data['date_quote']): timeline_data.append(("First Level Quotation", data['date_quote']))
    if data.get('date_review') and pd.notna(data['date_review']): timeline_data.append(("Joint Review of Quotation", data['date_review']))
    height_needed = 12 + 8 + 8
    if pdf.get_y() + height_needed > pdf.page_break_trigger: pdf.add_page()
    pdf.section_title('TIMELINES')
    pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Milestone', 1, 0, 'C'); pdf.cell(110, 8, 'Date', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for item, date_val in timeline_data:
        if date_val and pd.notna(date_val):
            if pdf.get_y() + 8 > pdf.page_break_trigger: pdf.add_page(); pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Milestone', 1, 0, 'C'); pdf.cell(110, 8, 'Date', 1, 1, 'C'); pdf.set_font('Arial', '', 10)
            pdf.cell(80, 8, item, 1, 0, 'L'); pdf.cell(110, 8, date_val.strftime('%B %d, %Y'), 1, 1, 'L')
    pdf.ln(5)
    height_needed = 12 + 25
    if pdf.get_y() + height_needed > pdf.page_break_trigger: pdf.add_page()
    pdf.section_title('SINGLE POINT OF CONTACT')
    def draw_contact_column(title, name, designation, phone, email):
        col_start_x = pdf.get_x(); pdf.set_font('Arial', 'BU', 10); pdf.multi_cell(90, 6, title, 0, 'L'); pdf.ln(1)
        def draw_kv_row(key, value):
            key_str = str(key).encode('latin-1', 'replace').decode('latin-1'); value_str = str(value).encode('latin-1', 'replace').decode('latin-1')
            row_start_y = pdf.get_y(); pdf.set_x(col_start_x); pdf.set_font('Arial', 'B', 10); pdf.cell(25, 6, key_str, 0, 0, 'L')
            pdf.set_xy(col_start_x + 25, row_start_y); pdf.set_font('Arial', '', 10); pdf.multi_cell(65, 6, value_str, 0, 'L')
        draw_kv_row("Name:", name); draw_kv_row("Designation:", designation); draw_kv_row("Phone No:", phone); draw_kv_row("Email ID:", email)
    start_y = pdf.get_y(); pdf.set_xy(pdf.l_margin, start_y); draw_contact_column('Primary Contact', data['spoc1_name'], data['spoc1_designation'], data['spoc1_phone'], data['spoc1_email'])
    end_y1 = pdf.get_y()
    if data.get('spoc2_name'):
        pdf.set_xy(pdf.l_margin + 98, start_y); draw_contact_column('Secondary Contact', data['spoc2_name'], data['spoc2_designation'], data['spoc2_phone'], data['spoc2_email']); end_y2 = pdf.get_y()
        pdf.set_y(max(end_y1, end_y2))
    else: pdf.set_y(end_y1)
    pdf.ln(5)
    height_needed = 12 + 12 + 8 + 8
    if pdf.get_y() + height_needed > pdf.page_break_trigger: pdf.add_page()
    pdf.section_title('COMMERCIAL REQUIREMENTS')
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 6, "Please provide a detailed cost breakup in the format below. All costs should be inclusive of taxes and duties as applicable.", 0, 'L'); pdf.ln(4)
    pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Cost Component', 1, 0, 'C'); pdf.cell(40, 8, 'Amount', 1, 0, 'C'); pdf.cell(70, 8, 'Remarks', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for index, row in data['commercial_df'].iterrows():
        if pdf.get_y() + 8 > pdf.page_break_trigger: pdf.add_page(); pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Cost Component', 1, 0, 'C'); pdf.cell(40, 8, 'Amount', 1, 0, 'C'); pdf.cell(70, 8, 'Remarks', 1, 1, 'C'); pdf.set_font('Arial', '', 10)
        component = str(row['Cost Component']).encode('latin-1', 'replace').decode('latin-1'); remarks = str(row['Remarks']).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(80, 8, component, 1, 0, 'L'); pdf.cell(40, 8, '', 1, 0); pdf.cell(70, 8, remarks, 1, 1, 'L')
    pdf.ln(10)
    if pdf.get_y() + 90 > pdf.page_break_trigger: pdf.add_page()
    if data.get('submit_to_name'):
        pdf.set_font('Arial', 'B', 12); pdf.cell(5, 8, chr(149)); pdf.cell(0, 8, 'Quotation to be Submit to:', 0, 1); pdf.ln(5)
        pdf.set_x(pdf.l_margin + 15); pdf.set_font('Arial', '', 12)
        hex_color = data.get('submit_to_color', '#DC3232').lstrip('#'); r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        pdf.set_text_color(r, g, b); pdf.multi_cell(0, 7, data.get('submit_to_name', '')); pdf.set_text_color(0, 0, 0); pdf.ln(1)
        if data.get('submit_to_registered_office'):
            pdf.set_x(pdf.l_margin + 15); pdf.set_font('Arial', '', 10); pdf.set_text_color(128, 128, 128)
            pdf.multi_cell(0, 6, data.get('submit_to_registered_office', ''), 0, 'L'); pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    if data.get('delivery_location'):
        pdf.set_font('Arial', 'B', 12); pdf.cell(5, 8, chr(149)); pdf.cell(0, 8, 'Delivery Location:', 0, 1); pdf.ln(2)
        pdf.set_font('Arial', '', 11); pdf.set_x(pdf.l_margin + 5); pdf.multi_cell(0, 6, data.get('delivery_location'), 0, 'L')
    pdf.ln(10)
    if data.get('annexures'):
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 8, 'ANNEXURES', 0, 1); pdf.ln(2)
        pdf.set_font('Arial', '', 11); pdf.set_x(pdf.l_margin + 5); pdf.multi_cell(0, 6, data.get('annexures'), 0, 'L')
    return bytes(pdf.output())

# --- STREAMLIT APP ---
st.title("🏭 Request For Quotation Generator")
st.markdown("---")

with st.expander("Step 1: Upload Company Logos & Set Dimensions (Optional)", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        logo1_file = st.file_uploader("Upload Company Logo 1 (Left Side)", type=['png', 'jpg', 'jpeg'], key="logo1")
        logo1_w = st.number_input("Logo 1 Width (mm)", 5, 50, 30, 1)
        logo1_h = st.number_input("Logo 1 Height (mm)", 5, 50, 15, 1)
    with c2:
        logo2_file = st.file_uploader("Upload Company Logo 2 (Right Side)", type=['png', 'jpg', 'jpeg'], key="logo2")
        logo2_w = st.number_input("Logo 2 Width (mm)", 5, 50, 30, 1)
        logo2_h = st.number_input("Logo 2 Height (mm)", 5, 50, 15, 1)

with st.expander("Step 2: Add Cover Page Details", expanded=True):
    Type_of_items = st.text_input("Type of Items*", help="e.g., Plastic Blue Bins OR Line Side Racks")
    Storage = st.text_input("Storage Type*", help="e.g., Material Storage")
    company_name = st.text_input("Requester Company Name*", help="e.g., Pinnacle Mobility Solutions Pvt. Ltd")
    company_address = st.text_input("Requester Company Address*", help="e.g., Nanekarwadi, Chakan, Pune 410501")

with st.expander("Step 3: Add Footer Details (Optional)", expanded=True):
    footer_company_name = st.text_input("Footer Company Name", help="e.g., Your Company Private Ltd")
    footer_company_address = st.text_input("Footer Company Address", help="e.g., Registered Office: 123 Business Rd, Commerce City")

st.subheader("Step 4: Fill Core RFQ Details")

rfq_type = st.radio( "Select RFQ Type:", ('Item', 'Storage Infrastructure'), horizontal=True, key='rfq_type_selector')
st.markdown("---")

if rfq_type == 'Item':
    with st.expander("Technical Specifications", expanded=True):
        st.info("Define the items for the vendor. Add or remove rows in the table; the image uploaders will update automatically.")
        st.markdown("##### Bin Details")
        if 'bin_df' not in st.session_state:
            st.session_state.bin_df = pd.DataFrame([{"Type of Bin": "TOTE", "Bin Outer Dimension (MM)": "600x400x300", "Bin Inner Dimension (MM)": "580x380x280", "Conceptual Image": None, "Qty Bin": 150}])
        st.markdown("###### Edit Bin Details and Upload Images per Row")
        st.info("ℹ️ Double-click a cell to edit. Use the `+` button at the bottom of the table to add more bin types.")
        editor_col, uploader_col = st.columns([3, 2])
        with editor_col:
            edited_bin_df = st.data_editor(st.session_state.bin_df, num_rows="dynamic", use_container_width=True, column_config={"Type of Bin": st.column_config.TextColumn(required=True), "Bin Outer Dimension (MM)": st.column_config.TextColumn(), "Bin Inner Dimension (MM)": st.column_config.TextColumn(), "Qty Bin": st.column_config.NumberColumn(), "Conceptual Image": st.column_config.ImageColumn("Image Preview")}, key="bin_df_editor")
        with uploader_col:
            st.write("**Upload Images**")
            for i in range(len(edited_bin_df)):
                bin_type = edited_bin_df.iloc[i]["Type of Bin"]
                label = f"Upload for '{bin_type}'" if bin_type else f"Upload for row {i+1}"
                uploaded_file = st.file_uploader(label, type=['png', 'jpg', 'jpeg'], key=f"image_uploader_{i}")
                if uploaded_file is not None:
                    edited_bin_df.at[i, 'Conceptual Image'] = uploaded_file.getvalue()
        st.session_state.bin_df = edited_bin_df
        st.markdown("---"); st.markdown("##### General Specifications"); c1, c2 = st.columns(2)
        with c1:
            color = st.text_input("Color"); capacity = st.number_input("Weight Carrying Capacity (KG)", 0.0, 1000.0, 0.0, format="%.2f")
            lid = st.radio("Lid Required?", ["Yes", "No", "N/A"], index=2, horizontal=True)
        with c2:
            label_space = st.radio("Space for Label?", ["Yes", "No", "N/A"], index=2, horizontal=True); label_size = "N/A"
            if label_space == "Yes": label_size = st.text_input("Label Size (e.g., 80*50)", "")
        st.markdown("###### Stacking Requirements (if applicable)"); c1, c2 = st.columns(2)
        stack_static = c1.text_input("Static (e.g., 1+3)"); stack_dynamic = c2.text_input("Dynamic (e.g., 1+1)")

elif rfq_type == 'Storage Infrastructure':
    with st.expander("Technical Specifications", expanded=True):
        st.markdown("##### Rack Details")
        
        # --- FIX FOR ALL COLUMNS NOT EDITING ---
        # Initialize the DataFrame with all columns explicitly set to string type.
        # This prevents Streamlit/Pandas from inferring a numeric type for empty columns,
        # which would make them non-editable for text input like "600x400".
        if 'rack_df' not in st.session_state or st.session_state.rack_df.empty:
            rack_data = {
                "Types of Rack": [""],
                "Rack Dimension (MM)": [""],
                "Level/Rack": [""],
                "Type of Bin": [""],
                "Bin Dimension (MM)": [""],
                "Level/Bin": [""]
            }
            st.session_state.rack_df = pd.DataFrame(rack_data).astype(str)

        st.info("ℹ️ Double-click any cell to edit. Use the `+` button at the bottom of the table to add more rack types.")
        
        edited_rack_df = st.data_editor(
            st.session_state.rack_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Types of Rack": st.column_config.TextColumn(required=True),
                "Rack Dimension (MM)": st.column_config.TextColumn(),
                "Level/Rack": st.column_config.TextColumn(),
                "Type of Bin": st.column_config.TextColumn(),
                "Bin Dimension (MM)": st.column_config.TextColumn(),
                "Level/Bin": st.column_config.TextColumn()
            },
            key="rack_df_editor"
        )
        st.session_state.rack_df = edited_rack_df
        
        st.markdown("---"); st.markdown("##### Key Inputs")
        if 'key_inputs_df' not in st.session_state or st.session_state.key_inputs_df.empty:
            st.session_state.key_inputs_df = pd.DataFrame([{"Input Text": "", "Upload Image?": False, "Image Data": None}])
        
        st.info("ℹ️ Describe each key requirement below. Check the box to enable the image uploader for that row. Use the `+` button to add more inputs.")
        
        edited_key_inputs_df = st.data_editor(
            st.session_state.key_inputs_df,
            num_rows="dynamic", use_container_width=True,
            column_config={"Input Text": st.column_config.TextColumn(width="large", required=True), "Upload Image?": st.column_config.CheckboxColumn(default=False), "Image Data": None},
            key="key_inputs_editor"
        )
        
        for i, row in edited_key_inputs_df.iterrows():
            if row["Upload Image?"]:
                input_text = row["Input Text"]
                label = f"Upload for '{input_text}'" if input_text else f"Upload for key input #{i+1}"
                uploaded_file = st.file_uploader(label, type=['png', 'jpg', 'jpeg'], key=f"key_input_uploader_{i}")
                if uploaded_file is not None:
                    edited_key_inputs_df.at[i, 'Image Data'] = uploaded_file.getvalue()
        st.session_state.key_inputs_df = edited_key_inputs_df

with st.form(key="advanced_rfq_form"):
    purpose = st.text_area("Purpose of Requirement*", max_chars=300, height=100)
    with st.expander("Timelines"):
        today = date.today()
        c1, c2, c3 = st.columns(3); date_release = c1.date_input("Date of RFQ Release *", today)
        date_query = c1.date_input("Query Resolution Deadline *", today + timedelta(days=7)); date_meet = c1.date_input("Face to Face Meet", None)
        date_selection = c2.date_input("Negotiation & Vendor Selection *", today + timedelta(days=30)); date_delivery = c2.date_input("Delivery Deadline *", today + timedelta(days=60))
        date_quote = c2.date_input("First Level Quotation", None); date_install = c3.date_input("Installation Deadline *", today + timedelta(days=75))
        date_review = c3.date_input("Joint Review of Quotation", None)
    with st.expander("Single Point of Contact (SPOC)"):
        st.markdown("##### Primary Contact*"); c1, c2 = st.columns(2); spoc1_name = c1.text_input("Name*", key="s1n")
        spoc1_designation = c1.text_input("Designation", key="s1d"); spoc1_phone = c2.text_input("Phone No*", key="s1p")
        spoc1_email = c2.text_input("Email ID*", key="s1e"); st.markdown("##### Secondary Contact (Optional)"); c1, c2 = st.columns(2)
        spoc2_name = c1.text_input("Name", key="s2n"); spoc2_designation = c1.text_input("Designation", key="s2d")
        spoc2_phone = c2.text_input("Phone No", key="s2p"); spoc2_email = c2.text_input("Email ID", key="s2e")
    with st.expander("Commercial Requirements"):
        edited_commercial_df = st.data_editor(
            pd.DataFrame([
                {"Cost Component": "Unit Cost", "Remarks": "Per item/unit specified in Section 2."}, {"Cost Component": "Freight", "Remarks": "Specify if included or extra."},
                {"Cost Component": "Any other Handling Cost", "Remarks": ""}, {"Cost Component": "Total Basic Cost (Per Unit)", "Remarks": ""}
            ]), num_rows="dynamic", use_container_width=True
        )
    with st.expander("Submission, Delivery & Annexures"):
        st.markdown("##### Quotation Submission Details*"); submit_to_name = st.text_input("Submit To (Company Name)*", "Agilomatrix Pvt. Ltd.")
        submit_to_color = st.color_picker("Company Name Color", "#DC3232")
        submit_to_registered_office = st.text_input("Submit To (Registered Office Address)", "Registered Office: F1403, 7 Plumeria Drive, 7PD Street, Tathawade, Pune - 411033")
        st.markdown("---"); st.markdown("##### Delivery & Annexures*"); delivery_location = st.text_area("Delivery Location Address*", height=100)
        annexures = st.text_area("Annexures (one item per line)", height=100)

    submitted = st.form_submit_button("Generate RFQ Document", use_container_width=True, type="primary")

if submitted:
    if not all([purpose, spoc1_name, spoc1_phone, spoc1_email, company_name, company_address, Type_of_items, Storage, submit_to_name, delivery_location]):
        st.error("⚠️ Please fill in all mandatory (*) fields.")
    else:
        with st.spinner("Generating PDF..."):
            rfq_data = {
                'rfq_type': rfq_type, 'Type_of_items': Type_of_items, 'Storage': Storage, 'company_name': company_name,
                'company_address': company_address, 'footer_company_name': footer_company_name, 'footer_company_address': footer_company_address,
                'logo1_data': logo1_file.getvalue() if logo1_file else None, 'logo2_data': logo2_file.getvalue() if logo2_file else None,
                'logo1_w': logo1_w, 'logo1_h': logo1_h, 'logo2_w': logo2_w, 'logo2_h': logo2_h, 'purpose': purpose,
                'date_release': date_release, 'date_query': date_query, 'date_selection': date_selection, 'date_delivery': date_delivery,
                'date_install': date_install, 'date_meet': date_meet, 'date_quote': date_quote, 'date_review': date_review,
                'spoc1_name': spoc1_name, 'spoc1_designation': spoc1_designation, 'spoc1_phone': spoc1_phone, 'spoc1_email': spoc1_email,
                'spoc2_name': spoc2_name, 'spoc2_designation': spoc2_designation, 'spoc2_phone': spoc2_phone, 'spoc2_email': spoc2_email,
                'commercial_df': edited_commercial_df, 'submit_to_name': submit_to_name, 'submit_to_color': submit_to_color,
                'submit_to_registered_office': submit_to_registered_office, 'delivery_location': delivery_location, 'annexures': annexures,
            }

            if rfq_type == 'Item':
                df_to_process = st.session_state.bin_df.dropna(subset=["Type of Bin"]).copy()
                df_to_process = df_to_process[df_to_process["Type of Bin"].str.strip() != ""]
                rfq_data['bin_details_df'] = df_to_process.rename(columns={"Conceptual Image": "image_data_bytes"})
                rfq_data.update({'color': color, 'capacity': capacity, 'lid': lid, 'label_space': label_space, 'label_size': label_size,
                                 'stack_static': stack_static, 'stack_dynamic': stack_dynamic})
            elif rfq_type == 'Storage Infrastructure':
                df_rack = st.session_state.rack_df.dropna(subset=["Types of Rack"]).copy()
                rfq_data['rack_details_df'] = df_rack[df_rack["Types of Rack"].str.strip() != ""]
                
                df_key = st.session_state.key_inputs_df.dropna(subset=["Input Text"]).copy()
                rfq_data['key_inputs_df'] = df_key[df_key["Input Text"].str.strip() != ""].rename(columns={"Image Data": "image_data_bytes"})

            pdf_data = create_advanced_rfq_pdf(rfq_data)

        st.success("✅ RFQ PDF Generated Successfully!")
        file_name = f"RFQ_{Type_of_items.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        st.download_button(label="📥 Download RFQ Document", data=pdf_data, file_name=file_name, mime="application/pdf", use_container_width=True, type="primary")
