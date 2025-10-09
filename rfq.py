import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF
import tempfile
import os

# --- App Configuration ---
st.set_page_config(
    page_title="Advanced SCM RFQ Generator",
    page_icon="🏭",
    layout="wide"
)

# --- PDF Generation Function (with Bug Fix) ---
def create_advanced_rfq_pdf(data):
    """
    Generates a detailed, professional RFQ document matching the specific table and bullet-point layout.
    """
    class PDF(FPDF):
        def create_cover_page(self, data):
            # ... (This function remains unchanged)
            logo1_data = data.get('logo1_data')
            logo1_w = data.get('logo1_w', 35)
            logo1_h = data.get('logo1_h', 20)
            if logo1_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo1_data)
                    tmp.flush()
                    self.image(tmp.name, x=self.l_margin, y=20, w=logo1_w, h=logo1_h)
                    os.remove(tmp.name)
            self.set_y(35)
            self.set_x(self.l_margin)
            self.set_font('Arial', 'B', 14)
            self.set_text_color(255, 0, 0)
            self.cell(0, 10, 'CONFIDENTIAL')
            self.set_text_color(0, 0, 0)
            logo2_data = data.get('logo2_data')
            logo2_w = data.get('logo2_w', 42)
            logo2_h = data.get('logo2_h', 20)
            if logo2_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo2_data)
                    tmp.flush()
                    logo2_path = tmp.name
                x_pos = self.w - self.r_margin - logo2_w
                self.image(logo2_path, x=x_pos, y=20, w=logo2_w, h=logo2_h)
                os.remove(logo2_path)
            self.set_y(60)
            self.set_font('Arial', 'B', 30)
            self.cell(0, 15, 'Request for Quotation', 0, 1, 'C')
            self.ln(5)
            self.set_font('Arial', '', 18)
            self.cell(0, 8, 'For', 0, 1, 'C')
            self.ln(3)
            self.set_font('Arial', 'B', 22)
            self.cell(0, 8, data['Type_of_items'], 0, 1, 'C')
            self.ln(5)
            self.set_font('Arial', '', 18)
            self.cell(0, 8, 'for', 0, 1, 'C')
            self.ln(3)
            self.set_font('Arial', 'B', 22)
            self.cell(0, 8, data['Storage'], 0, 1, 'C')
            self.ln(5)
            self.set_font('Arial', '', 18)
            self.cell(0, 8, 'At', 0, 1, 'C')
            self.ln(3)
            self.set_font('Arial', 'B', 24)
            self.cell(0, 10, data['company_name'], 0, 1, 'C')
            self.ln(3)
            self.set_font('Arial', '', 22)
            self.cell(0, 10, data['company_address'], 0, 1, 'C')

        def header(self):
            # ... (This function remains unchanged)
            if self.page_no() == 1:
                return
            logo1_data = data.get('logo1_data')
            logo1_w, logo1_h = data.get('logo1_w', 35), data.get('logo1_h', 20)
            if logo1_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo1_data)
                    tmp.flush()
                    self.image(tmp.name, x=self.l_margin, y=10, w=logo1_w, h=logo1_h)
                    os.remove(tmp.name)
            logo2_data = data.get('logo2_data')
            logo2_w, logo2_h = data.get('logo2_w', 42), data.get('logo2_h', 20)
            if logo2_data:
                x_pos = self.w - self.r_margin - logo2_w
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo2_data)
                    tmp.flush()
                    self.image(tmp.name, x=x_pos, y=10, w=logo2_w, h=logo2_h)
                    os.remove(tmp.name)
            self.set_y(12)
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Request for Quotation (RFQ)', 0, 1, 'C')
            self.set_font('Arial', 'I', 10)
            self.cell(0, 6, f"For: {data['Type_of_items']}", 0, 1, 'C')
            self.ln(15)

        def footer(self):
            # ... (This function remains unchanged)
            self.set_y(-25)
            footer_name = data.get('footer_company_name')
            footer_addr = data.get('footer_company_address')
            if footer_name or footer_addr:
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
                self.ln(3)
                self.set_text_color(128)
                if footer_name:
                    self.set_font('Arial', 'B', 14)
                    self.cell(0, 5, footer_name, 0, 1, 'C')
                if footer_addr:
                    self.set_font('Arial', '', 8)
                    self.cell(0, 5, footer_addr, 0, 1, 'C')
                self.set_text_color(0)
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

        def section_title(self, title):
            # ... (This function remains unchanged)
            if self.get_y() + 20 > self.page_break_trigger: self.add_page()
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(230, 230, 230)
            self.cell(0, 8, title, 0, 1, 'L', fill=True)
            self.ln(4)

    pdf = PDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.create_cover_page(data)
    pdf.add_page()

    pdf.section_title('1. Purpose of Requirement')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, data['purpose'], border=0, align='L')
    pdf.ln(5)

    # --- TECHNICAL SPECIFICATION SECTION ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '2. TECHNICAL SPECIFICATION', 0, 1, 'L')
    pdf.ln(4)

    # --- Bin Details Table ---
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'BIN DETAILS', 0, 1, 'L')
    pdf.ln(2)
    
    bin_headers = ['Type of Bin', 'Bin Outer\nDimension (MM)', 'Bin Inner\nDimension (MM)', 'Conceptual\nImage', 'Qty Bin']
    bin_col_widths = [38, 38, 38, 38, 38]
    pdf.set_font('Arial', 'B', 10)
    for i in range(len(bin_headers)):
        pdf.multi_cell(bin_col_widths[i], 8, bin_headers[i], border=1, align='C', ln=3 if i == len(bin_headers) - 1 else 0)
    
    pdf.set_font('Arial', '', 10)
    num_bin_rows_to_draw = max(4, len(data['bin_details_df']))
    for i in range(num_bin_rows_to_draw):
        row_data = data['bin_details_df'].iloc[i] if i < len(data['bin_details_df']) else {'Type of Bin': ''}
        pdf.cell(bin_col_widths[0], 10, str(row_data.get('Type of Bin', '')), border=1)
        for j in range(1, len(bin_col_widths)):
            pdf.cell(bin_col_widths[j], 10, '', border=1)
        pdf.ln()

    pdf.ln(8)

    # --- Rack Details Table ---
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'RACK DETAILS', 0, 1, 'L')
    pdf.ln(2)

    rack_headers = ['Types of\nRack', 'Rack Dimension\n(MM)', 'Level/Rack', 'Type of Bin', 'Bin Dimension\n(MM)', 'Level/Bin']
    rack_col_widths = [32, 32, 32, 32, 32, 30]
    pdf.set_font('Arial', 'B', 10)
    for i in range(len(rack_headers)):
        pdf.multi_cell(rack_col_widths[i], 8, rack_headers[i], border=1, align='C', ln=3 if i == len(rack_headers) - 1 else 0)

    pdf.set_font('Arial', '', 10)
    num_rack_rows_to_draw = max(4, len(data['rack_details_df']))
    for i in range(num_rack_rows_to_draw):
        row_data = data['rack_details_df'].iloc[i] if i < len(data['rack_details_df']) else {'Types of Rack': '', 'Type of Bin': ''}
        pdf.cell(rack_col_widths[0], 10, str(row_data.get('Types of Rack', '')), border=1)
        pdf.cell(rack_col_widths[1], 10, '', border=1)
        pdf.cell(rack_col_widths[2], 10, '', border=1)
        pdf.cell(rack_col_widths[3], 10, str(row_data.get('Type of Bin', '')), border=1)
        pdf.cell(rack_col_widths[4], 10, '', border=1)
        pdf.cell(rack_col_widths[5], 10, '', border=1)
        pdf.ln()
    
    pdf.ln(8)

    # --- START: CORRECTED BULLET POINT SECTION ---
    def add_bullet_point(key, value):
        # This check prevents empty values from being printed
        if value and str(value).strip() and value != 'N/A':
            start_y = pdf.get_y()
            
            # Set position and draw bullet and key
            pdf.set_x(pdf.l_margin)
            pdf.set_font('Arial', '', 10)
            pdf.cell(5, 6, chr(127)) # Bullet point character
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(55, 6, f"{key}:")
            key_end_y = pdf.get_y() # Will be start_y + 6

            # Explicitly set position for the value part
            value_start_x = pdf.l_margin + 60
            pdf.set_xy(value_startx, start_y)

            # Calculate the remaining width and draw the value using multi_cell
            remaining_width = pdf.w - pdf.r_margin - value_start_x
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(remaining_width, 6, str(value), 0, 'L')
            value_end_y = pdf.get_y() # multi_cell updates the y-position

            # Ensure the next line starts below the tallest part (the key or the value)
            pdf.set_y(max(key_end_y, value_end_y))
            pdf.ln(1) # Add a small gap

    add_bullet_point('Color', data['color'])
    add_bullet_point('Weight Carrying Capacity', f"{data['capacity']:.2f} KG" if data.get('capacity') else None)
    add_bullet_point('Lid Required', data['lid'])
    label_info = f"{data['label_space']} (Size: {data['label_size']})" if data['label_space'] == 'Yes' else data['label_space']
    add_bullet_point('Space for Label', label_info)
    add_bullet_point('Stacking - Static', data['stack_static'])
    add_bullet_point('Stacking - Dynamic', data['stack_dynamic'])
    pdf.ln(5)
    # --- END: CORRECTED BULLET POINT SECTION ---

    # --- All subsequent sections remain unchanged ---
    pdf.section_title('3. Timelines')
    timeline_data = [("Date of RFQ Release", data['date_release']),("Query Resolution Deadline", data['date_query']),("Negotiation & Vendor Selection", data['date_selection']),("Delivery Deadline", data['date_delivery']),("Installation Deadline", data['date_install'])]
    if data['date_meet']: timeline_data.append(("Face to Face Meet", data['date_meet']))
    if data['date_quote']: timeline_data.append(("First Level Quotation", data['date_quote']))
    if data['date_review']: timeline_data.append(("Joint Review of Quotation", data['date_review']))
    
    table_height = (len(timeline_data) + 1) * 8
    if pdf.get_y() + table_height > pdf.page_break_trigger: pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(80, 8, 'Milestone', 1, 0, 'C')
    pdf.cell(110, 8, 'Date', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for item, date_val in timeline_data:
        pdf.cell(80, 8, item, 1, 0, 'L')
        pdf.cell(110, 8, date_val.strftime('%B %d, %Y'), 1, 1, 'L')
    pdf.ln(5)

    pdf.section_title('4. Single Point of Contact (for Query Resolution)')
    def draw_contact_column(title, name, designation, phone, email):
        col_start_x = pdf.get_x()
        pdf.set_font('Arial', 'BU', 10)
        pdf.multi_cell(90, 6, title, 0, 'L')
        pdf.ln(1)
        def draw_kv_row(key, value):
            key_str, value_str = str(key).encode('latin-1', 'replace').decode('latin-1'), str(value).encode('latin-1', 'replace').decode('latin-1')
            row_start_y = pdf.get_y()
            pdf.set_x(col_start_x)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(25, 6, key_str, 0, 0, 'L')
            pdf.set_xy(col_start_x + 25, row_start_y)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(65, 6, value_str, 0, 'L')
        draw_kv_row("Name:", name)
        draw_kv_row("Designation:", designation)
        draw_kv_row("Phone No:", phone)
        draw_kv_row("Email ID:", email)
    estimated_height = 45 
    if pdf.get_y() + estimated_height > pdf.page_break_trigger: pdf.add_page()
    start_y = pdf.get_y()
    pdf.set_xy(pdf.l_margin, start_y)
    draw_contact_column('Primary Contact', data['spoc1_name'], data['spoc1_designation'], data['spoc1_phone'], data['spoc1_email'])
    end_y1 = pdf.get_y()
    if data.get('spoc2_name'):
        pdf.set_xy(pdf.l_margin + 98, start_y)
        draw_contact_column('Secondary Contact', data['spoc2_name'], data['spoc2_designation'], data['spoc2_phone'], data['spoc2_email'])
        end_y2 = pdf.get_y()
        pdf.set_y(max(end_y1, end_y2))
    else:
        pdf.set_y(end_y1)
    pdf.ln(8)

    pdf.section_title('5. Commercial Requirements (To be filled by vendor)')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, "Please provide a detailed cost breakup in the format below. All costs should be inclusive of taxes and duties as applicable.", border=0, align='L')
    pdf.ln(4)
    table_height = (len(data['commercial_df']) + 1) * 8
    if pdf.get_y() + table_height > pdf.page_break_trigger: pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(80, 8, 'Cost Component', 1, 0, 'C')
    pdf.cell(40, 8, 'Amount', 1, 0, 'C')
    pdf.cell(70, 8, 'Remarks', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for index, row in data['commercial_df'].iterrows():
        component = str(row['Cost Component']).encode('latin-1', 'replace').decode('latin-1')
        remarks = str(row['Remarks']).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(80, 8, component, 1, 0, 'L')
        pdf.cell(40, 8, '', 1, 0)
        pdf.cell(70, 8, remarks, 1, 1, 'L')
        
    return bytes(pdf.output())

# --- STREAMLIT APP (Unchanged) ---
st.title("🏭 Advanced SCM RFQ Generator")
st.markdown("---")

with st.expander("Step 1: Upload Company Logos & Set Dimensions (Optional)", expanded=True):
    st.info("Logos will be displayed on the header of every page. Dimensions are in mm.")
    c1, c2 = st.columns(2)
    with c1:
        logo1_file = st.file_uploader("Upload Company Logo 1 (Left Side)", type=['png', 'jpg', 'jpeg'])
        sub_c1, sub_c2 = st.columns(2)
        logo1_w = sub_c1.number_input("Logo 1 Width", 5, 50, 30, 1)
        logo1_h = sub_c2.number_input("Logo 1 Height", 5, 50, 15, 1)
    with c2:
        logo2_file = st.file_uploader("Upload Company Logo 2 (Right Side)", type=['png', 'jpg', 'jpeg'])
        sub_c1, sub_c2 = st.columns(2)
        logo2_w = sub_c1.number_input("Logo 2 Width", 5, 50, 30, 1)
        logo2_h = sub_c2.number_input("Logo 2 Height", 5, 50, 15, 1)

with st.expander("Step 2: Add Cover Page Details", expanded=True):
    Type_of_items = st.text_input("Type of Items*", help="e.g., Plastic Blue Bins & Line Side Racks")
    Storage = st.text_input("Storage Type*", help="e.g., Material Storage")
    company_name = st.text_input("Requester Company Name*", help="e.g., Pinnacle Mobility Solutions Pvt. Ltd (PMSPL)")
    company_address = st.text_input("Requester Company Address*", help="e.g., Nanekarwadi, Chakan, Pune 410501")

with st.expander("Step 3: Add Footer Details (Optional)", expanded=True):
    st.info("This information will appear in the footer of every page.")
    footer_company_name = st.text_input("Footer Company Name", help="e.g., Your Company Private Ltd")
    footer_company_address = st.text_input("Footer Company Address", help="e.g., Registered Office: 123 Business Rd, Commerce City, 12345")

with st.form(key="advanced_rfq_form"):
    st.subheader("Step 4: Fill Core RFQ Details")
    purpose = st.text_area("Purpose of Requirement (Max 200 characters)*", max_chars=200, height=100)

    with st.expander("Technical Specifications", expanded=True):
        st.info("Define the types of Bins and Racks you need quotes for. The vendor will fill in the dimensions and other details on the generated PDF.")
        
        st.markdown("##### Bin Details")
        bin_df = st.data_editor(
            pd.DataFrame([{"Type of Bin": "Example Bin Type A"}, {"Type of Bin": "Example Bin Type B"}]),
            num_rows="dynamic",
            use_container_width=True,
            column_config={"Type of Bin": st.column_config.TextColumn(required=True)}
        )

        st.markdown("##### Rack Details")
        rack_df = st.data_editor(
            pd.DataFrame([
                {"Types of Rack": "Example Rack Type X", "Type of Bin": "Bin Type A"},
                {"Types of Rack": "Example Rack Type Y", "Type of Bin": "Bin Type B"}
            ]),
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Types of Rack": st.column_config.TextColumn(required=True),
                "Type of Bin": st.column_config.TextColumn(help="Which bin type will be used with this rack?", required=True)
            }
        )

        st.markdown("##### General Specifications")
        c1, c2 = st.columns(2)
        with c1:
            color = st.text_input("Color")
            capacity = st.number_input("Weight Carrying Capacity (in KG)", 0.0, format="%.2f")
            lid = st.radio("Lid Required?", ["Yes", "No", "N/A"], index=2, horizontal=True)
        with c2:
            label_space = st.radio("Space for Label?", ["Yes", "No", "N/A"], index=2, horizontal=True)
            label_size = "N/A"
            if label_space == "Yes":
                label_size = st.text_input("Label Size (e.g., 100x50 mm)")
        
        st.markdown("###### Stacking Requirements (if applicable)")
        c1, c2 = st.columns(2)
        stack_static = c1.text_input("Static (e.g., 1+3)")
        stack_dynamic = c2.text_input("Dynamic (e.g., 1+1)")
            
    with st.expander("Timelines"):
        st.info("Fields marked with * are mandatory.")
        today = date.today()
        c1, c2, c3 = st.columns(3)
        with c1:
            date_release, date_query, date_meet = st.date_input("Date of RFQ Release *", today), st.date_input("Query Resolution Deadline *", today + timedelta(days=7)), st.date_input("Face to Face Meet (Optional)", None)
        with c2:
            date_selection, date_delivery, date_quote = st.date_input("Negotiation and Vendor Selection *", today + timedelta(days=30)), st.date_input("Delivery Deadline *", today + timedelta(days=60)), st.date_input("First Level Quotation (Optional)", None)
        with c3:
            date_install, date_review = st.date_input("Installation Deadline *", today + timedelta(days=75)), st.date_input("Joint Review of Quotation (Optional)", None)

    with st.expander("Single Point of Contact (SPOC)"):
        st.markdown("##### Primary Contact (Mandatory)")
        c1, c2 = st.columns(2)
        with c1:
            spoc1_name, spoc1_designation = st.text_input("Name*"), st.text_input("Designation")
        with c2:
            spoc1_phone, spoc1_email = st.text_input("Phone No*"), st.text_input("Email ID*")
        st.markdown("---")
        st.markdown("##### Secondary Contact (Optional)")
        c1, c2 = st.columns(2)
        with c1:
            spoc2_name, spoc2_designation = st.text_input("Name", key="spoc2_name"), st.text_input("Designation", key="spoc2_des")
        with c2:
            spoc2_phone, spoc2_email = st.text_input("Phone No", key="spoc2_phone"), st.text_input("Email ID", key="spoc2_email")

    with st.expander("Commercial Requirements"):
        st.info("Define the cost components for the vendor to quote. The vendor will fill the 'Amount' column.")
        edited_commercial_df = st.data_editor(pd.DataFrame([{"Cost Component": "Unit Cost", "Remarks": "Per item/unit specified in Section 2."},{"Cost Component": "Freight", "Remarks": "Specify if included or extra."},{"Cost Component": "Any other Handling Cost", "Remarks": "e.g., loading, unloading."},{"Cost Component": "Total Basic Cost (Per Unit)", "Remarks": ""}]), num_rows="dynamic", use_container_width=True, column_config={"Cost Component": st.column_config.TextColumn(required=True)})

    st.markdown("---")
    submitted = st.form_submit_button("Generate RFQ Document", use_container_width=True, type="primary")

if submitted:
    if not all([purpose, spoc1_name, spoc1_phone, spoc1_email, company_name, company_address, Type_of_items, Storage]):
        st.error("⚠️ Please fill in all mandatory fields: Purpose, Primary Contact, and all Cover Page details.")
    else:
        logo1_data = logo1_file.getvalue() if logo1_file else None
        logo2_data = logo2_file.getvalue() if logo2_file else None

        rfq_data = {
            'Type_of_items': Type_of_items, 'Storage': Storage, 'company_name': company_name, 'company_address': company_address,
            'footer_company_name': footer_company_name, 'footer_company_address': footer_company_address,
            'logo1_data': logo1_data, 'logo2_data': logo2_data, 'logo1_w': logo1_w, 'logo1_h': logo1_h, 'logo2_w': logo2_w, 'logo2_h': logo2_h,
            'purpose': purpose,
            'bin_details_df': bin_df,
            'rack_details_df': rack_df,
            'color': color, 'capacity': capacity, 'lid': lid, 'label_space': label_space, 'label_size': label_size, 'stack_static': stack_static, 'stack_dynamic': stack_dynamic,
            'date_release': date_release, 'date_query': date_query, 'date_selection': date_selection, 'date_delivery': date_delivery, 'date_install': date_install, 'date_meet': date_meet, 'date_quote': date_quote, 'date_review': date_review,
            'spoc1_name': spoc1_name, 'spoc1_designation': spoc1_designation, 'spoc1_phone': spoc1_phone, 'spoc1_email': spoc1_email,
            'spoc2_name': spoc2_name, 'spoc2_designation': spoc2_designation, 'spoc2_phone': spoc2_phone, 'spoc2_email': spoc2_email,
            'commercial_df': edited_commercial_df,
        }
        
        with st.spinner("Generating PDF..."):
            pdf_data = create_advanced_rfq_pdf(rfq_data)
        
        st.success("✅ RFQ PDF Generated Successfully!")
        file_name = f"RFQ_{Type_of_items.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        st.download_button(label="📥 Download RFQ Document (.pdf)", data=pdf_data, file_name=file_name, mime="application/pdf", use_container_width=True, type="primary")
