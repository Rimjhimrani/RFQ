import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF
import tempfile
import os
from PIL import Image
import io

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

# Groups that use the standard items table (Sr, Item Name, Description, Qty, Unit, Remarks)
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
    "Warehouse Safety Equipment": [
        "Rack Protectors", "Column Guards", "Safety Barriers",
        "Safety Mirrors", "Fire Extinguishers", "Safety Signage",
    ],
}

# Storage Containers use the Item-style landscape 20-column table (separate group)
STORAGE_CONTAINERS_ITEMS = [
    "Plastic Bins", "Crates", "Pallets (Wood)", "Pallets (Plastic)", "Pallets (Metal)", "Storage Boxes",
]

CAROUSEL_SPEC_TEMPLATE = {
    "Model Details": [
        {"Sr": 1,  "Category": "Dimensions of VStore", "Description": "Height (mm)",                          "Unit": "mm",      "Requirement": "28000"},
        {"Sr": "", "Category": "",                      "Description": "Width (mm)",                           "Unit": "mm",      "Requirement": "3200"},
        {"Sr": "", "Category": "",                      "Description": "Depth (mm)",                           "Unit": "mm",      "Requirement": "3400"},
        {"Sr": "", "Category": "",                      "Description": "Floor area (m2)",                      "Unit": "m2",      "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "1st Access Point Height (mm)",         "Unit": "mm",      "Requirement": "836"},
        {"Sr": "", "Category": "",                      "Description": "2nd Access Point Height (mm)",         "Unit": "mm",      "Requirement": "5836"},
        {"Sr": "", "Category": "",                      "Description": "3rd Access Point Height (mm)",         "Unit": "mm",      "Requirement": "8836"},
        {"Sr": "", "Category": "",                      "Description": "4th Access Point Height (mm)",         "Unit": "mm",      "Requirement": "11836"},
        {"Sr": "", "Category": "",                      "Description": "Dead weight of Machine (Kg)",          "Unit": "Kg",      "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Total Weight of Tray (Kg)",            "Unit": "Kg",      "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Total Weight of Machine (Kg)",         "Unit": "Kg",      "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Storage capacity (Kg)",                "Unit": "Kg",      "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Total Machine carrying capacity",      "Unit": "",        "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Total full weight (Kg)",               "Unit": "Kg",      "Requirement": ""},
        {"Sr": 2,  "Category": "Floor load",            "Description": "Total (Kgs/sqm)",                      "Unit": "Kgs/sqm", "Requirement": ""},
        {"Sr": 3,  "Category": "Tray Details",          "Description": "Usable width (mm)",                    "Unit": "mm",      "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Usable depth (mm)",                    "Unit": "mm",      "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Empty Tray weight",                    "Unit": "Kg",      "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Area of each Trays (mm)",              "Unit": "mm",      "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Maximum load capacity (Kg)",           "Unit": "Kg",      "Requirement": "465"},
        {"Sr": "", "Category": "",                      "Description": "Number of Trays (Nos.)",               "Unit": "Nos",     "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Total area of all Trays (m2)",         "Unit": "m2",      "Requirement": ""},
        {"Sr": 4,  "Category": "Access time",           "Description": "Maximum (Sec.)",                       "Unit": "Sec",     "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Average (Sec.)",                       "Unit": "Sec",     "Requirement": ""},
        {"Sr": 5,  "Category": "No Trays can Fetch",    "Description": "No trays / Hour",                      "Unit": "Nos/Hr",  "Requirement": ""},
        {"Sr": 6,  "Category": "Power supply",          "Description": "",                                     "Unit": "",        "Requirement": ""},
        {"Sr": 7,  "Category": "Maximum Power rating",  "Description": "",                                     "Unit": "",        "Requirement": ""},
        {"Sr": 8,  "Category": "Control Panel",         "Description": "VStore standard control panel",        "Unit": "",        "Requirement": ""},
        {"Sr": 9,  "Category": "Height optimisation",   "Description": "Provided for storage",                 "Unit": "",        "Requirement": ""},
        {"Sr": 10, "Category": "Operator panel",        "Description": "",                                     "Unit": "",        "Requirement": ""},
        {"Sr": 11, "Category": "Accessories",           "Description": "Emergency stop",                       "Unit": "",        "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Accident protection light curtains",   "Unit": "",        "Requirement": ""},
        {"Sr": "", "Category": "",                      "Description": "Lighting in the accessing area",       "Unit": "",        "Requirement": ""},
    ],
}

# Item RFQ — landscape table column definitions (shared between Item RFQ and Storage Containers)
ITEM_TABLE_HEADERS = [
    "Sr.No", "Description", "Material", "Length", "Width", "Height",
    "Inner L", "Inner W", "Inner H", "UOM", "Base Type", "Colour",
    "Weight", "Load Cap", "Stackable", "Cover/Open", "Rate", "Qty",
    "Conceptual Image", "Remarks"
]
ITEM_TABLE_COL_WIDTHS = [
    12, 30, 22, 14, 14, 14, 14, 14, 14,
    14, 18, 18, 16, 18, 18, 18, 14, 12,
    28, 28
]

UNIT_OPTIONS = ["Nos", "Pieces", "Sets", "Meters", "Sq.Ft", "Sq.M", "Kg", "Tons", "Liters", "Boxes", "Rolls", "Pairs", "Lots"]

# Default empty row for Item / Storage Container table
def _empty_container_row(sr=1):
    return {
        "Sr.No": sr,
        "Description": "",
        "Material Type": "Plastic",
        "Length": "",
        "Width": "",
        "Height": "",
        "Inner Length": "",
        "Inner Width": "",
        "Inner Height": "",
        "Unit of Measurement": "Nos",
        "Base Type": "Flat",
        "Colour": "",
        "Weight Kg": "",
        "Load capacity": "",
        "Stackable": "Yes",
        "BIn Cover/ Open": "Open",
        "Rate": "",
        "Qty": 1,
        "Remarks": ""
    }


# ==============================================================
# Shared helper: draw the 20-column landscape item table into PDF
# ==============================================================
def _draw_item_landscape_table(pdf, df, images_dict=None):
    """
    Renders the 20-column landscape table for Item / Storage Container rows.
    df            : DataFrame with item rows (must have columns matching row_values below)
    images_dict   : dict {row_index -> bytes} for conceptual images (optional)
    """
    headers = ITEM_TABLE_HEADERS
    col_widths = ITEM_TABLE_COL_WIDTHS
    header_height = 10
    row_height = 28
    FIXED_IMG_WIDTH = 22
    FIXED_IMG_HEIGHT = 18

    def draw_header():
        pdf.set_font("Arial", "B", 7)
        sy = pdf.get_y()
        cx = pdf.l_margin
        for i, h in enumerate(headers):
            pdf.rect(cx, sy, col_widths[i], header_height)
            pdf.set_xy(cx, sy + 2)
            pdf.multi_cell(col_widths[i], 3, h, align="C")
            cx += col_widths[i]
        pdf.set_y(sy + header_height)

    draw_header()
    pdf.set_font("Arial", "", 7)

    if not df.empty:
        for idx, row in df.iterrows():
            row_y = pdf.get_y()
            if row_y + row_height > pdf.page_break_trigger:
                pdf.add_page(orientation='L')
                draw_header()
                pdf.set_font("Arial", "", 7)
                row_y = pdf.get_y()

            row_values = [
                str(row.get("Sr.No", idx + 1)),
                str(row.get("Description", "")),
                str(row.get("Material Type", "")),
                str(row.get("Length", "")),
                str(row.get("Width", "")),
                str(row.get("Height", "")),
                str(row.get("Inner Length", "")),
                str(row.get("Inner Width", "")),
                str(row.get("Inner Height", "")),
                str(row.get("Unit of Measurement", "")),
                str(row.get("Base Type", "")),
                str(row.get("Colour", "")),
                str(row.get("Weight Kg", "")),
                str(row.get("Load capacity", "")),
                str(row.get("Stackable", "")),
                str(row.get("BIn Cover/ Open", "")),
                str(row.get("Rate", "")),
                str(row.get("Qty", "")),
                "",   # Image — handled separately
                str(row.get("Remarks", ""))
            ]

            current_x = pdf.l_margin
            for i, value in enumerate(row_values):
                w = col_widths[i]
                pdf.rect(current_x, row_y, w, row_height)
                if headers[i] == "Conceptual Image":
                    # Prefer image_data_bytes column; fallback to images_dict
                    image_data = row.get("image_data_bytes")
                    if not isinstance(image_data, bytes) and images_dict is not None:
                        image_data = images_dict.get(idx)
                    if isinstance(image_data, bytes):
                        try:
                            img = Image.open(io.BytesIO(image_data))
                            img_x = current_x + (w - FIXED_IMG_WIDTH) / 2
                            img_y = row_y + (row_height - FIXED_IMG_HEIGHT) / 2
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                                img.save(tmp.name, format="PNG")
                                pdf.image(tmp.name, x=img_x, y=img_y, w=FIXED_IMG_WIDTH, h=FIXED_IMG_HEIGHT)
                            os.remove(tmp.name)
                        except Exception:
                            pass
                else:
                    pdf.set_xy(current_x, row_y + 6)
                    pdf.multi_cell(w, 4, value, align="C")
                current_x += w
            pdf.set_y(row_y + row_height)
    else:
        # Three empty placeholder rows
        for _ in range(3):
            ry = pdf.get_y()
            cx = pdf.l_margin
            for w in col_widths:
                pdf.rect(cx, ry, w, row_height)
                cx += w
            pdf.set_y(ry + row_height)

    pdf.ln(6)


# ==============================================================
# PDF Generation
# ==============================================================
def create_advanced_rfq_pdf(data):
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
            self.set_font('Arial', 'I', 10)
            self.cell(0, 6, f"For: {data['Type_of_items']} | Category: {data.get('rfq_category', '')}", 0, 1, 'C')
            self.ln(15)

        def footer(self):
            self.set_y(-25)
            footer_name, footer_addr = data.get('footer_company_name'), data.get('footer_company_address')
            if footer_name or footer_addr:
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y()); self.ln(3); self.set_text_color(128)
                if footer_name: self.set_font('Arial', 'B', 14); self.cell(0, 5, footer_name, 0, 1, 'C')
                if footer_addr: self.set_font('Arial', '', 8); self.cell(0, 5, footer_addr, 0, 1, 'C')
                self.set_text_color(0)
            self.set_y(-15); self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

        def section_title(self, title):
            self.set_font('Arial', 'B', 12); self.set_fill_color(230, 230, 230)
            self.cell(0, 8, title, 0, 1, 'L', fill=True); self.ln(4)

    pdf = PDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.create_cover_page(data)
    pdf.add_page()

    # REQUIREMENT BACKGROUND
    pdf.section_title('REQUIREMENT BACKGROUND')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, data['purpose'], border=0, align='L')
    pdf.ln(5)

    # TECHNICAL SPECIFICATION
    pdf.section_title('TECHNICAL SPECIFICATION')

    rfq_type = data.get('rfq_type', 'Dynamic')

    # ================================================================
    # ITEM RFQ — Landscape page with 20-column table
    # ================================================================
    if rfq_type == 'Item':
        pdf.add_page(orientation='L')
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, 'ITEM DETAILS', 0, 1, 'L')
        _draw_item_landscape_table(pdf, data.get('bin_details_df', pd.DataFrame()))

        # Return to portrait for the rest of the document
        pdf.add_page(orientation='P')

    # ================================================================
    # STORAGE INFRASTRUCTURE RFQ
    # ================================================================
    elif rfq_type == 'Storage Infrastructure':
        pdf.set_font('Arial', 'B', 11); pdf.cell(0, 8, 'RACK DETAILS', 0, 1, 'L')
        rack_headers = ["Types of \nRack", "Rack \nDimension(MM)", "Level/Rack", "Type of \nBin", "Bin \nDimension(MM)", "Level/Bin"]
        rack_col_widths = [34, 34.5, 29.5, 30, 34.5, 27.5]; header_height = 16; line_height_header = 6
        pdf.set_font('Arial', 'B', 10); y_start_header = pdf.get_y(); current_x_header = pdf.l_margin
        for i, header in enumerate(rack_headers):
            pdf.rect(current_x_header, y_start_header, rack_col_widths[i], header_height)
            num_lines = header.count('\n') + 1
            y_text_header = y_start_header + (header_height - num_lines * line_height_header) / 2
            pdf.set_xy(current_x_header, y_text_header)
            pdf.multi_cell(rack_col_widths[i], line_height_header, header, align='C', border=0)
            current_x_header += rack_col_widths[i]
        pdf.set_y(y_start_header + header_height); pdf.set_font('Arial', '', 10)
        rack_df = data['rack_details_df']
        if not rack_df.empty:
            for _, row_data in rack_df.iterrows():
                if pdf.get_y() + 10 > pdf.page_break_trigger: pdf.add_page()
                pdf.cell(rack_col_widths[0], 10, str(row_data.get('Types of Rack', '')), border=1, align='C')
                pdf.cell(rack_col_widths[1], 10, str(row_data.get('Rack Dimension (MM)', '')), border=1, align='C')
                pdf.cell(rack_col_widths[2], 10, str(row_data.get('Level/Rack', '')), border=1, align='C')
                pdf.cell(rack_col_widths[3], 10, str(row_data.get('Type of Bin', '')), border=1, align='C')
                pdf.cell(rack_col_widths[4], 10, str(row_data.get('Bin Dimension (MM)', '')), border=1, align='C')
                pdf.cell(rack_col_widths[5], 10, str(row_data.get('Level/Bin', '')), border=1, align='C', ln=1)
        else:
            pdf.cell(sum(rack_col_widths), 10, "No rack details provided.", border=1, align='C', ln=1)
        pdf.ln(8)

        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 8, 'Key Inputs:', 0, 1, 'L'); pdf.ln(2)
        key_inputs_df = data['key_inputs_df']
        if not key_inputs_df.empty:
            for index, row in key_inputs_df.iterrows():
                if not row['Input Text']: continue
                if pdf.get_y() + 20 > pdf.page_break_trigger: pdf.add_page()
                pdf.set_font('Arial', 'B', 11)
                pdf.multi_cell(0, 6, f"{index + 1}. {row['Input Text']}", 0, 'L'); pdf.ln(3)
                image_data = row.get('image_data_bytes')
                if isinstance(image_data, bytes):
                    try:
                        img = Image.open(io.BytesIO(image_data)); img_w, img_h = img.size
                        aspect_ratio = img_h / img_w; available_width = pdf.w - pdf.l_margin - pdf.r_margin
                        img_display_w = available_width; img_display_h = img_display_w * aspect_ratio
                        max_img_height = (pdf.h - pdf.t_margin - pdf.b_margin) * 0.45
                        if img_display_h > max_img_height:
                            img_display_h = max_img_height; img_display_w = img_display_h / aspect_ratio
                        if pdf.get_y() + img_display_h + 5 > pdf.page_break_trigger: pdf.add_page()
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                            img.save(tmp.name, format='PNG')
                            pdf.image(tmp.name, x=pdf.l_margin, y=pdf.get_y(), w=img_display_w, h=img_display_h)
                            os.remove(tmp.name)
                        pdf.set_y(pdf.get_y() + img_display_h + 8)
                    except Exception: pdf.ln(5)
                else: pdf.ln(5)

    # ================================================================
    # DYNAMIC / WAREHOUSE RFQ
    # ================================================================
    elif rfq_type == 'Dynamic':
        rfq_category = data.get('rfq_category', 'General')
        items_df = data.get('items_df', pd.DataFrame())
        is_warehouse = (rfq_category == 'Warehouse Equipment')

        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, f'CATEGORY: {rfq_category.upper()}', 0, 1, 'L'); pdf.ln(2)

        def draw_items_table(items_df, global_sr_start=1):
            col_widths = [8, 50, 72, 20, 20, 20]
            headers = ["Sr.", "Item Name", "Description / Specification", "Qty", "Unit", "Remarks"]
            header_height = 10
            pdf.set_font('Arial', 'B', 9)
            for i, h in enumerate(headers):
                pdf.cell(col_widths[i], header_height, h, border=1, align='C')
            pdf.ln()
            pdf.set_font('Arial', '', 9)
            sr = global_sr_start
            if not items_df.empty:
                for _, row in items_df.iterrows():
                    item_name = str(row.get('Item Name', ''))
                    if not item_name.strip(): continue
                    description = str(row.get('Description / Specification', ''))
                    qty = str(row.get('Quantity', ''))
                    unit = str(row.get('Unit', ''))
                    remarks = str(row.get('Remarks', ''))
                    # Use Sr.no from data if available
                    row_sr = str(row.get('Sr.no', sr))
                    desc_lines = max(1, len(description) // 40 + 1)
                    row_h = max(8, desc_lines * 6)
                    if pdf.get_y() + row_h > pdf.page_break_trigger:
                        pdf.add_page()
                        pdf.set_font('Arial', 'B', 9)
                        for i, h in enumerate(headers):
                            pdf.cell(col_widths[i], header_height, h, border=1, align='C')
                        pdf.ln(); pdf.set_font('Arial', '', 9)
                    row_y = pdf.get_y()
                    pdf.rect(pdf.l_margin, row_y, col_widths[0], row_h)
                    pdf.set_xy(pdf.l_margin, row_y + (row_h - 6) / 2)
                    pdf.cell(col_widths[0], 6, row_sr, align='C')
                    x = pdf.l_margin + col_widths[0]
                    pdf.rect(x, row_y, col_widths[1], row_h)
                    pdf.set_xy(x + 1, row_y + 2)
                    pdf.multi_cell(col_widths[1] - 2, 6, item_name, align='L')
                    x += col_widths[1]
                    pdf.rect(x, row_y, col_widths[2], row_h)
                    pdf.set_xy(x + 1, row_y + 2)
                    pdf.multi_cell(col_widths[2] - 2, 6, description, align='L')
                    x += col_widths[2]
                    pdf.rect(x, row_y, col_widths[3], row_h)
                    pdf.set_xy(x, row_y + (row_h - 6) / 2)
                    pdf.cell(col_widths[3], 6, qty, align='C')
                    x += col_widths[3]
                    pdf.rect(x, row_y, col_widths[4], row_h)
                    pdf.set_xy(x, row_y + (row_h - 6) / 2)
                    pdf.cell(col_widths[4], 6, unit, align='C')
                    x += col_widths[4]
                    pdf.rect(x, row_y, col_widths[5], row_h)
                    pdf.set_xy(x + 1, row_y + 2)
                    pdf.multi_cell(col_widths[5] - 2, 6, remarks, align='L')
                    pdf.set_y(row_y + row_h)
                    sr += 1
            else:
                pdf.cell(sum(col_widths), 10, "No items added.", border=1, align='C', ln=1)

        if is_warehouse:
            # ---- Groups that use the standard table (Storage Systems, MHE, Automated, Loading Dock, Safety) ----
            groups_data = data.get('warehouse_groups_df', {})
            for group_name in list(WAREHOUSE_GROUPS.keys()):
                group_df = groups_data.get(group_name, pd.DataFrame())
                if group_df is None or group_df.empty: continue
                valid = group_df[group_df["Item Name"].astype(str).str.strip() != ""]
                if valid.empty: continue
                if pdf.get_y() + 20 > pdf.page_break_trigger: pdf.add_page()
                pdf.set_font('Arial', 'B', 10)
                pdf.set_fill_color(210, 230, 255)
                pdf.cell(0, 8, f'  {group_name}', border=1, ln=1, fill=True)
                draw_items_table(valid)
                pdf.ln(4)

            # ---- Storage Containers — uses 20-column landscape table (same as Item RFQ) ----
            container_df = data.get('storage_containers_df', pd.DataFrame())
            container_images = data.get('storage_containers_images', {})
            if container_df is not None and not container_df.empty:
                valid_containers = container_df[
                    container_df["Description"].astype(str).str.strip() != ""
                ].reset_index(drop=True)
                if not valid_containers.empty:
                    # Switch to landscape for this section
                    pdf.add_page(orientation='L')
                    pdf.set_font('Arial', 'B', 10)
                    pdf.set_fill_color(210, 230, 255)
                    pdf.cell(0, 8, '  Storage Containers', border=1, ln=1, fill=True)
                    pdf.ln(2)
                    _draw_item_landscape_table(pdf, valid_containers, images_dict=container_images)
                    # Back to portrait for remaining sections
                    pdf.add_page(orientation='P')

            # ---- Model Details, Key Features, Inbuilt Features, Installation Accountability ----
            # Only render these sections if the user has items in Automated Storage Systems
            automated_df = groups_data.get('Automated Storage Systems', pd.DataFrame())
            has_automated = (
                automated_df is not None
                and not automated_df.empty
                and not automated_df[automated_df["Item Name"].astype(str).str.strip() != ""].empty
            )

            model_detail_str = data.get('model_detail_header', '').strip()
            model_df = data.get('carousel_model_df', pd.DataFrame())
            if has_automated and model_df is not None and not model_df.empty:
                if pdf.get_y() + 20 > pdf.page_break_trigger: pdf.add_page()
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 8, 'MODEL DETAILS', 0, 1, 'L')
                if model_detail_str:
                    pdf.set_font('Arial', 'I', 9)
                    pdf.cell(0, 6, model_detail_str, 0, 1, 'C')
                pdf.ln(2)
                md_widths = [10, 45, 60, 25, 50]
                md_headers = ["Sr.", "Category", "Description", "Unit", "Requirement"]
                md_hh = 10; pdf.set_font('Arial', 'B', 9)
                for i, h in enumerate(md_headers):
                    pdf.cell(md_widths[i], md_hh, h, border=1, align='C')
                pdf.ln(); pdf.set_font('Arial', '', 8)
                for _, mrow in model_df.iterrows():
                    if pdf.get_y() + 8 > pdf.page_break_trigger:
                        pdf.add_page()
                        pdf.set_font('Arial', 'B', 9)
                        for i, h in enumerate(md_headers):
                            pdf.cell(md_widths[i], md_hh, h, border=1, align='C')
                        pdf.ln(); pdf.set_font('Arial', '', 8)
                    pdf.cell(md_widths[0], 8, str(mrow.get("Sr", "")), border=1, align='C')
                    pdf.cell(md_widths[1], 8, str(mrow.get("Category", "")), border=1, align='L')
                    pdf.cell(md_widths[2], 8, str(mrow.get("Description", "")), border=1, align='L')
                    pdf.cell(md_widths[3], 8, str(mrow.get("Unit", "")), border=1, align='C')
                    pdf.cell(md_widths[4], 8, str(mrow.get("Requirement", "")), border=1, align='C', ln=1)
                pdf.ln(6)

            kf_df = data.get('key_features_df', pd.DataFrame()) if has_automated else pd.DataFrame()
            if has_automated and (kf_df is None or (isinstance(kf_df, pd.DataFrame) and kf_df.empty)):
                kf_df = pd.DataFrame([
                    {"Description": "Material Tracking", "Status": "", "Remarks": "All these key features including in Vendor Dashboard."},
                    {"Description": "Tray Details", "Status": "", "Remarks": ""},
                    {"Description": "Inventory List", "Status": "", "Remarks": ""},
                    {"Description": "Tray Call History", "Status": "", "Remarks": ""},
                    {"Description": "Alarm History", "Status": "", "Remarks": ""},
                    {"Description": "Item Code Search", "Status": "", "Remarks": ""},
                    {"Description": "Bar Code Search", "Status": "", "Remarks": ""},
                    {"Description": "Pick from BOM", "Status": "", "Remarks": ""},
                    {"Description": "BOM Items List", "Status": "", "Remarks": ""},
                    {"Description": "User Management, with backup and restore options", "Status": "", "Remarks": ""},
                ])
            if has_automated and kf_df is not None and not kf_df.empty:
                if pdf.get_y() + 20 > pdf.page_break_trigger: pdf.add_page()
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 8, 'KEY FEATURES', 0, 1, 'L'); pdf.ln(2)
                kf_widths = [10, 100, 50, 30]
                kf_headers = ["Sr.", "Description", "Status", "Remarks"]
                kf_hh = 10; pdf.set_font('Arial', 'B', 9)
                for i, h in enumerate(kf_headers):
                    pdf.cell(kf_widths[i], kf_hh, h, border=1, align='C')
                pdf.ln(); pdf.set_font('Arial', '', 8)
                for ki, krow in kf_df.iterrows():
                    if pdf.get_y() + 8 > pdf.page_break_trigger: pdf.add_page()
                    pdf.cell(kf_widths[0], 8, str(ki + 1), border=1, align='C')
                    pdf.cell(kf_widths[1], 8, str(krow.get("Description", "")), border=1, align='L')
                    pdf.cell(kf_widths[2], 8, str(krow.get("Status", "")), border=1, align='C')
                    pdf.cell(kf_widths[3], 8, str(krow.get("Remarks", "")), border=1, align='L', ln=1)
                pdf.ln(6)

            ib_df = data.get('inbuilt_features_df', pd.DataFrame()) if has_automated else pd.DataFrame()
            if has_automated and (ib_df is None or (isinstance(ib_df, pd.DataFrame) and ib_df.empty)):
                ib_df = pd.DataFrame([
                    {"Description": "Ergonomic tray positioning", "Vendor Scope (Yes/No)": "", "Remarks": "All these key features including at Vendor Side."},
                    {"Description": "Variable frequency drives", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Tray uneven positioning sensor", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Light barrier for sensing material and operator intervention", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Operator panel with IPC", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Weight management system for sensing tray overload", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Tray Block option for Multiple users", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Password authentication", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Tray guide rail @ 50 pitch", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Total machine capacity 60 tone", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Expansion at later stage is possible", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Inventory management software", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                ])
            if has_automated and ib_df is not None and not ib_df.empty:
                if pdf.get_y() + 20 > pdf.page_break_trigger: pdf.add_page()
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 8, 'INBUILT FEATURES', 0, 1, 'L'); pdf.ln(2)
                ib_widths = [10, 100, 45, 35]
                ib_headers = ["Sr.", "Description", "Vendor Scope\n(Yes/No)", "Remarks"]
                ib_hh = 14; pdf.set_font('Arial', 'B', 9)
                y_hdr = pdf.get_y(); cx = pdf.l_margin
                for i, h in enumerate(ib_headers):
                    pdf.rect(cx, y_hdr, ib_widths[i], ib_hh)
                    nl = h.count('\n') + 1
                    pdf.set_xy(cx, y_hdr + (ib_hh - nl * 5) / 2)
                    pdf.multi_cell(ib_widths[i], 5, h, align='C', border=0)
                    cx += ib_widths[i]
                pdf.set_y(y_hdr + ib_hh); pdf.set_font('Arial', '', 8)
                for ii, irow in ib_df.iterrows():
                    if pdf.get_y() + 8 > pdf.page_break_trigger: pdf.add_page()
                    pdf.cell(ib_widths[0], 8, str(ii + 1), border=1, align='C')
                    pdf.cell(ib_widths[1], 8, str(irow.get("Description", "")), border=1, align='L')
                    pdf.cell(ib_widths[2], 8, str(irow.get("Vendor Scope (Yes/No)", "")), border=1, align='C')
                    pdf.cell(ib_widths[3], 8, str(irow.get("Remarks", "")), border=1, align='L', ln=1)
                pdf.ln(6)

            ia_df = data.get('installation_df', pd.DataFrame()) if has_automated else pd.DataFrame()
            if has_automated and (ia_df is None or (isinstance(ia_df, pd.DataFrame) and ia_df.empty)):
                ia_df = pd.DataFrame([
                    {"Category": "Inventory Management Suite (IPC).", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Packing, Freight & Transit Insurance.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Installation & Commissioning.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Training.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Warranty Period", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Unloading of material", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Material handling during the installation", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Power cable cost main junction Box to Vstore", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Biometric Access, Barcode Scanner", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "MS office.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Software Customization", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Machine Integration with ERP system will extra at Actual.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "UPS and Stabilizer with accessories Installation", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Equipment Movement & Installation location", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "PEB Cladding and Civil Floor for outside installation", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                ])
            if has_automated and ia_df is not None and not ia_df.empty:
                if pdf.get_y() + 20 > pdf.page_break_trigger: pdf.add_page()
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 8, 'INSTALLATION ACCOUNTABILITY', 0, 1, 'L'); pdf.ln(2)
                ia_widths = [10, 75, 30, 30, 45]
                ia_headers = ["Sr.", "Category", "Vendor Scope\n(Yes/No)", "Customer Scope\n(Yes/No)", "Remarks"]
                ia_hh = 14; pdf.set_font('Arial', 'B', 9)
                y_hdr = pdf.get_y(); cx = pdf.l_margin
                for i, h in enumerate(ia_headers):
                    pdf.rect(cx, y_hdr, ia_widths[i], ia_hh)
                    nl = h.count('\n') + 1
                    pdf.set_xy(cx, y_hdr + (ia_hh - nl * 5) / 2)
                    pdf.multi_cell(ia_widths[i], 5, h, align='C', border=0)
                    cx += ia_widths[i]
                pdf.set_y(y_hdr + ia_hh); pdf.set_font('Arial', '', 8)
                for iai, iarow in ia_df.iterrows():
                    if pdf.get_y() + 8 > pdf.page_break_trigger: pdf.add_page()
                    pdf.cell(ia_widths[0], 8, str(iai + 1), border=1, align='C')
                    pdf.cell(ia_widths[1], 8, str(iarow.get("Category", "")), border=1, align='L')
                    pdf.cell(ia_widths[2], 8, str(iarow.get("Vendor Scope (Yes/No)", "")), border=1, align='C')
                    pdf.cell(ia_widths[3], 8, str(iarow.get("Customer Scope (Yes/No)", "")), border=1, align='C')
                    pdf.cell(ia_widths[4], 8, str(iarow.get("Remarks", "")), border=1, align='L', ln=1)
                pdf.ln(6)
        else:
            draw_items_table(items_df)
            pdf.ln(8)

    # TIMELINES
    timeline_data = [
        ("Date of RFQ Release", data['date_release']),
        ("Query Resolution Deadline", data['date_query']),
        ("Negotiation & Vendor Selection", data['date_selection']),
        ("Delivery Deadline", data['date_delivery']),
        ("Installation Deadline", data['date_install'])
    ]
    if data.get('date_meet') and pd.notna(data['date_meet']): timeline_data.append(("Face to Face Meet", data['date_meet']))
    if data.get('date_quote') and pd.notna(data['date_quote']): timeline_data.append(("First Level Quotation", data['date_quote']))
    if data.get('date_review') and pd.notna(data['date_review']): timeline_data.append(("Joint Review of Quotation", data['date_review']))

    if pdf.get_y() + 40 > pdf.page_break_trigger: pdf.add_page()
    pdf.section_title('TIMELINES')
    pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Milestone', 1, 0, 'C'); pdf.cell(110, 8, 'Date', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for item, date_val in timeline_data:
        if date_val and pd.notna(date_val):
            if pdf.get_y() + 8 > pdf.page_break_trigger:
                pdf.add_page(); pdf.set_font('Arial', 'B', 10)
                pdf.cell(80, 8, 'Milestone', 1, 0, 'C'); pdf.cell(110, 8, 'Date', 1, 1, 'C')
                pdf.set_font('Arial', '', 10)
            pdf.cell(80, 8, item, 1, 0, 'L'); pdf.cell(110, 8, date_val.strftime('%B %d, %Y'), 1, 1, 'L')
    pdf.ln(5)

    # SPOC
    if pdf.get_y() + 40 > pdf.page_break_trigger: pdf.add_page()
    pdf.section_title('SINGLE POINT OF CONTACT')
    def draw_contact_column(title, name, designation, phone, email):
        col_start_x = pdf.get_x(); pdf.set_font('Arial', 'BU', 10); pdf.multi_cell(90, 6, title, 0, 'L'); pdf.ln(1)
        def draw_kv_row(key, value):
            key_str = str(key).encode('latin-1', 'replace').decode('latin-1')
            value_str = str(value).encode('latin-1', 'replace').decode('latin-1')
            row_start_y = pdf.get_y(); pdf.set_x(col_start_x)
            pdf.set_font('Arial', 'B', 10); pdf.cell(25, 6, key_str, 0, 0, 'L')
            pdf.set_xy(col_start_x + 25, row_start_y)
            pdf.set_font('Arial', '', 10); pdf.multi_cell(65, 6, value_str, 0, 'L')
        draw_kv_row("Name:", name); draw_kv_row("Designation:", designation)
        draw_kv_row("Phone No:", phone); draw_kv_row("Email ID:", email)
    start_y = pdf.get_y(); pdf.set_xy(pdf.l_margin, start_y)
    draw_contact_column('Primary Contact', data['spoc1_name'], data['spoc1_designation'], data['spoc1_phone'], data['spoc1_email'])
    end_y1 = pdf.get_y()
    if data.get('spoc2_name'):
        pdf.set_xy(pdf.l_margin + 98, start_y)
        draw_contact_column('Secondary Contact', data['spoc2_name'], data['spoc2_designation'], data['spoc2_phone'], data['spoc2_email'])
        end_y2 = pdf.get_y(); pdf.set_y(max(end_y1, end_y2))
    else: pdf.set_y(end_y1)
    pdf.ln(5)

    # COMMERCIAL
    if pdf.get_y() + 40 > pdf.page_break_trigger: pdf.add_page()
    pdf.section_title('COMMERCIAL REQUIREMENTS')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, "Please provide a detailed cost breakup in the format below. All costs should be inclusive of taxes and duties as applicable.", 0, 'L')
    pdf.ln(4)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(80, 8, 'Cost Component', 1, 0, 'C'); pdf.cell(40, 8, 'Amount', 1, 0, 'C'); pdf.cell(70, 8, 'Remarks', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for index, row in data['commercial_df'].iterrows():
        if pdf.get_y() + 8 > pdf.page_break_trigger:
            pdf.add_page(); pdf.set_font('Arial', 'B', 10)
            pdf.cell(80, 8, 'Cost Component', 1, 0, 'C'); pdf.cell(40, 8, 'Amount', 1, 0, 'C'); pdf.cell(70, 8, 'Remarks', 1, 1, 'C')
            pdf.set_font('Arial', '', 10)
        component = str(row['Cost Component']).encode('latin-1', 'replace').decode('latin-1')
        remarks = str(row['Remarks']).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(80, 8, component, 1, 0, 'L'); pdf.cell(40, 8, '', 1, 0); pdf.cell(70, 8, remarks, 1, 1, 'L')
    pdf.ln(10)

    # SUBMISSION & DELIVERY
    if pdf.get_y() + 90 > pdf.page_break_trigger: pdf.add_page()
    if data.get('submit_to_name'):
        pdf.set_font('Arial', 'B', 12); pdf.cell(5, 8, chr(149)); pdf.cell(0, 8, 'Quotation to be Submit to:', 0, 1); pdf.ln(5)
        pdf.set_x(pdf.l_margin + 15); pdf.set_font('Arial', '', 12)
        hex_color = data.get('submit_to_color', '#DC3232').lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        pdf.set_text_color(r, g, b); pdf.multi_cell(0, 7, data.get('submit_to_name', ''))
        pdf.set_text_color(0, 0, 0); pdf.ln(1)
        if data.get('submit_to_registered_office'):
            pdf.set_x(pdf.l_margin + 15); pdf.set_font('Arial', '', 10); pdf.set_text_color(128, 128, 128)
            pdf.multi_cell(0, 6, data.get('submit_to_registered_office', ''), 0, 'L')
            pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    if data.get('delivery_location'):
        pdf.set_font('Arial', 'B', 12); pdf.cell(5, 8, chr(149)); pdf.cell(0, 8, 'Delivery Location:', 0, 1); pdf.ln(2)
        pdf.set_font('Arial', '', 11); pdf.set_x(pdf.l_margin + 5)
        pdf.multi_cell(0, 6, data.get('delivery_location'), 0, 'L')
    pdf.ln(10)
    if data.get('annexures'):
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 8, 'ANNEXURES', 0, 1); pdf.ln(2)
        pdf.set_font('Arial', '', 11); pdf.set_x(pdf.l_margin + 5)
        pdf.multi_cell(0, 6, data.get('annexures'), 0, 'L')

    return bytes(pdf.output())


# ==============================================================
# STREAMLIT APP
# ==============================================================
st.title("🏭 Request For Quotation Generator")
st.markdown("---")

# Step 1 — Logos
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

# Step 2 — Cover page
with st.expander("Step 2: Add Cover Page Details", expanded=True):
    Type_of_items = st.text_input("Type of Items*", help="e.g., Plastic Blue Bins OR Line Side Racks")
    Storage = st.text_input("Storage Type*", help="e.g., Material Storage")
    company_name = st.text_input("Requester Company Name*", help="e.g., Pinnacle Mobility Solutions Pvt. Ltd")
    company_address = st.text_input("Requester Company Address*", help="e.g., Nanekarwadi, Chakan, Pune 410501")

# Step 3 — Footer
with st.expander("Step 3: Add Footer Details (Optional)", expanded=True):
    footer_company_name = st.text_input("Footer Company Name", help="e.g., Your Company Private Ltd")
    footer_company_address = st.text_input("Footer Company Address", help="e.g., Registered Office: 123 Business Rd, Commerce City")

# Step 4 — RFQ type & technical specs
st.subheader("Step 4: Fill Core RFQ Details")
rfq_type = st.radio(
    "Select RFQ Type:",
    ('Item', 'Storage Infrastructure', 'Dynamic (Category-Based)'),
    horizontal=True,
    key='rfq_type_selector'
)
st.markdown("---")

# ================================================================
# ITEM RFQ — detailed editor
# ================================================================
if rfq_type == 'Item':
    with st.expander("Technical Specifications", expanded=True):
        st.info(
            "Define each item type in the table below. Each row = one item type. "
            "Upload a conceptual image per row using the uploaders on the right."
        )
        st.markdown("##### Item Details")

        if 'bin_df' not in st.session_state:
            st.session_state.bin_df = pd.DataFrame([_empty_container_row(1)])

        if 'bin_images' not in st.session_state:
            st.session_state.bin_images = {}

        st.info("ℹ️ Double-click a cell to edit. Use the `+` button at the bottom to add more rows.")

        editor_col, uploader_col = st.columns([3, 2])
        with editor_col:
            edited_bin_df = st.data_editor(
                st.session_state.bin_df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Sr.No":               st.column_config.NumberColumn("Sr.No", width="small"),
                    "Description":         st.column_config.TextColumn("Description", width="medium", required=True),
                    "Material Type":       st.column_config.SelectboxColumn("Material", width="small",
                                               options=["Plastic", "Metal", "Wood", "Corrugated", "Fibre", "Other"]),
                    "Length":              st.column_config.TextColumn("Length (mm)", width="small"),
                    "Width":               st.column_config.TextColumn("Width (mm)", width="small"),
                    "Height":              st.column_config.TextColumn("Height (mm)", width="small"),
                    "Inner Length":        st.column_config.TextColumn("Inner L (mm)", width="small"),
                    "Inner Width":         st.column_config.TextColumn("Inner W (mm)", width="small"),
                    "Inner Height":        st.column_config.TextColumn("Inner H (mm)", width="small"),
                    "Unit of Measurement": st.column_config.SelectboxColumn("UOM", width="small", options=UNIT_OPTIONS),
                    "Base Type":           st.column_config.SelectboxColumn("Base Type", width="small",
                                               options=["Flat", "Ribbed", "Louvred", "Grid", "Other"]),
                    "Colour":              st.column_config.TextColumn("Colour", width="small"),
                    "Weight Kg":           st.column_config.TextColumn("Weight (Kg)", width="small"),
                    "Load capacity":       st.column_config.TextColumn("Load Cap (Kg)", width="small"),
                    "Stackable":           st.column_config.SelectboxColumn("Stackable", width="small",
                                               options=["Yes", "No", "N/A"]),
                    "BIn Cover/ Open":     st.column_config.SelectboxColumn("Cover/Open", width="small",
                                               options=["Open", "Covered", "Lid", "N/A"]),
                    "Rate":                st.column_config.TextColumn("Rate", width="small"),
                    "Qty":                 st.column_config.NumberColumn("Qty", width="small", min_value=0, step=1),
                    "Remarks":             st.column_config.TextColumn("Remarks", width="medium"),
                },
                key="bin_df_editor"
            )

        with uploader_col:
            st.write("**Upload Conceptual Images**")
            for i in range(len(edited_bin_df)):
                desc = str(edited_bin_df.iloc[i].get("Description", "")).strip()
                label = f"Image for '{desc}'" if desc else f"Image for row {i+1}"
                uploaded_file = st.file_uploader(label, type=['png', 'jpg', 'jpeg'], key=f"image_uploader_{i}")
                if uploaded_file is not None:
                    st.session_state.bin_images[i] = uploaded_file.getvalue()

        st.session_state.bin_df = edited_bin_df

# ================================================================
# STORAGE INFRASTRUCTURE RFQ
# ================================================================
elif rfq_type == 'Storage Infrastructure':
    with st.expander("Technical Specifications", expanded=True):
        st.markdown("##### Rack Details")
        if 'rack_df' not in st.session_state or st.session_state.rack_df.empty:
            st.session_state.rack_df = pd.DataFrame({
                "Types of Rack": [""], "Rack Dimension (MM)": [""], "Level/Rack": [""],
                "Type of Bin": [""], "Bin Dimension (MM)": [""], "Level/Bin": [""]
            }).astype(str)
        st.info("ℹ️ Double-click any cell to edit. Use the `+` button to add more rack types.")
        edited_rack_df = st.data_editor(
            st.session_state.rack_df, num_rows="dynamic", use_container_width=True,
            column_config={
                "Types of Rack": st.column_config.TextColumn(required=True),
                "Rack Dimension (MM)": st.column_config.TextColumn(),
                "Level/Rack": st.column_config.TextColumn(),
                "Type of Bin": st.column_config.TextColumn(),
                "Bin Dimension (MM)": st.column_config.TextColumn(),
                "Level/Bin": st.column_config.TextColumn()
            }, key="rack_df_editor")
        st.session_state.rack_df = edited_rack_df

        st.markdown("---"); st.markdown("##### Key Inputs")
        if 'key_inputs_df' not in st.session_state or st.session_state.key_inputs_df.empty:
            st.session_state.key_inputs_df = pd.DataFrame([{"Input Text": "", "Upload Image?": False, "Image Data": None}])
        st.info("ℹ️ Describe each key requirement. Check the box to enable an image uploader for that row.")
        edited_key_inputs_df = st.data_editor(
            st.session_state.key_inputs_df, num_rows="dynamic", use_container_width=True,
            column_config={
                "Input Text": st.column_config.TextColumn(width="large", required=True),
                "Upload Image?": st.column_config.CheckboxColumn(default=False),
                "Image Data": None
            }, key="key_inputs_editor")
        for i, row in edited_key_inputs_df.iterrows():
            if row["Upload Image?"]:
                label = f"Upload for '{row['Input Text']}'" if row['Input Text'] else f"Upload for key input #{i+1}"
                uploaded_file = st.file_uploader(label, type=['png', 'jpg', 'jpeg'], key=f"key_input_uploader_{i}")
                if uploaded_file is not None:
                    edited_key_inputs_df.at[i, 'Image Data'] = uploaded_file.getvalue()
        st.session_state.key_inputs_df = edited_key_inputs_df

# ================================================================
# DYNAMIC / WAREHOUSE RFQ
# ================================================================
elif rfq_type == 'Dynamic (Category-Based)':
    with st.expander("📦 Technical Specifications — Dynamic Item List", expanded=True):
        category_list = list(CATEGORY_HINTS.keys())
        rfq_category = st.selectbox("Select RFQ Category*", options=category_list, index=0)
        is_warehouse = (rfq_category == "Warehouse Equipment")

        if 'last_category' not in st.session_state:
            st.session_state.last_category = rfq_category
        if st.session_state.last_category != rfq_category:
            st.session_state.dynamic_items_df = pd.DataFrame(
                columns=["Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"])
            for g in WAREHOUSE_GROUPS:
                st.session_state[f'wh_group_{g}'] = pd.DataFrame(
                    columns=["Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"])
            st.session_state.carousel_model_df = pd.DataFrame()
            # Reset storage containers too
            st.session_state.storage_containers_df = pd.DataFrame([_empty_container_row(1)])
            st.session_state.storage_containers_images = {}
            st.session_state.last_category = rfq_category

        if is_warehouse:
            st.info("**Warehouse RFQ** — Select items group-by-group below.")
            st.markdown("---")

            # ---- Standard groups (Storage Systems, MHE, Automated, Loading Dock, Safety) ----
            for group_name, group_items in WAREHOUSE_GROUPS.items():
                state_key = f'wh_group_{group_name}'
                editor_key = f'wh_editor_{group_name}'
                # Dropdown options: blank + all group items
                item_options = [""] + group_items
                if state_key not in st.session_state:
                    st.session_state[state_key] = pd.DataFrame(
                        columns=["Sr.no", "Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"]
                    )
                with st.expander(f"📁 {group_name}", expanded=False):
                    df_edit = st.session_state[state_key].copy()
                    # Ensure correct columns exist
                    for col in ["Sr.no", "Item Name", "Description / Specification", "Unit", "Remarks"]:
                        if col not in df_edit.columns: df_edit[col] = ""
                    if "Quantity" not in df_edit.columns: df_edit["Quantity"] = 1
                    if df_edit.empty:
                        df_edit = pd.DataFrame([{
                            "Sr.no": 1, "Item Name": "", "Description / Specification": "",
                            "Quantity": 1, "Unit": "Nos", "Remarks": ""
                        }])
                    # Auto-number Sr.no
                    df_edit["Sr.no"] = range(1, len(df_edit) + 1)
                    df_edit["Quantity"] = pd.to_numeric(df_edit["Quantity"], errors='coerce').fillna(1).astype(int)
                    for col in ["Item Name", "Description / Specification", "Unit", "Remarks"]:
                        df_edit[col] = df_edit[col].astype(str).replace("nan", "")
                    # Reorder columns to match Excel spec
                    df_edit = df_edit[["Sr.no", "Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"]]
                    edited_group = st.data_editor(
                        df_edit, num_rows="dynamic", use_container_width=True,
                        column_config={
                            "Sr.no":                        st.column_config.NumberColumn("Sr.no", width="small", disabled=True),
                            "Item Name":                    st.column_config.SelectboxColumn("Item Name", width="medium", options=item_options),
                            "Description / Specification":  st.column_config.TextColumn("Description / Specification", width="large"),
                            "Quantity":                     st.column_config.NumberColumn("Qty", width="small", min_value=0, step=1, format="%d"),
                            "Unit":                         st.column_config.SelectboxColumn("Unit", width="small", options=UNIT_OPTIONS),
                            "Remarks":                      st.column_config.TextColumn("Remarks", width="medium"),
                        }, key=editor_key)
                    st.session_state[state_key] = edited_group
                    valid_count = len(edited_group[edited_group["Item Name"].astype(str).str.strip() != ""])
                    if valid_count > 0:
                        st.success(f"✅ {valid_count} item(s) in this group")

            # ---- Storage Containers — uses Item-style 20-column detailed table ----
            st.markdown("---")
            st.markdown("### 📦 Storage Containers")
            st.info(
                "Select container type from the dropdown, fill dimensions and details. "
                "Upload a conceptual image per row."
            )

            if 'storage_containers_df' not in st.session_state:
                st.session_state.storage_containers_df = pd.DataFrame([_empty_container_row(1)])
            if 'storage_containers_images' not in st.session_state:
                st.session_state.storage_containers_images = {}

            # Auto-number Sr.No
            sc_df_display = st.session_state.storage_containers_df.copy()
            sc_df_display["Sr.No"] = range(1, len(sc_df_display) + 1)
            for col in ["Description", "Material Type", "Length", "Width", "Height",
                        "Inner Length", "Inner Width", "Inner Height", "Unit of Measurement",
                        "Base Type", "Colour", "Weight Kg", "Load capacity",
                        "Stackable", "BIn Cover/ Open", "Rate", "Remarks"]:
                if col not in sc_df_display.columns: sc_df_display[col] = ""
                sc_df_display[col] = sc_df_display[col].astype(str).replace("nan", "")
            if "Qty" not in sc_df_display.columns: sc_df_display["Qty"] = 1
            sc_df_display["Qty"] = pd.to_numeric(sc_df_display["Qty"], errors='coerce').fillna(1).astype(int)

            container_options = [""] + STORAGE_CONTAINERS_ITEMS

            sc_editor_col, sc_uploader_col = st.columns([3, 2])
            with sc_editor_col:
                edited_sc_df = st.data_editor(
                    sc_df_display,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "Sr.No":               st.column_config.NumberColumn("Sr.No", width="small", disabled=True),
                        "Description":         st.column_config.SelectboxColumn("Container Type", width="medium",
                                                   options=container_options),
                        "Material Type":       st.column_config.SelectboxColumn("Material", width="small",
                                                   options=["", "Plastic", "Metal", "Wood", "Corrugated", "Fibre", "Other"]),
                        "Length":              st.column_config.TextColumn("Length (mm)", width="small"),
                        "Width":               st.column_config.TextColumn("Width (mm)", width="small"),
                        "Height":              st.column_config.TextColumn("Height (mm)", width="small"),
                        "Inner Length":        st.column_config.TextColumn("Inner L (mm)", width="small"),
                        "Inner Width":         st.column_config.TextColumn("Inner W (mm)", width="small"),
                        "Inner Height":        st.column_config.TextColumn("Inner H (mm)", width="small"),
                        "Unit of Measurement": st.column_config.SelectboxColumn("UOM", width="small",
                                                   options=[""] + UNIT_OPTIONS),
                        "Base Type":           st.column_config.SelectboxColumn("Base Type", width="small",
                                                   options=["", "Flat", "Ribbed", "Louvred", "Grid", "Other"]),
                        "Colour":              st.column_config.TextColumn("Colour", width="small"),
                        "Weight Kg":           st.column_config.TextColumn("Weight (Kg)", width="small"),
                        "Load capacity":       st.column_config.TextColumn("Load Cap (Kg)", width="small"),
                        "Stackable":           st.column_config.SelectboxColumn("Stackable", width="small",
                                                   options=["", "Yes", "No", "N/A"]),
                        "BIn Cover/ Open":     st.column_config.SelectboxColumn("Cover/Open", width="small",
                                                   options=["", "Open", "Covered", "Lid", "N/A"]),
                        "Rate":                st.column_config.TextColumn("Rate", width="small"),
                        "Qty":                 st.column_config.NumberColumn("Qty", width="small", min_value=0, step=1),
                        "Remarks":             st.column_config.TextColumn("Remarks", width="medium"),
                    },
                    key="sc_df_editor"
                )
            with sc_uploader_col:
                st.write("**Upload Conceptual Images**")
                for i in range(len(edited_sc_df)):
                    desc = str(edited_sc_df.iloc[i].get("Description", "")).strip()
                    label = f"Image for '{desc}'" if desc else f"Image for container row {i+1}"
                    uploaded_file = st.file_uploader(label, type=['png', 'jpg', 'jpeg'], key=f"sc_image_uploader_{i}")
                    if uploaded_file is not None:
                        st.session_state.storage_containers_images[i] = uploaded_file.getvalue()

            st.session_state.storage_containers_df = edited_sc_df
            valid_sc_count = len(edited_sc_df[edited_sc_df["Description"].astype(str).str.strip() != ""])
            if valid_sc_count > 0:
                st.success(f"✅ {valid_sc_count} container type(s) added")

            # ---- Carousel sections: only shown if Automated Storage Systems has items ----
            automated_state_key = 'wh_group_Automated Storage Systems'
            _auto_df = st.session_state.get(automated_state_key, pd.DataFrame())
            _has_automated_ui = (
                _auto_df is not None
                and not _auto_df.empty
                and not _auto_df[_auto_df["Item Name"].astype(str).str.strip() != ""].empty
            )

            if _has_automated_ui:
                import copy
                st.markdown("---")
                st.markdown("### 🎠 Carousel / VStore — Model Details")
                st.info("Pre-filled with standard spec. Edit the **Requirement** column as needed.")
                model_detail_header = st.text_input("Model Header",
                    value="3400 (L) x 3200 (W)   -  465 kgs/tray  -  28 m Height",
                    key="model_detail_header_input")
                if 'carousel_model_df' not in st.session_state or st.session_state.get('carousel_model_df') is None or (
                    isinstance(st.session_state.get('carousel_model_df'), pd.DataFrame) and st.session_state.carousel_model_df.empty
                ):
                    st.session_state.carousel_model_df = pd.DataFrame(copy.deepcopy(CAROUSEL_SPEC_TEMPLATE["Model Details"]))
                edited_model_df = st.data_editor(
                    st.session_state.carousel_model_df, num_rows="dynamic", use_container_width=True,
                    column_config={
                        "Sr": st.column_config.TextColumn("Sr.", width="small"),
                        "Category": st.column_config.TextColumn("Category", width="medium"),
                        "Description": st.column_config.TextColumn("Description", width="large"),
                        "Unit": st.column_config.TextColumn("Unit", width="small"),
                        "Requirement": st.column_config.TextColumn("Requirement", width="medium"),
                    }, key="carousel_model_editor")
                st.session_state.carousel_model_df = edited_model_df
                st.session_state.model_detail_header = model_detail_header

                st.markdown("---")
                st.markdown("### ⭐ Key Features")
                default_kf = pd.DataFrame([
                    {"Description": "Material Tracking", "Status": "", "Remarks": "All these key features including in Vendor Dashboard."},
                    {"Description": "Tray Details", "Status": "", "Remarks": ""},
                    {"Description": "Inventory List", "Status": "", "Remarks": ""},
                    {"Description": "Tray Call History", "Status": "", "Remarks": ""},
                    {"Description": "Alarm History", "Status": "", "Remarks": ""},
                    {"Description": "Item Code Search", "Status": "", "Remarks": ""},
                    {"Description": "Bar Code Search", "Status": "", "Remarks": ""},
                    {"Description": "Pick from BOM", "Status": "", "Remarks": ""},
                    {"Description": "BOM Items List", "Status": "", "Remarks": ""},
                    {"Description": "User Management, with backup and restore options", "Status": "", "Remarks": ""},
                ])
                if 'key_features_df' not in st.session_state or st.session_state.key_features_df.empty:
                    st.session_state.key_features_df = default_kf
                edited_kf = st.data_editor(st.session_state.key_features_df, num_rows="dynamic", use_container_width=True,
                    column_config={
                        "Description": st.column_config.TextColumn("Description", width="large"),
                        "Status": st.column_config.TextColumn("Status", width="small"),
                        "Remarks": st.column_config.TextColumn("Remarks", width="large"),
                    }, key="kf_editor")
                st.session_state.key_features_df = edited_kf

                st.markdown("### 🔧 Inbuilt Features")
                default_ib = pd.DataFrame([
                    {"Description": "Ergonomic tray positioning", "Vendor Scope (Yes/No)": "", "Remarks": "All these key features including at Vendor Side."},
                    {"Description": "Variable frequency drives", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Tray uneven positioning sensor", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Light barrier for sensing material and operator intervention", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Operator panel with IPC", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Weight management system for sensing tray overload", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Tray Block option for Multiple users", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Password authentication", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Tray guide rail @ 50 pitch", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Total machine capacity 60 tone", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Expansion at later stage is possible", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                    {"Description": "Inventory management software", "Vendor Scope (Yes/No)": "", "Remarks": ""},
                ])
                if 'inbuilt_features_df' not in st.session_state or st.session_state.inbuilt_features_df.empty:
                    st.session_state.inbuilt_features_df = default_ib
                edited_ib = st.data_editor(st.session_state.inbuilt_features_df, num_rows="dynamic", use_container_width=True,
                    column_config={
                        "Description": st.column_config.TextColumn("Description", width="large"),
                        "Vendor Scope (Yes/No)": st.column_config.SelectboxColumn("Vendor Scope", width="small", options=["Yes", "No", ""]),
                        "Remarks": st.column_config.TextColumn("Remarks", width="large"),
                    }, key="ib_editor")
                st.session_state.inbuilt_features_df = edited_ib

                st.markdown("### 🏗️ Installation Accountability")
                default_ia = pd.DataFrame([
                    {"Category": "Inventory Management Suite (IPC).", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Packing, Freight & Transit Insurance.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Installation & Commissioning.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Training.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Warranty Period", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Unloading of material", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Material handling during the installation", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Power cable cost main junction Box to Vstore", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Biometric Access, Barcode Scanner", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "MS office.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Software Customization", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Machine Integration with ERP system will extra at Actual.", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "UPS and Stabilizer with accessories Installation", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "Equipment Movement & Installation location", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                    {"Category": "PEB Cladding and Civil Floor for outside installation", "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
                ])
                if 'installation_df' not in st.session_state or st.session_state.installation_df.empty:
                    st.session_state.installation_df = default_ia
                edited_ia = st.data_editor(st.session_state.installation_df, num_rows="dynamic", use_container_width=True,
                    column_config={
                        "Category": st.column_config.TextColumn("Category", width="large"),
                        "Vendor Scope (Yes/No)": st.column_config.SelectboxColumn("Vendor Scope", width="small", options=["Yes", "No", ""]),
                        "Customer Scope (Yes/No)": st.column_config.SelectboxColumn("Customer Scope", width="small", options=["Yes", "No", ""]),
                        "Remarks": st.column_config.TextColumn("Remarks", width="medium"),
                    }, key="ia_editor")
                st.session_state.installation_df = edited_ia
            else:
                st.info("💡 Add items to **Automated Storage Systems** above to unlock Carousel / VStore specification tables.")

        else:
            hints = CATEGORY_HINTS.get(rfq_category, [])
            if hints:
                st.markdown(f"**💡 Common items in *{rfq_category}***")
            if 'dynamic_items_df' not in st.session_state:
                st.session_state.dynamic_items_df = pd.DataFrame(
                    columns=["Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"])
            if hints:
                btn_cols = st.columns(min(len(hints), 4))
                for idx, hint in enumerate(hints):
                    with btn_cols[idx % 4]:
                        if st.button(f"➕ {hint}", key=f"hint_btn_{idx}_{rfq_category}"):
                            new_row = pd.DataFrame([{"Item Name": hint, "Description / Specification": "", "Quantity": 1, "Unit": "Nos", "Remarks": ""}])
                            st.session_state.dynamic_items_df = pd.concat([st.session_state.dynamic_items_df, new_row], ignore_index=True)
                            st.rerun()
            st.markdown("---")
            st.markdown("##### 📋 Item List")
            df_to_edit = st.session_state.dynamic_items_df.copy()
            if df_to_edit.empty:
                df_to_edit = pd.DataFrame([{"Item Name": "", "Description / Specification": "", "Quantity": 1, "Unit": "Nos", "Remarks": ""}])
            df_to_edit["Quantity"] = pd.to_numeric(df_to_edit.get("Quantity", 1), errors='coerce').fillna(1).astype(int)
            for col in ["Item Name", "Description / Specification", "Unit", "Remarks"]:
                if col not in df_to_edit.columns: df_to_edit[col] = ""
                df_to_edit[col] = df_to_edit[col].astype(str)
            edited_dynamic_df = st.data_editor(
                df_to_edit, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Item Name": st.column_config.TextColumn("Item Name", width="medium", required=True),
                    "Description / Specification": st.column_config.TextColumn("Description / Specification", width="large"),
                    "Quantity": st.column_config.NumberColumn("Qty", width="small", min_value=0, step=1, format="%d"),
                    "Unit": st.column_config.SelectboxColumn("Unit", width="small", options=UNIT_OPTIONS, required=True),
                    "Remarks": st.column_config.TextColumn("Remarks", width="medium"),
                }, key="dynamic_items_editor")
            st.session_state.dynamic_items_df = edited_dynamic_df
            total_items = len(edited_dynamic_df[edited_dynamic_df["Item Name"].astype(str).str.strip() != ""])
            if total_items > 0:
                st.success(f"✅ {total_items} item(s) added to this RFQ")
            else:
                st.warning("⚠️ Add at least one item to generate the RFQ.")

# ================================================================
# REST OF FORM (Steps 5+)
# ================================================================
with st.form(key="advanced_rfq_form"):
    purpose = st.text_area("Purpose of Requirement*", max_chars=500, height=100)
    with st.expander("Timelines"):
        today = date.today()
        c1, c2, c3 = st.columns(3)
        date_release = c1.date_input("Date of RFQ Release *", today)
        date_query = c1.date_input("Query Resolution Deadline *", today + timedelta(days=7))
        date_meet = c1.date_input("Face to Face Meet", None)
        date_selection = c2.date_input("Negotiation & Vendor Selection *", today + timedelta(days=30))
        date_delivery = c2.date_input("Delivery Deadline *", today + timedelta(days=60))
        date_quote = c2.date_input("First Level Quotation", None)
        date_install = c3.date_input("Installation Deadline *", today + timedelta(days=75))
        date_review = c3.date_input("Joint Review of Quotation", None)
    with st.expander("Single Point of Contact (SPOC)"):
        st.markdown("##### Primary Contact*"); c1, c2 = st.columns(2)
        spoc1_name = c1.text_input("Name*", key="s1n"); spoc1_designation = c1.text_input("Designation", key="s1d")
        spoc1_phone = c2.text_input("Phone No*", key="s1p"); spoc1_email = c2.text_input("Email ID*", key="s1e")
        st.markdown("##### Secondary Contact (Optional)"); c1, c2 = st.columns(2)
        spoc2_name = c1.text_input("Name", key="s2n"); spoc2_designation = c1.text_input("Designation", key="s2d")
        spoc2_phone = c2.text_input("Phone No", key="s2p"); spoc2_email = c2.text_input("Email ID", key="s2e")
    with st.expander("Commercial Requirements"):
        edited_commercial_df = st.data_editor(
            pd.DataFrame([
                {"Cost Component": "Unit Cost", "Remarks": "Per item/unit specified in Section 2."},
                {"Cost Component": "Freight", "Remarks": "Specify if included or extra."},
                {"Cost Component": "Any other Handling Cost", "Remarks": ""},
                {"Cost Component": "Total Basic Cost (Per Unit)", "Remarks": ""}
            ]), num_rows="dynamic", use_container_width=True)
    with st.expander("Submission, Delivery & Annexures"):
        st.markdown("##### Quotation Submission Details*")
        submit_to_name = st.text_input("Submit To (Company Name)*", "Agilomatrix Pvt. Ltd.")
        submit_to_color = st.color_picker("Company Name Color", "#DC3232")
        submit_to_registered_office = st.text_input("Submit To (Registered Office Address)",
            "Registered Office: F1403, 7 Plumeria Drive, 7PD Street, Tathawade, Pune - 411033")
        st.markdown("---"); st.markdown("##### Delivery & Annexures*")
        delivery_location = st.text_area("Delivery Location Address*", height=100)
        annexures = st.text_area("Annexures (one item per line)", height=100)

    submitted = st.form_submit_button("Generate RFQ Document", use_container_width=True, type="primary")

# ================================================================
# PDF GENERATION ON SUBMIT
# ================================================================
if submitted:
    required_fields = [purpose, spoc1_name, spoc1_phone, spoc1_email, company_name,
                       company_address, Type_of_items, Storage, submit_to_name, delivery_location]
    if not all(required_fields):
        st.error("⚠️ Please fill in all mandatory (*) fields.")
    elif rfq_type == 'Dynamic (Category-Based)':
        current_category = st.session_state.get('last_category', 'General')
        is_warehouse_submit = (current_category == "Warehouse Equipment")
        has_items = True

        if not is_warehouse_submit:
            items_check = st.session_state.get('dynamic_items_df', pd.DataFrame())
            has_items = not items_check.empty and not items_check[
                items_check["Item Name"].astype(str).str.strip() != ""
            ].empty

        if not has_items:
            st.error("⚠️ Please add at least one item to the item list in Step 4.")
        else:
            with st.spinner("Generating PDF..."):
                common_data = {
                    'rfq_type': 'Dynamic', 'rfq_category': current_category,
                    'Type_of_items': Type_of_items, 'Storage': Storage,
                    'company_name': company_name, 'company_address': company_address,
                    'footer_company_name': footer_company_name, 'footer_company_address': footer_company_address,
                    'logo1_data': logo1_file.getvalue() if logo1_file else None,
                    'logo2_data': logo2_file.getvalue() if logo2_file else None,
                    'logo1_w': logo1_w, 'logo1_h': logo1_h, 'logo2_w': logo2_w, 'logo2_h': logo2_h,
                    'purpose': purpose,
                    'date_release': date_release, 'date_query': date_query,
                    'date_selection': date_selection, 'date_delivery': date_delivery,
                    'date_install': date_install, 'date_meet': date_meet,
                    'date_quote': date_quote, 'date_review': date_review,
                    'spoc1_name': spoc1_name, 'spoc1_designation': spoc1_designation,
                    'spoc1_phone': spoc1_phone, 'spoc1_email': spoc1_email,
                    'spoc2_name': spoc2_name, 'spoc2_designation': spoc2_designation,
                    'spoc2_phone': spoc2_phone, 'spoc2_email': spoc2_email,
                    'commercial_df': edited_commercial_df,
                    'submit_to_name': submit_to_name, 'submit_to_color': submit_to_color,
                    'submit_to_registered_office': submit_to_registered_office,
                    'delivery_location': delivery_location, 'annexures': annexures,
                }
                if is_warehouse_submit:
                    groups_data = {g: st.session_state.get(f'wh_group_{g}', pd.DataFrame()) for g in WAREHOUSE_GROUPS}
                    common_data['warehouse_groups_df'] = groups_data

                    # Storage Containers — separate, uses landscape 20-col table
                    sc_df = st.session_state.get('storage_containers_df', pd.DataFrame())
                    sc_images = st.session_state.get('storage_containers_images', {})
                    if sc_df is not None and not sc_df.empty:
                        valid_sc = sc_df[sc_df["Description"].astype(str).str.strip() != ""].reset_index(drop=True)
                        # Attach images to rows
                        valid_sc = valid_sc.copy()
                        valid_sc['image_data_bytes'] = [sc_images.get(i) for i in range(len(valid_sc))]
                        common_data['storage_containers_df'] = valid_sc
                    else:
                        common_data['storage_containers_df'] = pd.DataFrame()
                    common_data['storage_containers_images'] = sc_images

                    model_df = st.session_state.get('carousel_model_df', pd.DataFrame())
                    if model_df is None or model_df.empty:
                        import copy
                        model_df = pd.DataFrame(copy.deepcopy(CAROUSEL_SPEC_TEMPLATE["Model Details"]))
                    common_data['carousel_model_df'] = model_df
                    common_data['model_detail_header'] = st.session_state.get('model_detail_header', '3400 (L) x 3200 (W)   -  465 kgs/tray  -  28 m Height')
                    common_data['key_features_df'] = st.session_state.get('key_features_df', pd.DataFrame())
                    common_data['inbuilt_features_df'] = st.session_state.get('inbuilt_features_df', pd.DataFrame())
                    common_data['installation_df'] = st.session_state.get('installation_df', pd.DataFrame())
                else:
                    items_check = st.session_state.get('dynamic_items_df', pd.DataFrame())
                    valid_items = items_check[items_check["Item Name"].astype(str).str.strip() != ""].reset_index(drop=True)
                    common_data['items_df'] = valid_items
                pdf_data = create_advanced_rfq_pdf(common_data)

            st.success("✅ RFQ PDF Generated Successfully!")
            file_name = f"RFQ_{Type_of_items.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
            st.download_button("📥 Download RFQ Document", data=pdf_data, file_name=file_name,
                               mime="application/pdf", use_container_width=True, type="primary")
    else:
        with st.spinner("Generating PDF..."):
            rfq_data = {
                'rfq_type': rfq_type,
                'Type_of_items': Type_of_items, 'Storage': Storage,
                'company_name': company_name, 'company_address': company_address,
                'footer_company_name': footer_company_name, 'footer_company_address': footer_company_address,
                'logo1_data': logo1_file.getvalue() if logo1_file else None,
                'logo2_data': logo2_file.getvalue() if logo2_file else None,
                'logo1_w': logo1_w, 'logo1_h': logo1_h, 'logo2_w': logo2_w, 'logo2_h': logo2_h,
                'purpose': purpose,
                'date_release': date_release, 'date_query': date_query,
                'date_selection': date_selection, 'date_delivery': date_delivery,
                'date_install': date_install, 'date_meet': date_meet,
                'date_quote': date_quote, 'date_review': date_review,
                'spoc1_name': spoc1_name, 'spoc1_designation': spoc1_designation,
                'spoc1_phone': spoc1_phone, 'spoc1_email': spoc1_email,
                'spoc2_name': spoc2_name, 'spoc2_designation': spoc2_designation,
                'spoc2_phone': spoc2_phone, 'spoc2_email': spoc2_email,
                'commercial_df': edited_commercial_df,
                'submit_to_name': submit_to_name, 'submit_to_color': submit_to_color,
                'submit_to_registered_office': submit_to_registered_office,
                'delivery_location': delivery_location, 'annexures': annexures,
            }
            if rfq_type == 'Item':
                df_to_process = st.session_state.bin_df.copy()
                df_to_process = df_to_process[
                    df_to_process["Description"].astype(str).str.strip() != ""
                ].reset_index(drop=True)
                bin_images = st.session_state.get('bin_images', {})
                df_to_process['image_data_bytes'] = [bin_images.get(i) for i in range(len(df_to_process))]
                rfq_data['bin_details_df'] = df_to_process

            elif rfq_type == 'Storage Infrastructure':
                df_rack = st.session_state.rack_df.dropna(subset=["Types of Rack"]).copy()
                rfq_data['rack_details_df'] = df_rack[df_rack["Types of Rack"].str.strip() != ""]
                df_key = st.session_state.key_inputs_df.dropna(subset=["Input Text"]).copy()
                rfq_data['key_inputs_df'] = df_key[df_key["Input Text"].str.strip() != ""].rename(columns={"Image Data": "image_data_bytes"})

            pdf_data = create_advanced_rfq_pdf(rfq_data)

        st.success("✅ RFQ PDF Generated Successfully!")
        file_name = f"RFQ_{Type_of_items.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        st.download_button("📥 Download RFQ Document", data=pdf_data, file_name=file_name,
                           mime="application/pdf", use_container_width=True, type="primary")
