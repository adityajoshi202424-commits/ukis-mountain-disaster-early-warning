"""
Academic Project Idea Proposal Generator (Straightforward & Authentic)
Title: "Flash Flood Early Warning, Rescuer Assistance, and Safe Evacuation Routing System"
Subtitle: "A Practical Engineering Proposal for Sensor Failover, Street-Level Inundation Estimation,
           and Depth-Aware Evacuation Navigation"

Strict Rules:
- NO fake data, NO fabricated benchmark readings (no 248k edges, no 194ms, no 99.4%, no 6 islands).
- NO fake dilemmas or dramatic buzzwords.
- Straightforward presentation of:
  1. The issues we are fixing
  2. How the system works & its implementation
  3. How it is new (comparison table with existing systems)
- NO student or supervisor names (generic placeholders only).
- Exactly 4 balanced pages in ReportLab PDF.
"""

from __future__ import annotations
import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------
# Two-Pass Numbered Canvas for Running Header & Footer
# ----------------------------------------------------------------------
class ProposalNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        page = self._pageNumber
        w, h = A4

        # Running Header on pages > 1
        if page > 1:
            self.saveState()
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#1e3a8a"))
            self.drawString(40, h - 26, "MAJOR PROJECT IDEA PROPOSAL: FLASH FLOOD EARLY WARNING & RESCUE ROUTING")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(w - 40, h - 26, "B.TECH CSE (ACADEMIC YEAR 2026-2027)")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.65)
            self.line(40, h - 31, w - 40, h - 31)
            self.restoreState()

        # Running Footer on all pages
        self.saveState()
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.65)
        self.line(40, 34, w - 40, 34)

        self.setFont("Helvetica", 7.2)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(40, 23, "Dept. of Computer Science & Engineering | Project Idea Proposal & Synopsis")

        page_str = f"Page {page} of {page_count}"
        self.setFont("Helvetica-Bold", 7.8)
        self.setFillColor(colors.HexColor("#1e3a8a"))
        self.drawRightString(w - 40, 23, page_str)
        self.restoreState()


def build_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#0f172a"),
        alignment=0,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica-Bold',
        fontSize=9.8,
        leading=13.5,
        textColor=colors.HexColor("#2563eb"),
        alignment=0,
        spaceAfter=9
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=11.0,
        leading=14.5,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=9.2,
        leading=12.5,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.6,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4.5
    )
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        fontName='Helvetica',
        fontSize=8.3,
        leading=11.3,
        textColor=colors.HexColor("#334155"),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.5
    )
    meta_label = ParagraphStyle(
        'MetaLabel',
        fontName='Helvetica-Bold',
        fontSize=8.0,
        leading=10.5,
        textColor=colors.HexColor("#1e3a8a")
    )
    meta_val = ParagraphStyle(
        'MetaVal',
        fontName='Helvetica',
        fontSize=8.0,
        leading=10.5,
        textColor=colors.HexColor("#334155")
    )
    tbl_hdr = ParagraphStyle(
        'TblHdr',
        fontName='Helvetica-Bold',
        fontSize=8.0,
        leading=10.5,
        textColor=colors.white
    )
    tbl_cell = ParagraphStyle(
        'TblCell',
        fontName='Helvetica',
        fontSize=7.6,
        leading=10.0,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # =========================================================================
    # PAGE 1: BANNER, METADATA, INTRODUCTION & ISSUES WE ARE FIXING
    # =========================================================================
    
    # Top Institutional Banner
    banner_data = [
        [
            Paragraph("<b>DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING</b><br/><font size=7.5 color='#64748b'>B.Tech Major Project Idea Proposal • Academic Session 2026-2027</font>", meta_label),
            Paragraph("<b>Submission Date:</b> September 2026<br/><b>Location:</b> Uttarakhand, India", meta_val)
        ]
    ]
    banner_tbl = Table(banner_data, colWidths=[360, 155])
    banner_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(banner_tbl)
    story.append(HRFlowable(width="100%", thickness=1.0, color=colors.HexColor("#cbd5e1"), spaceBefore=3, spaceAfter=7))

    # Title & Subtitle
    story.append(Paragraph("Flash Flood Early Warning, Rescuer Assistance, and Safe Evacuation Routing System", title_style))
    story.append(Paragraph("A Practical Engineering Proposal for Sensor Failover, Street-Level Inundation Estimation, and Depth-Aware Evacuation Navigation", subtitle_style))

    # Metadata Box (Generic Placeholders - ZERO Student Names)
    meta_table_data = [
        [
            Paragraph("<b>Student Investigators:</b>", meta_label),
            Paragraph("[Undergraduate Project Group / Student Candidate Names & Roll Numbers]", meta_val),
        ],
        [
            Paragraph("<b>Project Guides:</b>", meta_label),
            Paragraph("[Faculty Supervisor / Project Guide, Dept. of Computer Science & Engineering]", meta_val),
        ],
        [
            Paragraph("<b>Target Study Area:</b>", meta_label),
            Paragraph("Alaknanda & Bhagirathi River Basins (Focusing on Chamoli, Rudraprayag & High-Risk Mountain Districts, Uttarakhand)", meta_val),
        ]
    ]
    meta_box = Table(meta_table_data, colWidths=[110, 405])
    meta_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_box)
    story.append(Spacer(1, 6))

    # Section 1: Introduction & Objective
    story.append(Paragraph("1. Introduction & Project Objective", h1_style))
    story.append(Paragraph(
        "During the monsoon season, sudden intense cloudbursts and glacial lake activity in the high Himalayan tracts of India cause mountain torrents "
        "to surge rapidly. In steep mountain regions like Uttarakhand, flash floods and debris flows raise water levels over very short periods, creating severe challenges for "
        "communities living near riverbanks and for municipal and state disaster agencies. The objective of this project is to develop an automated, practical "
        "software system that predicts street-level flood depths in advance, assists emergency rescue personnel (NDRF and SDRF) in positioning assets "
        "before access corridors submerge, and guides citizens along safe, dry routes to designated government relief shelters.",
        body_style
    ))
    story.append(Paragraph(
        "Rather than focusing on theoretical hydrodynamics alone, this project tackles the direct operational issues that cause disaster response to fail on the ground: "
        "loss of river gauge data during severe weather, general weather advisories that lack street-level depth details, standard GPS map apps that guide drivers "
        "into flooded roads, and reactive rescue deployments that arrive after road access is already cut off.",
        body_style
    ))

    # Section 2: The Core Issues We Are Fixing
    story.append(Paragraph("2. The Operational Issues We Are Fixing", h1_style))
    
    story.append(Paragraph("<b>Issue 1: Physical River Gauges Fail During Severe Storms</b>", h2_style))
    story.append(Paragraph(
        "Automated river staff gauges and ultrasonic level sensors installed on riverbanks are exposed to strong currents, uprooted trees, floating logs, "
        "and heavy silt. These forces frequently damage or submerge the sensors. At the same time, high winds cause local power blackouts and cellular tower "
        "failures. As a result, ground sensor telemetry frequently stops transmitting during extreme storms. When physical sensors go offline, disaster "
        "managers lose real-time visibility into river levels at the exact time when water is rising fastest.",
        body_style
    ))

    story.append(Paragraph("<b>Issue 2: Standard Navigation Apps Lack Flood Depth Information</b>", h2_style))
    story.append(Paragraph(
        "Commercial navigation apps (such as Google Maps) are designed to find the shortest or fastest dry-weather route based on traffic speed. "
        "They have no information about road water depth. During a flood, these apps continue directing fleeing families along roads that cross low underpasses, "
        "culverts, and river dips. Moving water as shallow as 15 cm can wash away pedestrians, while 30 cm floats ordinary passenger cars and stalls engines, "
        "creating serious hazards for evacuees.",
        body_style
    ))

    story.append(Paragraph("<b>Issue 3: Emergency Rescuers Are Dispatched After Access Roads Are Already Submerged</b>", h2_style))
    story.append(Paragraph(
        "Emergency rescue teams are usually dispatched only after distress calls begin arriving. Many low-lying villages connect to regional highways via "
        "a single low-lying road. Once that access road is submerged under deep water, heavy rescue vehicles cannot enter, and launching motorized rescue boats "
        "through flooded trees and debris becomes slow and difficult. Rescue teams need advance notification to move boats and supplies into position before "
        "the access road is cut off.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: WORKING MECHANISM & SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("3. System Architecture & Working Mechanism", h1_style))
    story.append(Paragraph(
        "The proposed system connects river sensor monitoring, automated satellite radar backup, road water depth calculation, and depth-aware navigation. "
        "The system operates across four coordinated stages:",
        body_style
    ))

    # 4-Stage Operational Table
    arch_tbl_data = [
        [
            Paragraph("<b>Stage</b>", tbl_hdr),
            Paragraph("<b>Core Function & Implementation</b>", tbl_hdr),
            Paragraph("<b>Operational Outcome</b>", tbl_hdr),
        ],
        [
            Paragraph("<b>1. River Monitoring & Satellite Radar Backup</b>", tbl_cell),
            Paragraph("Polls Central Water Commission (CWC) automated river gauges. Automatically switches to Copernicus Sentinel-3 SAR satellite radar altimetry if ground telemetry stops.", tbl_cell),
            Paragraph("Maintains water height tracking through dense monsoon rain clouds without relying on vulnerable ground poles.", tbl_cell),
        ],
        [
            Paragraph("<b>2. Downstream River Rise Estimation</b>", tbl_cell),
            Paragraph("Calculates flood wave travel along river reaches from upstream stations to downstream settlements; checks satellite soil moisture to identify when saturated soil creates direct runoff.", tbl_cell),
            Paragraph("Provides roughly 2 or more hours of advance notice before the flood crest reaches downstream settlements.", tbl_cell),
        ],
        [
            Paragraph("<b>3. Street-by-Street Flood Depth Mapping</b>", tbl_cell),
            Paragraph("Subtracts road elevation (from SRTM 30m Digital Elevation Model) from predicted river surface elevation across OpenStreetMap road centerlines.", tbl_cell),
            Paragraph("Determines estimated water depth on every road segment and identifies single-access roads at risk of cut-off.", tbl_cell),
        ],
        [
            Paragraph("<b>4. Multi-Channel Alerts & Depth-Aware Routing</b>", tbl_cell),
            Paragraph("Dispatches SMS alerts in local languages; routes evacuees along dry roads to verified government shelters; generates advance staging alerts for rescue teams.", tbl_cell),
            Paragraph("Prevents families from entering flooded roads and enables rescue personnel to pre-stage boats before roads close.", tbl_cell),
        ],
    ]
    arch_tbl = Table(arch_tbl_data, colWidths=[105, 230, 180])
    arch_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(arch_tbl)
    story.append(Spacer(1, 6))

    # Subsection 3.1: Satellite Radar Failover
    story.append(Paragraph("3.1 Satellite Radar Backup: Maintaining Data When Ground Sensors Fail", h2_style))
    story.append(Paragraph(
        "Under normal conditions, the pipeline queries automated water level feeds from CWC river stations. The software performs continuous heartbeat "
        "checks: if telemetry from a ground gauge is missing for 15 minutes or reports corrupt values, the system flags the station as offline and activates "
        "backup satellite radar data.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Working Principle of Satellite Radar:</b> Standard optical satellite cameras cannot see through dense monsoon clouds and rain. "
        "In contrast, Synthetic Aperture Radar (SAR) altimetry on satellites like Sentinel-3 sends microwave radar pulses that pass directly through thick storm clouds "
        "and heavy downpours. The radar beam reflects off the water surface back to the satellite, allowing water surface elevation to be measured from orbit. "
        "Because the satellite is in space, it is completely unaffected by damaged ground poles, local power cuts, or fallen cellular towers.",
        body_style
    ))

    # Subsection 3.2: Downstream Water Level Estimation
    story.append(Paragraph("3.2 Downstream River Rise Estimation", h2_style))
    story.append(Paragraph(
        "When heavy rainfall occurs in upper hill catchments, the surge moves downstream along the river channel. By tracking water elevation at upstream "
        "stations and estimating flood wave travel time along the river reach, the system estimates the expected river height and arrival time at downstream towns, "
        "providing a lead time of 2 or more hours.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Soil Moisture Factor:</b> Dry soil absorbs heavy rain, but after consecutive days of monsoon showers, soil becomes saturated. "
        "When soil moisture reaches saturation, additional rainfall cannot seep into the ground and turns immediately into rapid surface runoff. "
        "The system reads satellite soil moisture data (NASA GPM feeds) to identify when incoming rainfall will directly produce sharp surface surges.",
        body_style
    ))

    # Subsection 3.3: Street Flood Depth Calculation
    story.append(Paragraph("3.3 Street-Level Flood Depth Calculation", h2_style))
    story.append(Paragraph(
        "To calculate water depth on individual roads, the system compares the predicted river water level against the ground elevation of each road segment "
        "using a 30-meter Digital Elevation Model (SRTM DEM) and OpenStreetMap road vector centerlines. The estimated water depth determines road accessibility:",
        body_style
    ))

    # Table 2: Road Water Depth Risk Classification
    risk_tbl_data = [
        [
            Paragraph("<b>Depth Category</b>", tbl_hdr),
            Paragraph("<b>Estimated Depth</b>", tbl_hdr),
            Paragraph("<b>Vehicle & Pedestrian Accessibility</b>", tbl_hdr),
            Paragraph("<b>System Action</b>", tbl_hdr),
        ],
        [
            Paragraph("<b>Tier 1: Dry</b>", tbl_cell),
            Paragraph("&lt; 5 cm", tbl_cell),
            Paragraph("All civilian vehicles and pedestrians permitted.", tbl_cell),
            Paragraph("Designated as open evacuation corridor.", tbl_cell),
        ],
        [
            Paragraph("<b>Tier 2: Shallow Water</b>", tbl_cell),
            Paragraph("5 cm to 15 cm", tbl_cell),
            Paragraph("Vehicles passable with care; unsafe for walking pedestrians.", tbl_cell),
            Paragraph("Excluded from walking evacuation routes.", tbl_cell),
        ],
        [
            Paragraph("<b>Tier 3: Dangerous Depth</b>", tbl_cell),
            Paragraph("15 cm to 80 cm", tbl_cell),
            Paragraph("Closed for civilian cars and walkers; high rescue trucks only.", tbl_cell),
            Paragraph("Reserved for NDRF/SDRF 4x4 rescue trucks.", tbl_cell),
        ],
        [
            Paragraph("<b>Tier 4: Deep Flood</b>", tbl_cell),
            Paragraph("&gt; 80 cm", tbl_cell),
            Paragraph("Closed to all motor vehicles; rescue boats only.", tbl_cell),
            Paragraph("Marked impassable for all wheeled traffic.", tbl_cell),
        ],
    ]
    risk_tbl = Table(risk_tbl_data, colWidths=[95, 80, 185, 155])
    risk_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(risk_tbl)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: RESCUERS, EVACUATION, SHELTERS & NOVELTY COMPARISON
    # =========================================================================
    
    # Subsection 3.4: Rescuer Assistance
    story.append(Paragraph("3.4 Emergency Rescuer Assistance: Cut-Off Alerts & High-Clearance Routes", h1_style))
    story.append(Paragraph(
        "A practical contribution of this project is assisting rescue agencies (such as NDRF and SDRF) before access is lost:",
        body_style
    ))
    story.append(Paragraph(
        "<b>Advance Single-Access Cut-Off Alerts:</b> Many riverside villages connect to main highways through a single road. "
        "The system identifies villages whose sole connecting road is predicted to exceed 30 cm depth within the next 2 hours. "
        "Disaster coordinators receive an automated alert so they can dispatch boats, fuel, and medical personnel to high-ground staging areas near those "
        "villages before the road is submerged.",
        body_style
    ))
    story.append(Paragraph(
        "<b>High-Clearance Rescue Truck Routes:</b> Heavy emergency trucks (NDRF 4x4 vehicles) have high air intakes and can safely ford water up to 80 cm deep. "
        "The routing engine calculates dedicated paths allowing rescue convoys to traverse shallow flooded streets to reach stranded residents directly.",
        body_style
    ))

    # Subsection 3.5: Civilian Evacuation Routing
    story.append(Paragraph("3.5 Civilian Evacuation: Depth-Aware Safe Routing", h1_style))
    story.append(Paragraph(
        "The evacuation routing engine builds on OpenStreetMap road graphs using Dijkstra's algorithm with depth safety constraints:",
        body_style
    ))
    story.append(Paragraph(
        "&bull; <b>Pedestrian Ceiling (&lt; 15 cm):</b> Moving water as shallow as 15 cm can sweep away walking adults and children. "
        "For pedestrians, roads with 15 cm or more water are assigned infinite travel cost, guiding families strictly along dry ridges.",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Vehicle Ceiling (&lt; 30 cm):</b> For cars and two-wheelers, the system blocks road dips and underpasses where water exceeds 30 cm, preventing vehicle stall.",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Dynamic Road Blocking:</b> As rainfall continues and water levels rise, flooded segments are dynamically closed on the graph, "
        "automatically rerouting evacuees along safe alternative roads.",
        bullet_style
    ))

    # Subsection 3.6: Relief Shelters
    story.append(Paragraph("3.6 Government Relief Centre Selection & Capacity Balancing", h1_style))
    story.append(Paragraph(
        "The system ensures families are guided only to shelters that are genuinely secure: (1) verifying that the shelter's plinth elevation is above the "
        "projected flood water level, (2) confirming that at least one incoming road connection remains dry (&lt; 15 cm depth), and (3) monitoring shelter "
        "capacity so that once a relief center approaches its maximum occupancy, incoming evacuees are redirected to the next nearest open facility.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Section 4: How This Idea Is New (Novelty Comparison Table)
    story.append(Paragraph("4. How This Idea Is New: Comparison with Existing Systems", h1_style))
    story.append(Paragraph(
        "The table below summarizes the key operational differences between existing disaster management tools and our proposed engineering solution:",
        body_style
    ))

    # Comparison Table (Novelty)
    comp_tbl_data = [
        [
            Paragraph("<b>Operational Dimension</b>", tbl_hdr),
            Paragraph("<b>Current Standard Systems</b>", tbl_hdr),
            Paragraph("<b>Proposed Solution (What Is New)</b>", tbl_hdr),
        ],
        [
            Paragraph("<b>River Monitoring Continuity</b>", tbl_cell),
            Paragraph("Relies solely on physical river staff gauges; stops transmitting if sensors are damaged or storm power fails.", tbl_cell),
            Paragraph("Automated failover to Copernicus Sentinel-3 SAR satellite radar altimetry; penetrates rain clouds without ground sensors.", tbl_cell),
        ],
        [
            Paragraph("<b>Warning Granularity</b>", tbl_cell),
            Paragraph("Broad district-level or river basin warnings; does not specify which local streets will flood.", tbl_cell),
            Paragraph("Calculates estimated water depth street-by-street by intersecting DEM elevation with predicted water surface.", tbl_cell),
        ],
        [
            Paragraph("<b>Evacuation Navigation</b>", tbl_cell),
            Paragraph("Commercial GPS apps (Google Maps) only consider dry traffic; frequently route cars into submerged roads and underpasses.", tbl_cell),
            Paragraph("Depth-constrained graph routing enforcing physical safety limits (&lt;15 cm walking, &lt;30 cm car) to avoid flooded roads.", tbl_cell),
        ],
        [
            Paragraph("<b>Rescuer Support</b>", tbl_cell),
            Paragraph("Reactive deployment after distress calls; rescue teams often find access roads already submerged.", tbl_cell),
            Paragraph("Flags single-access villages facing road cut-off 2 hours in advance; provides special routes for 4x4 rescue trucks (&le;80 cm).", tbl_cell),
        ],
        [
            Paragraph("<b>Relief Shelter Allocation</b>", tbl_cell),
            Paragraph("Static list of shelters without verifying road access or live capacity; evacuees may find facilities flooded or full.", tbl_cell),
            Paragraph("Dynamically verifies dry road access to shelters and redirects evacuees when a facility approaches full capacity.", tbl_cell),
        ],
    ]
    comp_tbl = Table(comp_tbl_data, colWidths=[105, 205, 205])
    comp_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(comp_tbl)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: IMPLEMENTATION PLAN, WORK SCHEDULE, IMPACT & REFERENCES
    # =========================================================================

    story.append(Paragraph("5. Implementation Plan & Open-Source Technology Stack", h1_style))
    story.append(Paragraph(
        "The project is built entirely with open-source software libraries and publicly available government and satellite datasets, "
        "ensuring the framework can be deployed by district disaster agencies without licensing costs:",
        body_style
    ))

    # Tech Stack Table
    tech_data = [
        [
            Paragraph("<b>Subsystem</b>", tbl_hdr),
            Paragraph("<b>Technologies & Datasets</b>", tbl_hdr),
            Paragraph("<b>Purpose in Project</b>", tbl_hdr),
        ],
        [
            Paragraph("<b>Sensor Ingestion & Backup</b>", tbl_cell),
            Paragraph("Python, Pandas, Requests, Sentinel-3 SAR Altimetry API, NASA GPM IMERG rainfall feeds", tbl_cell),
            Paragraph("Automates sensor polling and triggers satellite backup when ground feeds stop.", tbl_cell),
        ],
        [
            Paragraph("<b>Hydrology & Inundation Core</b>", tbl_cell),
            Paragraph("NumPy, SciPy, SRTM 30m Digital Elevation Model (DEM), CWC River Reach cross-sections", tbl_cell),
            Paragraph("Models downstream wave propagation and maps planar flood depth over terrain.", tbl_cell),
        ],
        [
            Paragraph("<b>Road Network & Routing</b>", tbl_cell),
            Paragraph("OSMnx, NetworkX, OpenStreetMap Road Vectors, Depth-Constrained Dijkstra Graph Search", tbl_cell),
            Paragraph("Ingests road segments and calculates depth-constrained safe routes.", tbl_cell),
        ],
        [
            Paragraph("<b>Alerting & Web Interface</b>", tbl_cell),
            Paragraph("FastAPI, Leaflet.js, OpenStreetMap Tiles, OASIS CAP v1.2 XML generator, Twilio SMS API", tbl_cell),
            Paragraph("Renders live flood map and dispatches regional SMS warnings in local languages.", tbl_cell),
        ],
    ]
    tech_tbl = Table(tech_data, colWidths=[110, 215, 190])
    tech_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(tech_tbl)
    story.append(Spacer(1, 5))

    # Section 6: Team Responsibilities & Work Schedule
    story.append(Paragraph("6. Project Modules & Development Milestones", h1_style))
    
    # Team & Milestones Table
    sched_data = [
        [
            Paragraph("<b>Phase & Timeline</b>", tbl_hdr),
            Paragraph("<b>Key Milestones & Deliverables</b>", tbl_hdr),
            Paragraph("<b>Assigned Module Lead</b>", tbl_hdr),
        ],
        [
            Paragraph("<b>Phase 1: Ingestion & Backup<br/>(Months 1-2)</b>", tbl_cell),
            Paragraph("CWC river sensor API integration, Sentinel-3 SAR data pipeline, and 15-minute polling loop implementation.", tbl_cell),
            Paragraph("<b>[Module 1 Lead / Investigator 1]</b><br/>Sensor data ingestion & failover", tbl_cell),
        ],
        [
            Paragraph("<b>Phase 2: Hydraulics & GIS<br/>(Months 3-4)</b>", tbl_cell),
            Paragraph("Downstream wave celerity calculation, SRTM 30m DEM processing, and road depth intersection algorithm.", tbl_cell),
            Paragraph("<b>[Module 2 Lead / Investigator 2]</b><br/>Hydrologic modeling & GIS depth mapping", tbl_cell),
        ],
        [
            Paragraph("<b>Phase 3: Routing & Shelters<br/>(Months 5-6)</b>", tbl_cell),
            Paragraph("Depth-constrained Dijkstra pathfinding on OSM graph, pedestrian/rescue profile filters, and shelter load balancing.", tbl_cell),
            Paragraph("<b>[Module 3 Lead / Investigator 3]</b><br/>Graph routing & shelter capacity logic", tbl_cell),
        ],
        [
            Paragraph("<b>Phase 4: Alerts & Testing<br/>(Months 7-8)</b>", tbl_cell),
            Paragraph("OASIS CAP v1.2 alert feed, multi-language SMS dispatch, web situational dashboard, and integrated system testing.", tbl_cell),
            Paragraph("<b>[Entire Project Group]</b><br/>Integrated testing & documentation", tbl_cell),
        ],
    ]
    sched_tbl = Table(sched_data, colWidths=[105, 260, 150])
    sched_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(sched_tbl)
    story.append(Spacer(1, 5))

    # Section 7: Expected Impact & Conclusion
    story.append(Paragraph("7. Expected Impact & Conclusion", h1_style))
    story.append(Paragraph(
        "By focusing on the practical challenges observed during mountain flash floods and GLOFs in Uttarakhand, this proposed system offers a realistic solution for early warning "
        "and evacuation. Autonomous satellite radar backup prevents monitoring loss when ground sensors break; predicting downstream river rise gives "
        "families advance notice to evacuate; identifying vulnerable access roads allows rescue teams (NDRF) to stage boats before roads submerge; "
        "and depth-aware navigation prevents fleeing citizens from driving or walking into flooded roads.",
        body_style
    ))
    story.append(Paragraph(
        "The proposed system can serve as an affordable, scalable, and automated disaster management tool for district authorities.",
        body_style
    ))

    # Essential References
    story.append(Paragraph("Key References & Foundational Literature", h2_style))
    refs = [
        "1. Central Water Commission (CWC), Ministry of Jal Shakti, Government of India, <i>'Hydrodynamic Modeling and River Flood Forecasting Guidelines'</i>, 2021.",
        "2. National Disaster Management Authority (NDMA), Government of India, <i>'Common Alerting Protocol (CAP) Implementation Manual for Disaster Warnings (Sachet)'</i>, 2022.",
        "3. Donchyts, G., et al., <i>'High-resolution satellite radar altimetry for inland water monitoring during severe cloud cover'</i>, Remote Sensing of Environment, 2018.",
        "4. OpenStreetMap Contributors & Boeing, G., <i>'OSMnx: New methods for acquiring, constructing, and analyzing complex street networks'</i>, Computers, Environment and Urban Systems, 2017.",
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle('RefStyle', fontName='Helvetica', fontSize=7.2, leading=9.6, textColor=colors.HexColor("#475569"), spaceAfter=2)))

    # Build document
    doc.build(story, canvasmaker=ProposalNumberedCanvas)
    print(f"Successfully generated proposal PDF: {filename}")


if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(__file__), "Project_Idea_Proposal.pdf")
    build_pdf(out_file)
