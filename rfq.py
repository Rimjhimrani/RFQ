import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF

# --- PDF Generation Function ---
def create_rfq_pdf(rfq_number, issue_date, submission_deadline, company_name, company_address, 
                   contact_person, contact_email, project_description, items_df, 
                   delivery_address, payment_terms, terms_and_conditions):
    """
    Generates a professional RFQ document in PDF format.
    """
    
    class PDF(FPDF):
        def header(self):
            # Arial bold 15
            self.set_font('Arial', 'B', 15)
            # Move to the right
            self.cell(80)
            # Title
            self.cell(30, 10, 'Request for Quotation (RFQ)', 0, 0, 'C')
            # Line break
            self.ln(20)

        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            # Arial italic 8
            self.set_font('Arial', 'I', 8)
            # Page number
            self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    # --- PDF Creation Logic ---
    pdf = PDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # RFQ Metadata
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'RFQ Details', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(40, 7, 'RFQ Number:', 0, 0)
    pdf.cell(0, 7, rfq_number, 0, 1)
    pdf.cell(40, 7, 'Date of Issue:', 0, 0)
    pdf.cell(0, 7, issue_date.strftime('%B %d, %Y'), 0, 1)
    pdf.cell(40, 7, 'Submission Deadline:', 0, 0)
    pdf.cell(0, 7, submission_deadline.strftime('%B %d, %Y'), 0, 1)
    pdf.ln(5)

    # Requester Info
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. Issued By', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(40, 7, 'Company:', 0, 0)
    pdf.cell(0, 7, company_name, 0, 1)
    pdf.cell(40, 7, 'Contact:', 0, 0)
    pdf.cell(0, 7, f"{contact_person} ({contact_email})", 0, 1)
    pdf.cell(40, 7, 'Address:', 0, 0)
    pdf.multi_cell(0, 7, company_address, 0, 1)
    pdf.ln(5)

    # Project Overview
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. Project Overview', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, project_description, 0, 1)
    pdf.ln(5)

    # Items Table
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '3. Requested Items/Services', 0, 1)
    pdf.set_font('Arial', 'B', 10)
    
    # Define column widths
    effective_width = pdf.w - 2 * pdf.l_margin
    col_widths = {
        "Item/Service Description": effective_width * 0.45,
        "Quantity": effective_width * 0.1,
        "Unit of Measure": effective_width * 0.2,
        "Specifications": effective_width * 0.25,
    }

    # Table Header
    for col_name in items_df.columns:
        pdf.cell(col_widths[col_name], 8, col_name, 1, 0, 'C')
    pdf.ln()

    # Table Rows
    pdf.set_font('Arial', '', 10)
    for index, row in items_df.iterrows():
        # Store current y position
        y_before = pdf.get_y()
        
        # Draw cells, using multi_cell for wrapping text
        pdf.multi_cell(col_widths["Item/Service Description"], 6, str(row["Item/Service Description"]), 1, 'L')
        y1 = pdf.get_y()
        pdf.set_xy(pdf.l_margin + col_widths["Item/Service Description"], y_before)
        
        pdf.multi_cell(col_widths["Quantity"], 6, str(row["Quantity"]), 1, 'C')
        y2 = pdf.get_y()
        pdf.set_xy(pdf.l_margin + col_widths["Item/Service Description"] + col_widths["Quantity"], y_before)
        
        pdf.multi_cell(col_widths["Unit of Measure"], 6, str(row["Unit of Measure"]), 1, 'L')
        y3 = pdf.get_y()
        pdf.set_xy(pdf.l_margin + col_widths["Item/Service Description"] + col_widths["Quantity"] + col_widths["Unit of Measure"], y_before)
        
        pdf.multi_cell(col_widths["Specifications"], 6, str(row["Specifications"]), 1, 'L')
        y4 = pdf.get_y()

        # Set Y position to the max height of the cells in the row to ensure alignment
        pdf.set_y(max(y1, y2, y3, y4))
    pdf.ln(10)
    
    # Delivery & Terms
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '4. Delivery & Commercial Terms', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(50, 7, 'Delivery/Service Location:', 0, 0)
    pdf.multi_cell(0, 7, delivery_address, 0, 1)
    pdf.cell(50, 7, 'Payment Terms:', 0, 0)
    pdf.cell(0, 7, payment_terms, 0, 1)
    pdf.ln(5)

    # Terms and Conditions
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '5. Terms and Conditions', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, terms_and_conditions, 0, 1)

    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')


# --- Streamlit App ---

st.set_page_config(page_title="SCM RFQ Generator", page_icon="📦", layout="wide")

st.title("📦 Request for Quotation (RFQ) Generator")
st.markdown("Designed for Supply Chain Management Companies")
st.markdown("---")

st.header("Create a New Request for Quotation")

with st.form(key='rfq_form'):
    st.subheader("1. Requester's Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Your Company Name *")
        contact_person = st.text_input("Contact Person *")
    with col2:
        company_address = st.text_area("Company Address *")
        contact_email = st.text_input("Contact Email *")

    st.markdown("---")
    st.subheader("2. RFQ Details")
    col1, col2 = st.columns(2)
    with col1:
        rfq_number = st.text_input("RFQ Number / Identifier", f"RFQ-{date.today().strftime('%Y%m%d')}-001")
        issue_date = st.date_input("Date of Issue", value=date.today())
    with col2:
        submission_deadline = st.date_input("Submission Deadline *", min_value=date.today())

    st.markdown("---")
    st.subheader("3. Project / Service Overview")
    project_description = st.text_area(
        "Provide a brief description of the project or services required.",
        height=150,
        placeholder="e.g., Seeking a logistics partner for warehousing and last-mile delivery..."
    )

    st.markdown("---")
    st.subheader("4. Detailed List of Required Items/Services *")
    st.info("Use the table below to list all items/services. You can add or delete rows as needed.")
    initial_items_df = pd.DataFrame(
        [{"Item/Service Description": "", "Quantity": 1, "Unit of Measure": "", "Specifications": ""}]
    )
    edited_items = st.data_editor(
        initial_items_df, num_rows="dynamic", use_container_width=True,
        column_config={
            "Item/Service Description": st.column_config.TextColumn(required=True, width="large"),
            "Quantity": st.column_config.NumberColumn(required=True, min_value=1, format="%d"),
            "Unit of Measure": st.column_config.TextColumn(required=True),
            "Specifications": st.column_config.TextColumn(width="medium"),
        }
    )

    st.markdown("---")
    st.subheader("5. Delivery & Commercial Terms")
    col1, col2 = st.columns(2)
    with col1:
        delivery_address = st.text_area("Delivery Address / Location of Service")
    with col2:
        payment_terms = st.text_input("Preferred Payment Terms", "e.g., Net 30 Days")
    terms_and_conditions = st.text_area(
        "Specific Terms and Conditions", height=150,
        placeholder="Include confidentiality requirements, insurance prerequisites, etc."
    )

    st.markdown("---")
    submit_button = st.form_submit_button(
        label='Generate RFQ', use_container_width=True, type="primary"
    )

if submit_button:
    required_fields = [company_name, contact_person, company_address, contact_email, submission_deadline]
    if not all(required_fields) or edited_items.empty or edited_items['Item/Service Description'].iloc[0] == '':
        st.error("⚠️ Please fill in all required fields marked with an asterisk (*), including at least one item/service.")
    else:
        st.success("✅ RFQ Generated Successfully!")
        
        # Generate PDF in memory
        pdf_data = create_rfq_pdf(
            rfq_number, issue_date, submission_deadline, company_name, company_address,
            contact_person, contact_email, project_description, edited_items,
            delivery_address, payment_terms, terms_and_conditions
        )
        
        st.header("Download RFQ")
        st.download_button(
            label="📥 Download RFQ Document (.pdf)",
            data=pdf_data,
            file_name=f"{rfq_number}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
        
        # Optional: Show a preview/summary on the page as well
        st.markdown("---")
        st.header("RFQ Summary Preview")
        st.markdown(f"**RFQ Number:** `{rfq_number}`")
        st.markdown(f"**Company:** {company_name}")
        st.subheader("Requested Items/Services:")
        st.dataframe(edited_items, use_container_width=True)
