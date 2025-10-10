import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF
import tempfile
import os

# --- App Configuration ---
st.set_page_config(
    page_title="RFQ Generator",
    page_icon="🏭",
    layout="wide"
)

# --- PDF Generation Function (Final, Corrected Version) ---
def create_advanced_rfq_pdf(data):
    """
    Generates a professional RFQ document with clean, standard tabular layouts.
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
            if self.get_y() + 20 > self.page_break_trigger: self.add_page()
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

    # --- START: NEW CLEAN TABLE-BASED TECHNICAL SPECIFICATION SECTION ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'TECHNICAL SPECIFICATION', 0, 1, 'L'); pdf.ln(4)

    # --- Bin Details Table ---
    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 8, 'BIN DETAILS', 0, 1, 'L');
    pdf.set_font('Arial', 'B', 12)
    bin_headers = ["Type\nof Bin", "Bin Outer\nDimension (MM)", "Bin Inner\nDimension (MM)", "Conceptual\nImage", "Qty Bin"]
    bin_col_widths = [40, 38, 38, 37, 37]

    total_header_height = 16
    line_height = 8
    y_start = pdf.get_y()
    x_cursor = pdf.l_margin

    for i, header in enumerate(bin_headers):
        col_width = bin_col_widths[i]
        num_lines = header.count('\n') + 1
        text_height = num_lines * line_height
        y_text = y_start + (total_header_height - text_height) / 2
        pdf.set_xy(x_cursor, y_text)
        pdf.multi_cell(col_width, line_height, header, border=0, align='C')
        pdf.rect(x_cursor, y_start, col_width, total_header_height)
        x_cursor += col_width

    pdf.set_xy(pdf.l_margin, y_start + total_header_height)

    pdf.set_font('Arial', '', 10)
    num_bin_rows = max(4, len(data['bin_details_df']))
    for i in range(num_bin_rows):
        row_data = data['bin_details_df'].iloc[i] if i < len(data['bin_details_df']) else {}
        pdf.cell(bin_col_widths[0], 10, str(row_data.get('Type of Bin', '')), border=1, align='C')
        pdf.cell(bin_col_widths[1], 10, '', border=1, align='C')
        pdf.cell(bin_col_widths[2], 10, '', border=1, align='C')
        pdf.cell(bin_col_widths[3], 10, '', border=1, align='C')
        pdf.cell(bin_col_widths[4], 10, '', border=1, align='C', ln=1)
    pdf.ln(8)

    # --- Rack Details Table ---
    if pdf.get_y() + 80 > pdf.page_break_trigger: pdf.add_page()
    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 8, 'RACK DETAILS', 0, 1, 'L');
    pdf.set_font('Arial', 'B', 12)
    rack_headers = ["Types of \nRack", "Rack \nDimension(MM)", "Level/Rack", "Type of \nBin", "Bin \nDimension(MM)", "Level/Bin"]
    rack_col_widths = [34, 34.5, 29.5, 30, 34.5, 27.5]

    y_start = pdf.get_y()
    x_cursor = pdf.l_margin
    for i, header in enumerate(rack_headers):
        col_width = rack_col_widths[i]
        num_lines = header.count('\n') + 1
        text_height = num_lines * line_height
        y_text = y_start + (total_header_height - text_height) / 2
        pdf.set_xy(x_cursor, y_text)
        pdf.multi_cell(col_width, line_height, header, border=0, align='C')
        pdf.rect(x_cursor, y_start, col_width, total_header_height)
        x_cursor += col_width

    pdf.set_xy(pdf.l_margin, y_start + total_header_height)

    pdf.set_font('Arial', '', 10)
    num_rack_rows = max(4, len(data['rack_details_df']))
    for i in range(num_rack_rows):
        row_data = data['rack_details_df'].iloc[i] if i < len(data['rack_details_df']) else {}
        pdf.cell(rack_col_widths[0], 10, str(row_data.get('Types of Rack', '')), border=1, align='C')
        pdf.cell(rack_col_widths[1], 10, '', border=1, align='C')
        pdf.cell(rack_col_widths[2], 10, '', border=1, align='C')
        pdf.cell(rack_col_widths[3], 10, str(row_data.get('Type of Bin', '')), border=1, align='C')
        pdf.cell(rack_col_widths[4], 10, '', border=1, align='C')
        pdf.cell(rack_col_widths[5], 10, str(row_data.get('Level/Bin', '')), border=1, align='C', ln=1)
    pdf.ln(8)

    # --- Robust Bullet Point Function ---
    def add_bullet_point(key, value):
        if value and str(value).strip() and value not in ['N/A', '']:
            start_y = pdf.get_y(); pdf.set_x(pdf.l_margin)
            pdf.set_font('Arial', '', 12); pdf.cell(5, 6, chr(127))
            pdf.set_font('Arial', 'B', 12); pdf.cell(55, 6, f"{key}:")
            key_end_y = pdf.get_y() + 6
            value_start_x = pdf.l_margin + 60
            value_width = pdf.w - pdf.r_margin - value_start_x
            pdf.set_xy(value_start_x, start_y)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(value_width, 6, str(value), 0, 'L')
            value_end_y = pdf.get_y()
            pdf.set_y(max(key_end_y, value_end_y)); pdf.ln(1)

    add_bullet_point('Color', data.get('color'))
    add_bullet_point('Weight Carrying Capacity', f"{data.get('capacity', 0):.2f} KG" if data.get('capacity') else None)
    add_bullet_point('Lid Required', data.get('lid'))
    label_info = f"{data['label_space']} (Size: {data['label_size']})" if data.get('label_space') == 'Yes' else data.get('label_space')
    add_bullet_point('Space for Label', label_info)
    add_bullet_point('Stacking - Static', data.get('stack_static'))
    add_bullet_point('Stacking - Dynamic', data.get('stack_dynamic'))
    pdf.ln(5)
    # --- END: REDESIGNED SECTION ---

    pdf.section_title('TIMELINES')
    timeline_data = [("Date of RFQ Release", data['date_release']),("Query Resolution Deadline", data['date_query']),("Negotiation & Vendor Selection", data['date_selection']),("Delivery Deadline", data['date_delivery']),("Installation Deadline", data['date_install'])]
    if data['date_meet']: timeline_data.append(("Face to Face Meet", data['date_meet']))
    if data['date_quote']: timeline_data.append(("First Level Quotation", data['date_quote']))
    if data['date_review']: timeline_data.append(("Joint Review of Quotation", data['date_review']))
    if pdf.get_y() + (len(timeline_data) + 1) * 8 > pdf.page_break_trigger: pdf.add_page()
    pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Milestone', 1, 0, 'C'); pdf.cell(110, 8, 'Date', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for item, date_val in timeline_data: pdf.cell(80, 8, item, 1, 0, 'L'); pdf.cell(110, 8, date_val.strftime('%B %d, %Y'), 1, 1, 'L')
    pdf.ln(5)

    pdf.section_title('SINGLE POINT OF CONTACT')
    def draw_contact_column(title, name, designation, phone, email):
        col_start_x = pdf.get_x(); pdf.set_font('Arial', 'BU', 10); pdf.multi_cell(90, 6, title, 0, 'L'); pdf.ln(1)
        def draw_kv_row(key, value):
            key_str = str(key).encode('latin-1', 'replace').decode('latin-1'); value_str = str(value).encode('latin-1', 'replace').decode('latin-1')
            row_start_y = pdf.get_y(); pdf.set_x(col_start_x); pdf.set_font('Arial', 'B', 10); pdf.cell(25, 6, key_str, 0, 0, 'L')
            pdf.set_xy(col_start_x + 25, row_start_y); pdf.set_font('Arial', '', 10); pdf.multi_cell(65, 6, value_str, 0, 'L')
        draw_kv_row("Name:", name); draw_kv_row("Designation:", designation); draw_kv_row("Phone No:", phone); draw_kv_row("Email ID:", email)
    if pdf.get_y() + 45 > pdf.page_break_trigger: pdf.add_page()
    start_y = pdf.get_y(); pdf.set_xy(pdf.l_margin, start_y); draw_contact_column('Primary Contact', data['spoc1_name'], data['spoc1_designation'], data['spoc1_phone'], data['spoc1_email'])
    end_y1 = pdf.get_y()
    if data.get('spoc2_name'):
        pdf.set_xy(pdf.l_margin + 98, start_y); draw_contact_column('Secondary Contact', data['spoc2_name'], data['spoc2_designation'], data['spoc2_phone'], data['spoc2_email']); end_y2 = pdf.get_y()
        pdf.set_y(max(end_y1, end_y2))
    else: pdf.set_y(end_y1)
    pdf.ln(8)

    pdf.section_title('COMMERCIAL REQUIREMENTS')
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 6, "Please provide a detailed cost breakup in the format below. All costs should be inclusive of taxes and duties as applicable.", 0, 'L'); pdf.ln(4)
    if pdf.get_y() + (len(data['commercial_df']) + 1) * 8 > pdf.page_break_trigger: pdf.add_page()
    pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Cost Component', 1, 0, 'C'); pdf.cell(40, 8, 'Amount', 1, 0, 'C'); pdf.cell(70, 8, 'Remarks', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for index, row in data['commercial_df'].iterrows():
        component = str(row['Cost Component']).encode('latin-1', 'replace').decode('latin-1'); remarks = str(row['Remarks']).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(80, 8, component, 1, 0, 'L'); pdf.cell(40, 8, '', 1, 0); pdf.cell(70, 8, remarks, 1, 1, 'L')

    # --- START: MODIFIED FINAL SECTION (NOW DYNAMIC) ---
    pdf.ln(5)
    if pdf.get_y() + 90 > pdf.page_break_trigger:
        pdf.add_page()

    # --- Quotation Submission Details ---
    if data.get('submit_to_name'):
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(5, 8, chr(149))
        pdf.cell(0, 8, 'Quotation to be Submit to:', 0, 1)
        pdf.ln(5) # Add a line break for spacing

        # --- MODIFICATION START ---
        # The static text "Company Name" and "Company Full Address" has been removed.
        # Now, we directly print the user-provided values.

        pdf.set_x(pdf.l_margin + 15)
        pdf.set_font('Arial', '', 12)
        hex_color = data.get('submit_to_color', '#DC3232').lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        pdf.set_text_color(r, g, b)
        pdf.multi_cell(0, 7, data.get('submit_to_name', '')) # Using multi_cell for safety
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

        if data.get('submit_to_registered_office'):
            pdf.set_x(pdf.l_margin + 15)
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(128, 128, 128)
            pdf.multi_cell(0, 6, data.get('submit_to_registered_office', ''), 0, 'L') # Using multi_cell for safety
            pdf.set_text_color(0, 0, 0)
        # --- MODIFICATION END ---

    pdf.ln(5)

    # --- Delivery Location ---
    if data.get('delivery_location'):
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(5, 8, chr(149))
        pdf.cell(0, 8, 'Delivery Location:', 0, 1)
        pdf.ln(2)
        pdf.set_font('Arial', '', 11)
        pdf.set_x(pdf.l_margin + 5)
        pdf.multi_cell(0, 6, data.get('delivery_location'), 0, 'L')
    pdf.ln(5)

    # --- Annexures ---
    if data.get('annexures'):
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'ANNEXURES', 0, 1)
        pdf.ln(2)
        pdf.set_font('Arial', '', 11)
        pdf.set_x(pdf.l_margin + 5)
        pdf.multi_cell(0, 6, data.get('annexures'), 0, 'L')
    # --- END: MODIFIED FINAL SECTION ---

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
    Type_of_items = st.text_input("Type of Items*", help="e.g., Plastic Blue Bins & Line Side Racks")
    Storage = st.text_input("Storage Type*", help="e.g., Material Storage")
    company_name = st.text_input("Requester Company Name*", help="e.g., Pinnacle Mobility Solutions Pvt. Ltd")
    company_address = st.text_input("Requester Company Address*", help="e.g., Nanekarwadi, Chakan, Pune 410501")

with st.expander("Step 3: Add Footer Details (Optional)", expanded=True):
    footer_company_name = st.text_input("Footer Company Name", help="e.g., Your Company Private Ltd")
    footer_company_address = st.text_input("Footer Company Address", help="e.g., Registered Office: 123 Business Rd, Commerce City")

with st.form(key="advanced_rfq_form"):
    st.subheader("Step 4: Fill Core RFQ Details")
    purpose = st.text_area("Purpose of Requirement*", max_chars=300, height=100)

    with st.expander("Technical Specifications", expanded=True):
        st.info("Define the items for the vendor to quote on. The PDF will be generated with empty columns for the vendor to fill.")
        st.markdown("##### Bin Details")
        bin_df = st.data_editor(
            pd.DataFrame([{"Type of Bin": "TOTE"}, {"Type of Bin": "BIN C"}, {"Type of Bin": "BIN D"}]),
            num_rows="dynamic", use_container_width=True,
            column_config={"Type of Bin": st.column_config.TextColumn(required=True, help="Specify the name or type of the bin.")}
        )
        st.markdown("##### Rack Details")
        rack_df = st.data_editor(
            pd.DataFrame([
                {"Types of Rack": "MDR", "Type of Bin": "TOTE", "Level/Bin": "C"},
                {"Types of Rack": "SR", "Type of Bin": "BIN C", "Level/Bin": "A"},
                {"Types of Rack": "HRR", "Type of Bin": "BIN D", "Level/Bin": "S"}
            ]),
            num_rows="dynamic", use_container_width=True,
            column_config={
                "Types of Rack": st.column_config.TextColumn(required=True),
                "Type of Bin": st.column_config.TextColumn(required=True),
                "Level/Bin": st.column_config.TextColumn(required=False, help="This value will appear in the 'Level/Bin' column."),
            }
        )
        st.markdown("##### General Specifications")
        c1, c2 = st.columns(2)
        with c1:
            color = st.text_input("Color")
            capacity = st.number_input("Weight Carrying Capacity (KG)", 0.0, 1000.0, 0.0, format="%.2f")
            lid = st.radio("Lid Required?", ["Yes", "No", "N/A"], index=2, horizontal=True)
        with c2:
            label_space = st.radio("Space for Label?", ["Yes", "No", "N/A"], index=2, horizontal=True)
            label_size = "N/A"
            if label_space == "Yes":
                label_size = st.text_input("Label Size (e.g., 80*50)", "")
        st.markdown("###### Stacking Requirements (if applicable)")
        c1, c2 = st.columns(2)
        stack_static = c1.text_input("Static (e.g., 1+3)")
        stack_dynamic = c2.text_input("Dynamic (e.g., 1+1)")

    with st.expander("Timelines"):
        today = date.today()
        c1, c2, c3 = st.columns(3)
        with c1: date_release, date_query, date_meet = st.date_input("Date of RFQ Release *", today), st.date_input("Query Resolution Deadline *", today + timedelta(days=7)), st.date_input("Face to Face Meet", None)
        with c2: date_selection, date_delivery, date_quote = st.date_input("Negotiation & Vendor Selection *", today + timedelta(days=30)), st.date_input("Delivery Deadline *", today + timedelta(days=60)), st.date_input("First Level Quotation", None)
        with c3: date_install, date_review = st.date_input("Installation Deadline *", today + timedelta(days=75)), st.date_input("Joint Review of Quotation", None)

    with st.expander("Single Point of Contact (SPOC)"):
        st.markdown("##### Primary Contact*")
        c1, c2 = st.columns(2)
        with c1: spoc1_name, spoc1_designation = st.text_input("Name*", key="s1n"), st.text_input("Designation", key="s1d")
        with c2: spoc1_phone, spoc1_email = st.text_input("Phone No*", key="s1p"), st.text_input("Email ID*", key="s1e")
        st.markdown("##### Secondary Contact (Optional)")
        c1, c2 = st.columns(2)
        with c1: spoc2_name, spoc2_designation = st.text_input("Name", key="s2n"), st.text_input("Designation", key="s2d")
        with c2: spoc2_phone, spoc2_email = st.text_input("Phone No", key="s2p"), st.text_input("Email ID", key="s2e")

    with st.expander("Commercial Requirements"):
        edited_commercial_df = st.data_editor(pd.DataFrame([{"Cost Component": "Unit Cost", "Remarks": "Per item/unit specified in Section 2."},{"Cost Component": "Freight", "Remarks": "Specify if included or extra."},{"Cost Component": "Any other Handling Cost", "Remarks": ""},{"Cost Component": "Total Basic Cost (Per Unit)", "Remarks": ""}]), num_rows="dynamic", use_container_width=True)

    with st.expander("Submission, Delivery & Annexures"):
        st.markdown("##### Quotation Submission Details*")
        submit_to_name = st.text_input("Submit To (Company Name)*", "Agilomatrix Pvt. Ltd.")
        submit_to_color = st.color_picker("Company Name Color", "#DC3232")
        submit_to_registered_office = st.text_input("Submit To (Registered Office Address)", "Registered Office: F1403, 7 Plumeria Drive, 7PD Street, Tathawade, Pune - 411033")
        
        st.markdown("---")
        st.markdown("##### Logos for Final Section (Optional)")
        c1, c2 = st.columns(2)
        with c1:
            logo_eka_file = st.file_uploader("Upload First Logo (e.g., 'EKA')", type=['png', 'jpg', 'jpeg'], key="logo_eka")
        with c2:
            logo_agilo_file = st.file_uploader("Upload Second Logo (e.g., 'Agilomatrix')", type=['png', 'jpg', 'jpeg'], key="logo_agilo")

        st.markdown("---")
        st.markdown("##### Delivery & Annexures*")
        delivery_location = st.text_area("Delivery Location Address*", height=100)
        annexures = st.text_area("Annexures (one item per line)", height=100)

    submitted = st.form_submit_button("Generate RFQ Document", use_container_width=True, type="primary")

if submitted:
    if not all([purpose, spoc1_name, spoc1_phone, spoc1_email, company_name, company_address, Type_of_items, Storage, submit_to_name, delivery_location]):
        st.error("⚠️ Please fill in all mandatory (*) fields.")
    else:
        with st.spinner("Generating PDF..."):
            rfq_data = {
                'Type_of_items': Type_of_items, 'Storage': Storage, 'company_name': company_name, 'company_address': company_address,
                'footer_company_name': footer_company_name, 'footer_company_address': footer_company_address,
                'logo1_data': logo1_file.getvalue() if logo1_file else None, 'logo2_data': logo2_file.getvalue() if logo2_file else None,
                'logo1_w': logo1_w, 'logo1_h': logo1_h, 'logo2_w': logo2_w, 'logo2_h': logo2_h,
                'purpose': purpose,
                'bin_details_df': bin_df, 'rack_details_df': rack_df,
                'color': color, 'capacity': capacity, 'lid': lid, 'label_space': label_space, 'label_size': label_size,
                'stack_static': stack_static, 'stack_dynamic': stack_dynamic,
                'date_release': date_release, 'date_query': date_query, 'date_selection': date_selection, 'date_delivery': date_delivery,
                'date_install': date_install, 'date_meet': date_meet, 'date_quote': date_quote, 'date_review': date_review,
                'spoc1_name': spoc1_name, 'spoc1_designation': spoc1_designation, 'spoc1_phone': spoc1_phone, 'spoc1_email': spoc1_email,
                'spoc2_name': spoc2_name, 'spoc2_designation': spoc2_designation, 'spoc2_phone': spoc2_phone, 'spoc2_email': spoc2_email,
                'commercial_df': edited_commercial_df,
                'submit_to_name': submit_to_name, 'submit_to_color': submit_to_color, 'submit_to_registered_office': submit_to_registered_office,
                'logo_eka_data': logo_eka_file.getvalue() if logo_eka_file else None,
                'logo_agilo_data': logo_agilo_file.getvalue() if logo_agilo_file else None,
                'delivery_location': delivery_location,
                'annexures': annexures,
            }
            pdf_data = create_advanced_rfq_pdf(rfq_data)

        st.success("✅ RFQ PDF Generated Successfully!")
        file_name = f"RFQ_{Type_of_items.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        st.download_button(label="📥 Download RFQ Document", data=pdf_data, file_name=file_name, mime="application/pdf", use_container_width=True, type="primary")
