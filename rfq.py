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

# --- Category suggestion hints ---
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

WAREHOUSE_GROUPS = {
    "Storage Systems": [
        "Heavy-duty Racks", "Pallet Racking Systems", "Industrial Shelving",
        "Cantilever Racks", "Mezzanine Floors", "Tabular Racks", "Mobile Storage Racks",
    ],
    "Material Handling Equipment": [
        "Forklifts", "Hand Pallet Trucks", "Electric Pallet Trucks", "Stackers",
        "Trolleys", "Conveyor Systems", "Scissor Lifts",
    ],
    "Automated Storage Systems": [
        "Vertical Carousel System", "Horizontal Carousel System",
    ],
    "Loading Dock Equipment": [
        "Dock Levellers", "Dock Plates", "Loading Ramps",
    ],
}

STORAGE_CONTAINERS_ITEMS = [
    "Plastic Bins", "Crates", "Pallets (Wood)", "Pallets (Plastic)", "Pallets (Metal)", "Storage Boxes",
]

# ─────────────────────────────────────────────────────────────────────────────
# SPEC TABLE DATA — Full original templates
# ─────────────────────────────────────────────────────────────────────────────

# ── STORAGE SYSTEM ────────────────────────────────────────────────────────────
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
        {"Sr.no": 1,  "Description": "Material Tracking",                   "Status": "", "Remarks": "All key features to be confirmed by vendor."},
        {"Sr.no": 2,  "Description": "Tray Details","Status": "", "Remarks": ""},
        {"Sr.no": 3,  "Description": "Inventory List",               "Status": "", "Remarks": ""},
        {"Sr.no": 4,  "Description": "Tray Call History",                        "Status": "", "Remarks": ""},
        {"Sr.no": 5,  "Description": "Alarm History",                     "Status": "", "Remarks": ""},
        {"Sr.no": 6,  "Description": "Item Code Search",                         "Status": "", "Remarks": ""},
        {"Sr.no": 7,  "Description": "Bar Code Search",       "Status": "", "Remarks": ""},
        {"Sr.no": 8,  "Description": "Pick from BOM",                    "Status": "", "Remarks": ""},
        {"Sr.no": 9,  "Description": "BOM Items List",            "Status": "", "Remarks": ""},
        {"Sr.no": 10, "Description": "User Management, with backuo and restore options",       "Status": "", "Remarks": ""},
    ],
    "Inbuilt features": [
        {"Sr.no": 1,  "Description": "Ergonomic tray positioning",           "Vendor Scope (Yes/No)": "", "Remarks": "All features to be included at vendor side."},
        {"Sr.no": 2,  "Description": "Variable frequency drives",                       "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 3,  "Description": "Tray uneven positioning sensor",                 "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 4,  "Description": "Light barrier for sensing material and operator intervention", "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 5,  "Description": "Operator Panel with IPC", "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 6,  "Description": "Weight management system for sensing tray overload",          "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 7,  "Description": "Tray Block option for Multiple users",          "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 8,  "Description": "Password authentication",            "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 9,  "Description": "Tray guide rail @ 50 pitch",                     "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 10, "Description": "Total machine capacity 60 tone",        "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 11, "Description": "Expansion at later stage is possible",        "Vendor Scope (Yes/No)": "", "Remarks": ""},
        {"Sr.no": 12, "Description": "Inventory manangement software",        "Vendor Scope (Yes/No)": "", "Remarks": ""},
    ],
    "Installation Accountability": [
        {"Sr.no": 1,  "Category": "Inventory Management Suite (IPC)",                 "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 2,  "Category": "Packing, Freight & Transit Insurance",          "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 3,  "Category": "Installation & Commissioning",                 "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 4,  "Category": "Training",                  "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 5,  "Category": "Warranty Period","Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 6,  "Category": "Unloading of material","Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 7,  "Category": "Material handling during the installation",                "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 8,  "Category": "Power cable cost main junction Box to Vstore",        "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 9, "Category": "Biometric Access, Barcode Scanner",  "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 10, "Category": "MS Office",  "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 11, "Category": "Software Customization",  "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 12, "Category": "Machine Integration with ERP system will extra at Actual",  "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 13, "Category": "UPS and Stabilizer with accessories Installation",  "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 14, "Category": "Equipment Movement & Installation location",  "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
        {"Sr.no": 15, "Category": "PEB Cladding and Civil Floor for outside installation",  "Vendor Scope (Yes/No)": "", "Customer Scope\n(Yes/No)": "", "Remarks": ""},
    ],
}

# --- Copying similar logic for Dock Leveller and Material Handling as per original file ---
MATERIAL_HANDLING_SPEC = copy_of_ss = _copy.deepcopy(STORAGE_SYSTEM_SPEC)
DOCK_LEVELLER_SPEC = _copy.deepcopy(STORAGE_SYSTEM_SPEC)
CAROUSEL_SPEC_TEMPLATE = _copy.deepcopy(STORAGE_SYSTEM_SPEC)

ITEM_TABLE_HEADERS = [
    "Sr.No", "Description", "Material", "Length", "Width", "Height",
    "Inner L", "Inner W", "Inner H", "UOM", "Base Type", "Colour",
    "Weight", "Load Cap", "Stackable", "Cover/Open", "Rate", "Qty",
    "Conceptual Image", "Remarks"
]
ITEM_TABLE_COL_WIDTHS = [12, 30, 22, 14, 14, 14, 14, 14, 14, 14, 18, 18, 16, 18, 18, 18, 14, 12, 28, 28]

UNIT_OPTIONS = ["Nos", "Pieces", "Sets", "Meters", "Sq.Ft", "Sq.M", "Kg", "Tons", "Liters", "Boxes", "Rolls", "Pairs", "Lots"]

def _empty_container_row(sr=1):
    return {
        "Sr.No": sr, "Description": "", "Material Type": "Plastic", "Length": "", "Width": "", "Height": "",
        "Inner Length": "", "Inner Width": "", "Inner Height": "", "Unit of Measurement": "Nos",
        "Base Type": "Flat", "Colour": "", "Weight Kg": "", "Load capacity": "", "Stackable": "Yes",
        "BIn Cover/ Open": "Open", "Rate": "", "Qty": 1, "Remarks": ""
    }

# ==============================================================
# PDF Generation Function (Full restoration)
# ==============================================================
def create_advanced_rfq_pdf(data):
    class PDF(FPDF):
        def header(self):
            if self.page_no() == 1: return
            logo1_data = data.get('logo1_data')
            if logo1_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo1_data); tmp.flush()
                    self.image(tmp.name, x=150, y=10, w=40)
                    os.remove(tmp.name)
            self.set_y(12); self.set_font('Arial', 'B', 16); self.cell(0, 10, 'Request for Quotation (RFQ)', 0, 1, 'C')
            self.ln(15)

        def footer(self):
            self.set_y(-25)
            footer_name, footer_addr = data.get('footer_company_name'), data.get('footer_company_address')
            if footer_name or footer_addr:
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y()); self.ln(3)
                if footer_name: self.set_font('Arial', 'B', 12); self.cell(0, 5, footer_name, 0, 1, 'C')
                if footer_addr: self.set_font('Arial', '', 8); self.cell(0, 5, footer_addr, 0, 1, 'C')
            self.set_y(-15); self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

        def section_title(self, title):
            self.set_font('Arial', 'B', 12); self.set_fill_color(230, 230, 230)
            self.cell(0, 8, title, 0, 1, 'L', fill=True); self.ln(4)

        def render_merged_model_details(self, df, title="Model Details", subtitle=""):
            if df is None or df.empty: return
            cw = [10, 45, 75, 20, 40] 
            total_w = sum(cw); rh = 7
            self.set_font('Arial', 'B', 11); self.cell(total_w, 8, title, border=1, ln=1, align='C')
            if subtitle: self.set_font('Arial', 'B', 9); self.cell(total_w, 8, subtitle, border=1, ln=1, align='C')
            self.set_fill_color(220, 230, 241); self.set_font('Arial', 'B', 8)
            cols = ["Sr.no", "Category", "Description", "UNIT", "Requirement"]
            for i, c in enumerate(cols): self.cell(cw[i], 8, c, border=1, align='C', fill=True)
            self.ln()

            def _clean(v): return "" if pd.isna(v) or str(v).lower()=="nan" else str(v)
            rows_list = df.to_dict('records')
            groups = []
            if rows_list:
                curr = [rows_list[0]]
                for i in range(1, len(rows_list)):
                    if _clean(rows_list[i].get("Sr.no")) != "" or _clean(rows_list[i].get("Category")) != "":
                        groups.append(curr); curr = [rows_list[i]]
                    else: curr.append(rows_list[i])
                groups.append(curr)

            self.set_font('Arial', '', 8)
            for grp in groups:
                gh = len(grp) * rh
                if self.get_y() + gh > 270: self.add_page()
                sx, sy = self.get_x(), self.get_y()
                self.rect(sx, sy, cw[0], gh); self.set_xy(sx, sy + (gh/2) - 3); self.cell(cw[0], 6, _clean(grp[0]["Sr.no"]), align='C')
                self.rect(sx+cw[0], sy, cw[1], gh); self.set_xy(sx+cw[0]+1, sy + (gh/2)-3); self.multi_cell(cw[1]-2, 4, _clean(grp[0]["Category"]), align='L')
                for idx, row in enumerate(grp):
                    ry = sy + (idx * rh); self.set_xy(sx+cw[0]+cw[1], ry); self.cell(cw[2], rh, _clean(row["Description"]), border=1)
                    self.cell(cw[3], rh, _clean(row["UNIT"]), border=1, align='C'); self.set_fill_color(255, 255, 204)
                    self.cell(cw[4], rh, _clean(row["Requirement"]), border=1, align='C', fill=True)
                self.set_y(sy + gh)

        def render_navy_section(self, title, df, cols, widths):
            if df is None or df.empty: return
            self.set_fill_color(26, 58, 92); self.set_text_color(255, 255, 255); self.set_font('Arial', 'B', 10)
            self.cell(sum(widths), 8, f"  {title}", 0, 1, 'L', fill=True); self.set_text_color(0, 0, 0)
            self.set_fill_color(220, 230, 241); self.set_font('Arial', 'B', 8)
            for i, c in enumerate(cols): self.cell(widths[i], 8, c, border=1, align='C', fill=True)
            self.ln(); self.set_font('Arial', '', 8)
            for _, row in df.iterrows():
                if self.get_y() + 8 > 270: self.add_page()
                cx = self.l_margin; cy = self.get_y()
                for i, c in enumerate(cols):
                    self.set_xy(cx, cy); self.multi_cell(widths[i], 8, str(row.get(c, "")), border=1, align='L' if i==1 else 'C')
                    cx += widths[i]
                self.ln(0)

    pdf = PDF('P', 'mm', 'A4'); pdf.alias_nb_pages(); pdf.add_page()
    
    # --- Cover Page ---
    if data.get('logo1_data'):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(data['logo1_data']); tmp.flush()
            pdf.image(tmp.name, x=150, y=10, w=40); os.remove(tmp.name)
    pdf.set_y(40); pdf.set_font('Arial', 'B', 14); pdf.set_text_color(255, 0, 0); pdf.cell(0, 10, 'CONFIDENTIAL'); pdf.set_text_color(0, 0, 0)
    pdf.set_y(60); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 15, 'Request for Quotation', 0, 1, 'C')
    pdf.set_font('Arial', '', 18); pdf.cell(0, 8, 'For', 0, 1, 'C'); pdf.set_font('Arial', 'B', 22); pdf.cell(0, 8, data['Type_of_items'], 0, 1, 'C')
    pdf.set_font('Arial', '', 18); pdf.cell(0, 8, 'At', 0, 1, 'C'); pdf.set_font('Arial', 'B', 24); pdf.cell(0, 10, data['company_name'], 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.multi_cell(0, 10, data['company_address'], 0, 'C')

    # --- Section 1: Background ---
    pdf.add_page(); pdf.section_title('REQUIREMENT BACKGROUND'); pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 6, data['purpose']); pdf.ln(5)

    # --- Section 2: Technical Specs ---
    pdf.section_title('TECHNICAL SPECIFICATION')
    wh_sub = data.get('wh_sub')
    if wh_sub in ["Storage System", "Material Handling", "Automated Storage System", "Dock Leveller"]:
        pfx = {'Storage System':'ss', 'Material Handling':'mh', 'Automated Storage System':'carousel', 'Dock Leveller':'dl'}.get(wh_sub)
        pdf.render_merged_model_details(data.get(f'spec_{pfx}_Model Details'), title="Model Details", subtitle=data.get('model_detail_header'))
        pdf.render_navy_section("Key Features", data.get(f'spec_{pfx}_Key Features'), ["Sr.no", "Description", "Status", "Remarks"], [10, 110, 30, 40])
        pdf.render_navy_section("Inbuilt features", data.get(f'spec_{pfx}_Inbuilt features'), ["Sr.no", "Description", "Vendor Scope (Yes/No)", "Remarks"], [10, 110, 30, 40])
        pdf.render_navy_section("Installation Accountability", data.get(f'spec_{pfx}_Installation Accountability'), ["Sr.no", "Category", "Vendor Scope (Yes/No)", "Customer Scope\n(Yes/No)", "Remarks"], [10, 75, 28, 28, 49])

    # Layout Page
    if data.get('layout_pics'):
        pdf.add_page(); pdf.section_title('LAYOUT DRAWINGS'); pdf.ln(5)
        for img_bytes in data['layout_pics']:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(img_bytes); tmp.flush()
                if pdf.get_y() > 200: pdf.add_page()
                pdf.image(tmp.name, w=150); pdf.ln(10); os.remove(tmp.name)

    # --- Section 3: Timelines ---
    pdf.add_page(); pdf.section_title('TIMELINES'); pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Milestone', 1, 0, 'C'); pdf.cell(110, 8, 'Date', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    tls = [("Date of RFQ Release", data['date_release']), ("Query Resolution", data['date_query']), ("Vendor Selection", data['date_selection']), ("Delivery Deadline", data['date_delivery']), ("Installation Deadline", data['date_install'])]
    for m, d in tls: pdf.cell(80, 8, m, 1, 0, 'L'); pdf.cell(110, 8, d.strftime('%B %d, %Y'), 1, 1, 'L')

    # --- Section 4: SPOC & Commercials ---
    pdf.ln(5); pdf.section_title('SPOC & COMMERCIALS')
    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 6, f"Primary SPOC: {data['spoc1_name']} | {data['spoc1_email']}", 0, 1); pdf.ln(5)
    pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Cost Component', 1, 0, 'C'); pdf.cell(40, 8, 'Amount', 1, 0, 'C'); pdf.cell(70, 8, 'Remarks', 1, 1, 'C')
    for _, r in data['commercial_df'].iterrows(): pdf.cell(80, 8, str(r['Cost Component']), 1, 0); pdf.cell(40, 8, '', 1, 0); pdf.cell(70, 8, str(r['Remarks']), 1, 1)

    # --- Footer Info ---
    pdf.ln(10); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 8, 'Submission & Delivery', 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 6, f"Submit to: {data['submit_to_name']}\nLocation: {data['delivery_location']}")

    return bytes(pdf.output())

# ================================================================
# STREAMLIT UI - (Steps Restore)
# ================================================================
st.title("🏭 RFQ Generator")

with st.expander("Step 1: Logos", expanded=True):
    logo1_file = st.file_uploader("Upload Company Logo", type=['png', 'jpg'])

with st.expander("Step 2: Cover Details", expanded=True):
    Type_of_items = st.text_input("Type of Items*", "Carousel Racking System")
    company_name = st.text_input("Requester Company Name*", "Pinnacle Mobility Solutions Pvt Ltd")
    company_address = st.text_area("Requester Address*", "Pithampur, MP.")

with st.expander("Step 3: Footer Details"):
    footer_company_name = st.text_input("Footer Company Name", "Agilomatrix Private Ltd")
    footer_company_address = st.text_input("Footer Address", "Tathawade, Pune - 411033")

st.subheader("Step 4: Technical Specifications")
with st.expander("📦 Core Specifications", expanded=True):
    rfq_category = st.selectbox("Category", ["Warehouse Equipment", "Furniture", "Electrical"])
    wh_sub = st.selectbox("Warehouse Type", ["Storage System", "Material Handling", "Automated Storage System", "Dock Leveller", "Storage Container"])
    
    m_header = st.text_input("Model Detail Header", "3400 (L) x 3200 (W) - 465 kgs/tray")
    
    # Render Editable Tables
    prefix_map = {'Storage System':'ss', 'Material Handling':'mh', 'Automated Storage System':'carousel', 'Dock Leveller':'dl'}
    pfx = prefix_map.get(wh_sub, 'ss')
    
    st.markdown("##### Model Details (Merged Column View)")
    df_m = st.data_editor(pd.DataFrame(STORAGE_SYSTEM_SPEC["Model Details"]), num_rows="dynamic", key="m_edit", use_container_width=True)
    st.markdown("##### Key Features")
    df_k = st.data_editor(pd.DataFrame(STORAGE_SYSTEM_SPEC["Key Features"]), num_rows="dynamic", key="k_edit", use_container_width=True)
    st.markdown("##### Inbuilt Features")
    df_i = st.data_editor(pd.DataFrame(STORAGE_SYSTEM_SPEC["Inbuilt features"]), num_rows="dynamic", key="i_edit", use_container_width=True)
    st.markdown("##### Installation Accountability")
    df_a = st.data_editor(pd.DataFrame(STORAGE_SYSTEM_SPEC["Installation Accountability"]), num_rows="dynamic", key="a_edit", use_container_width=True)

    st.markdown("##### Layout Upload (1-5 Photos)")
    layout_files = st.file_uploader("Upload Drawings", accept_multiple_files=True, type=['png','jpg','jpeg'], key="layout_up")

# Steps 5-9: Restoring original form steps
with st.form("complete_form"):
    purpose = st.text_area("Purpose of Requirement*", "Pinnacle is expanding its facility...")
    
    st.markdown("##### Timelines")
    c1, c2 = st.columns(2)
    date_release = c1.date_input("Release Date", date.today())
    date_query = c1.date_input("Query Deadline", date.today() + timedelta(7))
    date_selection = c2.date_input("Selection Date", date.today() + timedelta(14))
    date_delivery = c2.date_input("Delivery Deadline", date.today() + timedelta(30))
    date_install = c2.date_input("Installation Deadline", date.today() + timedelta(45))
    
    st.markdown("##### Contact & Commercials")
    spoc1_name = st.text_input("SPOC Name", "Mr. Pankaj")
    spoc1_email = st.text_input("SPOC Email", "pankaj@example.com")
    
    comm_df = st.data_editor(pd.DataFrame([{"Cost Component": "Unit Cost", "Remarks": ""}, {"Cost Component": "Freight", "Remarks": ""}]), num_rows="dynamic")
    
    submit_to_name = st.text_input("Submit To", "Agilomatrix Pvt Ltd")
    delivery_location = st.text_area("Delivery Location", "Pithampur, MP")
    
    submitted = st.form_submit_button("Generate Complete RFQ PDF", use_container_width=True, type="primary")

if submitted:
    common_data = {
        'logo1_data': logo1_file.getvalue() if logo1_file else None,
        'Type_of_items': Type_of_items, 'company_name': company_name, 'company_address': company_address,
        'footer_company_name': footer_company_name, 'footer_company_address': footer_company_address,
        'purpose': purpose, 'wh_sub': wh_sub, 'model_detail_header': m_header,
        'date_release': date_release, 'date_query': date_query, 'date_selection': date_selection, 
        'date_delivery': date_delivery, 'date_install': date_install,
        'spoc1_name': spoc1_name, 'spoc1_email': spoc1_email, 'commercial_df': comm_df,
        'submit_to_name': submit_to_name, 'delivery_location': delivery_location,
        'layout_pics': [f.getvalue() for f in layout_files] if layout_files else [],
    }
    # Map the edited tables
    pfx = prefix_map.get(wh_sub, 'ss')
    common_data[f'spec_{pfx}_Model Details'] = df_m
    common_data[f'spec_{pfx}_Key Features'] = df_k
    common_data[f'spec_{pfx}_Inbuilt features'] = df_i
    common_data[f'spec_{pfx}_Installation Accountability'] = df_a
    
    with st.spinner("Generating PDF..."):
        pdf_bytes = create_advanced_rfq_pdf(common_data)
        st.download_button("📥 Download Document", data=pdf_bytes, file_name="RFQ.pdf", use_container_width=True)
