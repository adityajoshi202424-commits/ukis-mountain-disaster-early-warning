"""
Generate Clean, Plain-Language Word Document (.docx) for Undergraduate Idea Proposal:
"Flash Flood Early Warning, Rescuer Assistance, and Safe Evacuation Routing System"

Rules:
- NO fake data, NO fabricated benchmark readings (no 248k edges, no 194ms, no 99.4%, no 6 islands).
- NO fake dilemmas or dramatic buzzwords.
- Straightforward presentation of:
  1. The issues we are fixing
  2. How the system works & its implementation
  3. How it is new (comparison table with existing systems)
- NO student or supervisor names (generic placeholders only).
- Formatted tables with colored header rows and alternating row shading.
- Callout highlight boxes with clean left accent borders.
- Running header and footer with dynamic Word page numbers (Page X of Y).
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# ---------------------------------------------------------------------------
# Styling Constants (Professional Engineering Palette)
# ---------------------------------------------------------------------------
HEX_PRIMARY = "1E3A8A"      # Deep Navy Blue
HEX_SECONDARY = "2563EB"    # Vibrant Royal Blue
HEX_TEXT_DARK = "0F172A"    # Slate 900
HEX_TEXT_MUTED = "475569"   # Slate 600
HEX_BORDER = "CBD5E1"       # Light Slate Border
HEX_BG_LIGHT = "F8FAFC"     # Off-white / Cool Grey Background
HEX_CALLOUT_BG = "F1F5F9"   # Slate 100 Callout Background
HEX_ALT_ROW = "F8FAFC"      # Alternating Table Row

RGB_PRIMARY = RGBColor(30, 58, 138)
RGB_SECONDARY = RGBColor(37, 99, 235)
RGB_TEXT_DARK = RGBColor(15, 23, 42)
RGB_TEXT_BODY = RGBColor(51, 65, 85)
RGB_TEXT_MUTED = RGBColor(100, 116, 139)


def set_cell_background(cell, hex_color):
    """Sets the background fill color of a table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_padding(cell, top=80, bottom=80, left=120, right=120):
    """Sets internal padding (margins) for a table cell in dxa (1 pt = 20 dxa)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)


def set_cell_border(cell, top=None, bottom=None, left=None, right=None):
    """Sets custom borders on an individual cell."""
    tcPr = cell._element.get_or_add_tcPr()
    borders = ['<w:tcBorders %s>' % nsdecls('w')]
    for side, border_spec in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        if border_spec:
            val, sz, space, color = border_spec
            borders.append(f'<w:{side} w:val="{val}" w:sz="{sz}" w:space="{space}" w:color="{color}"/>')
        else:
            borders.append(f'<w:{side} w:val="none"/>')
    borders.append('</w:tcBorders>')
    tcBorders = parse_xml(''.join(borders))
    tcPr.append(tcBorders)


def set_table_borders(table, color="CBD5E1", sz="4"):
    """Applies subtle border lines across an entire table."""
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            </w:tblBorders>
        ''')
        tblPr[0].append(borders)


def add_callout(doc, text_content, title=""):
    """Adds a stylish callout box with a prominent left accent border."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.8)
    
    cell = tbl.cell(0, 0)
    set_cell_background(cell, HEX_CALLOUT_BG)
    set_cell_padding(cell, top=120, bottom=120, left=180, right=140)
    set_cell_border(cell, left=('single', '24', '0', HEX_SECONDARY))
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    if title:
        run_title = p.add_run(f"{title}\n")
        run_title.font.name = 'Calibri'
        run_title.font.size = Pt(9.5)
        run_title.font.bold = True
        run_title.font.color.rgb = RGB_PRIMARY
    
    run_body = p.add_run(text_content)
    run_body.font.name = 'Calibri'
    run_body.font.size = Pt(9.0)
    run_body.font.color.rgb = RGB_TEXT_BODY
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)


def add_heading_1(doc, text):
    """Adds a primary numbered section heading."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(13)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGB_PRIMARY
    return p


def add_heading_2(doc, text):
    """Adds a subsection heading."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGB_TEXT_DARK
    return p


def add_body_p(doc, text, bold_prefix="", italic=False):
    """Adds standard formatted body text."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.font.name = 'Calibri'
        rb.font.size = Pt(10)
        rb.font.bold = True
        rb.font.color.rgb = RGB_TEXT_DARK
        
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(10)
    run.font.italic = italic
    run.font.color.rgb = RGB_TEXT_BODY
    return p


def add_bullet_item(doc, bold_lead, text):
    """Adds a bullet point with bold lead-in."""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    
    r_lead = p.add_run(bold_lead + " ")
    r_lead.font.name = 'Calibri'
    r_lead.font.size = Pt(9.5)
    r_lead.font.bold = True
    r_lead.font.color.rgb = RGB_TEXT_DARK
    
    r_text = p.add_run(text)
    r_text.font.name = 'Calibri'
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = RGB_TEXT_BODY
    return p


def build_docx(filename: str):
    doc = Document()
    
    # -----------------------------------------------------------------------
    # Page Setup: Standard Margins (0.8 in)
    # -----------------------------------------------------------------------
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        section.different_first_page_header_footer = True
        
        # Running Header (Pages > 1)
        hdr = section.header
        hp = hdr.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        hp.paragraph_format.space_after = Pt(2)
        
        hr1 = hp.add_run("MAJOR PROJECT IDEA PROPOSAL: FLASH FLOOD EARLY WARNING & RESCUE ROUTING")
        hr1.font.name = 'Calibri'
        hr1.font.size = Pt(8.5)
        hr1.font.bold = True
        hr1.font.color.rgb = RGB_PRIMARY
        
        hp.paragraph_format.tab_stops.add_tab_stop(Inches(6.9))
        hr2 = hp.add_run("\tB.TECH CSE (ACADEMIC YEAR 2026-2027)")
        hr2.font.name = 'Calibri'
        hr2.font.size = Pt(8.0)
        hr2.font.color.rgb = RGB_TEXT_MUTED
        
        # Running Footer (All Pages with Dynamic Page Numbering)
        ftr = section.footer
        fp = ftr.paragraphs[0]
        fp.paragraph_format.space_before = Pt(4)
        fp.paragraph_format.tab_stops.add_tab_stop(Inches(6.9))
        
        fr1 = fp.add_run("Dept. of Computer Science & Engineering | Project Idea Proposal & Synopsis")
        fr1.font.name = 'Calibri'
        fr1.font.size = Pt(8.0)
        fr1.font.color.rgb = RGB_TEXT_MUTED
        
        fr2 = fp.add_run("\tPage ")
        fr2.font.name = 'Calibri'
        fr2.font.size = Pt(8.0)
        fr2.font.color.rgb = RGB_PRIMARY
        
        fld_page = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>')
        fr2._r.append(fld_page)
        
        fr3 = fp.add_run(" of ")
        fr3.font.name = 'Calibri'
        fr3.font.size = Pt(8.0)
        fr3.font.color.rgb = RGB_PRIMARY
        
        fld_numpages = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="NUMPAGES"/>')
        fr3._r.append(fld_numpages)

    # -----------------------------------------------------------------------
    # Document Top Banner & Header
    # -----------------------------------------------------------------------
    p_banner = doc.add_paragraph()
    p_banner.paragraph_format.space_before = Pt(0)
    p_banner.paragraph_format.space_after = Pt(2)
    
    r_ban1 = p_banner.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n")
    r_ban1.font.name = 'Calibri'
    r_ban1.font.size = Pt(9.5)
    r_ban1.font.bold = True
    r_ban1.font.color.rgb = RGB_PRIMARY
    
    r_ban2 = p_banner.add_run("Undergraduate Major Project Idea Proposal • Academic Session 2026-2027")
    r_ban2.font.name = 'Calibri'
    r_ban2.font.size = Pt(8.5)
    r_ban2.font.color.rgb = RGB_TEXT_MUTED
    
    # Document Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(2)
    p_title.paragraph_format.line_spacing = 1.1
    r_t = p_title.add_run("Flash Flood Early Warning, Rescuer Assistance, and Safe Evacuation Routing System")
    r_t.font.name = 'Calibri'
    r_t.font.size = Pt(17)
    r_t.font.bold = True
    r_t.font.color.rgb = RGB_TEXT_DARK
    
    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(8)
    r_s = p_sub.add_run("A Practical Engineering Proposal for Sensor Failover, Street-Level Inundation Estimation, and Depth-Aware Evacuation Navigation")
    r_s.font.name = 'Calibri'
    r_s.font.size = Pt(10.0)
    r_s.font.bold = True
    r_s.font.color.rgb = RGB_SECONDARY

    # Metadata Box (Generic Placeholders - ZERO Student Names)
    meta_tbl = doc.add_table(rows=4, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_tbl.autofit = False
    set_table_borders(meta_tbl, color=HEX_BORDER, sz="4")
    
    col_widths = [Inches(1.8), Inches(5.0)]
    meta_entries = [
        ("Student Investigators:", "[Undergraduate Project Student Group / Candidate Names & Roll Numbers]"),
        ("Project Supervisor(s):", "[Faculty Supervisor / Project Guide, Dept. of Computer Science & Engineering]"),
        ("Project Category:", "B.Tech Major Project Synopsis & Research Idea Proposal"),
        ("Target Study Region:", "Alaknanda & Bhagirathi River Basins (Focusing on Chamoli, Rudraprayag & High-Risk Mountain Districts, Uttarakhand)")
    ]
    
    for row_idx, (label, val) in enumerate(meta_entries):
        row = meta_tbl.rows[row_idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        
        cell_lbl.width, cell_val.width = col_widths[0], col_widths[1]
        set_cell_background(cell_lbl, "F1F5F9")
        set_cell_background(cell_val, HEX_BG_LIGHT)
        set_cell_padding(cell_lbl, top=60, bottom=60, left=100, right=100)
        set_cell_padding(cell_val, top=60, bottom=60, left=100, right=100)
        
        p_l = cell_lbl.paragraphs[0]
        p_l.paragraph_format.space_before = Pt(0)
        p_l.paragraph_format.space_after = Pt(0)
        r_l = p_l.add_run(label)
        r_l.font.name = 'Calibri'
        r_l.font.size = Pt(8.5)
        r_l.font.bold = True
        r_l.font.color.rgb = RGB_PRIMARY
        
        p_v = cell_val.paragraphs[0]
        p_v.paragraph_format.space_before = Pt(0)
        p_v.paragraph_format.space_after = Pt(0)
        r_v = p_v.add_run(val)
        r_v.font.name = 'Calibri'
        r_v.font.size = Pt(8.5)
        r_v.font.color.rgb = RGB_TEXT_DARK
        
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -----------------------------------------------------------------------
    # Section 1: Introduction & Project Objective
    # -----------------------------------------------------------------------
    add_heading_1(doc, "1. Introduction & Project Objective")
    add_body_p(
        doc,
        "During the monsoon season, sudden intense cloudbursts and glacial lake activity in the high Himalayan tracts of India cause mountain torrents "
        "to surge rapidly. In steep mountain regions like Uttarakhand, flash floods and debris flows raise water levels over very short periods, creating severe challenges for "
        "communities living near riverbanks and for municipal and state disaster agencies. The objective of this project is to develop an automated, practical "
        "software system that predicts street-level flood depths in advance, assists emergency rescue personnel (NDRF and SDRF) in positioning assets "
        "before access corridors submerge, and guides citizens along safe, dry routes to designated government relief shelters."
    )
    add_body_p(
        doc,
        "Rather than focusing on theoretical hydrodynamics alone, this project tackles the direct operational issues that cause disaster response to fail on the ground: "
        "loss of river gauge data during severe weather, general weather advisories that lack street-level depth details, standard GPS map apps that guide drivers "
        "into flooded roads, and reactive rescue deployments that arrive after road access is already cut off."
    )

    # -----------------------------------------------------------------------
    # Section 2: The Operational Issues We Are Fixing
    # -----------------------------------------------------------------------
    add_heading_1(doc, "2. The Operational Issues We Are Fixing")
    
    add_heading_2(doc, "Issue 1: Physical River Gauges Fail During Severe Storms")
    add_body_p(
        doc,
        "Automated river staff gauges and ultrasonic level sensors installed on riverbanks are exposed to strong currents, uprooted trees, floating logs, "
        "and heavy silt. These forces frequently damage or submerge the sensors. At the same time, high winds cause local power blackouts and cellular tower "
        "failures. As a result, ground sensor telemetry frequently stops transmitting during extreme storms. When physical sensors go offline, disaster "
        "managers lose real-time visibility into river levels at the exact time when water is rising fastest."
    )
    
    add_heading_2(doc, "Issue 2: Standard Navigation Apps Lack Flood Depth Information")
    add_body_p(
        doc,
        "Commercial navigation apps (such as Google Maps) are designed to find the shortest or fastest dry-weather route based on traffic speed. "
        "They have no information about road water depth. During a flood, these apps continue directing fleeing families along roads that cross low underpasses, "
        "culverts, and river dips. Moving water as shallow as 15 cm can wash away pedestrians, while 30 cm floats ordinary passenger cars and stalls engines, "
        "creating serious hazards for evacuees."
    )
    
    add_heading_2(doc, "Issue 3: Emergency Rescuers Are Dispatched After Access Roads Are Already Submerged")
    add_body_p(
        doc,
        "Emergency rescue teams are usually dispatched only after distress calls begin arriving. Many low-lying villages connect to regional highways via "
        "a single low-lying road. Once that access road is submerged under deep water, heavy rescue vehicles cannot enter, and launching motorized rescue boats "
        "through flooded trees and debris becomes slow and difficult. Rescue teams need advance notification to move boats and supplies into position before "
        "the access road is cut off."
    )

    # -----------------------------------------------------------------------
    # Section 3: System Architecture & Working Mechanism
    # -----------------------------------------------------------------------
    add_heading_1(doc, "3. System Architecture & Working Mechanism")
    add_body_p(
        doc,
        "The proposed system connects river sensor monitoring, automated satellite radar backup, road water depth calculation, and depth-aware navigation. "
        "The system operates across four coordinated stages:"
    )

    # Table 1: 4-Stage Operational Table
    arch_tbl = doc.add_table(rows=5, cols=3)
    arch_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    arch_tbl.autofit = False
    set_table_borders(arch_tbl, color=HEX_BORDER, sz="4")
    
    arch_col_widths = [Inches(1.5), Inches(2.7), Inches(2.6)]
    arch_headers = ["Operational Stage", "Core Function & Implementation", "Operational Outcome"]
    
    for col_idx, h_text in enumerate(arch_headers):
        cell = arch_tbl.rows[0].cells[col_idx]
        cell.width = arch_col_widths[col_idx]
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_padding(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = 'Calibri'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    arch_rows_data = [
        (
            "Stage 1: River Monitoring & Satellite Radar Backup",
            "Polls Central Water Commission (CWC) automated river gauges. Automatically switches to Copernicus Sentinel-3 SAR satellite radar altimetry if ground telemetry stops.",
            "Maintains water height tracking through dense monsoon rain clouds without relying on vulnerable ground poles."
        ),
        (
            "Stage 2: Downstream River Rise Estimation",
            "Calculates flood wave travel along river reaches from upstream stations to downstream settlements; checks satellite soil moisture to identify when saturated soil creates direct runoff.",
            "Provides roughly 2 or more hours of advance notice before the flood crest reaches downstream settlements."
        ),
        (
            "Stage 3: Street-by-Street Flood Depth Mapping",
            "Subtracts road elevation (from SRTM 30m Digital Elevation Model) from predicted river surface elevation across OpenStreetMap road centerlines.",
            "Determines estimated water depth on every road segment and identifies single-access roads at risk of cut-off."
        ),
        (
            "Stage 4: Multi-Channel Alerts & Depth-Aware Routing",
            "Dispatches SMS alerts in local languages; routes evacuees along dry roads to verified government shelters; generates advance staging alerts for rescue teams.",
            "Prevents families from entering flooded roads and enables rescue personnel to pre-stage boats before roads close."
        ),
    ]
    
    for row_idx, (col1, col2, col3) in enumerate(arch_rows_data, start=1):
        row = arch_tbl.rows[row_idx]
        bg_color = HEX_ALT_ROW if (row_idx % 2 == 1) else "FFFFFF"
        for c_idx, text in enumerate([col1, col2, col3]):
            cell = row.cells[c_idx]
            cell.width = arch_col_widths[c_idx]
            set_cell_background(cell, bg_color)
            set_cell_padding(cell, top=60, bottom=60, left=90, right=90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = 'Calibri'
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGB_PRIMARY
            else:
                r.font.color.rgb = RGB_TEXT_BODY
                
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Subsection 3.1: Satellite Radar Backup
    add_heading_2(doc, "3.1 Satellite Radar Backup: Maintaining Data When Ground Sensors Fail")
    add_body_p(
        doc,
        "Under normal conditions, the pipeline queries automated water level feeds from CWC river stations. The software performs continuous heartbeat "
        "checks: if telemetry from a ground gauge is missing for 15 minutes or reports corrupt values, the system flags the station as offline and activates "
        "backup satellite radar data."
    )
    add_callout(
        doc,
        "Working Principle of Satellite Radar: Standard optical satellite cameras cannot see through dense monsoon clouds and rain. "
        "In contrast, Synthetic Aperture Radar (SAR) altimetry on satellites like Sentinel-3 sends microwave radar pulses that pass directly through thick storm clouds "
        "and heavy downpours. The radar beam reflects off the water surface back to the satellite, allowing water surface elevation to be measured from orbit. "
        "Because the satellite is in space, it is completely unaffected by damaged ground poles, local power cuts, or fallen cellular towers.",
        title="Key Principle: Autonomous Satellite Radar Backup"
    )

    # Subsection 3.2: Downstream River Rise Estimation
    add_heading_2(doc, "3.2 Downstream River Rise Estimation")
    add_body_p(
        doc,
        "When heavy rainfall occurs in upper hill catchments, the surge moves downstream along the river channel. By tracking water elevation at upstream "
        "stations and estimating flood wave travel time along the river reach, the system estimates the expected river height and arrival time at downstream towns, "
        "providing a lead time of 2 or more hours."
    )
    add_body_p(
        doc,
        "Dry soil absorbs heavy rain, but after consecutive days of monsoon showers, soil becomes saturated. "
        "When soil moisture reaches saturation, additional rainfall cannot seep into the ground and turns immediately into rapid surface runoff. "
        "The system reads satellite soil moisture data (NASA GPM feeds) to identify when incoming rainfall will directly produce sharp surface surges.",
        bold_prefix="Soil Moisture Factor: "
    )

    # Subsection 3.3: Street Flood Depth Calculation
    add_heading_2(doc, "3.3 Street-Level Flood Depth Calculation")
    add_body_p(
        doc,
        "To calculate water depth on individual roads, the system compares the predicted river water level against the ground elevation of each road segment "
        "using a 30-meter Digital Elevation Model (SRTM DEM) and OpenStreetMap road vector centerlines. The estimated water depth determines road accessibility:"
    )

    # Table 2: Road Water Depth Risk Classification
    risk_tbl = doc.add_table(rows=5, cols=4)
    risk_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    risk_tbl.autofit = False
    set_table_borders(risk_tbl, color=HEX_BORDER, sz="4")
    
    risk_col_widths = [Inches(1.2), Inches(1.3), Inches(2.1), Inches(2.2)]
    risk_headers = ["Depth Category", "Estimated Depth", "Vehicle & Pedestrian Accessibility", "System Action"]
    
    for col_idx, h_text in enumerate(risk_headers):
        cell = risk_tbl.rows[0].cells[col_idx]
        cell.width = risk_col_widths[col_idx]
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_padding(cell, top=80, bottom=80, left=90, right=90)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = 'Calibri'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    risk_rows_data = [
        ("Tier 1: Dry", "< 5 cm", "All civilian vehicles and pedestrians permitted.", "Designated as open evacuation corridor."),
        ("Tier 2: Shallow Water", "5 cm - 15 cm", "Vehicles passable with care; unsafe for walking pedestrians.", "Excluded from walking evacuation routes."),
        ("Tier 3: Dangerous Depth", "15 cm - 80 cm", "Closed for civilian cars and walkers; high rescue trucks only.", "Reserved for NDRF/SDRF 4x4 rescue trucks."),
        ("Tier 4: Deep Flood", "> 80 cm", "Closed to all motor vehicles; rescue boats only.", "Marked impassable for all wheeled traffic."),
    ]
    
    for row_idx, row_vals in enumerate(risk_rows_data, start=1):
        row = risk_tbl.rows[row_idx]
        bg_color = HEX_ALT_ROW if (row_idx % 2 == 1) else "FFFFFF"
        for c_idx, text in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = risk_col_widths[c_idx]
            set_cell_background(cell, bg_color)
            set_cell_padding(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = 'Calibri'
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGB_PRIMARY
            else:
                r.font.color.rgb = RGB_TEXT_BODY
                
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Subsection 3.4: Emergency Rescuer Assistance
    add_heading_2(doc, "3.4 Emergency Rescuer Assistance: Cut-Off Alerts & High-Clearance Routes")
    add_body_p(
        doc,
        "A practical contribution of this project is assisting rescue agencies (such as NDRF and SDRF) before access is lost:"
    )
    add_bullet_item(
        doc,
        "Advance Single-Access Cut-Off Alerts:",
        "Many riverside villages connect to main highways through a single road. "
        "The system identifies villages whose sole connecting road is predicted to exceed 30 cm depth within the next 2 hours. "
        "Disaster coordinators receive an automated alert so they can dispatch boats, fuel, and medical personnel to high-ground staging areas near those "
        "villages before the road is submerged."
    )
    add_bullet_item(
        doc,
        "High-Clearance Rescue Truck Routes:",
        "Heavy emergency trucks (NDRF 4x4 vehicles) have high air intakes and can safely ford water up to 80 cm deep. "
        "The routing engine calculates dedicated paths allowing rescue convoys to traverse shallow flooded streets to reach stranded residents directly."
    )

    # Subsection 3.5: Civilian Evacuation Routing
    add_heading_2(doc, "3.5 Civilian Evacuation: Depth-Aware Safe Routing")
    add_body_p(
        doc,
        "The evacuation routing engine builds on OpenStreetMap road graphs using Dijkstra's algorithm with depth safety constraints:"
    )
    add_bullet_item(
        doc,
        "Pedestrian Ceiling (< 15 cm):",
        "Moving water as shallow as 15 cm can sweep away walking adults and children. "
        "For pedestrians, roads with 15 cm or more water are assigned infinite travel cost, guiding families strictly along dry ridges."
    )
    add_bullet_item(
        doc,
        "Vehicle Ceiling (< 30 cm):",
        "For cars and two-wheelers, the system blocks road dips and underpasses where water exceeds 30 cm, preventing vehicle stall."
    )
    add_bullet_item(
        doc,
        "Dynamic Road Blocking:",
        "As rainfall continues and water levels rise, flooded segments are dynamically closed on the graph, "
        "automatically rerouting evacuees along safe alternative roads."
    )

    # Subsection 3.6: Relief Shelters
    add_heading_2(doc, "3.6 Government Relief Centre Selection & Capacity Balancing")
    add_body_p(
        doc,
        "The system ensures families are guided only to shelters that are genuinely secure: (1) verifying that the shelter's plinth elevation is above the "
        "projected flood water level, (2) confirming that at least one incoming road connection remains dry (< 15 cm depth), and (3) monitoring shelter "
        "capacity so that once a relief center approaches its maximum occupancy, incoming evacuees are redirected to the next nearest open facility."
    )

    # -----------------------------------------------------------------------
    # Section 4: How This Idea Is New: Comparison with Existing Systems
    # -----------------------------------------------------------------------
    add_heading_1(doc, "4. How This Idea Is New: Comparison with Existing Systems")
    add_body_p(
        doc,
        "The table below summarizes the key operational differences between existing disaster management tools and our proposed engineering solution:"
    )

    # Comparison Table (Novelty)
    comp_tbl = doc.add_table(rows=6, cols=3)
    comp_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    comp_tbl.autofit = False
    set_table_borders(comp_tbl, color=HEX_BORDER, sz="4")
    
    comp_col_widths = [Inches(1.8), Inches(2.5), Inches(2.5)]
    comp_headers = ["Operational Dimension", "Current Standard Systems", "Proposed Solution (What Is New)"]
    
    for col_idx, h_text in enumerate(comp_headers):
        cell = comp_tbl.rows[0].cells[col_idx]
        cell.width = comp_col_widths[col_idx]
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_padding(cell, top=80, bottom=80, left=90, right=90)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = 'Calibri'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    comp_rows_data = [
        (
            "River Monitoring Continuity",
            "Relies solely on physical river staff gauges; stops transmitting if sensors are damaged or storm power fails.",
            "Automated failover to Copernicus Sentinel-3 SAR satellite radar altimetry; penetrates rain clouds without ground sensors."
        ),
        (
            "Warning Granularity",
            "Broad district-level or river basin warnings; does not specify which local streets will flood.",
            "Calculates estimated water depth street-by-street by intersecting DEM elevation with predicted water surface."
        ),
        (
            "Evacuation Navigation",
            "Commercial GPS apps (Google Maps) only consider dry traffic; frequently route cars into submerged roads and underpasses.",
            "Depth-constrained graph routing enforcing physical safety limits (<15 cm walking, <30 cm car) to avoid flooded roads."
        ),
        (
            "Rescuer Support",
            "Reactive deployment after distress calls; rescue teams often find access roads already submerged.",
            "Flags single-access villages facing road cut-off 2 hours in advance; provides special routes for 4x4 rescue trucks (<=80 cm)."
        ),
        (
            "Relief Shelter Allocation",
            "Static list of shelters without verifying road access or live capacity; evacuees may find facilities flooded or full.",
            "Dynamically verifies dry road access to shelters and redirects evacuees when a facility approaches full capacity."
        ),
    ]
    
    for row_idx, row_vals in enumerate(comp_rows_data, start=1):
        row = comp_tbl.rows[row_idx]
        bg_color = HEX_ALT_ROW if (row_idx % 2 == 1) else "FFFFFF"
        for c_idx, text in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = comp_col_widths[c_idx]
            set_cell_background(cell, bg_color)
            set_cell_padding(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = 'Calibri'
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGB_PRIMARY
            else:
                r.font.color.rgb = RGB_TEXT_BODY
                
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -----------------------------------------------------------------------
    # Section 5: Implementation Plan & Open-Source Technology Stack
    # -----------------------------------------------------------------------
    add_heading_1(doc, "5. Implementation Plan & Open-Source Technology Stack")
    add_body_p(
        doc,
        "The project is built entirely with open-source software libraries and publicly available government and satellite datasets, "
        "ensuring the framework can be deployed by district disaster agencies without licensing costs:"
    )

    # Tech Stack Table
    tech_tbl = doc.add_table(rows=5, cols=3)
    tech_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tech_tbl.autofit = False
    set_table_borders(tech_tbl, color=HEX_BORDER, sz="4")
    
    tech_col_widths = [Inches(1.8), Inches(2.6), Inches(2.4)]
    tech_headers = ["Subsystem", "Technologies & Datasets", "Purpose in Project"]
    
    for col_idx, h_text in enumerate(tech_headers):
        cell = tech_tbl.rows[0].cells[col_idx]
        cell.width = tech_col_widths[col_idx]
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_padding(cell, top=80, bottom=80, left=90, right=90)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = 'Calibri'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    tech_rows_data = [
        (
            "Sensor Ingestion & Backup",
            "Python, Pandas, Requests, Sentinel-3 SAR Altimetry API, NASA GPM IMERG rainfall feeds",
            "Automates sensor polling and triggers satellite backup when ground feeds stop."
        ),
        (
            "Hydrology & Inundation Core",
            "NumPy, SciPy, SRTM 30m Digital Elevation Model (DEM), CWC River Reach cross-sections",
            "Models downstream wave propagation and maps planar flood depth over terrain."
        ),
        (
            "Road Network & Routing",
            "OSMnx, NetworkX, OpenStreetMap Road Vectors, Depth-Constrained Dijkstra Graph Search",
            "Ingests road segments and calculates depth-constrained safe routes."
        ),
        (
            "Alerting & Web Interface",
            "FastAPI, Leaflet.js, OpenStreetMap Tiles, OASIS CAP v1.2 XML generator, Twilio SMS API",
            "Renders live flood map and dispatches regional SMS warnings in local languages."
        ),
    ]
    
    for row_idx, row_vals in enumerate(tech_rows_data, start=1):
        row = tech_tbl.rows[row_idx]
        bg_color = HEX_ALT_ROW if (row_idx % 2 == 1) else "FFFFFF"
        for c_idx, text in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = tech_col_widths[c_idx]
            set_cell_background(cell, bg_color)
            set_cell_padding(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = 'Calibri'
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGB_PRIMARY
            else:
                r.font.color.rgb = RGB_TEXT_BODY
                
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -----------------------------------------------------------------------
    # Section 6: Project Modules & Development Milestones
    # -----------------------------------------------------------------------
    add_heading_1(doc, "6. Project Modules & Development Milestones")
    add_body_p(
        doc,
        "The project work is partitioned into four balanced technical modules distributed across an 8-month development schedule:"
    )

    # Work Schedule Table
    sched_tbl = doc.add_table(rows=5, cols=3)
    sched_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    sched_tbl.autofit = False
    set_table_borders(sched_tbl, color=HEX_BORDER, sz="4")
    
    sched_col_widths = [Inches(1.8), Inches(3.2), Inches(1.8)]
    sched_headers = ["Project Phase & Timeline", "Key Milestones & Deliverables", "Assigned Module Lead"]
    
    for col_idx, h_text in enumerate(sched_headers):
        cell = sched_tbl.rows[0].cells[col_idx]
        cell.width = sched_col_widths[col_idx]
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_padding(cell, top=80, bottom=80, left=90, right=90)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = 'Calibri'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    sched_rows_data = [
        (
            "Phase 1: Ingestion & Backup\n(Months 1 - 2)",
            "CWC river sensor API integration, Sentinel-3 SAR data pipeline, and 15-minute polling loop implementation.",
            "[Module 1 Lead / Investigator 1]\nSensor data ingestion & failover"
        ),
        (
            "Phase 2: Hydraulics & GIS\n(Months 3 - 4)",
            "Downstream wave celerity calculation, SRTM 30m DEM processing, and road depth intersection algorithm.",
            "[Module 2 Lead / Investigator 2]\nHydrologic modeling & GIS depth mapping"
        ),
        (
            "Phase 3: Routing & Shelters\n(Months 5 - 6)",
            "Depth-constrained Dijkstra pathfinding on OSM graph, pedestrian/rescue profile filters, and shelter load balancing.",
            "[Module 3 Lead / Investigator 3]\nGraph routing & shelter capacity logic"
        ),
        (
            "Phase 4: Alerts & Testing\n(Months 7 - 8)",
            "OASIS CAP v1.2 alert feed, multi-language SMS dispatch, web situational dashboard, and integrated system testing.",
            "[Entire Project Group]\nIntegrated testing & documentation"
        ),
    ]
    
    for row_idx, row_vals in enumerate(sched_rows_data, start=1):
        row = sched_tbl.rows[row_idx]
        bg_color = HEX_ALT_ROW if (row_idx % 2 == 1) else "FFFFFF"
        for c_idx, text in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = sched_col_widths[c_idx]
            set_cell_background(cell, bg_color)
            set_cell_padding(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = 'Calibri'
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGB_PRIMARY
            else:
                r.font.color.rgb = RGB_TEXT_BODY
                
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -----------------------------------------------------------------------
    # Section 7: Expected Impact & Conclusion
    # -----------------------------------------------------------------------
    add_heading_1(doc, "7. Expected Impact & Conclusion")
    add_body_p(
        doc,
        "By focusing on the practical challenges observed during mountain flash floods and GLOFs in Uttarakhand, this proposed system offers a realistic solution for early warning "
        "and evacuation. Autonomous satellite radar backup prevents monitoring loss when ground sensors break; predicting downstream river rise gives "
        "families advance notice to evacuate; identifying vulnerable access roads allows rescue teams (NDRF) to stage boats before roads submerge; "
        "and depth-aware navigation prevents fleeing citizens from driving or walking into flooded roads."
    )
    add_body_p(
        doc,
        "The proposed system can serve as an affordable, scalable, and automated disaster management tool for district authorities."
    )

    # -----------------------------------------------------------------------
    # Section 8: Key References & Foundational Literature
    # -----------------------------------------------------------------------
    add_heading_1(doc, "8. Key References & Foundational Literature")
    refs = [
        "1. Central Water Commission (CWC), Ministry of Jal Shakti, Government of India, 'Hydrodynamic Modeling and River Flood Forecasting Guidelines', New Delhi, 2021.",
        "2. National Disaster Management Authority (NDMA), Government of India, 'Common Alerting Protocol (CAP) Implementation Manual for Disaster Warnings (Sachet)', New Delhi, 2022.",
        "3. Donchyts, G., et al., 'High-resolution satellite radar altimetry for inland water monitoring during severe cloud cover', Remote Sensing of Environment, vol. 212, pp. 115-128, 2018.",
        "4. OpenStreetMap Contributors & Boeing, G., 'OSMnx: New methods for acquiring, constructing, and analyzing complex street networks', Computers, Environment and Urban Systems, vol. 65, pp. 126-139, 2017.",
        "5. Copernicus Sentinel-3 Radar Altimetry Technical Guide, European Space Agency (ESA), Document ESA-EOPS-S3-TN, 2020.",
        "6. Uttarakhand State Disaster Management Authority (USDMA), 'Disaster Management Action Plan and Standard Operating Procedures for Mountain Hazards', Dehradun, Uttarakhand, 2023."
    ]
    for r in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_before = Pt(0)
        p_r.paragraph_format.space_after = Pt(2.5)
        p_r.paragraph_format.line_spacing = 1.15
        r_ref = p_r.add_run(r)
        r_ref.font.name = 'Calibri'
        r_ref.font.size = Pt(8.0)
        r_ref.font.color.rgb = RGB_TEXT_MUTED

    # -----------------------------------------------------------------------
    # Save the Word Document
    # -----------------------------------------------------------------------
    doc.save(filename)
    print(f"Successfully generated clean Word proposal document: {filename}")


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.join(out_dir, "Project_Idea_Proposal.docx")
    build_docx(out_file)
    
    # Also save a copy in the workspace root for convenience
    workspace_root = os.path.dirname(out_dir)
    root_out_file = os.path.join(workspace_root, "Project_Idea_Proposal.docx")
    try:
        import shutil
        shutil.copy2(out_file, root_out_file)
        print(f"Copied proposal docx to workspace root: {root_out_file}")
    except Exception as e:
        print(f"Warning: Could not copy to root: {e}")
