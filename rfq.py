import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF
import tempfile
import os
from PIL import Image
import io
import copy as _copy

# --- App Configuration ---
st.set_page_config(
    page_title="RFQ Generator",
    page_icon="🏭",
    layout="wide"
)

# --- Category Constants ---
CATEGORY_HINTS = {
    "Furniture": ["Office Desk", "Ergonomic Chair", "Conference Table", "Storage Cabinet", "Bookshelf"],
    "Electrical": ["MCB Panel", "Cable Tray", "DB Box", "Power Socket", "LED Fixture"],
    "IT / Electronics": ["Laptop", "Desktop PC", "Network Switch", "UPS", "CCTV Camera"],
    "Civil / Construction": ["Cement Bags", "TMT Steel Bars", "AAC Blocks", "Ready Mix Concrete", "Tiles"],
    "HVAC": ["Split AC Unit", "Ducted AC", "AHU", "Chiller Unit", "FCU"],
    "Plumbing": ["CPVC Pipes", "Ball Valve", "Water Pump", "Pressure Gauge", "Flow Meter"],
    "Interior / Fit-Out": ["False Ceiling", "Partition Wall", "Glass Partition", "Vinyl Flooring", "Acoustic Panel"],
    "Stationery & Office Supplies": ["A4 Paper Ream", "Ballpoint Pens", "Whiteboard", "File Folders", "Stapler"],
    "Warehouse Equipment": [
        "Heavy-duty Racks", "Pallet Racking Systems", "Industrial Shelving",
        "Cantilever Racks", "Mezzanine Floors", "Tabular Racks", "Mobile Storage Racks",
        "Forklifts", "Hand Pallet Trucks", "Electric Pallet Trucks", "Stackers",
        "Trolleys", "Conveyor Systems", "Scissor Lifts",
        "Vertical Carousel System", "Horizontal Carousel System",
        "Dock Levellers", "Dock Plates", "Loading Ramps",
        "Plastic Bins", "Crates", "Pallets (Wood)", "Pallets (Plastic)", "Pallets (Metal)", "Storage Boxes",
        "Rack Protectors", "Column Guards", "Safety Barriers",
        "Safety Mirrors", "Fire Extinguishers", "Safety Signage",
    ],
}

UNIT_OPTIONS = ["Nos", "Pieces", "Sets", "Meters", "Sq.Ft", "Sq.M", "Kg", "Tons", "Liters", "Boxes", "Rolls", "Pairs", "Lots"]

# --- Full Templates from Original File ---
STORAGE_SYSTEM_SPEC = {
    "Model Details": [
        {"Sr.no": 1,  "Category": "Dimensions of VStore",        "Description": "Height (mm)",                       "UNIT": "",       "Requirement": ""},
        {"Sr.no": "",  "Category": "",                  "Description": "Width (mm)",                    "UNIT": "Nos",    "Requirement": ""},
        {"Sr.no": "",  "Category": "",  "Description": "Depth (mm)",                        "UNIT": "mm",     "Requirement": ""},
        {"Sr.no": "",  "Category": "",                  "Description": "Floor area (m2)",                   "UNIT": "mm",     "Requirement": ""},
        {"Sr.no": "",  "Category": "",                  "Description": "1st Access Point Height (mm)",                         "UNIT": "mm",     "Requirement": ""},
        {"Sr.no": "",  "Category": "",                  "Description": "2nd Access Point Height (mm)",                    "UNIT": "m2",     "Requirement": ""},
        {"Sr.no": "",  "Category": "",    "Description": "3rd Access Point Height (mm)",                 "UNIT": "Kg",     "Requirement": ""},
        {"Sr.no": "",  "Category": "",                  "Description": "4th Access Point Height (mm)",           "UNIT": "Kg",     "Requirement": ""},
        {"Sr.no": "",  "Category": "",            "Description": "Dead weight of Machine (Kg)",           "UNIT": "Nos",    "Requirement": ""},
        {"Sr.no": "",  "Category": "",          "Description": "Total Weight of Tray (Kg)",                     "UNIT": "",       "Requirement": "MS Steel"},
        {"Sr.no": "",  "Category": "",                  "Description": "Total Weight of Machine (Kg)",                     "UNIT": "",       "Requirement": "Powder Coated"},
        {"Sr.no": "",  "Category": "",       "Description": "Storage capacity (Kg)",                          "UNIT": "",       "Requirement": ""},
        {"Sr.no": "",  "Category": "",                  "Description": "Total Machine carrying capacity",                         "UNIT": "",       "Requirement": ""},
        {"Sr.no": "",  "Category": "",                  "Description": "Total full weight (Kg)",                        "UNIT": "",       "Requirement": ""},
        {"Sr.no": 2,  "Category": "Floor Load",      "Description": "Total (Kgs/sqm)",              "UNIT": "Yes/No", "Requirement": ""},
        {"Sr.no": 3,  "Category": "Tray Details",         "Description": "Usable width (mm)",                    "UNIT": "",       "Requirement": ""},
        {"Sr.no": "",  "Category": "",          "Description": "Usable depth (mm)",            "UNIT": "Nos",    "Requirement": ""},
        {"Sr.no": "", "Category": "",          "Description": "Empty Tray weight",         "UNIT": "Weeks",  "Requirement": ""},
        {"Sr.no": "", "Category": "",           "Description": "Area of each Trays (mm)",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": "", "Category": "",           "Description": "Maximim Load capacity(Kg)",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": "", "Category": "",           "Description": "Number of Trays (Nos.)",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": "", "Category": "",           "Description": "Total area of all Trays(m2)",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": 4, "Category": "Access time",           "Description": "Maximum (Sec.)",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": "", "Category": "",           "Description": "Average (Sec.)",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": 5, "Category": "No Trays can Fetch",           "Description": "No trays/ Hour",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": 6, "Category": "Power Supply",           "Description": "",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": 7, "Category": "Maximum Power rating",           "Description": "",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": 8, "Category": "Control Panel",           "Description": "VStore standard control panel",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": 9, "Category": "Height Optimisation",           "Description": "Provided for storage",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": 10, "Category": "Operator Panel",           "Description": "",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": 11, "Category": "Accessories",           "Description": "Emergency stop",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": "", "Category": "",           "Description": "Accident protection light curtains",        "UNIT": "",       "Requirement": ""},
        {"Sr.no": "", "Category": "",           "Description": "Lighting in the accessing areaa",        "UNIT": "",       "Requirement": ""},
    ],
    "Key Features": [
        {"Sr.no": 1,  "Description": "Material Tracking",                   "Status": "YES", "Remarks": "All key features to be confirmed by vendor."},
        {"Sr.no": 2,  "Description": "Tray Details","Status": "YES", "Remarks": ""},
        {"Sr.no": 3,  "Description": "Inventory List",               "Status": "YES", "Remarks": ""},
        {"Sr.no": 4,  "Description": "Tray Call History",                        "Status": "YES", "Remarks": ""},
        {"Sr.no": 5,  "Description": "Alarm History",                     "Status": "YES", "Remarks": ""},
        {"Sr.no": 6,  "Description": "Item Code Search",                         "Status": "YES", "Remarks": ""},
        {"Sr.no": 7,  "Description": "Bar Code Search",       "Status": "YES", "Remarks": ""},
        {"Sr.no": 8,  "Description": "Pick from BOM",                    "Status": "YES", "Remarks": ""},
        {"Sr.no": 9,  "Description": "BOM Items List",            "Status": "YES", "Remarks": ""},
        {"Sr.no": 10, "Description": "User Management, with backup and restore options",       "Status": "YES", "Remarks": ""},
    ],
    "Inbuilt features": [
        {"Sr.no": 1,  "Description": "Ergonomic tray positioning",           "Vendor Scope (Yes/No)": "YES", "Remarks": "All features to be included at vendor side."},
        {"Sr.no": 2,  "Description": "Variable frequency drives",                       "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 3,  "Description": "Tray uneven positioning sensor",                 "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 4,  "Description": "Light barrier for sensing material and operator intervention", "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 5,  "Description": "Operator Panel with IPC", "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 6,  "Description": "Weight management system for sensing tray overload",          "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 7,  "Description": "Tray Block option for Multiple users",          "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 8,  "Description": "Password authentication",            "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 9,  "Description": "Tray guide rail @ 50 pitch",                     "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 10, "Description": "Total machine capacity 60 tone",        "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 11, "Description": "Expansion at later stage is possible",        "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
        {"Sr.no": 12, "Description": "Inventory manangement software",        "Vendor Scope (Yes/No)": "YES", "Remarks": ""},
    ],
    "Installation Accountability": [
        {"Sr.no": 1,  "Category": "Inventory Management Suite (IPC)",                 "Vendor Scope (Yes/No)": "YES", "Customer Scope\n(Yes/No)": "NO", "Remarks": ""},
        {"Sr.no": 2,  "Category": "Packing, Freight & Transit Insurance",          "Vendor Scope (Yes/No)": "YES", "Customer Scope\n(Yes/No)": "NO", "Remarks": ""},
        {"Sr.no": 3,  "Category": "Installation & Commissioning",                 "Vendor Scope (Yes/No)": "YES", "Customer Scope\n(Yes/No)": "NO", "Remarks": ""},
        {"Sr.no": 4,  "Category": "Training",                  "Vendor Scope (Yes/No)": "YES", "Customer Scope\n(Yes/No)": "NO", "Remarks": ""},
        {"Sr.no": 5,  "Category": "Warranty Period","Vendor Scope (Yes/No)": "YES", "Customer Scope\n(Yes/No)": "NO", "Remarks": ""},
        {"Sr.no": 6,  "Category": "Unloading of material","Vendor Scope (Yes/No)": "NO", "Customer Scope\n(Yes/No)": "YES", "Remarks": ""},
    ],
}

# --- PDF Generation with Merged Column Logic ---
class RFQ_PDF(FPDF):
    def __init__(self, data):
        super().__init__('P', 'mm', 'A4')
        self.data = data
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            if self.data.get('logo1_data'):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(self.data['logo1_data']); tmp.flush()
                    self.image(tmp.name, x=150, y=10, w=40)
                    os.remove(tmp.name)
            self.set_y(15)
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, "Request for Quotation", 0, 1, 'C')

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, self.data.get('footer_company_name', 'Agilomatrix Private Ltd'), 0, 1, 'C')
        self.set_font('Arial', '', 7)
        self.cell(0, 5, self.data.get('footer_company_address', ''), 0, 1, 'C')
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} of {{nb}}', 0, 0, 'R')

    def render_merged_model_details(self, df, title, subtitle=""):
        self.ln(5)
        cw = [10, 45, 75, 20, 40] 
        total_w = sum(cw)
        rh = 7 

        # Table Blue Header
        self.set_fill_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(total_w, 8, title, border=1, ln=1, align='C')
        if subtitle:
            self.set_font('Arial', 'B', 9)
            self.cell(total_w, 8, subtitle, border=1, ln=1, align='C')

        # Column Names
        self.set_fill_color(220, 230, 241)
        self.set_font('Arial', 'B', 8)
        cols = ["Sr.no", "Category", "Description", "UNIT", "Requirement"]
        for i, c in enumerate(cols):
            self.cell(cw[i], 8, c, border=1, align='C', fill=True)
        self.ln()

        # Grouping for Merged Cells
        rows_list = df.to_dict('records')
        groups = []
        if rows_list:
            curr_group = [rows_list[0]]
            for i in range(1, len(rows_list)):
                if str(rows_list[i]["Sr.no"]).strip() != "" or str(rows_list[i]["Category"]).strip() != "":
                    groups.append(curr_group)
                    curr_group = [rows_list[i]]
                else:
                    curr_group.append(rows_list[i])
            groups.append(curr_group)

        self.set_font('Arial', '', 8)
        for grp in groups:
            group_h = len(grp) * rh
            if self.get_y() + group_h > 270: self.add_page()

            start_x, start_y = self.get_x(), self.get_y()

            # Column 1 & 2: Merged Sr.no and Category
            self.rect(start_x, start_y, cw[0], group_h)
            self.set_xy(start_x, start_y + (group_h/2) - 3)
            self.cell(cw[0], 6, str(grp[0]["Sr.no"]), align='C')

            self.rect(start_x + cw[0], start_y, cw[1], group_h)
            self.set_xy(start_x + cw[0] + 1, start_y + (group_h/2) - 3)
            self.multi_cell(cw[1] - 2, 4, str(grp[0]["Category"]), align='L')

            # Column 3, 4, 5: Row by Row
            for idx, item in enumerate(grp):
                row_y = start_y + (idx * rh)
                self.set_xy(start_x + cw[0] + cw[1], row_y)
                self.cell(cw[2], rh, str(item["Description"]), border=1)
                self.cell(cw[3], rh, str(item["UNIT"]), border=1, align='C')
                # Yellow Requirement Column
                self.set_fill_color(255, 255, 204)
                self.cell(cw[4], rh, str(item["Requirement"]), border=1, align='C', fill=True)
            self.set_y(start_y + group_h)

    def render_navy_table(self, title, df, col_widths):
        self.ln(5)
        total_w = sum(col_widths)
        self.set_fill_color(26, 58, 92)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        self.cell(total_w, 8, f"  {title}", 0, 1, 'L', fill=True)
        self.set_text_color(0, 0, 0)
        
        self.set_fill_color(220, 230, 241)
        self.set_font('Arial', 'B', 8)
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], 8, col, border=1, align='C', fill=True)
        self.ln()
        
        self.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            if self.get_y() > 270: self.add_page()
            x = self.get_x()
            y = self.get_y()
            for i, val in enumerate(row):
                self.set_xy(x + sum(col_widths[:i]), y)
                self.multi_cell(col_widths[i], 7, str(val), border=1, align='L')
            self.set_y(y + 7)

# --- Streamlit UI ---
st.title("Request For Quotation Generator")

# Step 1: Branding
with st.expander("Step 1: Branding", expanded=True):
    logo1 = st.file_uploader("Upload Company Logo", type=['png', 'jpg'])

# Step 2: Cover Details
with st.expander("Step 2: Cover Details", expanded=True):
    t_items = st.text_input("Type of Items*", value="Carousel Racking System on Ground Floor + 3Floor")
    c_name = st.text_input("Requester Company Name*", value="Pinnacle Mobility Solutions Pvt Ltd")
    c_addr = st.text_area("Requester Address*", value="Pithampur, MP.")

# Step 4: Technical Specs (The Core Request)
with st.expander("Step 4: Technical Specifications", expanded=True):
    wh_sub = st.selectbox("Select Category", ["Storage System", "Material Handling", "Automated Storage System", "Dock Leveller"])
    
    st.markdown("##### Model Detail Header")
    m_header = st.text_input("Header Subtitle", "3400 (L) x 3200 (W) - 465 kgs/tray - 28 m Height")

    # Load All Original Data into Editors
    st.markdown("### Model Details (Merged Table)")
    df_model = st.data_editor(pd.DataFrame(STORAGE_SYSTEM_SPEC["Model Details"]), num_rows="dynamic", use_container_width=True)

    st.markdown("### Key Features")
    df_key = st.data_editor(pd.DataFrame(STORAGE_SYSTEM_SPEC["Key Features"]), num_rows="dynamic", use_container_width=True)

    st.markdown("### Inbuilt Features")
    df_inbuilt = st.data_editor(pd.DataFrame(STORAGE_SYSTEM_SPEC["Inbuilt features"]), num_rows="dynamic", use_container_width=True)

    st.markdown("### Installation Accountability")
    df_install = st.data_editor(pd.DataFrame(STORAGE_SYSTEM_SPEC["Installation Accountability"]), num_rows="dynamic", use_container_width=True)

    st.markdown("### Layout Photos (Min 1, Max 5)")
    layout_pics = st.file_uploader("Upload Layout Drawings", accept_multiple_files=True, type=['png','jpg','jpeg'])
    if layout_pics:
        st.write(f"Uploaded {len(layout_pics)} images.")

# Step 5: Submission Details
with st.expander("Step 5: Contact Information"):
    purpose = st.text_area("Purpose", "Pinnacle Mobility Solutions is expanding production...")
    sub_to = st.text_input("Submit To Name", "Pinnacle Mobility Solutions Pvt. Ltd.")
    sub_addr = st.text_area("Submit To Address", "SAI RADHE Complex, Pune - 411 001")
    del_loc = st.text_area("Delivery Location", "EKA Mobility, Pithampur Indore")

# PDF Generation Execution
if st.button("Generate RFQ PDF", type="primary", use_container_width=True):
    pdf_data = {
        'logo1_data': logo1.getvalue() if logo1 else None,
        'Type_of_items': t_items,
        'company_name': c_name,
        'company_address': c_addr,
        'purpose': purpose,
        'model_header': m_header,
        'model_df': df_model,
        'key_df': df_key,
        'inbuilt_df': df_inbuilt,
        'install_df': df_install,
        'layout_images': [f.getvalue() for f in layout_pics] if layout_pics else [],
        'submit_to_name': sub_to,
        'submit_to_address': sub_addr,
        'delivery_location': del_loc,
        'footer_company_address': "F1403, 7 Plumeria Drive, Pune - 411033"
    }
    
    pdf = RFQ_PDF(pdf_data)
    pdf.alias_nb_pages()
    
    # 1. Cover
    pdf.add_page()
    pdf.set_y(30); pdf.set_text_color(255, 0, 0); pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "CONFIDENTIAL", 0, 1)
    pdf.set_y(60); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', 'B', 28); pdf.cell(0, 20, "Request for Quotation", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 20); pdf.multi_cell(0, 10, t_items, 0, 'C')
    pdf.ln(10); pdf.set_font('Arial', '', 18); pdf.cell(0, 10, "At", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 22); pdf.cell(0, 10, c_name, 0, 1, 'C')
    pdf.set_font('Arial', '', 18); pdf.multi_cell(0, 10, c_addr, 0, 'C')
    
    # 2. Specs
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "Requirement Background:", 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 6, purpose)
    pdf.render_merged_model_details(df_model, "Model Details", m_header)
    
    # 3. Features
    pdf.add_page()
    pdf.render_navy_table("Inbuilt features", df_inbuilt, [10, 100, 30, 50])
    pdf.render_navy_table("Key Features", df_key, [10, 100, 30, 50])
    
    # 4. Installation & Layout
    pdf.add_page()
    pdf.render_navy_table("Installation Accountability", df_install, [10, 75, 28, 28, 49])
    
    if pdf_data['layout_images']:
        pdf.ln(10); pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "Layout:-", 0, 1)
        for img_bytes in pdf_data['layout_images']:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(img_bytes); tmp.flush()
                if pdf.get_y() > 220: pdf.add_page()
                pdf.image(tmp.name, w=120)
                pdf.ln(10)

    # 5. Delivery Details
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "Key Inputs:", 0, 1)
    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 10, "o Quotation to be submit to:", 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, f"{sub_to}\n{sub_addr}")
    pdf.ln(5); pdf.set_font('Arial', 'B', 10); pdf.cell(0, 10, "o Delivery Location:", 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, del_loc)

    final_pdf = pdf.output(dest='S').encode('latin-1')
    st.download_button("Download RFQ Document", data=final_pdf, file_name="RFQ_Generated.pdf", mime="application/pdf", use_container_width=True)
