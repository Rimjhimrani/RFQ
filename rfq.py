import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF
import tempfile
import os
from PIL import Image
import io
import copy as _copy
import base64

# ── Hardcoded Agilomatrix logo (Logo 2 — always appears top-right) ────────────
_LOGO2_B64 = "Image.png"
LOGO2_BYTES = base64.b64decode(_LOGO2_B64)
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

STORAGE_CONTAINERS_ITEMS = [
    "Plastic Bins", "Crates", "Pallets (Wood)", "Pallets (Plastic)", "Pallets (Metal)", "Storage Boxes",
]

UNIT_OPTIONS = ["Nos", "Pieces", "Sets", "Meters", "Sq.Ft", "Sq.M", "Kg", "Tons", "Liters", "Boxes", "Rolls", "Pairs", "Lots"]

# ─── SPEC TABLE DATA ──────────────────────────────────────────────────────────
MODEL_DETAILS_ROWS = [
    {"Sr.no": 1,  "Category": "Dimensions",        "Description": "Height (mm)",                       "UNIT": "mm",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Width (mm)",                        "UNIT": "mm",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Depth (mm)",                        "UNIT": "mm",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Floor area (m2)",                   "UNIT": "m2",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "1st Access Point Height (mm)",      "UNIT": "mm",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "2nd Access Point Height (mm)",      "UNIT": "mm",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "3rd Access Point Height (mm)",      "UNIT": "mm",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "4th Access Point Height (mm)",      "UNIT": "mm",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Dead weight of Machine (Kg)",       "UNIT": "Kg",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Total Weight of Tray (Kg)",         "UNIT": "Kg",     "Requirement": "MS Steel"},
    {"Sr.no": "",  "Category": "",                  "Description": "Total Weight of Machine (Kg)",      "UNIT": "Kg",     "Requirement": "Powder Coated"},
    {"Sr.no": "",  "Category": "",                  "Description": "Storage capacity (Kg)",             "UNIT": "Kg",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Total Machine carrying capacity",   "UNIT": "Kg",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Total full weight (Kg)",            "UNIT": "Kg",     "Requirement": ""},
    {"Sr.no": 2,  "Category": "Floor Load",         "Description": "Total (Kgs/sqm)",                  "UNIT": "Kg/m2",  "Requirement": ""},
    {"Sr.no": 3,  "Category": "Tray Details",       "Description": "Usable width (mm)",                "UNIT": "mm",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Usable depth (mm)",                "UNIT": "mm",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Empty Tray weight",                "UNIT": "Kg",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Area of each Trays (mm)",          "UNIT": "mm2",    "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Maximum Load capacity (Kg)",       "UNIT": "Kg",     "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Number of Trays (Nos.)",           "UNIT": "Nos",    "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Total area of all Trays (m2)",     "UNIT": "m2",     "Requirement": ""},
    {"Sr.no": 4,  "Category": "Access time",        "Description": "Maximum (Sec.)",                   "UNIT": "Sec",    "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Average (Sec.)",                   "UNIT": "Sec",    "Requirement": ""},
    {"Sr.no": 5,  "Category": "No Trays can Fetch", "Description": "No trays / Hour",                  "UNIT": "Nos/hr", "Requirement": ""},
    {"Sr.no": 6,  "Category": "Power Supply",       "Description": "",                                 "UNIT": "",       "Requirement": ""},
    {"Sr.no": 7,  "Category": "Maximum Power rating","Description": "",                                "UNIT": "kW",     "Requirement": ""},
    {"Sr.no": 8,  "Category": "Control Panel",      "Description": "Standard control panel",          "UNIT": "",       "Requirement": ""},
    {"Sr.no": 9,  "Category": "Height Optimisation","Description": "Provided for storage",             "UNIT": "",       "Requirement": ""},
    {"Sr.no": 10, "Category": "Operator Panel",     "Description": "",                                 "UNIT": "",       "Requirement": ""},
    {"Sr.no": 11, "Category": "Accessories",        "Description": "Emergency stop",                  "UNIT": "",       "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Accident protection light curtains","UNIT": "",      "Requirement": ""},
    {"Sr.no": "",  "Category": "",                  "Description": "Lighting in the accessing area",   "UNIT": "",       "Requirement": ""},
]

KEY_FEATURES_ROWS = [
    {"Sr.no": 1,  "Description": "Material Tracking",                               "Status": "", "Remarks": "All key features to be confirmed by vendor."},
    {"Sr.no": 2,  "Description": "Tray Details",                                    "Status": "", "Remarks": ""},
    {"Sr.no": 3,  "Description": "Inventory List",                                  "Status": "", "Remarks": ""},
    {"Sr.no": 4,  "Description": "Tray Call History",                               "Status": "", "Remarks": ""},
    {"Sr.no": 5,  "Description": "Alarm History",                                   "Status": "", "Remarks": ""},
    {"Sr.no": 6,  "Description": "Item Code Search",                                "Status": "", "Remarks": ""},
    {"Sr.no": 7,  "Description": "Bar Code Search",                                 "Status": "", "Remarks": ""},
    {"Sr.no": 8,  "Description": "Pick from BOM",                                   "Status": "", "Remarks": ""},
    {"Sr.no": 9,  "Description": "BOM Items List",                                  "Status": "", "Remarks": ""},
    {"Sr.no": 10, "Description": "User Management, with backup and restore options","Status": "", "Remarks": ""},
]

INBUILT_FEATURES_ROWS = [
    {"Sr.no": 1,  "Description": "Ergonomic tray positioning",                                     "Vendor Scope (Yes/No)": "", "Remarks": "All features to be included at vendor side."},
    {"Sr.no": 2,  "Description": "Variable frequency drives",                                      "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 3,  "Description": "Tray uneven positioning sensor",                                 "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 4,  "Description": "Light barrier for sensing material and operator intervention",   "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 5,  "Description": "Operator Panel with IPC",                                        "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 6,  "Description": "Weight management system for sensing tray overload",             "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 7,  "Description": "Tray Block option for Multiple users",                           "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 8,  "Description": "Password authentication",                                        "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 9,  "Description": "Tray guide rail @ 50 pitch",                                    "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 10, "Description": "Total machine capacity 60 tone",                                 "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 11, "Description": "Expansion at later stage is possible",                           "Vendor Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 12, "Description": "Inventory management software",                                  "Vendor Scope (Yes/No)": "", "Remarks": ""},
]

INSTALLATION_ROWS = [
    {"Sr.no": 1,  "Category": "Inventory Management Suite (IPC)",                        "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 2,  "Category": "Packing, Freight & Transit Insurance",                    "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 3,  "Category": "Installation & Commissioning",                            "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 4,  "Category": "Training",                                                "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 5,  "Category": "Warranty Period",                                         "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 6,  "Category": "Unloading of material",                                  "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 7,  "Category": "Material handling during the installation",               "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 8,  "Category": "Power cable cost main junction Box to Machine",           "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 9,  "Category": "Biometric Access, Barcode Scanner",                      "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 10, "Category": "MS Office",                                               "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 11, "Category": "Software Customization",                                  "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 12, "Category": "Machine Integration with ERP system (extra at Actual)",   "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 13, "Category": "UPS and Stabilizer with accessories Installation",        "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 14, "Category": "Equipment Movement & Installation location",              "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
    {"Sr.no": 15, "Category": "PEB Cladding and Civil Floor for outside installation",   "Vendor Scope (Yes/No)": "", "Customer Scope (Yes/No)": "", "Remarks": ""},
]

# One shared template used for ALL warehouse spec subtypes
SPEC_TEMPLATE = {
    "Model Details": MODEL_DETAILS_ROWS,
    "Key Features": KEY_FEATURES_ROWS,
    "Inbuilt features": INBUILT_FEATURES_ROWS,
    "Installation Accountability": INSTALLATION_ROWS,
}

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

def _empty_container_row(sr=1):
    return {
        "Sr.No": sr, "Description": "", "Material Type": "Plastic",
        "Length": "", "Width": "", "Height": "",
        "Inner Length": "", "Inner Width": "", "Inner Height": "",
        "Unit of Measurement": "Nos", "Base Type": "Flat", "Colour": "",
        "Weight Kg": "", "Load capacity": "", "Stackable": "Yes",
        "BIn Cover/ Open": "Open", "Rate": "", "Qty": 1, "Remarks": ""
    }


# ==============================================================
# PDF GENERATION
# ==============================================================
def create_advanced_rfq_pdf(data):

    class PDF(FPDF):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._data = data  # store reference for header/footer

        def header(self):
            if self.page_no() == 1:
                return
            logo1_data = self._data.get('logo1_data')
            logo2_data = self._data.get('logo2_data') or LOGO2_BYTES
            logo2_w    = self._data.get('logo2_w', 45)
            logo2_h    = self._data.get('logo2_h', 20)

            # Logo 1 — left
            if logo1_data:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        tmp.write(logo1_data)
                        tmp.flush()
                        self.image(tmp.name, x=self.l_margin, y=6,
                                   w=self._data.get('logo1_w', 35),
                                   h=self._data.get('logo1_h', 18))
                    os.remove(tmp.name)
                except Exception:
                    pass

            # Logo 2 — right, user-uploaded PNG or hardcoded fallback
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo2_data)
                    tmp.flush()
                    self.image(tmp.name,
                               x=self.w - self.r_margin - logo2_w,
                               y=6, w=logo2_w, h=logo2_h)
                os.remove(tmp.name)
            except Exception:
                pass

            # Page title centred — sits below the logos
            header_h = max(self._data.get('logo1_h', 18), logo2_h) + 2
            self.set_y(6)
            self.set_font('Arial', 'B', 12)
            self.cell(0, header_h, 'Request for Quotation (RFQ)', 0, 1, 'C')
            self.ln(4)

        def footer(self):
            self.set_y(-25)
            fn = self._data.get('footer_company_name', '')
            fa = self._data.get('footer_company_address', '')
            if fn or fa:
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
                self.ln(2)
                if fn:
                    self.set_font('Arial', 'B', 10)
                    self.cell(0, 5, fn, 0, 1, 'C')
                if fa:
                    self.set_font('Arial', '', 8)
                    self.cell(0, 4, fa, 0, 1, 'C')
            self.set_y(-12)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

        def section_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(26, 58, 92)
            self.set_text_color(255, 255, 255)
            usable = self.w - self.l_margin - self.r_margin
            sx = self.l_margin
            sy = self.get_y()
            sh = 9
            self.rect(sx, sy, usable, sh, 'F')
            self.set_xy(sx + 2, sy + 2)
            self.multi_cell(usable - 4, 6, f'  {title}', border=0, align='L')
            self.set_text_color(0, 0, 0)
            self.set_y(sy + sh)
            self.ln(3)

    def _clean(v):
        if v is None or str(v).strip().lower() in ("nan", "none", ""):
            return ""
        try:
            f = float(v)
            return str(int(f)) if f == int(f) else str(f)
        except Exception:
            return str(v).strip()

    def _write_logo(pdf, logo_data, x, y, w, h):
        if not logo_data:
            return
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(logo_data)
                tmp.flush()
                pdf.image(tmp.name, x=x, y=y, w=w, h=h)
            os.remove(tmp.name)
        except Exception:
            pass

    # ── COVER PAGE ────────────────────────────────────────────────────────────
    def create_cover_page(pdf):
        pdf.add_page()
        logo2_data = data.get('logo2_data') or LOGO2_BYTES
        logo2_w    = data.get('logo2_w', 45)
        logo2_h    = data.get('logo2_h', 20)

        # Logo 1 — left, user-defined size
        _write_logo(pdf, data.get('logo1_data'), pdf.l_margin, 12,
                    data.get('logo1_w', 35), data.get('logo1_h', 18))
        # Logo 2 — right, user-uploaded PNG or hardcoded fallback
        _write_logo(pdf, logo2_data,
                    pdf.w - pdf.r_margin - logo2_w, 12, logo2_w, logo2_h)

        pdf.set_y(35)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 8, 'CONFIDENTIAL', 0, 1, 'C')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(8)

        pdf.set_font('Arial', 'B', 28)
        pdf.cell(0, 14, 'Request for Quotation', 0, 1, 'C')
        pdf.ln(4)
        pdf.set_font('Arial', '', 16)
        pdf.cell(0, 8, 'For', 0, 1, 'C')
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, data.get('Type_of_items', ''), 0, 1, 'C')
        pdf.ln(4)
        pdf.set_font('Arial', '', 16)
        pdf.cell(0, 8, 'for', 0, 1, 'C')
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, data.get('Storage', ''), 0, 1, 'C')
        pdf.ln(4)
        pdf.set_font('Arial', '', 16)
        pdf.cell(0, 8, 'At', 0, 1, 'C')
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 22)
        pdf.cell(0, 10, data.get('company_name', ''), 0, 1, 'C')
        pdf.ln(2)
        pdf.set_font('Arial', '', 14)
        pdf.cell(0, 8, data.get('company_address', ''), 0, 1, 'C')

    # ── MERGED MODEL DETAILS TABLE ────────────────────────────────────────────
    def render_model_details(pdf, df, subtitle=""):
        if df is None or df.empty:
            return
        cw = [10, 42, 72, 22, 44]
        total_w = sum(cw)
        rh = 8          # per-row height (body font 9 fits comfortably)
        header_fill = (220, 230, 241)
        req_fill = (255, 255, 204)

        def draw_col_headers():
            pdf.set_fill_color(*header_fill)
            pdf.set_font('Arial', 'B', 11)
            col_y = pdf.get_y()
            col_h = 9
            cx = pdf.l_margin
            labels = ["Sr.no", "Category", "Description", "UNIT", "Requirement"]
            for i, c in enumerate(labels):
                lines = max(1, -(-len(c) // max(1, int(cw[i] / 2.5))))
                col_h = max(col_h, lines * 6 + 3)
            for i, c in enumerate(labels):
                pdf.rect(cx, col_y, cw[i], col_h, 'FD')
                pdf.set_xy(cx + 1, col_y + 1)
                pdf.multi_cell(cw[i] - 2, 6, c, border=0, align='C')
                cx += cw[i]
                pdf.set_xy(cx, col_y)
            pdf.set_y(col_y + col_h)

        # Section header — navy, font 12, wraps inside box
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(26, 58, 92)
        pdf.set_text_color(255, 255, 255)
        hdr_x = pdf.l_margin
        hdr_y = pdf.get_y()
        hdr_h = 9
        pdf.rect(hdr_x, hdr_y, total_w, hdr_h, 'F')
        pdf.set_xy(hdr_x + 2, hdr_y + 2)
        pdf.multi_cell(total_w - 4, 6, '  Model Details', border=0, align='L')
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(hdr_y + hdr_h)

        if subtitle:
            pdf.set_font('Arial', 'B', 9)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(total_w, 7, subtitle, border=1, ln=1, align='C', fill=True)

        draw_col_headers()

        # Build groups
        rows_list = []
        for _, r in df.iterrows():
            rows_list.append({
                "sr":   _clean(r.get("Sr.no", "")),
                "cat":  _clean(r.get("Category", "")),
                "desc": _clean(r.get("Description", "")),
                "unit": _clean(r.get("UNIT", r.get("Unit", ""))),
                "req":  _clean(r.get("Requirement", ""))
            })

        groups = []
        if rows_list:
            curr = [rows_list[0]]
            for item in rows_list[1:]:
                if item["sr"] != "" or item["cat"] != "":
                    groups.append(curr)
                    curr = [item]
                else:
                    curr.append(item)
            groups.append(curr)

        pdf.set_font('Arial', '', 9)
        for grp in groups:
            group_h = len(grp) * rh
            if pdf.get_y() + group_h > pdf.page_break_trigger:
                pdf.add_page()
                draw_col_headers()
                pdf.set_font('Arial', '', 9)

            sy = pdf.get_y()
            sx = pdf.l_margin

            # Sr.no — merged vertically
            pdf.rect(sx, sy, cw[0], group_h)
            pdf.set_xy(sx, sy + (group_h - 5) / 2)
            pdf.cell(cw[0], 5, grp[0]["sr"], align='C')

            # Category — merged vertically, wrapped
            pdf.rect(sx + cw[0], sy, cw[1], group_h)
            pdf.set_xy(sx + cw[0] + 1, sy + 1)
            pdf.multi_cell(cw[1] - 2, 5, grp[0]["cat"], border=0, align='L')

            # Description / Unit / Requirement — one row per sub-item
            for idx, item in enumerate(grp):
                ry = sy + idx * rh
                rx = sx + cw[0] + cw[1]

                # Description — wrap inside cell
                pdf.rect(rx, ry, cw[2], rh)
                pdf.set_xy(rx + 1, ry + 1)
                pdf.multi_cell(cw[2] - 2, 5, item["desc"], border=0, align='L')
                pdf.set_xy(rx + cw[2], ry)   # reset after multi_cell

                # UNIT
                pdf.rect(rx + cw[2], ry, cw[3], rh)
                pdf.set_xy(rx + cw[2], ry + 1)
                pdf.cell(cw[3], rh - 2, item["unit"], align='C')

                # Requirement — yellow highlight
                pdf.set_fill_color(*req_fill)
                pdf.rect(rx + cw[2] + cw[3], ry, cw[4], rh, 'FD')
                pdf.set_xy(rx + cw[2] + cw[3] + 1, ry + 1)
                pdf.multi_cell(cw[4] - 2, 5, item["req"], border=0, align='C')
                pdf.set_fill_color(255, 255, 255)

            pdf.set_y(sy + group_h)
        pdf.ln(5)

    # ── NAVY SECTION TABLE ────────────────────────────────────────────────────
    def render_navy_section(pdf, title, df, cols, widths):
        if df is None or df.empty:
            return
        total_w = sum(widths)
        if pdf.get_y() + 30 > pdf.page_break_trigger:
            pdf.add_page()

        # ── Navy section title — wraps inside box ────────────────────────────
        pdf.set_fill_color(26, 58, 92)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 12)
        title_x = pdf.l_margin
        title_y = pdf.get_y()
        # Measure height needed for the title text
        title_lines = max(1, -(-len(f'  {title}') // max(1, int(total_w / 3.0))))
        title_h = title_lines * 6 + 4
        pdf.rect(title_x, title_y, total_w, title_h, 'F')
        pdf.set_xy(title_x + 2, title_y + 2)
        pdf.multi_cell(total_w - 4, 6, f'  {title}', border=0, align='L')
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(title_y + title_h)
        pdf.ln(1)

        # ── Column headers — each wraps inside its own box ───────────────────
        pdf.set_fill_color(220, 230, 241)
        pdf.set_font('Arial', 'B', 11)
        col_header_y = pdf.get_y()
        # Calculate max height needed across all column headers
        col_header_h = 9
        for i, c in enumerate(cols):
            label = c.replace('\n', ' ')
            lines = max(1, -(-len(label) // max(1, int(widths[i] / 2.5))))
            col_header_h = max(col_header_h, lines * 6 + 4)

        cx = pdf.l_margin
        for i, c in enumerate(cols):
            label = c.replace('\n', ' ')
            pdf.rect(cx, col_header_y, widths[i], col_header_h, 'FD')
            pdf.set_xy(cx + 1, col_header_y + 1)
            pdf.multi_cell(widths[i] - 2, 6, label, border=0, align='C')
            cx += widths[i]
            pdf.set_xy(cx, col_header_y)
        pdf.set_y(col_header_y + col_header_h)

        # ── Data rows ────────────────────────────────────────────────────────
        pdf.set_font('Arial', '', 9)

        for _, row in df.iterrows():
            row_vals = [_clean(row.get(c, "")) for c in cols]

            # Calculate required row height based on tallest cell
            rh = 8
            for i, val in enumerate(row_vals):
                chars_per_line = max(1, int(widths[i] / 2.2))
                lines = max(1, -(-len(val) // chars_per_line))
                rh = max(rh, lines * 5 + 3)

            if pdf.get_y() + rh > pdf.page_break_trigger:
                pdf.add_page()
                # Repeat column headers
                pdf.set_fill_color(220, 230, 241)
                pdf.set_font('Arial', 'B', 11)
                cy2 = pdf.get_y()
                cx2 = pdf.l_margin
                for i, c in enumerate(cols):
                    label = c.replace('\n', ' ')
                    pdf.rect(cx2, cy2, widths[i], col_header_h, 'FD')
                    pdf.set_xy(cx2 + 1, cy2 + 1)
                    pdf.multi_cell(widths[i] - 2, 6, label, border=0, align='C')
                    cx2 += widths[i]
                    pdf.set_xy(cx2, cy2)
                pdf.set_y(cy2 + col_header_h)
                pdf.set_font('Arial', '', 9)

            row_y = pdf.get_y()
            cx = pdf.l_margin

            for i, val in enumerate(row_vals):
                pdf.rect(cx, row_y, widths[i], rh)
                pdf.set_xy(cx + 1, row_y + 1)
                pdf.multi_cell(widths[i] - 2, 5, val, border=0,
                               align='L' if i <= 1 else 'C')
                cx += widths[i]
                pdf.set_xy(cx, row_y)

            pdf.set_y(row_y + rh)
        pdf.ln(4)

    # ── LANDSCAPE STORAGE CONTAINER TABLE ─────────────────────────────────────
    def render_container_table(pdf, df, images_dict=None):
        headers = ITEM_TABLE_HEADERS
        cw = ITEM_TABLE_COL_WIDTHS
        hh = 10
        rh = 28
        IMG_W, IMG_H = 22, 18

        def draw_header():
            pdf.set_font("Arial", "B", 7)
            pdf.set_fill_color(220, 230, 241)
            sy = pdf.get_y()
            cx = pdf.l_margin
            for i, h in enumerate(headers):
                pdf.rect(cx, sy, cw[i], hh)
                pdf.set_xy(cx, sy + 1)
                pdf.multi_cell(cw[i], 3, h, align="C")
                cx += cw[i]
            pdf.set_y(sy + hh)

        draw_header()
        pdf.set_font("Arial", "", 7)

        if df is not None and not df.empty:
            for idx, row in df.iterrows():
                ry = pdf.get_y()
                if ry + rh > pdf.page_break_trigger:
                    pdf.add_page(orientation='L')
                    draw_header()
                    pdf.set_font("Arial", "", 7)
                    ry = pdf.get_y()

                vals = [
                    str(idx + 1), _clean(row.get("Description")),
                    _clean(row.get("Material Type")), _clean(row.get("Length")),
                    _clean(row.get("Width")), _clean(row.get("Height")),
                    _clean(row.get("Inner Length")), _clean(row.get("Inner Width")),
                    _clean(row.get("Inner Height")), _clean(row.get("Unit of Measurement")),
                    _clean(row.get("Base Type")), _clean(row.get("Colour")),
                    _clean(row.get("Weight Kg")), _clean(row.get("Load capacity")),
                    _clean(row.get("Stackable")), _clean(row.get("BIn Cover/ Open")),
                    _clean(row.get("Rate")), _clean(row.get("Qty")), "", _clean(row.get("Remarks"))
                ]

                cx = pdf.l_margin
                for i, val in enumerate(vals):
                    pdf.rect(cx, ry, cw[i], rh)
                    if headers[i] == "Conceptual Image":
                        img_bytes = row.get("image_data_bytes")
                        if not isinstance(img_bytes, bytes) and images_dict:
                            img_bytes = images_dict.get(idx)
                        if isinstance(img_bytes, bytes):
                            try:
                                img = Image.open(io.BytesIO(img_bytes))
                                ix = cx + (cw[i] - IMG_W) / 2
                                iy = ry + (rh - IMG_H) / 2
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                                    img.save(tmp.name, "PNG")
                                    pdf.image(tmp.name, x=ix, y=iy, w=IMG_W, h=IMG_H)
                                os.remove(tmp.name)
                            except Exception:
                                pass
                    else:
                        pdf.set_xy(cx, ry + 8)
                        pdf.multi_cell(cw[i], 4, val, align="C")
                    cx += cw[i]
                pdf.set_y(ry + rh)
        else:
            for _ in range(3):
                ry = pdf.get_y()
                cx = pdf.l_margin
                for w in cw:
                    pdf.rect(cx, ry, w, rh)
                    cx += w
                pdf.set_y(ry + rh)
        pdf.ln(6)

    # ── GENERIC ITEMS TABLE ────────────────────────────────────────────────────
    def render_generic_items(pdf, df):
        if df is None or df.empty:
            return
        cols = ["Sr.No", "Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"]
        widths = [12, 40, 70, 18, 18, 32]
        total_w = sum(widths)

        pdf.set_fill_color(220, 230, 241)
        pdf.set_font('Arial', 'B', 11)
        ch_y = pdf.get_y()
        ch_h = 9
        for i, c in enumerate(cols):
            lines = max(1, -(-len(c) // max(1, int(widths[i] / 2.5))))
            ch_h = max(ch_h, lines * 6 + 3)
        cx = pdf.l_margin
        for i, c in enumerate(cols):
            pdf.rect(cx, ch_y, widths[i], ch_h, 'FD')
            pdf.set_xy(cx + 1, ch_y + 1)
            pdf.multi_cell(widths[i] - 2, 6, c, border=0, align='C')
            cx += widths[i]
            pdf.set_xy(cx, ch_y)
        pdf.set_y(ch_y + ch_h)
        pdf.set_font('Arial', '', 9)

        for i, (_, row) in enumerate(df.iterrows()):
            vals = [
                str(i + 1), _clean(row.get("Item Name")),
                _clean(row.get("Description / Specification")),
                _clean(row.get("Quantity")), _clean(row.get("Unit")),
                _clean(row.get("Remarks"))
            ]
            rh = 8
            if pdf.get_y() + rh > pdf.page_break_trigger:
                pdf.add_page()
                pdf.set_fill_color(220, 230, 241)
                pdf.set_font('Arial', 'B', 11)
                cy2 = pdf.get_y()
                cx2 = pdf.l_margin
                for j, c in enumerate(cols):
                    pdf.rect(cx2, cy2, widths[j], ch_h, 'FD')
                    pdf.set_xy(cx2 + 1, cy2 + 1)
                    pdf.multi_cell(widths[j] - 2, 6, c, border=0, align='C')
                    cx2 += widths[j]
                    pdf.set_xy(cx2, cy2)
                pdf.set_y(cy2 + ch_h)
                pdf.set_font('Arial', '', 9)
            row_y = pdf.get_y()
            cx = pdf.l_margin
            for j, val in enumerate(vals):
                pdf.rect(cx, row_y, widths[j], rh)
                pdf.set_xy(cx + 1, row_y + 1)
                pdf.multi_cell(widths[j] - 2, 5, val, border=0,
                               align='L' if j <= 2 else 'C')
                cx += widths[j]
                pdf.set_xy(cx, row_y)
            pdf.set_y(row_y + rh)
        pdf.ln(5)

    # ── LAYOUT IMAGES SECTION ─────────────────────────────────────────────────
    def render_layout_images(pdf, layout_images):
        """
        Render 1-5 layout/drawing images in a 'Layout:-' section.
        Images are placed 2-per-row (side by side), fitting the page width,
        with a navy section header matching the rest of the document.
        """
        if not layout_images:
            return

        # New page for layout so it's clean
        pdf.add_page()

        # Section header — matches the navy style
        pdf.set_fill_color(26, 58, 92)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '  Layout:-', border=0, ln=1, align='L', fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(6)

        usable_w = pdf.w - pdf.l_margin - pdf.r_margin
        n = len(layout_images)

        if n == 1:
            # Single image — centred, large
            img_w = usable_w * 0.75
            img_h = img_w * 0.65
            img_x = pdf.l_margin + (usable_w - img_w) / 2
            _place_image(pdf, layout_images[0], img_x, pdf.get_y(), img_w, img_h)
            pdf.set_y(pdf.get_y() + img_h + 4)

        elif n == 2:
            # Side by side
            img_w = (usable_w - 6) / 2
            img_h = img_w * 0.7
            y = pdf.get_y()
            _place_image(pdf, layout_images[0], pdf.l_margin, y, img_w, img_h)
            _place_image(pdf, layout_images[1], pdf.l_margin + img_w + 6, y, img_w, img_h)
            pdf.set_y(y + img_h + 4)

        else:
            # 2-per-row grid for 3, 4, 5 images
            img_w = (usable_w - 6) / 2
            img_h = img_w * 0.65
            for i in range(0, n, 2):
                y = pdf.get_y()
                if y + img_h > pdf.page_break_trigger:
                    pdf.add_page()
                    y = pdf.get_y()
                # Left image
                _place_image(pdf, layout_images[i], pdf.l_margin, y, img_w, img_h)
                # Right image (if exists)
                if i + 1 < n:
                    _place_image(pdf, layout_images[i + 1], pdf.l_margin + img_w + 6, y, img_w, img_h)
                pdf.set_y(y + img_h + 6)

        pdf.ln(4)

    def _place_image(pdf, img_bytes, x, y, w, h):
        """Helper to place a single image byte string onto the PDF at given position."""
        if not isinstance(img_bytes, bytes):
            return
        try:
            img = Image.open(io.BytesIO(img_bytes))
            # Maintain aspect ratio within the bounding box
            iw, ih = img.size
            ratio = min(w / iw, h / ih)
            draw_w = iw * ratio
            draw_h = ih * ratio
            # Centre within bounding box
            cx = x + (w - draw_w) / 2
            cy = y + (h - draw_h) / 2
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                img.save(tmp.name, "PNG")
                pdf.image(tmp.name, x=cx, y=cy, w=draw_w, h=draw_h)
            os.remove(tmp.name)
            # Thin border around bounding box
            pdf.rect(x, y, w, h)
        except Exception:
            pass

    # ── BUILD PDF ─────────────────────────────────────────────────────────────
    pdf = PDF('P', 'mm', 'A4')
    pdf._data = data
    pdf.alias_nb_pages()

    create_cover_page(pdf)
    pdf.add_page()

    # 1. Background
    pdf.section_title('REQUIREMENT BACKGROUND')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, data.get('purpose', ''), 0, 'L')
    pdf.ln(5)

    # 2. Technical Specification
    pdf.section_title('TECHNICAL SPECIFICATION')

    rfq_category = data.get('rfq_category', 'General')
    wh_sub = data.get('wh_sub', '')

    if rfq_category == "Warehouse Equipment":
        if wh_sub == "Storage Container":
            pdf.add_page(orientation='L')
            sc_df = data.get('storage_containers_df', pd.DataFrame())
            sc_images = data.get('storage_containers_images', {})
            render_container_table(pdf, sc_df, sc_images)
            pdf.add_page(orientation='P')
            render_layout_images(pdf, data.get('layout_images', []))

        elif wh_sub == "Automated Storage System":
            # Items list
            wh_items = data.get('wh_items_df', pd.DataFrame())
            if wh_items is not None and not wh_items.empty:
                valid_items = wh_items[wh_items.get("Item Name", pd.Series(dtype=str)).astype(str).str.strip() != ""]
                if not valid_items.empty:
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(0, 7, 'Items Required:', 0, 1)
                    pdf.set_font('Arial', '', 10)
                    for _, r in valid_items.iterrows():
                        item_line = f"  - {_clean(r.get('Item Name', ''))}   Qty: {_clean(r.get('Quantity', ''))} {_clean(r.get('Unit', ''))}"
                        if _clean(r.get('Description / Specification', '')):
                            item_line += f"   -   {_clean(r.get('Description / Specification', ''))}"
                        pdf.cell(0, 6, item_line, 0, 1)
                    pdf.ln(4)

            render_model_details(pdf, data.get('carousel_model_df'), subtitle=data.get('model_detail_header', ''))
            render_navy_section(pdf, "Key Features", data.get('key_features_df'),
                                ["Sr.no", "Description", "Status", "Remarks"], [10, 110, 30, 40])
            render_navy_section(pdf, "Inbuilt features", data.get('inbuilt_features_df'),
                                ["Sr.no", "Description", "Vendor Scope (Yes/No)", "Remarks"], [10, 110, 30, 40])
            render_navy_section(pdf, "Installation Accountability", data.get('installation_df'),
                                ["Sr.no", "Category", "Vendor Scope (Yes/No)", "Customer Scope (Yes/No)", "Remarks"],
                                [10, 75, 28, 28, 49])
            render_layout_images(pdf, data.get('layout_images', []))

        else:
            # Storage System / Material Handling / Dock Leveller
            pfx = {'Storage System': 'ss', 'Material Handling': 'mh', 'Dock Leveller': 'dl'}.get(wh_sub, 'ss')
            render_model_details(pdf, data.get(f'spec_{pfx}_Model Details'),
                                 subtitle=data.get('model_detail_header', ''))
            render_navy_section(pdf, "Key Features", data.get(f'spec_{pfx}_Key Features'),
                                ["Sr.no", "Description", "Status", "Remarks"], [10, 110, 30, 40])
            render_navy_section(pdf, "Inbuilt features", data.get(f'spec_{pfx}_Inbuilt features'),
                                ["Sr.no", "Description", "Vendor Scope (Yes/No)", "Remarks"], [10, 110, 30, 40])
            render_navy_section(pdf, "Installation Accountability",
                                data.get(f'spec_{pfx}_Installation Accountability'),
                                ["Sr.no", "Category", "Vendor Scope (Yes/No)", "Customer Scope (Yes/No)", "Remarks"],
                                [10, 75, 28, 28, 49])
            render_layout_images(pdf, data.get('layout_images', []))
    else:
        render_generic_items(pdf, data.get('items_df', pd.DataFrame()))

    # 3. Timelines
    if pdf.get_y() + 60 > pdf.page_break_trigger:
        pdf.add_page()
    pdf.section_title('TIMELINES')
    milestones = [
        ("Date of RFQ Release",             data.get('date_release')),
        ("Query Resolution Deadline",        data.get('date_query')),
        ("Face to Face Meet",                data.get('date_meet')),
        ("First Level Quotation",            data.get('date_quote')),
        ("Negotiation & Vendor Selection",   data.get('date_selection')),
        ("Joint Review of Quotation",        data.get('date_review')),
        ("Delivery Deadline",                data.get('date_delivery')),
        ("Installation Deadline",            data.get('date_install')),
    ]
    pdf.set_fill_color(220, 230, 241)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(90, 9, 'Milestone', 1, 0, 'C', fill=True)
    pdf.cell(100, 9, 'Date', 1, 1, 'C', fill=True)
    pdf.set_font('Arial', '', 11)
    for m, d in milestones:
        date_str = d.strftime('%B %d, %Y') if d else 'TBD'
        pdf.cell(90, 8, m, 1, 0, 'L')
        pdf.cell(100, 8, date_str, 1, 1, 'L')
    pdf.ln(5)

    # 4. SPOC
    if pdf.get_y() + 40 > pdf.page_break_trigger:
        pdf.add_page()
    pdf.section_title('SINGLE POINT OF CONTACT')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 6, 'Primary Contact:', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f"Name: {data.get('spoc1_name', '')}   |   Designation: {data.get('spoc1_designation', '')}", 0, 1)
    pdf.cell(0, 7, f"Phone: {data.get('spoc1_phone', '')}   |   Email: {data.get('spoc1_email', '')}", 0, 1)
    if data.get('spoc2_name'):
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 6, 'Secondary Contact:', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f"Name: {data.get('spoc2_name', '')}   |   Designation: {data.get('spoc2_designation', '')}", 0, 1)
        pdf.cell(0, 7, f"Phone: {data.get('spoc2_phone', '')}   |   Email: {data.get('spoc2_email', '')}", 0, 1)
    pdf.ln(5)

    # 5. Commercials
    if pdf.get_y() + 50 > pdf.page_break_trigger:
        pdf.add_page()
    pdf.section_title('COMMERCIAL REQUIREMENTS')
    commercial_df = data.get('commercial_df', pd.DataFrame())
    if commercial_df is not None and not commercial_df.empty:
        pdf.set_fill_color(220, 230, 241)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(85, 9, 'Cost Component', 1, 0, 'C', fill=True)
        pdf.cell(40, 9, 'Amount', 1, 0, 'C', fill=True)
        pdf.cell(65, 9, 'Remarks', 1, 1, 'C', fill=True)
        pdf.set_font('Arial', '', 11)
        for _, r in commercial_df.iterrows():
            pdf.cell(85, 8, _clean(r.get('Cost Component', '')), 1, 0, 'L')
            pdf.cell(40, 8, '', 1, 0)
            pdf.cell(65, 8, _clean(r.get('Remarks', '')), 1, 1, 'L')
    pdf.ln(5)

    # 6. Submission & Delivery
    if pdf.get_y() + 40 > pdf.page_break_trigger:
        pdf.add_page()
    pdf.section_title('QUOTATION SUBMISSION & DELIVERY')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, f"Submit To: {data.get('submit_to_name', '')}", 0, 1)
    if data.get('submit_to_registered_office'):
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, data.get('submit_to_registered_office', ''), 0, 1)
    pdf.ln(3)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Delivery Location:', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, data.get('delivery_location', ''), 0, 'L')

    annexures = data.get('annexures', '').strip()
    if annexures:
        pdf.ln(5)
        pdf.section_title('ANNEXURES')
        pdf.set_font('Arial', '', 11)
        for line in annexures.split('\n'):
            if line.strip():
                pdf.cell(0, 7, f'  - {line.strip()}', 0, 1)

    return bytes(pdf.output())


# ==============================================================
# STREAMLIT UI
# ==============================================================
st.title("🏭 Request For Quotation Generator")
st.markdown("---")

# ── Step 1: Logos ─────────────────────────────────────────────────────────────
with st.expander("Step 1: Upload Company Logos (Optional)", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Logo 1 — Your company logo (top-left)**")
        logo1_file = st.file_uploader("Upload Logo 1", type=['png', 'jpg', 'jpeg'], key="logo1")
        lc1, lc2 = st.columns(2)
        logo1_w = lc1.number_input("Width (mm)", 5, 80, 35, 1, key="l1w")
        logo1_h = lc2.number_input("Height (mm)", 5, 50, 18, 1, key="l1h")
        if logo1_file:
            st.image(logo1_file, width=160)
    with c2:
        st.markdown("**Logo 2 — Agilomatrix logo (top-right, PNG only)**")
        logo2_file = st.file_uploader("Upload Logo 2 (.png)", type=['png'], key="logo2")
        lc3, lc4 = st.columns(2)
        logo2_w = lc3.number_input("Width (mm)", 20, 80, 45, 1, key="l2w")
        logo2_h = lc4.number_input("Height (mm)", 8, 40, 20, 1, key="l2h")
        if logo2_file:
            st.image(logo2_file, width=160)
        else:
            st.caption("If no logo is uploaded, the default Agilomatrix placeholder appears.")

# ── Step 2: Cover page ────────────────────────────────────────────────────────
with st.expander("Step 2: Add Cover Page Details", expanded=True):
    Type_of_items = st.text_input("Type of Items *", help="e.g., Plastic Blue Bins OR Line Side Racks")
    Storage = st.text_input("Storage Type *", help="e.g., Material Storage")
    company_name = st.text_input("Requester Company Name *", help="e.g., Pinnacle Mobility Solutions Pvt. Ltd")
    company_address = st.text_input("Requester Company Address *", help="e.g., Nanekarwadi, Chakan, Pune 410501")

# ── Step 3: Footer ────────────────────────────────────────────────────────────
with st.expander("Step 3: Add Footer Details (Optional)", expanded=False):
    footer_company_name = st.text_input("Footer Company Name")
    footer_company_address = st.text_input("Footer Company Address")

# ── Step 4: Technical Specifications ─────────────────────────────────────────
st.subheader("Step 4: Technical Specifications")
st.markdown("---")

with st.expander("📦 Technical Specifications", expanded=True):
    category_list = list(CATEGORY_HINTS.keys())

    # Use session_state to persist category selection across reruns
    if 'rfq_category' not in st.session_state:
        st.session_state['rfq_category'] = category_list[0]

    rfq_category = st.selectbox(
        "Select RFQ Category *",
        options=category_list,
        key="rfq_category_select",
        index=category_list.index(st.session_state.get('rfq_category', category_list[0]))
    )
    # Sync to session state
    if st.session_state.get('rfq_category') != rfq_category:
        # Category changed — clear dependent state
        for k in ['dynamic_items_df', 'storage_containers_df', 'storage_containers_images',
                  'wh_items_df', 'carousel_model_df', 'key_features_df',
                  'inbuilt_features_df', 'installation_df',
                  'spec_ss_Model Details', 'spec_ss_Key Features', 'spec_ss_Inbuilt features', 'spec_ss_Installation Accountability',
                  'spec_mh_Model Details', 'spec_mh_Key Features', 'spec_mh_Inbuilt features', 'spec_mh_Installation Accountability',
                  'spec_dl_Model Details', 'spec_dl_Key Features', 'spec_dl_Inbuilt features', 'spec_dl_Installation Accountability']:
            st.session_state.pop(k, None)
        st.session_state['rfq_category'] = rfq_category
        st.session_state.pop('wh_sub', None)

    is_warehouse = (rfq_category == "Warehouse Equipment")

    WH_SUB_CATEGORIES = [
        "Storage System", "Material Handling", "Automated Storage System",
        "Dock Leveller", "Storage Container",
    ]

    if is_warehouse:
        wh_sub = st.selectbox(
            "Select Warehouse Sub-Category *",
            options=WH_SUB_CATEGORIES,
            key="wh_sub_select",
        )
        # Clear sub-state on sub-category change
        if st.session_state.get('wh_sub') != wh_sub:
            for k in ['wh_items_df', 'storage_containers_df', 'storage_containers_images',
                      'carousel_model_df', 'key_features_df', 'inbuilt_features_df', 'installation_df',
                      'spec_ss_Model Details', 'spec_ss_Key Features', 'spec_ss_Inbuilt features', 'spec_ss_Installation Accountability',
                      'spec_mh_Model Details', 'spec_mh_Key Features', 'spec_mh_Inbuilt features', 'spec_mh_Installation Accountability',
                      'spec_dl_Model Details', 'spec_dl_Key Features', 'spec_dl_Inbuilt features', 'spec_dl_Installation Accountability']:
                st.session_state.pop(k, None)
            st.session_state['wh_sub'] = wh_sub
    else:
        wh_sub = ""
        st.session_state['wh_sub'] = ""

    # ── Shared multi-section spec renderer ───────────────────────────────────
    def _render_multisection_spec(state_key_prefix):
        section_cfg = {
            "Model Details": {
                "cols": ["Sr.no", "Category", "Description", "UNIT", "Requirement"],
                "column_config": {
                    "Sr.no":       st.column_config.TextColumn("Sr.no", width="small"),
                    "Category":    st.column_config.TextColumn("Category", width="medium"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                    "UNIT":        st.column_config.TextColumn("UNIT", width="small"),
                    "Requirement": st.column_config.TextColumn("Requirement ✏️", width="medium"),
                },
            },
            "Key Features": {
                "cols": ["Sr.no", "Description", "Status", "Remarks"],
                "column_config": {
                    "Sr.no":       st.column_config.TextColumn("Sr.no", width="small"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                    "Status":      st.column_config.TextColumn("Status ✏️", width="small"),
                    "Remarks":     st.column_config.TextColumn("Remarks", width="large"),
                },
            },
            "Inbuilt features": {
                "cols": ["Sr.no", "Description", "Vendor Scope (Yes/No)", "Remarks"],
                "column_config": {
                    "Sr.no":                 st.column_config.TextColumn("Sr.no", width="small"),
                    "Description":           st.column_config.TextColumn("Description", width="large"),
                    "Vendor Scope (Yes/No)": st.column_config.SelectboxColumn("Vendor Scope ✏️", width="small", options=["", "Yes", "No"]),
                    "Remarks":               st.column_config.TextColumn("Remarks", width="large"),
                },
            },
            "Installation Accountability": {
                "cols": ["Sr.no", "Category", "Vendor Scope (Yes/No)", "Customer Scope (Yes/No)", "Remarks"],
                "column_config": {
                    "Sr.no":                   st.column_config.TextColumn("Sr.no", width="small"),
                    "Category":                st.column_config.TextColumn("Category", width="large"),
                    "Vendor Scope (Yes/No)":   st.column_config.SelectboxColumn("Vendor Scope ✏️", width="small", options=["", "Yes", "No"]),
                    "Customer Scope (Yes/No)": st.column_config.SelectboxColumn("Customer Scope ✏️", width="small", options=["", "Yes", "No"]),
                    "Remarks":                 st.column_config.TextColumn("Remarks", width="medium"),
                },
            },
        }

        for section_name, rows in SPEC_TEMPLATE.items():
            sk = f"spec_{state_key_prefix}_{section_name}"
            cfg = section_cfg[section_name]

            st.markdown(
                f"<div style='background:#1a3a5c;color:white;font-weight:bold;"
                f"padding:6px 10px;margin-top:14px;margin-bottom:2px;"
                f"font-size:14px;border-radius:3px;'>{section_name}</div>",
                unsafe_allow_html=True
            )

            if sk not in st.session_state:
                # Use Customer Scope (Yes/No) key (not the \n version)
                st.session_state[sk] = pd.DataFrame(_copy.deepcopy(rows))

            df = st.session_state[sk].copy()
            for col in cfg["cols"]:
                if col not in df.columns:
                    df[col] = ""
                df[col] = df[col].astype(str).replace("nan", "")
            df = df[cfg["cols"]]

            edited = st.data_editor(
                df, num_rows="dynamic", use_container_width=True,
                column_config=cfg["column_config"],
                key=f"editor_{sk}_{state_key_prefix}"
            )
            st.session_state[sk] = edited

    # ── Layout image uploader helper (1-5 images) ─────────────────────────────
    def _render_layout_uploader(prefix):
        """Renders a Layout section with 1-5 image uploaders below the spec tables."""
        sk = f"layout_images_{prefix}"
        if sk not in st.session_state:
            st.session_state[sk] = []

        st.markdown("---")
        st.markdown(
            "<div style='background:#1a3a5c;color:white;font-weight:bold;"
            "padding:8px 12px;margin-bottom:8px;font-size:15px;border-radius:3px;'>"
            "📐 Layout Images (1 to 5)</div>",
            unsafe_allow_html=True
        )
        st.caption("Upload layout drawings, front/side views, or 3D renders. Min 1, Max 5. These will appear on a dedicated 'Layout:-' page in the PDF.")

        uploaded = []
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                f = st.file_uploader(
                    f"Image {i+1}" + (" *" if i == 0 else " (optional)"),
                    type=["png", "jpg", "jpeg"],
                    key=f"layout_img_{prefix}_{i}"
                )
                if f is not None:
                    uploaded.append(f.getvalue())
                    st.image(f.getvalue(), use_container_width=True)
                elif i < len(st.session_state[sk]):
                    # Show previously uploaded
                    uploaded.append(st.session_state[sk][i])
                    st.image(st.session_state[sk][i], use_container_width=True)

        # Store only non-None images
        st.session_state[sk] = [b for b in uploaded if b]
        n = len(st.session_state[sk])
        if n > 0:
            st.success(f"✅ {n} layout image(s) ready for PDF")
        else:
            st.info("Upload at least 1 layout image to include the Layout section in the PDF.")

    # ── Render per sub-category ───────────────────────────────────────────────
    if is_warehouse:
        if wh_sub in ("Storage System", "Material Handling", "Dock Leveller"):
            pfx = {'Storage System': 'ss', 'Material Handling': 'mh', 'Dock Leveller': 'dl'}[wh_sub]
            st.markdown(f"#### 📋 {wh_sub} Specification")
            st.caption("Pre-filled from standard template. Edit the **Requirement / Status / Vendor Scope** columns.")
            _render_multisection_spec(pfx)
            _render_layout_uploader(pfx)

        elif wh_sub == "Automated Storage System":
            st.markdown("#### 📋 Automated Storage System")
            item_opts = [""] + ["Vertical Carousel System", "Horizontal Carousel System"]
            if 'wh_items_df' not in st.session_state:
                st.session_state['wh_items_df'] = pd.DataFrame([{
                    "Sr.no": 1, "Item Name": "",
                    "Description / Specification": "", "Quantity": 1, "Unit": "Nos", "Remarks": ""
                }])
            df_items = st.session_state['wh_items_df'].copy()
            df_items["Sr.no"] = range(1, len(df_items) + 1)
            df_items["Quantity"] = pd.to_numeric(df_items.get("Quantity", 1), errors='coerce').fillna(1).astype(int)
            for col in ["Item Name", "Description / Specification", "Unit", "Remarks"]:
                if col not in df_items.columns: df_items[col] = ""
                df_items[col] = df_items[col].astype(str).replace("nan", "")

            edited_items = st.data_editor(
                df_items[["Sr.no", "Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"]],
                num_rows="dynamic", use_container_width=True,
                column_config={
                    "Sr.no": st.column_config.NumberColumn("Sr.no", width="small", disabled=True),
                    "Item Name": st.column_config.SelectboxColumn("Item Name ▼", width="medium", options=item_opts),
                    "Description / Specification": st.column_config.TextColumn("Description / Specification", width="large"),
                    "Quantity": st.column_config.NumberColumn("Qty", width="small", min_value=0, step=1, format="%d"),
                    "Unit": st.column_config.SelectboxColumn("Unit ▼", width="small", options=[""] + UNIT_OPTIONS),
                    "Remarks": st.column_config.TextColumn("Remarks", width="medium"),
                }, key="wh_items_editor")
            st.session_state['wh_items_df'] = edited_items

            st.markdown("---")
            model_header = st.text_input("Model Header / Subtitle",
                                         value="3400 (L) x 3200 (W)  -  465 kgs/tray  -  28 m Height",
                                         key="model_detail_header_input")
            st.session_state['model_detail_header'] = model_header

            # Re-use the shared multi-section renderer but with carousel prefix
            st.markdown("#### 📐 Full Specification Tables")
            _render_multisection_spec("carousel")
            _render_layout_uploader("carousel")

        elif wh_sub == "Storage Container":
            st.caption("Select container type, fill dimensions, and upload a conceptual image per row.")
            container_options = [""] + STORAGE_CONTAINERS_ITEMS
            if 'storage_containers_df' not in st.session_state:
                st.session_state['storage_containers_df'] = pd.DataFrame([_empty_container_row(1)])
            if 'storage_containers_images' not in st.session_state:
                st.session_state['storage_containers_images'] = {}

            sc_df = st.session_state['storage_containers_df'].copy()
            sc_df["Sr.No"] = range(1, len(sc_df) + 1)
            for col in ["Description", "Material Type", "Length", "Width", "Height",
                        "Inner Length", "Inner Width", "Inner Height", "Unit of Measurement",
                        "Base Type", "Colour", "Weight Kg", "Load capacity",
                        "Stackable", "BIn Cover/ Open", "Rate", "Remarks"]:
                if col not in sc_df.columns: sc_df[col] = ""
                sc_df[col] = sc_df[col].astype(str).replace("nan", "")
            if "Qty" not in sc_df.columns: sc_df["Qty"] = 1
            sc_df["Qty"] = pd.to_numeric(sc_df["Qty"], errors='coerce').fillna(1).astype(int)

            editor_col, img_col = st.columns([3, 1])
            with editor_col:
                edited_sc = st.data_editor(
                    sc_df, num_rows="dynamic", use_container_width=True,
                    column_config={
                        "Sr.No":               st.column_config.NumberColumn("Sr.No", width="small", disabled=True),
                        "Description":         st.column_config.SelectboxColumn("Container Type ▼", width="medium", options=container_options),
                        "Material Type":       st.column_config.SelectboxColumn("Material ▼", width="small", options=["", "Plastic", "Metal", "Wood", "Corrugated", "Fibre", "Other"]),
                        "Length":              st.column_config.TextColumn("Outer L (mm)", width="small"),
                        "Width":               st.column_config.TextColumn("Outer W (mm)", width="small"),
                        "Height":              st.column_config.TextColumn("Outer H (mm)", width="small"),
                        "Inner Length":        st.column_config.TextColumn("Inner L (mm)", width="small"),
                        "Inner Width":         st.column_config.TextColumn("Inner W (mm)", width="small"),
                        "Inner Height":        st.column_config.TextColumn("Inner H (mm)", width="small"),
                        "Unit of Measurement": st.column_config.SelectboxColumn("UOM ▼", width="small", options=[""] + UNIT_OPTIONS),
                        "Base Type":           st.column_config.SelectboxColumn("Base Type ▼", width="small", options=["", "Flat", "Ribbed", "Louvred", "Grid", "Other"]),
                        "Colour":              st.column_config.TextColumn("Colour", width="small"),
                        "Weight Kg":           st.column_config.TextColumn("Weight (Kg)", width="small"),
                        "Load capacity":       st.column_config.TextColumn("Load Cap (Kg)", width="small"),
                        "Stackable":           st.column_config.SelectboxColumn("Stackable ▼", width="small", options=["", "Yes", "No", "N/A"]),
                        "BIn Cover/ Open":     st.column_config.SelectboxColumn("Cover/Open ▼", width="small", options=["", "Open", "Covered", "Lid", "N/A"]),
                        "Rate":                st.column_config.TextColumn("Rate", width="small"),
                        "Qty":                 st.column_config.NumberColumn("Qty", width="small", min_value=0, step=1),
                        "Remarks":             st.column_config.TextColumn("Remarks", width="medium"),
                    }, key="sc_df_editor")
            with img_col:
                st.write("**Conceptual Images**")
                for i in range(len(edited_sc)):
                    desc = str(edited_sc.iloc[i].get("Description", "")).strip()
                    lbl = f"Row {i+1}: {desc}" if desc else f"Row {i+1}"
                    f_up = st.file_uploader(lbl, type=["png", "jpg", "jpeg"], key=f"sc_img_{i}")
                    if f_up is not None:
                        st.session_state['storage_containers_images'][i] = f_up.getvalue()
                    if i in st.session_state['storage_containers_images']:
                        st.image(st.session_state['storage_containers_images'][i], width=80)

            st.session_state['storage_containers_df'] = edited_sc
            valid_count = len(edited_sc[edited_sc["Description"].astype(str).str.strip() != ""])
            if valid_count:
                st.success(f"✅ {valid_count} container type(s) defined")
            _render_layout_uploader("sc")

    else:
        # Non-warehouse generic category
        hints = CATEGORY_HINTS.get(rfq_category, [])
        if hints:
            st.markdown(f"**💡 Common items in *{rfq_category}*:**")
            btn_cols = st.columns(min(len(hints), 4))
            for idx, hint in enumerate(hints):
                with btn_cols[idx % 4]:
                    if st.button(f"➕ {hint}", key=f"hint_{idx}_{rfq_category}"):
                        if 'dynamic_items_df' not in st.session_state:
                            st.session_state['dynamic_items_df'] = pd.DataFrame(
                                columns=["Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"])
                        new_row = pd.DataFrame([{"Item Name": hint, "Description / Specification": "",
                                                 "Quantity": 1, "Unit": "Nos", "Remarks": ""}])
                        st.session_state['dynamic_items_df'] = pd.concat(
                            [st.session_state['dynamic_items_df'], new_row], ignore_index=True)
                        st.rerun()

        st.markdown("---")
        st.markdown("##### 📋 Item List")
        if 'dynamic_items_df' not in st.session_state:
            st.session_state['dynamic_items_df'] = pd.DataFrame(
                [{"Item Name": "", "Description / Specification": "", "Quantity": 1, "Unit": "Nos", "Remarks": ""}])
        df_items_edit = st.session_state['dynamic_items_df'].copy()
        df_items_edit["Quantity"] = pd.to_numeric(df_items_edit.get("Quantity", 1), errors='coerce').fillna(1).astype(int)
        for col in ["Item Name", "Description / Specification", "Unit", "Remarks"]:
            if col not in df_items_edit.columns: df_items_edit[col] = ""
            df_items_edit[col] = df_items_edit[col].astype(str)

        edited_dynamic = st.data_editor(
            df_items_edit, num_rows="dynamic", use_container_width=True,
            column_config={
                "Item Name":                   st.column_config.TextColumn("Item Name", width="medium", required=True),
                "Description / Specification": st.column_config.TextColumn("Description / Specification", width="large"),
                "Quantity":                    st.column_config.NumberColumn("Qty", width="small", min_value=0, step=1, format="%d"),
                "Unit":                        st.column_config.SelectboxColumn("Unit", width="small", options=UNIT_OPTIONS, required=True),
                "Remarks":                     st.column_config.TextColumn("Remarks", width="medium"),
            }, key="dynamic_items_editor")
        st.session_state['dynamic_items_df'] = edited_dynamic
        n_items = len(edited_dynamic[edited_dynamic["Item Name"].astype(str).str.strip() != ""])
        if n_items > 0:
            st.success(f"✅ {n_items} item(s) added")
        else:
            st.warning("⚠️ Add at least one item to generate the RFQ.")

# ── Steps 5+ — inside the form ────────────────────────────────────────────────
with st.form(key="rfq_form"):
    st.subheader("Step 5: Requirement Background")
    purpose = st.text_area("Purpose of Requirement *", max_chars=1000, height=120,
                           placeholder="Describe why this RFQ is being raised, the business need, and any key constraints...")

    with st.expander("📅 Timelines", expanded=True):
        today = date.today()
        c1, c2, c3 = st.columns(3)
        date_release  = c1.date_input("Date of RFQ Release *",          today)
        date_query    = c1.date_input("Query Resolution Deadline *",     today + timedelta(days=7))
        date_meet     = c1.date_input("Face to Face Meet (optional)",    None)
        date_selection= c2.date_input("Negotiation & Vendor Selection *",today + timedelta(days=30))
        date_delivery = c2.date_input("Delivery Deadline *",             today + timedelta(days=60))
        date_quote    = c2.date_input("First Level Quotation (optional)",None)
        date_install  = c3.date_input("Installation Deadline *",         today + timedelta(days=75))
        date_review   = c3.date_input("Joint Review (optional)",         None)

    with st.expander("👤 Single Point of Contact (SPOC)", expanded=True):
        st.markdown("##### Primary Contact *")
        p1, p2 = st.columns(2)
        spoc1_name        = p1.text_input("Name *",           key="s1n")
        spoc1_designation = p1.text_input("Designation",      key="s1d")
        spoc1_phone       = p2.text_input("Phone No *",        key="s1p")
        spoc1_email       = p2.text_input("Email ID *",        key="s1e")
        st.markdown("##### Secondary Contact (Optional)")
        s1, s2 = st.columns(2)
        spoc2_name        = s1.text_input("Name",              key="s2n")
        spoc2_designation = s1.text_input("Designation",       key="s2d")
        spoc2_phone       = s2.text_input("Phone No",          key="s2p")
        spoc2_email       = s2.text_input("Email ID",          key="s2e")

    with st.expander("💰 Commercial Requirements", expanded=True):
        edited_commercial_df = st.data_editor(
            pd.DataFrame([
                {"Cost Component": "Unit Cost",                  "Remarks": "Per item/unit specified in Section 2."},
                {"Cost Component": "Freight",                    "Remarks": "Specify if included or extra."},
                {"Cost Component": "Any other Handling Cost",    "Remarks": ""},
                {"Cost Component": "Total Basic Cost (Per Unit)","Remarks": ""},
            ]), num_rows="dynamic", use_container_width=True, key="commercial_editor")

    with st.expander("📦 Submission, Delivery & Annexures", expanded=True):
        submit_to_name = st.text_input("Submit To (Company Name) *", "Agilomatrix Pvt. Ltd.")
        submit_to_registered_office = st.text_input(
            "Submit To (Registered Office Address)",
            "Registered Office: F1403, 7 Plumeria Drive, 7PD Street, Tathawade, Pune - 411033")
        delivery_location = st.text_area("Delivery Location Address *", height=80)
        annexures = st.text_area("Annexures (one item per line)", height=80)

    submitted = st.form_submit_button("🚀 Generate RFQ Document", use_container_width=True, type="primary")

# ── PDF Generation ────────────────────────────────────────────────────────────
if submitted:
    # Read category from session_state (persisted across form submit)
    current_category = st.session_state.get('rfq_category', rfq_category)
    current_wh_sub   = st.session_state.get('wh_sub', '')
    is_wh = (current_category == "Warehouse Equipment")

    # Validate mandatory fields
    errors = []
    if not Type_of_items.strip():   errors.append("Type of Items")
    if not Storage.strip():         errors.append("Storage Type")
    if not company_name.strip():    errors.append("Company Name")
    if not company_address.strip(): errors.append("Company Address")
    if not purpose.strip():         errors.append("Purpose of Requirement")
    if not spoc1_name.strip():      errors.append("SPOC Primary Name")
    if not spoc1_phone.strip():     errors.append("SPOC Primary Phone")
    if not spoc1_email.strip():     errors.append("SPOC Primary Email")
    if not submit_to_name.strip():  errors.append("Submit To Company Name")
    if not delivery_location.strip(): errors.append("Delivery Location")

    # Category-specific validation
    if not is_wh:
        items_df_check = st.session_state.get('dynamic_items_df', pd.DataFrame())
        if items_df_check.empty or items_df_check[items_df_check["Item Name"].astype(str).str.strip() != ""].empty:
            errors.append("At least one Item in the Item List")

    if errors:
        st.error(f"⚠️ Please fill in the following mandatory fields:\n" + "\n".join(f"  • {e}" for e in errors))
        st.stop()

    # Build data dict
    pdf_data_dict = {
        'rfq_category': current_category,
        'wh_sub': current_wh_sub,
        'Type_of_items': Type_of_items, 'Storage': Storage,
        'company_name': company_name, 'company_address': company_address,
        'footer_company_name': footer_company_name, 'footer_company_address': footer_company_address,
        'logo1_data': logo1_file.getvalue() if logo1_file else None,
        'logo1_w': logo1_w, 'logo1_h': logo1_h,
        'logo2_data': logo2_file.getvalue() if logo2_file else None,
        'logo2_w': logo2_w, 'logo2_h': logo2_h,
        'purpose': purpose,
        'date_release': date_release, 'date_query': date_query,
        'date_meet': date_meet, 'date_quote': date_quote,
        'date_selection': date_selection, 'date_delivery': date_delivery,
        'date_install': date_install, 'date_review': date_review,
        'spoc1_name': spoc1_name, 'spoc1_designation': spoc1_designation,
        'spoc1_phone': spoc1_phone, 'spoc1_email': spoc1_email,
        'spoc2_name': spoc2_name, 'spoc2_designation': spoc2_designation,
        'spoc2_phone': spoc2_phone, 'spoc2_email': spoc2_email,
        'commercial_df': edited_commercial_df,
        'submit_to_name': submit_to_name,
        'submit_to_registered_office': submit_to_registered_office,
        'delivery_location': delivery_location,
        'annexures': annexures,
        'model_detail_header': st.session_state.get('model_detail_header', ''),
    }

    if is_wh:
        # Collect layout images — key matches the prefix used by _render_layout_uploader
        pfx_map = {
            "Storage Container":       "sc",
            "Automated Storage System":"carousel",
            "Storage System":          "ss",
            "Material Handling":       "mh",
            "Dock Leveller":           "dl",
        }
        layout_key = f"layout_images_{pfx_map.get(current_wh_sub, 'ss')}"
        pdf_data_dict['layout_images'] = st.session_state.get(layout_key, [])

        if current_wh_sub == "Storage Container":
            sc_df = st.session_state.get('storage_containers_df', pd.DataFrame())
            sc_images = st.session_state.get('storage_containers_images', {})
            if sc_df is not None and not sc_df.empty:
                valid_sc = sc_df[sc_df["Description"].astype(str).str.strip() != ""].reset_index(drop=True).copy()
                valid_sc['image_data_bytes'] = [sc_images.get(i) for i in range(len(valid_sc))]
                pdf_data_dict['storage_containers_df'] = valid_sc
            else:
                pdf_data_dict['storage_containers_df'] = pd.DataFrame()
            pdf_data_dict['storage_containers_images'] = sc_images

        elif current_wh_sub == "Automated Storage System":
            pdf_data_dict['wh_items_df']       = st.session_state.get('wh_items_df', pd.DataFrame())
            # Pull from carousel spec sections
            for section_name in SPEC_TEMPLATE.keys():
                sk = f"spec_carousel_{section_name}"
                fallback = pd.DataFrame(_copy.deepcopy(SPEC_TEMPLATE[section_name]))
                pdf_data_dict[{
                    "Model Details":               'carousel_model_df',
                    "Key Features":                'key_features_df',
                    "Inbuilt features":            'inbuilt_features_df',
                    "Installation Accountability": 'installation_df',
                }[section_name]] = st.session_state.get(sk, fallback)

        else:
            pfx = {'Storage System': 'ss', 'Material Handling': 'mh', 'Dock Leveller': 'dl'}.get(current_wh_sub, 'ss')
            for section_name in SPEC_TEMPLATE.keys():
                sk = f"spec_{pfx}_{section_name}"
                fallback = pd.DataFrame(_copy.deepcopy(SPEC_TEMPLATE[section_name]))
                pdf_data_dict[f"spec_{pfx}_{section_name}"] = st.session_state.get(sk, fallback)
    else:
        pdf_data_dict['layout_images'] = []
        items_df = st.session_state.get('dynamic_items_df', pd.DataFrame())
        pdf_data_dict['items_df'] = items_df[items_df["Item Name"].astype(str).str.strip() != ""].reset_index(drop=True)

    with st.spinner("⚙️ Generating your RFQ PDF..."):
        try:
            pdf_bytes = create_advanced_rfq_pdf(pdf_data_dict)
            st.success("✅ RFQ PDF Generated Successfully!")
            fname = f"RFQ_{Type_of_items.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
            st.download_button(
                "📥 Download RFQ Document",
                data=pdf_bytes, file_name=fname,
                mime="application/pdf",
                use_container_width=True, type="primary"
            )
        except Exception as e:
            st.error(f"❌ PDF generation failed: {e}")
            st.exception(e)
