"""
Master Production Engine: Cinematic Glassmorphic Morph-Driven Presentation Generator (Academic & Engineering Edition)
Generates: presentation/Flash_Flood_Early_Warning_Invention.pptx

Strictly isolated within the presentation/ directory to prevent codebase interference.
"""

from __future__ import annotations

import os
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml import parse_xml

# ==============================================================================
# COLOR PALETTE (Strict Adherence to Specifications)
# ==============================================================================
DEEP_SLATE = RGBColor(0x3A, 0x44, 0x54)      # #3A4454 Primary dark canvas
MUDDY_BROWN = RGBColor(0x5C, 0x4A, 0x3C)     # #5C4A3C Turbulent earth
CLOUD_WHITE = RGBColor(0xF5, 0xF7, 0xFA)     # #F5F7FA Primary text/labels
OFF_WHITE = RGBColor(0xF0, 0xF2, 0xF5)       # #F0F2F5 Light technical canvas
MIDNIGHT_INDIGO = RGBColor(0x1A, 0x2B, 0x4C) # #1A2B4C Deep technical titles
SAFETY_ORANGE = RGBColor(0xFF, 0x6B, 0x35)   # #FF6B35 Emergency / Breach / Alert
WARNING_YELLOW = RGBColor(0xFF, 0xC9, 0x3C)  # #FFC93C Watch / Caution / Redundancy

# Subtle Glass borders and accents
GLASS_BORDER_LIGHT = RGBColor(245, 247, 250)
GLASS_BORDER_DARK = RGBColor(100, 115, 135)
GLASS_CARD_BG = RGBColor(26, 35, 48)         # Deep slate-indigo glass tint

FONT_PRIMARY = "Segoe UI"  # Universally supported on Windows, clean sans-serif

ASSETS_DIR = Path(__file__).parent / "assets"
HERO_FLOOD_IMG = str(ASSETS_DIR / "hero_flash_flood.jpg")
SENSOR_HAZARD_IMG = str(ASSETS_DIR / "sensor_flood_hazard.jpg")
SATELLITE_ORBIT_IMG = str(ASSETS_DIR / "satellite_radar_orbit.jpg")
GIS_AERIAL_IMG = str(ASSETS_DIR / "gis_river_basin_aerial.jpg")

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def inject_morph_transition(slide):
    """Injects PowerPoint OpenXML Morph transition for smooth morphing."""
    morph_xml = (
        '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:p16="http://schemas.microsoft.com/office/powerpoint/2015/09/main" spd="med">'
        '<p16:morph option="byObject"/>'
        '</p:transition>'
    )
    slide._element.append(parse_xml(morph_xml))


def set_shape_alpha(shape, alpha_pct=85):
    """Sets transparency on a shape's solid fill in OpenXML (0-100%)."""
    try:
        spPr = shape.element.spPr
        solidFill = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill')
        if solidFill is not None:
            srgbClr = solidFill.find('{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr')
            if srgbClr is not None:
                for child in list(srgbClr):
                    if child.tag.endswith('alpha'):
                        srgbClr.remove(child)
                alpha_val = int(alpha_pct * 1000)
                alpha_elem = parse_xml(
                    f'<a:alpha xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="{alpha_val}"/>'
                )
                srgbClr.append(alpha_elem)
    except Exception:
        pass


def add_glass_card(
    slide,
    left,
    top,
    width,
    height,
    bg_color=GLASS_CARD_BG,
    border_color=GLASS_BORDER_LIGHT,
    border_width=Pt(1.0),
    alpha_pct=85,
    shape_name=None,
):
    """Creates a glassmorphic card container with rounded corners and controlled padding."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    if shape_name:
        card.name = shape_name
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    set_shape_alpha(card, alpha_pct)

    card.line.color.rgb = border_color
    card.line.width = border_width

    # Adjust rounding radius
    try:
        prstGeom = card.element.spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}prstGeom')
        if prstGeom is not None:
            avLst = prstGeom.find('{http://schemas.openxmlformats.org/drawingml/2006/main}avLst')
            if avLst is not None:
                for gd in list(avLst):
                    avLst.remove(gd)
                gd_elem = parse_xml('<a:gd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="adj" fmla="val 6000"/>')
                avLst.append(gd_elem)
    except Exception:
        pass

    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.24)
    tf.margin_right = Inches(0.24)
    tf.margin_top = Inches(0.20)
    tf.margin_bottom = Inches(0.20)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    return card


def add_dark_canvas_background(slide, color=DEEP_SLATE):
    """Adds a dark slate widescreen background rectangle."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.name = "!!BackgroundCanvas"
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg


def add_header(slide, tag_text: str, title_text: str, is_dark: bool = True):
    """Adds standard clean header conforming to safe margins (left 0.8")."""
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.52), Inches(11.733), Inches(1.2))
    tb.name = "!!SlideHeader"
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    # Tag line
    p_tag = tf.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = FONT_PRIMARY
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    if "CRITICAL" in tag_text or "EMERGENCY" in tag_text or "ALERT" in tag_text:
        p_tag.font.color.rgb = SAFETY_ORANGE
    elif "WATCH" in tag_text or "HAZARD" in tag_text or "VULNERABILITY" in tag_text or "REDUNDANCY" in tag_text:
        p_tag.font.color.rgb = WARNING_YELLOW
    else:
        p_tag.font.color.rgb = RGBColor(160, 180, 205) if is_dark else MIDNIGHT_INDIGO
    p_tag.space_after = Pt(4)

    # Title line
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.name = FONT_PRIMARY
    p_title.font.size = Pt(26)
    p_title.font.bold = True
    p_title.font.color.rgb = CLOUD_WHITE if is_dark else MIDNIGHT_INDIGO


# ==============================================================================
# SLIDE BUILDERS (15 SCENES OF ENGINEERING ARCHITECTURE & FIELD EVALUATION)
# ==============================================================================

def build_slide_01(prs):
    """Slide 01: Title Slide - When The Flood Rises Fast"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Hero flood image full-bleed
    pic = slide.shapes.add_picture(HERO_FLOOD_IMG, 0, 0, width=Inches(13.333), height=Inches(7.5))
    pic.name = "!!RiverBasinLandscape"

    # Dark atmospheric gradient overlay
    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    overlay.name = "!!AtmosphericOverlay"
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = DEEP_SLATE
    overlay.line.fill.background()
    set_shape_alpha(overlay, 45)

    # Main Hero Title Box on the Left
    title_box = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(11.5), Inches(3.2))
    title_box.name = "!!HeroTitleContainer"
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p0 = tf.paragraphs[0]
    p0.text = "RESEARCH & ENGINEERING PROPOSAL"
    p0.font.name = FONT_PRIMARY
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = WARNING_YELLOW
    p0.space_after = Pt(10)

    p1 = tf.add_paragraph()
    p1.text = "WHEN THE FLOOD RISES FAST,\nEVERY MINUTE MATTERS"
    p1.font.name = FONT_PRIMARY
    p1.font.size = Pt(42)
    p1.font.bold = True
    p1.font.color.rgb = CLOUD_WHITE
    p1.space_after = Pt(14)

    p2 = tf.add_paragraph()
    p2.text = "Hydrodynamic Modeling  •  Automated Satellite Backup  •  Depth-Constrained Evacuation"
    p2.font.name = FONT_PRIMARY
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(220, 230, 245)

    # Bottom Glass Telemetry Ribbon
    ribbon = add_glass_card(
        slide, Inches(0.9), Inches(5.7), Inches(11.533), Inches(1.1),
        bg_color=RGBColor(20, 28, 40), alpha_pct=80, shape_name="!!TelemetryRibbon"
    )
    rtf = ribbon.text_frame
    rp = rtf.paragraphs[0]
    rp.text = "TARGET RIVER BASIN: ALAKNANDA & MANDAKINI VALLEY (UTTARAKHAND)   •   SATELLITE FAILOVER LATENCY: 420 MS   •   STATUS: ACTIVE"
    rp.font.name = FONT_PRIMARY
    rp.font.size = Pt(12)
    rp.font.bold = True
    rp.font.color.rgb = CLOUD_WHITE
    rp.space_after = Pt(2)

    rp2 = rtf.add_paragraph()
    rp2.text = "Coupling 1D Saint-Venant hydraulic routing, automated Sentinel-3 radar backup, and profile-aware Dijkstra graph search."
    rp2.font.name = FONT_PRIMARY
    rp2.font.size = Pt(11)
    rp2.font.color.rgb = RGBColor(170, 185, 205)


def build_slide_02(prs):
    """Slide 02: Hazard Analysis - 3 Critical System Blind Spots"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas_background(slide)

    # Photo crop of river gauge hazard
    pic = slide.shapes.add_picture(SENSOR_HAZARD_IMG, Inches(0.8), Inches(1.9), width=Inches(4.5), height=Inches(4.8))
    pic.name = "!!HazardGaugePhoto"

    add_header(slide, "HAZARD ANALYSIS", "THE FLASH-FLOOD REALITY: 3 CRITICAL SYSTEM BLIND SPOTS")

    # Three Glass Cards on Right
    cards_data = [
        ("01", "RAPID ONSET SURGE", "Water levels rise within 15–45 minutes of upstream cloudbursts. Conventional 24-hr numerical forecast models fail to run in time.", WARNING_YELLOW),
        ("02", "TERRESTRIAL SENSOR FAILURE", "Violent river torrents submerge and physically sever riverbank staff gauges, knocking critical telemetry offline during storms.", SAFETY_ORANGE),
        ("03", "DEPTH-BLIND EVACUATION TRAPS", "Standard road navigation lacks floodwater depth awareness, inadvertently routing citizens onto submerged, impassable roadways.", CLOUD_WHITE),
    ]

    card_y = 1.9
    for i, (num, title, desc, accent_col) in enumerate(cards_data):
        card = add_glass_card(
            slide, Inches(5.6), Inches(card_y), Inches(6.9), Inches(1.45),
            bg_color=RGBColor(24, 32, 45), alpha_pct=85, shape_name=f"!!ProblemCard_{num}"
        )
        ctf = card.text_frame
        cp1 = ctf.paragraphs[0]
        cp1.text = f"[{num}]  {title}"
        cp1.font.name = FONT_PRIMARY
        cp1.font.size = Pt(14)
        cp1.font.bold = True
        cp1.font.color.rgb = accent_col
        cp1.space_after = Pt(4)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(11)
        cp2.font.color.rgb = RGBColor(200, 212, 228)

        card_y += 1.65


def build_slide_03(prs):
    """Slide 03: Sensor Vulnerability - Terrestrial Sensor Failure"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas_background(slide)

    add_header(slide, "SENSOR VULNERABILITY", "WHY A SINGLE TERRESTRIAL SENSOR CANNOT BE TRUSTED")

    # 3 Stage Flow: River Gauge -> Communication Link -> Prediction Engine
    stages = [
        ("STAGE 1: RIVER GAUGE", "STN-004 Joshimath Station\nTurbulent Flood Surge Peak\nStatus: SEVERED BY DEBRIS\n\nSensor Type: Physical staff probe\nFailure Cause: Debris impact & silt\nImpact: River stage telemetry lost", Inches(0.8), SAFETY_ORANGE),
        ("STAGE 2: TELEMETRY LINK", "Cellular / LPWAN Link\nContinuous Packet Dropout\nStatus: SIGNAL LOST (TIMEOUT)\n\nProtocol: 4G LTE Uplink / LoRa\nTransmission: Connection severed\nImpact: Telemetry dead-zone", Inches(4.8), WARNING_YELLOW),
        ("STAGE 3: CONVENTIONAL FORECAST", "Hydrodynamic Prediction Core\nMissing River Stage Parameter\nStatus: PREDICTION HALTED\n\nComputation: Model crashes\nLead Time: Zero warning issued\nImpact: Communities blind-sided", Inches(8.8), RGBColor(220, 100, 100)),
    ]

    for title, desc, left_x, status_col in stages:
        c = add_glass_card(
            slide, left_x, Inches(2.0), Inches(3.7), Inches(2.8),
            bg_color=RGBColor(25, 34, 48), alpha_pct=90, shape_name=f"!!FailureStage_{title[:7]}"
        )
        tf = c.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = status_col
        p.space_after = Pt(8)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_PRIMARY
        p2.font.size = Pt(10)
        p2.font.color.rgb = CLOUD_WHITE

    # Diagnostic Banner across bottom
    diag = add_glass_card(
        slide, Inches(0.8), Inches(5.2), Inches(11.733), Inches(1.5),
        bg_color=RGBColor(38, 20, 20), border_color=SAFETY_ORANGE, border_width=Pt(1.5),
        alpha_pct=90, shape_name="!!DiagnosticBanner"
    )
    dtf = diag.text_frame
    dp = dtf.paragraphs[0]
    dp.text = "CRITICAL GAP: TERRESTRIAL SENSOR SUSCEPTIBILITY TO DEBRIS"
    dp.font.name = FONT_PRIMARY
    dp.font.size = Pt(14)
    dp.font.bold = True
    dp.font.color.rgb = SAFETY_ORANGE
    dp.space_after = Pt(4)

    dp2 = dtf.add_paragraph()
    dp2.text = "In conventional early warning setups, losing a river gauge halts flood forecasting completely. Our architecture detects missing telemetry or impossible derivatives within 420 ms, initiating an automated switchover to spaceborne radar altimetry."
    dp2.font.name = FONT_PRIMARY
    dp2.font.size = Pt(11)
    dp2.font.color.rgb = CLOUD_WHITE


def build_slide_04(prs):
    """Slide 04: Sensor Redundancy - Falling Back to Satellite Data"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    
    # Background: Earth observation radar satellite
    pic = slide.shapes.add_picture(SATELLITE_ORBIT_IMG, 0, 0, width=Inches(13.333), height=Inches(7.5))
    pic.name = "!!SatelliteHeroBg"

    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = DEEP_SLATE
    overlay.line.fill.background()
    set_shape_alpha(overlay, 55)

    add_header(slide, "SENSOR REDUNDANCY", "FALLING BACK TO SATELLITE DATA")

    # Left Side: Simple Three-Box Flow Diagram
    panel = add_glass_card(
        slide, Inches(0.8), Inches(1.9), Inches(5.8), Inches(4.8),
        bg_color=RGBColor(18, 25, 38), alpha_pct=88, shape_name="!!FailoverFlowPanel"
    )
    ptf = panel.text_frame
    pp1 = ptf.paragraphs[0]
    pp1.text = "AUTOMATED FAILOVER SEQUENCE"
    pp1.font.name = FONT_PRIMARY
    pp1.font.size = Pt(14)
    pp1.font.bold = True
    pp1.font.color.rgb = WARNING_YELLOW
    pp1.space_after = Pt(12)

    flow_boxes = [
        ("1. GROUND GAUGE TELEMETRY", "Central Water Commission (CWC) river station provides primary water level (h) and discharge (Q) readings at 15-minute polling intervals.", CLOUD_WHITE),
        ("2. FAILOVER TRIPWIRE (420 ms)", "Detection rule: If no gauge reading arrives for 15 minutes, or the rate of rise is physically impossible (Δh/Δt > 1.5 m/min), the system automatically initiates failover.", SAFETY_ORANGE),
        ("3. SENTINEL-3 SAR TAKEOVER", "Sentinel-3 Synthetic Aperture Radar (SAR) altimetry immediately supplies river surface height from orbit, maintaining hydrodynamic model continuity.", RGBColor(120, 190, 255)),
    ]

    for title, desc, col in flow_boxes:
        p_t = ptf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_PRIMARY
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = col
        p_t.space_after = Pt(2)

        p_d = ptf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_PRIMARY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = RGBColor(210, 222, 238)
        p_d.space_after = Pt(10)

    # Right Glass Panel: Technical Explanation (Plain sentences, not marketing bullets)
    panel2 = add_glass_card(
        slide, Inches(6.9), Inches(1.9), Inches(5.6), Inches(4.8),
        bg_color=RGBColor(18, 25, 38), alpha_pct=88, shape_name="!!FailoverExplanationPanel"
    )
    p2tf = panel2.text_frame
    p2p1 = p2tf.paragraphs[0]
    p2p1.text = "WHY SATELLITE RADAR WORKS AS BACKUP"
    p2p1.font.name = FONT_PRIMARY
    p2p1.font.size = Pt(14)
    p2p1.font.bold = True
    p2p1.font.color.rgb = CLOUD_WHITE
    p2p1.space_after = Pt(12)

    reasons = [
        ("Penetrates Heavy Cloud & Rainfall", "Satellite radar altimeters operate in microwave frequencies that penetrate dense monsoon clouds and torrential downpours. Optical satellites and ground cameras are blinded during major storms, but SAR radar measures surface height directly through cloud cover."),
        ("Independent of Ground Infrastructure", "Spaceborne altimetry operates entirely from orbit. A debris strike, embankment washout, local power failure, or cellular tower outage on land has zero impact on orbital radar observations."),
        ("Verified 420 ms Switchover Latency", "The backend polling engine detects sensor loss and rebinds the hydrodynamic boundary condition to Sentinel-3 SAR orbital passes in 420 ms, preventing forecast stalling during active flash-flood emergencies."),
    ]
    for title, body in reasons:
        p_a = p2tf.add_paragraph()
        p_a.text = title
        p_a.font.name = FONT_PRIMARY
        p_a.font.size = Pt(12)
        p_a.font.bold = True
        p_a.font.color.rgb = WARNING_YELLOW
        p_a.space_after = Pt(3)

        p_b = p2tf.add_paragraph()
        p_b.text = body
        p_b.font.name = FONT_PRIMARY
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = RGBColor(210, 220, 235)
        p_b.space_after = Pt(10)


def build_slide_05(prs):
    """Slide 05: Data Ingestion - Three-Tier Sensing Architecture"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas_background(slide)

    add_header(slide, "DATA INGESTION", "THREE-TIER SENSING ARCHITECTURE")

    tiers = [
        ("TIER 1: TERRESTRIAL SENSING", [
            "Central Water Commission (CWC) River Gauges",
            "India Meteorological Dept (IMD) AWS Telemetry",
            "Ground-based Automatic Weather Stations",
            "Sampling Rate: 15-minute polling interval",
            "Telemetry: Water level H, Rain intensity P",
            "Failover: Instant tripwire on sensor drop",
        ], Inches(0.8), RGBColor(120, 180, 240)),
        ("TIER 2: SPACEBORNE RADAR", [
            "Sentinel-3 SAR Radar Altimetry (River Surface)",
            "NASA GPM IMERG Real-Time Satellite Rainfall",
            "Synthetic Aperture Radar (SAR) Constellation",
            "Spatial Resolution: 0.1° gridded precipitation",
            "Cloud Penetration: Dual-frequency radar altimetry",
            "Orbital Tracking: Regular passes over major basins",
        ], Inches(4.8), WARNING_YELLOW),
        ("TIER 3: TOPOGRAPHY & INFRASTRUCTURE", [
            "SRTM 30m Digital Elevation Model (DEM)",
            "ISRIC SoilGrids Antecedent Soil Moisture",
            "OpenStreetMap High-Resolution Road Network",
            "Catchment Gradient & Channel Roughness",
            "Registered Relief Shelter Plinth Elevations",
            "Hydraulic Cross-Sections: Manning's n factors",
        ], Inches(8.8), RGBColor(180, 210, 160)),
    ]

    for title, items, left_x, col in tiers:
        card = add_glass_card(
            slide, left_x, Inches(1.9), Inches(3.7), Inches(3.9),
            bg_color=RGBColor(24, 32, 46), alpha_pct=88, shape_name=f"!!IngestionTier_{title[:6]}"
        )
        ctf = card.text_frame
        cp = ctf.paragraphs[0]
        cp.text = title
        cp.font.name = FONT_PRIMARY
        cp.font.size = Pt(13)
        cp.font.bold = True
        cp.font.color.rgb = col
        cp.space_after = Pt(10)

        for item in items:
            p_i = ctf.add_paragraph()
            p_i.text = f"• {item}"
            p_i.font.name = FONT_PRIMARY
            p_i.font.size = Pt(10)
            p_i.font.color.rgb = CLOUD_WHITE
            p_i.space_after = Pt(5)

    # Ingestion Convergence Banner
    conv = add_glass_card(
        slide, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.9),
        bg_color=RGBColor(18, 25, 36), alpha_pct=90, shape_name="!!ConvergenceBar"
    )
    cv_tf = conv.text_frame
    cv_p = cv_tf.paragraphs[0]
    cv_p.text = "DATA PROVENANCE: Every sensor reading carries full source telemetry and timestamp. Missing or corrupt feeds trigger automated fallback."
    cv_p.font.name = FONT_PRIMARY
    cv_p.font.size = Pt(12)
    cv_p.font.bold = True
    cv_p.font.color.rgb = CLOUD_WHITE


def build_slide_06(prs):
    """Slide 06: Hydrodynamic Modeling - Physics-Based Surge Estimation"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas_background(slide)

    add_header(slide, "HYDRODYNAMIC MODELING", "PHYSICS-BASED SURGE ESTIMATION")

    # Top Half: 2 Equation Cards Side-by-Side (Saint-Venant Celerity and Dynamic Rate-of-Rise)
    c1 = add_glass_card(
        slide, Inches(0.8), Inches(1.9), Inches(5.7), Inches(2.7),
        bg_color=RGBColor(24, 32, 45), alpha_pct=88, shape_name="!!CelerityCard"
    )
    c1_tf = c1.text_frame
    p1 = c1_tf.paragraphs[0]
    p1.text = "1. SAINT-VENANT 1D WAVE CELERITY"
    p1.font.name = FONT_PRIMARY
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = WARNING_YELLOW
    p1.space_after = Pt(6)

    p1_f = c1_tf.add_paragraph()
    p1_f.text = "c = dQ / dA ≈ (5/3) v"
    p1_f.font.name = "Consolas"
    p1_f.font.size = Pt(13)
    p1_f.font.bold = True
    p1_f.font.color.rgb = SAFETY_ORANGE
    p1_f.space_after = Pt(8)

    p1_d = c1_tf.add_paragraph()
    p1_d.text = "Calculates downstream flood-wave propagation velocity along the mountain river channel. At flow velocity v ≈ 4.1 m/s, celerity c ≈ 6.8 m/s, providing critical early warning between upstream Rishiganga and downstream stations."
    p1_d.font.name = FONT_PRIMARY
    p1_d.font.size = Pt(10)
    p1_d.font.color.rgb = RGBColor(215, 225, 240)

    c2 = add_glass_card(
        slide, Inches(6.8), Inches(1.9), Inches(5.7), Inches(2.7),
        bg_color=RGBColor(24, 32, 45), alpha_pct=88, shape_name="!!RateOfRiseCard"
    )
    c2_tf = c2.text_frame
    p2 = c2_tf.paragraphs[0]
    p2.text = "2. DYNAMIC RATE-OF-RISE DERIVATIVE"
    p2.font.name = FONT_PRIMARY
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = WARNING_YELLOW
    p2.space_after = Pt(6)

    p2_f = c2_tf.add_paragraph()
    p2_f.text = "Δh / Δt = (h_t - h_{t-1}) / Δt"
    p2_f.font.name = "Consolas"
    p2_f.font.size = Pt(13)
    p2_f.font.bold = True
    p2_f.font.color.rgb = SAFETY_ORANGE
    p2_f.space_after = Pt(8)

    p2_d = c2_tf.add_paragraph()
    p2_d.text = "Calculates instantaneous water level surge velocity across rolling 15-minute intervals. Detects abrupt cloudburst flood waves while filtering out normal seasonal rising."
    p2_d.font.name = FONT_PRIMARY
    p2_d.font.size = Pt(10)
    p2_d.font.color.rgb = RGBColor(215, 225, 240)

    # Caption folding wave attenuation and soil saturation
    caption = add_glass_card(
        slide, Inches(0.8), Inches(4.75), Inches(11.733), Inches(0.65),
        bg_color=RGBColor(20, 26, 38), alpha_pct=85, shape_name="!!PhysicsCaption"
    )
    cap_tf = caption.text_frame
    cap_p = cap_tf.paragraphs[0]
    cap_p.text = "Catchment Wave Coupling: When antecedent soil saturation Sm ≥ 0.80, infiltration drops sharply, accelerating surface runoff. Downstream flood-wave attenuation is modeled with exponential decay λ = 0.15/hr."
    cap_p.font.name = FONT_PRIMARY
    cap_p.font.size = Pt(10)
    cap_p.font.color.rgb = RGBColor(180, 205, 230)

    # Bottom Left-to-Right Flowchart
    flow = add_glass_card(
        slide, Inches(0.8), Inches(5.55), Inches(11.733), Inches(1.35),
        bg_color=RGBColor(26, 35, 50), border_color=WARNING_YELLOW, border_width=Pt(1.2),
        alpha_pct=90, shape_name="!!PhysicsFlowchart"
    )
    ftf = flow.text_frame
    fp1 = ftf.paragraphs[0]
    fp1.text = "HYDRODYNAMIC PROCESSING SEQUENCE"
    fp1.font.name = FONT_PRIMARY
    fp1.font.size = Pt(11)
    fp1.font.bold = True
    fp1.font.color.rgb = WARNING_YELLOW
    fp1.space_after = Pt(4)

    fp2 = ftf.add_paragraph()
    fp2.text = "Rainfall Influx  →  Soil Saturation Check (Sm ≥ 0.80)  →  Overland Runoff  →  Rate-of-Rise (Δh/Δt)  →  Thresholds: Watch (0.30) | Alert (0.50) | Emergency (0.85 m/hr)"
    fp2.font.name = FONT_PRIMARY
    fp2.font.size = Pt(11)
    fp2.font.bold = True
    fp2.font.color.rgb = CLOUD_WHITE


def build_slide_07(prs):
    """Slide 07: Constraining Machine Learning with Hydraulic Physics"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas_background(slide)

    add_header(slide, "PREDICTION FRAMEWORK", "CONSTRAINING MACHINE LEARNING WITH HYDRAULIC PHYSICS")

    # Left: Physics Domain Card
    left_card = add_glass_card(
        slide, Inches(0.8), Inches(1.9), Inches(5.7), Inches(3.7),
        bg_color=RGBColor(22, 30, 42), border_color=WARNING_YELLOW, border_width=Pt(1.2),
        alpha_pct=88, shape_name="!!PhysicsDomainCard"
    )
    ltf = left_card.text_frame
    lp1 = ltf.paragraphs[0]
    lp1.text = "PHYSICS MODEL: 1D SAINT-VENANT HYDRAULICS"
    lp1.font.name = FONT_PRIMARY
    lp1.font.size = Pt(13)
    lp1.font.bold = True
    lp1.font.color.rgb = WARNING_YELLOW
    lp1.space_after = Pt(8)

    phys_items = [
        "Enforces physical mass and momentum conservation along river channels.",
        "Calculates plausible hydrodynamic bounds for river discharge (Q) and stage (h).",
        "Prevents physically impossible predictions (e.g., negative depths, infinite surge).",
        "Provides deterministic baseline accuracy (NSE = 0.89, RMSE = 0.32 m).",
        "Operates independently of historical training distribution shifts.",
    ]
    for item in phys_items:
        p = ltf.add_paragraph()
        p.text = f"• {item}"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(10.5)
        p.font.color.rgb = CLOUD_WHITE
        p.space_after = Pt(6)

    # Right: ML Domain Card
    right_card = add_glass_card(
        slide, Inches(6.8), Inches(1.9), Inches(5.7), Inches(3.7),
        bg_color=RGBColor(22, 30, 42), border_color=RGBColor(130, 190, 255), border_width=Pt(1.2),
        alpha_pct=88, shape_name="!!MLDomainCard"
    )
    rtf = right_card.text_frame
    rp1 = rtf.paragraphs[0]
    rp1.text = "MACHINE LEARNING: TEMPORAL LSTM PREDICTOR"
    rp1.font.name = FONT_PRIMARY
    rp1.font.size = Pt(13)
    rp1.font.bold = True
    rp1.font.color.rgb = RGBColor(130, 190, 255)
    rp1.space_after = Pt(8)

    ml_items = [
        "Multi-layer LSTM captures complex temporal lag across upstream tributary inflows.",
        "Output is strictly bounded within the Saint-Venant hydraulic search space.",
        "Overcomes pure ML vulnerability to extreme, out-of-distribution cloudburst events.",
        "Achieves superior predictive accuracy (NSE = 0.98, RMSE = 0.16 m).",
        "Delivers 2.5-hour advance lead time with rapid inference suitable for real-time alerts.",
    ]
    for item in ml_items:
        p = rtf.add_paragraph()
        p.text = f"• {item}"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(10.5)
        p.font.color.rgb = CLOUD_WHITE
        p.space_after = Pt(6)

    # Bottom Synthesis Banner: Why Combine Them
    synth = add_glass_card(
        slide, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.2),
        bg_color=RGBColor(35, 45, 62), border_color=SAFETY_ORANGE, border_width=Pt(1.5),
        alpha_pct=92, shape_name="!!HybridSynthesisBanner"
    )
    stf = synth.text_frame
    sp1 = stf.paragraphs[0]
    sp1.text = "WHY WE COMBINED PHYSICS AND MACHINE LEARNING"
    sp1.font.name = FONT_PRIMARY
    sp1.font.size = Pt(12)
    sp1.font.bold = True
    sp1.font.color.rgb = SAFETY_ORANGE
    sp1.space_after = Pt(3)

    sp2 = stf.add_paragraph()
    sp2.text = "In empirical testing, unconstrained ML models gave unrealistic peak stage forecasts during rare cloudburst events (NSE = 0.71, RMSE = 0.84 m). Enforcing 1D Saint-Venant hydraulic constraints anchors predictions to physical laws, raising the Nash-Sutcliffe Efficiency to 0.98 and reducing peak RMSE to 0.16 m."
    sp2.font.name = FONT_PRIMARY
    sp2.font.size = Pt(10.5)
    sp2.font.color.rgb = CLOUD_WHITE


def build_slide_08(prs):
    """Slide 08: Geographic Inundation & Road Water Depth Estimation"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    
    # Background GIS aerial river basin
    pic = slide.shapes.add_picture(GIS_AERIAL_IMG, 0, 0, width=Inches(13.333), height=Inches(7.5))
    pic.name = "!!GISAerialFoundation"

    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = DEEP_SLATE
    overlay.line.fill.background()
    set_shape_alpha(overlay, 50)

    add_header(slide, "INUNDATION MAPPING", "GEOGRAPHIC INUNDATION & ROAD WATER DEPTH ESTIMATION")

    # Left Panel: 4 GIS Layers Flowchart
    panel = add_glass_card(
        slide, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8),
        bg_color=RGBColor(20, 28, 40), alpha_pct=88, shape_name="!!GISLayerStackPanel"
    )
    ptf = panel.text_frame
    pp = ptf.paragraphs[0]
    pp.text = "FOUR-LAYER GIS TRANSFORMATION PIPELINE"
    pp.font.name = FONT_PRIMARY
    pp.font.size = Pt(13)
    pp.font.bold = True
    pp.font.color.rgb = WARNING_YELLOW
    pp.space_after = Pt(10)

    layers = [
        ("LAYER 1: DIGITAL ELEVATION MODEL", "SRTM 30m topographic grid providing terrain elevations and catchment slope vectors."),
        ("LAYER 2: HYDROLOGIC NETWORK", "Central Water Commission mapped river channels, confluences, and drainage paths."),
        ("LAYER 3: PRECIPITATION & INFILTRATION", "NASA GPM real-time satellite rainfall contours coupled with Green-Ampt soil absorption."),
        ("LAYER 4: PLANAR DEPTH OVERLAY", "Projected water elevation surface intersected with local topography to map flood extent."),
    ]
    for l_title, l_desc in layers:
        p1 = ptf.add_paragraph()
        p1.text = l_title
        p1.font.name = FONT_PRIMARY
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = CLOUD_WHITE
        p1.space_after = Pt(2)

        p2 = ptf.add_paragraph()
        p2.text = l_desc
        p2.font.name = FONT_PRIMARY
        p2.font.size = Pt(10)
        p2.font.color.rgb = RGBColor(180, 195, 215)
        p2.space_after = Pt(8)

    # Right Panel: Road Network Intersection & Passability Analysis
    scale_card = add_glass_card(
        slide, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8),
        bg_color=RGBColor(20, 28, 40), alpha_pct=88, shape_name="!!RoadIntersectionCard"
    )
    stf = scale_card.text_frame
    sp = stf.paragraphs[0]
    sp.text = "ROAD NETWORK INTERSECTION & PASSABILITY"
    sp.font.name = FONT_PRIMARY
    sp.font.size = Pt(13)
    sp.font.bold = True
    sp.font.color.rgb = CLOUD_WHITE
    sp.space_after = Pt(10)

    steps = [
        ("OpenStreetMap Network Ingestion", "High-resolution road vectors are extracted and structured as a weighted directed graph across the target river basin."),
        ("Per-Segment Water Depth Estimation", "The computed flood surface is intersected with road geometry, assigning each segment a predicted maximum water depth (d_est)."),
        ("Passability Classification", "Road segments are dynamically classified: dry (<0.05m), citizen passable (<0.15m), high-clearance rescue only (0.15–0.80m), and impassable (>0.80m)."),
        ("Dynamic Graph Edge Weighting", "Edges exceeding vehicle profile depth thresholds receive infinite impedance, ensuring Dijkstra pathfinding routes around submerged corridors."),
    ]
    for s_title, s_desc in steps:
        p1 = stf.add_paragraph()
        p1.text = s_title
        p1.font.name = FONT_PRIMARY
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = WARNING_YELLOW
        p1.space_after = Pt(2)

        p2 = stf.add_paragraph()
        p2.text = s_desc
        p2.font.name = FONT_PRIMARY
        p2.font.size = Pt(10)
        p2.font.color.rgb = RGBColor(190, 205, 225)
        p2.space_after = Pt(8)


def build_slide_09(prs):
    """Slide 09: Surge Detection - Four-Stage Rate-of-Rise Surge Thresholds"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas_background(slide)

    add_header(slide, "SURGE DETECTION", "FOUR-STAGE RATE-OF-RISE SURGE THRESHOLDS")

    cols = [
        ("NORMAL", "< 0.30 m/hr", "River stage rises within baseline seasonal absorption limits. System maintains routine 15-minute telemetry polling and background execution.", RGBColor(100, 210, 140), Inches(0.8)),
        ("WATCH", "≥ 0.30 m/hr", "Upstream surge acceleration detected. District disaster dashboard flags the catchment and alerts field observers to monitor local riverbanks.", WARNING_YELLOW, Inches(3.8)),
        ("ALERT", "≥ 0.50 m/hr", "Rapid water level rise indicates impending bankfull conditions. Emergency responders are placed on standby and candidate shelters are pre-notified.", RGBColor(255, 150, 50), Inches(6.8)),
        ("EMERGENCY", "≥ 0.85 m/hr", "Critical flash-flood surge confirmed. Automated alert dispatch is triggered for public broadcast and evacuation routing without manual delay.", SAFETY_ORANGE, Inches(9.8)),
    ]

    for title, val, desc, col, left_x in cols:
        card = add_glass_card(
            slide, left_x, Inches(1.9), Inches(2.733), Inches(4.8),
            bg_color=RGBColor(24, 32, 45), border_color=col, border_width=Pt(1.5),
            alpha_pct=88, shape_name=f"!!ThresholdCol_{title[:4]}"
        )
        ctf = card.text_frame
        cp = ctf.paragraphs[0]
        cp.text = title
        cp.font.name = FONT_PRIMARY
        cp.font.size = Pt(14)
        cp.font.bold = True
        cp.font.color.rgb = col
        cp.space_after = Pt(8)

        cp_v = ctf.add_paragraph()
        cp_v.text = val
        cp_v.font.name = FONT_PRIMARY
        cp_v.font.size = Pt(22)
        cp_v.font.bold = True
        cp_v.font.color.rgb = CLOUD_WHITE
        cp_v.space_after = Pt(12)

        cp_d = ctf.add_paragraph()
        cp_d.text = desc
        cp_d.font.name = FONT_PRIMARY
        cp_d.font.size = Pt(11)
        cp_d.font.color.rgb = RGBColor(210, 220, 235)


def build_slide_10(prs):
    """Slide 10: Emergency Response - Automated Emergency Alerting"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    
    # Dark Emergency Crimson Canvas
    add_dark_canvas_background(slide, color=RGBColor(35, 15, 18))

    add_header(slide, "EMERGENCY RESPONSE", "AUTOMATED EMERGENCY ALERTING")

    # Top Alert Banner: Plain sentence on trigger conditions
    alert_box = add_glass_card(
        slide, Inches(0.8), Inches(1.9), Inches(11.733), Inches(2.1),
        bg_color=RGBColor(50, 15, 20), border_color=SAFETY_ORANGE, border_width=Pt(2.0),
        alpha_pct=92, shape_name="!!EmergencyTakeoverPanel"
    )
    atf = alert_box.text_frame
    ap = atf.paragraphs[0]
    ap.text = "CRITICAL SURGE THRESHOLDS SIMULTANEOUSLY EXCEEDED"
    ap.font.name = FONT_PRIMARY
    ap.font.size = Pt(15)
    ap.font.bold = True
    ap.font.color.rgb = SAFETY_ORANGE
    ap.space_after = Pt(6)

    ap_metrics = atf.add_paragraph()
    ap_metrics.text = "RATE OF RISE: ≥ 0.85 m/hr   |   SOIL SATURATION: ≥ 80%   |   RAINFALL INTENSITY: ≥ 60 mm/hr"
    ap_metrics.font.name = FONT_PRIMARY
    ap_metrics.font.size = Pt(16)
    ap_metrics.font.bold = True
    ap_metrics.font.color.rgb = CLOUD_WHITE
    ap_metrics.space_after = Pt(8)

    ap_action = atf.add_paragraph()
    ap_action.text = "When rate-of-rise, soil saturation, and rainfall intensity all cross their thresholds at once, the system automatically issues an emergency alert without waiting for manual approval."
    ap_action.font.name = FONT_PRIMARY
    ap_action.font.size = Pt(11.5)
    ap_action.font.color.rgb = RGBColor(230, 205, 205)

    # 2 Parallel Action Cards
    b1 = add_glass_card(
        slide, Inches(0.8), Inches(4.3), Inches(5.7), Inches(2.5),
        bg_color=RGBColor(30, 18, 22), border_color=SAFETY_ORANGE, border_width=Pt(1.2),
        alpha_pct=90, shape_name="!!ActionBranchBroadcast"
    )
    b1_tf = b1.text_frame
    b1_p = b1_tf.paragraphs[0]
    b1_p.text = "ACTION 1: MULTI-CHANNEL PUBLIC WARNING"
    b1_p.font.name = FONT_PRIMARY
    b1_p.font.size = Pt(13)
    b1_p.font.bold = True
    b1_p.font.color.rgb = SAFETY_ORANGE
    b1_p.space_after = Pt(6)

    b1_items = [
        "Generates standardized OASIS Common Alerting Protocol (CAP v1.2) XML payload.",
        "Dispatches cellular SMS warnings in 7 regional languages to vulnerable blocks.",
        "Actuates bilingual audible siren announcements (English & Hindi) at station kiosks.",
    ]
    for item in b1_items:
        p = b1_tf.add_paragraph()
        p.text = f"• {item}"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(10.5)
        p.font.color.rgb = CLOUD_WHITE
        p.space_after = Pt(4)

    b2 = add_glass_card(
        slide, Inches(6.8), Inches(4.3), Inches(5.7), Inches(2.5),
        bg_color=RGBColor(30, 18, 22), border_color=WARNING_YELLOW, border_width=Pt(1.2),
        alpha_pct=90, shape_name="!!ActionBranchEvacuation"
    )
    b2_tf = b2.text_frame
    b2_p = b2_tf.paragraphs[0]
    b2_p.text = "ACTION 2: PROFILE-AWARE EVACUATION ROUTING"
    b2_p.font.name = FONT_PRIMARY
    b2_p.font.size = Pt(13)
    b2_p.font.bold = True
    b2_p.font.color.rgb = WARNING_YELLOW
    b2_p.space_after = Pt(6)

    b2_items = [
        "Initiates depth-constrained Dijkstra pathfinding across the OpenStreetMap road graph.",
        "Calculates separate, safe corridors for pedestrians (<0.15m) and rescue vehicles (≤0.80m).",
        "Dynamically allocates evacuees toward verified high-ground relief shelters (≥29.5m MSL).",
    ]
    for item in b2_items:
        p = b2_tf.add_paragraph()
        p.text = f"• {item}"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(10.5)
        p.font.color.rgb = CLOUD_WHITE
        p.space_after = Pt(4)


def build_slide_11(prs):
    """Slide 11: Alert Dissemination - Multi-Channel Emergency Alert Broadcast"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas_background(slide)

    add_header(slide, "ALERT DISSEMINATION", "MULTI-CHANNEL EMERGENCY ALERT BROADCAST")

    channels = [
        ("STANDARDIZED CAP v1.2 ALERT", "Machine-readable alert payload compliant with National Disaster Management Authority (NDMA Sachet) standard portal.", [
            "Severity: Extreme | Urgency: Immediate",
            "Contains affected coordinate polygon",
            "Includes recommended protective actions",
        ], Inches(0.8), SAFETY_ORANGE),
        ("SMS IN 7 REGIONAL LANGUAGES", "Cellular text dispatch reaching communities without smartphones or mobile internet connectivity.", [
            "Hindi, Garhwali, Kumaoni, Jaunsari",
            "Sylheti, Hindi, and English",
            "Prioritized by cell tower proximity",
        ], Inches(4.8), WARNING_YELLOW),
        ("BILINGUAL AUDIO SIREN", "Local station audio evacuation siren with synthesized voice announcements for community assembly points.", [
            "Dual-language audio: English & Hindi",
            "Clear verbal evacuation instructions",
            "Synchronized countdown for local teams",
        ], Inches(8.8), RGBColor(120, 190, 255)),
    ]

    for title, desc, bullets, left_x, col in channels:
        card = add_glass_card(
            slide, left_x, Inches(1.9), Inches(3.7), Inches(3.0),
            bg_color=RGBColor(24, 32, 45), border_color=col, border_width=Pt(1.2),
            alpha_pct=88, shape_name=f"!!BroadcastCard_{title[:6]}"
        )
        ctf = card.text_frame
        cp = ctf.paragraphs[0]
        cp.text = title
        cp.font.name = FONT_PRIMARY
        cp.font.size = Pt(12.5)
        cp.font.bold = True
        cp.font.color.rgb = col
        cp.space_after = Pt(6)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(10)
        cp2.font.color.rgb = CLOUD_WHITE
        cp2.space_after = Pt(8)

        for b in bullets:
            cp_b = ctf.add_paragraph()
            cp_b.text = f"• {b}"
            cp_b.font.name = FONT_PRIMARY
            cp_b.font.size = Pt(9.5)
            cp_b.font.color.rgb = RGBColor(180, 205, 230)
            cp_b.space_after = Pt(3)

    # Bottom Parallel Dissemination Flowchart
    flow = add_glass_card(
        slide, Inches(0.8), Inches(5.2), Inches(11.733), Inches(1.6),
        bg_color=RGBColor(18, 25, 38), border_color=SAFETY_ORANGE, border_width=Pt(1.4),
        alpha_pct=90, shape_name="!!DisseminationFlowchart"
    )
    ftf = flow.text_frame
    fp1 = ftf.paragraphs[0]
    fp1.text = "PARALLEL ALERT DISSEMINATION PIPELINE"
    fp1.font.name = FONT_PRIMARY
    fp1.font.size = Pt(12)
    fp1.font.bold = True
    fp1.font.color.rgb = SAFETY_ORANGE
    fp1.space_after = Pt(4)

    fp2 = ftf.add_paragraph()
    fp2.text = "Flood Surge Detected  →  CAP v1.2 Payload Generated  →  Concurrent Broadcast: [ NDMA Sachet Portal  |  Regional Cellular SMS  |  Local Audio Siren & Dashboard ]"
    fp2.font.name = FONT_PRIMARY
    fp2.font.size = Pt(11)
    fp2.font.bold = True
    fp2.font.color.rgb = CLOUD_WHITE
    fp2.space_after = Pt(4)

    fp3 = ftf.add_paragraph()
    fp3.text = "All three dissemination channels execute concurrently in under 2 seconds, ensuring warnings reach both official response coordination portals and offline rural residents."
    fp3.font.name = FONT_PRIMARY
    fp3.font.size = Pt(10)
    fp3.font.color.rgb = RGBColor(190, 210, 235)


def build_slide_12(prs):
    """Slide 12: Safe Routing - Profile-Aware Evacuation Routing"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    
    # Aerial GIS background
    pic = slide.shapes.add_picture(GIS_AERIAL_IMG, 0, 0, width=Inches(13.333), height=Inches(7.5))
    pic.name = "!!GISAerialEvac"

    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = DEEP_SLATE
    overlay.line.fill.background()
    set_shape_alpha(overlay, 55)

    add_header(slide, "SAFE ROUTING", "PROFILE-AWARE EVACUATION ROUTING")

    profiles = [
        ("CITIZEN / PEDESTRIAN", "DEPTH LIMIT: < 0.15 m", "Re-routes around flooded dips and submerged underpasses. Strictly guides pedestrians along elevated dry ridges to prevent water entrapment.", CLOUD_WHITE),
        ("FAMILY VEHICLE / CAR", "DEPTH LIMIT: < 0.30 m", "Allows transit through minor road ponding while strictly avoiding water depths that exceed standard exhaust and engine intake heights.", WARNING_YELLOW),
        ("NDRF RESCUE TRUCK", "DEPTH LIMIT: ≤ 0.80 m", "Permits heavy high-clearance rescue vehicles to navigate shallow flooded corridors, reducing travel time to isolated neighborhoods.", SAFETY_ORANGE),
    ]

    for p_title, p_limit, p_desc, col, left_x in [
        (profiles[0][0], profiles[0][1], profiles[0][2], profiles[0][3], Inches(0.8)),
        (profiles[1][0], profiles[1][1], profiles[1][2], profiles[1][3], Inches(4.8)),
        (profiles[2][0], profiles[2][1], profiles[2][2], profiles[2][3], Inches(8.8)),
    ]:
        card = add_glass_card(
            slide, left_x, Inches(1.9), Inches(3.7), Inches(3.2),
            bg_color=RGBColor(20, 28, 42), border_color=col, border_width=Pt(1.5),
            alpha_pct=90, shape_name=f"!!EvacProfile_{p_title[:7]}"
        )
        ctf = card.text_frame
        cp = ctf.paragraphs[0]
        cp.text = p_title
        cp.font.name = FONT_PRIMARY
        cp.font.size = Pt(13)
        cp.font.bold = True
        cp.font.color.rgb = col
        cp.space_after = Pt(4)

        cp_lim = ctf.add_paragraph()
        cp_lim.text = p_limit
        cp_lim.font.name = FONT_PRIMARY
        cp_lim.font.size = Pt(12)
        cp_lim.font.bold = True
        cp_lim.font.color.rgb = col
        cp_lim.space_after = Pt(8)

        cp_d = ctf.add_paragraph()
        cp_d.text = p_desc
        cp_d.font.name = FONT_PRIMARY
        cp_d.font.size = Pt(10)
        cp_d.font.color.rgb = RGBColor(210, 222, 238)

    # Bottom Benchmark Ribbon (Citing measured proposal numbers)
    bench = add_glass_card(
        slide, Inches(0.8), Inches(5.35), Inches(11.733), Inches(1.5),
        bg_color=RGBColor(18, 25, 38), border_color=WARNING_YELLOW, border_width=Pt(1.2),
        alpha_pct=90, shape_name="!!DijkstraBenchmarkRibbon"
    )
    btf = bench.text_frame
    bp1 = btf.paragraphs[0]
    bp1.text = "DIJKSTRA GRAPH ROUTING BENCHMARK (248,512 OSM EDGES)"
    bp1.font.name = FONT_PRIMARY
    bp1.font.size = Pt(12)
    bp1.font.bold = True
    bp1.font.color.rgb = WARNING_YELLOW
    bp1.space_after = Pt(4)

    bp2 = btf.add_paragraph()
    bp2.text = "Query Latency: 194 ms ± 22 ms per request   |   Safe Route Discovery Rate: 99.4%   |   Graph Size: 248,512 edges"
    bp2.font.name = FONT_PRIMARY
    bp2.font.size = Pt(13)
    bp2.font.bold = True
    bp2.font.color.rgb = CLOUD_WHITE
    bp2.space_after = Pt(4)

    bp3 = btf.add_paragraph()
    bp3.text = "Evaluated across 1,000 simulated trips in the target river basin. The engine assigns infinite impedance (cost = ∞) to edges exceeding the profile depth threshold, ensuring robust detour calculation in sub-second time."
    bp3.font.name = FONT_PRIMARY
    bp3.font.size = Pt(10)
    bp3.font.color.rgb = RGBColor(190, 210, 235)


def build_slide_13(prs):
    """Slide 13: Relief Operations - High-Ground Shelter Selection & Occupancy Tracking"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas_background(slide)

    add_header(slide, "RELIEF OPERATIONS", "HIGH-GROUND SHELTER SELECTION & OCCUPANCY TRACKING")

    # Top Half: 4-Step Verification Flowchart
    flow_steps = [
        ("1. CANDIDATE REGISTRY", "Official district disaster shelters, public schools, and elevated community halls identified from registry.", Inches(0.8), CLOUD_WHITE),
        ("2. ELEVATION FILTER", "Plinth elevation must exceed projected maximum flood stage (plinth elevation ≥ 29.5 m MSL).", Inches(3.8), WARNING_YELLOW),
        ("3. ACCESS ROAD CHECK", "At least one ingress road connection must remain dry (water depth < 0.15 m) throughout surge.", Inches(6.8), RGBColor(255, 150, 50)),
        ("4. VERIFIED SAFE SHELTER", "Only facilities passing both elevation and access road verification are approved for routing.", Inches(9.8), RGBColor(100, 220, 150)),
    ]

    for title, desc, left_x, col in flow_steps:
        card = add_glass_card(
            slide, left_x, Inches(1.9), Inches(2.733), Inches(2.8),
            bg_color=RGBColor(24, 32, 46), border_color=col, border_width=Pt(1.2),
            alpha_pct=88, shape_name=f"!!ShelterStep_{title[:4]}"
        )
        ctf = card.text_frame
        cp = ctf.paragraphs[0]
        cp.text = title
        cp.font.name = FONT_PRIMARY
        cp.font.size = Pt(12)
        cp.font.bold = True
        cp.font.color.rgb = col
        cp.space_after = Pt(6)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(10)
        cp2.font.color.rgb = RGBColor(210, 222, 238)

    # Bottom Half: Shelter Capacity & Real-Time Flow Balancing (Matching dashboard figures)
    cap_card = add_glass_card(
        slide, Inches(0.8), Inches(4.95), Inches(11.733), Inches(1.9),
        bg_color=RGBColor(20, 28, 40), border_color=WARNING_YELLOW, border_width=Pt(1.2),
        alpha_pct=90, shape_name="!!ShelterCapacityBar"
    )
    ctf2 = cap_card.text_frame
    cp2_1 = ctf2.paragraphs[0]
    cp2_1.text = "REAL-TIME SHELTER CAPACITY & DYNAMIC RE-ROUTING"
    cp2_1.font.name = FONT_PRIMARY
    cp2_1.font.size = Pt(13)
    cp2_1.font.bold = True
    cp2_1.font.color.rgb = WARNING_YELLOW
    cp2_1.space_after = Pt(6)

    cp2_2 = ctf2.add_paragraph()
    cp2_2.text = "Joshimath Shelter: 72% Capacity (Operational)   |   Pipalkoti High School: 65% Capacity (Operational)\nChamoli Regional Camp: 88% Capacity (Near Limit)   |   Rudraprayag Relief Enclave: 30% Capacity (Open)"
    cp2_2.font.name = FONT_PRIMARY
    cp2_2.font.size = Pt(11)
    cp2_2.font.bold = True
    cp2_2.font.color.rgb = CLOUD_WHITE
    cp2_2.space_after = Pt(6)

    cp2_3 = ctf2.add_paragraph()
    cp2_3.text = "Dynamic Load Balancing: When a shelter approaches 85% capacity (e.g. Chamoli at 88%), the routing engine automatically redirects incoming evacuee groups to the nearest alternative safe shelter, preventing facility overcrowding."
    cp2_3.font.name = FONT_PRIMARY
    cp2_3.font.size = Pt(10)
    cp2_3.font.color.rgb = RGBColor(190, 210, 235)


def build_slide_14(prs):
    """Slide 14: Data Validation - Field Report Cross-Verification"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas_background(slide)

    add_header(slide, "DATA VALIDATION", "FIELD REPORT CROSS-VERIFICATION")

    steps = [
        ("1. CITIZEN FIELD REPORT", "Volunteers and local residents submit water level observations via mobile web form, capturing GPS location, timestamp, and photograph.", [
            "Local geotagged coordinate",
            "Observed water depth estimate",
            "Timestamped field photograph",
        ], Inches(0.8)),
        ("2. SENSOR CROSS-CHECK", "The system cross-references reported depth against the nearest CWC river gauge (within 5 km) and Sentinel-3 radar trend.", [
            "Proximity gauge correlation",
            "Satellite radar trend check",
            "Filters impossible surge rates",
        ], Inches(4.8)),
        ("3. SITUATIONAL MAP UPDATE", "Corroborated reports update the live district flood map with verified status. Uncorroborated submissions are held for review.", [
            "Calibrates local depth layer",
            "Flags localized drainage blocks",
            "Prevents false panic rumors",
        ], Inches(8.8)),
    ]

    for title, desc, bullets, left_x in steps:
        card = add_glass_card(
            slide, left_x, Inches(1.9), Inches(3.7), Inches(3.2),
            bg_color=RGBColor(24, 32, 46), border_color=RGBColor(120, 160, 200), border_width=Pt(1.2),
            alpha_pct=88, shape_name=f"!!ValidationStep_{title[:4]}"
        )
        ctf = card.text_frame
        cp = ctf.paragraphs[0]
        cp.text = title
        cp.font.name = FONT_PRIMARY
        cp.font.size = Pt(13)
        cp.font.bold = True
        cp.font.color.rgb = WARNING_YELLOW
        cp.space_after = Pt(6)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(10)
        cp2.font.color.rgb = CLOUD_WHITE
        cp2.space_after = Pt(8)

        for b in bullets:
            cp_b = ctf.add_paragraph()
            cp_b.text = f"• {b}"
            cp_b.font.name = FONT_PRIMARY
            cp_b.font.size = Pt(9.5)
            cp_b.font.color.rgb = RGBColor(170, 200, 230)
            cp_b.space_after = Pt(3)

    # Bottom Summary Card
    sec = add_glass_card(
        slide, Inches(0.8), Inches(5.35), Inches(11.733), Inches(1.5),
        bg_color=RGBColor(18, 26, 38), border_color=SAFETY_ORANGE, border_width=Pt(1.2),
        alpha_pct=90, shape_name="!!ValidationSummaryBanner"
    )
    stf = sec.text_frame
    sp1 = stf.paragraphs[0]
    sp1.text = "GROUND-TRUTH VALIDATION WITHOUT FALSE ALARMS"
    sp1.font.name = FONT_PRIMARY
    sp1.font.size = Pt(12)
    sp1.font.bold = True
    sp1.font.color.rgb = SAFETY_ORANGE
    sp1.space_after = Pt(4)

    sp2 = stf.add_paragraph()
    sp2.text = "Crowdsourced reports fill observational gaps in un-gauged micro-tributaries, but uncorroborated submissions cannot directly trigger public alarms. By validating citizen inputs against physical river gauges and radar altimetry, the system maintains high data reliability while benefiting from on-the-ground volunteer reporting."
    sp2.font.name = FONT_PRIMARY
    sp2.font.size = Pt(10.5)
    sp2.font.color.rgb = CLOUD_WHITE


def build_slide_15(prs):
    """Slide 15: System Summary - End-to-End Early Warning & Evacuation Workflow"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    
    # Return to Hero Flash Flood Image (Full Circle Narrative)
    pic = slide.shapes.add_picture(HERO_FLOOD_IMG, 0, 0, width=Inches(13.333), height=Inches(7.5))
    pic.name = "!!RiverBasinLandscape"

    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    overlay.name = "!!AtmosphericOverlay"
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = DEEP_SLATE
    overlay.line.fill.background()
    set_shape_alpha(overlay, 55)

    add_header(slide, "SYSTEM SUMMARY", "END-TO-END EARLY WARNING & EVACUATION WORKFLOW")

    milestones = [
        ("INGESTION", "CWC Gauges + IMD AWS + Sentinel-3 SAR Altimetry", "Multi-source telemetry with 420 ms automated failover to spaceborne radar if ground gauges drop offline."),
        ("HYDRAULICS", "1D Saint-Venant Routing + Dynamic Rate-of-Rise", "Downstream wave celerity (c ≈ 5.3 m/s) and rolling rate-of-rise derivative detect sudden cloudburst surges."),
        ("PREDICTION", "Physics-Constrained LSTM + GIS Road Depth", "Neural network bounded by hydraulic mass conservation predicts water depth across the road network."),
        ("ALERTING", "Standardized CAP v1.2 + 7-Language SMS", "Automated broadcast delivers OASIS CAP v1.2 XML feeds, regional text messages, and audible sirens in <2s."),
        ("EVACUATION", "Profile-Aware Dijkstra to Safe Shelters", "Sub-second pathfinding (194 ms) guides citizens and rescue vehicles along dry routes to verified high ground."),
    ]

    card_width = 2.15
    start_x = 0.8
    for i, (m_title, m_tech, m_desc) in enumerate(milestones):
        card = add_glass_card(
            slide, Inches(start_x), Inches(2.1), Inches(card_width), Inches(3.3),
            bg_color=RGBColor(20, 28, 42), border_color=SAFETY_ORANGE if i == 4 else WARNING_YELLOW,
            border_width=Pt(1.4), alpha_pct=90, shape_name=f"!!LoopMilestone_{i}"
        )
        ctf = card.text_frame
        cp = ctf.paragraphs[0]
        cp.text = f"0{i+1}\n{m_title}"
        cp.font.name = FONT_PRIMARY
        cp.font.size = Pt(13)
        cp.font.bold = True
        cp.font.color.rgb = SAFETY_ORANGE if i == 4 else WARNING_YELLOW
        cp.space_after = Pt(4)

        cp2 = ctf.add_paragraph()
        cp2.text = m_tech
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(9.5)
        cp2.font.bold = True
        cp2.font.color.rgb = RGBColor(160, 205, 235)
        cp2.space_after = Pt(6)

        cp3 = ctf.add_paragraph()
        cp3.text = m_desc
        cp3.font.name = FONT_PRIMARY
        cp3.font.size = Pt(9)
        cp3.font.color.rgb = CLOUD_WHITE

        start_x += 2.4

    # Final Summary Glass Panel
    summary = add_glass_card(
        slide, Inches(0.8), Inches(5.7), Inches(11.733), Inches(1.2),
        bg_color=RGBColor(16, 22, 34), alpha_pct=92, shape_name="!!FinalSummaryPanel"
    )
    stf = summary.text_frame
    sp = stf.paragraphs[0]
    sp.text = "CLOSED-LOOP DISASTER RISK REDUCTION ARCHITECTURE"
    sp.font.name = FONT_PRIMARY
    sp.font.size = Pt(13)
    sp.font.bold = True
    sp.font.color.rgb = CLOUD_WHITE
    sp.space_after = Pt(2)

    sp2 = stf.add_paragraph()
    sp2.text = "An integrated engineering pipeline connecting physical river monitoring, automated satellite redundancy, standardized public alerts, and real-time evacuation routing to reduce flash-flood casualties."
    sp2.font.name = FONT_PRIMARY
    sp2.font.size = Pt(10.5)
    sp2.font.color.rgb = RGBColor(180, 200, 225)


# ==============================================================================
# MAIN COMPILATION ENTRYPOINT
# ==============================================================================

def main():
    prs = pptx.Presentation()
    # 16:9 Widescreen standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    print("Compiling 15-Scene Morph-Driven Presentation Deck...")
    build_slide_01(prs)
    build_slide_02(prs)
    build_slide_03(prs)
    build_slide_04(prs)
    build_slide_05(prs)
    build_slide_06(prs)
    build_slide_07(prs)
    build_slide_08(prs)
    build_slide_09(prs)
    build_slide_10(prs)
    build_slide_11(prs)
    build_slide_12(prs)
    build_slide_13(prs)
    build_slide_14(prs)
    build_slide_15(prs)

    output_path = Path(__file__).parent / "Flash_Flood_Early_Warning_Invention.pptx"
    prs.save(str(output_path))
    print(f"Successfully generated: {output_path}")


if __name__ == "__main__":
    main()
