import streamlit as st
import pandas as pd
from datetime import date

# --- App Configuration ---
st.set_page_config(
    page_title="SCM RFQ Generator",
    page_icon="📦",
    layout="wide"
)

# --- App Title and Description ---
st.title("📦 Request for Quotation (RFQ) Generator")
st.markdown("Designed for Supply Chain Management Companies")
st.markdown("---")

# --- RFQ Form ---
st.header("Create a New Request for Quotation")

# Using st.form to batch inputs
with st.form(key='rfq_form'):

    # Section 1: Requester's Information (Your Company)
    st.subheader("1. Requester's Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Your Company Name *")
        contact_person = st.text_input("Contact Person *")
    with col2:
        company_address = st.text_area("Company Address *")
        contact_email = st.text_input("Contact Email *")

    st.markdown("---")

    # Section 2: RFQ Metadata
    st.subheader("2. RFQ Details")
    col1, col2 = st.columns(2)
    with col1:
        rfq_number = st.text_input("RFQ Number / Identifier", f"RFQ-{date.today().strftime('%Y%m%d')}-001")
        issue_date = st.date_input("Date of Issue", value=date.today())
    with col2:
        submission_deadline = st.date_input("Submission Deadline *", min_value=date.today())

    st.markdown("---")

    # Section 3: Project Overview
    st.subheader("3. Project / Service Overview")
    project_description = st.text_area(
        "Provide a brief description of the project or services required.",
        height=150,
        placeholder="e.g., Seeking a logistics partner for warehousing and last-mile delivery of perishable goods in the Midwest region."
    )

    st.markdown("---")

    # Section 4: Detailed List of Goods/Services
    st.subheader("4. Detailed List of Required Items/Services *")
    st.info("Use the table below to list all the items or services you require. You can add or delete rows as needed.")

    # Create an initial DataFrame for the data editor
    initial_items_df = pd.DataFrame(
        [
            {"Item/Service Description": "e.g., Pallet Storage (per pallet/month)", "Quantity": 100, "Unit of Measure": "Pallet", "Specifications": "Standard 48x40, max height 60 inches"},
        ]
    )

    # Use st.data_editor for a dynamic, editable table
    edited_items = st.data_editor(
        initial_items_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Item/Service Description": st.column_config.TextColumn("Item/Service Description", help="Detailed description of the good or service.", required=True, width="large"),
            "Quantity": st.column_config.NumberColumn("Quantity", help="The total quantity required.", required=True, min_value=0, format="%d"),
            "Unit of Measure": st.column_config.TextColumn("Unit of Measure", help="e.g., Each, KG, Pallet, Hour, Shipment", required=True),
            "Specifications": st.column_config.TextColumn("Technical Specifications / Notes", help="Provide any relevant technical details or notes.", width="medium"),
        }
    )

    st.markdown("---")

    # Section 5: Delivery and Terms
    st.subheader("5. Delivery & Commercial Terms")
    col1, col2 = st.columns(2)
    with col1:
        delivery_address = st.text_area("Delivery Address / Location of Service", placeholder="Enter the full address for delivery or service location.")
    with col2:
        payment_terms = st.text_input("Preferred Payment Terms", "e.g., Net 30 Days")

    terms_and_conditions = st.text_area(
        "Specific Terms and Conditions",
        height=150,
        placeholder="Include any specific clauses, confidentiality requirements, insurance prerequisites, etc."
    )

    # Form Submission Button
    st.markdown("---")
    submit_button = st.form_submit_button(
        label='Generate RFQ Summary',
        use_container_width=True,
        type="primary"
    )

# --- Post-Submission Display and Download Logic ---
if submit_button:
    # Validate required fields
    required_fields = [company_name, contact_person, company_address, contact_email, submission_deadline]
    if not all(required_fields) or edited_items.empty:
        st.error("⚠️ Please fill in all required fields marked with an asterisk (*), including at least one item/service.")
    else:
        st.success("✅ RFQ Summary Generated Successfully!")
        st.balloons()

        # --- 1. Display the summarized RFQ details on the screen ---
        st.header("RFQ Summary")
        st.markdown(f"**RFQ Number:** `{rfq_number}`")
        st.markdown(f"**Date of Issue:** `{issue_date.strftime('%B %d, %Y')}`")
        st.markdown(f"**Submission Deadline:** `{submission_deadline.strftime('%B %d, %Y')}`")
        st.markdown("---")

        st.subheader("Issued By:")
        st.markdown(f"**Company:** {company_name}")
        st.markdown(f"**Address:** {company_address}")
        st.markdown(f"**Contact Person:** {contact_person} ({contact_email})")
        st.markdown("---")

        st.subheader("Project Overview:")
        st.write(project_description)
        st.markdown("---")

        st.subheader("Requested Items/Services:")
        st.dataframe(edited_items, use_container_width=True)
        st.markdown("---")

        st.subheader("Delivery & Terms:")
        st.markdown(f"**Delivery/Service Location:** {delivery_address}")
        st.markdown(f"**Payment Terms:** {payment_terms}")
        st.subheader("Terms and Conditions:")
        st.write(terms_and_conditions)
        st.markdown("---")

        # --- 2. Prepare data for Markdown download ---
        
        # Using the DataFrame's to_markdown() method creates a nicely formatted table
        items_table_md = edited_items.to_markdown(index=False)

        # Construct the full RFQ content as a Markdown string
        rfq_md_content = f"""
# Request for Quotation (RFQ)

- **RFQ Number:** `{rfq_number}`
- **Date of Issue:** `{issue_date.strftime('%B %d, %Y')}`
- **Submission Deadline:** `{submission_deadline.strftime('%B %d, %Y')}`

---

## 1. Issued By
- **Company:** {company_name}
- **Address:** \n{company_address}
- **Contact Person:** {contact_person}
- **Contact Email:** {contact_email}

---

## 2. Project Overview
{project_description}

---

## 3. Requested Items/Services
{items_table_md}

---

## 4. Delivery & Commercial Terms
- **Delivery/Service Location:** \n{delivery_address}
- **Payment Terms:** {payment_terms}

---

## 5. Terms and Conditions
{terms_and_conditions}
"""
        
        # --- 3. Display Download Button ---
        st.header("Download RFQ")
        st.download_button(
            label="📥 Download RFQ Document (.md)",
            data=rfq_md_content,
            file_name=f"{rfq_number}.md",
            mime="text/markdown",
            use_container_width=True,
            type="primary"
        )
