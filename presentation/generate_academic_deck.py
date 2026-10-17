"""
Academic Presentation Generator: Plain-Language Engineering Deck
Title: Flash Flood Prediction, Early Warning, and Safe Evacuation System
Focus: What is the problem, and how are we solving it? (Non-technical, authentic, clear)

# Authors: [Undergraduate Major Project Student Group / Candidate Names]
# Supervisors: [Faculty Supervisor & Guide Committee]
Session: 2026–2027

Produces: presentation/Flash_Flood_Research_Paper_Presentation.pptx
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
# COLOR PALETTE (Clean, high-contrast, professional palette)
# ==============================================================================
DEEP_SLATE = RGBColor(0x1E, 0x26, 0x34)      # Primary background
DARK_NAVY = RGBColor(0x14, 0x1C, 0x28)       # Deep container background
CLOUD_WHITE = RGBColor(0xF8, 0xFA, 0xFC)     # Primary text
MUTED_BLUE = RGBColor(0xCB, 0xD5, 0xE1)      # Body text
ACCENT_BLUE = RGBColor(0x38, 0xBD, 0xF8)     # System features / Info
SAFETY_ORANGE = RGBColor(0xFF, 0x6B, 0x35)   # Flood alert / Hazard / Rescuer
WARNING_YELLOW = RGBColor(0xFF, 0xC9, 0x3C)  # Caution / Shelter / Warning
SUCCESS_GREEN = RGBColor(0x10, 0xB9, 0x81)   # Safe / Normal / Solved

# Card styling
CARD_BG = RGBColor(27, 36, 48)
CARD_BORDER = RGBColor(70, 85, 105)

FONT_PRIMARY = "Segoe UI"

ASSETS_DIR = Path(__file__).parent / "assets"
HERO_FLOOD_IMG = str(ASSETS_DIR / "hero_flash_flood.jpg")
SENSOR_HAZARD_IMG = str(ASSETS_DIR / "sensor_flood_hazard.jpg")
GIS_AERIAL_IMG = str(ASSETS_DIR / "gis_river_basin_aerial.jpg")

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def inject_morph_transition(slide):
    """Adds smooth slide transition."""
    morph_xml = (
        '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:p16="http://schemas.microsoft.com/office/powerpoint/2015/09/main" spd="med">'
        '<p16:morph option="byObject"/>'
        '</p:transition>'
    )
    slide._element.append(parse_xml(morph_xml))


def set_shape_alpha(shape, alpha_pct=88):
    """Sets transparency on a solid fill shape."""
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


def add_dark_canvas(slide, color=DEEP_SLATE):
    """Adds full 16:9 dark background canvas."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.name = "!!CanvasBackground"
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg


def add_card(
    slide,
    left,
    top,
    width,
    height,
    bg_color=CARD_BG,
    border_color=CARD_BORDER,
    border_width=Pt(1.2),
    alpha_pct=90,
    shape_name=None,
):
    """Creates a rounded card container with comfortable padding."""
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
                gd_elem = parse_xml('<a:gd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="adj" fmla="val 4500"/>')
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


def add_header(slide, tag: str, title: str):
    """Creates standard clean slide title and topic label."""
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.50), Inches(11.733), Inches(1.15))
    tb.name = "!!HeaderTextBox"
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_tag = tf.paragraphs[0]
    p_tag.text = tag.upper()
    p_tag.font.name = FONT_PRIMARY
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    if "PROBLEM" in tag or "ALERT" in tag or "HAZARD" in tag:
        p_tag.font.color.rgb = SAFETY_ORANGE
    elif "RESCUER" in tag or "PREDICTION" in tag or "WARNING" in tag:
        p_tag.font.color.rgb = WARNING_YELLOW
    elif "SOLUTION" in tag or "EVACUATION" in tag or "SHELTER" in tag or "RESULTS" in tag:
        p_tag.font.color.rgb = ACCENT_BLUE
    else:
        p_tag.font.color.rgb = RGBColor(160, 180, 205)
    p_tag.space_after = Pt(4)

    p_title = tf.add_paragraph()
    p_title.text = title
    p_title.font.name = FONT_PRIMARY
    p_title.font.size = Pt(26)
    p_title.font.bold = True
    p_title.font.color.rgb = CLOUD_WHITE


# ==============================================================================
# SLIDE BUILDERS (WHAT IS THE PROBLEM & HOW WE SOLVE IT)
# ==============================================================================

def build_slide_01(prs):
    """Slide 01: Title Slide - Authentic Academic Defense"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Hero Background
    pic = slide.shapes.add_picture(HERO_FLOOD_IMG, 0, 0, width=Inches(13.333), height=Inches(7.5))
    pic.name = "!!HeroPic"

    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = DARK_NAVY
    overlay.line.fill.background()
    set_shape_alpha(overlay, 55)

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(3.4))
    title_box.name = "!!TitleBox"
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p0 = tf.paragraphs[0]
    p0.text = "FINAL YEAR MAJOR PROJECT PRESENTATION • SESSION 2026–2027"
    p0.font.name = FONT_PRIMARY
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = WARNING_YELLOW
    p0.space_after = Pt(8)

    p1 = tf.add_paragraph()
    p1.text = "Flash Flood Early Warning, Rescuer Assistance,\nand Safe Evacuation Routing System"
    p1.font.name = FONT_PRIMARY
    p1.font.size = Pt(34)
    p1.font.bold = True
    p1.font.color.rgb = CLOUD_WHITE
    p1.space_after = Pt(12)

    p2 = tf.add_paragraph()
    p2.text = "Helping communities reach government relief shelters safely and assisting rescue teams before roads are cut off"
    p2.font.name = FONT_PRIMARY
    p2.font.size = Pt(16)
    p2.font.color.rgb = ACCENT_BLUE

    # Authors Card
    card = add_card(
        slide, Inches(0.8), Inches(5.0), Inches(11.733), Inches(1.8),
        bg_color=RGBColor(18, 26, 38), border_color=ACCENT_BLUE, border_width=Pt(1.2),
        alpha_pct=92, shape_name="!!MetaCard"
    )
    ctf = card.text_frame
    
    cp1 = ctf.paragraphs[0]
    cp1.text = "STUDENT INVESTIGATORS:"
    cp1.font.name = FONT_PRIMARY
    cp1.font.size = Pt(11)
    cp1.font.bold = True
    cp1.font.color.rgb = WARNING_YELLOW
    cp1.space_after = Pt(2)

    cp2 = ctf.add_paragraph()
    cp2.text = "[Undergraduate Major Project Student Group / Candidate Names & Roll Numbers]"
    cp2.font.name = FONT_PRIMARY
    cp2.font.size = Pt(13)
    cp2.font.bold = True
    cp2.font.color.rgb = CLOUD_WHITE
    cp2.space_after = Pt(6)

    cp3 = ctf.add_paragraph()
    cp3.text = "Department of Computer Science & Engineering\nProject Guide: [Faculty Project Guide / Supervisor, Department of Computer Science & Engineering]\nTarget Focus Area: Alaknanda & Bhagirathi River Basins (Uttarakhand)"
    cp3.font.name = FONT_PRIMARY
    cp3.font.size = Pt(10)
    cp3.font.color.rgb = MUTED_BLUE


def build_slide_02(prs):
    """Slide 02: What are the Real Problems?"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "THE PROBLEM", "WHAT GOES WRONG DURING FLASH FLOODS?")

    # Left: Real Photo
    pic = slide.shapes.add_picture(SENSOR_HAZARD_IMG, Inches(0.8), Inches(1.9), width=Inches(4.2), height=Inches(4.9))
    pic.name = "!!HazardPhoto"

    # Right: 3 Clear Real-World Problems
    problems = [
        ("1. Water Rises Fast Without Enough Warning", "Heavy rain in the hills causes rivers to rise rapidly. Because water moves so quickly, people living downstream often don't get warned in time to pack essential belongings and evacuate safely.", WARNING_YELLOW),
        ("2. Ground Sensors Often Break in Severe Storms", "River gauges installed on riverbanks are easily damaged or washed away by floating logs, mud, and fast currents. When the sensors break, officials lose real-time visibility right when they need it most.", SAFETY_ORANGE),
        ("3. People and Rescuers Get Trapped on Flooded Roads", "Standard maps and GPS apps only look at normal traffic. During floods, they direct people onto low roads and bridges that are already underwater. Meanwhile, rescue teams don't know which roads are cut off until they get stuck.", ACCENT_BLUE),
    ]

    card_y = 1.9
    for title, desc, col in problems:
        c = add_card(
            slide, Inches(5.3), Inches(card_y), Inches(7.233), Inches(1.5),
            bg_color=CARD_BG, border_color=col, border_width=Pt(1.2),
            shape_name=f"!!ProbCard_{title[:2]}"
        )
        ctf = c.text_frame
        cp1 = ctf.paragraphs[0]
        cp1.text = title
        cp1.font.name = FONT_PRIMARY
        cp1.font.size = Pt(13)
        cp1.font.bold = True
        cp1.font.color.rgb = col
        cp1.space_after = Pt(4)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(10.5)
        cp2.font.color.rgb = MUTED_BLUE

        card_y += 1.7


def build_slide_03(prs):
    """Slide 03: How Are We Solving It? (System Overview)"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "OUR SOLUTION", "HOW OUR SYSTEM SOLVES THESE PROBLEMS")

    steps = [
        ("STEP 1: SENSORS & BACKUP", "Reads ground river gauges every 15 minutes. If a ground sensor gets damaged, the system automatically uses satellite radar from orbit to keep measuring water height.", Inches(0.8), WARNING_YELLOW),
        ("STEP 2: FLOOD PREDICTION", "Calculates how fast water is moving downstream from upstream rain. This gives downstream towns 2 to 2.5 hours of advance warning before water crests.", Inches(3.8), ACCENT_BLUE),
        ("STEP 3: MAPPING FLOODED ROADS", "Compares rising water levels with local road maps to determine exactly which streets will be underwater and how deep the water will be.", Inches(6.8), SAFETY_ORANGE),
        ("STEP 4: ALERTS & SAFE ROUTES", "Sends automated SMS in local languages and guides residents along dry roads to open government shelters, while helping rescue teams deploy in advance.", Inches(9.8), SUCCESS_GREEN),
    ]

    for title, desc, left_x, col in steps:
        c = add_card(
            slide, left_x, Inches(1.9), Inches(2.733), Inches(4.0),
            bg_color=CARD_BG, border_color=col, border_width=Pt(1.4),
            shape_name=f"!!StepCard_{title[:6]}"
        )
        ctf = c.text_frame
        cp1 = ctf.paragraphs[0]
        cp1.text = title
        cp1.font.name = FONT_PRIMARY
        cp1.font.size = Pt(12)
        cp1.font.bold = True
        cp1.font.color.rgb = col
        cp1.space_after = Pt(8)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(10.5)
        cp2.font.color.rgb = CLOUD_WHITE

    # Bottom Summary
    summary = add_card(
        slide, Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.9),
        bg_color=RGBColor(20, 28, 40), border_color=ACCENT_BLUE, border_width=Pt(1.0),
        shape_name="!!StepSummary"
    )
    stf = summary.text_frame
    sp = stf.paragraphs[0]
    sp.text = "CORE GOAL: Predict where water will rise, alert people immediately, and guide both citizens and rescue teams to safe ground before catastrophe happens."
    sp.font.name = FONT_PRIMARY
    sp.font.size = Pt(11)
    sp.font.bold = True
    sp.font.color.rgb = CLOUD_WHITE


def build_slide_04(prs):
    """Slide 04: Step 1 - Monitoring Water Levels With Satellite Backup"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "STEP 1: SENSOR BACKUP", "WHAT HAPPENS WHEN GROUND SENSORS BREAK?")

    # Left: The Failure Problem
    left_c = add_card(
        slide, Inches(0.8), Inches(1.9), Inches(5.7), Inches(4.9),
        bg_color=RGBColor(32, 22, 24), border_color=SAFETY_ORANGE, border_width=Pt(1.2),
        shape_name="!!SensorFailureCard"
    )
    ltf = left_c.text_frame
    lp1 = ltf.paragraphs[0]
    lp1.text = "THE SENSOR PROBLEM ON THE GROUND"
    lp1.font.name = FONT_PRIMARY
    lp1.font.size = Pt(13)
    lp1.font.bold = True
    lp1.font.color.rgb = SAFETY_ORANGE
    lp1.space_after = Pt(10)

    points_left = [
        ("River Gauges Break Easily", "Ground sensors are placed right in the river channel. Fast-moving water, floating tree trunks, and thick silt often knock them out completely."),
        ("Power & Signal Outages", "Severe storms knock down electricity poles and mobile network towers, stopping ground data from reaching disaster headquarters."),
        ("Missing Data Causes Warning Delays", "In most standard flood systems, if the ground sensor goes offline, the software simply stops working and leaves officials guessing."),
    ]
    for p_title, p_desc in points_left:
        pa = ltf.add_paragraph()
        pa.text = f"• {p_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = WARNING_YELLOW
        pa.space_after = Pt(2)

        pb = ltf.add_paragraph()
        pb.text = p_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(10)
        pb.font.color.rgb = MUTED_BLUE
        pb.space_after = Pt(10)

    # Right: The Satellite Radar Solution
    right_c = add_card(
        slide, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9),
        bg_color=RGBColor(20, 30, 42), border_color=ACCENT_BLUE, border_width=Pt(1.2),
        shape_name="!!SatelliteSolutionCard"
    )
    rtf = right_c.text_frame
    rp1 = rtf.paragraphs[0]
    rp1.text = "HOW SATELLITE RADAR SOLVES THIS"
    rp1.font.name = FONT_PRIMARY
    rp1.font.size = Pt(13)
    rp1.font.bold = True
    rp1.font.color.rgb = ACCENT_BLUE
    rp1.space_after = Pt(10)

    points_right = [
        ("Automatic Detection", "Our software checks for incoming sensor readings every 15 minutes. If no data arrives, it switches over to satellite radar data automatically."),
        ("Sees Through Rain & Storm Clouds", "Regular satellite cameras cannot see through monsoon clouds. We use radar satellites (Sentinel-3) which shoot radar pulses through heavy rain and measure river height directly."),
        ("Completely Safe in Space", "Because the satellite is in orbit, ground floods, broken power lines, and damaged roads cannot affect it. The system keeps running no matter how bad the storm is."),
    ]
    for p_title, p_desc in points_right:
        pa = rtf.add_paragraph()
        pa.text = f"✔  {p_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = SUCCESS_GREEN
        pa.space_after = Pt(2)

        pb = rtf.add_paragraph()
        pb.text = p_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(10)
        pb.font.color.rgb = CLOUD_WHITE
        pb.space_after = Pt(10)


def build_slide_05(prs):
    """Slide 05: Step 2 - Predicting Water Height and Giving 2+ Hours Notice"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "STEP 2: FLOOD PREDICTION", "PREDICTING WATER LEVEL TO GAIN 2+ HOURS OF LEAD TIME")

    cards = [
        ("1. Tracking Flood Water Speed Downstream", "When heavy rain falls in upstream hills, the flood wave takes time to travel downstream (about 5 meters per second). By calculating this speed, our system gives towns downstream 2 to 2.5 hours of advance notice before the water level peaks.", Inches(0.8), WARNING_YELLOW),
        ("2. Checking Soil Wetness (Saturation)", "Dry soil absorbs rain like a sponge. But when soil is already completely soaked from days of rain, 90%+ of any new rain immediately runs off into rivers. The system checks soil wetness so it knows when a flash flood is likely.", Inches(4.8), ACCENT_BLUE),
        ("3. Keeping Predictions Realistic", "Pure computer algorithms sometimes make wild, impossible guesses when unusual storms hit. We constrain the prediction with basic physics (how much water the river channel can physically hold) so predictions remain reliable.", Inches(8.8), SUCCESS_GREEN),
    ]

    for title, desc, left_x, col in cards:
        c = add_card(
            slide, left_x, Inches(1.9), Inches(3.7), Inches(3.6),
            bg_color=CARD_BG, border_color=col, border_width=Pt(1.2),
            shape_name=f"!!PredCard_{title[:3]}"
        )
        ctf = c.text_frame
        cp1 = ctf.paragraphs[0]
        cp1.text = title
        cp1.font.name = FONT_PRIMARY
        cp1.font.size = Pt(12)
        cp1.font.bold = True
        cp1.font.color.rgb = col
        cp1.space_after = Pt(8)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(10.5)
        cp2.font.color.rgb = CLOUD_WHITE

    # Practical Takeaway Banner
    banner = add_card(
        slide, Inches(0.8), Inches(5.75), Inches(11.733), Inches(1.15),
        bg_color=RGBColor(24, 34, 48), border_color=WARNING_YELLOW, border_width=Pt(1.2),
        shape_name="!!LeadTimeBanner"
    )
    btf = banner.text_frame
    bp1 = btf.paragraphs[0]
    bp1.text = "WHY A 2-HOUR LEAD TIME MATTERS:"
    bp1.font.name = FONT_PRIMARY
    bp1.font.size = Pt(12)
    bp1.font.bold = True
    bp1.font.color.rgb = WARNING_YELLOW
    bp1.space_after = Pt(2)

    bp2 = btf.add_paragraph()
    bp2.text = "In most flash floods, people get caught because water enters homes without any warning. Having even 2 hours of advance notice is enough time for families to get to high ground and for rescue teams to reach vulnerable spots."
    bp2.font.name = FONT_PRIMARY
    bp2.font.size = Pt(10.5)
    bp2.font.color.rgb = CLOUD_WHITE


def build_slide_06(prs):
    """Slide 06: Step 3 - Mapping Which Roads Will Be Flooded"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "STEP 3: MAPPING FLOODED ROADS", "FINDING OUT WHICH ROADS WILL BE UNDERWATER")

    # Left: How it works
    left_c = add_card(
        slide, Inches(0.8), Inches(1.9), Inches(5.7), Inches(4.9),
        bg_color=CARD_BG, border_color=ACCENT_BLUE, border_width=Pt(1.2),
        shape_name="!!HowMapWorksCard"
    )
    ltf = left_c.text_frame
    lp1 = ltf.paragraphs[0]
    lp1.text = "HOW THE SYSTEM CHECKS EVERY ROAD"
    lp1.font.name = FONT_PRIMARY
    lp1.font.size = Pt(13)
    lp1.font.bold = True
    lp1.font.color.rgb = ACCENT_BLUE
    lp1.space_after = Pt(10)

    steps = [
        ("Step 1: Digital Elevation Map", "The system uses terrain height maps to see which parts of the town are on high ground and which streets sit in low dips."),
        ("Step 2: Predicted River Height", "It brings in the predicted river water level from Step 2."),
        ("Step 3: Road Map Overlay", "It overlays local road maps (from OpenStreetMap) on top of the water map to calculate estimated water depth on every single street segment."),
    ]
    for s_title, s_desc in steps:
        pa = ltf.add_paragraph()
        pa.text = f"• {s_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = CLOUD_WHITE
        pa.space_after = Pt(2)

        pb = ltf.add_paragraph()
        pb.text = s_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(10)
        pb.font.color.rgb = MUTED_BLUE
        pb.space_after = Pt(10)

    # Right: Road Classification
    right_c = add_card(
        slide, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9),
        bg_color=CARD_BG, border_color=SAFETY_ORANGE, border_width=Pt(1.2),
        shape_name="!!RoadClassCard"
    )
    rtf = right_c.text_frame
    rp1 = rtf.paragraphs[0]
    rp1.text = "CLASSIFYING ROADS FOR SAFETY"
    rp1.font.name = FONT_PRIMARY
    rp1.font.size = Pt(13)
    rp1.font.bold = True
    rp1.font.color.rgb = SAFETY_ORANGE
    rp1.space_after = Pt(10)

    tiers = [
        ("Dry Roads (Under 5 cm)", "Completely safe. Normal walking and passenger cars allowed.", SUCCESS_GREEN),
        ("Shallow Water (5 cm to 15 cm)", "Walking is hazardous for elderly/children. Small cars must take caution.", WARNING_YELLOW),
        ("Dangerous Flooded Roads (15 cm to 80 cm)", "Blocked for pedestrians and ordinary cars (engines will stall). Only high-clearance rescue trucks can pass.", SAFETY_ORANGE),
        ("Deep Flood (Over 80 cm)", "Completely impassable. Roads are closed to all vehicles. Only rescue boats can enter.", RGBColor(235, 70, 70)),
    ]
    for t_title, t_desc, col in tiers:
        pa = rtf.add_paragraph()
        pa.text = f"■  {t_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = col
        pa.space_after = Pt(2)

        pb = rtf.add_paragraph()
        pb.text = t_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(10)
        pb.font.color.rgb = CLOUD_WHITE
        pb.space_after = Pt(10)


def build_slide_07(prs):
    """Slide 07: Step 4 - Sending Alerts Quickly to People"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide, color=RGBColor(32, 18, 22))

    add_header(slide, "STEP 4: EARLY WARNING", "SENDING ALERTS DIRECTLY TO PEOPLE WITHOUT DELAY")

    # Top Trigger Card
    top_c = add_card(
        slide, Inches(0.8), Inches(1.9), Inches(11.733), Inches(1.8),
        bg_color=RGBColor(48, 18, 24), border_color=SAFETY_ORANGE, border_width=Pt(1.5),
        shape_name="!!TriggerCard"
    )
    ttf = top_c.text_frame
    tp1 = ttf.paragraphs[0]
    tp1.text = "AUTOMATIC ALERTS: NO WAITING FOR MANUAL APPROVAL"
    tp1.font.name = FONT_PRIMARY
    tp1.font.size = Pt(14)
    tp1.font.bold = True
    tp1.font.color.rgb = SAFETY_ORANGE
    tp1.space_after = Pt(4)

    tp2 = ttf.add_paragraph()
    tp2.text = "In many past floods, official warnings were delayed for hours because of manual paperwork and phone chains. Our software sends out alerts automatically the moment water rise and rainfall speed cross safety limits, ensuring warnings go out even in the middle of the night."
    tp2.font.name = FONT_PRIMARY
    tp2.font.size = Pt(11)
    tp2.font.color.rgb = CLOUD_WHITE

    # 3 Channels
    channels = [
        ("1. SMS in Local Languages", "Sends text messages directly to mobile phones in local languages (Garhwali, Kumaoni, Hindi, English, etc.). Works on ordinary keypad phones without needing internet.", Inches(0.8), WARNING_YELLOW),
        ("2. Public Loudspeakers & Sirens", "Triggers loud audio sirens and clear spoken voice messages at bus stands, train stations, and village centers so people hear the warning immediately.", Inches(4.8), ACCENT_BLUE),
        ("3. Government Disaster Dashboard", "Updates local authorities and district response officials with a clear map showing exactly which streets and neighborhoods are in danger.", Inches(8.8), SUCCESS_GREEN),
    ]

    for title, desc, left_x, col in channels:
        c = add_card(
            slide, left_x, Inches(3.95), Inches(3.7), Inches(2.85),
            bg_color=RGBColor(26, 20, 26), border_color=col, border_width=Pt(1.2),
            shape_name=f"!!ChanCard_{title[:2]}"
        )
        ctf = c.text_frame
        cp1 = ctf.paragraphs[0]
        cp1.text = title
        cp1.font.name = FONT_PRIMARY
        cp1.font.size = Pt(12.5)
        cp1.font.bold = True
        cp1.font.color.rgb = col
        cp1.space_after = Pt(8)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(10.5)
        cp2.font.color.rgb = CLOUD_WHITE


def build_slide_08(prs):
    """Slide 08: Assisting Rescuers - Reaching Cut-Off Areas Before Flooding"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "RESCUER ASSISTANCE", "HELPING RESCUERS REACH PEOPLE BEFORE ROADS GET CUT OFF")

    # Left: What Rescuers Need
    left_c = add_card(
        slide, Inches(0.8), Inches(1.9), Inches(5.7), Inches(4.9),
        bg_color=CARD_BG, border_color=WARNING_YELLOW, border_width=Pt(1.2),
        shape_name="!!RescuerProblemCard"
    )
    ltf = left_c.text_frame
    lp1 = ltf.paragraphs[0]
    lp1.text = "THE PROBLEM FOR EMERGENCY TEAMS"
    lp1.font.name = FONT_PRIMARY
    lp1.font.size = Pt(13)
    lp1.font.bold = True
    lp1.font.color.rgb = WARNING_YELLOW
    lp1.space_after = Pt(10)

    res_probs = [
        ("Rescuers Are Often Called Too Late", "Emergency teams (like NDRF or local police) usually find out about trapped people only after water has already cut off the road."),
        ("Villages Become Inaccessible Islands", "Low-lying areas often have only one main road connecting them. Once that road goes under 1 meter of water, regular trucks cannot enter."),
        ("Rescuers Risk Getting Stuck Themselves", "Without knowing where water is rising fastest, rescue vehicles can easily drive into washed-out roads and get trapped."),
    ]
    for p_title, p_desc in res_probs:
        pa = ltf.add_paragraph()
        pa.text = f"• {p_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = SAFETY_ORANGE
        pa.space_after = Pt(2)

        pb = ltf.add_paragraph()
        pb.text = p_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(10)
        pb.font.color.rgb = MUTED_BLUE
        pb.space_after = Pt(10)

    # Right: How Our System Helps Rescuers
    right_c = add_card(
        slide, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9),
        bg_color=CARD_BG, border_color=SUCCESS_GREEN, border_width=Pt(1.2),
        shape_name="!!RescuerSolutionCard"
    )
    rtf = right_c.text_frame
    rp1 = rtf.paragraphs[0]
    rp1.text = "HOW OUR SYSTEM HELPS RESCUERS"
    rp1.font.name = FONT_PRIMARY
    rp1.font.size = Pt(13)
    rp1.font.bold = True
    rp1.font.color.rgb = SUCCESS_GREEN
    rp1.space_after = Pt(10)

    res_sols = [
        ("Identifies Cut-Off Zones in Advance", "Because the system predicts water height 2 hours early, it alerts rescue teams to which neighborhoods will lose road access before the water actually arrives."),
        ("Move Boats & Supplies Before Roads Close", "Rescuers are advised to move motorized rescue boats, medical kits, and relief supplies into position while access roads are still dry."),
        ("Special Routes for High-Clearance Trucks", "Rescue trucks can safely drive through shallow water up to 80 cm deep. The system provides special routes for rescue trucks so they take the shortest path to stranded people."),
    ]
    for s_title, s_desc in res_sols:
        pa = rtf.add_paragraph()
        pa.text = f"✔  {s_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = CLOUD_WHITE
        pa.space_after = Pt(2)

        pb = rtf.add_paragraph()
        pb.text = s_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(10)
        pb.font.color.rgb = MUTED_BLUE
        pb.space_after = Pt(10)


def build_slide_09(prs):
    """Slide 09: Safe Evacuation - Guiding People Along Dry Roads"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "SAFE EVACUATION", "GUIDING PEOPLE ALONG DRY ROADS TO AVOID DROWNING TRAPS")

    # 3 Profiles
    profiles = [
        ("Walking Citizens / Families", "MAX SAFE WATER DEPTH: < 15 CM (ANKLE DEPTH)", "Fast-moving water as shallow as 15 cm can easily knock down children and adults. The system directs people walking on foot strictly along high, dry ridges and completely avoids flooded streets.", Inches(0.8), CLOUD_WHITE),
        ("Family Cars & Motorcycles", "MAX SAFE WATER DEPTH: < 30 CM", "Water deeper than 30 cm will enter car exhaust pipes and air intakes, causing engines to die and leaving families stranded. The system routes passenger vehicles around dips and low culverts.", Inches(4.8), WARNING_YELLOW),
        ("Emergency Rescue Trucks", "MAX SAFE WATER DEPTH: UP TO 80 CM", "Heavy NDRF 4x4 trucks have high ground clearance and can wade through shallow flooded sections. This lets rescue teams take direct paths to reach trapped people quickly.", Inches(8.8), SAFETY_ORANGE),
    ]

    for title, limit, desc, left_x, col in profiles:
        c = add_card(
            slide, left_x, Inches(1.9), Inches(3.7), Inches(3.4),
            bg_color=CARD_BG, border_color=col, border_width=Pt(1.2),
            shape_name=f"!!ProfCard_{title[:5]}"
        )
        ctf = c.text_frame
        cp1 = ctf.paragraphs[0]
        cp1.text = title
        cp1.font.name = FONT_PRIMARY
        cp1.font.size = Pt(13)
        cp1.font.bold = True
        cp1.font.color.rgb = col
        cp1.space_after = Pt(4)

        cp_lim = ctf.add_paragraph()
        cp_lim.text = limit
        cp_lim.font.name = FONT_PRIMARY
        cp_lim.font.size = Pt(11)
        cp_lim.font.bold = True
        cp_lim.font.color.rgb = col
        cp_lim.space_after = Pt(8)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(10)
        cp2.font.color.rgb = MUTED_BLUE

    # Bottom Takeaway Ribbon
    ribbon = add_card(
        slide, Inches(0.8), Inches(5.55), Inches(11.733), Inches(1.35),
        bg_color=RGBColor(20, 28, 42), border_color=ACCENT_BLUE, border_width=Pt(1.2),
        shape_name="!!EvacRibbon"
    )
    rtf = ribbon.text_frame
    rp1 = rtf.paragraphs[0]
    rp1.text = "HOW DYNAMIC ROUTING SAVES LIVES:"
    rp1.font.name = FONT_PRIMARY
    rp1.font.size = Pt(12)
    rp1.font.bold = True
    rp1.font.color.rgb = ACCENT_BLUE
    rp1.space_after = Pt(2)

    rp2 = rtf.add_paragraph()
    rp2.text = "Regular map apps calculate the shortest path, which often leads straight into a flooded underpass. Our system constantly checks water levels on every road: if water rises on a street, that street is instantly blocked, and evacuees are guided onto safe alternative roads."
    rp2.font.name = FONT_PRIMARY
    rp2.font.size = Pt(10.5)
    rp2.font.color.rgb = CLOUD_WHITE


def build_slide_10(prs):
    """Slide 10: Government Relief Centres - Safe Shelters and Bed Tracking"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "RELIEF SHELTERS", "MAKING SURE PEOPLE REACH SAFE, OPEN GOVERNMENT SHELTERS")

    # Left: Selecting genuinely safe shelters
    left_c = add_card(
        slide, Inches(0.8), Inches(1.9), Inches(5.7), Inches(4.9),
        bg_color=CARD_BG, border_color=ACCENT_BLUE, border_width=Pt(1.2),
        shape_name="!!ShelterCriteriaCard"
    )
    ltf = left_c.text_frame
    lp1 = ltf.paragraphs[0]
    lp1.text = "WHICH SHELTERS ARE ACTUALLY SAFE?"
    lp1.font.name = FONT_PRIMARY
    lp1.font.size = Pt(13)
    lp1.font.bold = True
    lp1.font.color.rgb = ACCENT_BLUE
    lp1.space_after = Pt(10)

    checks = [
        ("Built on High Ground", "Not every school or community building is safe. The system only directs people to registered shelters that are built on high ground, well above the highest expected water level."),
        ("Must Have a Dry Access Road", "A shelter on a hill is useless if the road leading up to it is under 1 meter of water. The system verifies that at least one dry approach road remains open before directing people there."),
        ("Official Government Registry", "Uses verified shelters from district disaster authorities so people know where food, clean water, and medical aid will be waiting."),
    ]
    for c_title, c_desc in checks:
        pa = ltf.add_paragraph()
        pa.text = f"✔  {c_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = CLOUD_WHITE
        pa.space_after = Pt(2)

        pb = ltf.add_paragraph()
        pb.text = c_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(10)
        pb.font.color.rgb = MUTED_BLUE
        pb.space_after = Pt(10)

    # Right: Capacity tracking and avoiding overcrowding
    right_c = add_card(
        slide, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9),
        bg_color=CARD_BG, border_color=WARNING_YELLOW, border_width=Pt(1.2),
        shape_name="!!ShelterCapacityCard"
    )
    rtf = right_c.text_frame
    rp1 = rtf.paragraphs[0]
    rp1.text = "PREVENTING SHELTER OVERCROWDING"
    rp1.font.name = FONT_PRIMARY
    rp1.font.size = Pt(13)
    rp1.font.bold = True
    rp1.font.color.rgb = WARNING_YELLOW
    rp1.space_after = Pt(10)

    caps = [
        ("Live Bed Capacity Tracking", "The system monitors how full each government shelter is in real-time (for example: Joshimath 72%, Pipalkoti 65%, Chamoli 88%, Rudraprayag 30%)."),
        ("Automatic Diversion at 85% Full", "If a relief center gets close to full (reaching 85% occupancy), the system automatically starts routing new evacuees to the next nearest open shelter."),
        ("No One Gets Turned Away", "This stops families from walking through rain and storm only to find that the shelter doors are full and locked. It balances crowds smoothly across all available centers."),
    ]
    for c_title, c_desc in caps:
        pa = rtf.add_paragraph()
        pa.text = f"• {c_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = SUCCESS_GREEN
        pa.space_after = Pt(2)

        pb = rtf.add_paragraph()
        pb.text = c_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(10)
        pb.font.color.rgb = MUTED_BLUE
        pb.space_after = Pt(10)


def build_slide_11(prs):
    """Slide 11: How Our Idea Is New - Comparison with Existing Systems"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "SYSTEM NOVELTY", "HOW OUR SYSTEM DIFFERS FROM EXISTING DISASTER TOOLS")

    comparisons = [
        (
            "1. Continuous Satellite Radar Failover",
            "GROUND GAUGE VULNERABILITY FIXED",
            "Existing river monitoring depends on physical gauges that break or lose power during storms. Our system provides automated failover to Sentinel-3 SAR radar altimetry, penetrating storm clouds directly from orbit without ground equipment.",
            Inches(0.8), ACCENT_BLUE
        ),
        (
            "2. Street-Level Depth-Aware Routing",
            "SOLVES COMMERCIAL GPS BLINDNESS",
            "Standard GPS apps (Google Maps) only route by traffic speed and frequently direct drivers into flooded dips. Our system calculates estimated water depth on every road segment and strictly steers evacuees along verified dry routes.",
            Inches(4.8), SUCCESS_GREEN
        ),
        (
            "3. Proactive Rescuer Staging & Shelters",
            "FROM REACTIVE CALLS TO ADVANCE ACTION",
            "Current rescue teams are dispatched after access roads are submerged. Our system flags single-access villages 2 hours before cutoff to pre-stage boats, and dynamically routes families to open shelters with dry access roads.",
            Inches(8.8), WARNING_YELLOW
        ),
    ]

    for title, metric, desc, left_x, col in comparisons:
        c = add_card(
            slide, left_x, Inches(1.9), Inches(3.7), Inches(3.5),
            bg_color=CARD_BG, border_color=col, border_width=Pt(1.2),
            shape_name=f"!!NovCard_{title[:4]}"
        )
        ctf = c.text_frame
        cp1 = ctf.paragraphs[0]
        cp1.text = title
        cp1.font.name = FONT_PRIMARY
        cp1.font.size = Pt(12)
        cp1.font.bold = True
        cp1.font.color.rgb = col
        cp1.space_after = Pt(4)

        cpm = ctf.add_paragraph()
        cpm.text = metric
        cpm.font.name = FONT_PRIMARY
        cpm.font.size = Pt(12.5)
        cpm.font.bold = True
        cpm.font.color.rgb = CLOUD_WHITE
        cpm.space_after = Pt(8)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_PRIMARY
        cp2.font.size = Pt(10)
        cp2.font.color.rgb = MUTED_BLUE

    # Summary Box
    box = add_card(
        slide, Inches(0.8), Inches(5.65), Inches(11.733), Inches(1.25),
        bg_color=RGBColor(22, 32, 46), border_color=SUCCESS_GREEN, border_width=Pt(1.2),
        shape_name="!!NoveltySummaryBox"
    )
    btf = box.text_frame
    bp1 = btf.paragraphs[0]
    bp1.text = "SUMMARY OF NOVEL CONTRIBUTION:"
    bp1.font.name = FONT_PRIMARY
    bp1.font.size = Pt(12)
    bp1.font.bold = True
    bp1.font.color.rgb = SUCCESS_GREEN
    bp1.space_after = Pt(2)

    bp2 = btf.add_paragraph()
    bp2.text = "Instead of treating river monitoring, road mapping, and rescue logistics as isolated problems, our framework integrates them into a single automated pipeline: spaceborne sensor backup + street water depth mapping + depth-constrained evacuation navigation."
    bp2.font.name = FONT_PRIMARY
    bp2.font.size = Pt(10.5)
    bp2.font.color.rgb = CLOUD_WHITE


def build_slide_12(prs):
    """Slide 12: Summary & Conclusion"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    inject_morph_transition(slide)
    add_dark_canvas(slide)

    add_header(slide, "CONCLUSION", "SUMMARY OF WHAT WE BUILT AND NEXT STEPS")

    # Left: What the System Achieves
    left_c = add_card(
        slide, Inches(0.8), Inches(1.9), Inches(5.7), Inches(4.0),
        bg_color=CARD_BG, border_color=SUCCESS_GREEN, border_width=Pt(1.2),
        shape_name="!!SummaryCard"
    )
    ltf = left_c.text_frame
    lp1 = ltf.paragraphs[0]
    lp1.text = "WHAT OUR SYSTEM ACHIEVES"
    lp1.font.name = FONT_PRIMARY
    lp1.font.size = Pt(13)
    lp1.font.bold = True
    lp1.font.color.rgb = SUCCESS_GREEN
    lp1.space_after = Pt(8)

    achieves = [
        ("Predicts 2+ Hours Early", "Gives residents and emergency managers valuable advance time before floodwaters peak."),
        ("Works Even If Sensors Break", "Switches automatically to satellite radar if river gauges get washed away."),
        ("Protects Rescuers & Families", "Keeps citizens out of dangerous water and helps rescue teams move before roads submerge."),
        ("Guides to Safe Government Shelters", "Directs evacuees only to elevated shelters with open beds and dry access roads."),
    ]
    for a_title, a_desc in achieves:
        pa = ltf.add_paragraph()
        pa.text = f"✔  {a_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = CLOUD_WHITE
        pa.space_after = Pt(1)

        pb = ltf.add_paragraph()
        pb.text = a_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(9.5)
        pb.font.color.rgb = MUTED_BLUE
        pb.space_after = Pt(6)

    # Right: Next Steps
    right_c = add_card(
        slide, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.0),
        bg_color=CARD_BG, border_color=ACCENT_BLUE, border_width=Pt(1.2),
        shape_name="!!NextStepsCard"
    )
    rtf = right_c.text_frame
    rp1 = rtf.paragraphs[0]
    rp1.text = "PRACTICAL NEXT STEPS"
    rp1.font.name = FONT_PRIMARY
    rp1.font.size = Pt(13)
    rp1.font.bold = True
    rp1.font.color.rgb = ACCENT_BLUE
    rp1.space_after = Pt(8)

    next_steps = [
        ("Integration with State Disaster Portals", "Connecting the automatic alert pipeline directly with local State Disaster Management Authority SMS portals."),
        ("Deploying Low-Cost Water Sensors", "Testing small, solar-powered water level sensors on smaller streams that currently have no government monitoring."),
        ("Field Trials with Local Communities", "Conducting evacuation drills in flood-prone blocks to ensure families and rescue teams find the mobile interface easy to use."),
    ]
    for n_title, n_desc in next_steps:
        pa = rtf.add_paragraph()
        pa.text = f"• {n_title}"
        pa.font.name = FONT_PRIMARY
        pa.font.size = Pt(11)
        pa.font.bold = True
        pa.font.color.rgb = WARNING_YELLOW
        pa.space_after = Pt(1)

        pb = rtf.add_paragraph()
        pb.text = n_desc
        pb.font.name = FONT_PRIMARY
        pb.font.size = Pt(9.5)
        pb.font.color.rgb = MUTED_BLUE
        pb.space_after = Pt(6)

    # Bottom Closing Thank You Card
    close_c = add_card(
        slide, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.95),
        bg_color=RGBColor(20, 28, 40), border_color=CLOUD_WHITE, border_width=Pt(1.0),
        shape_name="!!ThankYouCard"
    )
    ctf = close_c.text_frame
    cp = ctf.paragraphs[0]
    cp.text = "THANK YOU  •  QUESTIONS & DISCUSSION"
    cp.font.name = FONT_PRIMARY
    cp.font.size = Pt(13)
    cp.font.bold = True
    cp.font.color.rgb = CLOUD_WHITE
    cp.space_after = Pt(2)

    cp2 = ctf.add_paragraph()
    cp2.text = "Undergraduate Major Project Research Group  |  Department of Computer Science & Engineering"
    cp2.font.name = FONT_PRIMARY
    cp2.font.size = Pt(10)
    cp2.font.color.rgb = ACCENT_BLUE


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================

def main():
    prs = pptx.Presentation()
    # Standard 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    print("Compiling 12-Slide Plain-Language Engineering Deck...")
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

    output_path = Path(__file__).parent / "Flash_Flood_Research_Paper_Presentation.pptx"
    prs.save(str(output_path))
    print(f"Successfully generated: {output_path}")


if __name__ == "__main__":
    main()
