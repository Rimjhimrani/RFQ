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

# --- PDF Generation Function (Final, Corrected Version) ---
def create_advanced_rfq_pdf(data):
    """
    Generates a detailed, professional RFQ document with a dedicated cover page and a custom footer on all pages.
    """
    class PDF(FPDF):
        def create_cover_page(self, data):
            # --- Add Logo 1 (Left Side) ---
            logo1_data = data.get('logo1_data')
            logo1_w = data.get('logo1_w', 30)
            logo1_h = data.get('logo1_h', 15)
            if logo1_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo1_data)
                    tmp.flush()
                    self.image(tmp.name, x=self.l_margin, y=20, w=logo1_w, h=logo1_h)
                    os.remove(tmp.name)

            # Add "CONFIDENTIAL" on the top left, slightly below the logo
            self.set_y(35)
            self.set_x(self.l_margin)
            self.set_font('Arial', 'B', 14)
            self.set_text_color(255, 0, 0)
            self.cell(0, 10, 'CONFIDENTIAL')
            self.set_text_color(0, 0, 0)

            # --- Add Logo 2 (Right Side) ---
            logo2_data = data.get('logo2_data')
            logo2_w = data.get('logo2_w', 30)
            logo2_h = data.get('logo2_h', 15)
            if logo2_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo2_data)
                    tmp.flush()
                    logo2_path = tmp.name
                x_pos = self.w - self.r_margin - logo2_w
                self.image(logo2_path, x=x_pos, y=20, w=logo2_w, h=logo2_h)
                os.remove(logo2_path)

            # --- Centered Title Block (Your Custom Design) ---
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
            # No header on the first (cover) page
            if self.page_no() == 1:
                return
            
            logo1_data = data.get('logo1_data')
            logo1_w, logo1_h = data.get('logo1_w', 30), data.get('logo1_h', 15)
            if logo1_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo1_data)
                    tmp.flush()
                    self.image(tmp.name, x=self.l_margin, y=10, w=logo1_w, h=logo1_h)
                    os.remove(tmp.name)

            logo2_data = data.get('logo2_data')
            logo2_w, logo2_h = data.get('logo2_w', 30), data.get('logo2_h', 15)
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
            self.cell(0, 6, f"For: {data['main_type']} - {data['sub_type']}", 0, 1, 'C')
            self.ln(15)

        # --- CORRECTED CUSTOMIZABLE FOOTER FOR ALL PAGES ---
        def footer(self):
            self.set_y(-25) 

            footer_name = data.get('footer_company_name')
            footer_addr = data.get('footer_company_address')

            if footer_name or footer_addr:
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
                self.ln(3)
                self.set_font('Arial', '', 8)
                self.set_text_color(128)
                if footer_name:
                    self.cell(0, 5, footer_name, 0, 1, 'C')
                if footer_addr:
                    self.cell(0, 5, footer_addr, 0, 1, 'C')
                self.set_text_color(0)

            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

        def section_title(self, title):
            if self.get_y() + 20 > self.page_break_trigger: self.add_page()
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(230, 230, 230)
            self.cell(0, 8, title, 0, 1, 'L', fill=True)
            self.ln(4)

        def key_value_pair(self, key, value):
            if self.get_y() + 12 > self.page_break_trigger: self.add_page()
            key_width = 60
            value_width = self.w - self.l_margin - self.r_margin - key_width
            start_y = self.get_y()
            self.set_font('Arial', 'B', 10)
            self.multi_cell(key_width, 6, key, border=0, align='L')
            key_end_y = self.get_y()
            self.set_xy(self.l_margin + key_width, start_y)
            self.set_font('Arial', '', 10)
            self.multi_cell(value_width, 6, str(value), border=0, align='L')
            value_end_y = self.get_y()
            self.set_y(max(key_end_y, value_end_y))
            self.ln(1)
            
    pdf = PDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.create_cover_page(data)
    pdf.add_page()

    pdf.section_title('1. Purpose of Requirement')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, data['purpose'], border=0, align='L')
    pdf.ln(5)

    pdf.section_title('2. Technical Specifications')
    pdf.key_value_pair('Item / Infrastructure:', f"{data['main_type']} - {data['sub_type']}")
    pdf.key_value_pair('Internal Dimensions (LxWxH):', f"{data['dim_int_l']:.2f} x {data['dim_int_w']:.2f} x {data['dim_int_h']:.2f} mm")
    pdf.key_value_pair('External Dimensions (LxWxH):', f"{data['dim_ext_l']:.2f} x {data['dim_ext_w']:.2f} x {data['dim_ext_h']:.2f} mm")
    pdf.key_value_pair('Color:', data['color'])
    pdf.key_value_pair('Weight Carrying Capacity:', f"{data['capacity']:.2f} KG")
    
    if data['main_type'] == 'Item Type (Container)':
        pdf.key_value_pair('Lid Required:', data['lid'])
        pdf.key_value_pair('Space for Label:', f"{data['label_space']} (Size: {data['label_size']})")
        pdf.key_value_pair('Stacking - Static:', data['stack_static'])
        pdf.key_value_pair('Stacking - Dynamic:', data['stack_dynamic'])
    pdf.ln(5)

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

# --- STREAMLIT APP ---
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
    main_type = st.selectbox("Select RFQ Category", ["Item Type (Container)", "Storage Infrastructure"])
    if main_type == "Item Type (Container)": sub_type_options = ["Bin", "Trolley", "Carton Box", "Wooden Box", "Other"]
    else: sub_type_options = ["Heavy Duty Rack", "Cantilever Rack", "Shelving Rack", "Bin Flow Rack", "Other"]
    sub_type_selection = st.selectbox(f"Select {main_type}", sub_type_options)
    final_sub_type = st.text_input("Please specify 'Other' type") if sub_type_selection == "Other" else sub_type_selection
    purpose = st.text_area("Purpose of Requirement (Max 200 characters)*", max_chars=200, height=100)

    with st.expander("Technical Specifications", expanded=True):
        st.markdown("##### Dimensions (in mm)")
        c1, c2 = st.columns(2)
        with c1:
            dim_int_l, dim_int_w, dim_int_h = st.number_input("Internal - Length", 0.0, format="%.2f"), st.number_input("Internal - Width", 0.0, format="%.2f"), st.number_input("Internal - Height", 0.0, format="%.2f")
        with c2:
            dim_ext_l, dim_ext_w, dim_ext_h = st.number_input("External - Length", 0.0, format="%.2f"), st.number_input("External - Width", 0.0, format="%.2f"), st.number_input("External - Height", 0.0, format="%.2f")
        st.markdown("##### Other Specifications")
        c1, c2 = st.columns(2)
        with c1:
            color, capacity = st.text_input("Color"), st.number_input("Weight Carrying Capacity (in KG)", 0.0, format="%.2f")
        with c2:
            lid, label_space, label_size = "N/A", "N/A", "N/A"
            if main_type == "Item Type (Container)":
                lid, label_space = st.radio("Lid Required?", ["Yes", "No"], horizontal=True), st.radio("Space for Label?", ["Yes", "No"], horizontal=True)
                if label_space == "Yes": label_size = st.text_input("Label Size (e.g., 100x50 mm)")
        stack_static, stack_dynamic = "N/A", "N/A"
        if main_type == "Item Type (Container)":
            st.markdown("##### Stacking Requirements")
            c1, c2 = st.columns(2)
            stack_static, stack_dynamic = c1.text_input("Static (e.g., 1+3)"), c2.text_input("Dynamic (e.g., 1+1)")
            
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
            'main_type': main_type, 'sub_type': final_sub_type, 'purpose': purpose,
            'dim_int_l': dim_int_l, 'dim_int_w': dim_int_w, 'dim_int_h': dim_int_h, 'dim_ext_l': dim_ext_l, 'dim_ext_w': dim_ext_w, 'dim_ext_h': dim_ext_h,
            'color': color, 'capacity': capacity, 'lid': lid, 'label_space': label_space, 'label_size': label_size, 'stack_static': stack_static, 'stack_dynamic': stack_dynamic,
            'date_release': date_release, 'date_query': date_query, 'date_selection': date_selection, 'date_delivery': date_delivery, 'date_install': date_install, 'date_meet': date_meet, 'date_quote': date_quote, 'date_review': date_review,
            'spoc1_name': spoc1_name, 'spoc1_designation': spoc1_designation, 'spoc1_phone': spoc1_phone, 'spoc1_email': spoc1_email,
            'spoc2_name': spoc2_name, 'spoc2_designation': spoc2_designation, 'spoc2_phone': spoc2_phone, 'spoc2_email': spoc2_email,
            'commercial_df': edited_commercial_df,
        }
        
        with st.spinner("Generating PDF..."):
            pdf_data = create_advanced_rfq_pdf(rfq_data)
        
        st.success("✅ RFQ PDF Generated Successfully!")
        file_name = f"RFQ_{final_sub_type.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        st.download_button(label="📥 Download RFQ Document (.pdf)", data=pdf_data, file_name=file_name, mime="application/pdf", use_container_width=True, type="primary")
