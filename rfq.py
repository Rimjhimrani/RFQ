import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF
import tempfile
import os
from PIL import Image
import io
import copy

# --- App Configuration ---
st.set_page_config(
    page_title="RFQ Generator Pro",
    page_icon="🏭",
    layout="wide"
)

# --- Constants & Templates ---
CATEGORY_HINTS = {
    "Furniture": ["Office Desk", "Ergonomic Chair", "Conference Table"],
    "Electrical": ["MCB Panel", "Cable Tray", "DB Box"],
    "IT / Electronics": ["Laptop", "Network Switch", "UPS"],
    "Civil / Construction": ["Cement Bags", "TMT Steel Bars"],
    "HVAC": ["Split AC Unit", "AHU", "Chiller"],
    "Warehouse Equipment": [
        "Heavy-duty Racks", "Pallet Racking Systems", "Forklifts", "Hand Pallet Trucks",
        "Vertical Carousel System", "Dock Levellers", "Plastic Bins", "Metal Crates"
    ],
}

WAREHOUSE_GROUPS = {
    "Storage Systems": [
        "Heavy-duty Racks", "Pallet Racking Systems", "Industrial Shelving", "Mezzanine Floors",
    ],
    "Material Handling Equipment": [
        "Forklifts", "Hand Pallet Trucks", "Electric Pallet Trucks", "Stackers",
    ],
    "Automated Storage Systems": [
        "Vertical Carousel System", "Horizontal Carousel System",
    ],
    "Loading Dock Equipment": [
        "Dock Levellers", "Dock Plates", "Loading Ramps",
    ],
    "Storage Containers": [
        "Plastic Bins", "Crates", "Pallets (Wood)", "Pallets (Plastic)", "Metal Bins",
    ],
    "Warehouse Safety Equipment": [
        "Rack Protectors", "Column Guards", "Safety Barriers", "Safety Signage",
    ],
}

UNIT_OPTIONS = ["Nos", "Pieces", "Sets", "Meters", "Sq.Ft", "Sq.M", "Kg", "Tons", "Liters", "Boxes", "Rolls"]

CAROUSEL_SPEC_TEMPLATE = {
    "Model Details": [
        {"Sr": 1,  "Category": "Dimensions of VStore", "Description": "Height (mm)", "Unit": "mm", "Requirement": "28000"},
        {"Sr": "", "Category": "", "Description": "Width (mm)", "Unit": "mm", "Requirement": "3200"},
        {"Sr": "", "Category": "", "Description": "Depth (mm)", "Unit": "mm", "Requirement": "3400"},
        {"Sr": 3,  "Category": "Tray Details", "Description": "Maximum load capacity (Kg)", "Unit": "Kg", "Requirement": "465"},
    ],
}

# Column definitions for the 20-column Detailed Table
DETAILED_HEADERS = [
    "Sr.No", "Description", "Material", "Length", "Width", "Height",
    "Inner L", "Inner W", "Inner H", "UOM", "Base Type", "Colour",
    "Weight", "Load Cap", "Stackable", "Cover/Open", "Rate", "Qty",
    "Conceptual Image", "Remarks"
]
DETAILED_COL_WIDTHS = [
    12, 30, 22, 14, 14, 14, 14, 14, 14,
    14, 18, 18, 16, 18, 18, 18, 14, 12,
    28, 28
]

# ==============================================================
# PDF GENERATION CLASS
# ==============================================================
class RFQ_PDF(FPDF):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

    def header(self):
        if self.page_no() == 1: return
        # Logos
        l1 = self.data.get('logo1_data')
        if l1:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(l1); tmp.flush()
                self.image(tmp.name, x=self.l_margin, y=10, w=self.data.get('logo1_w', 30), h=self.data.get('logo1_h', 15))
                os.remove(tmp.name)
        l2 = self.data.get('logo2_data')
        if l2:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(l2); tmp.flush()
                self.image(tmp.name, x=self.w - self.r_margin - self.data.get('logo2_w', 30), y=10, w=self.data.get('logo2_w', 30), h=self.data.get('logo2_h', 15))
                os.remove(tmp.name)
        self.set_y(12); self.set_font('Arial', 'B', 14); self.cell(0, 10, 'Request for Quotation (RFQ)', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def create_cover_page(self):
        self.add_page()
        # Cover Content logic
        self.set_y(60); self.set_font('Arial', 'B', 30); self.cell(0, 15, 'Request for Quotation', 0, 1, 'C')
        self.ln(10); self.set_font('Arial', '', 18); self.cell(0, 8, 'For', 0, 1, 'C')
        self.set_font('Arial', 'B', 22); self.cell(0, 10, self.data['Type_of_items'], 0, 1, 'C')
        self.ln(5); self.set_font('Arial', 'B', 24); self.cell(0, 12, self.data['company_name'], 0, 1, 'C')
        self.set_font('Arial', '', 18); self.cell(0, 10, self.data['company_address'], 0, 1, 'C')

    def section_title(self, title):
        self.set_font('Arial', 'B', 12); self.set_fill_color(230, 230, 230)
        self.cell(0, 8, title, 0, 1, 'L', fill=True); self.ln(4)

    def draw_detailed_landscape_table(self, df, title, images_dict=None):
        """ The 20-column table logic provided by you """
        self.add_page(orientation='L')
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, title, 0, 1, 'L')

        header_height = 10
        row_height = 28
        FIXED_IMG_WIDTH = 22
        FIXED_IMG_HEIGHT = 18

        # Header
        pdf.set_font("Arial", "B", 7)
        sy = pdf.get_y(); cx = pdf.l_margin
        for i, h in enumerate(DETAILED_HEADERS):
            pdf.rect(cx, sy, DETAILED_COL_WIDTHS[i], header_height)
            pdf.set_xy(cx, sy + 2)
            pdf.multi_cell(DETAILED_COL_WIDTHS[i], 3, h, align="C")
            cx += DETAILED_COL_WIDTHS[i]
        pdf.set_y(sy + header_height)

        # Rows
        pdf.set_font("Arial", "", 7)
        for idx, row in df.iterrows():
            row_y = pdf.get_y()
            if row_y + row_height > pdf.page_break_trigger:
                pdf.add_page(orientation='L')
                # (Header would be redrawn here in production)
            
            curr_x = pdf.l_margin
            row_vals = [
                str(idx+1), row.get("Description",""), row.get("Material",""),
                row.get("Length",""), row.get("Width",""), row.get("Height",""),
                row.get("Inner L",""), row.get("Inner W",""), row.get("Inner H",""),
                row.get("UOM",""), row.get("Base Type",""), row.get("Colour",""),
                row.get("Weight",""), row.get("Load Cap",""), row.get("Stackable",""),
                row.get("Cover/Open",""), row.get("Rate",""), row.get("Qty",""),
                "", row.get("Remarks","")
            ]

            for i, val in enumerate(row_vals):
                w = DETAILED_COL_WIDTHS[i]
                pdf.rect(curr_x, row_y, w, row_height)
                if DETAILED_HEADERS[i] == "Conceptual Image":
                    img_data = None
                    if images_dict:
                        # Key matches index from loop
                        img_data = images_dict.get(idx) or images_dict.get(f"row_{idx}")
                    
                    if img_data:
                        try:
                            img = Image.open(io.BytesIO(img_data))
                            ix = curr_x + (w - FIXED_IMG_WIDTH)/2
                            iy = row_y + (row_height - FIXED_IMG_HEIGHT)/2
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                                img.save(tmp.name, format="PNG")
                                pdf.image(tmp.name, x=ix, y=iy, w=FIXED_IMG_WIDTH, h=FIXED_IMG_HEIGHT)
                            os.remove(tmp.name)
                        except: pass
                else:
                    pdf.set_xy(curr_x, row_y + 6)
                    pdf.multi_cell(w, 4, str(val), align="C")
                curr_x += w
            pdf.set_y(row_y + row_height)
        
        pdf.add_page(orientation='P')

# ==============================================================
# MAIN PDF GENERATION FUNCTION
# ==============================================================
def create_advanced_rfq_pdf(data):
    pdf = RFQ_PDF(data, 'P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.create_cover_page()
    pdf.add_page()

    # Requirement Background
    pdf.section_title('REQUIREMENT BACKGROUND')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, data['purpose'])
    pdf.ln(5)

    # Technical Specification
    pdf.section_title('TECHNICAL SPECIFICATION')
    rt = data.get('rfq_type')

    if rt == 'Item':
        pdf.draw_detailed_landscape_table(data['bin_details_df'], 'ITEM DETAILS', data.get('bin_images'))

    elif rt == 'Storage Infrastructure':
        # (Standard Rack table logic...)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 10, "Rack Details", 0, 1)
        # Simplified for brevity
        pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 10, "Detailed Rack specs follow standard portrait table.")

    elif rt == 'Dynamic':
        is_warehouse = (data.get('rfq_category') == 'Warehouse Equipment')
        
        if is_warehouse:
            groups = data.get('warehouse_groups_df', {})
            for g_name in WAREHOUSE_GROUPS.keys():
                df = groups.get(g_name, pd.DataFrame())
                if df.empty: continue
                
                if g_name == "Storage Containers":
                    # TRIGGER THE 20-COLUMN LANDSCAPE LOGIC
                    pdf.draw_detailed_landscape_table(df, 'STORAGE CONTAINER DETAILS', data.get('wh_container_images'))
                else:
                    # Standard 6-column Portrait Table
                    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 8, f"Group: {g_name}", 0, 1)
                    col_w = [10, 50, 70, 20, 20, 20]
                    hdrs = ["Sr.", "Item", "Specs", "Qty", "Unit", "Remarks"]
                    for i, h in enumerate(hdrs): pdf.cell(col_w[i], 8, h, 1, 0, 'C')
                    pdf.ln(); pdf.set_font('Arial', '', 9)
                    for i, r in df.iterrows():
                        pdf.cell(col_w[0], 8, str(i+1), 1)
                        pdf.cell(col_w[1], 8, str(r.get('Item Name','')), 1)
                        pdf.cell(col_w[2], 8, str(r.get('Description / Specification','')), 1)
                        pdf.cell(col_w[3], 8, str(r.get('Quantity','')), 1)
                        pdf.cell(col_w[4], 8, str(r.get('Unit','')), 1)
                        pdf.cell(col_w[5], 8, str(r.get('Remarks','')), 1, 1)
                    pdf.ln(5)
            
            # Additional Compulsory Warehouse sections (Carousel, Features etc)
            if not data.get('carousel_model_df', pd.DataFrame()).empty:
                pdf.section_title("Carousel / VStore Model Details")
                # ... draw carousel table ...
        else:
            # Non-warehouse dynamic items
            items_df = data.get('items_df', pd.DataFrame())
            # ... draw standard table ...

    # Final Sections: Timelines, SPOC, Commercials
    pdf.section_title("TIMELINES")
    # ... draw timeline table ...

    return bytes(pdf.output())

# ==============================================================
# STREAMLIT UI
# ==============================================================
st.title("🏭 RFQ Generator Pro")

with st.sidebar:
    st.header("1. Global Setup")
    logo1_file = st.file_uploader("Logo 1", type=['png','jpg'])
    logo2_file = st.file_uploader("Logo 2", type=['png','jpg'])
    company_name = st.text_input("Requester Name", "Pinnacle Mobility")
    company_address = st.text_input("Address", "Chakan, Pune")
    Type_of_items = st.text_input("Type of Items", "Storage Bins")
    Storage = st.text_input("Storage Area", "Raw Material Store")

st.header("Step 4: Technical Specifications")
rfq_type_choice = st.radio("RFQ Type", ["Item", "Storage Infrastructure", "Dynamic (Category-Based)"], horizontal=True)

if rfq_type_choice == "Item":
    st.subheader("20-Column Item Specification")
    if 'item_df' not in st.session_state:
        st.session_state.item_df = pd.DataFrame(columns=DETAILED_HEADERS[:-2]) # Except Image & Remarks
    
    edit_df = st.data_editor(st.session_state.item_df, num_rows="dynamic")
    st.session_state.item_df = edit_df
    # Image uploads logic...

elif rfq_type_choice == "Dynamic (Category-Based)":
    rfq_category = st.selectbox("Select Category", list(CATEGORY_HINTS.keys()))
    
    if rfq_category == "Warehouse Equipment":
        st.info("Assign items to groups. 'Storage Containers' uses detailed landscape logic.")
        wh_groups_results = {}
        wh_container_images = {}

        for group_name in WAREHOUSE_GROUPS.keys():
            with st.expander(f"📁 {group_name}", expanded=False):
                if group_name == "Storage Containers":
                    # Detailed 18-column editor (Remarks and Image handled separately/later)
                    cols = ["Description", "Material", "Length", "Width", "Height", "Inner L", "Inner W", "Inner H", 
                            "UOM", "Base Type", "Colour", "Weight", "Load Cap", "Stackable", "Cover/Open", "Rate", "Qty", "Remarks"]
                    
                    if f"df_{group_name}" not in st.session_state:
                        st.session_state[f"df_{group_name}"] = pd.DataFrame(columns=cols)
                    
                    edited = st.data_editor(st.session_state[f"df_{group_name}"], num_rows="dynamic", key=f"editor_{group_name}")
                    wh_groups_results[group_name] = edited
                    
                    # Image Uploader for each container row
                    for idx in range(len(edited)):
                        img_key = f"img_wh_{idx}"
                        f = st.file_uploader(f"Image for row {idx+1}", type=['png','jpg'], key=img_key)
                        if f: wh_container_images[idx] = f.getvalue()
                
                else:
                    # Standard 5-column editor
                    cols = ["Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"]
                    if f"df_{group_name}" not in st.session_state:
                        st.session_state[f"df_{group_name}"] = pd.DataFrame(columns=cols)
                    edited = st.data_editor(st.session_state[f"df_{group_name}"], num_rows="dynamic", key=f"editor_{group_name}")
                    wh_groups_results[group_name] = edited

        # Compulsory Warehouse Forms (Carousel, Accountability etc.)
        st.write("---")
        st.subheader("Carousel & Accountability")
        # Pre-fill session states for these tables...

# Final Form
with st.form("gen_rfq"):
    purpose = st.text_area("Purpose", "To optimize storage...")
    spoc_name = st.text_input("SPOC Name", "John Doe")
    spoc_email = st.text_input("SPOC Email", "john@pinnacle.com")
    spoc_phone = st.text_input("SPOC Phone", "9876543210")
    
    delivery_location = st.text_area("Delivery Location")
    submit_to = st.text_input("Submit To", "Agilomatrix Pvt Ltd")

    generate = st.form_submit_button("Generate RFQ PDF")

if generate:
    # Build payload
    payload = {
        'rfq_type': 'Dynamic' if rfq_type_choice == "Dynamic (Category-Based)" else rfq_type_choice,
        'rfq_category': rfq_category if rfq_type_choice == "Dynamic (Category-Based)" else "",
        'company_name': company_name, 'company_address': company_address,
        'Type_of_items': Type_of_items, 'purpose': purpose,
        'logo1_data': logo1_file.getvalue() if logo1_file else None,
        'logo2_data': logo2_file.getvalue() if logo2_file else None,
        'wh_group_data': wh_groups_results if rfq_type_choice == "Dynamic (Category-Based)" else {},
        'wh_container_images': wh_container_images if rfq_type_choice == "Dynamic (Category-Based)" else {},
        'warehouse_groups_df': wh_groups_results if rfq_type_choice == "Dynamic (Category-Based)" else {},
        'bin_details_df': st.session_state.get('item_df', pd.DataFrame()),
    }
    
    # Process and Download
    with st.spinner("Creating Document..."):
        pdf_bytes = create_advanced_rfq_pdf(payload)
        st.download_button("📥 Download RFQ", data=pdf_bytes, file_name="RFQ_Final.pdf", mime="application/pdf")
