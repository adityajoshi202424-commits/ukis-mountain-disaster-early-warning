"""
Generate Concise, Clickable Word (.docx) and PDF (.pdf) Documentation
Features:
- Concise, easy-to-understand executive structure
- Clickable live hyperlinks that open the site directly on click
- Feature links table for judges
- Real data provenance table
- Multi-channel active alert system summary
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

LIVE_TUNNEL_URL = "https://frontend-rosy-phi-23.vercel.app"
VERCEL_LIVE_URL = "https://frontend-rosy-phi-23.vercel.app"

# Helper to add clickable hyperlink in python-docx
def add_docx_hyperlink(paragraph, url, text, color_hex="0056B3", underline=True, bold=True):
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    hyperlink = parse_xml(f'<w:hyperlink {nsdecls("w")} {nsdecls("r")} r:id="{r_id}"/>')
    new_run = parse_xml(
        f'<w:r {nsdecls("w")}>'
        f'  <w:rPr>'
        f'    <w:color w:val="{color_hex}"/>'
        f'    {"<w:u w:val=\'single\'/>" if underline else ""}'
        f'    {"<w:b/>" if bold else ""}'
        f'    <w:sz w:val="19"/>'
        f'  </w:rPr>'
        f'  <w:t>{text}</w:t>'
        f'</w:r>'
    )
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:left w:w="{left}" w:type="dxa"/>'
        f'  <w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def create_docx(output_path):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    navy = RGBColor(0x0A, 0x25, 0x40)
    crimson = RGBColor(0xB9, 0x1C, 0x1C)
    slate = RGBColor(0x33, 0x41, 0x55)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run("GOVERNMENT OF UTTARAKHAND • USDMA & ITDA DEVBHOOMI\n")
    r_sub.font.size = Pt(9.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = crimson

    r_main = p_title.add_run("AI Mountain Disaster Early-Warning Intelligence\n")
    r_main.font.size = Pt(18)
    r_main.font.bold = True
    r_main.font.color.rgb = navy

    r_code = p_title.add_run("UKIS 2026 Problem Statement P-011 • Operational System Documentation")
    r_code.font.size = Pt(10.5)
    r_code.font.italic = True
    r_code.font.color.rgb = slate

    # Summary Card Box
    tbl_card = doc.add_table(rows=1, cols=1)
    tbl_card.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_card = tbl_card.cell(0, 0)
    set_cell_background(cell_card, "F0F9FF")
    set_cell_margins(cell_card, 120, 120, 180, 180)
    p_card = cell_card.paragraphs[0]
    r_c1 = p_card.add_run("EXECUTIVE SUMMARY (WHY THIS IS NOT JUST A DASHBOARD):\n")
    r_c1.bold = True
    r_c1.font.size = Pt(9.5)
    r_c1.font.color.rgb = navy
    r_c2 = p_card.add_run(
        "Standard dashboards passively wait for someone to check a screen. In Himalayan valleys, flash floods "
        "and GLOFs travel at >5 m/s, leaving only 15–45 minutes of warning time. This system actively defends lives by: "
        "(1) Autonomously dialing voice phone calls to SDRF and District Magistrates with spoken English/Hindi alerts, "
        "(2) Pushing multilingual SMS in 6 local dialects with Dijkstra escape routes, (3) Actuating 120dB physical sirens, and "
        "(4) Providing an AI Commander Bot grounded in USDMA SOPs with 0% data fabrication."
    )
    r_c2.font.size = Pt(9.0)

    doc.add_paragraph()

    # Section 1: Live Interactive Links (Click to Open)
    h1 = doc.add_heading("1. Live Clickable Links for Judges & Evaluators", level=1)
    h1.runs[0].font.color.rgb = navy
    p_click_note = doc.add_paragraph("Click any link below to open the live system directly in your browser:")
    p_click_note.runs[0].font.size = Pt(9.5)
    p_click_note.runs[0].font.italic = True

    # Table of Links
    links_data = [
        ("Citizen Active Alerts Dashboard", f"{LIVE_TUNNEL_URL}", "Official CAP v1.2 real-time emergency warnings (Chamoli, Rudraprayag, Uttarkashi)"),
        ("Zero-Data Alert Simulator (iOS/Android)", f"{LIVE_TUNNEL_URL}/api/v1/alerts/mobile-broadcast", "3GPP TS 23.041 zero-data & grid power failure mobile broadcast test API"),
        ("Interactive AI Commander Bot", f"{LIVE_TUNNEL_URL}", "Click bottom-right floating bot. Answers evacuation queries, hazard reasons, and SOPs"),
        ("ISRO Bhuvan GIS Emergency Map", f"{LIVE_TUNNEL_URL}/emergency", "Interactive 14-hazard spatial grid, satellite/terrain layers & telemetry badges"),
        ("DMMC Ops Control & SMS Dispatcher", f"{LIVE_TUNNEL_URL}/admin", "Tab 7: Test live multilingual SMS push & dispatch automated voice calls"),
        ("Evacuation Shelters Directory", f"{LIVE_TUNNEL_URL}/shelters", "High-ground shelter capacities, GPS coordinates & emergency supply tracking"),
        ("Citizen Emergency Guidebook", f"{LIVE_TUNNEL_URL}/guidebook", "Offline survival protocols, flash flood evacuation rules & hotlines (112 / 1070)"),
        ("Permanent 24/7 Cloud Link (Vercel)", f"{VERCEL_LIVE_URL}", "Permanent production deployment hosted on Vercel's global edge network"),
        ("Official GitHub Repository (Dual-Sync)", "https://github.com/adityajoshi202424-commits/ukis-mountain-disaster-early-warning", "Direct git tracking repo synced with Vercel production"),
    ]

    tbl_links = doc.add_table(rows=1, cols=3)
    tbl_links.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = tbl_links.rows[0].cells
    hdr[0].text = "Platform Feature"
    hdr[1].text = "Direct Clickable Link (Click to Open)"
    hdr[2].text = "Live Interactive Capability"
    for c in hdr:
        set_cell_background(c, "0A2540")
        set_cell_margins(c, 100, 100, 120, 120)
        p = c.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8.5)
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for idx, (feat, url, desc) in enumerate(links_data):
        row = tbl_links.add_row()
        cells = row.cells
        cells[0].text = feat
        # Hyperlink in cell 1
        p_link = cells[1].paragraphs[0]
        add_docx_hyperlink(p_link, url, url, color_hex="0056B3", underline=True, bold=True)
        cells[2].text = desc

        for c_idx, c in enumerate(cells):
            set_cell_margins(c, 80, 80, 100, 100)
            if idx % 2 == 1:
                set_cell_background(c, "F8FAFC")
            p = c.paragraphs[0]
            if len(p.runs) > 0 and c_idx != 1:
                p.runs[0].font.size = Pt(8.0)

    doc.add_paragraph()

    # Section 2: Real Data Provenance
    h2 = doc.add_heading("2. What Data Are We Curating & From Where?", level=1)
    h2.runs[0].font.color.rgb = navy

    data_summary = [
        ("Open-Meteo Weather API", "Hourly rainfall, precipitation rate, surface pressure, 0°C freezing level", "Live / Real-Time", "Rainfall rate-of-rise & cloudburst detection"),
        ("Open-Meteo DEM Elevation", "High-res Copernicus 10m Digital Elevation Model (DEM)", "Live / Static DEM", "Topographic slope angle, elevation contour & flood routing"),
        ("Copernicus GloFAS (ECMWF)", "River discharge forecasts (m³/s), 5-day ensemble runoff", "Live / Real-Time", "Alaknanda and Bhagirathi river wave propagation"),
        ("USGS Real-Time Earthquakes", "Seismic magnitude, focal depth, epicenter coordinates", "Live / Real-Time", "Slope stability & seismically-triggered landslide alerts"),
        ("Central Water Commission (CWC)", "River gauge levels (m), discharge, danger mark exceedance", "Sensor Feeds", "Critical threshold detection & automated call triggers"),
        ("USDMA Shelter Database", "Safe haven capacity, altitude, coordinates, contact officers", "GIS Registry", "Dynamic haven allocation & shortest escape routing"),
    ]

    tbl_data = doc.add_table(rows=1, cols=4)
    tbl_data.alignment = WD_TABLE_ALIGNMENT.CENTER
    d_hdr = tbl_data.rows[0].cells
    d_hdr[0].text = "Source Provider"
    d_hdr[1].text = "Curated Data Parameters"
    d_hdr[2].text = "Query Cadence"
    d_hdr[3].text = "Core Function in Platform"
    for c in d_hdr:
        set_cell_background(c, "B91C1C")
        set_cell_margins(c, 100, 100, 120, 120)
        p = c.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8.5)
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for idx, (src, params, cad, func) in enumerate(data_summary):
        row = tbl_data.add_row()
        cells = row.cells
        cells[0].text = src
        cells[1].text = params
        cells[2].text = cad
        cells[3].text = func
        for c in cells:
            set_cell_margins(c, 70, 70, 100, 100)
            if idx % 2 == 1:
                set_cell_background(c, "FEF2F2")
            p = c.paragraphs[0]
            if len(p.runs) > 0:
                p.runs[0].font.size = Pt(8.0)

    doc.add_paragraph()

    # Section 3: Active Alerting Channels
    h3 = doc.add_heading("3. Active Alerting & Autonomous Authority Calling", level=1)
    h3.runs[0].font.color.rgb = navy

    bullets = [
        ("Autonomous Authority Voice Calls: ", "When hazard severity hits CRITICAL/RED, the AuthorityCallDispatcher dials emergency commanders (SEOC Duty Officer, SDRF Commandant, District Magistrates) with synthesized bilingual English/Hindi audio briefings and gathers DTMF keypad confirmation."),
        ("Hyperlocal Multilingual SMS Push: ", "Dispatches vernacular SMS alerts across 6 regional tongues (Hindi, Garhwali, Kumaoni, Jaunsari, English, Sanskrit) embedding dynamically computed Dijkstra evacuation paths and safe havens."),
        ("C-DOT Cell Broadcast (Zero Data): ", "Geo-targeted cell tower pings that alert every mobile phone in the affected polygon without requiring mobile data or active SMS balance."),
        ("Physical 120dB Sirens: ", "Actuates on-site relay horns and strobe beacons on sensor towers to wake sleeping residents during nocturnal mountain floods."),
        ("SOP-Grounded AI Commander Bot: ", "Provides natural-language answers strictly grounded in live telemetry and USDMA SOP-01 protocols with 0% data fabrication."),
    ]
    for b_title, b_desc in bullets:
        p = doc.add_paragraph()
        r1 = p.add_run(f"• {b_title}")
        r1.bold = True
        r1.font.color.rgb = navy
        r1.font.size = Pt(9.0)
        r2 = p.add_run(b_desc)
        r2.font.size = Pt(9.0)

    doc.save(output_path)
    print(f"Created Word document: {output_path}")


def create_pdf(output_path):
    pdf = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0A2540'),
        alignment=1, # Center
    )
    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#B91C1C'),
        alignment=1,
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#0A2540'),
        spaceBefore=10,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155'),
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0A2540'),
    )
    link_style = ParagraphStyle(
        'Link',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.0,
        leading=10,
        textColor=colors.HexColor('#0056B3'),
    )
    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.0,
        leading=10,
        textColor=colors.white,
    )
    td_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1E293B'),
    )
    card_style = ParagraphStyle(
        'Card',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.0,
        leading=11,
        textColor=colors.HexColor('#0F172A'),
    )

    story = []

    # Title Banner
    story.append(Paragraph("GOVERNMENT OF UTTARAKHAND • USDMA & ITDA DEVBHOOMI", sub_style))
    story.append(Paragraph("AI Mountain Disaster Early-Warning Intelligence", title_style))
    story.append(Paragraph("<i>UKIS 2026 Problem Statement P-011 • System Documentation &amp; Live Links</i>", ParagraphStyle('Ital', parent=sub_style, fontName='Helvetica-Oblique', textColor=colors.HexColor('#64748B'))))
    story.append(Spacer(1, 8))

    # Executive Callout
    card_data = [[
        Paragraph(
            "<b>EXECUTIVE SUMMARY (WHY THIS IS NOT JUST A DASHBOARD):</b><br/>"
            "Mountain flash floods travel at &gt;5 m/s, leaving only 15–45 minutes of warning time. "
            "This system actively defends lives by: <b>(1) Autonomously dialing voice phone calls</b> to SDRF &amp; District Magistrates "
            "with spoken English/Hindi audio briefings, <b>(2) Pushing multilingual SMS</b> in 6 dialects with Dijkstra escape routes, "
            "<b>(3) Actuating 120dB physical sirens</b>, and <b>(4) Operating an interactive AI Commander Bot</b> with 0% data fabrication.",
            card_style
        )
    ]]
    t_card = Table(card_data, colWidths=[522])
    t_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F9FF')),
        ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor('#BAE6FD')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_card)
    story.append(Spacer(1, 10))

    # Section 1: Live Interactive Links
    story.append(Paragraph("1. Live Clickable Links for Judges &amp; Evaluators", h1_style))
    story.append(Paragraph("<i>Click any blue link below to open the live system directly in your browser:</i>", body_style))
    story.append(Spacer(1, 5))

    links_rows = [
        [Paragraph("Platform Feature", th_style), Paragraph("Clickable Live URL (Click to Open)", th_style), Paragraph("Live Interactive Capability", th_style)],
        [
            Paragraph("<b>Citizen Active Alerts</b>", td_style),
            Paragraph(f'<a href="{LIVE_TUNNEL_URL}"><u><b>{LIVE_TUNNEL_URL}</b></u></a>', link_style),
            Paragraph("Official CAP v1.2 real-time emergency warnings (Chamoli, Rudraprayag, Uttarkashi)", td_style),
        ],
        [
            Paragraph("<b>Zero-Data Alert Simulator</b>", td_style),
            Paragraph(f'<a href="{LIVE_TUNNEL_URL}/api/v1/alerts/mobile-broadcast"><u><b>{LIVE_TUNNEL_URL}/api/v1/alerts/mobile-broadcast</b></u></a>', link_style),
            Paragraph("3GPP TS 23.041 zero-data &amp; power-cut mobile broadcast test API (iOS &amp; Android)", td_style),
        ],
        [
            Paragraph("<b>Interactive AI Commander Bot</b>", td_style),
            Paragraph(f'<a href="{LIVE_TUNNEL_URL}"><u><b>{LIVE_TUNNEL_URL}</b></u></a>', link_style),
            Paragraph("Click bottom-right floating bot. Answers evacuation queries, hazard reasons, and SOPs", td_style),
        ],
        [
            Paragraph("<b>ISRO Bhuvan GIS Map</b>", td_style),
            Paragraph(f'<a href="{LIVE_TUNNEL_URL}/emergency"><u><b>{LIVE_TUNNEL_URL}/emergency</b></u></a>', link_style),
            Paragraph("Interactive 14-hazard spatial grid, satellite/terrain layers &amp; telemetry badges", td_style),
        ],
        [
            Paragraph("<b>Admin Room &amp; SMS Dispatcher</b>", td_style),
            Paragraph(f'<a href="{LIVE_TUNNEL_URL}/admin"><u><b>{LIVE_TUNNEL_URL}/admin</b></u></a>', link_style),
            Paragraph("Tab 7: Test live multilingual SMS push &amp; dispatch automated authority voice calls", td_style),
        ],
        [
            Paragraph("<b>Evacuation Shelters Directory</b>", td_style),
            Paragraph(f'<a href="{LIVE_TUNNEL_URL}/shelters"><u><b>{LIVE_TUNNEL_URL}/shelters</b></u></a>', link_style),
            Paragraph("High-ground shelter capacities, GPS coordinates &amp; emergency supply tracking", td_style),
        ],
        [
            Paragraph("<b>Citizen Guidebook</b>", td_style),
            Paragraph(f'<a href="{LIVE_TUNNEL_URL}/guidebook"><u><b>{LIVE_TUNNEL_URL}/guidebook</b></u></a>', link_style),
            Paragraph("Offline survival protocols, flash flood evacuation rules &amp; hotlines (112 / 1070)", td_style),
        ],
        [
            Paragraph("<b>Permanent Cloud Link (Vercel)</b>", td_style),
            Paragraph(f'<a href="{VERCEL_LIVE_URL}"><u><b>{VERCEL_LIVE_URL}</b></u></a>', link_style),
            Paragraph("Permanent production deployment hosted on Vercel's global edge network", td_style),
        ],
        [
            Paragraph("<b>GitHub Repository (Dual-Sync)</b>", td_style),
            Paragraph('<a href="https://github.com/adityajoshi202424-commits/ukis-mountain-disaster-early-warning"><u><b>github.com/.../ukis-mountain-disaster-early-warning</b></u></a>', link_style),
            Paragraph("Public repository with dual-sync script for automated Vercel production deployment", td_style),
        ],
    ]

    t_links = Table(links_rows, colWidths=[125, 175, 222])
    t_links.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A2540')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_links)
    story.append(Spacer(1, 10))

    # Section 2: Data Curation
    story.append(Paragraph("2. What Data Are We Curating &amp; From Where?", h1_style))
    data_rows = [
        [Paragraph("Source Provider", th_style), Paragraph("Curated Parameters", th_style), Paragraph("Cadence", th_style), Paragraph("Core Function in Platform", th_style)],
        [
            Paragraph("<b>Open-Meteo Weather API</b>", td_style),
            Paragraph("Rainfall rate, 24h rain, 0°C freezing level, soil moisture", td_style),
            Paragraph("Live Real-Time", td_style),
            Paragraph("Rainfall rate-of-rise &amp; cloudburst detection", td_style),
        ],
        [
            Paragraph("<b>Open-Meteo DEM Elevation</b>", td_style),
            Paragraph("Copernicus / SRTM 10m Digital Elevation Model", td_style),
            Paragraph("Live DEM Query", td_style),
            Paragraph("Slope gradient, contour elevation &amp; flood routing", td_style),
        ],
        [
            Paragraph("<b>Copernicus GloFAS (ECMWF)</b>", td_style),
            Paragraph("River discharge forecasts (m³/s), 5-day runoff", td_style),
            Paragraph("Live Forecast", td_style),
            Paragraph("Alaknanda &amp; Bhagirathi basin flood surge modeling", td_style),
        ],
        [
            Paragraph("<b>USGS Real-Time Seismicity</b>", td_style),
            Paragraph("Earthquake magnitude, depth, epicenter coordinates", td_style),
            Paragraph("Live Feed", td_style),
            Paragraph("Slope creep stress &amp; seismically-triggered landslide alerts", td_style),
        ],
        [
            Paragraph("<b>Central Water Commission</b>", td_style),
            Paragraph("Gauge river stage (m), danger mark exceedance", td_style),
            Paragraph("Sensor Stream", td_style),
            Paragraph("River cresting detection &amp; automated call triggers", td_style),
        ],
        [
            Paragraph("<b>USDMA Shelter Registry</b>", td_style),
            Paragraph("Shelter capacities, high-ground GPS coordinates", td_style),
            Paragraph("GIS Registry", td_style),
            Paragraph("Dynamic haven allocation &amp; shortest escape routing", td_style),
        ],
    ]

    t_data = Table(data_rows, colWidths=[120, 160, 75, 167])
    t_data.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B91C1C')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FEF2F2')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_data)
    story.append(Spacer(1, 10))

    # Section 3: Active Warning System
    story.append(Paragraph("3. Active Multi-Channel Alerting &amp; Calling System", h1_style))
    bullets_pdf = [
        "<b>• Autonomous Authority Voice Calls:</b> Dials emergency commanders (SEOC, SDRF, District Magistrates) with synthesized bilingual English/Hindi audio briefings and gathers keypad acknowledgment.",
        "<b>• Hyperlocal Multilingual SMS Push:</b> Dispatches vernacular SMS in 6 languages (Hindi, Garhwali, Kumaoni, Jaunsari, English, Sanskrit) embedding dynamically computed safe haven escape routes.",
        "<b>• C-DOT Cell Broadcast (Zero Data):</b> Mass geo-fenced cell tower pings alerting all mobile handsets in the hazard zone without requiring internet or active SIM balance.",
        "<b>• Physical 120dB Sirens:</b> Actuates on-site relay horns and strobe beacons on sensor towers to wake sleeping residents during nocturnal mountain floods.",
        "<b>• Interactive AI Commander Bot:</b> Answers operational queries strictly grounded in live telemetry and USDMA SOPs with 0% data fabrication.",
    ]
    for b in bullets_pdf:
        story.append(Paragraph(b, body_style))
        story.append(Spacer(1, 2))

    pdf.build(story)
    print(f"Created PDF document: {output_path}")


def safe_save_docx(create_fn, target_path, alt_path):
    try:
        create_fn(target_path)
    except PermissionError:
        print(f"[NOTE] '{target_path}' is currently open in Microsoft Word. Saving to '{alt_path}' instead.")
        create_fn(alt_path)

def safe_save_pdf(create_fn, target_path, alt_path):
    try:
        create_fn(target_path)
    except PermissionError:
        print(f"[NOTE] '{target_path}' is currently open in a PDF viewer. Saving to '{alt_path}' instead.")
        create_fn(alt_path)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(root_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    # Primary Names
    docx_root = os.path.join(root_dir, "DATA_CURATION_AND_ACTIVE_ALERT_SYSTEM.docx")
    docx_alt = os.path.join(root_dir, "DATA_CURATION_AND_ACTIVE_ALERT_SYSTEM_SHORT.docx")
    docx_docs = os.path.join(docs_dir, "DATA_CURATION_AND_ACTIVE_ALERT_SYSTEM.docx")
    docx_overview = os.path.join(root_dir, "UKIS_DISASTER_SYSTEM_OVERVIEW.docx")

    pdf_root = os.path.join(root_dir, "DATA_CURATION_AND_ACTIVE_ALERT_SYSTEM.pdf")
    pdf_alt = os.path.join(root_dir, "DATA_CURATION_AND_ACTIVE_ALERT_SYSTEM_PERMANENT.pdf")
    pdf_docs = os.path.join(docs_dir, "DATA_CURATION_AND_ACTIVE_ALERT_SYSTEM.pdf")
    pdf_overview = os.path.join(root_dir, "UKIS_DISASTER_SYSTEM_OVERVIEW.pdf")

    # Generate Word Documents
    safe_save_docx(create_docx, docx_root, docx_alt)
    safe_save_docx(create_docx, docx_docs, os.path.join(docs_dir, "DATA_CURATION_AND_ACTIVE_ALERT_SYSTEM_SHORT.docx"))
    safe_save_docx(create_docx, docx_overview, os.path.join(root_dir, "UKIS_DISASTER_SYSTEM_OVERVIEW_UPDATED.docx"))

    # Generate PDF Documents
    safe_save_pdf(create_pdf, pdf_root, pdf_alt)
    safe_save_pdf(create_pdf, pdf_docs, os.path.join(docs_dir, "DATA_CURATION_AND_ACTIVE_ALERT_SYSTEM_PERMANENT.pdf"))
    safe_save_pdf(create_pdf, pdf_overview, os.path.join(root_dir, "UKIS_DISASTER_SYSTEM_OVERVIEW_PERMANENT.pdf"))

    print("\n==========================================================================")
    print(" [SUCCESS] GENERATED SHORT, EASY-TO-UNDERSTAND WORD & PDF DOCUMENTS:")
    print(f" • PDF (Instant Clickable Links): {pdf_root}")
    print(f" • PDF (Docs Copy):               {pdf_docs}")
    print(f" • Word (.docx Overview):         {docx_overview}")
    print(f" • Word (.docx):                  {docx_root}")
    print("==========================================================================")

if __name__ == "__main__":
    main()
