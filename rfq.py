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
    Generates a professional RFQ document with a dedicated final page for submission details.
    """
    class PDF(FPDF):
        def create_cover_page(self, data):
            # This method remains unchanged
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
            # The standard header should not appear on the cover page or the new final page
            if self.page_no() == 1 or self.page_no() == self.pages_count + 1: return
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
            # This method remains unchanged
            self.set_y(-25)
            footer_name, footer_addr = data.get('footer_company_name'), data.get('footer_company_address')
            if footer_name or footer_addr:
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y()); self.ln(3); self.set_text_color(128)
                if footer_name: self.set_font('Arial', 'B', 14); self.cell(0, 5, footer_name, 0, 1, 'C')
                if footer_addr: self.set_font('Arial', '', 8); self.cell(0, 5, footer_addr, 0, 1, 'C')
                self.set_text_color(0)
            self.set_y(-15); self.set_font('Arial', 'I', 8); self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

        def section_title(self, title):
            # This method remains unchanged
            if self.get_y() + 20 > self.page_break_trigger: self.add_page()
            self.set_font('Arial', 'B', 12); self.set_fill_color(230, 230, 230); self.cell(0, 8, title, 0, 1, 'L', fill=True); self.ln(4)

    pdf = PDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.create_cover_page(data)
    pdf.add_page()
    
    # --- All standard sections remain the same ---
    pdf.section_title('REQUIREMENT BACKGROUND')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, data['purpose'], border=0, align='L')
    pdf.ln(5)

    pdf.section_title('TECHNICAL SPECIFICATION')
    # ... (code for Bin, Rack, and other technical details remains unchanged)
    
    # --- START: NEW FINAL PAGE AS PER IMAGE ---
    def create_final_page(pdf_obj, data_dict):
        pdf_obj.add_page()
        
        # --- Header section on this specific page ---
        pdf_obj.set_y(45); pdf_obj.set_font('Arial', 'B', 16)
        pdf_obj.cell(0, 10, 'Request for Quotation (RFQ)', 0, 1, 'C')
        pdf_obj.set_font('Arial', '', 12)
        pdf_obj.cell(0, 8, f"For: {data_dict['Type_of_items']}", 0, 1, 'C')
        pdf_obj.ln(25)

        # --- Quotation Submission Details (WITHOUT PLACEHOLDERS) ---
        if data_dict.get('submit_to_name'):
            pdf_obj.set_font('Arial', 'B', 12)
            pdf_obj.cell(5, 8, chr(149)); pdf_obj.cell(0, 8, 'Quotation to be Submit to:', 0, 1)
            pdf_obj.ln(8)
            
            pdf_obj.set_x(pdf_obj.l_margin + 15)
            pdf_obj.set_font('Arial', '', 12)
            hex_color = data_dict.get('submit_to_color', '#DC3232').lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            pdf_obj.set_text_color(r, g, b)
            pdf_obj.cell(0, 7, data_dict.get('submit_to_name'), 0, 1)
            pdf_obj.set_text_color(0, 0, 0)

            if data_dict.get('submit_to_registered_office'):
                pdf_obj.set_x(pdf_obj.l_margin + 15)
                pdf_obj.set_font('Arial', '', 10); pdf_obj.set_text_color(128, 128, 128)
                pdf_obj.multi_cell(0, 6, data_dict.get('submit_to_registered_office'), 0, 'L')
                pdf_obj.set_text_color(0, 0, 0)
        pdf_obj.ln(15)

        # --- Delivery Location ---
        if data_dict.get('delivery_location'):
            pdf_obj.set_font('Arial', 'B', 12)
            pdf_obj.cell(5, 8, chr(149)); pdf_obj.cell(0, 8, 'Delivery Location:', 0, 1)
            pdf_obj.ln(4)
            pdf_obj.set_font('Arial', '', 11); pdf_obj.set_x(pdf_obj.l_margin + 15)
            pdf_obj.multi_cell(0, 6, data_dict.get('delivery_location'), 0, 'L')
        pdf_obj.ln(15)
        
        # --- Annexures ---
        if data_dict.get('annexures'):
            pdf_obj.set_font('Arial', 'B', 12)
            pdf_obj.cell(5, 8, chr(149)); pdf_obj.cell(0, 8, 'ANNEXURES:', 0, 1)
            pdf_obj.ln(4)
            pdf_obj.set_font('Arial', '', 11); pdf_obj.set_x(pdf_obj.l_margin + 15)
            pdf_obj.multi_cell(0, 6, data_dict.get('annexures'), 0, 'L')

    # Add the final page at the end of the document
    create_final_page(pdf, data)
        
    return bytes(pdf.output())

# --- STREAMLIT APP ---
st.title("🏭 Advanced SCM RFQ Generator")
st.markdown("---")

with st.expander("Step 1: Upload Company Logos & Set Dimensions (Optional)", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        logo1_file = st.file_uploader("Upload Company Logo 1 (Left Side, for Headers)", type=['png', 'jpg', 'jpeg'])
        logo1_w = st.number_input("Logo 1 Width (mm)", 5, 50, 30, 1)
        logo1_h = st.number_input("Logo 1 Height (mm)", 5, 50, 15, 1)
    with c2:
        logo2_file = st.file_uploader("Upload Company Logo 2 (Right Side, for Headers)", type=['png', 'jpg', 'jpeg'])
        logo2_w = st.number_input("Logo 2 Width (mm)", 5, 50, 30, 1)
        logo2_h = st.number_input("Logo 2 Height (mm)", 5, 50, 15, 1)

# ... (All other expanders and form elements remain the same)
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
    # ... (All form elements like purpose, technical specs, timelines, SPOC, commercial remain the same)
    with st.expander("Submission, Delivery & Annexures"):
        st.markdown("##### Quotation Submission Details*")
        submit_to_name = st.text_input("Submit To (Company Name)*", "Pinnacle Mobility Solutions Pvt. Ltd.")
        submit_to_color = st.color_picker("Company Name Color", "#DC3232")
        submit_to_registered_office = st.text_input("Submit To (Address)", "Nanerwadi, Wagholi")
        
        st.markdown("---")
        st.markdown("##### Delivery & Annexures*")
        delivery_location = st.text_area("Delivery Location Address*", "Quarter no:- 1136, Sector:- 6/C, Steel City\nNear Hanuman Mandir", height=100)
        annexures = st.text_area("Annexures (one item per line)", "Please attach technical datasheets for all quoted items.\nA company profile document is requested.", height=100)

    submitted = st.form_submit_button("Generate RFQ Document", use_container_width=True, type="primary")

if submitted:
    if not all([Type_of_items, Storage, company_name, company_address, submit_to_name, delivery_location]):
        st.error("⚠️ Please fill in all mandatory (*) fields.")
    else:
        with st.spinner("Generating PDF..."):
            rfq_data = {
                'Type_of_items': Type_of_items, 'Storage': Storage, 'company_name': company_name, 'company_address': company_address,
                'footer_company_name': footer_company_name, 'footer_company_address': footer_company_address,
                'logo1_data': logo1_file.getvalue() if logo1_file else None, 'logo2_data': logo2_file.getvalue() if logo2_file else None,
                'logo1_w': logo1_w, 'logo1_h': logo1_h, 'logo2_w': logo2_w, 'logo2_h': logo2_h,
                # ... (rest of the data dictionary remains the same)
                # --- UPDATED FIELDS FOR FINAL PAGE ---
                'submit_to_name': submit_to_name,
                'submit_to_color': submit_to_color,
                'submit_to_registered_office': submit_to_registered_office,
                'delivery_location': delivery_location,
                'annexures': annexures,
            }
            pdf_data = create_advanced_rfq_pdf(rfq_data)

        st.success("✅ RFQ PDF Generated Successfully!")
        file_name = f"RFQ_{Type_of_items.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        st.download_button(label="📥 Download RFQ Document", data=pdf_data, file_name=file_name, mime="application/pdf", use_container_width=True, type="primary")
