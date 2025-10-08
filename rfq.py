import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF

# --- App Configuration ---
st.set_page_config(
    page_title="Advanced SCM RFQ Generator",
    page_icon="🏭",
    layout="wide"
)

# --- PDF Generation Function (Final Version) ---
def create_advanced_rfq_pdf(data):
    """
    Generates a detailed, professional RFQ document in PDF format from a dictionary of data.
    """
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Request for Quotation (RFQ)', 0, 1, 'C')
            self.set_font('Arial', 'I', 10)
            self.cell(0, 6, f"For: {data['main_type']} - {data['sub_type']}", 0, 1, 'C')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

        def section_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(230, 230, 230)
            self.cell(0, 8, title, 0, 1, 'L', fill=True)
            self.ln(4)

        def key_value_pair(self, key, value):
            estimated_height = 12 
            if self.get_y() + estimated_height > self.page_break_trigger:
                self.add_page()

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
            final_y = max(key_end_y, value_end_y)
            self.set_y(final_y)
            self.ln(1)

    pdf = PDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()

    # Sections 1-4 (Unchanged)
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
    pdf.key_value_pair('Date of RFQ Release:', data['date_release'].strftime('%B %d, %Y'))
    pdf.key_value_pair('Query Resolution Deadline:', data['date_query'].strftime('%B %d, %Y'))
    pdf.key_value_pair('Negotiation & Vendor Selection:', data['date_selection'].strftime('%B %d, %Y'))
    pdf.key_value_pair('Delivery Deadline:', data['date_delivery'].strftime('%B %d, %Y'))
    pdf.key_value_pair('Installation Deadline:', data['date_install'].strftime('%B %d, %Y'))
    if data['date_meet']: pdf.key_value_pair('Face to Face Meet:', data['date_meet'].strftime('%B %d, %Y'))
    if data['date_quote']: pdf.key_value_pair('First Level Quotation:', data['date_quote'].strftime('%B %d, %Y'))
    if data['date_review']: pdf.key_value_pair('Joint Review of Quotation:', data['date_review'].strftime('%B %d, %Y'))
    pdf.ln(5)
    pdf.section_title('4. Single Point of Contact (for Query Resolution)')
    pdf.set_font('Arial', 'BU', 10)
    pdf.cell(0, 6, 'Primary Contact', 0, 1)
    pdf.key_value_pair('Name:', data['spoc1_name'])
    pdf.key_value_pair('Designation:', data['spoc1_designation'])
    pdf.key_value_pair('Phone No:', data['spoc1_phone'])
    pdf.key_value_pair('Email ID:', data['spoc1_email'])
    if data.get('spoc2_name'):
        pdf.ln(3)
        pdf.set_font('Arial', 'BU', 10)
        pdf.cell(0, 6, 'Secondary Contact', 0, 1)
        pdf.key_value_pair('Name:', data['spoc2_name'])
        pdf.key_value_pair('Designation:', data['spoc2_designation'])
        pdf.key_value_pair('Phone No:', data['spoc2_phone'])
        pdf.key_value_pair('Email ID:', data['spoc2_email'])
    pdf.ln(5)

    # --- SECTION 5: NEW ROBUST COMMERCIAL TABLE ---
    pdf.section_title('5. Commercial Requirements (To be filled by vendor)')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, "Please provide a detailed cost breakup in the format below. All costs should be inclusive of taxes and duties as applicable.", border=0, align='L')
    pdf.ln(4)
    
    # Check for page break before drawing table
    table_height_estimate = (len(data['commercial_df']) + 1) * 10 # Estimate 10mm per row
    if pdf.get_y() + table_height_estimate > pdf.page_break_trigger:
        pdf.add_page()
    
    line_height = 8
    col_widths = {'component': 80, 'amount': 40, 'remarks': 70}
    
    # Draw Table Header
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(col_widths['component'], line_height, 'Cost Component', 1, 0, 'C')
    pdf.cell(col_widths['amount'], line_height, 'Amount', 1, 0, 'C')
    pdf.cell(col_widths['remarks'], line_height, 'Remarks', 1, 1, 'C')

    # Draw Table Rows
    pdf.set_font('Arial', '', 10)
    for index, row in data['commercial_df'].iterrows():
        start_y = pdf.get_y()
        
        # Draw text using multi_cell to allow wrapping
        pdf.multi_cell(col_widths['component'], line_height, str(row['Cost Component']), border='LR', align='L')
        y1 = pdf.get_y()
        
        pdf.set_xy(start_y, pdf.get_x() + col_widths['component']) # Reset cursor for next column
        
        # Remarks column (drawn before Amount to calculate height)
        pdf.set_xy(start_y, pdf.get_x() + col_widths['component'] + col_widths['amount'])
        pdf.multi_cell(col_widths['remarks'], line_height, str(row['Remarks']), border='LR', align='L')
        y2 = pdf.get_y()

        # Determine the max height of the row
        row_height = max(y1, y2) - start_y
        
        # Reset cursor and draw the borders and the blank 'Amount' cell
        pdf.set_xy(start_y, pdf.get_x())
        pdf.cell(col_widths['component'], row_height, '', border='LRB', align='L')
        pdf.cell(col_widths['amount'], row_height, '', border='LRB', align='L')
        pdf.cell(col_widths['remarks'], row_height, '', border='LRB', align='L')
        pdf.ln(row_height)

    return bytes(pdf.output())


# --- STREAMLIT APP (Unchanged from previous version) ---
st.title("🏭 Advanced SCM RFQ Generator")
st.markdown("---")

with st.form(key="advanced_rfq_form"):
    
    st.subheader("1. RFQ Details")
    main_type = st.selectbox("Select RFQ Category", ["Item Type (Container)", "Storage Infrastructure"])
    if main_type == "Item Type (Container)":
        sub_type_options = ["Bin", "Trolley", "Carton Box", "Wooden Box", "Other"]
    else:
        sub_type_options = ["Heavy Duty Rack", "Cantilever Rack", "Shelving Rack", "Bin Flow Rack", "Other"]
    sub_type_selection = st.selectbox(f"Select {main_type}", sub_type_options)
    final_sub_type = sub_type_selection
    if sub_type_selection == "Other":
        final_sub_type = st.text_input("Please specify 'Other' type")
    purpose = st.text_area("Purpose of Requirement (Max 200 characters)*", max_chars=200, height=100)

    with st.expander("2. Technical Specifications", expanded=True):
        st.markdown("##### Dimensions (in mm)")
        c1, c2 = st.columns(2)
        with c1:
            dim_int_l = st.number_input("Internal - Length", min_value=0.0, format="%.2f")
            dim_int_w = st.number_input("Internal - Width", min_value=0.0, format="%.2f")
            dim_int_h = st.number_input("Internal - Height", min_value=0.0, format="%.2f")
        with c2:
            dim_ext_l = st.number_input("External - Length", min_value=0.0, format="%.2f")
            dim_ext_w = st.number_input("External - Width", min_value=0.0, format="%.2f")
            dim_ext_h = st.number_input("External - Height", min_value=0.0, format="%.2f")
        st.markdown("##### Other Specifications")
        c1, c2 = st.columns(2)
        with c1:
            color = st.text_input("Color")
            capacity = st.number_input("Weight Carrying Capacity (in KG)", min_value=0.0, format="%.2f")
        with c2:
            lid, label_space, label_size = "N/A", "N/A", "N/A"
            if main_type == "Item Type (Container)":
                lid = st.radio("Lid Required?", ["Yes", "No"], horizontal=True)
                label_space = st.radio("Space for Label?", ["Yes", "No"], horizontal=True)
                if label_space == "Yes":
                    label_size = st.text_input("Label Size (e.g., 100x50 mm)")
        stack_static, stack_dynamic = "N/A", "N/A"
        if main_type == "Item Type (Container)":
            st.markdown("##### Stacking Requirements")
            c1, c2 = st.columns(2)
            with c1: stack_static = st.text_input("Static (e.g., 1+3)")
            with c2: stack_dynamic = st.text_input("Dynamic (e.g., 1+1)")

    with st.expander("3. Timelines"):
        st.info("Fields marked with * are mandatory.")
        today = date.today()
        c1, c2, c3 = st.columns(3)
        with c1:
            date_release = st.date_input("Date of RFQ Release *", value=today)
            date_query = st.date_input("Query Resolution Deadline *", value=today + timedelta(days=7))
            date_meet = st.date_input("Face to Face Meet (Optional)", value=None, help="Leave blank if not applicable.")
        with c2:
            date_selection = st.date_input("Negotiation and Vendor Selection *", value=today + timedelta(days=30))
            date_delivery = st.date_input("Delivery Deadline *", value=today + timedelta(days=60))
            date_quote = st.date_input("First Level Quotation (Optional)", value=None, help="Leave blank if not applicable.")
        with c3:
            date_install = st.date_input("Installation Deadline *", value=today + timedelta(days=75))
            date_review = st.date_input("Joint Review of Quotation (Optional)", value=None, help="Leave blank if not applicable.")

    with st.expander("4. Single Point of Contact (SPOC)"):
        st.markdown("##### Primary Contact (Mandatory)")
        c1, c2 = st.columns(2)
        with c1:
            spoc1_name = st.text_input("Name*")
            spoc1_designation = st.text_input("Designation")
        with c2:
            spoc1_phone = st.text_input("Phone No*")
            spoc1_email = st.text_input("Email ID*")
        st.markdown("---")
        st.markdown("##### Secondary Contact (Optional)")
        c1, c2 = st.columns(2)
        with c1:
            spoc2_name = st.text_input("Name", key="spoc2_name")
            spoc2_designation = st.text_input("Designation", key="spoc2_des")
        with c2:
            spoc2_phone = st.text_input("Phone No", key="spoc2_phone")
            spoc2_email = st.text_input("Email ID", key="spoc2_email")

    with st.expander("5. Commercial Requirements"):
        st.info("Define the cost components you require the vendor to quote. The vendor will fill in the 'Amount' column on the PDF.")
        commercial_df_initial = pd.DataFrame([
            {"Cost Component": "Unit Cost", "Remarks": "Per item/unit specified in Section 2."},
            {"Cost Component": "Freight", "Remarks": "Specify if included or extra."},
            {"Cost Component": "Any other Handling Cost", "Remarks": "e.g., loading, unloading."},
            {"Cost Component": "Total Basic Cost (Per Unit)", "Remarks": ""},
        ])
        edited_commercial_df = st.data_editor(
            commercial_df_initial, num_rows="dynamic", use_container_width=True,
            column_config={"Cost Component": st.column_config.TextColumn(required=True)}
        )

    st.markdown("---")
    submitted = st.form_submit_button("Generate RFQ Document", use_container_width=True, type="primary")

if submitted:
    if not all([purpose, spoc1_name, spoc1_phone, spoc1_email]):
        st.error("⚠️ Please fill in all mandatory fields: Purpose and all Primary Contact details.")
    else:
        rfq_data = {
            'main_type': main_type, 'sub_type': final_sub_type, 'purpose': purpose,
            'dim_int_l': dim_int_l, 'dim_int_w': dim_int_w, 'dim_int_h': dim_int_h,
            'dim_ext_l': dim_ext_l, 'dim_ext_w': dim_ext_w, 'dim_ext_h': dim_ext_h,
            'color': color, 'capacity': capacity, 'lid': lid,
            'label_space': label_space, 'label_size': label_size,
            'stack_static': stack_static, 'stack_dynamic': stack_dynamic,
            'date_release': date_release, 'date_query': date_query, 'date_selection': date_selection,
            'date_delivery': date_delivery, 'date_install': date_install,
            'date_meet': date_meet, 'date_quote': date_quote, 'date_review': date_review,
            'spoc1_name': spoc1_name, 'spoc1_designation': spoc1_designation,
            'spoc1_phone': spoc1_phone, 'spoc1_email': spoc1_email,
            'spoc2_name': spoc2_name, 'spoc2_designation': spoc2_designation,
            'spoc2_phone': spoc2_phone, 'spoc2_email': spoc2_email,
            'commercial_df': edited_commercial_df,
        }
        
        with st.spinner("Generating PDF..."):
            pdf_data = create_advanced_rfq_pdf(rfq_data)
        
        st.success("✅ RFQ PDF Generated Successfully!")
        file_name = f"RFQ_{final_sub_type.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        st.download_button(
            label="📥 Download RFQ Document (.pdf)", data=pdf_data,
            file_name=file_name, mime="application/pdf",
            use_container_width=True, type="primary"
        )
