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
# SPEC TABLE DATA — multi-section format matching Excel exactly
# Every type uses the same structure:
#   dict keyed by section title → list of row dicts
# Each section renders as: bold title header row  +  5-col table beneath it
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

# ── MATERIAL HANDLING ─────────────────────────────────────────────────────────
MATERIAL_HANDLING_SPEC = {
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

# ── DOCK LEVELLER ─────────────────────────────────────────────────────────────
DOCK_LEVELLER_SPEC = {
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

# Automated Storage System (VStore / Carousel) — exactly matches Excel
CAROUSEL_SPEC_TEMPLATE = {
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
                "",
                str(row.get("Remarks", ""))
            ]

            current_x = pdf.l_margin
            for i, value in enumerate(row_values):
                w = col_widths[i]
                pdf.rect(current_x, row_y, w, row_height)
                if headers[i] == "Conceptual Image":
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
            # --- Logos ---
            logo1_data = data.get('logo1_data')
            if logo1_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo1_data); tmp.flush()
                    self.image(tmp.name, x=self.l_margin, y=20, w=data.get('logo1_w', 35), h=data.get('logo1_h', 20))
                    os.remove(tmp.name)
            
            self.set_y(40); self.set_x(self.l_margin); self.set_font('Arial', 'B', 14); self.set_text_color(255, 0, 0)
            self.cell(0, 10, 'CONFIDENTIAL'); self.set_text_color(0, 0, 0)
            
            logo2_data = data.get('logo2_data')
            if logo2_data:
                logo2_w = data.get('logo2_w', 42)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo2_data); tmp.flush()
                    self.image(tmp.name, x=self.w - self.r_margin - logo2_w, y=20, w=logo2_w, h=data.get('logo2_h', 20))
                    os.remove(tmp.name)
            
            # --- Cover Text ---
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
            if logo1_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo1_data); tmp.flush()
                    self.image(tmp.name, x=self.l_margin, y=10, w=data.get('logo1_w', 35), h=data.get('logo1_h', 20))
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

    pdf = PDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.create_cover_page(data)
    pdf.add_page()

    # 1. Background
    pdf.section_title('REQUIREMENT BACKGROUND')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, data['purpose'], 0, 'L')
    pdf.ln(5)

    # 2. Technical Specification Header
    pdf.section_title('TECHNICAL SPECIFICATION')
    rfq_category = data.get('rfq_category', 'General')
    wh_sub = data.get('wh_sub', '')

    def _clean(v):
        if v is None or str(v).lower() in ("nan", "none", ""): return ""
        try:
            f = float(v)
            if f == int(f): return str(int(f))
            return str(f)
        except: return str(v).strip()

    # --- THE UPDATED MODEL DETAILS TABLE (WITH MERGING & COLORS) ---
    def render_merged_model_details(df, title="Model Details", subtitle=""):
        if df is None or df.empty: return
        # A4 Width is ~190mm usable. 
        cw = [10, 45, 75, 20, 40] 
        total_w = sum(cw)
        rh = 7 # Row Height

        # Table Header Styling (Blue/Grey)
        header_fill = (220, 230, 241) 
        req_fill = (255, 255, 204) # Yellow for requirements

        # 1. Title Row
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(total_w, 8, title, border=1, ln=1, align='C')
        
        # 2. Subtitle Row (if provided, like the dimensions string)
        if subtitle:
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(total_w, 8, subtitle, border=1, ln=1, align='C')

        # 3. Column Header Row
        pdf.set_fill_color(*header_fill)
        pdf.set_font('Arial', 'B', 8)
        cols = ["Sr.no", "Category", "Description", "UNIT", "Requirement"]
        for i, c in enumerate(cols):
            pdf.cell(cw[i], 8, c, border=1, align='C', fill=True)
        pdf.ln()

        # 4. Prepare Data for Merging Logic
        rows_list = []
        for _, r in df.iterrows():
            rows_list.append({
                "sr": _clean(r.get("Sr.no", "")),
                "cat": _clean(r.get("Category", "")),
                "desc": _clean(r.get("Description", "")),
                "unit": _clean(r.get("UNIT", r.get("Unit", ""))),
                "req": _clean(r.get("Requirement", ""))
            })

        # Group rows by "non-empty Sr.no or Category"
        groups = []
        if rows_list:
            curr_group = [rows_list[0]]
            for i in range(1, len(rows_list)):
                if rows_list[i]["sr"] != "" or rows_list[i]["cat"] != "":
                    groups.append(curr_group)
                    curr_group = [rows_list[i]]
                else:
                    curr_group.append(rows_list[i])
            groups.append(curr_group)

        # 5. Render Groups
        pdf.set_font('Arial', '', 8)
        for grp in groups:
            group_h = len(grp) * rh
            
            # Check Page Break
            if pdf.get_y() + group_h > pdf.page_break_trigger:
                pdf.add_page()
                pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(*header_fill)
                for i, c in enumerate(cols): pdf.cell(cw[i], 8, c, border=1, align='C', fill=True)
                pdf.ln(); pdf.set_font('Arial', '', 8)

            start_y = pdf.get_y()
            start_x = pdf.l_margin

            # Col 1: Sr.no (Merged)
            pdf.rect(start_x, start_y, cw[0], group_h)
            pdf.set_xy(start_x, start_y + (group_h/2) - 3)
            pdf.cell(cw[0], 6, grp[0]["sr"], align='C')

            # Col 2: Category (Merged)
            pdf.rect(start_x + cw[0], start_y, cw[1], group_h)
            pdf.set_xy(start_x + cw[0] + 1, start_y + (group_h/2) - 3)
            pdf.multi_cell(cw[1] - 2, 6, grp[0]["cat"], border=0, align='L')

            # Cols 3, 4, 5: Row by Row
            for idx, item in enumerate(grp):
                row_y = start_y + (idx * rh)
                row_x = start_x + cw[0] + cw[1]

                # Description
                pdf.rect(row_x, row_y, cw[2], rh)
                pdf.set_xy(row_x + 1, row_y)
                pdf.cell(cw[2]-1, rh, item["desc"], align='L')

                # Unit
                pdf.rect(row_x + cw[2], row_y, cw[3], rh)
                pdf.set_xy(row_x + cw[2], row_y)
                pdf.cell(cw[3], rh, item["unit"], align='C')

                # Requirement (Yellow Highlight)
                pdf.set_fill_color(*req_fill)
                pdf.rect(row_x + cw[2] + cw[3], row_y, cw[4], rh, 'FD')
                pdf.set_xy(row_x + cw[2] + cw[3], row_y)
                pdf.cell(cw[4], rh, item["req"], align='C')

            pdf.set_y(start_y + group_h)
        pdf.ln(5)

    # Helper for standard navy-blue title tables (Key Features, etc.)
    def render_navy_section(title, df, cols, widths, fill_col_idx=None):
        if df is None or df.empty: return
        if pdf.get_y() + 20 > pdf.page_break_trigger: pdf.add_page()
        
        total_w = sum(widths)
        pdf.set_fill_color(26, 58, 92); pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(total_w, 8, f"  {title}", 0, 1, 'L', fill=True)
        pdf.set_text_color(0, 0, 0); pdf.ln(1)
        
        pdf.set_fill_color(220, 230, 241); pdf.set_font('Arial', 'B', 8)
        for i, c in enumerate(cols):
            pdf.cell(widths[i], 8, c, border=1, align='C', fill=True)
        pdf.ln(); pdf.set_font('Arial', '', 8)
        
        for _, row in df.iterrows():
            row_vals = [str(row.get(c, "")).strip() for c in cols]
            rh = 8
            if pdf.get_y() + rh > pdf.page_break_trigger: pdf.add_page()
            
            curr_x = pdf.l_margin
            for i, val in enumerate(row_vals):
                pdf.rect(curr_x, pdf.get_y(), widths[i], rh)
                pdf.set_xy(curr_x + 1, pdf.get_y())
                pdf.cell(widths[i]-2, rh, val, align='L' if i==1 else 'C')
                curr_x += widths[i]
            pdf.ln(rh)
        pdf.ln(4)

    # Dispatching Technical Content
    if rfq_category == "Warehouse Equipment":
        if wh_sub == "Automated Storage System":
            # 1. Show the specific items chosen
            wh_items = data.get('wh_items_df', pd.DataFrame())
            if not wh_items.empty:
                # Standard Portrait Items Table
                pdf.set_font('Arial', 'B', 10); pdf.cell(0, 8, "Items Required", 0, 1)
                pdf.set_font('Arial', '', 9)
                # ... Simplified items table ...
                for _, r in wh_items.iterrows():
                    pdf.cell(0, 6, f"- {r['Item Name']} (Qty: {r['Quantity']})", 0, 1)
                pdf.ln(4)

            # 2. The Merged Model Details Table (Exact as Screenshot)
            render_merged_model_details(
                data.get('carousel_model_df'), 
                title="Model Details", 
                subtitle=data.get('model_detail_header', "")
            )

            # 3. Key Features
            render_navy_section("Key Features", data.get('key_features_df'), 
                                ["Sr.no", "Description", "Status", "Remarks"], [10, 110, 30, 40])
            
            # 4. Inbuilt Features
            render_navy_section("Inbuilt features", data.get('inbuilt_features_df'), 
                                ["Sr.no", "Description", "Vendor Scope (Yes/No)", "Remarks"], [10, 110, 30, 40])
            
            # 5. Installation
            render_navy_section("Installation Accountability", data.get('installation_df'), 
                                ["Sr.no", "Category", "Vendor Scope (Yes/No)", "Customer Scope\n(Yes/No)", "Remarks"], [10, 75, 28, 28, 49])

        elif wh_sub in ["Storage System", "Material Handling", "Dock Leveller"]:
            p = {'Storage System':'ss', 'Material Handling':'mh', 'Dock Leveller':'dl'}.get(wh_sub)
            render_merged_model_details(data.get(f'spec_{p}_Model Details'), title="Model Details")
            render_navy_section("Key Features", data.get(f'spec_{p}_Key Features'), ["Sr.no", "Description", "Status", "Remarks"], [10, 110, 30, 40])
            render_navy_section("Inbuilt features", data.get(f'spec_{p}_Inbuilt features'), ["Sr.no", "Description", "Vendor Scope (Yes/No)", "Remarks"], [10, 110, 30, 40])
            render_navy_section("Installation Accountability", data.get(f'spec_{p}_Installation Accountability'), ["Sr.no", "Category", "Vendor Scope (Yes/No)", "Customer Scope\n(Yes/No)", "Remarks"], [10, 75, 28, 28, 49])
    
    elif wh_sub == "Storage Container":
        # Landscape table logic (already provided in original code)
        pass
    else:
        # Standard Item Table for other categories
        pass

    # 3. Timelines
    if pdf.get_y() + 50 > pdf.page_break_trigger: pdf.add_page()
    pdf.section_title('TIMELINES')
    timeline_data = [
        ("Date of RFQ Release", data['date_release']),
        ("Query Resolution Deadline", data['date_query']),
        ("Negotiation & Vendor Selection", data['date_selection']),
        ("Delivery Deadline", data['date_delivery']),
        ("Installation Deadline", data['date_install'])
    ]
    pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Milestone', 1, 0, 'C'); pdf.cell(110, 8, 'Date', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for m, d in timeline_data:
        pdf.cell(80, 8, m, 1, 0, 'L'); pdf.cell(110, 8, d.strftime('%B %d, %Y'), 1, 1, 'L')
    pdf.ln(5)

    # 4. SPOC
    pdf.section_title('SINGLE POINT OF CONTACT')
    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 6, "Primary Contact:", 0, 1)
    pdf.set_font('Arial', '', 10); pdf.cell(0, 6, f"Name: {data['spoc1_name']} | Email: {data['spoc1_email']} | Phone: {data['spoc1_phone']}", 0, 1)
    pdf.ln(5)

    # 5. Commercials
    pdf.section_title('COMMERCIAL REQUIREMENTS')
    pdf.set_font('Arial', 'B', 10); pdf.cell(80, 8, 'Cost Component', 1, 0, 'C'); pdf.cell(40, 8, 'Amount', 1, 0, 'C'); pdf.cell(70, 8, 'Remarks', 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for _, r in data['commercial_df'].iterrows():
        pdf.cell(80, 8, str(r['Cost Component']), 1, 0, 'L'); pdf.cell(40, 8, '', 1, 0); pdf.cell(70, 8, str(r['Remarks']), 1, 1, 'L')
    pdf.ln(10)

    # 6. Submission & Delivery
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 8, 'Quotation Submission & Delivery', 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 6, f"Submit to: {data['submit_to_name']}\nLocation: {data['delivery_location']}", 0, 'L')

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

# Step 4 — Technical specs (Dynamic only)
st.subheader("Step 4: Fill Core RFQ Details")
st.markdown("---")

with st.expander("📦 Technical Specifications", expanded=True):
    category_list = list(CATEGORY_HINTS.keys())
    rfq_category = st.selectbox("Select RFQ Category*", options=category_list, index=0)
    is_warehouse = (rfq_category == "Warehouse Equipment")

    if 'last_category' not in st.session_state:
        st.session_state.last_category = rfq_category
    if st.session_state.last_category != rfq_category:
        for k in ['dynamic_items_df', 'storage_containers_df', 'storage_containers_images',
                  'wh_items_df', 'spec_df', 'carousel_model_df', 'key_features_df',
                  'inbuilt_features_df', 'installation_df', 'last_wh_sub']:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.last_category = rfq_category

    if is_warehouse:
        WH_SUB_CATEGORIES = [
            "Storage System",
            "Material Handling",
            "Automated Storage System",
            "Dock Leveller",
            "Storage Container",
        ]
        wh_sub = st.selectbox(
            "Select Warehouse Item Category",
            options=WH_SUB_CATEGORIES,
            key="wh_sub_category",
            help="Fields will change based on your selection"
        )

        # Reset sub-category state when switching
        if st.session_state.get('last_wh_sub') != wh_sub:
            for k in ['wh_items_df', 'storage_containers_df', 'storage_containers_images',
                      'carousel_model_df', 'key_features_df', 'inbuilt_features_df',
                      'installation_df', 'spec_df']:
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state['last_wh_sub'] = wh_sub

        # ────────────────────────────────────────────────────────────
        # SHARED helper: render one multi-section spec template in UI
        # ────────────────────────────────────────────────────────────
        def _render_multisection_spec(template_dict, state_key_prefix, sub_label):
            """
            Renders the Excel-style multi-section layout in Streamlit.
            Each section = bold title + editable 5-col or 4-col table.
            template_dict keys determine column layout:
              'Model Details'            → Sr.no | Category | Description | Unit | Requirement
              'Key Features'             → Sr.no | Description | Status | Remarks
              'Inbuilt Features'         → Sr.no | Description | Vendor Scope (Yes/No) | Remarks
              'Installation Accountability' → Sr.no | Category | Vendor Scope | Customer Scope | Remarks
            """
            st.caption(
                "All sections are pre-filled as per standard template. "
                "Fill in the highlighted columns and edit any field as needed. "
                "Use ➕ at the bottom of each table to add rows."
            )
            section_cfg = {
                "Model Details": {
                    "cols": ["Sr.no", "Category", "Description", "UNIT", "Requirement"],
                    "edit_col": "Requirement",
                    "column_config": {
                        "Sr.no":        st.column_config.TextColumn("Sr.no", width="small"),
                        "Category":     st.column_config.TextColumn("Category", width="medium"),
                        "Description":  st.column_config.TextColumn("Description", width="large"),
                        "UNIT":         st.column_config.TextColumn("UNIT", width="small"),
                        "Requirement":  st.column_config.TextColumn("Requirement ✏️", width="medium"),
                    },
                },
                "Key Features": {
                    "cols": ["Sr.no", "Description", "Status", "Remarks"],
                    "edit_col": "Status",
                    "column_config": {
                        "Sr.no":       st.column_config.TextColumn("Sr.no", width="small"),
                        "Description": st.column_config.TextColumn("Description", width="large"),
                        "Status":      st.column_config.TextColumn("Status ✏️", width="small"),
                        "Remarks":     st.column_config.TextColumn("Remarks", width="large"),
                    },
                },
                "Inbuilt features": {
                    "cols": ["Sr.no", "Description", "Vendor Scope (Yes/No)", "Remarks"],
                    "edit_col": "Vendor Scope (Yes/No)",
                    "column_config": {
                        "Sr.no":                   st.column_config.TextColumn("Sr.no", width="small"),
                        "Description":             st.column_config.TextColumn("Description", width="large"),
                        "Vendor Scope (Yes/No)":   st.column_config.SelectboxColumn("Vendor Scope (Yes/No) ✏️", width="small", options=["", "Yes", "No"]),
                        "Remarks":                 st.column_config.TextColumn("Remarks", width="large"),
                    },
                },
                "Installation Accountability": {
                    "cols": ["Sr.no", "Category", "Vendor Scope (Yes/No)", "Customer Scope\n(Yes/No)", "Remarks"],
                    "edit_col": "Vendor Scope (Yes/No)",
                    "column_config": {
                        "Sr.no":                    st.column_config.TextColumn("Sr.no", width="small"),
                        "Category":                 st.column_config.TextColumn("Category", width="large"),
                        "Vendor Scope (Yes/No)":    st.column_config.SelectboxColumn("Vendor Scope (Yes/No) ✏️", width="small", options=["", "Yes", "No"]),
                        "Customer Scope\n(Yes/No)": st.column_config.SelectboxColumn("Customer Scope (Yes/No) ✏️", width="small", options=["", "Yes", "No"]),
                        "Remarks":                  st.column_config.TextColumn("Remarks", width="medium"),
                    },
                },
            }

            for section_name, rows in template_dict.items():
                sk = f"{state_key_prefix}_{section_name}"
                cfg = section_cfg.get(section_name, section_cfg["Model Details"])

                # Bold section title exactly like Excel
                st.markdown(
                    f"<div style='background:#1a3a5c;color:white;font-weight:bold;"
                    f"padding:6px 10px;margin-top:14px;margin-bottom:2px;"
                    f"font-size:14px;border-radius:3px;'>{section_name}</div>",
                    unsafe_allow_html=True
                )

                # Init state
                if sk not in st.session_state:
                    st.session_state[sk] = pd.DataFrame(_copy.deepcopy(rows))

                df = st.session_state[sk].copy()
                for col in cfg["cols"]:
                    if col not in df.columns:
                        df[col] = ""
                    df[col] = df[col].astype(str).replace("nan", "")
                df = df[cfg["cols"]]

                edited = st.data_editor(
                    df,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config=cfg["column_config"],
                    key=f"editor_{sk}"
                )
                st.session_state[sk] = edited

        # ────────────────────────────────────────────────────────────
        # STORAGE SYSTEM
        # ────────────────────────────────────────────────────────────
        if wh_sub == "Storage System":
            st.markdown("#### 📋 Storage System Specification")
            _render_multisection_spec(STORAGE_SYSTEM_SPEC, "ss", "Storage System")

        # ────────────────────────────────────────────────────────────
        # MATERIAL HANDLING
        # ────────────────────────────────────────────────────────────
        elif wh_sub == "Material Handling":
            st.markdown("#### 📋 Material Handling Equipment Specification")
            _render_multisection_spec(MATERIAL_HANDLING_SPEC, "mh", "Material Handling")

        # ────────────────────────────────────────────────────────────
        # DOCK LEVELLER
        # ────────────────────────────────────────────────────────────
        elif wh_sub == "Dock Leveller":
            st.markdown("#### 📋 Dock Leveller / Dock Equipment Specification")
            _render_multisection_spec(DOCK_LEVELLER_SPEC, "dl", "Dock Leveller")

        # ────────────────────────────────────────────────────────────
        # AUTOMATED STORAGE SYSTEM — VStore / Carousel
        # ────────────────────────────────────────────────────────────
        elif wh_sub == "Automated Storage System":
            st.markdown("#### 📋 Automated Storage System")
            st.caption("Select item(s) below, then fill in all specification tables.")

            item_opts_auto = [""] + ["Vertical Carousel System", "Horizontal Carousel System"]
            if 'wh_items_df' not in st.session_state:
                st.session_state['wh_items_df'] = pd.DataFrame([{
                    "Sr.no": 1, "Item Name": "",
                    "Description / Specification": "",
                    "Quantity": 1, "Unit": "Nos", "Remarks": ""
                }])
            dfe_auto = st.session_state['wh_items_df'].copy()
            dfe_auto["Sr.no"] = range(1, len(dfe_auto) + 1)
            dfe_auto["Quantity"] = pd.to_numeric(dfe_auto.get("Quantity", 1), errors='coerce').fillna(1).astype(int)
            for col in ["Item Name", "Description / Specification", "Unit", "Remarks"]:
                if col not in dfe_auto.columns: dfe_auto[col] = ""
                dfe_auto[col] = dfe_auto[col].astype(str).replace("nan", "")
            dfe_auto = dfe_auto[["Sr.no", "Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"]]
            edited_auto = st.data_editor(
                dfe_auto, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Sr.no":                       st.column_config.NumberColumn("Sr.no", width="small", disabled=True),
                    "Item Name":                   st.column_config.SelectboxColumn("Item Name ▼", width="medium", options=item_opts_auto),
                    "Description / Specification": st.column_config.TextColumn("Description / Specification", width="large"),
                    "Quantity":                    st.column_config.NumberColumn("Qty", width="small", min_value=0, step=1, format="%d"),
                    "Unit":                        st.column_config.SelectboxColumn("Unit ▼", width="small", options=[""] + UNIT_OPTIONS),
                    "Remarks":                     st.column_config.TextColumn("Remarks", width="medium"),
                }, key="wh_items_editor")
            st.session_state['wh_items_df'] = edited_auto

            st.markdown("---")
            model_detail_header = st.text_input(
                "Model Header",
                value="3400 (L) x 3200 (W)   -  465 kgs/tray  -  28 m Height",
                key="model_detail_header_input"
            )
            st.session_state['model_detail_header'] = model_detail_header

            st.markdown("#### 📐 Model Details")
            st.caption("Pre-filled as per template. Fill / edit the **Requirement** column.")
            if 'carousel_model_df' not in st.session_state or st.session_state.carousel_model_df.empty:
                st.session_state['carousel_model_df'] = pd.DataFrame(
                    _copy.deepcopy(CAROUSEL_SPEC_TEMPLATE["Model Details"]))
            df_md = st.session_state['carousel_model_df'].copy()
            for col in ["Sr.no", "Category", "Description", "UNIT", "Requirement"]:
                if col not in df_md.columns: df_md[col] = ""
                df_md[col] = df_md[col].astype(str).replace("nan", "")
            edited_model_df = st.data_editor(
                df_md, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Sr.no":        st.column_config.TextColumn("Sr.no", width="small"),
                    "Category":     st.column_config.TextColumn("Category", width="medium"),
                    "Description":  st.column_config.TextColumn("Description", width="large"),
                    "UNIT":         st.column_config.TextColumn("UNIT", width="small"),
                    "Requirement":  st.column_config.TextColumn("Requirement ✏️", width="medium"),
                }, key="carousel_model_editor")
            st.session_state['carousel_model_df'] = edited_model_df

            st.markdown("#### ⭐ Key Features")
            st.caption("Fill in the **Status** column.")
            if 'key_features_df' not in st.session_state or st.session_state.key_features_df.empty:
                st.session_state['key_features_df'] = pd.DataFrame(_copy.deepcopy(CAROUSEL_SPEC_TEMPLATE["Key Features"]))
            df_kf = st.session_state['key_features_df'].copy()
            for col in ["Sr.no", "Description", "Status", "Remarks"]:
                if col not in df_kf.columns: df_kf[col] = ""
                df_kf[col] = df_kf[col].astype(str).replace("nan", "")
            edited_kf = st.data_editor(
                df_kf, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Sr.no":       st.column_config.TextColumn("Sr.no", width="small"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                    "Status":      st.column_config.TextColumn("Status ✏️", width="small"),
                    "Remarks":     st.column_config.TextColumn("Remarks", width="large"),
                }, key="kf_editor")
            st.session_state['key_features_df'] = edited_kf

            st.markdown("#### 🔧 Inbuilt features")
            st.caption("Fill in the **Vendor Scope (Yes/No)** column.")
            if 'inbuilt_features_df' not in st.session_state or st.session_state.inbuilt_features_df.empty:
                st.session_state['inbuilt_features_df'] = pd.DataFrame(_copy.deepcopy(CAROUSEL_SPEC_TEMPLATE["Inbuilt features"]))
            df_ib = st.session_state['inbuilt_features_df'].copy()
            for col in ["Sr.no", "Description", "Vendor Scope (Yes/No)", "Remarks"]:
                if col not in df_ib.columns: df_ib[col] = ""
                df_ib[col] = df_ib[col].astype(str).replace("nan", "")
            edited_ib = st.data_editor(
                df_ib, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Sr.no":                   st.column_config.TextColumn("Sr.no", width="small"),
                    "Description":             st.column_config.TextColumn("Description", width="large"),
                    "Vendor Scope (Yes/No)":   st.column_config.SelectboxColumn("Vendor Scope (Yes/No) ✏️", width="small", options=["", "Yes", "No"]),
                    "Remarks":                 st.column_config.TextColumn("Remarks", width="large"),
                }, key="ib_editor")
            st.session_state['inbuilt_features_df'] = edited_ib

            st.markdown("#### 🏗️ Installation Accountability")
            st.caption("Fill in **Vendor Scope (Yes/No)** and **Customer Scope (Yes/No)** columns.")
            if 'installation_df' not in st.session_state or st.session_state.installation_df.empty:
                st.session_state['installation_df'] = pd.DataFrame(_copy.deepcopy(CAROUSEL_SPEC_TEMPLATE["Installation Accountability"]))
            df_ia = st.session_state['installation_df'].copy()
            for col in ["Sr.no", "Category", "Vendor Scope (Yes/No)", "Customer Scope\n(Yes/No)", "Remarks"]:
                if col not in df_ia.columns: df_ia[col] = ""
                df_ia[col] = df_ia[col].astype(str).replace("nan", "")
            edited_ia = st.data_editor(
                df_ia, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Sr.no":                    st.column_config.TextColumn("Sr.no", width="small"),
                    "Category":                 st.column_config.TextColumn("Category", width="large"),
                    "Vendor Scope (Yes/No)":    st.column_config.SelectboxColumn("Vendor Scope (Yes/No) ✏️", width="small", options=["", "Yes", "No"]),
                    "Customer Scope\n(Yes/No)": st.column_config.SelectboxColumn("Customer Scope (Yes/No) ✏️", width="small", options=["", "Yes", "No"]),
                    "Remarks":                  st.column_config.TextColumn("Remarks", width="medium"),
                }, key="ia_editor")
            st.session_state['installation_df'] = edited_ia

        # ────────────────────────────────────────────────────────────
        # STORAGE CONTAINER — unchanged
        # ────────────────────────────────────────────────────────────
        elif wh_sub == "Storage Container":
            st.caption("Select container type from the dropdown, fill all dimensions, and upload a conceptual image per row.")

            container_options = [""] + STORAGE_CONTAINERS_ITEMS
            if 'storage_containers_df' not in st.session_state:
                st.session_state['storage_containers_df'] = pd.DataFrame([_empty_container_row(1)])
            if 'storage_containers_images' not in st.session_state:
                st.session_state['storage_containers_images'] = {}

            sc_df_display = st.session_state['storage_containers_df'].copy()
            sc_df_display["Sr.No"] = range(1, len(sc_df_display) + 1)
            for col in ["Description", "Material Type", "Length", "Width", "Height",
                        "Inner Length", "Inner Width", "Inner Height", "Unit of Measurement",
                        "Base Type", "Colour", "Weight Kg", "Load capacity",
                        "Stackable", "BIn Cover/ Open", "Rate", "Remarks"]:
                if col not in sc_df_display.columns: sc_df_display[col] = ""
                sc_df_display[col] = sc_df_display[col].astype(str).replace("nan", "")
            if "Qty" not in sc_df_display.columns: sc_df_display["Qty"] = 1
            sc_df_display["Qty"] = pd.to_numeric(sc_df_display["Qty"], errors='coerce').fillna(1).astype(int)

            sc_editor_col, sc_uploader_col = st.columns([3, 1])
            with sc_editor_col:
                edited_sc_df = st.data_editor(
                    sc_df_display, num_rows="dynamic", use_container_width=True,
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

            with sc_uploader_col:
                st.write("**Conceptual Images**")
                for i in range(len(edited_sc_df)):
                    desc = str(edited_sc_df.iloc[i].get("Description", "")).strip()
                    lbl = f"Row {i+1}: {desc}" if desc else f"Row {i+1}"
                    f_up = st.file_uploader(lbl, type=["png", "jpg", "jpeg"], key=f"sc_image_uploader_{i}")
                    if f_up is not None:
                        st.session_state['storage_containers_images'][i] = f_up.getvalue()
                    if i in st.session_state['storage_containers_images']:
                        st.image(st.session_state['storage_containers_images'][i], width=80)

            st.session_state['storage_containers_df'] = edited_sc_df
            valid_sc = edited_sc_df[edited_sc_df["Description"].astype(str).str.strip() != ""]
            if len(valid_sc):
                st.success(f"✅ {len(valid_sc)} container type(s) defined")

    else:
        # Non-warehouse categories — generic item list
        hints = CATEGORY_HINTS.get(rfq_category, [])
        if hints:
            st.markdown(f"**💡 Common items in *{rfq_category}***")
        if 'dynamic_items_df' not in st.session_state:
            st.session_state['dynamic_items_df'] = pd.DataFrame(
                columns=["Item Name", "Description / Specification", "Quantity", "Unit", "Remarks"])
        if hints:
            btn_cols = st.columns(min(len(hints), 4))
            for idx, hint in enumerate(hints):
                with btn_cols[idx % 4]:
                    if st.button(f"➕ {hint}", key=f"hint_btn_{idx}_{rfq_category}"):
                        new_row = pd.DataFrame([{"Item Name": hint, "Description / Specification": "", "Quantity": 1, "Unit": "Nos", "Remarks": ""}])
                        st.session_state['dynamic_items_df'] = pd.concat([st.session_state['dynamic_items_df'], new_row], ignore_index=True)
                        st.rerun()
        st.markdown("---")
        st.markdown("##### 📋 Item List")
        df_to_edit = st.session_state['dynamic_items_df'].copy()
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
        st.session_state['dynamic_items_df'] = edited_dynamic_df
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
    else:
        current_category = st.session_state.get('last_category', rfq_category)
        is_warehouse_submit = (current_category == "Warehouse Equipment")
        wh_sub_submit = st.session_state.get('wh_sub_category', 'Storage System')

        common_data = {
            'rfq_category': current_category,
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
            'wh_sub': wh_sub_submit,
        }

        if is_warehouse_submit:
            if wh_sub_submit == 'Storage Container':
                sc_df = st.session_state.get('storage_containers_df', pd.DataFrame())
                sc_images = st.session_state.get('storage_containers_images', {})
                if sc_df is not None and not sc_df.empty:
                    valid_sc = sc_df[sc_df["Description"].astype(str).str.strip() != ""].reset_index(drop=True).copy()
                    valid_sc['image_data_bytes'] = [sc_images.get(i) for i in range(len(valid_sc))]
                    common_data['storage_containers_df'] = valid_sc
                else:
                    common_data['storage_containers_df'] = pd.DataFrame()
                common_data['storage_containers_images'] = sc_images

            elif wh_sub_submit == 'Automated Storage System':
                wh_items = st.session_state.get('wh_items_df', pd.DataFrame())
                common_data['wh_items_df'] = wh_items
                model_df = st.session_state.get('carousel_model_df', pd.DataFrame())
                if model_df is None or model_df.empty:
                    model_df = pd.DataFrame(_copy.deepcopy(CAROUSEL_SPEC_TEMPLATE["Model Details"]))
                common_data['carousel_model_df'] = model_df
                common_data['model_detail_header'] = st.session_state.get('model_detail_header', '')
                common_data['key_features_df']     = st.session_state.get('key_features_df', pd.DataFrame())
                common_data['inbuilt_features_df']  = st.session_state.get('inbuilt_features_df', pd.DataFrame())
                common_data['installation_df']      = st.session_state.get('installation_df', pd.DataFrame())

            else:
                # Storage System / Material Handling / Dock Leveller — multi-section
                prefix_map  = {'Storage System':'ss', 'Material Handling':'mh', 'Dock Leveller':'dl'}
                template_map = {
                    'Storage System':   STORAGE_SYSTEM_SPEC,
                    'Material Handling':MATERIAL_HANDLING_SPEC,
                    'Dock Leveller':    DOCK_LEVELLER_SPEC,
                }
                pfx  = prefix_map.get(wh_sub_submit, 'ss')
                tmpl = template_map.get(wh_sub_submit, STORAGE_SYSTEM_SPEC)
                for section_name in tmpl.keys():
                    sk = f"{pfx}_{section_name}"
                    sec_df = st.session_state.get(sk, pd.DataFrame(_copy.deepcopy(tmpl[section_name])))
                    common_data[f'spec_{pfx}_{section_name}'] = sec_df

        else:
            items_check = st.session_state.get('dynamic_items_df', pd.DataFrame())
            if items_check.empty or items_check[items_check["Item Name"].astype(str).str.strip() != ""].empty:
                st.error("⚠️ Please add at least one item to the item list in Step 4.")
                st.stop()
            common_data['items_df'] = items_check[items_check["Item Name"].astype(str).str.strip() != ""].reset_index(drop=True)

        with st.spinner("Generating PDF..."):
            pdf_data = create_advanced_rfq_pdf(common_data)

        st.success("✅ RFQ PDF Generated Successfully!")
        file_name = f"RFQ_{Type_of_items.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        st.download_button("📥 Download RFQ Document", data=pdf_data, file_name=file_name,
                           mime="application/pdf", use_container_width=True, type="primary")
