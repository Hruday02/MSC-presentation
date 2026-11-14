

import base64
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import dash
from dash import html, dcc, Input, Output, State, callback_context, no_update, ALL
import dash_cytoscape as cyto

# =============================================================================
# CONTENT CONFIGURATION
# All text, node definitions, groups, edges, coordinates, and ship simulation
# parameters are defined here so wording, layout, and connections can be edited
# without altering logic.
# =============================================================================

CONTENT: Dict[str, Any] = {
    # App header & branding
    "app": {
        "eyebrow": "MSC ballast tank digital twin proof of concept",
        "title": "From separate projects to one digital twin",
        "port": 8056,
        "host": "127.0.0.1",
        "canvas_size": {"width": 1000, "height": 620},
    },

    # 4 Project Phases
    "phases": {
        1: {
            "name": "Phase 1",
            "title": "Separate projects",
            "subtitle": "Independent Foundation",
            "description": (
                "The initial phase establishes the physical Ballast Tank and its onboard inspection sensors (LiDAR 3D Scanner, "
                "RGB/Video Camera, and Hyperspectral Chemical Scanner). Each sensor operates directly on the tank before "
                "computation and surface area pipelines are connected in Phase 2."
            ),
        },
        2: {
            "name": "Phase 2",
            "title": "Connected projects",
            "subtitle": "Early Integration",
            "description": (
                "The first integration links form between scanning and computation. LiDAR point cloud from the "
                "Ballast Tank feeds the SAC surface area calculation engine, and SAC outputs verified 3D models "
                "and calculated surface area into the VTL."
            ),
        },
        3: {
            "name": "Phase 3",
            "title": "The digital twin",
            "subtitle": "Full Digital Synchronization",
            "description": (
                "The complete digital twin architecture is live. All three sensors (LiDAR, RGB/Video, Hyper) "
                "monitor the physical Ballast Tank, while VTL feeds structural records to the Digital Twin (DT). "
                "DT maintains continuous real-time bidirectional synchronization with the Ballast Tank."
            ),
        },
        4: {
            "name": "Phase 4",
            "title": "Beyond the twin",
            "subtitle": "External Expansion & Decision Support",
            "description": (
                "Beyond the twin: LRMS and HMS act as the next link for the digital twin. "
                "DT feeds HMS (Hull Maintenance System) for fleet-wide awareness and analytics, "
                "while LRMS (Long Range Maintenance Schedule) provides decision support directing maintenance actions back to the physical Ballast Tank."
            ),
        },
        4.5: {
        "name": "Phase 4.5",
        "title": "AST System Model",
        "subtitle": "",
        "description": "",
    },
    },

    # Groups (Compound parent bounding boxes)
    "groups": {
        "sensors": {
            "label": "Ballast Tank & Sensors",
            "border_color": "#ef4444",      # red dashed border
            "bg_color": "rgba(254, 242, 242, 0.4)",
            "text_color": "#b91c1c",
            "phases": [1, 2, 3, 4],
        },
        "computation": {
            "label": "Computation",
            "border_color": "#10b981",      # green dashed border
            "bg_color": "rgba(240, 253, 244, 0.4)",
            "text_color": "#047857",
            "phases": [1, 2, 3, 4],
        },
        "dtsync": {
            "label": "Digital Twin",
            "border_color": "#3b82f6",      # blue dashed border
            "bg_color": "rgba(239, 246, 255, 0.4)",
            "text_color": "#1d4ed8",
            "phases": [2, 3, 4],            # visible from phase 2 onwards
        },
        "decision": {
            "label": "Beyond the Twin",
            "border_color": "#8b5cf6",      # purple dashed border
            "bg_color": "rgba(245, 243, 255, 0.4)",
            "text_color": "#6d28d9",
            "phases": [4],                  # ONLY in phase 4 (Beyond the Twin)!
        },
    },

    # Nodes (System modules and DT sync entities)
    "nodes": {
        "lidar": {
            "label": "LIDAR",
            "sublabel": "3D laser scan",
            "group": "sensors",
            "style": "sensor",
            "description": "3D laser scanner capturing high-density geometric point clouds inside the ballast tank.",
            "provides": ["Point cloud data", "Geometry scan"],
        },
        "rgb": {
            "label": "RGB/Video",
            "sublabel": "visual images",
            "group": "sensors",
            "style": "sensor",
            "description": "High-definition optical camera providing visual confirmation and color gradient analysis of tank plating.",
            "provides": ["Photos", "4K Video Stream"],
        },
        "hyp": {
            "label": "Hyper",
            "sublabel": "surface condition",
            "group": "sensors",
            "style": "sensor",
            "description": (
                "Hyperspectral imaging sensor capturing Near-IR reflectance (780-940nm) to detect surface "
                "condition, epoxy breakdown, and chemical oxidation (Fe₂O₃)."
            ),
            "provides": ["Surface condition data", "Chemical reflectance"],
        },
        "sac": {
            "label": "SAC",
            "sublabel": "surface area",
            "group": "computation",
            "style": "project",
            "description": (
                "Surface Area Calculation engine. Converts LiDAR scans into verified 3D models and calculated surface area "
                "to supply geometric dimensions to the Virtual Technical Library."
            ),
            "provides": ["3D tank model", "Surface area", "Mesh calculations"],
        },
        "vtl": {
            "label": "VTL Prototype",
            "sublabel": "technical library",
            "group": "computation",
            "style": "project",
            "description": (
                "Virtual Technical Library. Central repository storing structural tank specifications, geometry, "
                "and historical records to feed the Digital Twin."
            ),
            "provides": ["Tank records", "CAD baseline models"],
        },
        "tank": {
            "label": "Ballast Tank",
            "sublabel": "",
            "group": "sensors",
            "style": "asset",
            "description": (
                "The physical ballast water storage tank on the ship (MSC Cargo Vessel Compartment B-3). "
                "Real-world asset continuously monitored by LiDAR, RGB/Video, and Hyperspectral sensors."
            ),
            "provides": ["Current physical state", "Sensor scan target"],
        },
        "twin": {
            "label": "DT",
            "sublabel": "digital twin",
            "group": "dtsync",
            "style": "twin",
            "description": (
                "Digital Twin (DT). Virtual counterpart kept in continuous real-time bidirectional "
                "synchronization with the physical Ballast Tank, integrating technical records from VTL."
            ),
            "provides": ["Live synchronized state", "Historical degradation tracking"],
        },
        "samm": {
            "label": "LRMS",
            "sublabel": "Long Range Maintenance Schedule",
            "group": "decision",
            "style": "samm",
            "description": (
                "LRMS: Long Range Maintenance Schedule (Beyond the Twin). Top-level operational management evaluating fleet priorities "
                "and directing maintenance, recoating, and inspection actions back to the physical Ballast Tank."
            ),
            "provides": ["Maintenance actions", "Coating decisions"],
        },
        "cms": {
            "label": "HMS",
            "sublabel": "Hull Maintenance System",
            "group": "decision",
            "style": "cms",
            "description": (
                "HMS: Hull Maintenance System (Beyond the Twin). Uses Digital Twin telemetry to drive Corrosion Data, "
                "Analytics, and Situational Awareness across vessel tanks."
            ),
            "provides": ["Data", "Analytics", "Awareness"],
        },
    },

    # Coordinates per phase on a 1000 x 620 coordinate canvas.
    # Perfectly centered layout with clean separation across all groups:
    # - Center-Top: Ballast Tank & Sensors [LiDAR, RGB, Hyper] row at Y=130, Ballast Tank at (520, 265)
    # - Left: Computation [SAC (180, 205), VTL (220, 410)]
    # - Center-Bottom: Digital Twin [DT (520, 475)] directly under Ballast Tank
    # - Right: Beyond the Twin layer [LRMS (820, 335), HMS (820, 475)]
    "positions": {
        1: {
            "lidar": (400, 130),
            "rgb": (520, 130),
            "hyp": (640, 130),
            "tank": (520, 265),
            "sac": (180, 205),
            "vtl": (220, 410),
        },
        2: {
            "lidar": (400, 130),
            "rgb": (520, 130),
            "hyp": (640, 130),
            "tank": (520, 265),
            "sac": (180, 205),
            "vtl": (220, 410),
            "twin": (520, 475),
        },
        3: {
            "lidar": (400, 130),
            "rgb": (520, 130),
            "hyp": (640, 130),
            "tank": (520, 265),
            "sac": (180, 205),
            "vtl": (220, 410),
            "twin": (520, 475),
        },
        4: {
            "lidar": (400, 130),
            "rgb": (520, 130),
            "hyp": (640, 130),
            "tank": (520, 265),
            "sac": (180, 205),
            "vtl": (220, 410),
            "twin": (520, 475),
            "samm": (820, 335),
            "cms": (820, 475),
        },
        4.5: {},
    },

    # Directed and bidirectional edges matching remapped architecture
    "edges": [
        # Phase 2, 3, 4: Computation links (LiDAR -> SAC -> VTL) and direct DT connections (SAC -> DT, VTL -> DT)
        {"source": "lidar", "target": "sac", "label": "point cloud", "phases": [2, 3, 4]},
        {"source": "sac", "target": "twin", "label": "area + model", "phases": [2, 3, 4]},

        # Phase 3 & 4: Sensor inputs to physical Ballast Tank (Bidirectional telemetry & control loop)
        {"source": "lidar", "target": "tank", "label": "", "phases": [3, 4], "bidirectional": True},
        {"source": "rgb", "target": "tank", "label": "", "phases": [3, 4], "bidirectional": True},
        {"source": "hyp", "target": "tank", "label": "", "phases": [3, 4], "bidirectional": True},

        # Phase 2, 3 & 4: Digital Twin synchronization & Technical records
        {"source": "tank", "target": "twin", "label": "sync", "phases": [3, 4], "bidirectional": True},
        {"source": "vtl", "target": "twin", "label": "tank records", "phases": [2, 3, 4]},

        # Phase 4: Beyond the Twin layer connections (DT -> HMS, LRMS -> Ballast Tank)
        {"source": "twin", "target": "cms", "label": "twin data", "phases": [4]},
        {"source": "samm", "target": "tank", "label": "actions", "phases": [4]},
        {"source": "cms", "target": "vtl", "label": "", "phases": [4], "dashed": True, "style": "dashed"},
        {"source": "samm", "target": "cms", "label": "", "phases": [4], "bidirectional": True},
    ],

    # Phase 3 Ship & Tank Simulation Configuration
    "ship_simulation": {
        "vessel_name": "MSC Mediterranean Cargo Vessel",
        "compartment_name": "Ballast Water Tank B-3 (Port)",
        "location": "Lower Cargo Hold 3, Frames 36-44, Port Bulkhead",
        "dimensions": "18.4m L x 9.2m W x 7.6m H",
        "capacity": "1,280 m³ Seawater Ballast",
        "elevation": "-4.2m below operational waterline",

        "sensors": {
            "lidar": {
                "name": "LiDAR 3D Scanner",
                "tag": "LD-01",
                "position": "Ceiling Dome (X: 9.2m, Y: 4.6m, Z: +7.2m)",
                "spec": "1.2 Million pts/sec, 0.8mm geometric accuracy",
                "role": "Scans 3D interior point cloud and detects volumetric wall thickness recess",
            },
            "hyp": {
                "name": "Hyperspectral Sensor",
                "tag": "HS-01",
                "position": "Upper Port Stiffener (X: 14.8m, Y: 7.8m, Z: +6.4m)",
                "spec": "780nm - 940nm Near-Infrared Spectrum",
                "role": "Detects chemical signature of surface oxidation (Fe₂O₃) and protective epoxy coating breakdown",
            },
            "rgb": {
                "name": "RGB 4K Video Camera",
                "tag": "CAM-02",
                "position": "Aft Inspection Gimbal (X: 3.2m, Y: 2.1m, Z: +5.8m)",
                "spec": "3840x2160 @ 60fps, Marine IP68 Encapsulated",
                "role": "Provides optical visual confirmation and color gradient analysis of corrosion discoloration",
            },
        },

        "scenarios": {
            "clean": {
                "status_title": "Nominal Operating Condition · Baseline",
                "health_score": 96,
                "badge_color": "#10b981",
                "badge_text": "NOMINAL · SENSORS ACTIVE",
                "summary": "Protective epoxy coating fully intact. All 3 sensors (LiDAR, Hyperspectral, RGB) continuously scanning and reporting healthy baseline values.",
                "how_caught": {
                    "location": "MSC Cargo Vessel · Ballast Tank B-3 (All surfaces nominal)",
                    "hyperspectral": "HS-01 Near-IR: Baseline 780-920nm reflection nominal. Zero Fe₂O₃ oxidation detected.",
                    "rgb": "CAM-02 Optical: Smooth uniform marine coating. Zero discoloration or blister flaking.",
                    "lidar": "LD-01 3D Scan: Surface CAD profile matches baseline within ±0.2mm tolerance.",
                    "twin_sync": "Live twin fully synchronized with physical tank · Health Score: 96%",
                },
            },
            "rust": {
                "status_title": "Corrosion Detected: Localized Rust & Coating Breakdown",
                "health_score": 68,
                "badge_color": "#ef4444",
                "badge_text": "RUST DETECTED · CAUGHT BY SENSORS",
                "summary": "Severe localized rust oxidation has formed on the Port Bulkhead at Frame 38. All 3 sensors independently caught the defect across chemical, optical, and physical geometric dimensions.",
                "defect_details": {
                    "site": "Port Lower Bulkhead, Frame 38 (Elevation -4.2m below waterline)",
                    "affected_area": "4.8 m²",
                    "metal_loss_depth": "1.8 mm",
                    "severity": "High (Level 3 Accelerated Steel Oxidation)",
                },
                "how_caught": {
                    "location": "Ballast Tank B-3, Lower Port Bulkhead, Frame 38 (-4.2m below waterline)",
                    "hyperspectral": "HS-01 caught chemical oxidation: Fe₂O₃ absorption band spike at 850nm reveals subsurface coating failure.",
                    "rgb": "CAM-02 caught visual appearance: Red/brown rust bloom discoloration gradient & perimeter flaking.",
                    "lidar": "LD-01 caught geometric loss: Multi-beam point cloud measures -1.8mm steel thickness recession.",
                    "twin_sync": "SAC engine recalculates 4.8 m² damaged mesh -> VTL logs telemetry -> Digital Twin Health drops 96% -> 68%.",
                },
            },
        },
    },
}


# =============================================================================
# CYTOSCAPE STYLESHEET DEFINITION
# Clean engineering visual aesthetic: off-white palette, dashed compound boxes,
# round bubble nodes, amber active indicators, legible typography.
# =============================================================================

CYTO_STYLESHEET: List[Dict[str, Any]] = [
    # General compound group boxes (Clean, non-overlapping dashed boundaries)
    {
        "selector": "node.group-box",
        "style": {
            "label": "data(label)",
            "text-valign": "top",
            "text-halign": "center",
            "text-margin-y": 12,
            "font-family": "'Barlow Semi Condensed', 'Arial Narrow', sans-serif",
            "font-weight": "800",
            "font-size": "13px",
            "text-transform": "uppercase",
            "letter-spacing": "1.5px",
            "background-opacity": 0.03,
            "border-style": "dashed",
            "border-width": "2px",
            "padding": "20px",
            "events": "no",  # Group boxes are not tappable
            "transition-property": "opacity, border-color, background-color",
            "transition-duration": "0.38s",
            "transition-timing-function": "cubic-bezier(0.25, 0.1, 0.25, 1)",
        },
    },
    # Group box color variants & specialized label positioning
    {
        "selector": "node.group-sensors",
        "style": {
            "border-color": "#ef4444",
            "color": "#b91c1c",
            "background-color": "#ef4444",
            "text-valign": "top",
            "text-halign": "center",
            "text-margin-y": 12,
        },
    },
    {
        "selector": "node.group-computation",
        "style": {
            "border-color": "#10b981",
            "color": "#047857",
            "background-color": "#10b981",
            "text-valign": "bottom",
            "text-halign": "center",
            "text-margin-y": -12,
        },
    },
    {
        "selector": "node.group-dtsync",
        "style": {
            "border-color": "#3b82f6",
            "color": "#1d4ed8",
            "background-color": "#3b82f6",
            "text-valign": "top",
            "text-halign": "center",
            "text-margin-y": 12,
        },
    },
    {
        "selector": "node.group-decision",
        "style": {
            "border-color": "#8b5cf6",
            "color": "#6d28d9",
            "background-color": "#8b5cf6",
            "text-valign": "top",
            "text-halign": "center",
            "text-margin-y": 12,
        },
    },

    # Base Nodes (Rectangles for system modules, matching reference architecture)
    {
        "selector": "node.bubble-node",
        "style": {
            "shape": "round-rectangle",
            "corner-radius": "10px",
            "width": "116px",
            "height": "62px",
            "label": "data(display_label)",
            "text-valign": "center",
            "text-halign": "center",
            "text-wrap": "wrap",
            "text-max-width": "104px",
            "font-family": "'Barlow Semi Condensed', 'Arial Narrow', sans-serif",
            "font-weight": "700",
            "font-size": "12.5px",
            "line-height": 1.2,
            "color": "#0f172a",
            "background-color": "#ffffff",
            "border-width": "2.5px",
            "border-style": "solid",
            "border-color": "#1e293b",
            "cursor": "pointer",
            "transition-property": "opacity, border-color, border-width, background-color, width, height",
            "transition-duration": "0.38s",
            "transition-timing-function": "cubic-bezier(0.25, 0.1, 0.25, 1)",
        },
    },
    {
        "selector": "node.bubble-node:active",
        "style": {
            "overlay-color": "#f59e0b",
            "overlay-opacity": 0.18,
            "overlay-padding": "10px",
        },
    },

    # Node Category Styles
    # 1. Sensors (LIDAR, Hyper, RGB/Video): white card with crisp dark border
    {
        "selector": "node.sensor-node",
        "style": {
            "background-color": "#ffffff",
            "border-color": "#1e293b",
            "border-width": "2.5px",
        },
    },
    # 2. Computation (SAC, VTL): white card with crisp dark border
    {
        "selector": "node.project-node",
        "style": {
            "background-color": "#ffffff",
            "border-color": "#1e293b",
            "border-width": "2.5px",
        },
    },
    # 3. Fuel Tank: Distinctive Oval/Ellipse matching reference slide
    {
        "selector": "node.asset-node",
        "style": {
            "shape": "ellipse",
            "width": "118px",
            "height": "76px",
            "text-max-width": "98px",
            "font-size": "12.5px",
            "background-color": "#ffffff",
            "border-color": "#1e293b",
            "border-width": "2.5px",
        },
    },
    # 4. Digital Twin (DT): Distinctive Oval/Ellipse matching reference slide
    {
        "selector": "node.twin-node",
        "style": {
            "shape": "ellipse",
            "width": "118px",
            "height": "76px",
            "text-max-width": "98px",
            "font-size": "12.5px",
            "background-color": "#ffffff",
            "border-color": "#1e293b",
            "border-width": "2.5px",
        },
    },
    # 5. LRMS Long Range Maintenance Schedule: Solid Cyan-Blue Box with Bold White Text (Matching Slide)
    {
        "selector": "node.samm-node",
        "style": {
            "shape": "round-rectangle",
            "corner-radius": "10px",
            "width": "116px",
            "height": "62px",
            "background-color": "#0284c7",
            "border-color": "#0369a1",
            "border-width": "2.5px",
            "color": "#ffffff",
            "font-weight": "800",
        },
    },
    # 6. HMS Hull Maintenance System: Solid Green Box with Bold White Text (Matching Slide)
    {
        "selector": "node.cms-node",
        "style": {
            "shape": "round-rectangle",
            "corner-radius": "10px",
            "width": "116px",
            "height": "62px",
            "background-color": "#10b981",
            "border-color": "#059669",
            "border-width": "2.5px",
            "color": "#ffffff",
            "font-weight": "800",
        },
    },
    # 7. Next Link (Phase 4): Pale amber with dashed border
    {
        "selector": "node.external-node",
        "style": {
            "shape": "round-rectangle",
            "corner-radius": "10px",
            "width": "116px",
            "height": "62px",
            "background-color": "#fef3c7",
            "border-color": "#f59e0b",
            "border-style": "dashed",
            "border-width": "2.5px",
        },
    },

    # Selection & Highlighting States (Selected node stands out boldly with zero opacity fading)
    {
        "selector": "node.node-selected",
        "style": {
            "border-color": "#d97706",          # Rich Amber
            "border-width": "6px",
            "opacity": 1.0,
            "z-index": 9999,
            "underlay-color": "#f59e0b",
            "underlay-padding": "10px",
            "underlay-opacity": 0.38,
            "underlay-shape": "round-rectangle",
        },
    },
    # Selected underlay shape for elliptical nodes
    {
        "selector": "node.asset-node.node-selected, node.twin-node.node-selected",
        "style": {
            "underlay-shape": "ellipse",
            "background-color": "#f1f5f9",
            "border-color": "#d97706",
            "color": "#0f172a",
        },
    },
    # Selected category background accents
    {
        "selector": "node.sensor-node.node-selected, node.project-node.node-selected",
        "style": {
            "background-color": "#fef3c7",
            "border-color": "#d97706",
            "color": "#0f172a",
        },
    },
    {
        "selector": "node.samm-node.node-selected",
        "style": {
            "background-color": "#0369a1",
            "border-color": "#f59e0b",
            "color": "#ffffff",
        },
    },
    {
        "selector": "node.cms-node.node-selected",
        "style": {
            "background-color": "#047857",
            "border-color": "#f59e0b",
            "color": "#ffffff",
        },
    },
    {
        "selector": "node.external-node.node-selected",
        "style": {
            "background-color": "#fef08a",
            "border-color": "#d97706",
        },
    },

    # Connected Nodes in current phase
    {
        "selector": "node.node-connected",
        "style": {
            "border-color": "#f59e0b",
            "border-width": "3.5px",
            "opacity": 1.0,
            "z-index": 900,
            "underlay-color": "#fde68a",
            "underlay-padding": "5px",
            "underlay-opacity": 0.25,
            "underlay-shape": "round-rectangle",
        },
    },
    {
        "selector": "node.asset-node.node-connected, node.twin-node.node-connected",
        "style": {
            "underlay-shape": "ellipse",
        },
    },

    # Dimmed Nodes (Unconnected)
    {
        "selector": "node.node-dimmed",
        "style": {
            "opacity": 0.22,
            "z-index": 10,
        },
    },

    # Group Dimmed - NEVER set 'opacity' directly on compound parent nodes,
    # because Cytoscape propagates parent opacity to all children!
    # Instead, dim only the border, text, and background fill of the group container.
    {
        "selector": "node.group-dimmed",
        "style": {
            "border-opacity": 0.20,
            "text-opacity": 0.25,
            "background-opacity": 0.01,
        },
    },

    # Invisible Boundary Anchors (Lock coordinates to exactly 1000 x 620)
    {
        "selector": "node.boundary-anchor",
        "style": {
            "opacity": 0,
            "events": "no",
            "width": "1px",
            "height": "1px",
            "border-width": "0px",
        },
    },

    # Edges - Solid clean blue matching the proof of concept reference
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "arrow-scale": 1.25,
            "line-color": "#2563eb",
            "target-arrow-color": "#2563eb",
            "width": 2.5,
            "label": "data(label)",
            "font-size": "10.5px",
            "font-weight": "700",
            "font-family": "'Barlow Semi Condensed', 'Inter', system-ui, sans-serif",
            "color": "#1e293b",
            "text-background-color": "#ffffff",
            "text-background-opacity": 0.96,
            "text-background-padding": "2px",
            "text-background-shape": "roundrectangle",
            "text-rotation": "autorotate",
            "text-margin-y": -2,
            "transition-property": "opacity, line-color, target-arrow-color, source-arrow-color, width",
            "transition-duration": "0.35s",
            "transition-timing-function": "cubic-bezier(0.25, 0.1, 0.25, 1)",
        },
    },
    # Dashed Feedback Edge (SAC -> LiDAR confidence score check > 0.83)
    {
        "selector": "edge.dashed-edge",
        "style": {
            "line-style": "dashed",
            "line-dash-pattern": [6, 4],
            "line-color": "#94a3b8",
            "target-arrow-color": "#94a3b8",
            "color": "#64748b",
        },
    },
    # Two-way bidirectional arrow for tank <-> twin ("sync")
    {
        "selector": "edge.bidirectional",
        "style": {
            "source-arrow-shape": "triangle",
            "source-arrow-color": "#2563eb",
            "arrow-scale": 1.3,
        },
    },
    # Highlighted edge (amber)
    {
        "selector": "edge.edge-highlighted",
        "style": {
            "line-color": "#d97706",
            "target-arrow-color": "#d97706",
            "source-arrow-color": "#d97706",
            "width": 4.5,
            "opacity": 1.0,
            "z-index": 99,
        },
    },
    # Dimmed edge
    {
        "selector": "edge.edge-dimmed",
        "style": {
            "opacity": 0.12,
        },
    },
]


# =============================================================================
# HELPER FUNCTIONS: GRAPH ELEMENTS
# =============================================================================

def build_elements(phase: int, selected_node_id: Optional[str] = None, is_initial: bool = False) -> List[Dict[str, Any]]:
    """Build Cytoscape element dictionaries for the given phase and selection state."""
    elements: List[Dict[str, Any]] = []

    # 1. Coordinate frame anchors (preserve 1000 x 620 coordinate box)
    elements.append({
        "data": {"id": "__anchor_tl"},
        "position": {"x": 0, "y": 0},
        "classes": "boundary-anchor",
    })
    elements.append({
        "data": {"id": "__anchor_br"},
        "position": {"x": 1000, "y": 620},
        "classes": "boundary-anchor",
    })

    # Nodes visible in this phase
    phase_positions = CONTENT["positions"].get(phase, {})
    visible_node_ids = set(phase_positions.keys())

    # Find connected nodes and edges if a node is selected
    connected_node_ids = set()
    highlighted_edge_ids = set()
    active_edge_defs = []

    for edge in CONTENT["edges"]:
        if phase in edge["phases"]:
            src, tgt = edge["source"], edge["target"]
            if src in visible_node_ids and tgt in visible_node_ids:
                edge_id = f"{src}->{tgt}"
                active_edge_defs.append((edge_id, edge))
                if selected_node_id:
                    if src == selected_node_id:
                        connected_node_ids.add(tgt)
                        highlighted_edge_ids.add(edge_id)
                    elif tgt == selected_node_id:
                        connected_node_ids.add(src)
                        highlighted_edge_ids.add(edge_id)

    # 2. Add Groups (compound parent nodes) if they have visible children
    selected_group = CONTENT["nodes"].get(selected_node_id, {}).get("group") if selected_node_id else None

    for grp_id, grp_info in CONTENT["groups"].items():
        if phase in grp_info["phases"]:
            has_children = any(
                CONTENT["nodes"][nid].get("group") == grp_id
                for nid in visible_node_ids
                if nid in CONTENT["nodes"]
            )
            if has_children:
                grp_classes = f"group-box group-{grp_id}"
                # Only dim groups that do not contain the selected node
                if selected_node_id and grp_id != selected_group:
                    grp_classes += " group-dimmed"
                elements.append({
                    "data": {
                        "id": grp_id,
                        "label": grp_info["label"],
                        "is_group": True,
                    },
                    "classes": grp_classes,
                })

    # 3. Add Bubble Nodes
    for node_id in visible_node_ids:
        node_info = CONTENT["nodes"][node_id]
        pos = phase_positions[node_id]
        style_type = node_info["style"]

        display_label = f"{node_info['label']}\n{node_info['sublabel']}"

        classes = ["bubble-node", f"{style_type}-node"]

        if selected_node_id is not None:
            if node_id == selected_node_id:
                classes.append("node-selected")
            elif node_id in connected_node_ids:
                classes.append("node-connected")
            else:
                classes.append("node-dimmed")

        node_data: Dict[str, Any] = {
            "id": node_id,
            "label": node_info["label"],
            "sublabel": node_info["sublabel"],
            "display_label": display_label,
            "style_type": style_type,
            "is_group": False,
        }
        if node_info.get("group"):
            node_data["parent"] = node_info["group"]

        node_el: Dict[str, Any] = {
            "data": node_data,
            "classes": " ".join(classes),
        }

        # Always assign exact coordinates so preset layout and cy.animate() stay perfectly in sync
        node_el["position"] = {"x": pos[0], "y": pos[1]}

        elements.append(node_el)

    # 4. Add Edges
    for edge_id, edge in active_edge_defs:
        src, tgt = edge["source"], edge["target"]
        classes = ["normal-edge"]
        if edge.get("bidirectional"):
            classes.append("bidirectional")
        if edge.get("style") == "dashed":
            classes.append("dashed-edge")

        if selected_node_id is not None:
            if edge_id in highlighted_edge_ids:
                classes.append("edge-highlighted")
            else:
                classes.append("edge-dimmed")

        elements.append({
            "data": {
                "id": edge_id,
                "source": src,
                "target": tgt,
                "label": edge.get("label", ""),
            },
            "classes": " ".join(classes),
        })

    return elements


def get_node_connections(node_id: str, phase: int):
    """Retrieve lists of incoming and outgoing connections for a node in a given phase."""
    visible_node_ids = set(CONTENT["positions"].get(phase, {}).keys())
    receives_from = []
    sends_to = []

    for edge in CONTENT["edges"]:
        if phase in edge["phases"]:
            src, tgt = edge["source"], edge["target"]
            if src not in visible_node_ids or tgt not in visible_node_ids:
                continue

            lbl = edge.get("label", "").strip()
            label_suffix = f" · \"{lbl}\"" if lbl else ""
            is_bidi = edge.get("bidirectional", False)

            if tgt == node_id:
                src_label = CONTENT["nodes"][src]["label"]
                receives_from.append(f"{src_label}{label_suffix}")
            elif is_bidi and src == node_id:
                tgt_label = CONTENT["nodes"][tgt]["label"]
                receives_from.append(f"{tgt_label}{label_suffix}")

            if src == node_id:
                tgt_label = CONTENT["nodes"][tgt]["label"]
                sends_to.append(f"{tgt_label}{label_suffix}")
            elif is_bidi and tgt == node_id:
                src_label = CONTENT["nodes"][src]["label"]
                sends_to.append(f"{src_label}{label_suffix}")

    return receives_from, sends_to


# =============================================================================
# HELPER FUNCTIONS: PHASE 3 SHIP & SENSOR VECTOR GRAPHIC
# =============================================================================

def render_ship_svg(scenario: str = "clean") -> str:
    """Generate high-resolution SVG of the vessel, cutaway tank, and sensors with dynamic defect states."""
    
    # Dynamic defect overlay on the Port Bulkhead wall
    if scenario == "rust":
        defect_svg = """
        <!-- RUST DEFECT OVERLAY -->
        <g id="rust-defect-group">
            <!-- Organic Rust Patches on Port Bulkhead Plate (x=736 to 768, y=268 to 345) -->
            <path d="M 732 272 Q 748 260 766 270 Q 774 290 764 318 Q 748 344 728 335 Q 714 310 732 272 Z" fill="#7c2d12" opacity="0.95" />
            <path d="M 738 278 Q 752 270 762 282 Q 768 298 758 316 Q 744 332 732 322 Q 722 304 738 278 Z" fill="#c2410c" />
            <path d="M 744 286 Q 754 282 758 292 Q 762 306 754 314 Q 742 320 736 310 Q 730 298 744 286 Z" fill="#ea580c" />
            
            <!-- Rust Droplets & Stains Running Down -->
            <path d="M 738 330 Q 739 350 740 370" stroke="#7c2d12" stroke-width="3.5" stroke-linecap="round" opacity="0.9" />
            <path d="M 748 326 Q 750 354 749 382" stroke="#9a3412" stroke-width="4" stroke-linecap="round" opacity="0.95" />
            <path d="M 760 320 Q 762 344 761 364" stroke="#c2410c" stroke-width="2.5" stroke-linecap="round" opacity="0.8" />
            
            <!-- Pulsing Concentric Defect Reticle -->
            <circle cx="746" cy="302" r="28" stroke="#ef4444" stroke-width="2.5" fill="none" opacity="0.85" stroke-dasharray="5 3" />
            <circle cx="746" cy="302" r="16" stroke="#f59e0b" stroke-width="2" fill="rgba(239, 68, 68, 0.25)" />
            <circle cx="746" cy="302" r="5" fill="#ef4444" />
            
            <!-- Focused Hyperspectral Detection Beam locked onto Rust -->
            <polygon points="660,196 734,285 758,320" fill="url(#hypActiveBeam)" opacity="0.75" />
            <line x1="660" y1="196" x2="746" y2="302" stroke="#f97316" stroke-width="3" stroke-dasharray="6 3" />
            
            <!-- Defect Callout Bracket -->
            <g transform="translate(640, 248)">
                <rect x="-15" y="-22" width="168" height="26" rx="6" fill="#1e293b" stroke="#ef4444" stroke-width="2" />
                <text x="69" y="-5" fill="#ffffff" font-size="11.5" font-family="'Barlow Semi Condensed', sans-serif" font-weight="800" text-anchor="middle">
                    ⚠️ Fe₂O₃ RUST DETECTED (-1.8mm)
                </text>
            </g>
        </g>
        """
    elif scenario == "repaired":
        defect_svg = """
        <!-- REPAIR / RECOATED OVERLAY -->
        <g id="repaired-defect-group">
            <!-- Fresh Marine Protective Epoxy Patch -->
            <path d="M 732 270 Q 748 260 766 268 Q 775 288 766 318 Q 748 344 728 335 Q 714 310 732 270 Z" fill="#0284c7" opacity="0.85" stroke="#38bdf8" stroke-width="2.5" />
            <!-- Robotic Recoating Spray Grid Pattern -->
            <path d="M 734 285 L 764 285 M 732 300 L 766 300 M 735 315 L 762 315" stroke="#bae6fd" stroke-width="1.5" stroke-dasharray="4 2" />
            
            <!-- Checkmark Success Badge -->
            <g transform="translate(640, 248)">
                <rect x="-15" y="-22" width="168" height="26" rx="6" fill="#0f172a" stroke="#0ea5e9" stroke-width="2" />
                <text x="69" y="-5" fill="#38bdf8" font-size="11.5" font-family="'Barlow Semi Condensed', sans-serif" font-weight="800" text-anchor="middle">
                    ✓ RECOATED VIA LRMS ACTION
                </text>
            </g>
        </g>
        """
    else:  # Clean nominal
        defect_svg = """
        <!-- NOMINAL CLEAN WALL -->
        <g id="clean-status-tag" transform="translate(650, 252)">
            <rect x="-15" y="-22" width="150" height="24" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5" opacity="0.9" />
            <text x="60" y="-6" fill="#10b981" font-size="11" font-family="'Barlow Semi Condensed', sans-serif" font-weight="800" text-anchor="middle">
                ✓ COATING HEALTHY (100%)
            </text>
        </g>
        """

    svg = f"""
    <svg viewBox="0 0 1000 480" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <!-- Ocean Gradient -->
            <linearGradient id="oceanGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#0284c7" stop-opacity="0.35" />
                <stop offset="60%" stop-color="#0369a1" stop-opacity="0.75" />
                <stop offset="100%" stop-color="#0c4a6e" stop-opacity="0.95" />
            </linearGradient>

            <!-- Tank Interior Gradient -->
            <linearGradient id="tankInteriorGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#1e293b" />
                <stop offset="100%" stop-color="#0f172a" />
            </linearGradient>

            <!-- Fuel Liquid Gradient -->
            <linearGradient id="fuelGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.3" />
                <stop offset="100%" stop-color="#d97706" stop-opacity="0.65" />
            </linearGradient>

            <!-- LiDAR Beam Fan -->
            <linearGradient id="lidarBeam" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.65" />
                <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.05" />
            </linearGradient>

            <!-- Hyperspectral Ambient Beam -->
            <linearGradient id="hypBeam" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#f97316" stop-opacity="0.5" />
                <stop offset="100%" stop-color="#f97316" stop-opacity="0.05" />
            </linearGradient>

            <!-- Hyperspectral Active Rust Beam -->
            <linearGradient id="hypActiveBeam" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ea580c" stop-opacity="0.85" />
                <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.2" />
            </linearGradient>

            <!-- RGB Camera Cone -->
            <linearGradient id="rgbCone" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#10b981" stop-opacity="0.45" />
                <stop offset="100%" stop-color="#10b981" stop-opacity="0.03" />
            </linearGradient>
        </defs>

        <!-- Sky Background -->
        <rect width="1000" height="480" fill="#f8fafc" />

        <!-- Ocean Water Profile -->
        <path d="M 0 350 Q 250 345 500 350 T 1000 350 L 1000 480 L 0 480 Z" fill="url(#oceanGrad)" />
        <path d="M 0 354 Q 150 348 300 354 T 600 354 T 900 354 T 1000 354" stroke="#38bdf8" stroke-width="1.8" fill="none" opacity="0.5" />
        <path d="M 0 366 Q 200 360 400 366 T 800 366 T 1000 366" stroke="#bae6fd" stroke-width="1.2" fill="none" opacity="0.3" />

        <!-- Waterline Depth Calibration Ruler -->
        <g font-family="'Inter', sans-serif" font-size="9" fill="#94a3b8" font-weight="600">
            <line x1="970" y1="350" x2="985" y2="350" stroke="#94a3b8" stroke-width="1.5" />
            <text x="965" y="353" text-anchor="end">0m (WL)</text>
            <line x1="975" y1="380" x2="985" y2="380" stroke="#94a3b8" stroke-width="1" />
            <text x="970" y="383" text-anchor="end">-5m</text>
            <line x1="975" y1="410" x2="985" y2="410" stroke="#94a3b8" stroke-width="1" />
            <text x="970" y="413" text-anchor="end">-10m</text>
        </g>

        <!-- SHIP PROFILE (Commercial MSC Cargo Hull) -->
        <g id="ship-hull">
            <!-- Underwater Hull Section (Antifouling Marine Red) -->
            <path d="M 70 350 L 60 410 Q 150 415 350 415 L 750 415 Q 900 415 950 395 Q 960 380 940 350 Z" fill="#991b1b" stroke="#7f1d1d" stroke-width="2" />
            
            <!-- Above-Water Main Hull (Dark Naval Slate Plating) -->
            <path d="M 50 280 L 50 350 L 940 350 L 930 170 L 80 170 L 50 280 Z" fill="#0f172a" stroke="#1e293b" stroke-width="2" />
            
            <!-- Bulbous Bow at Under-Waterline Keel -->
            <path d="M 940 375 Q 965 385 962 400 Q 950 412 925 412" fill="#991b1b" stroke="#7f1d1d" stroke-width="2" />

            <!-- Deck Railings & Bulwark -->
            <line x1="80" y1="168" x2="930" y2="168" stroke="#cbd5e1" stroke-width="1.8" />
            
            <!-- Superstructure / Navigation Bridge Tower (Aft) -->
            <g id="bridge-tower">
                <rect x="110" y="80" width="110" height="90" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
                <rect x="125" y="60" width="80" height="20" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.5" />
                <!-- Bridge Windows -->
                <rect x="130" y="64" width="70" height="10" fill="#0284c7" opacity="0.85" rx="2" />
                <!-- MSC Yellow/Black Funnel with Exhaust -->
                <rect x="90" y="70" width="22" height="60" fill="#eab308" stroke="#ca8a04" stroke-width="1.5" />
                <rect x="90" y="70" width="22" height="12" fill="#0f172a" />
                <!-- Radar Antenna Mast -->
                <line x1="165" y1="60" x2="165" y2="35" stroke="#64748b" stroke-width="2" />
                <line x1="150" y1="40" x2="180" y2="40" stroke="#64748b" stroke-width="2.5" />
            </g>

            <!-- Cargo Container Stacks (Forward and Aft of Tank) -->
            <g id="containers">
                <!-- Aft Stack -->
                <rect x="235" y="110" width="45" height="58" fill="#0369a1" stroke="#0284c7" stroke-width="1.5" />
                <rect x="285" y="95" width="45" height="73" fill="#b91c1c" stroke="#dc2626" stroke-width="1.5" />
                <!-- Forward Stack -->
                <rect x="790" y="105" width="50" height="63" fill="#047857" stroke="#10b981" stroke-width="1.5" />
                <rect x="845" y="120" width="48" height="48" fill="#d97706" stroke="#f59e0b" stroke-width="1.5" />
            </g>

            <!-- Ship Hull Identification Text -->
            <text x="140" y="155" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-weight="800" font-size="11" letter-spacing="1">MSC MARITIME</text>
            <text x="915" y="200" fill="#cbd5e1" font-family="'Barlow Semi Condensed', sans-serif" font-weight="700" font-size="9" text-anchor="end">BOW</text>
        </g>

        <!-- CUTAWAY COMPARTMENT: FUEL OIL TANK B-3 (Midships, Port) -->
        <g id="tank-cutaway">
            <!-- Cutaway Outer Chamber Frame (Double Steel Hull Bulkheads) -->
            <rect x="335" y="176" width="450" height="236" fill="#0f172a" stroke="#38bdf8" stroke-width="3" rx="6" />
            
            <!-- Tank Interior Chamber -->
            <rect x="340" y="181" width="440" height="226" fill="url(#tankInteriorGrad)" />

            <!-- Steel Double-Hull Ribs / Transverse Frames -->
            <g stroke="#334155" stroke-width="2.5" opacity="0.7">
                <line x1="410" y1="181" x2="410" y2="407" />
                <line x1="480" y1="181" x2="480" y2="407" />
                <line x1="640" y1="181" x2="640" y2="407" />
                <line x1="710" y1="181" x2="710" y2="407" />
            </g>

            <!-- Central Transverse Baffle Plate with Lightening / Wash Holes -->
            <g id="baffle-plate">
                <rect x="556" y="181" width="10" height="226" fill="#334155" stroke="#475569" stroke-width="1" />
                <!-- Wash Holes in Baffle -->
                <ellipse cx="561" cy="235" rx="3.5" ry="18" fill="#1e293b" />
                <ellipse cx="561" cy="295" rx="3.5" ry="18" fill="#1e293b" />
                <ellipse cx="561" cy="355" rx="3.5" ry="18" fill="#1e293b" />
            </g>

            <!-- Fuel Liquid Layer (Marine Gas Oil) at Bottom of Tank -->
            <g id="fuel-liquid">
                <path d="M 340 338 Q 440 334 560 338 T 780 338 L 780 407 L 340 407 Z" fill="url(#fuelGrad)" />
                <path d="M 340 338 Q 440 334 560 338 T 780 338" stroke="#fbbf24" stroke-width="1.5" fill="none" opacity="0.8" />
                <!-- Suction Bellmouth / Sump Drain at Bottom -->
                <path d="M 450 407 L 460 392 L 470 392 L 480 407 Z" fill="#475569" />
                <text x="350" y="400" fill="#fef3c7" font-family="'Inter', sans-serif" font-size="9" font-weight="600" opacity="0.85">MGO LEVEL: 64%</text>
            </g>

            <!-- Top Access Manhole Dome and Inspection Hatch -->
            <g id="tank-hatch">
                <rect x="440" y="172" width="40" height="9" fill="#475569" stroke="#64748b" stroke-width="1.5" rx="2" />
                <!-- Inspection Ladder -->
                <g stroke="#64748b" stroke-width="1.5" opacity="0.65">
                    <line x1="365" y1="181" x2="365" y2="340" />
                    <line x1="375" y1="181" x2="375" y2="340" />
                    <line x1="365" y1="205" x2="375" y2="205" />
                    <line x1="365" y1="225" x2="375" y2="225" />
                    <line x1="365" y1="245" x2="375" y2="245" />
                    <line x1="365" y1="265" x2="375" y2="265" />
                    <line x1="365" y1="285" x2="375" y2="285" />
                </g>
            </g>

            <!-- Port Bulkhead Wall (Right Plate, x=768) -->
            <rect x="768" y="181" width="12" height="226" fill="#1e293b" stroke="#475569" stroke-width="1.5" />

            <!-- ================= SENSORS IN TANK ================= -->

            <!-- Sensor 1: LiDAR 3D Scanner (Top Center, x=460, y=186) -->
            <g id="sensor-lidar">
                <!-- Laser Scan Rays Fan -->
                <polygon points="460,192 350,335 770,335" fill="url(#lidarBeam)" opacity="0.4" />
                <line x1="460" y1="192" x2="360" y2="335" stroke="#06b6d4" stroke-width="1" stroke-dasharray="4 3" opacity="0.7" />
                <line x1="460" y1="192" x2="430" y2="335" stroke="#06b6d4" stroke-width="1" stroke-dasharray="4 3" opacity="0.7" />
                <line x1="460" y1="192" x2="520" y2="335" stroke="#06b6d4" stroke-width="1" stroke-dasharray="4 3" opacity="0.7" />
                <line x1="460" y1="192" x2="620" y2="335" stroke="#06b6d4" stroke-width="1" stroke-dasharray="4 3" opacity="0.7" />
                <line x1="460" y1="192" x2="720" y2="310" stroke="#06b6d4" stroke-width="1" stroke-dasharray="4 3" opacity="0.7" />
                <!-- LiDAR Housing Dome -->
                <circle cx="460" cy="188" r="8" fill="#0f172a" stroke="#06b6d4" stroke-width="2.5" />
                <circle cx="460" cy="188" r="3.5" fill="#06b6d4" />
                <!-- Label Pill -->
                <rect x="424" y="198" width="72" height="16" rx="4" fill="#0f172a" stroke="#06b6d4" stroke-width="1" />
                <text x="460" y="210" fill="#06b6d4" font-family="'Barlow Semi Condensed', sans-serif" font-weight="800" font-size="9.5" text-anchor="middle">LiDAR 3D</text>
            </g>

            <!-- Sensor 2: RGB / Video Camera (Top Left Gimbal, x=385, y=192) -->
            <g id="sensor-rgb">
                <!-- Optical FOV Cone -->
                <polygon points="385,195 400,320 540,320" fill="url(#rgbCone)" opacity="0.5" />
                <line x1="385" y1="195" x2="540" y2="320" stroke="#10b981" stroke-width="1" stroke-dasharray="4 3" opacity="0.6" />
                <!-- Camera Gimbal -->
                <rect x="378" y="186" width="14" height="12" fill="#0f172a" stroke="#10b981" stroke-width="2" rx="2" />
                <circle cx="385" cy="192" r="3" fill="#10b981" />
                <!-- Label Pill -->
                <rect x="352" y="202" width="66" height="16" rx="4" fill="#0f172a" stroke="#10b981" stroke-width="1" />
                <text x="385" y="214" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-weight="800" font-size="9.5" text-anchor="middle">RGB VIDEO</text>
            </g>

            <!-- Sensor 3: Hyperspectral Sensor (Top Right, x=660, y=190) -->
            <g id="sensor-hyp">
                <!-- Ambient Scanning Cone (Angled toward Port Bulkhead) -->
                {"" if scenario == "rust" else '<polygon points="660,195 720,260 770,320" fill="url(#hypBeam)" opacity="0.6" />'}
                {"" if scenario == "rust" else '<line x1="660" y1="195" x2="765" y2="290" stroke="#f97316" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.7" />'}
                <!-- Hyperspectral Sensor Housing -->
                <polygon points="652,185 668,185 664,196 656,196" fill="#0f172a" stroke="#f97316" stroke-width="2.5" />
                <circle cx="660" cy="196" r="3.5" fill="#f97316" />
                <!-- Label Pill -->
                <rect x="618" y="202" width="84" height="16" rx="4" fill="#0f172a" stroke="#f97316" stroke-width="1" />
                <text x="660" y="214" fill="#f97316" font-family="'Barlow Semi Condensed', sans-serif" font-weight="800" font-size="9.5" text-anchor="middle">HYPERSPECTRAL</text>
            </g>

            <!-- Dynamic Defect Layer (Rust / Repair / Clean) -->
            {defect_svg}

            <!-- Tank Metadata Labels -->
            <g font-family="'Barlow Semi Condensed', sans-serif" font-weight="800" font-size="10">
                <text x="350" y="196" fill="#cbd5e1" letter-spacing="1">MSC TANK B-3</text>
                <text x="770" y="196" fill="#cbd5e1" text-anchor="end">PORT BULKHEAD (FRAME 38)</text>
            </g>
        </g>
    </svg>
    """
    return svg


# =============================================================================
# SENSOR & COMPONENT INSPECTION IMAGES CONFIGURATION
# Enter the file path (JPG, PNG, WebP) in quotes for each popup below.
# Whenever a path is set, the popup displays NOTHING BUT THAT IMAGE.
# If left as None or "", a clean placeholder slot is displayed.
# These images automatically compile and embed themselves as base64 data URIs
# into the standalone HTML file so it opens anywhere on any device!
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets" / "images"
UPLOADS_DIR = PROJECT_ROOT / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Place LiDAR image here
IMAGE_PATH_LIDAR: Optional[str] = str(UPLOADS_DIR / "lidar.jpg") if (UPLOADS_DIR / "lidar.jpg").is_file() else None

# Place RGB / Video camera image here
IMAGE_PATH_RGB: Optional[str] = None  # e.g. r"C:\path\to\rgb_inspection.jpg"

# Place Hyperspectral camera image here
IMAGE_PATH_HYP: Optional[str] = str(ASSETS_DIR / "hyperspectral.jpg") if (ASSETS_DIR / "hyperspectral.jpg").is_file() else None

# Place SAC (Surface Area Calculation) image here
IMAGE_PATH_SAC: Optional[str] = str(UPLOADS_DIR / "sac.jpg") if (UPLOADS_DIR / "sac.jpg").is_file() else None
IMAGE_PATH_BLENDER: Optional[str] = str(UPLOADS_DIR / "blender_remesh.jpg") if (UPLOADS_DIR / "blender_remesh.jpg").is_file() else None
IMAGE_PATH_AST_SLIDE: Optional[str] = str(UPLOADS_DIR / "ast_system_model.png") if (UPLOADS_DIR / "ast_system_model.png").is_file() else None

# Place VTL (Virtual Technical Library) image here
IMAGE_PATH_VTL: Optional[str] = None  # e.g. r"C:\path\to\vtl_scantling_record.jpg"

# Place LRMS (Long Range Maintenance Schedule) & HMS (Hull Maintenance System) images here
IMAGE_PATH_LRMS: Optional[str] = None  # e.g. r"C:\path\to\lrms_schedule.jpg"
IMAGE_PATH_SAMM: Optional[str] = IMAGE_PATH_LRMS  # backward-compatibility alias
IMAGE_PATH_HMS: Optional[str] = None   # e.g. r"C:\path\to\hms_analytics.jpg"
IMAGE_PATH_CMS: Optional[str] = IMAGE_PATH_HMS   # backward-compatibility alias

# Primary image file locations
IMAGE_PATHS: Dict[str, Optional[str]] = {
    "clean": str(ASSETS_DIR / "tank_clean.jpg"),
    "rust": str(ASSETS_DIR / "tank_rust.jpg"),
    "tank": str(ASSETS_DIR / "tank_clean.jpg"),
    "dt_clean": str(ASSETS_DIR / "dt_nominal.jpg"),
    "dt_rust": str(ASSETS_DIR / "dt_rust.jpg"),
    "twin": str(ASSETS_DIR / "dt_nominal.jpg"),
    "hyperspectral_cubert": IMAGE_PATH_HYP,
    "lidar": IMAGE_PATH_LIDAR,
    "rgb": IMAGE_PATH_RGB,
    "hyp": IMAGE_PATH_HYP,
    "sac": IMAGE_PATH_SAC,
    "blender": IMAGE_PATH_BLENDER,
    "blender_remesh": IMAGE_PATH_BLENDER,
    "ast_system_model": IMAGE_PATH_AST_SLIDE,
    "ast_slide": IMAGE_PATH_AST_SLIDE,
    "vtl": IMAGE_PATH_VTL,
    "lrms": IMAGE_PATH_LRMS,
    "samm": IMAGE_PATH_SAMM,
    "hms": IMAGE_PATH_HMS,
    "cms": IMAGE_PATH_CMS,
}

def load_image_as_base64(path_str: Optional[str]) -> str:
    """Read an image file and encode it as a standard base64 data URI for zero-latency browser rendering."""
    try:
        if not path_str:
            return ""
        p = Path(path_str)
        if p.is_file():
            with open(p, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                ext = p.suffix.lower().replace(".", "")
                mime = "image/svg+xml" if ext == "svg" else "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
                return f"data:{mime};base64,{encoded}"
    except Exception as e:
        print(f"Warning: Could not read image at {path_str}: {e}")
    return ""

IMAGE_DATA: Dict[str, str] = {
    key: load_image_as_base64(path)
    for key, path in IMAGE_PATHS.items()
}

UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

def _scan_uploads_folder():
    """Load any uploaded images from uploads/ directory so they are immediately available across all systems."""
    if not UPLOADS_DIR.is_dir():
        return
    for cand in UPLOADS_DIR.iterdir():
        if cand.is_file() and cand.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
            k = cand.stem.lower()
            b64 = load_image_as_base64(str(cand))
            if b64:
                IMAGE_PATHS[k] = str(cand)
                IMAGE_DATA[k] = b64
                if k in ("samm", "lrms"):
                    IMAGE_PATHS["samm"] = str(cand)
                    IMAGE_PATHS["lrms"] = str(cand)
                    IMAGE_DATA["samm"] = b64
                    IMAGE_DATA["lrms"] = b64
                elif k in ("cms", "hms"):
                    IMAGE_PATHS["cms"] = str(cand)
                    IMAGE_PATHS["hms"] = str(cand)
                    IMAGE_DATA["cms"] = b64
                    IMAGE_DATA["hms"] = b64

_scan_uploads_folder()

def save_uploaded_image_file(node_id: str, data_url: str):
    """Save an uploaded image permanently to uploads/ folder so it persists across all systems and devices."""
    try:
        if not data_url or "," not in data_url:
            return None
        header, b64_data = data_url.split(",", 1)
        ext = ".png"
        if "image/jpeg" in header or "image/jpg" in header:
            ext = ".jpg"
        elif "image/webp" in header:
            ext = ".webp"
        elif "image/svg" in header:
            ext = ".svg"

        file_path = UPLOADS_DIR / f"{node_id}{ext}"
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(b64_data))

        IMAGE_PATHS[node_id] = str(file_path)
        IMAGE_DATA[node_id] = data_url

        if node_id in ("samm", "lrms"):
            IMAGE_PATHS["samm"] = str(file_path)
            IMAGE_PATHS["lrms"] = str(file_path)
            IMAGE_DATA["samm"] = data_url
            IMAGE_DATA["lrms"] = data_url
        elif node_id in ("cms", "hms"):
            IMAGE_PATHS["cms"] = str(file_path)
            IMAGE_PATHS["hms"] = str(file_path)
            IMAGE_DATA["cms"] = data_url
            IMAGE_DATA["hms"] = data_url

        # Auto-compile into standalone HTML files
        try:
            import export_to_html
            export_to_html.generate_html()
        except Exception as ex:
            print(f"Notice auto-generating HTML: {ex}")

        return str(file_path)
    except Exception as e:
        print(f"Error saving image for {node_id}: {e}")
        return None

def remove_uploaded_image_file(node_id: str):
    """Remove an uploaded image from uploads/ folder and reset its state."""
    try:
        for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
            cand = UPLOADS_DIR / f"{node_id}{ext}"
            if cand.is_file():
                cand.unlink(missing_ok=True)
        IMAGE_PATHS.pop(node_id, None)
        IMAGE_DATA.pop(node_id, None)
        if node_id in ("samm", "lrms"):
            IMAGE_PATHS.pop("samm", None)
            IMAGE_PATHS.pop("lrms", None)
            IMAGE_DATA.pop("samm", None)
            IMAGE_DATA.pop("lrms", None)
        elif node_id in ("cms", "hms"):
            IMAGE_PATHS.pop("cms", None)
            IMAGE_PATHS.pop("hms", None)
            IMAGE_DATA.pop("cms", None)
            IMAGE_DATA.pop("hms", None)
        try:
            import export_to_html
            export_to_html.generate_html()
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"Error removing image for {node_id}: {e}")
        return False


def generate_digital_twin_tank_svg(scenario: str = "clean") -> str:
    """Generate interactive 3D SVG visualization of the Tank B-3 Digital Twin replica."""
    is_rust = (scenario == "rust")
    
    # Theme colors based on scenario
    primary_color = "#ef4444" if is_rust else "#06b6d4"
    accent_color = "#f97316" if is_rust else "#10b981"
    status_label = "ALERT: RUST DEFECT DETECTED" if is_rust else "SYNCHRONIZED · BULKHEAD NOMINAL"
    status_bg = "#450a0a" if is_rust else "#064e3b"
    status_border = "#ef4444" if is_rust else "#10b981"
    status_text = "#fca5a5" if is_rust else "#6ee7b7"
    health_text = "42% (CRITICAL)" if is_rust else "98% (NOMINAL)"
    health_color = "#ef4444" if is_rust else "#10b981"
    thickness_val = "16.2 mm (-1.8mm recess)" if is_rust else "18.0 mm (nominal)"
    thickness_color = "#f97316" if is_rust else "#38bdf8"
    spectral_val = "Fe2O3 Peak @ 850nm" if is_rust else "Zero oxidation (Clear)"
    spectral_color = "#ef4444" if is_rust else "#10b981"
    fr38_fill = "#ef4444" if is_rust else "#64748b"
    
    svg_parts = [
        '<svg viewBox="0 0 600 380" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%; display:block; background:#030712;">',
        '  <defs>',
        '    <linearGradient id="tankShellGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.9"/>',
        '      <stop offset="50%" stop-color="#1e293b" stop-opacity="0.4"/>',
        '      <stop offset="100%" stop-color="#0f172a" stop-opacity="0.9"/>',
        '    </linearGradient>',
        '    <radialGradient id="defectHeatmap" cx="50%" cy="50%" r="50%">',
        '      <stop offset="0%" stop-color="#ef4444" stop-opacity="0.95"/>',
        '      <stop offset="45%" stop-color="#ea580c" stop-opacity="0.75"/>',
        '      <stop offset="75%" stop-color="#f59e0b" stop-opacity="0.35"/>',
        '      <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>',
        '    </radialGradient>',
        '  </defs>',
        '  <!-- Background Grid -->',
        '  <g stroke="#1e293b" stroke-width="0.75" opacity="0.6">',
        '    <line x1="30" y1="55" x2="570" y2="55"/>',
        '    <line x1="30" y1="115" x2="570" y2="115"/>',
        '    <line x1="30" y1="175" x2="570" y2="175"/>',
        '    <line x1="30" y1="235" x2="570" y2="235"/>',
        '    <line x1="30" y1="295" x2="570" y2="295"/>',
        '    <line x1="110" y1="30" x2="110" y2="330"/>',
        '    <line x1="205" y1="30" x2="205" y2="330"/>',
        '    <line x1="300" y1="30" x2="300" y2="330"/>',
        '    <line x1="395" y1="30" x2="395" y2="330"/>',
        '    <line x1="490" y1="30" x2="490" y2="330"/>',
        '  </g>',
        '  <!-- Top HUD Header -->',
        '  <text x="24" y="26" fill="#38bdf8" font-family="sans-serif" font-size="12" font-weight="800" letter-spacing="1">VIRTUAL ASSET · DIGITAL TWIN REPLICA</text>',
        '  <text x="24" y="42" fill="#94a3b8" font-family="sans-serif" font-size="10" font-weight="600">CAD MODEL: MSC-TNK-B3-V2.1 · 42,850 MESH VERTICES</text>',
        f'  <rect x="390" y="14" width="186" height="26" rx="6" fill="{status_bg}" stroke="{status_border}" stroke-width="1.5"/>',
        f'  <text x="483" y="31" fill="{status_text}" font-family="sans-serif" font-size="9" font-weight="800" text-anchor="middle" letter-spacing="0.5">{status_label}</text>',
        '  <!-- 3D Tank Cylinder Geometry -->',
        '  <path d="M 140,95 L 460,95 L 460,275 L 140,275 Z" fill="url(#tankShellGrad)"/>',
        '  <ellipse cx="300" cy="95" rx="160" ry="32" fill="#0f172a" stroke="#0284c7" stroke-width="2" opacity="0.85"/>',
        '  <ellipse cx="300" cy="275" rx="160" ry="32" fill="#020617" stroke="#0284c7" stroke-width="2" opacity="0.85"/>',
        '  <line x1="140" y1="95" x2="140" y2="275" stroke="#0284c7" stroke-width="2"/>',
        '  <line x1="460" y1="95" x2="460" y2="275" stroke="#0284c7" stroke-width="2"/>',
        '  <!-- Frame Ribs -->',
        '  <g stroke="#0369a1" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.75">',
        '    <path d="M 190,98 C 190,120 190,250 190,278"/>',
        '    <path d="M 245,101 C 245,125 245,255 245,281"/>',
        '    <path d="M 300,102 C 300,130 300,260 300,282"/>',
        '    <path d="M 355,101 C 355,125 355,255 355,281"/>',
        '    <path d="M 410,98 C 410,120 410,250 410,278"/>',
        '  </g>',
        '  <!-- Frame Labels -->',
        '  <g fill="#64748b" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle">',
        '    <text x="190" y="295">FR 36</text>',
        '    <text x="245" y="297">FR 37</text>',
        f'    <text x="300" y="299" fill="{fr38_fill}">FR 38</text>',
        '    <text x="355" y="297">FR 39</text>',
        '    <text x="410" y="295">FR 40</text>',
        '  </g>',
        '  <!-- Horizontal Elevation Waterlines -->',
        '  <g stroke="#0891b2" stroke-width="0.9" stroke-dasharray="3 3" opacity="0.6">',
        '    <ellipse cx="300" cy="145" rx="156" ry="26" fill="none"/>',
        '    <ellipse cx="300" cy="195" rx="156" ry="26" fill="none"/>',
        '    <ellipse cx="300" cy="240" rx="156" ry="26" fill="none"/>',
        '  </g>',
        '  <g fill="#0891b2" font-family="sans-serif" font-size="8.5" font-weight="600">',
        '    <text x="466" y="148">-2.0m</text>',
        '    <text x="466" y="198">-4.0m</text>',
        '    <text x="466" y="243">-6.0m</text>',
        '  </g>',
        '  <!-- Sensor Origin Nodes -->',
        '  <g font-family="sans-serif" font-size="8" font-weight="700">',
        '    <circle cx="36" cy="90" r="4" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5"/>',
        '    <text x="44" y="93" fill="#38bdf8">LD-01 3D LASER</text>',
        '    <circle cx="36" cy="130" r="4" fill="#ea580c" stroke="#fb923c" stroke-width="1.5"/>',
        '    <text x="44" y="133" fill="#fb923c">HS-01 SPECTRAL</text>',
        '    <circle cx="36" cy="170" r="4" fill="#10b981" stroke="#34d399" stroke-width="1.5"/>',
        '    <text x="44" y="173" fill="#34d399">CAM-02 4K VIDEO</text>',
        '  </g>',
        '  <!-- Projection Rays -->',
        '  <g stroke="#38bdf8" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.65">',
        '    <line x1="36" y1="90" x2="300" y2="195"/>',
        '    <line x1="36" y1="130" x2="300" y2="195"/>',
        '    <line x1="36" y1="170" x2="300" y2="195"/>',
        '  </g>',
    ]
    if is_rust:
        svg_parts.extend([
            '  <!-- DEFECT HEATMAP OVERLAY ON TWIN BULKHEAD (FRAME 38 · ELEVATION -4.2M) -->',
            '  <ellipse cx="300" cy="195" rx="44" ry="28" fill="url(#defectHeatmap)"/>',
            '  <ellipse cx="300" cy="195" rx="22" ry="14" fill="#ef4444" opacity="0.8"/>',
            '  <ellipse cx="300" cy="195" rx="54" ry="34" fill="none" stroke="#f97316" stroke-width="1.5" stroke-dasharray="4 2"/>',
            '  <!-- Reticle -->',
            '  <g stroke="#ef4444" stroke-width="1.8" fill="none">',
            '    <path d="M 272,175 L 265,175 L 265,182"/>',
            '    <path d="M 328,175 L 335,175 L 335,182"/>',
            '    <path d="M 272,215 L 265,215 L 265,208"/>',
            '    <path d="M 328,215 L 335,215 L 335,208"/>',
            '    <line x1="300" y1="168" x2="300" y2="173"/>',
            '    <line x1="300" y1="217" x2="300" y2="222"/>',
            '    <line x1="260" y1="195" x2="265" y2="195"/>',
            '    <line x1="335" y1="195" x2="340" y2="195"/>',
            '  </g>',
            '  <circle cx="300" cy="195" r="5" fill="#fef08a" stroke="#dc2626" stroke-width="2"/>',
            '  <path d="M 315,185 L 365,145 L 375,145" stroke="#ef4444" stroke-width="1.5" fill="none"/>',
            '  <g transform="translate(375, 110)">',
            '    <rect width="190" height="74" rx="8" fill="#1e1b4b" stroke="#ef4444" stroke-width="1.8"/>',
            '    <rect width="190" height="22" rx="8" fill="#ef4444"/>',
            '    <text x="95" y="15" fill="#ffffff" font-family="sans-serif" font-size="9" font-weight="800" text-anchor="middle" letter-spacing="0.5">⚠️ RUST DEFECT DETECTED IN TWIN</text>',
            '    <text x="10" y="36" fill="#fca5a5" font-family="sans-serif" font-size="9" font-weight="700">LOCATION: FRAME 38 (ELEV -4.2M)</text>',
            '    <text x="10" y="50" fill="#fef08a" font-family="sans-serif" font-size="9" font-weight="600">3D RECESS: -1.8mm (4.8 m² AREA)</text>',
            '    <text x="10" y="64" fill="#67e8f9" font-family="sans-serif" font-size="8.5" font-weight="600">NIR SPECTRA: Fe₂O₃ PEAK @ 850nm</text>',
            '  </g>',
            '  <rect x="24" y="338" width="552" height="28" rx="6" fill="#450a0a" stroke="#dc2626" stroke-width="1.5"/>',
            '  <text x="300" y="356" fill="#fca5a5" font-family="sans-serif" font-size="10" font-weight="800" text-anchor="middle" letter-spacing="0.8">⚠️ PHYSICAL DEFECT CAUGHT BY REAL SHIP SENSORS & LOGGED IN DIGITAL TWIN</text>',
        ])
    else:
        svg_parts.extend([
            '  <g transform="translate(230, 175)">',
            '    <rect width="140" height="40" rx="8" fill="#022c22" stroke="#10b981" stroke-width="1.5" opacity="0.9"/>',
            '    <circle cx="18" cy="20" r="5" fill="#10b981"/>',
            '    <text x="32" y="17" fill="#6ee7b7" font-family="sans-serif" font-size="9.5" font-weight="800">BULKHEAD INTACT</text>',
            '    <text x="32" y="30" fill="#a7f3d0" font-family="sans-serif" font-size="8.5" font-weight="600">Nominal 18.0mm Steel</text>',
            '  </g>',
            '  <rect x="24" y="338" width="552" height="28" rx="6" fill="#022c22" stroke="#059669" stroke-width="1.2"/>',
            '  <text x="300" y="356" fill="#6ee7b7" font-family="sans-serif" font-size="10" font-weight="800" text-anchor="middle" letter-spacing="0.8">🟢 REAL SHIP SENSORS CONTINUOUSLY VERIFYING NOMINAL DIGITAL TWIN BASELINE</text>',
        ])
    svg_parts.extend([
        f'  <text x="24" y="320" fill="{thickness_color}" font-family="sans-serif" font-size="9" font-weight="700">PLATE THICKNESS: {thickness_val}</text>',
        f'  <text x="235" y="320" fill="{spectral_color}" font-family="sans-serif" font-size="9" font-weight="700">CHEMICAL NIR: {spectral_val}</text>',
        f'  <text x="455" y="320" fill="{health_color}" font-family="sans-serif" font-size="9" font-weight="800">TWIN HEALTH: {health_text}</text>',
        '</svg>'
    ])
    return "\n".join(svg_parts)


def get_digital_twin_svg_uri(scenario: str = "clean") -> str:
    """Encode the 3D Digital Twin SVG as a base64 Data URI for fast, zero-latency browser rendering."""
    svg_str = generate_digital_twin_tank_svg(scenario)
    encoded = base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


def render_ship_status_bar(scenario: str = "clean") -> List[Any]:
    """Render high-contrast engineering telemetry banner directly above the ship illustration."""
    sc = scenario or "clean"
    sc_info = CONTENT["ship_simulation"]["scenarios"].get(sc, CONTENT["ship_simulation"]["scenarios"]["clean"])

    if sc == "rust":
        status_icon = "⚠️"
        status_text = "RUST DEFECT DETECTED ON BULKHEAD (FRAME 38 · ELEVATION -4.2M)"
        status_sub = "Simulated physical change active · Caught in real-time by Hyperspectral HS-01, RGB CAM-02, and LiDAR LD-01"
        badge_bg = "#ef4444"
        badge_txt = "#ffffff"
        text_accent = "#f87171"
    else:
        status_icon = "🟢"
        status_text = "NOMINAL BASELINE: MSC BALLAST TANK WITH 3 ACTIVE INSPECTION SENSORS"
        status_sub = "LiDAR 3D (Geometry) · Hyperspectral (Chemical NIR) · RGB Video (Optical Vision) · Health: 96%"
        badge_bg = "#10b981"
        badge_txt = "#ffffff"
        text_accent = "#4ade80"

    return [
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "10px"},
            children=[
                html.Span(
                    status_icon,
                    style={"fontSize": "22px", "transition": "transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)"},
                ),
                html.Div(
                    style={"display": "flex", "flexDirection": "column"},
                    children=[
                        html.Span(
                            status_text,
                            style={
                                "fontSize": "14px",
                                "fontWeight": "800",
                                "color": text_accent,
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                "letterSpacing": "0.5px",
                                "transition": "color 0.4s ease",
                            },
                        ),
                        html.Span(
                            status_sub,
                            style={"fontSize": "12px", "color": "#cbd5e1", "fontWeight": "500"},
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "10px"},
            children=[
                html.Span(
                    "VESSEL: MSC BALLAST TANK B-3",
                    style={
                        "fontSize": "11px",
                        "fontWeight": "800",
                        "color": "#94a3b8",
                        "letterSpacing": "1.2px",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                    },
                ),
                html.Span(
                    sc_info["badge_text"],
                    className="pulse-alert-badge" if sc == "rust" else "",
                    style={
                        "fontSize": "12px",
                        "fontWeight": "800",
                        "backgroundColor": badge_bg,
                        "color": badge_txt,
                        "padding": "4px 12px",
                        "borderRadius": "6px",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                        "letterSpacing": "0.8px",
                        "transition": "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                    },
                ),
            ],
        ),
    ]


def render_provenance_hud(scenario: str = "clean") -> html.Div:
    """
    Render high-contrast, touch-readable sensor detection pipeline:
    Shows the physical vessel change (rust) and exactly how each sensor catches it.
    """
    sc = scenario or "clean"
    is_alert = (sc == "rust")

    accent_color = "#ef4444" if is_alert else "#10b981"
    panel_bg = "#fef2f2" if is_alert else "#f8fafc"

    if is_alert:
        cards_data = [
            {
                "num": "STEP 1 · VESSEL CHANGE",
                "title": "WHERE ON SHIP",
                "tag": "PORT BULKHEAD · FRAME 38",
                "badge_color": "#dc2626",
                "lines": [
                    ("Location", "Ballast Tank B-3, Lower Port Bulkhead, Frame 38 (-4.2m below waterline)"),
                    ("Physical Change", "Severe localized steel oxidation & epoxy coating breakdown"),
                    ("Affected Area", "4.8 m² damaged plate · -1.8mm steel thickness recession"),
                ],
            },
            {
                "num": "STEP 2 · HOW CAUGHT (CHEMICAL)",
                "title": "HYPERSPECTRAL SENSOR",
                "tag": "HS-01 · 780-940nm NIR",
                "badge_color": "#ea580c",
                "lines": [
                    ("Detection Mode", "Near-Infrared chemical reflectance spectroscopy"),
                    ("Chemical Signature", "Fe₂O₃ iron oxide absorption peak caught at 850nm"),
                    ("Early Warning", "Catches subsurface chemical breakdown before visible to eye"),
                ],
            },
            {
                "num": "STEP 3 · HOW CAUGHT (VISUAL)",
                "title": "RGB OPTICAL CAMERA",
                "tag": "CAM-02 · 4K MACHINE VISION",
                "badge_color": "#0284c7",
                "lines": [
                    ("Detection Mode", "High-definition optical chromatic gradient analysis"),
                    ("Visual Appearance", "Caught dark red/brown rust bloom & flaking paint boundary"),
                    ("Cross-Check", "Confirms physical boundary coordinates against CAD baseline"),
                ],
            },
            {
                "num": "STEP 4 · HOW CAUGHT (3D GEOMETRY)",
                "title": "3D LiDAR SCANNER",
                "tag": "LD-01 · 1.2M PTS/SEC",
                "badge_color": "#7c3aed",
                "lines": [
                    ("Detection Mode", "Time-of-flight multi-beam laser point cloud scanning"),
                    ("Geometric Defect", "Measures -1.8mm depth reduction (steel plate thinning)"),
                    ("Twin Sync", "SAC recalculates 4.8 m² mesh -> Twin condition drops 96% -> 68%"),
                ],
            },
        ]
    else:
        cards_data = [
            {
                "num": "STEP 1 · VESSEL BASELINE",
                "title": "WHERE ON SHIP",
                "tag": "PORT BULKHEAD · FRAME 38",
                "badge_color": "#16a34a",
                "lines": [
                    ("Location", "Ballast Tank B-3, Lower Port Bulkhead, Frame 38 (-4.2m depth)"),
                    ("Physical State", "Protective marine epoxy barrier 100% intact, zero corrosion"),
                    ("Hull Integrity", "Pristine steel plating at nominal 18.0mm design thickness"),
                ],
            },
            {
                "num": "STEP 2 · CONTINUOUS MONITOR",
                "title": "HYPERSPECTRAL SENSOR",
                "tag": "HS-01 · 780-940nm NIR",
                "badge_color": "#16a34a",
                "lines": [
                    ("Inspection Target", "Bulkhead chemical surface signature monitoring"),
                    ("Oxidation Reading", "Zero Fe₂O₃ absorption detected (Baseline reflection flat)"),
                    ("Status", "Protective coating fully intact, no oxidation detected"),
                ],
            },
            {
                "num": "STEP 3 · CONTINUOUS MONITOR",
                "title": "RGB OPTICAL CAMERA",
                "tag": "CAM-02 · 4K MACHINE VISION",
                "badge_color": "#16a34a",
                "lines": [
                    ("Inspection Target", "Visual surface color, texture, and paint continuity"),
                    ("Optical Reading", "Uniform surface color gradient, zero blistering or stains"),
                    ("Status", "Visual appearance 100% clear across inspection area"),
                ],
            },
            {
                "num": "STEP 4 · CONTINUOUS MONITOR",
                "title": "3D LiDAR SCANNER",
                "tag": "LD-01 · 1.2M PTS/SEC",
                "badge_color": "#16a34a",
                "lines": [
                    ("Inspection Target", "3D cavity geometry and plate thickness profile"),
                    ("Geometric Reading", "Point cloud matches CAD model within ±0.2mm tolerance"),
                    ("Status", "Digital Twin in full geometric sync · Health: 96% (Nominal)"),
                ],
            },
        ]

    card_elements = []
    for idx, s in enumerate(cards_data):
        card = html.Div(
            className=f"hud-step-card card-animate-{idx + 1}",
            style={
                "backgroundColor": "#ffffff",
                "borderRadius": "10px",
                "border": f"1.5px solid {'#fca5a5' if is_alert else '#cbd5e1'}",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.04)",
                "padding": "12px 14px",
                "display": "flex",
                "flexDirection": "column",
                "gap": "6px",
                "flex": "1",
                "minWidth": "0",
                "transition": "all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)",
            },
            children=[
                # Step badge & title
                html.Div(
                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                    children=[
                        html.Span(
                            s["num"],
                            style={
                                "fontSize": "10px",
                                "fontWeight": "800",
                                "color": s["badge_color"],
                                "letterSpacing": "1px",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                            },
                        ),
                        html.Span(
                            s["tag"],
                            style={
                                "fontSize": "9.5px",
                                "fontWeight": "800",
                                "color": "#475569",
                                "backgroundColor": "#f1f5f9",
                                "padding": "2px 6px",
                                "borderRadius": "4px",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                            },
                        ),
                    ],
                ),
                html.Span(
                    s["title"],
                    style={
                        "fontSize": "14px",
                        "fontWeight": "800",
                        "color": "#0f172a",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                        "letterSpacing": "0.3px",
                    },
                ),
                # Line items
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "4px", "marginTop": "2px"},
                    children=[
                        html.Div(
                            style={"fontSize": "11.5px", "lineHeight": "1.3"},
                            children=[
                                html.Span(f"{k}: ", style={"fontWeight": "700", "color": "#1e293b"}),
                                html.Span(v, style={"color": "#475569"}),
                            ],
                        )
                        for k, v in s["lines"]
                    ],
                ),
            ],
        )
        card_elements.append(card)

    return html.Div(
        className="hud-panel-transition",
        style={
            "backgroundColor": panel_bg,
            "border": f"2px solid {accent_color}",
            "borderRadius": "12px",
            "padding": "14px 18px",
            "display": "flex",
            "flexDirection": "column",
            "gap": "10px",
            "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
            "transition": "all 0.45s cubic-bezier(0.4, 0, 0.2, 1)",
        },
        children=[
            # Header
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "flexWrap": "wrap", "gap": "6px"},
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                        children=[
                            html.Span(
                                "SENSOR DETECTION PIPELINE · HOW THE CHANGE IS CAUGHT",
                                style={
                                    "fontSize": "12px",
                                    "fontWeight": "800",
                                    "letterSpacing": "1.2px",
                                    "color": accent_color,
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "transition": "color 0.4s ease",
                                },
                            ),
                            html.Span(
                                "— Demonstrating how chemical (HS), visual (RGB), and geometric (LiDAR) sensors catch rust and sync to the twin",
                                style={"fontSize": "12px", "color": "#64748b", "fontWeight": "600"},
                            ),
                        ],
                    ),
                    html.Span(
                        "⚠️ ACTIVE SENSOR CATCH · HEALTH: 68%" if is_alert else "🟢 ALL SENSORS CALIBRATED · HEALTH: 96%",
                        style={
                            "fontSize": "11px",
                            "fontWeight": "800",
                            "color": accent_color,
                            "letterSpacing": "1px",
                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                            "transition": "color 0.4s ease",
                        },
                    ),
                ],
            ),
            # 4 Cards Row
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "gap": "10px",
                    "alignItems": "stretch",
                },
                children=card_elements,
            ),
        ],
    )


# =============================================================================
# DASH APPLICATION SETUP
# =============================================================================

app = dash.Dash(
    __name__,
    title="Digital Twin Story Timeline",
    update_title=None,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],

)

server = app.server  # Expose Flask instance for Gunicorn / Render / Railway

@server.route('/api/upload', methods=['POST'])
def api_upload_image():
    """REST API endpoint so dropped images from any device/browser are saved permanently to disk."""
    from flask import request, jsonify
    try:
        data = request.get_json(force=True)
        node_id = data.get("nodeId")
        data_url = data.get("dataUrl")
        if node_id and data_url:
            saved_path = save_uploaded_image_file(node_id, data_url)
            return jsonify({"status": "ok", "nodeId": node_id, "path": saved_path})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify({"status": "invalid"}), 400

@server.route('/api/images', methods=['GET'])
def api_get_images():
    """REST API endpoint to return all currently active image data URIs."""
    from flask import jsonify
    return jsonify(IMAGE_DATA)

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            body {
                background-color: #f8fafc;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: #0f172a;
                -webkit-font-smoothing: antialiased;
                -webkit-tap-highlight-color: transparent;
                user-select: none;
                overflow-x: hidden;
            }
            
            /* Stage & Drafting Sheet Aesthetics */
            .stage {
                position: relative;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                overflow: hidden;
                height: 620px;
                background-image: 
                    radial-gradient(#cbd5e1 1.1px, transparent 1.1px),
                    linear-gradient(to right, rgba(226, 232, 240, 0.6) 1px, transparent 1px),
                    linear-gradient(to bottom, rgba(226, 232, 240, 0.6) 1px, transparent 1px);
                background-size: 25px 25px, 25px 25px, 25px 25px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
            }
            .stage svg {
                width: 100%;
                height: 100%;
                display: block;
                touch-action: manipulation;
            }
            .hint {
                position: absolute;
                left: 14px;
                bottom: 10px;
                font-family: 'Barlow Semi Condensed', sans-serif;
                font-size: 11.5px;
                color: #64748b;
                letter-spacing: .04em;
                background: rgba(255, 255, 255, 0.94);
                padding: 3px 8px;
                border-radius: 6px;
                border: 1px solid #cbd5e1;
                pointer-events: none;
            }

            /* SVG Nodes & Fluid Styling */
            .node {
                cursor: pointer;
            }
            .node .body {
                stroke-width: 2.5px;
                transition: stroke-width .22s cubic-bezier(0.34, 1.56, 0.64, 1),
                            filter .22s ease,
                            stroke .22s ease;
            }
            .node:hover .body {
                stroke-width: 3.5px;
                filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.12));
            }
            .node.selected .body {
                stroke: #d97706 !important;
                stroke-width: 5.5px !important;
                filter: drop-shadow(0 0 12px rgba(245, 158, 11, 0.65));
            }
            .node .glow-ring {
                fill: none;
                stroke: #f59e0b;
                stroke-width: 4px;
                opacity: 0;
                transition: opacity .25s ease;
            }
            .node.selected .glow-ring {
                opacity: 0.55;
                animation: nodePulse 2s infinite ease-in-out;
            }
            @keyframes nodePulse {
                0%, 100% { stroke-width: 4px; opacity: 0.55; }
                50% { stroke-width: 7px; opacity: 0.25; }
            }

            .node .label {
                font-family: 'Barlow Semi Condensed', 'Arial Narrow', sans-serif;
                font-weight: 700;
                font-size: 13.5px;
                fill: #0f172a;
                text-anchor: middle;
                pointer-events: none;
            }
            .node .sub {
                font-family: 'Barlow Semi Condensed', 'Arial Narrow', sans-serif;
                font-weight: 600;
                font-size: 11px;
                fill: #64748b;
                text-anchor: middle;
                pointer-events: none;
            }
            .node.k-samm .label, .node.k-cms .label { fill: #ffffff; }
            .node.k-samm .sub, .node.k-cms .sub { fill: rgba(255, 255, 255, 0.95); }
            .node.k-samm .sub {
                font-size: 7.8px;
                font-weight: 700;
                letter-spacing: -0.2px;
            }
            .node.k-cms .sub {
                font-size: 8.5px;
                font-weight: 700;
                letter-spacing: -0.2px;
            }

            /* Synchronized Rust Defect Alert State for Ballast Tank & Digital Twin */
            .node.defect-alert .body {
                stroke: #ef4444 !important;
                stroke-width: 3.5px !important;
            }
            .node.defect-alert .glow-ring {
                stroke: rgba(239, 68, 68, 0.7) !important;
                stroke-width: 7px !important;
                opacity: 0.85 !important;
            }

            /* Dimmed State */
            .dim {
                opacity: 0.20 !important;
                transition: opacity .3s ease;
            }
            .node, .edge, .group-box {
                transition: opacity .3s ease;
            }

            /* Edges */
    .clickable-pipeline-edge {
        cursor: pointer;
    }
    .clickable-pipeline-edge .elabel-bg {
        transition: all 0.2s ease;
    }
    .clickable-pipeline-edge:hover .edge-path {
        stroke: #0284c7 !important;
        stroke-width: 3.5px !important;
        filter: drop-shadow(0 0 10px rgba(2, 132, 199, 0.75));
    }
    .clickable-pipeline-edge:hover .elabel-bg {
        fill: #0284c7 !important;
        stroke: #38bdf8 !important;
    }
    .clickable-pipeline-edge:hover .elabel {
        fill: #ffffff !important;
        font-weight: 800 !important;
    }
            .edge path {
                stroke: #2563eb;
                stroke-width: 2.5px;
                fill: none;
                transition: stroke 0.25s, stroke-width 0.25s;
            }
            .edge.feedback path {
                stroke: #94a3b8;
                stroke-width: 2px;
                stroke-dasharray: 6 4;
            }
            .edge.hot path {
                stroke: #d97706 !important;
                stroke-width: 4px !important;
            }
            .edge .elabel {
                font-family: 'Barlow Semi Condensed', sans-serif;
                font-size: 10.5px;
                font-weight: 700;
                fill: #1e293b;
                text-anchor: middle;
                pointer-events: none;
            }
            .edge .elabel-bg {
                fill: #ffffff;
                stroke: #cbd5e1;
                stroke-width: 1px;
                rx: 4px;
            }
            .edge.hot .elabel { fill: #b45309; }
            .edge.hot .elabel-bg { stroke: #f59e0b; fill: #fffbeb; }

            /* Group Boxes */
            .group-box { pointer-events: none; }
            .group-box rect.group-bg {
                stroke-dasharray: 6 4;
                stroke-width: 2px;
            }
            .group-box text.group-title {
                font-family: 'Barlow Semi Condensed', sans-serif;
                font-weight: 800;
                font-size: 13px;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                text-anchor: middle;
            }
            
            /* Fluid Spring & Bezier Transitions on All Interactive Controls */
            .phase-tab-btn, .sim-action-btn, .mode-toggle-btn {
                transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1),
                            background-color 0.25s ease,
                            border-color 0.25s ease,
                            box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1),
                            color 0.25s ease !important;
            }
            .phase-tab-btn:hover, .sim-action-btn:hover, .mode-toggle-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
            }
            .phase-tab-btn:active, .sim-action-btn:active, .mode-toggle-btn:active {
                transform: scale(0.97) translateY(0);
            }
            
            /* Smooth View Transitions */
            .view-enter-anim {
                animation: viewFadeSlide 0.38s cubic-bezier(0.16, 1, 0.3, 1) both;
            }
            @keyframes viewFadeSlide {
                0% {
                    opacity: 0;
                    transform: translateY(12px) scale(0.995);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            /* Notes Panel Slide In */
            .panel-slide-anim {
                animation: panelSlideIn 0.32s cubic-bezier(0.16, 1, 0.3, 1) both;
            }
            @keyframes panelSlideIn {
                0% {
                    opacity: 0;
                    transform: translateX(12px);
                }
                100% {
                    opacity: 1;
                    transform: translateX(0);
                }
            }

            /* Provenance HUD Staggered Cards */
            .hud-step-card {
                transition: transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1),
                            box-shadow 0.32s ease,
                            border-color 0.4s ease,
                            background-color 0.4s ease;
            }
            .hud-step-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            }
            .card-animate-1 { animation: cardPopIn 0.36s cubic-bezier(0.16, 1, 0.3, 1) 0.04s both; }
            .card-animate-2 { animation: cardPopIn 0.36s cubic-bezier(0.16, 1, 0.3, 1) 0.10s both; }
            .card-animate-3 { animation: cardPopIn 0.36s cubic-bezier(0.16, 1, 0.3, 1) 0.16s both; }
            .card-animate-4 { animation: cardPopIn 0.36s cubic-bezier(0.16, 1, 0.3, 1) 0.22s both; }

            @keyframes cardPopIn {
                0% {
                    opacity: 0;
                    transform: translateY(10px) scale(0.98);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            /* Laser Scanner Beam Sweep across Tank */
            .scanner-beam {
                position: absolute;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.95), rgba(249, 115, 22, 0.95), transparent);
                box-shadow: 0 0 16px rgba(56, 189, 248, 0.9), 0 0 32px rgba(249, 115, 22, 0.7);
                opacity: 0;
                pointer-events: none;
                z-index: 10;
            }
            .active-sweep {
                animation: sweepAnimation 1.1s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            }
            .dt-active-sweep {
                animation: sweepAnimation 1.1s 0.22s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            }
            @keyframes sweepAnimation {
                0% { top: 12%; opacity: 0; }
                20% { opacity: 0.95; }
                80% { opacity: 0.95; }
                100% { top: 88%; opacity: 0; }
            }

            /* Pulsing Alert Badge */
            @keyframes alertPulseGlow {
                0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); }
                50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
            }
            .pulse-alert-badge {
                animation: alertPulseGlow 2s infinite ease-in-out;
            }

            .custom-scroll::-webkit-scrollbar { width: 6px; }
            .custom-scroll::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 4px; }
            .custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
            .custom-scroll::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

            @media (max-width: 1040px) {
                #main-flex-container { flex-direction: column !important; }
                #left-graph-pane { width: 100% !important; flex: none !important; }
                #right-notes-pane { width: 100% !important; flex: none !important; min-width: 0 !important; }
                #phase-buttons-bar { grid-template-columns: repeat(2, 1fr) !important; }
                #dual-twin-viewport-container { grid-template-columns: 1fr !important; }
            }
            @media (max-width: 600px) {
                #phase-buttons-bar { grid-template-columns: 1fr !important; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // =========================================================================
            // BUTTERY-SMOOTH SVG DIAGRAM ANIMATION ENGINE
            // Ported directly from dt-story.html with 60fps RAF interpolation,
            // cubic ease-in-out curve, dynamic edge clipping, and seamless Dash sync.
            // =========================================================================

            const svgNS = "http://www.w3.org/2000/svg";

            const SVG_NODES = {
                lidar: { group: "sensors", label: "LIDAR", sub: "3D laser scan", shape: "rect", w: 116, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", text: "#0f172a" },
                rgb:   { group: "sensors", label: "RGB/Video", sub: "visual images", shape: "rect", w: 116, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", text: "#0f172a" },
                hyp:   { group: "sensors", label: "Hyper", sub: "surface condition", shape: "rect", w: 116, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", text: "#0f172a" },
                sac:   { group: "computation", label: "SAC", sub: "surface area", shape: "rect", w: 116, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", text: "#0f172a" },
                vtl:   { group: "computation", label: "VTL Prototype", sub: "technical library", shape: "rect", w: 116, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", text: "#0f172a" },
                tank:  { group: "sensors", label: "Ballast Tank", sub: "", shape: "ellipse", rx: 65, ry: 38, fill: "#ffffff", stroke: "#1e293b", text: "#0f172a" },
                twin:  { group: "dtsync", label: "DT", sub: "digital twin", shape: "ellipse", rx: 59, ry: 38, fill: "#ffffff", stroke: "#1e293b", text: "#0f172a" },
                samm:  { group: "decision", label: "LRMS", sub: "Long Range Maintenance Schedule", shape: "rect", w: 126, h: 62, rx: 10, fill: "#0284c7", stroke: "#0369a1", text: "#ffffff" },
                cms:   { group: "decision", label: "HMS", sub: "Hull Maintenance System", shape: "rect", w: 126, h: 62, rx: 10, fill: "#10b981", stroke: "#059669", text: "#ffffff" }
            };

            const SVG_GROUPS = {
                sensors:     { label: "Ballast Tank & Sensors", stroke: "#ef4444", fill: "rgba(254, 242, 242, 0.45)", text: "#b91c1c", badgeAlign: "top-center" },
                computation: { label: "Computation", stroke: "#10b981", fill: "rgba(240, 253, 244, 0.45)", text: "#047857", badgeAlign: "bottom-center" },
                dtsync:      { label: "Digital Twin", stroke: "#3b82f6", fill: "rgba(239, 246, 255, 0.45)", text: "#1d4ed8", badgeAlign: "top-center" },
                decision:    { label: "Beyond the Twin", stroke: "#8b5cf6", fill: "rgba(245, 243, 255, 0.45)", text: "#6d28d9", badgeAlign: "top-center" }
            };

            const SVG_LAYOUT = {
                1: {
                    lidar: [370, 230], rgb: [500, 230], hyp: [630, 230],
                    tank: [500, 385]
                },
                2: {
                    lidar: [400, 130], rgb: [520, 130], hyp: [640, 130],
                    tank: [520, 265],
                    sac: [180, 205], vtl: [220, 410]
                },
                3: {
                    lidar: [400, 130], rgb: [520, 130], hyp: [640, 130],
                    tank: [520, 265],
                    sac: [180, 205], vtl: [220, 410],
                    twin: [520, 475]
                },
                4: {
                    lidar: [400, 130], rgb: [520, 130], hyp: [640, 130],
                    tank: [520, 265],
                    sac: [180, 205], vtl: [220, 410],
                    twin: [520, 475],
                    samm: [820, 335], cms: [820, 475]
                },
                4.5: {}
            };

            const SVG_EDGES = [
                // Phase 2, 3, 4: LiDAR -> SAC -> VTL
                { a: "lidar", b: "sac", label: "point cloud", phases: [2, 3, 4] },
                { a: "sac", b: "vtl", label: "model + area", phases: [2, 3, 4] },

                // Phase 3, 4: Sensors -> Ballast Tank (Bidirectional telemetry & control loop)
                { a: "lidar", b: "tank", label: "", phases: [3, 4], bidirectional: true },
                { a: "rgb", b: "tank", label: "", phases: [3, 4], bidirectional: true },
                { a: "hyp", b: "tank", label: "", phases: [3, 4], bidirectional: true },

                // Phase 3, 4: DT sync & VTL records
                { a: "tank", b: "twin", label: "sync", phases: [3, 4], bidirectional: true },
                { a: "vtl", b: "twin", label: "tank records", phases: [3, 4] },

                // Phase 4: Beyond the Twin layer
                { a: "twin", b: "cms", label: "twin data", phases: [4] },
                { a: "samm", b: "tank", label: "actions", phases: [4] },
                { a: "cms", b: "vtl", label: "", phases: [4], dashed: true, curve: -140 },
                { a: "samm", b: "cms", label: "", phases: [4], bidirectional: true }
            ];

            let currentPhase = 1, selectedNode = null;
            const pos = {};
            const nodeEls = {}, groupEls = {}, edgeEls = [];

            for (const id in SVG_NODES) {
                const start = SVG_LAYOUT[1][id] || SVG_LAYOUT[3][id] || SVG_LAYOUT[4][id] || [500, 300];
                pos[id] = { x: start[0], y: start[1], o: SVG_LAYOUT[1][id] ? 1 : 0 };
            }

            function svgEl(tag, attrs, parent) {
                const el = document.createElementNS(svgNS, tag);
                for (const k in attrs) el.setAttribute(k, attrs[k]);
                if (parent) parent.appendChild(el);
                return el;
            }

            function initDiagram() {
                const mount = document.getElementById("svg-diagram-mount");
                if (!mount) return;
                if (mount._diagramMounted && document.getElementById("svg")) return;
                mount._diagramMounted = true;

                mount.innerHTML = `
                    <svg id="svg" viewBox="0 0 1000 620" preserveAspectRatio="xMidYMid meet">
                        <defs>
                            <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="13" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#2563eb"/></marker>
                            <marker id="arrow-hot" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="13" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#d97706"/></marker>
                            <marker id="arrow-feedback" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker>
                            <marker id="arrow-start" viewBox="0 0 10 10" refX="1" refY="5" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="13" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#2563eb"/></marker>
                            <marker id="arrow-start-hot" viewBox="0 0 10 10" refX="1" refY="5" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="13" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#d97706"/></marker>
                        </defs>
                        <g id="group-boxes"></g>
                        <g id="edges"></g>
                        <g id="nodes"></g>
                        <!-- ======================================================== -->
    <!-- PHASE 4.5: AST SYSTEM MODEL & MBSE ARCHITECTURE BLUEPRINT -->
    <!-- ======================================================== -->
    <!-- ======================================================== -->
    <!-- PHASE 4.5: AST SYSTEM MODEL & MBSE ARCHITECTURE BLUEPRINT -->
    <!-- Styled in the presentation's native design language       -->
    <!-- ======================================================== -->
    <g id="phase45-placeholder" style="display:none;">
        <!-- Top Canvas Title Bar -->
        <g id="p45-header">
            <text x="32" y="38" font-family="'Barlow Semi Condensed', sans-serif" font-size="24" font-weight="800" fill="#0f172a" letter-spacing="0.5">AST System Model</text>
            
            <rect x="745" y="16" width="225" height="26" rx="6" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>
            <text x="857" y="33" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" fill="#2563eb" text-anchor="middle" letter-spacing="0.8">PHASE 4.5 &middot; DIGITAL THREAD</text>
        </g>

        <!-- ========================================================= -->
        <!-- CONTAINER 1 (LEFT): DATA STACK & CYBERNETICS               -->
        <!-- ========================================================= -->
        <g id="group-datastack">
            <!-- Dashed Group Box -->
            <rect x="25" y="58" width="465" height="528" rx="14" fill="rgba(248, 250, 252, 0.75)" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6,6" />
            <!-- Group Header Tag -->
            <rect x="42" y="47" width="210" height="22" rx="5" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1" />
            <text x="147" y="62" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" fill="#334155" text-anchor="middle" letter-spacing="1">1. DATA STACK &amp; CYBERNETICS</text>

            <!-- Persistence Bus (Left, pointing DOWN) -->
            <g id="bus-persistence" style="cursor:help;">
                <title>Persistence Bus: Downward flow into multi-temporal historical survey ledger</title>
                <rect x="36" y="80" width="22" height="450" rx="4" fill="#0f2942" stroke="#1e3a5f" stroke-width="1"/>
                <polygon points="31,525 63,525 47,552" fill="#0f2942" stroke="#1e3a5f" stroke-width="1"/>
                <text x="47" y="115" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">P</text>
                <text x="47" y="152" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">E</text>
                <text x="47" y="189" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">R</text>
                <text x="47" y="226" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">S</text>
                <text x="47" y="263" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">I</text>
                <text x="47" y="300" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">S</text>
                <text x="47" y="337" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">T</text>
                <text x="47" y="374" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">E</text>
                <text x="47" y="411" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">N</text>
                <text x="47" y="448" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">C</text>
                <text x="47" y="485" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">E</text>
                <rect x="30" y="556" width="34" height="15" rx="3" fill="#e2e8f0"/>
                <text x="47" y="567" font-family="'Inter', sans-serif" font-size="8.5" font-weight="700" fill="#475569" text-anchor="middle">&darr; STORE</text>
            </g>

            <!-- Algedonic Feedback Bus (Right, pointing UP) -->
            <g id="bus-algedonic" style="cursor:help;">
                <title>Algedonic Loop: Upward cybernetic alerts when measured states violate safety boundaries</title>
                <polygon points="445,107 477,107 461,80" fill="#0f2942" stroke="#1e3a5f" stroke-width="1"/>
                <rect x="450" y="102" width="22" height="450" rx="4" fill="#0f2942" stroke="#1e3a5f" stroke-width="1"/>
                <text x="461" y="145" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">A</text>
                <text x="461" y="185" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">L</text>
                <text x="461" y="225" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">G</text>
                <text x="461" y="265" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">E</text>
                <text x="461" y="305" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">D</text>
                <text x="461" y="345" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">O</text>
                <text x="461" y="385" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">N</text>
                <text x="461" y="425" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">I</text>
                <text x="461" y="465" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">C</text>
                <rect x="444" y="556" width="34" height="15" rx="3" fill="#e2e8f0"/>
                <text x="461" y="567" font-family="'Inter', sans-serif" font-size="8.5" font-weight="700" fill="#475569" text-anchor="middle">&uarr; ALERT</text>
            </g>

            <!-- Tier 1 Card: Ontology Semantic Representation -->
            <g id="card-tier-1" style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="68" y="78" width="372" height="152" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.03))" />
                <rect x="68" y="78" width="372" height="34" rx="10" fill="#fff7ed" stroke="#fdba74" stroke-width="1" />
                <rect x="68" y="100" width="372" height="12" fill="#fff7ed" />
                <!-- Number Pill -->
                <rect x="78" y="85" width="20" height="20" rx="4" fill="#ea580c" />
                <text x="88" y="99" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">1</text>
                <!-- Title -->
                <text x="106" y="99" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800" fill="#9a3412">ONTOLOGY SEMANTIC REPRESENTATION</text>
                <rect x="352" y="86" width="80" height="18" rx="4" fill="#ffedd5"/>
                <text x="392" y="98" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#c2410c" text-anchor="middle">SEMANTIC GRAPH</text>
                <!-- Body Text -->
                <text x="80" y="130" font-family="'Inter', sans-serif" font-size="10.8" font-weight="600" fill="#1e293b">&bull; Encodes system entities, relationships, &amp; constraints in a formal model.</text>
                <text x="80" y="148" font-family="'Inter', sans-serif" font-size="10.8" font-weight="600" fill="#1e293b">&bull; Answers: What exists in this system and how do dependencies connect?</text>
                <!-- Detail Box -->
                <rect x="80" y="162" width="348" height="56" rx="6" fill="#f8fafc" stroke="#e2e8f0"/>
                <text x="90" y="180" font-family="'Inter', sans-serif" font-size="10" font-weight="700" fill="#ea580c">SYSTEM KNOWLEDGE &amp; AXIOMS:</text>
                <text x="90" y="196" font-family="'Inter', sans-serif" font-size="9.8" fill="#475569">Defines physical ballast compartments, corrosion degradation physics,</text>
                <text x="90" y="210" font-family="'Inter', sans-serif" font-size="9.8" fill="#475569">sensor observation bindings, and classification society safety objectives.</text>
            </g>

            <!-- Tier 2 Card: Taxonomy Hierarchical Classification -->
            <g id="card-tier-2" style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="68" y="240" width="372" height="152" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.03))" />
                <rect x="68" y="240" width="372" height="34" rx="10" fill="#f0f9ff" stroke="#bae6fd" stroke-width="1" />
                <rect x="68" y="262" width="372" height="12" fill="#f0f9ff" />
                <!-- Number Pill -->
                <rect x="78" y="247" width="20" height="20" rx="4" fill="#0284c7" />
                <text x="88" y="261" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">2</text>
                <!-- Title -->
                <text x="106" y="261" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800" fill="#0369a1">TAXONOMY HIERARCHICAL CLASSIFICATION</text>
                <rect x="352" y="248" width="80" height="18" rx="4" fill="#e0f2fe"/>
                <text x="392" y="260" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#0284c7" text-anchor="middle">TYPED CLASSES</text>
                <!-- Body Text -->
                <text x="80" y="292" font-family="'Inter', sans-serif" font-size="10.8" font-weight="600" fill="#1e293b">&bull; Organizes system elements into typed classes with inheritance.</text>
                <text x="80" y="310" font-family="'Inter', sans-serif" font-size="10.8" font-weight="600" fill="#1e293b">&bull; Enables structured reasoning about failure modes &amp; behaviors.</text>
                <!-- Detail Box -->
                <rect x="80" y="324" width="348" height="56" rx="6" fill="#f8fafc" stroke="#e2e8f0"/>
                <text x="90" y="342" font-family="'Inter', sans-serif" font-size="10" font-weight="700" fill="#0284c7">CLASS INHERITANCE HIERARCHY:</text>
                <text x="90" y="358" font-family="'Inter', sans-serif" font-size="9.8" fill="#475569">Classifies structural members (girders, stiffeners, plating), sensor profiles,</text>
                <text x="90" y="372" font-family="'Inter', sans-serif" font-size="9.8" fill="#475569">and defect severities across levels of abstraction from asset to fleet.</text>
            </g>

            <!-- Tier 3 Card: Schema Data Structure & Relational Encoding -->
            <g id="card-tier-3" style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="68" y="402" width="372" height="152" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.03))" />
                <rect x="68" y="402" width="372" height="34" rx="10" fill="#f0fdfa" stroke="#99f6e4" stroke-width="1" />
                <rect x="68" y="424" width="372" height="12" fill="#f0fdfa" />
                <!-- Number Pill -->
                <rect x="78" y="409" width="20" height="20" rx="4" fill="#0d9488" />
                <text x="88" y="423" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">3</text>
                <!-- Title -->
                <text x="106" y="423" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800" fill="#0f766e">SCHEMA DATA STRUCTURE &amp; ENCODING</text>
                <rect x="352" y="410" width="80" height="18" rx="4" fill="#ccfbf1"/>
                <text x="392" y="422" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#0f766e" text-anchor="middle">QUERYABLE DATA</text>
                <!-- Body Text -->
                <text x="80" y="454" font-family="'Inter', sans-serif" font-size="10.8" font-weight="600" fill="#1e293b">&bull; Translates ontology into structured, queryable, &amp; traceable relational data.</text>
                <text x="80" y="472" font-family="'Inter', sans-serif" font-size="10.8" font-weight="600" fill="#1e293b">&bull; Establishes traceability links between system states and requirements.</text>
                <!-- Detail Box -->
                <rect x="80" y="486" width="348" height="56" rx="6" fill="#f8fafc" stroke="#e2e8f0"/>
                <text x="90" y="504" font-family="'Inter', sans-serif" font-size="10" font-weight="700" fill="#0d9488">RELATIONAL ENCODING &amp; TRACEABILITY:</text>
                <text x="90" y="520" font-family="'Inter', sans-serif" font-size="9.8" fill="#475569">Maps 3D point coordinates, orthophoto rust masks, and thickness curves</text>
                <text x="90" y="534" font-family="'Inter', sans-serif" font-size="9.8" fill="#475569">to explicit DNV-GL scantling limits, SQL tables, and survey certificates.</text>
            </g>
        </g>

        <!-- ========================================================= -->
        <!-- CENTER: BIDIRECTIONAL CONNECTOR                            -->
        <!-- ========================================================= -->
        <g id="connector-thread">
            <line x1="490" y1="322" x2="520" y2="322" stroke="#2563eb" stroke-width="2" stroke-dasharray="3,3"/>
            <polygon points="522,322 514,317 514,327" fill="#2563eb"/>
            <polygon points="488,322 496,317 496,327" fill="#2563eb"/>
            <rect x="480" y="306" width="50" height="32" rx="6" fill="#ffffff" stroke="#2563eb" stroke-width="1.5"/>
            <text x="505" y="321" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" fill="#2563eb" text-anchor="middle">&hArr;</text>
            <text x="505" y="332" font-family="'Inter', sans-serif" font-size="7" font-weight="700" fill="#1e40af" text-anchor="middle">MBSE LINK</text>
        </g>

        <!-- ========================================================= -->
        <!-- CONTAINER 2 (RIGHT): SYSML MBSE & RUNTIME TWIN             -->
        <!-- ========================================================= -->
        <g id="group-sysml-runtime">
            <!-- Dashed Group Box -->
            <rect x="520" y="58" width="455" height="528" rx="14" fill="rgba(245, 243, 255, 0.45)" stroke="#8b5cf6" stroke-width="1.5" stroke-dasharray="6,6" />
            <!-- Group Header Tag -->
            <rect x="536" y="47" width="250" height="22" rx="5" fill="#ede9fe" stroke="#ddd6fe" stroke-width="1" />
            <text x="661" y="62" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" fill="#6d28d9" text-anchor="middle" letter-spacing="1">2. SYSML MBSE &amp; RUNTIME DIGITAL TWIN</text>

            <!-- ----------------------------------------------------- -->
            <!-- SUB-BLOCK: RUNTIME SENSORS & TWIN NODES (TOP)         -->
            <!-- Authentic match to user slide (top_right_zoom.png)    -->
            <!-- All 3 sensors connect to Tank; SAC/VTL connect to DT  -->
            <!-- ----------------------------------------------------- -->
            <!-- Vertical drops from each sensor to the horizontal bus -->
            <line x1="584" y1="92" x2="584" y2="103" stroke="#2563eb" stroke-width="1.8"/>
            <line x1="728" y1="92" x2="728" y2="103" stroke="#2563eb" stroke-width="1.8"/>
            <line x1="872" y1="92" x2="872" y2="103" stroke="#2563eb" stroke-width="1.8"/>
            <!-- Horizontal bus spanning across all 3 sensors -->
            <line x1="584" y1="103" x2="872" y2="103" stroke="#2563eb" stroke-width="1.8"/>
            <!-- Single combined drop from bus directly into Tank -->
            <line x1="728" y1="103" x2="728" y2="111" stroke="#2563eb" stroke-width="1.8"/>
            <polygon points="724,106 728,112 732,106" fill="#2563eb"/>

            <!-- LIDAR -> SAC -->
            <path d="M 540 75 L 518 75 L 518 129 L 538 129" fill="none" stroke="#2563eb" stroke-width="1.6"/>
            <polygon points="534,125 540,129 534,133" fill="#2563eb"/>

            <!-- SAC -> DT & VTL -> DT (Direct connections to DT, NO link between SAC and VTL) -->
            <path d="M 628 129 C 656 129, 656 183, 682 183" fill="none" stroke="#2563eb" stroke-width="1.6"/>
            <polygon points="678,179 684,183 678,187" fill="#2563eb"/>

            <line x1="628" y1="183" x2="682" y2="183" stroke="#2563eb" stroke-width="1.6"/>
            <polygon points="678,179 684,183 678,187" fill="#2563eb"/>

            <!-- Tank <==> DT Bidirectional Real-Time Sync -->
            <line x1="728" y1="147" x2="728" y2="165" stroke="#0284c7" stroke-width="2"/>
            <polygon points="724,151 728,145 732,151" fill="#0284c7"/>
            <polygon points="724,161 728,167 732,161" fill="#0284c7"/>

            <!-- SAMM -> Tank & DT -> CMS -->
            <line x1="828" y1="129" x2="774" y2="129" stroke="#2563eb" stroke-width="1.6"/>
            <polygon points="778,125 772,129 778,133" fill="#2563eb"/>

            <line x1="772" y1="183" x2="826" y2="183" stroke="#16a34a" stroke-width="1.6"/>
            <polygon points="822,179 828,183 822,187" fill="#16a34a"/>

            <!-- Sensor Nodes -->
            <!-- LIDAR -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('lidar');">
                <rect x="540" y="58" width="88" height="34" rx="6" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
                <text x="584" y="79" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">LIDAR</text>
            </g>

            <!-- Hyper -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('hyp');">
                <rect x="684" y="58" width="88" height="34" rx="6" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
                <text x="728" y="79" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">Hyper</text>
            </g>

            <!-- RGB/Video -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('rgb');">
                <rect x="828" y="58" width="88" height="34" rx="6" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
                <text x="872" y="79" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">RGB/Video</text>
            </g>

            <!-- SAC -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('sac');">
                <rect x="540" y="112" width="88" height="34" rx="6" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
                <text x="584" y="133" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">SAC</text>
            </g>

            <!-- Tank (Physical Tank Oval) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('tank');">
                <ellipse cx="728" cy="129" rx="44" ry="17" fill="#ffffff" stroke="#1e293b" stroke-width="1.8" />
                <text x="728" y="133" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">Tank</text>
            </g>

            <!-- SAMM (Solid Blue Box) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('lrms');">
                <rect x="828" y="112" width="88" height="34" rx="6" fill="#2563eb" stroke="#1d4ed8" stroke-width="1.5" />
                <text x="872" y="133" font-family="'Barlow Semi Condensed', sans-serif" font-size="11.5" font-weight="800" fill="#ffffff" text-anchor="middle">SAMM</text>
            </g>

            <!-- VTL -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('vtl');">
                <rect x="540" y="166" width="88" height="34" rx="6" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
                <text x="584" y="187" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">VTL</text>
            </g>

            <!-- DT (Virtual Twin Oval) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('twin');">
                <ellipse cx="728" cy="183" rx="44" ry="17" fill="#eff6ff" stroke="#2563eb" stroke-width="2" />
                <text x="728" y="187" font-family="'Barlow Semi Condensed', sans-serif" font-size="12.5" font-weight="800" fill="#1d4ed8" text-anchor="middle">DT</text>
            </g>

            <!-- CMS (Solid Green Box) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('hms');">
                <rect x="828" y="166" width="88" height="34" rx="6" fill="#16a34a" stroke="#15803d" stroke-width="1.5" />
                <text x="872" y="187" font-family="'Barlow Semi Condensed', sans-serif" font-size="11.5" font-weight="800" fill="#ffffff" text-anchor="middle">CMS</text>
            </g>
            <!-- ----------------------------------------------------- -->
            <!-- SUB-BLOCK: SYSML 2.0 HIERARCHY TREE METAMODEL         -->
            <!-- Authentic match to user slide (uploaded_media_1794606972675.png) -->
            <!-- ----------------------------------------------------- -->
            <!-- Connecting Tree Lines & Generalization Triangles -->
            <!-- ----------------------------------------------------- -->
            <!-- CONNECTING TREE LINES & GENERALIZATION TRIANGLES      -->
            <!-- ----------------------------------------------------- -->
            <!-- Root to Level 1 spine -->
            <path d="M 626 350 L 642 350 L 642 260 L 655 260" fill="none" stroke="#334155" stroke-width="1.2"/>
            <path d="M 626 365 L 655 365" fill="none" stroke="#334155" stroke-width="1.2"/>
            <path d="M 626 380 L 642 380 L 642 453 L 655 453" fill="none" stroke="#334155" stroke-width="1.2"/>

            <!-- Generalization Triangles pointing into Root (SysML Diagram) -->
            <polygon points="626,350 634,346 634,354" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>
            <polygon points="626,365 634,361 634,369" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>
            <polygon points="626,380 634,376 634,384" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>

            <!-- Behavior Diagram to 4 children spine (Continuous, original structure) -->
            <path d="M 753 248 L 766 248 L 766 217 L 778 217" fill="none" stroke="#334155" stroke-width="1.2"/>
            <path d="M 753 256 L 766 256 L 766 244 L 778 244" fill="none" stroke="#334155" stroke-width="1.2"/>
            <path d="M 753 264 L 766 264 L 766 271 L 778 271" fill="none" stroke="#334155" stroke-width="1.2"/>
            <path d="M 753 272 L 766 272 L 766 298 L 778 298" fill="none" stroke="#334155" stroke-width="1.2"/>

            <!-- Generalization Triangles pointing into Behavior Diagram -->
            <polygon points="753,248 760,245 760,251" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>
            <polygon points="753,256 760,253 760,259" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>
            <polygon points="753,264 760,261 760,267" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>
            <polygon points="753,272 760,269 760,275" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>

            <!-- Structure Diagram to 3 children spine (Continuous, original structure) -->
            <path d="M 753 444 L 766 444 L 766 405 L 778 405" fill="none" stroke="#334155" stroke-width="1.2"/>
            <path d="M 753 453 L 766 453 L 766 432 L 778 432" fill="none" stroke="#334155" stroke-width="1.2"/>
            <path d="M 753 462 L 766 462 L 766 459 L 778 459" fill="none" stroke="#334155" stroke-width="1.2"/>

            <!-- Generalization Triangles pointing into Structure Diagram -->
            <polygon points="753,444 760,441 760,447" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>
            <polygon points="753,453 760,450 760,456" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>
            <polygon points="753,462 760,459 760,465" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>

            <!-- Internal Block Diagram to Parametric Diagram (Vertical drop) -->
            <line x1="845" y1="470" x2="845" y2="483" stroke="#334155" stroke-width="1.2"/>
            <polygon points="845,470 841,476 849,476" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>

            <!-- ----------------------------------------------------- -->
            <!-- NODES: LEVEL 0 (ROOT)                                 -->
            <!-- ----------------------------------------------------- -->
            <!-- SysML Diagram -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="530" y="343" width="96" height="44" rx="4" fill="#ffffff" stroke="#1e293b" stroke-width="1.5" />
                <text x="578" y="369" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">SysML Diagram</text>
            </g>

            <!-- ----------------------------------------------------- -->
            <!-- NODES: LEVEL 1 (PRIMARY BRANCHES - UNIFORM 98px WIDTH)-->
            <!-- ----------------------------------------------------- -->
            <!-- Behavior Diagram -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="655" y="240" width="98" height="40" rx="4" fill="#ffffff" stroke="#1e293b" stroke-width="1.4" />
                <text x="704" y="264" font-family="'Barlow Semi Condensed', sans-serif" font-size="11.5" font-weight="800" fill="#0f172a" text-anchor="middle">Behavior Diagram</text>
            </g>

            <!-- Requirement Diagram (Preserved 98px width, perfectly centered) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="655" y="347" width="98" height="40" rx="4" fill="#fff1f2" stroke="#fda4af" stroke-width="1.5" />
                <text x="704" y="371" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="800" fill="#be123c" text-anchor="middle">Requirement Diagram</text>
            </g>

            <!-- Structure Diagram -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="655" y="433" width="98" height="40" rx="4" fill="#ffffff" stroke="#1e293b" stroke-width="1.4" />
                <text x="704" y="457" font-family="'Barlow Semi Condensed', sans-serif" font-size="11.5" font-weight="800" fill="#0f172a" text-anchor="middle">Structure Diagram</text>
            </g>

            <!-- ----------------------------------------------------- -->
            <!-- NODES: LEVEL 2 (BEHAVIOR LEAVES)                      -->
            <!-- ----------------------------------------------------- -->
            <!-- 1. Use Case Diagram (Same as UML 2.0 / Purple) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="778" y="206" width="136" height="22" rx="3" fill="#faf5ff" stroke="#c084fc" stroke-width="1.2" />
                <text x="846" y="221" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">Use Case Diagram</text>
            </g>

            <!-- 2. State Machine Diagram (Same as UML 2.0 / Purple) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="778" y="233" width="136" height="22" rx="3" fill="#faf5ff" stroke="#c084fc" stroke-width="1.2" />
                <text x="846" y="248" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">State Machine Diagram</text>
            </g>

            <!-- 3. Sequence Diagram (Same as UML 2.0 / Purple) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="778" y="260" width="136" height="22" rx="3" fill="#faf5ff" stroke="#c084fc" stroke-width="1.2" />
                <text x="846" y="275" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">Sequence Diagram</text>
            </g>

            <!-- 4. Activity Diagram (Modified from UML 2.0 / Green) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="778" y="287" width="136" height="22" rx="3" fill="#f0fdf4" stroke="#86efac" stroke-width="1.2" />
                <text x="846" y="302" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#15803d" text-anchor="middle">Activity Diagram</text>
            </g>

            <!-- ----------------------------------------------------- -->
            <!-- NODES: LEVEL 2 (STRUCTURE LEAVES)                     -->
            <!-- ----------------------------------------------------- -->
            <!-- 5. Package Diagram (Same as UML 2.0 / Purple) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="778" y="394" width="136" height="22" rx="3" fill="#faf5ff" stroke="#c084fc" stroke-width="1.2" />
                <text x="846" y="409" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">Package Diagram</text>
            </g>

            <!-- 6. Block Definition Diagram (Modified from UML 2.0 / Green) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="778" y="421" width="136" height="22" rx="3" fill="#f0fdf4" stroke="#86efac" stroke-width="1.2" />
                <text x="846" y="436" font-family="'Inter', sans-serif" font-size="8.8" font-weight="700" fill="#15803d" text-anchor="middle">Block Definition Diagram</text>
            </g>

            <!-- 7. Internal Block Diagram (Modified from UML 2.0 / Green) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="778" y="448" width="136" height="22" rx="3" fill="#f0fdf4" stroke="#86efac" stroke-width="1.2" />
                <text x="846" y="463" font-family="'Inter', sans-serif" font-size="8.8" font-weight="700" fill="#15803d" text-anchor="middle">Internal Block Diagram</text>
            </g>

            <!-- 8. Parametric Diagram (New Diagram Type / Pink) -->
            <!-- Child of Internal Block Diagram -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
                <rect x="778" y="484" width="136" height="22" rx="3" fill="#fff1f2" stroke="#fda4af" stroke-width="1.2" />
                <text x="846" y="499" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#be123c" text-anchor="middle">Parametric Diagram</text>
            </g>
        </g>

        <!-- ========================================================= -->
        <!-- SYSML 2.0 DIGITAL THREAD BENT ARROW (Exact match Image 4) -->
        <!-- Authentic PowerPoint Bent Arrow on right of SysML diagram -->
        <!-- Frames entire SysML architecture; zero line collision     -->
        <!-- ========================================================= -->
        <g id="p45-digital-thread-arrow" style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
            <!-- Background Knockout Halo -->
            <path d="M 770 346 L 920 346 L 920 216 L 910 216 L 929 193 L 948 216 L 938 216 L 938 364 L 770 364 Z" 
                  fill="#ffffff" stroke="#ffffff" stroke-width="4" stroke-linejoin="round"/>
            
            <!-- Authentic Green Bent Arrow (Frames entire SysML model, points UP to DT) -->
            <path d="M 770 346 L 920 346 L 920 216 L 910 216 L 929 193 L 948 216 L 938 216 L 938 364 L 770 364 Z" 
                  fill="#86efac" stroke="#15803d" stroke-width="1.5" stroke-linejoin="round"/>
            
            <!-- Digital Thread text inside shaft -->
            <text x="929" y="290" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="800" fill="#14532d" text-anchor="middle" transform="rotate(-90 929 290)" letter-spacing="1.5">DIGITAL THREAD</text>
            
            <!-- Connection from arrow tip to DT bottom-right -->
            <path d="M 929 193 C 929 184, 780 184, 748 197" fill="none" stroke="#16a34a" stroke-width="2" stroke-dasharray="3 3"/>
            <polygon points="744,202 748,197 753,202" fill="#16a34a"/>
        </g>

            <!-- Legend -->
            <g id="p45-legend" transform="translate(535, 528)">
                <rect x="0" y="0" width="124" height="24" rx="5" fill="#fff1f2" stroke="#fda4af" stroke-width="1"/>
                <circle cx="12" cy="12" r="4.5" fill="#f43f5e"/>
                <text x="24" y="16" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#be123c">New Diagram Type</text>

                <rect x="134" y="0" width="124" height="24" rx="5" fill="#faf5ff" stroke="#c084fc" stroke-width="1"/>
                <circle cx="146" cy="12" r="4.5" fill="#a855f7"/>
                <text x="158" y="16" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#6b21a8">Same as UML 2.0</text>

                <rect x="268" y="0" width="138" height="24" rx="5" fill="#f0fdf4" stroke="#86efac" stroke-width="1"/>
                <circle cx="280" cy="12" r="4.5" fill="#22c55e"/>
                <text x="292" y="16" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#15803d">Modified from UML 2.0</text>
            </g>
    </g>
</svg>
                `;

                const svg = mount.querySelector("svg");
                const gGroups = document.getElementById("group-boxes");
                const gEdges = document.getElementById("edges");
                const gNodes = document.getElementById("nodes");

                for (const k in nodeEls) delete nodeEls[k];
                for (const k in groupEls) delete groupEls[k];
                edgeEls.length = 0;

                // 1. Build Group Boxes
                for (const gid in SVG_GROUPS) {
                    const grp = SVG_GROUPS[gid];
                    const g = svgEl("g", { class: "group-box group-" + gid }, gGroups);
                    const rect = svgEl("rect", {
                        class: "group-bg",
                        rx: 14,
                        fill: grp.fill,
                        stroke: grp.stroke
                    }, g);
                    const text = svgEl("text", {
                        class: "group-title",
                        fill: grp.text
                    }, g);
                    text.textContent = grp.label;
                    groupEls[gid] = { g, rect, text };
                }

                // 2. Build Edges
                SVG_EDGES.forEach(e => {
                    const eg = svgEl("g", { class: "edge" + (e.dashed ? " feedback" : "") }, gEdges);
                    const path = svgEl("path", { class: "edge-path" }, eg);
                    let bg = null, tx = null;
                    if (e.label) {
                        bg = svgEl("rect", { class: "elabel-bg", height: 18 }, eg);
                        tx = svgEl("text", { class: "elabel" }, eg);
                        tx.textContent = e.label;
                    }
                    if (e.label === "point cloud" || (e.a === "lidar" && e.b === "sac")) {
                        eg.style.cursor = "pointer";
                        eg.classList.add("clickable-pipeline-edge");
                        eg.setAttribute("role", "button");
                        eg.setAttribute("tabindex", "0");
                        eg.setAttribute("title", "Click to inspect LiDAR ➔ SAC Point Cloud Surface Area Pipeline");
                        eg.addEventListener("click", function(evt) {
                            evt.stopPropagation();
                            window.selectNode("point_cloud");
                        });
                        if (bg) { bg.style.cursor = "pointer"; }
                        if (tx) { tx.style.cursor = "pointer"; }
                    }
                    edgeEls.push({ a: e.a, b: e.b, label: e.label, phases: e.phases, curve: e.curve || 0, dashed: e.dashed, bidirectional: e.bidirectional, g: eg, path, bg, tx });
                });

                // 3. Build Nodes
                for (const id in SVG_NODES) {
                    const n = SVG_NODES[id];
                    const ng = svgEl("g", {
                        class: "node k-" + id + " k-" + n.shape,
                        tabindex: "0",
                        role: "button",
                        "aria-label": n.label
                    }, gNodes);

                    let glow = null, body = null;
                    if (n.shape === "ellipse") {
                        glow = svgEl("ellipse", { class: "glow-ring", rx: n.rx + 6, ry: n.ry + 6 }, ng);
                        body = svgEl("ellipse", { class: "body", rx: n.rx, ry: n.ry, fill: n.fill, stroke: n.stroke }, ng);
                    } else {
                        glow = svgEl("rect", { class: "glow-ring", x: -n.w / 2 - 5, y: -n.h / 2 - 5, width: n.w + 10, height: n.h + 10, rx: n.rx + 4, ry: n.rx + 4 }, ng);
                        body = svgEl("rect", { class: "body", x: -n.w / 2, y: -n.h / 2, width: n.w, height: n.h, rx: n.rx, ry: n.rx, fill: n.fill, stroke: n.stroke }, ng);
                        if (n.dashed) body.setAttribute("stroke-dasharray", "6 4");
                    }

                    const t = svgEl("text", { class: "label", y: n.sub ? -4 : 4 }, ng);
                    t.textContent = n.label;
                    if (n.sub) {
                        const s = svgEl("text", { class: "sub", y: 16 }, ng);
                        s.textContent = n.sub;
                    }

                    ng.addEventListener("click", function(evt) {
                        evt.stopPropagation();
                        window.selectNode(id);
                    });
                    ng.addEventListener("keydown", function(evt) {
                        if (evt.key === "Enter" || evt.key === " ") {
                            evt.preventDefault();
                            window.selectNode(id);
                        }
                    });

                    nodeEls[id] = ng;
                }

                // Background click clears selection
                svg.addEventListener("click", function(e) {
                    if (e.target.closest && e.target.closest(".node")) return;
                    if (selectedNode) window.selectNode(null);
                });

                draw();
                highlight();
                if (window.setScenario) window.setScenario(window.currentScenario || "clean");
            }

            function clipBoundary(xA, yA, xB, yB, node) {
                const dx = xB - xA, dy = yB - yA, d = Math.hypot(dx, dy) || 1;
                const ux = dx / d, uy = dy / d;
                if (node.shape === "ellipse") {
                    const scale = 1.0 / Math.sqrt(Math.pow(ux / node.rx, 2) + Math.pow(uy / node.ry, 2));
                    return { x: xA + ux * scale, y: yA + uy * scale };
                } else {
                    const hw = node.w / 2, hh = node.h / 2;
                    const tx = ux !== 0 ? Math.abs(hw / ux) : 1e9;
                    const ty = uy !== 0 ? Math.abs(hh / uy) : 1e9;
                    const t = Math.min(tx, ty);
                    return { x: xA + ux * (t + 1), y: yA + uy * (t + 1) };
                }
            }

            function isConnected(a, b) {
                return edgeEls.some(e => e.phases.includes(currentPhase) && ((e.a === a && e.b === b) || (e.a === b && e.b === a)));
            }

            function draw() {
                const p45El = document.getElementById("phase45-placeholder");
                if (p45El) {
                    p45El.style.display = (currentPhase === 4.5) ? "" : "none";
                }

                // 1. Draw Nodes
                for (const id in SVG_NODES) {
                    const p = pos[id], el = nodeEls[id];
                    if (!el) continue;
                    el.setAttribute("transform", "translate(" + p.x + "," + p.y + ")");
                    el.setAttribute("opacity", p.o.toFixed(3));
                    el.style.display = p.o < 0.02 ? "none" : "";
                }

                // 2. Draw Group Boxes (Smoothly bounds visible child nodes)
                for (const gid in SVG_GROUPS) {
                    const grp = SVG_GROUPS[gid];
                    const grpEl = groupEls[gid];
                    if (!grpEl) continue;

                    const childIds = Object.keys(SVG_NODES).filter(nid => SVG_NODES[nid].group === gid);
                    const visChildren = childIds.filter(nid => pos[nid] && pos[nid].o > 0.02);

                    if (visChildren.length === 0) {
                        grpEl.g.style.display = "none";
                        continue;
                    }
                    grpEl.g.style.display = "";

                    let minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9, maxO = 0;
                    visChildren.forEach(nid => {
                        const p = pos[nid], n = SVG_NODES[nid];
                        const hw = (n.shape === "ellipse" ? n.rx : n.w / 2);
                        const hh = (n.shape === "ellipse" ? n.ry : n.h / 2);
                        minX = Math.min(minX, p.x - hw);
                        maxX = Math.max(maxX, p.x + hw);
                        minY = Math.min(minY, p.y - hh);
                        maxY = Math.max(maxY, p.y + hh);
                        maxO = Math.max(maxO, p.o);
                    });

                    const padX = 20;
                    const padYTop = (grp.badgeAlign === "top-center" ? 26 : 20);
                    const padYBottom = (grp.badgeAlign === "bottom-center" ? 32 : 20);
                    minX -= padX; maxX += padX;
                    minY -= padYTop; maxY += padYBottom;
                    const w = maxX - minX, h = maxY - minY;

                    grpEl.rect.setAttribute("x", minX);
                    grpEl.rect.setAttribute("y", minY);
                    grpEl.rect.setAttribute("width", w);
                    grpEl.rect.setAttribute("height", h);
                    grpEl.g.setAttribute("opacity", maxO.toFixed(3));

                    if (grp.badgeAlign === "bottom-center") {
                        grpEl.text.setAttribute("x", (minX + maxX) / 2);
                        grpEl.text.setAttribute("y", maxY - 10);
                    } else {
                        grpEl.text.setAttribute("x", (minX + maxX) / 2);
                        grpEl.text.setAttribute("y", minY + 15);
                    }
                }

                // 3. Draw Edges with exact perimeter intersection & Bezier curves
                edgeEls.forEach(e => {
                    const on = e.phases.includes(currentPhase);
                    const A = pos[e.a], B = pos[e.b];
                    const vis = on ? Math.min(A.o, B.o) : 0;

                    e.g.style.display = vis < 0.02 ? "none" : "";
                    e.g.setAttribute("opacity", vis.toFixed(3));
                    if (vis < 0.02) return;

                    const p1 = clipBoundary(A.x, A.y, B.x, B.y, SVG_NODES[e.a]);
                    const p2 = clipBoundary(B.x, B.y, A.x, A.y, SVG_NODES[e.b]);

                    const x1 = p1.x, y1 = p1.y, x2 = p2.x, y2 = p2.y;
                    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;

                    if (e.a === "cms" && e.b === "vtl") {
                        // Clear, elegant arc below Digital Twin with 40px+ clearance so it touches nothing else
                        const sx = A.x - 30, sy = A.y + 31;
                        const ex = B.x, ey = B.y + 31;
                        const cx = (sx + ex) / 2, cy = 630;
                        e.path.setAttribute("d", "M " + sx + " " + sy + " Q " + cx + " " + cy + " " + ex + " " + ey);
                    } else if (e.curve) {
                        const dx = x2 - x1, dy = y2 - y1, d = Math.hypot(dx, dy) || 1;
                        const nx = -dy / d, ny = dx / d;
                        const cx = mx + nx * e.curve, cy = my + ny * e.curve;
                        e.path.setAttribute("d", "M " + x1 + " " + y1 + " Q " + cx + " " + cy + " " + x2 + " " + y2);
                        if (e.tx) {
                            e.tx.setAttribute("x", cx);
                            e.tx.setAttribute("y", cy + 4);
                            const tw = e.label.length * 6.5 + 10;
                            e.bg.setAttribute("x", cx - tw / 2);
                            e.bg.setAttribute("y", cy - 8);
                            e.bg.setAttribute("width", tw);
                        }
                    } else {
                        e.path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);
                        if (e.tx) {
                            e.tx.setAttribute("x", mx);
                            e.tx.setAttribute("y", my + 3.5);
                            const tw = e.label.length * 6.5 + 10;
                            e.bg.setAttribute("x", mx - tw / 2);
                            e.bg.setAttribute("y", my - 8);
                            e.bg.setAttribute("width", tw);
                        }
                    }
                });
            }

            function highlight() {
                for (const id in SVG_NODES) {
                    const el = nodeEls[id];
                    if (!el) continue;
                    const isSel = (id === selectedNode);
                    el.classList.toggle("selected", isSel);

                    const isRelated = !selectedNode || isSel || isConnected(selectedNode, id);
                    el.classList.toggle("dim", !isRelated);
                }

                edgeEls.forEach(e => {
                    const isHot = selectedNode && (e.a === selectedNode || e.b === selectedNode);
                    e.g.classList.toggle("hot", !!isHot);
                    e.g.classList.toggle("dim", !!selectedNode && !isHot);

                    if (e.bidirectional) {
                        e.path.setAttribute("marker-start", isHot ? "url(#arrow-start-hot)" : "url(#arrow-start)");
                        e.path.setAttribute("marker-end", isHot ? "url(#arrow-hot)" : "url(#arrow)");
                    } else if (e.dashed) {
                        e.path.setAttribute("marker-end", "url(#arrow-feedback)");
                    } else {
                        e.path.setAttribute("marker-end", isHot ? "url(#arrow-hot)" : "url(#arrow)");
                    }
                });

                for (const gid in SVG_GROUPS) {
                    const grpEl = groupEls[gid];
                    if (!grpEl) continue;
                    const hasSelected = selectedNode && SVG_NODES[selectedNode] && SVG_NODES[selectedNode].group === gid;
                    grpEl.g.classList.toggle("dim", !!selectedNode && !hasSelected);
                }
            }

            let anim = null;
            window.goToPhase = function(targetPhase) {
                const target = parseFloat(targetPhase);
                const p = isNaN(target) ? 1 : target;
                currentPhase = p;
                if (!document.getElementById("svg")) {
                    initDiagram();
                }
                if (selectedNode && (!SVG_LAYOUT[p] || !SVG_LAYOUT[p][selectedNode])) {
                    window.selectNodeInternal(null);
                }

                const from = {};
                for (const id in pos) from[id] = { ...pos[id] };
                const to = {};
                for (const id in pos) {
                    const t = SVG_LAYOUT[p] ? SVG_LAYOUT[p][id] : null;
                    to[id] = t ? { x: t[0], y: t[1], o: 1 } : { x: from[id].x, y: from[id].y, o: 0 };
                    if (t && from[id].o < 0.02) {
                        from[id].x = t[0];
                        from[id].y = t[1];
                    }
                }

                if (anim) cancelAnimationFrame(anim);
                const dur = 650;
                const t0 = performance.now();
                // Exact cubic ease-in-out from dt-story.html
                const ease = t => t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2;

                const step = function(now) {
                    const k = Math.min(1, (now - t0) / dur);
                    const e = ease(k);
                    for (const id in pos) {
                        pos[id].x = from[id].x + (to[id].x - from[id].x) * e;
                        pos[id].y = from[id].y + (to[id].y - from[id].y) * e;
                        pos[id].o = from[id].o + (to[id].o - from[id].o) * e;
                    }
                    draw();
                    if (k < 1) {
                        anim = requestAnimationFrame(step);
                    }
                };
                anim = requestAnimationFrame(step);
                highlight();
            };

            window.selectNodeInternal = function(id) {
                selectedNode = (id && id === selectedNode) ? null : id;
                highlight();
            };

            window.selectNode = function(id) {
                window.selectNodeInternal(id);
                // Dispatch event to Dash through hidden input
                const inp = document.getElementById("svg-selected-sync-input");
                if (inp) {
                    inp.value = selectedNode || "";
                    inp.dispatchEvent(new Event("change", { bubbles: true }));
                    inp.dispatchEvent(new Event("input", { bubbles: true }));
                }
                if (window.dash_clientside && window.dash_clientside.set_props) {
                    try {
                        window.dash_clientside.set_props('selected-node', { data: selectedNode });
                    } catch (_) {}
                }
            };

            window.currentScenario = "clean";
            window.setScenario = function(sc) {
                window.currentScenario = sc || "clean";
                const isRust = (window.currentScenario === "rust");
                const tankEl = nodeEls["tank"];
                const twinEl = nodeEls["twin"];
                if (tankEl) tankEl.classList.toggle("defect-alert", isRust);
                if (twinEl) twinEl.classList.toggle("defect-alert", isRust);
            };

            // Keyboard Navigation (Left/Right arrows change phase, Escape clears selection and closes modal)
            window.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    const modal = document.getElementById("tank-twin-modal");
                    if (modal && modal.style.display !== "none") {
                        const btnClose = document.getElementById("btn-close-modal");
                        if (btnClose) btnClose.click();
                    }
                    window.selectNode(null);
                    return;
                }
                if (e.target.closest && e.target.closest("button, [role=button], input")) return;
                if (e.key === 'ArrowLeft') {
                    const btn = document.getElementById('btn-prev-phase');
                    if (btn && !btn.disabled) { e.preventDefault(); btn.click(); }
                } else if (e.key === 'ArrowRight') {
                    const btn = document.getElementById('btn-next-phase');
                    if (btn && !btn.disabled) { e.preventDefault(); btn.click(); }
                }
            });

            // Backdrop click closes full-screen modal
            document.addEventListener('click', function(e) {
                const modal = document.getElementById("tank-twin-modal");
                if (modal && modal.style.display !== "none" && e.target === modal) {
                    const btnClose = document.getElementById("btn-close-modal");
                    if (btnClose) btnClose.click();
                }
            });

            // Zero-Latency Click Binding on Phase Buttons & Navigation
            document.addEventListener('click', function(e) {
                const target = e.target.closest('button, .phase-tab-btn');
                if (!target) return;
                const PHASE_KEYS = [1, 2, 3, 4, 4.5];
                const curIdx = PHASE_KEYS.indexOf(currentPhase);
                if (target.id === 'btn-prev-phase') {
                    if (window.goToPhase && curIdx > 0) window.goToPhase(PHASE_KEYS[curIdx - 1]);
                } else if (target.id === 'btn-next-phase') {
                    if (window.goToPhase && curIdx < PHASE_KEYS.length - 1) window.goToPhase(PHASE_KEYS[curIdx + 1]);
                } else {
                    const match = (target.id || '').match(/btn-phase-([0-9_]+)/);
                    if (match) {
                        const p = parseFloat(match[1].replace('_', '.'));
                        if (window.goToPhase) window.goToPhase(p);
                    }
                }
            });

            // Instant mount using MutationObserver
            const mountObserver = new MutationObserver(function() {
                const mount = document.getElementById("svg-diagram-mount");
                if (mount && (!mount._diagramMounted || !document.getElementById("svg"))) {
                    initDiagram();
                }
            });
            mountObserver.observe(document.documentElement, { childList: true, subtree: true });

            document.addEventListener('DOMContentLoaded', initDiagram);
            setInterval(function() {
                const mount = document.getElementById("svg-diagram-mount");
                if (mount && (!mount._diagramMounted || !document.getElementById("svg"))) {
                    initDiagram();
                }
            }, 200);
        </script>
    </body>
</html>
"""


# =============================================================================
# APPLICATION LAYOUT
# =============================================================================

def create_layout() -> html.Div:
    """Build the root Dash application layout."""
    return html.Div(
        style={
            "maxWidth": "1640px",
            "margin": "0 auto",
            "padding": "24px 32px 36px 32px",
            "display": "flex",
            "flexDirection": "column",
            "gap": "18px",
            "minHeight": "100vh",
        },
        children=[
            # State Stores
            dcc.Store(id="current-phase", data=1),
            dcc.Store(id="selected-node", data=None),
            dcc.Store(id="phase3-view-mode", data="graph"),  # "graph" or "ship"
            dcc.Store(id="ship-scenario", data="clean"),     # "clean", "rust", "repaired"
            dcc.Store(id="user-dropped-images", storage_type="local", data={}),

            # Full-Screen Pop-up Modal covering the screen (Synchronized Real Ballast Tank & Digital Twin CAD Mesh)
            html.Div(
                id="tank-twin-modal",
                style={
                    "position": "fixed",
                    "inset": "0",
                    "width": "100vw",
                    "height": "100vh",
                    "backgroundColor": "rgba(2, 6, 23, 0.88)",
                    "backdropFilter": "blur(10px)",
                    "WebkitBackdropFilter": "blur(10px)",
                    "zIndex": 99999,
                    "display": "none",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "padding": "24px",
                    "boxSizing": "border-box",
                },
                children=[
                    html.Div(
                        id="modal-card",
                        style={
                            "width": "100%",
                            "maxWidth": "1340px",
                            "backgroundColor": "#0b1329",
                            "borderRadius": "20px",
                            "border": "1.5px solid #334155",
                            "boxShadow": "0 25px 65px -12px rgba(0, 0, 0, 0.85), 0 0 50px rgba(56, 189, 248, 0.15)",
                            "overflow": "hidden",
                            "display": "flex",
                            "flexDirection": "column",
                            "maxHeight": "92vh",
                        },
                        children=[
                            # Static Header
                            html.Div(
                                style={
                                    "backgroundColor": "#0f172a",
                                    "padding": "16px 24px",
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "borderBottom": "1px solid #1e293b",
                                },
                                children=[
                                    html.Div(
                                        id="modal-header-titles",
                                        children=[
                                            html.Span(
                                                "PHYSICAL ASSET · MSC VESSEL CARGO COMPARTMENT B-3",
                                                style={
                                                    "fontSize": "11px",
                                                    "fontWeight": "800",
                                                    "letterSpacing": "1.2px",
                                                    "color": "#38bdf8",
                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                },
                                            ),
                                            html.H2(
                                                "MSC Ballast Tank B-3 Inspection",
                                                style={
                                                    "fontSize": "22px",
                                                    "fontWeight": "800",
                                                    "color": "#ffffff",
                                                    "margin": "2px 0 0 0",
                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                },
                                            ),
                                            html.Span(
                                                "Frame 38 Port Bulkhead · Mounts LiDAR LD-01, Hyperspectral HS-01 & 4K Video",
                                                style={"fontSize": "12px", "color": "#94a3b8"},
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        style={"display": "flex", "alignItems": "center", "gap": "14px"},
                                        children=[
                                            html.Div(id="modal-header-status-badge"),
                                            html.Button(
                                                "✕ Close",
                                                id="btn-close-modal",
                                                n_clicks=0,
                                                style={
                                                    "minHeight": "38px",
                                                    "padding": "6px 16px",
                                                    "borderRadius": "8px",
                                                    "border": "1.5px solid #475569",
                                                    "backgroundColor": "#1e293b",
                                                    "color": "#ffffff",
                                                    "fontSize": "13px",
                                                    "fontWeight": "800",
                                                    "cursor": "pointer",
                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # Dynamic Body
                            html.Div(
                                id="modal-body-container",
                                style={"display": "flex", "flexDirection": "column", "width": "100%", "overflow": "hidden"},
                            ),
                        ],
                    ),
                ],
            ),

            # Hidden Sync Inputs & Output for SVG Fluid Story Diagram & Animations
            dcc.Input(id="svg-selected-sync-input", type="hidden", value=""),
            dcc.Input(id="svg-phase-sync-input", type="hidden", value="1"),
            html.Button(id="btn-clear-selection", style={"display": "none"}, n_clicks=0),
            html.Div(id="dummy-clientside-anim", style={"display": "none"}),

            # Top Header Block
            html.Div(
                children=[
                    html.Div(
                        CONTENT["app"]["eyebrow"].upper(),
                        style={
                            "fontSize": "13px",
                            "fontWeight": "700",
                            "letterSpacing": "1.8px",
                            "color": "#64748b",
                            "marginBottom": "4px",
                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                        },
                    ),
                    html.H1(
                        CONTENT["app"]["title"],
                        style={
                            "fontSize": "34px",
                            "fontWeight": "800",
                            "letterSpacing": "-0.5px",
                            "color": "#0f172a",
                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                            "lineHeight": 1.15,
                        },
                    ),
                ]
            ),

            # Phase Buttons Bar (4 large touch-friendly buttons under title)
            html.Div(
                id="phase-buttons-bar",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(5, 1fr)",
                    "gap": "12px",
                    "width": "100%",
                },
                children=[
                    html.Button(
                        id=f"btn-phase-{str(p).replace('.', '_')}",
                        n_clicks=0,
                        className="phase-tab-btn",
                        style={
                            "minHeight": "60px",
                            "padding": "10px 14px",
                            "borderRadius": "12px",
                            "border": "2px solid #cbd5e1",
                            "backgroundColor": "#ffffff",
                            "cursor": "pointer",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "center",
                            "alignItems": "flex-start",
                            "textAlign": "left",
                        },
                        children=[
                            html.Span(
                                f"{CONTENT['phases'][p]['name'].upper()}",
                                style={
                                    "fontSize": "11px",
                                    "fontWeight": "800",
                                    "letterSpacing": "1.2px",
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "opacity": 0.85,
                                    "marginBottom": "2px",
                                },
                            ),
                            html.Span(
                                CONTENT["phases"][p]["title"],
                                style={
                                    "fontSize": "15px",
                                    "fontWeight": "700",
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "lineHeight": 1.15,
                                },
                            ),
                        ],
                    )
                    for p in [1, 2, 3, 4, 4.5]
                ],
            ),

            # Main 2-Column Presentation Area
            html.Div(
                id="main-flex-container",
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "gap": "24px",
                    "alignItems": "stretch",
                    "flex": "1",
                },
                children=[
                    # Left 70% Column: Cytoscape Graph OR Phase 3 Ship Simulation
                    html.Div(
                        id="left-graph-pane",
                        style={
                            "flex": "7",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "12px",
                            "minWidth": "0",
                        },
                        children=[
                            # Phase 3 View Mode Switcher (Visible strictly when in Phase 3)
                            html.Div(
                                id="phase3-mode-bar",
                                style={
                                    "display": "none",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "backgroundColor": "#ffffff",
                                    "border": "1.5px solid #e2e8f0",
                                    "borderRadius": "12px",
                                    "padding": "6px 10px",
                                },
                                children=[
                                    html.Div(
                                        style={"display": "flex", "alignItems": "center", "gap": "10px"},
                                        children=[
                                            html.Span("PHASE 3 VIEW MODE:", style={
                                                "fontSize": "11px",
                                                "fontWeight": "800",
                                                "letterSpacing": "1px",
                                                "color": "#64748b",
                                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            }),
                                            html.Button(
                                                "🗺️ Architecture Network",
                                                id="btn-view-graph",
                                                n_clicks=0,
                                                className="mode-toggle-btn",
                                                style={
                                                    "padding": "8px 16px",
                                                    "borderRadius": "8px",
                                                    "border": "2px solid #cbd5e1",
                                                    "backgroundColor": "#ffffff",
                                                    "color": "#0f172a",
                                                    "fontSize": "13.5px",
                                                    "fontWeight": "700",
                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                    "cursor": "pointer",
                                                },
                                            ),
                                            html.Button(
                                                "🚢 Ship & Tank Live Twin",
                                                id="btn-view-ship",
                                                n_clicks=0,
                                                className="mode-toggle-btn",
                                                style={
                                                    "padding": "8px 16px",
                                                    "borderRadius": "8px",
                                                    "border": "2px solid #d97706",
                                                    "backgroundColor": "#f59e0b",
                                                    "color": "#ffffff",
                                                    "fontSize": "13.5px",
                                                    "fontWeight": "700",
                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                    "cursor": "pointer",
                                                },
                                            ),
                                        ],
                                    ),
                                    html.Span(
                                        "Interactive Tank & Sensor Simulation",
                                        style={"fontSize": "12px", "color": "#64748b", "fontWeight": "600"},
                                    ),
                                ],
                            ),

                            # View A: SVG Fluid Story Diagram Canvas
                            html.Div(
                                id="cytoscape-container",
                                className="view-enter-anim",
                                style={"display": "block", "width": "100%"},
                                children=[
                                    html.Div(
                                        id="svg-stage",
                                        className="stage",
                                        children=[
                                            html.Div(id="svg-diagram-mount", style={"width": "100%", "height": "100%"}),
                                            html.Div("Touch any bubble for details · arrow keys change phase · Esc clears", className="hint"),
                                        ],
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "padding": "6px 8px 0 8px",
                                            "fontSize": "12.5px",
                                            "color": "#64748b",
                                            "fontWeight": "500",
                                        },
                                        children=[
                                            html.Span("Touch any bubble to inspect connections · Tap again or empty space to clear"),
                                            html.Span("← / → arrow keys change phase · Esc clears"),
                                        ],
                                    ),
                                ],
                            ),

                            # View B: Phase 3 Ship & Tank Live Twin Simulation Canvas
                            html.Div(
                                id="ship-simulation-container",
                                className="view-enter-anim",
                                style={
                                    "display": "none",
                                    "flexDirection": "column",
                                    "gap": "14px",
                                    "width": "100%",
                                },
                                children=[
                                    # Top Simulation Control Bar with Simulation Action Buttons
                                    html.Div(
                                        style={
                                            "backgroundColor": "#ffffff",
                                            "borderRadius": "12px",
                                            "border": "1.5px solid #e2e8f0",
                                            "padding": "14px 18px",
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "flexWrap": "wrap",
                                            "gap": "12px",
                                        },
                                        children=[
                                            html.Div(
                                                style={"display": "flex", "flexDirection": "column", "gap": "2px"},
                                                children=[
                                                    html.Span(
                                                        "PHYSICAL TO VIRTUAL ASSET SYNCHRONIZATION",
                                                        style={
                                                            "fontSize": "11px",
                                                            "fontWeight": "800",
                                                            "letterSpacing": "1.2px",
                                                            "color": "#64748b",
                                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                        },
                                                    ),
                                                    html.Span(
                                                        "Click to inject a rust event on the real ship and observe detection in the Digital Twin:",
                                                        style={"fontSize": "13.5px", "fontWeight": "700", "color": "#0f172a"},
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                style={"display": "flex", "alignItems": "center", "gap": "10px"},
                                                children=[
                                                    # Action Button: Rust Event
                                                    html.Button(
                                                        "⚠️ Simulate Rust Event on Ship",
                                                        id="btn-sim-rust",
                                                        n_clicks=0,
                                                        className="sim-action-btn",
                                                        style={
                                                            "minHeight": "52px",
                                                            "padding": "10px 22px",
                                                            "borderRadius": "10px",
                                                            "border": "2px solid #ef4444",
                                                            "backgroundColor": "#fef2f2",
                                                            "color": "#b91c1c",
                                                            "fontSize": "15px",
                                                            "fontWeight": "800",
                                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                            "cursor": "pointer",
                                                        },
                                                    ),
                                                    # Action Button: Reset
                                                    html.Button(
                                                        "🟢 Baseline (Clean Ship)",
                                                        id="btn-sim-clean",
                                                        n_clicks=0,
                                                        className="sim-action-btn",
                                                        style={
                                                            "minHeight": "52px",
                                                            "padding": "10px 20px",
                                                            "borderRadius": "10px",
                                                            "border": "2px solid #cbd5e1",
                                                            "backgroundColor": "#ffffff",
                                                            "color": "#475569",
                                                            "fontSize": "15px",
                                                            "fontWeight": "700",
                                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                            "cursor": "pointer",
                                                        },
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),

                                    # Cybernetic Telemetry Bridge Banner: Real Ship -> Digital Twin
                                    html.Div(
                                        id="telemetry-bridge-banner",
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "backgroundColor": "#0f172a",
                                            "borderRadius": "12px",
                                            "padding": "10px 18px",
                                            "border": "1.5px solid #334155",
                                            "fontSize": "12px",
                                            "fontWeight": "700",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "color": "#94a3b8",
                                            "letterSpacing": "0.5px",
                                            "flexWrap": "wrap",
                                            "gap": "10px",
                                        },
                                        children=[
                                            html.Div(
                                                style={"display": "flex", "alignItems": "center", "gap": "6px"},
                                                children=[
                                                    html.Span("⚓ PHYSICAL ASSET", style={"color": "#38bdf8", "fontWeight": "800", "fontSize": "12.5px"}),
                                                    html.Span("· REAL MSC VESSEL (BULKHEAD FRAME 38)"),
                                                ],
                                            ),
                                            html.Div(
                                                id="bridge-stream-status",
                                                style={"display": "flex", "alignItems": "center", "gap": "8px", "color": "#f59e0b"},
                                                children=[
                                                    html.Span("LIVE SENSOR TELEMETRY STREAM", style={"fontWeight": "800", "fontSize": "11px", "letterSpacing": "1px"}),
                                                    html.Span("──────►", style={"fontSize": "14px", "fontWeight": "800", "color": "#38bdf8"}),
                                                ],
                                            ),
                                            html.Div(
                                                style={"display": "flex", "alignItems": "center", "gap": "6px"},
                                                children=[
                                                    html.Span("🌐 VIRTUAL ASSET", style={"color": "#34d399", "fontWeight": "800", "fontSize": "12.5px"}),
                                                    html.Span("· 3D DIGITAL TWIN (BALLAST TANK B-3 CAD MESH)"),
                                                ],
                                            ),
                                        ],
                                    ),

                                    # Dual-Viewport Grid: Real Ship (Physical) vs. Digital Twin (Virtual)
                                    html.Div(
                                        id="dual-twin-viewport-container",
                                        style={
                                            "display": "grid",
                                            "gridTemplateColumns": "1fr 1fr",
                                            "gap": "16px",
                                            "width": "100%",
                                        },
                                        children=[
                                            # Left Panel: Real Ship (Physical Asset)
                                            html.Div(
                                                id="real-ship-card",
                                                style={
                                                    "backgroundColor": "#0f172a",
                                                    "borderRadius": "14px",
                                                    "border": "2px solid #334155",
                                                    "boxShadow": "0 8px 24px rgba(0, 0, 0, 0.12)",
                                                    "overflow": "hidden",
                                                    "display": "flex",
                                                    "flexDirection": "column",
                                                    "position": "relative",
                                                    "transition": "all 0.4s ease",
                                                },
                                                children=[
                                                    # Real Ship Header
                                                    html.Div(
                                                        style={
                                                            "backgroundColor": "#1e293b",
                                                            "padding": "10px 14px",
                                                            "display": "flex",
                                                            "justifyContent": "space-between",
                                                            "alignItems": "center",
                                                            "borderBottom": "1px solid #334155",
                                                        },
                                                        children=[
                                                            html.Div(
                                                                style={"display": "flex", "alignItems": "center", "gap": "6px"},
                                                                children=[
                                                                    html.Span("⚓", style={"fontSize": "15px"}),
                                                                    html.Span(
                                                                        "REAL SHIP: BALLAST TANK B-3 CUTAWAY",
                                                                        style={"fontSize": "13px", "fontWeight": "800", "color": "#f8fafc", "fontFamily": "'Barlow Semi Condensed', sans-serif"},
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Span(
                                                                "🟢 PHYSICAL: NOMINAL BASELINE",
                                                                id="real-ship-status-badge",
                                                                style={
                                                                    "fontSize": "11px",
                                                                    "fontWeight": "800",
                                                                    "backgroundColor": "#059669",
                                                                    "color": "#ffffff",
                                                                    "padding": "3px 10px",
                                                                    "borderRadius": "6px",
                                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                                    "letterSpacing": "0.5px",
                                                                },
                                                            ),
                                                        ],
                                                    ),
                                                    # Real Ship Viewport with Cross-Fade & Defect Callout
                                                    html.Div(
                                                        id="ship-image-viewport",
                                                        style={
                                                            "width": "100%",
                                                            "backgroundColor": "#020617",
                                                            "position": "relative",
                                                            "height": "380px",
                                                            "overflow": "hidden",
                                                        },
                                                        children=[
                                                            # Baseline Clean Tank Image
                                                            html.Img(
                                                                id="ship-img-baseline",
                                                                src=IMAGE_DATA.get("clean", ""),
                                                                alt="Real MSC Vessel Nominal Baseline",
                                                                style={
                                                                    "position": "absolute",
                                                                    "inset": "0",
                                                                    "width": "100%",
                                                                    "height": "100%",
                                                                    "objectFit": "contain",
                                                                    "display": "block",
                                                                    "transition": "opacity 0.65s cubic-bezier(0.4, 0, 0.2, 1)",
                                                                    "opacity": 1.0,
                                                                    "pointerEvents": "none",
                                                                },
                                                            ),
                                                            # Rust Defect Tank Image
                                                            html.Img(
                                                                id="ship-img-rust",
                                                                src=IMAGE_DATA.get("rust", ""),
                                                                alt="Real MSC Vessel Rust Defect Formed",
                                                                style={
                                                                    "position": "absolute",
                                                                    "inset": "0",
                                                                    "width": "100%",
                                                                    "height": "100%",
                                                                    "objectFit": "contain",
                                                                    "display": "block",
                                                                    "transition": "opacity 0.65s cubic-bezier(0.4, 0, 0.2, 1)",
                                                                    "opacity": 0.0,
                                                                    "pointerEvents": "none",
                                                                },
                                                            ),
                                                            # Animated Laser Sweep
                                                            html.Div(id="sensor-laser-sweep", className="scanner-beam"),
                                                            # Physical Rust Callout Marker on Ship
                                                            html.Div(
                                                                id="real-ship-defect-callout",
                                                                style={
                                                                    "position": "absolute",
                                                                    "bottom": "22%",
                                                                    "left": "22%",
                                                                    "display": "none",
                                                                    "alignItems": "center",
                                                                    "gap": "6px",
                                                                    "backgroundColor": "rgba(220, 38, 38, 0.94)",
                                                                    "color": "#ffffff",
                                                                    "padding": "6px 12px",
                                                                    "borderRadius": "8px",
                                                                    "boxShadow": "0 0 16px rgba(239, 68, 68, 0.85)",
                                                                    "fontSize": "11.5px",
                                                                    "fontWeight": "800",
                                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                                    "letterSpacing": "0.5px",
                                                                    "pointerEvents": "none",
                                                                    "zIndex": "20",
                                                                },
                                                                children=[
                                                                    html.Span("🔴 PHYSICAL CORROSION: FRAME 38 LOWER BULKHEAD"),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                    # Real Ship Footer
                                                    html.Div(
                                                        style={
                                                            "backgroundColor": "#0f172a",
                                                            "padding": "8px 14px",
                                                            "borderTop": "1px solid #1e293b",
                                                            "display": "flex",
                                                            "justifyContent": "space-between",
                                                            "alignItems": "center",
                                                            "fontSize": "11px",
                                                            "color": "#94a3b8",
                                                            "fontWeight": "600",
                                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                        },
                                                        children=[
                                                            html.Span("MOUNTED SENSORS: LD-01 (LiDAR) · HS-01 (Hyperspectral) · CAM-02 (4K Video)"),
                                                            html.Span("PHYSICAL ASSET", style={"color": "#38bdf8", "fontWeight": "800"}),
                                                        ],
                                                    ),
                                                ],
                                            ),

                                            # Right Panel: Digital Twin of the Tank (Virtual Asset)
                                            html.Div(
                                                id="digital-twin-card",
                                                style={
                                                    "backgroundColor": "#030712",
                                                    "borderRadius": "14px",
                                                    "border": "2px solid #1e293b",
                                                    "boxShadow": "0 8px 24px rgba(0, 0, 0, 0.12)",
                                                    "overflow": "hidden",
                                                    "display": "flex",
                                                    "flexDirection": "column",
                                                    "position": "relative",
                                                    "transition": "all 0.4s ease",
                                                },
                                                children=[
                                                    # Digital Twin Header
                                                    html.Div(
                                                        style={
                                                            "backgroundColor": "#0f172a",
                                                            "padding": "10px 14px",
                                                            "display": "flex",
                                                            "justifyContent": "space-between",
                                                            "alignItems": "center",
                                                            "borderBottom": "1px solid #1e293b",
                                                        },
                                                        children=[
                                                            html.Div(
                                                                style={"display": "flex", "alignItems": "center", "gap": "6px"},
                                                                children=[
                                                                    html.Span("🌐", style={"fontSize": "15px"}),
                                                                    html.Span(
                                                                        "DIGITAL TWIN: 3D TANK CAD MODEL",
                                                                        style={"fontSize": "13px", "fontWeight": "800", "color": "#f8fafc", "fontFamily": "'Barlow Semi Condensed', sans-serif"},
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Span(
                                                                "🟢 TWIN: SYNCHRONIZED (NOMINAL)",
                                                                id="digital-twin-status-badge",
                                                                style={
                                                                    "fontSize": "11px",
                                                                    "fontWeight": "800",
                                                                    "backgroundColor": "#059669",
                                                                    "color": "#ffffff",
                                                                    "padding": "3px 10px",
                                                                    "borderRadius": "6px",
                                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                                    "letterSpacing": "0.5px",
                                                                },
                                                            ),
                                                        ],
                                                    ),
                                                    # Digital Twin Viewport (Dual-Layer 3D CAD Tank Model with Cross-Fade)
                                                    html.Div(
                                                        id="digital-twin-viewport",
                                                        style={
                                                            "width": "100%",
                                                            "backgroundColor": "#020617",
                                                            "position": "relative",
                                                            "height": "380px",
                                                            "overflow": "hidden",
                                                        },
                                                        children=[
                                                            # Baseline Nominal Digital Twin 3D CAD Tank
                                                            html.Img(
                                                                id="dt-img-baseline",
                                                                src=IMAGE_DATA.get("dt_clean", ""),
                                                                alt="Digital Twin Ballast Tank B-3 CAD Nominal Model",
                                                                style={
                                                                    "position": "absolute",
                                                                    "inset": "0",
                                                                    "width": "100%",
                                                                    "height": "100%",
                                                                    "objectFit": "contain",
                                                                    "display": "block",
                                                                    "transition": "opacity 0.65s cubic-bezier(0.4, 0, 0.2, 1)",
                                                                    "opacity": 1.0,
                                                                    "pointerEvents": "none",
                                                                },
                                                            ),
                                                            # Defect Detected Digital Twin 3D CAD Tank
                                                            html.Img(
                                                                id="dt-img-rust",
                                                                src=IMAGE_DATA.get("dt_rust", ""),
                                                                alt="Digital Twin Ballast Tank B-3 CAD Defect Detected",
                                                                style={
                                                                    "position": "absolute",
                                                                    "inset": "0",
                                                                    "width": "100%",
                                                                    "height": "100%",
                                                                    "objectFit": "contain",
                                                                    "display": "block",
                                                                    "transition": "opacity 0.65s cubic-bezier(0.4, 0, 0.2, 1)",
                                                                    "opacity": 0.0,
                                                                    "pointerEvents": "none",
                                                                },
                                                            ),
                                                            # Animated Twin Telemetry / Laser Sweep
                                                            html.Div(id="dt-scanner-sweep", className="scanner-beam"),
                                                            # Defect Detection HUD Callout Marker on Digital Twin
                                                            html.Div(
                                                                id="digital-twin-defect-callout",
                                                                style={
                                                                    "position": "absolute",
                                                                    "bottom": "22%",
                                                                    "right": "18%",
                                                                    "display": "none",
                                                                    "alignItems": "center",
                                                                    "gap": "6px",
                                                                    "backgroundColor": "rgba(220, 38, 38, 0.94)",
                                                                    "color": "#ffffff",
                                                                    "padding": "6px 12px",
                                                                    "borderRadius": "8px",
                                                                    "boxShadow": "0 0 16px rgba(239, 68, 68, 0.85)",
                                                                    "fontSize": "11.5px",
                                                                    "fontWeight": "800",
                                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                                    "letterSpacing": "0.5px",
                                                                    "pointerEvents": "none",
                                                                    "zIndex": "20",
                                                                },
                                                                children=[
                                                                    html.Span("⚠️ TWIN CAD DELTA: -1.8mm RECESS DETECTED"),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                    # Digital Twin Footer
                                                    html.Div(
                                                        style={
                                                            "backgroundColor": "#090d16",
                                                            "padding": "8px 14px",
                                                            "borderTop": "1px solid #1e293b",
                                                            "display": "flex",
                                                            "justifyContent": "space-between",
                                                            "alignItems": "center",
                                                            "fontSize": "11px",
                                                            "color": "#94a3b8",
                                                            "fontWeight": "600",
                                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                        },
                                                        children=[
                                                            html.Span("SURFACE AREA LIBRARY (SAC): Continuous mesh profiling & delta detection"),
                                                            html.Span("SYNC: < 180ms", style={"color": "#38bdf8", "fontWeight": "800"}),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),

                                    # Provenance HUD: "From where the changes were made"
                                    html.Div(
                                        id="provenance-hud-container",
                                        children=render_provenance_hud("clean"),
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Right 30% Column: Notes & Details Panel
                    html.Div(
                        id="right-notes-pane",
                        style={
                            "flex": "3",
                            "minWidth": "360px",
                            "backgroundColor": "#ffffff",
                            "borderRadius": "14px",
                            "border": "1px solid #e2e8f0",
                            "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03)",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "space-between",
                            "overflow": "hidden",
                        },
                        children=[
                            # Scrollable Dynamic Notes Content
                            html.Div(
                                id="notes-panel-content",
                                className="custom-scroll",
                                style={
                                    "padding": "24px",
                                    "overflowY": "auto",
                                    "maxHeight": "548px",
                                    "flex": "1",
                                },
                            ),
                            # Pinned Bottom Navigation Buttons
                            html.Div(
                                style={
                                    "padding": "16px 20px",
                                    "borderTop": "1px solid #e2e8f0",
                                    "backgroundColor": "#f8fafc",
                                    "display": "grid",
                                    "gridTemplateColumns": "1fr 1fr",
                                    "gap": "12px",
                                },
                                children=[
                                    html.Button(
                                        "← Previous",
                                        id="btn-prev-phase",
                                        n_clicks=0,
                                        style={
                                            "minHeight": "56px",
                                            "borderRadius": "10px",
                                            "border": "2px solid #cbd5e1",
                                            "backgroundColor": "#ffffff",
                                            "color": "#0f172a",
                                            "fontSize": "16px",
                                            "fontWeight": "700",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "cursor": "pointer",
                                            "transition": "all 0.15s ease",
                                        },
                                    ),
                                    html.Button(
                                        "Next →",
                                        id="btn-next-phase",
                                        n_clicks=0,
                                        style={
                                            "minHeight": "56px",
                                            "borderRadius": "10px",
                                            "border": "2px solid #0f172a",
                                            "backgroundColor": "#0f172a",
                                            "color": "#ffffff",
                                            "fontSize": "16px",
                                            "fontWeight": "700",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "cursor": "pointer",
                                            "transition": "all 0.15s ease",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


app.layout = create_layout



# =============================================================================
# NODE MODAL METADATA, BLUEPRINTS & PLACEHOLDER DIALOGS
# =============================================================================

NODE_MODAL_METADATA = {
    "lidar": {
        "super_title": "EDGE SENSOR · OPTICAL TIME-OF-FLIGHT SENSOR",
        "title": "LD-01 3D Conical LiDAR Laser Scanner",
        "subtitle": "Mounted on Tank Ceiling Dome · 1.2M points/sec · ±0.8mm depth accuracy · Point cloud output to SAC",
        "clean_badge": "🔵 3D LASER SCANNING ACTIVE · POINT CLOUD BUFFER NOMINAL",
        "clean_badge_style": {"backgroundColor": "#0c4a6e", "color": "#38bdf8", "border": "1.5px solid #0284c7"},
        "rust_badge": "⚠️ DEFECT CONTOUR DETECTED @ FR 38 (-1.8mm RECESS)",
        "rust_badge_style": {"backgroundColor": "#450a0a", "color": "#f87171", "border": "1.5px solid #ef4444"},
    },
    "rgb": {
        "super_title": "EDGE SENSOR · 4K MACHINE VISION OPTICAL ARRAY",
        "title": "CAM-02 High-Definition RGB Optical Inspection Video",
        "subtitle": "3840×2160 @ 60 FPS · Polarized Macro Lens · Surface colorimetry & blistering texture analysis",
        "clean_badge": "🟢 4K VIDEO FEED STREAMING · EPOXY COATING NOMINAL",
        "clean_badge_style": {"backgroundColor": "#064e3b", "color": "#34d399", "border": "1.5px solid #10b981"},
        "rust_badge": "⚠️ COLOR DELTA DETECTED: OXIDATION COLOR SHIFT #B91C1C",
        "rust_badge_style": {"backgroundColor": "#450a0a", "color": "#f87171", "border": "1.5px solid #ef4444"},
    },
    "hyp": {
        "super_title": "EDGE SENSOR · CHEMICAL SPECTRAL IMAGING",
        "title": "Cubert Hyperspectral Chemical Scanner (Auto_000_1123.cu3s)",
        "subtitle": "450 - 850 nm VNIR Spectral Domain · Multi-Point Raw Spectral Profiling & Fe₂O₃ Oxidation Detection",
        "clean_badge": "🟢 SPECTRAL SCAN CLEAR · NOMINAL COATING REFLECTANCE",
        "clean_badge_style": {"backgroundColor": "#064e3b", "color": "#34d399", "border": "1.5px solid #10b981"},
        "rust_badge": "🔴 RAW SPECTRAL PEAK DETECTED (710 - 770 nm OXIDATION)",
        "rust_badge_style": {"backgroundColor": "#450a0a", "color": "#f87171", "border": "1.5px solid #ef4444"},
    },
    "sac": {
        "super_title": "COMPUTATION · FINITE ELEMENT GEOMETRIC ENGINE",
        "title": "SAC: Surface Area Library & Mesh Geometry Engine",
        "subtitle": "Delaunay Triangulation · Volumetric & Surface Area Integration · Real-time delta comparison against CAD baseline",
        "clean_badge": "🟢 MESH AREA NOMINAL: Δ = 0.0 m² (NO EXPANSION)",
        "clean_badge_style": {"backgroundColor": "#064e3b", "color": "#34d399", "border": "1.5px solid #10b981"},
        "rust_badge": "⚠️ CORROSION EXPANSION: 4.8 m² DEGRADED SURFACE DETECTED",
        "rust_badge_style": {"backgroundColor": "#450a0a", "color": "#f87171", "border": "1.5px solid #ef4444"},
    },
    "vtl": {
        "super_title": "COMPUTATION · CLASS SOCIETY & SCANTLING DATABASE",
        "title": "VTL Prototype: Virtual Technical Library & Scantling Records",
        "subtitle": "DNV-GL Class Registry · Steel Grade NV DH36 Scantling Plans · Historical coating decay curves",
        "clean_badge": "🟢 SCANTLING COMPLIANT: 18.0mm STEEL (MIN ALLOWABLE 14.5mm)",
        "clean_badge_style": {"backgroundColor": "#064e3b", "color": "#34d399", "border": "1.5px solid #10b981"},
        "rust_badge": "⚠️ SCANTLING MARGIN REDUCED: 16.2mm REMAINING (-1.8mm LOSS)",
        "rust_badge_style": {"backgroundColor": "#450a0a", "color": "#f87171", "border": "1.5px solid #ef4444"},
    },
    "samm": {
        "super_title": "BEYOND THE TWIN · FLEET DECISION SUPPORT SYSTEM",
        "title": "LRMS: Long Range Maintenance Schedule",
        "subtitle": "CBM (Condition-Based Maintenance) Policy Engine · Drydock work pack generator · Repair ROI optimizer",
        "clean_badge": "🟢 VESSEL VOYAGE READY · NO WORK ORDERS REQUIRED",
        "clean_badge_style": {"backgroundColor": "#064e3b", "color": "#34d399", "border": "1.5px solid #10b981"},
        "rust_badge": "🔴 WORK PACK GENERATED: WP-MSC-2026-B3 (DRYDOCK RECOMMENDED)",
        "rust_badge_style": {"backgroundColor": "#450a0a", "color": "#f87171", "border": "1.5px solid #ef4444"},
    },
    "cms": {
        "super_title": "BEYOND THE TWIN · FLEET SITUATIONAL AWARENESS",
        "title": "HMS: Hull Maintenance System",
        "subtitle": "Predictive Remaining Useful Life (RUL) Modeling · Fleet corrosion trends · Cathodic protection monitoring",
        "clean_badge": "🟢 FLEET STATUS NOMINAL · RUL: 8.4 YEARS",
        "clean_badge_style": {"backgroundColor": "#064e3b", "color": "#34d399", "border": "1.5px solid #10b981"},
        "rust_badge": "⚠️ ACCELERATED DECAY PREDICTED · RUL DROPPED TO 2.1 YEARS",
        "rust_badge_style": {"backgroundColor": "#450a0a", "color": "#f87171", "border": "1.5px solid #ef4444"},
    },
}

NODE_MODAL_DETAILS = {
    "lidar": {
        "specs": [("SENSOR MODEL", "Velodyne/Ouster VLP-32 Marine"), ("OPTICAL WAVELENGTH", "905 nm Class 1 (Eye-Safe)"), ("FIELD OF VIEW", "360° Horiz × 40° Vert")],
        "telemetry_nominal": [("PULSE RATE", "1,248,000 pts/sec"), ("ACCURACY TOLERANCE", "± 0.8 mm"), ("SURFACE PROFILE", "Bulkhead Intact (Δ = 0.0mm)")],
        "telemetry_rust": [("PULSE RATE", "1,248,000 pts/sec"), ("ACCURACY TOLERANCE", "± 0.8 mm"), ("SURFACE PROFILE", "⚠️ -1.8 mm Defect @ FR 38")],
        "pipeline": [("MOUNT LOCATION", "Ballast Tank B-3 Ceiling Dome"), ("OUTPUT RECEIVER", "Surface Area Library (SAC)"), ("STREAM PROTOCOL", "UDP Point Cloud Buffer (<28ms)")],
    },
    "rgb": {
        "specs": [("CAMERA MODEL", "Sony IMX530 Global Shutter CMOS"), ("RESOLUTION", "3840 × 2160 (4K UHD) @ 60 FPS"), ("OPTICS", "16mm Polarized Anti-Fog Macro")],
        "telemetry_nominal": [("EXPOSURE", "1/500s Auto / ISO 100"), ("SURFACE COLOR HUE", "142° Epoxy Coating (#0f766e)"), ("TEXTURE VARIANCE", "σ² = 1.4 (Uniform Finish)")],
        "telemetry_rust": [("EXPOSURE", "1/500s Auto / ISO 100"), ("SURFACE COLOR HUE", "⚠️ 18° Ochre Rust (#b91c1c)"), ("TEXTURE VARIANCE", "⚠️ σ² = 48.2 (Pitting & Spall)")],
        "pipeline": [("MOUNT LOCATION", "Frame 38 Bulkhead Rigging"), ("OUTPUT RECEIVER", "Digital Twin CAD Texture Engine"), ("STREAM PROTOCOL", "RTSP / WebRTC Stream (<35ms)")],
    },
    "hyp": {
        "specs": [("SPECTRAL CAMERA", "Cubert Ultris / FireflEYE VNIR"), ("FILE SOURCE", "Auto_000_1123.cu3s (Frame 0)"), ("SPECTRAL DOMAIN", "450 nm – 850 nm (VNIR Channels)")],
        "telemetry_nominal": [("SAMPLING PINS", "10 Spatial Regions of Interest"), ("PEAK RESPONSE", "Channels 710 - 750 nm (~1050 RAW counts)"), ("SURFACE PROFILE", "Coating Intact (Nominal Reflectance)")],
        "telemetry_rust": [("SAMPLING PINS", "10 Spatial Regions of Interest"), ("PEAK RESPONSE", "🔴 Elevated Fe₂O₃ Oxidation Band @ 730nm"), ("CORROSION STATE", "⚠️ Heterogeneous Pitting / Iron Oxide Detected")],
        "pipeline": [("MOUNT LOCATION", "Cubert Test Stand / Tank Traverse Rig"), ("OUTPUT RECEIVER", "VTL Scantling & Digital Twin"), ("STREAM PROTOCOL", "gRPC Chemical Tensor (<45ms)")],
    },
    "sac": {
        "specs": [("GEOMETRIC ENGINE", "Delaunay Adaptive Polygonal Tessellation"), ("MESH MAPPING", "Double Surface Integral ∬ dS"), ("CAD BASELINE REF", "MSC-TNK-B3-V2.1 Scantling")],
        "telemetry_nominal": [("ACTIVE VERTICES", "42,850 Vertices"), ("TRIANGULAR FACETS", "85,210 Polygons"), ("SURFACE AREA DELTA", "0.0 m² (CAD Equilibrium)")],
        "telemetry_rust": [("ACTIVE VERTICES", "42,850 Vertices"), ("TRIANGULAR FACETS", "85,210 Polygons"), ("SURFACE AREA DELTA", "⚠️ +4.8 m² Degraded Area @ FR 38")],
        "pipeline": [("INPUT INGESTION", "LiDAR LD-01 Point Stream"), ("OUTPUT RECEIVER", "VTL & Digital Twin (DT) CAD Mesh"), ("PROCESSING DELAY", "<140 ms Pipeline Latency")],
    },
    "vtl": {
        "specs": [("CLASS REGISTRY", "DNV-GL 100 A5 Container Ship"), ("STEEL SPECIFICATION", "NV DH36 High-Strength Maritime Steel"), ("PLATE NOMINAL", "18.0 mm (Renewal Min: 14.5 mm)")],
        "telemetry_nominal": [("CURRENT STEEL THICKNESS", "18.0 mm (Nominal Baseline)"), ("SAFETY MARGIN", "+3.5 mm Above Mandatory Renewal"), ("CLASS COMPLIANCE", "100% Fully Compliant")],
        "telemetry_rust": [("CURRENT STEEL THICKNESS", "⚠️ 16.2 mm (-1.8 mm Local Loss)"), ("SAFETY MARGIN", "⚠️ +1.7 mm (Action Recommended)"), ("CLASS COMPLIANCE", "⚠️ Survey Non-Conformity Advisory")],
        "pipeline": [("INPUT INGESTION", "SAC Surface Area & Mesh Profiling"), ("OUTPUT RECEIVER", "Digital Twin Records & LRMS Decision"), ("DATABASE ARCH", "Encrypted Cloud Scantling SQL")],
    },
    "samm": {
        "specs": [("POLICY REGIME", "Dynamic Condition-Based Maintenance (CBM)"), ("ENTERPRISE ASSET", "MSC Fleet Decision Support Suite"), ("OPTIMIZATION", "Min Laytime & Zero Class Disruption")],
        "telemetry_nominal": [("WORK ORDER DISPATCH", "None Required (Voyage Ready)"), ("VESSEL AVAILABILITY", "99.8% Nominal Uptime"), ("DRYDOCK FORECAST", "Scheduled 5-Year Survey (2028)")],
        "telemetry_rust": [("WORK ORDER DISPATCH", "🔴 WP-2026-B3 (Drydock Spot Hydroblast)"), ("VESSEL AVAILABILITY", "⚠️ 94.2% (Laytime Action Required)"), ("DRYDOCK FORECAST", "⚠️ Urgent 18hr Laytime Recommended")],
        "pipeline": [("INPUT INGESTION", "Digital Twin State & Degradation Delta"), ("OUTPUT RECEIVER", "MSC Ship Operations & Port Engineers"), ("DISPATCH PROTOCOL", "REST / SAP PM Automated Work Order")],
    },
    "cms": {
        "specs": [("ANALYTICS ENGINE", "Weibull Extreme Value & Arrhenius Kinetic"), ("CATHODIC MONITOR", "Sacrificial Zinc Anode Array (-850mV)"), ("ENTERPRISE LINK", "SAP PM / DNV Veracity Asset Cloud")],
        "telemetry_nominal": [("FLEET CORROSION INDEX", "Grade A+ (98 / 100 Score)"), ("PREDICTED RUL", "8.4 Years to Renewal Limit"), ("CORROSION RATE", "0.04 mm/yr (Normal Passive)")],
        "telemetry_rust": [("FLEET CORROSION INDEX", "⚠️ Grade C (64 / 100 Score)"), ("PREDICTED RUL", "⚠️ 2.1 Years (Decay Accelerated)"), ("CORROSION RATE", "🔴 0.38 mm/yr (Active Attack)")],
        "pipeline": [("INPUT INGESTION", "Digital Twin Telemetry & VTL Records"), ("OUTPUT RECEIVER", "MSC Executive Fleet Awareness Dashboard"), ("TELEMETRY UPDATE", "Streaming Real-Time Updates")],
    },
}

def get_placeholder_svg(node_id: str, is_rust: bool = False) -> str:
    """Generate professional, high-detail engineering SVG blueprints for all non-tank/twin nodes."""
    
    if node_id == "lidar":
        laser_color = "#f97316" if is_rust else "#38bdf8"
        alert_badge = """
        <rect x="520" y="24" width="250" height="36" rx="8" fill="#450a0a" stroke="#ef4444" stroke-width="1.5"/>
        <text x="645" y="46" fill="#fca5a5" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">⚠️ POINT CLOUD DEFECT DETECTED @ FR 38</text>
        """ if is_rust else """
        <rect x="520" y="24" width="250" height="36" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
        <text x="645" y="46" fill="#6ee7b7" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">🟢 SCANNER NOMINAL: NO SURFACE RECESS</text>
        """
        recess_val = "-1.8 mm (CORROSION PIT)" if is_rust else "0.0 mm (NOMINAL)"
        recess_col = "#ef4444" if is_rust else "#10b981"
        
        return f"""<svg width="100%" height="100%" viewBox="0 0 840 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <radialGradient id="lidarGlow" cx="50%" cy="20%" r="70%">
                    <stop offset="0%" stop-color="{laser_color}" stop-opacity="0.35"/>
                    <stop offset="70%" stop-color="#0284c7" stop-opacity="0.05"/>
                    <stop offset="100%" stop-color="#030712" stop-opacity="0"/>
                </radialGradient>
                <pattern id="lidarGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.8"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="#030712"/>
            <rect width="100%" height="100%" fill="url(#lidarGrid)"/>
            
            <!-- Baseline & Stations -->
            <line x1="50" y1="330" x2="790" y2="330" stroke="#334155" stroke-width="1.5" stroke-dasharray="4 4"/>
            <text x="55" y="322" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="700">BASELINE: Z = -4.2m LOWER BULKHEAD</text>
            <text x="720" y="322" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="700">FRAME 36-40</text>
            
            {alert_badge}
            
            <!-- LiDAR Conical Laser Projection -->
            <polygon points="420,65 140,330 700,330" fill="url(#lidarGlow)" stroke="{laser_color}" stroke-width="1.5" stroke-dasharray="6 4"/>
            
            <!-- Scanner Head Mounted at Ceiling Dome -->
            <rect x="370" y="24" width="100" height="42" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="2"/>
            <circle cx="420" cy="45" r="12" fill="#38bdf8"/>
            <circle cx="420" cy="45" r="6" fill="#ffffff"/>
            <text x="420" y="16" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">LD-01 3D LASER SCANNER HEAD</text>
            
            <!-- Scan Rays -->
            <line x1="420" y1="45" x2="220" y2="330" stroke="#0ea5e9" stroke-width="1.2" opacity="0.8"/>
            <line x1="420" y1="45" x2="330" y2="330" stroke="{laser_color}" stroke-width="1.2" opacity="0.8"/>
            <line x1="420" y1="45" x2="490" y2="330" stroke="{laser_color}" stroke-width="1.2" opacity="0.8"/>
            <line x1="420" y1="45" x2="620" y2="330" stroke="#0ea5e9" stroke-width="1.2" opacity="0.8"/>
            
            <!-- 3D Point Cloud Matrix (Scatter Dots) -->
            <g fill="{laser_color}" opacity="0.85">
                <circle cx="240" cy="310" r="2.5"/><circle cx="260" cy="295" r="2"/><circle cx="280" cy="305" r="3"/>
                <circle cx="300" cy="290" r="2.5"/><circle cx="330" cy="315" r="2"/><circle cx="350" cy="300" r="2.5"/>
                <circle cx="380" cy="285" r="3"/><circle cx="410" cy="295" r="2.5"/><circle cx="430" cy="310" r="2"/>
                <circle cx="460" cy="290" r="2.5"/><circle cx="480" cy="305" r="3"/><circle cx="510" cy="295" r="2"/>
                <circle cx="540" cy="310" r="2.5"/><circle cx="560" cy="285" r="2"/><circle cx="590" cy="305" r="3"/>
                <circle cx="620" cy="320" r="2.5"/><circle cx="200" cy="325" r="2"/>
            </g>
            
            <!-- Volumetric Thickness Delta Overlay Cards -->
            <rect x="70" y="80" width="160" height="60" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="150" y="102" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">POINT BUFFER RATE</text>
            <text x="150" y="125" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="16" font-weight="800" text-anchor="middle">1,248,000 pts/s</text>
            
            <rect x="70" y="155" width="160" height="60" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="{recess_col}" stroke-width="1.5"/>
            <text x="150" y="177" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">MAX DEPTH DELTA</text>
            <text x="150" y="200" fill="{recess_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800" text-anchor="middle">{recess_val}</text>
            
            <rect x="70" y="230" width="160" height="60" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#10b981" stroke-width="1.5"/>
            <text x="150" y="252" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">DEPTH ACCURACY</text>
            <text x="150" y="275" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="16" font-weight="800" text-anchor="middle">± 0.8 mm</text>
        </svg>"""

    elif node_id == "rgb":
        alert_badge = """
        <rect x="520" y="24" width="250" height="36" rx="8" fill="#450a0a" stroke="#ef4444" stroke-width="1.5"/>
        <text x="645" y="46" fill="#fca5a5" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">⚠️ BLISTERING & RUST COLOR DETECTED</text>
        """ if is_rust else """
        <rect x="520" y="24" width="250" height="36" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
        <text x="645" y="46" fill="#6ee7b7" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">🟢 4K VIDEO: COATING INTEGRITY NOMINAL</text>
        """
        hue_val = "18.4° (OXIDIZED OCHRE #b91c1c)" if is_rust else "142.1° (COATING EPOXY #0f766e)"
        hue_col = "#ef4444" if is_rust else "#10b981"
        return f"""<svg width="100%" height="100%" viewBox="0 0 840 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="rgbGrid" width="30" height="30" patternUnits="userSpaceOnUse">
                    <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" stroke-width="0.8"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="#030712"/>
            <rect width="100%" height="100%" fill="url(#rgbGrid)"/>
            
            {alert_badge}
            
            <!-- Camera Viewport Reticle Box -->
            <rect x="270" y="80" width="300" height="230" rx="12" fill="#090d16" stroke="#3b82f6" stroke-width="2"/>
            
            <!-- Lens Crosshairs -->
            <line x1="420" y1="90" x2="420" y2="185" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="4 2"/>
            <line x1="420" y1="205" x2="420" y2="300" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="4 2"/>
            <line x1="280" y1="195" x2="410" y2="195" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="4 2"/>
            <line x1="430" y1="195" x2="560" y2="195" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="4 2"/>
            <circle cx="420" cy="195" r="28" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
            <circle cx="420" cy="195" r="3" fill="#38bdf8"/>
            
            <!-- Inspection Reticle Corner Brackets -->
            <path d="M 290 100 L 290 115 M 290 100 L 305 100" stroke="#38bdf8" stroke-width="2" fill="none"/>
            <path d="M 550 100 L 550 115 M 550 100 L 535 100" stroke="#38bdf8" stroke-width="2" fill="none"/>
            <path d="M 290 290 L 290 275 M 290 290 L 305 290" stroke="#38bdf8" stroke-width="2" fill="none"/>
            <path d="M 550 290 L 550 275 M 550 290 L 535 290" stroke="#38bdf8" stroke-width="2" fill="none"/>
            
            <!-- Live Viewport Status Tag -->
            <text x="285" y="74" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800">CAM-02 4K UHD OPTICAL FEED · 60 FPS</text>
            <text x="555" y="74" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="700" text-anchor="end">POLARIZED MACRO</text>
            
            <!-- Telemetry Cards Left -->
            <rect x="50" y="80" width="180" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="140" y="103" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">RESOLUTION</text>
            <text x="140" y="128" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="15" font-weight="800" text-anchor="middle">3840 × 2160 (4K UHD)</text>
            
            <rect x="50" y="160" width="180" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#10b981" stroke-width="1.5"/>
            <text x="140" y="183" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">FRAME RATE & LATENCY</text>
            <text x="140" y="208" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="15" font-weight="800" text-anchor="middle">60 FPS · &lt; 28 ms</text>
            
            <rect x="50" y="240" width="180" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="{hue_col}" stroke-width="1.5"/>
            <text x="140" y="263" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">SURFACE COLOR HUE</text>
            <text x="140" y="288" fill="{hue_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="11.5" font-weight="800" text-anchor="middle">{hue_val}</text>
            
            <!-- Telemetry Cards Right (Color Channel Histogram) -->
            <rect x="610" y="80" width="180" height="225" rx="10" fill="rgba(15, 23, 42, 0.9)" stroke="#334155" stroke-width="1.5"/>
            <text x="700" y="105" fill="#f8fafc" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">COLOR CHROMINANCE</text>
            <text x="630" y="135" fill="#ef4444" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="700">R: {'92%' if is_rust else '24%'}</text>
            <rect x="680" y="125" width="95" height="12" rx="4" fill="#1e293b"/>
            <rect x="680" y="125" width="{'87' if is_rust else '23'}" height="12" rx="4" fill="#ef4444"/>
            
            <text x="630" y="170" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="700">G: {'28%' if is_rust else '78%'}</text>
            <rect x="680" y="160" width="95" height="12" rx="4" fill="#1e293b"/>
            <rect x="680" y="160" width="{'26' if is_rust else '74'}" height="12" rx="4" fill="#10b981"/>
            
            <text x="630" y="205" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="700">B: {'19%' if is_rust else '81%'}</text>
            <rect x="680" y="195" width="95" height="12" rx="4" fill="#1e293b"/>
            <rect x="680" y="195" width="{'18' if is_rust else '77'}" height="12" rx="4" fill="#38bdf8"/>
            
            <text x="700" y="250" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700" text-anchor="middle">TEXTURE VARIANCE</text>
            <text x="700" y="275" fill="{hue_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="15" font-weight="800" text-anchor="middle">{'σ² = 48.2 (PITTING)' if is_rust else 'σ² = 1.4 (SMOOTH)'}</text>
        </svg>"""

    elif node_id == "hyp":
        alert_badge = """
        <rect x="520" y="24" width="250" height="36" rx="8" fill="#450a0a" stroke="#ef4444" stroke-width="1.5"/>
        <text x="645" y="46" fill="#fca5a5" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">🔴 ACTIVE Fe₂O₃ OXIDATION DETECTED</text>
        """ if is_rust else """
        <rect x="520" y="24" width="250" height="36" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
        <text x="645" y="46" fill="#6ee7b7" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">🟢 NIR SPECTRUM CLEAN: NO RUST PEAK</text>
        """
        dip_path = "M 220 220 Q 320 215 380 280 T 480 200 T 600 210" if is_rust else "M 220 220 Q 320 215 420 210 T 520 215 T 600 210"
        peak_text = "Fe₂O₃ ABSORPTION DIP @ 850nm" if is_rust else "NO ABSORPTION DIP (CLEAR EPOXY)"
        peak_col = "#ef4444" if is_rust else "#10b981"
        return f"""<svg width="100%" height="100%" viewBox="0 0 840 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="hypGrid" width="30" height="30" patternUnits="userSpaceOnUse">
                    <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" stroke-width="0.8"/>
                </pattern>
                <linearGradient id="spectrumRainbow" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#ef4444"/>
                    <stop offset="30%" stop-color="#f59e0b"/>
                    <stop offset="60%" stop-color="#10b981"/>
                    <stop offset="100%" stop-color="#38bdf8"/>
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="#030712"/>
            <rect width="100%" height="100%" fill="url(#hypGrid)"/>
            
            {alert_badge}
            
            <!-- Spectral Band Ribbon -->
            <rect x="220" y="70" width="380" height="14" rx="4" fill="url(#spectrumRainbow)"/>
            <text x="220" y="62" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700">850 nm (NIR)</text>
            <text x="600" y="62" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="end">1650 nm (SWIR)</text>
            
            <!-- Spectrum Oscillogram Chart Frame -->
            <rect x="200" y="95" width="420" height="210" rx="10" fill="#090d16" stroke="#334155" stroke-width="1.5"/>
            
            <!-- Axis lines -->
            <line x1="240" y1="120" x2="240" y2="280" stroke="#334155" stroke-width="1.2"/>
            <line x1="240" y1="280" x2="590" y2="280" stroke="#334155" stroke-width="1.2"/>
            <text x="235" y="130" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700" text-anchor="end">1.0</text>
            <text x="235" y="200" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700" text-anchor="end">0.5</text>
            <text x="235" y="275" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700" text-anchor="end">0.0</text>
            <text x="240" y="295" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700">850nm</text>
            <text x="410" y="295" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700">1250nm</text>
            <text x="580" y="295" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700">1650nm</text>
            
            <!-- Spectral Waveform Curve -->
            <path d="{dip_path}" fill="none" stroke="{peak_col}" stroke-width="3"/>
            
            <!-- Highlight Reticle on 850nm absorption dip -->
            <circle cx="380" cy="{'280' if is_rust else '212'}" r="6" fill="{peak_col}"/>
            <line x1="380" y1="110" x2="380" y2="280" stroke="{peak_col}" stroke-width="1.2" stroke-dasharray="3 3"/>
            <text x="380" y="125" fill="{peak_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="800" text-anchor="middle">{peak_text}</text>
            
            <!-- Telemetry Cards Left -->
            <rect x="35" y="95" width="150" height="60" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="110" y="117" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">SPECTRAL BANDS</text>
            <text x="110" y="140" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="16" font-weight="800" text-anchor="middle">128 Channels</text>
            
            <rect x="35" y="170" width="150" height="60" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#10b981" stroke-width="1.5"/>
            <text x="110" y="192" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">BAND RESOLUTION</text>
            <text x="110" y="215" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="16" font-weight="800" text-anchor="middle">5.2 nm / px</text>
            
            <rect x="35" y="245" width="150" height="60" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="{peak_col}" stroke-width="1.5"/>
            <text x="110" y="267" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">OXIDATION DETECT</text>
            <text x="110" y="290" fill="{peak_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">{'POSITIVE (Fe₂O₃)' if is_rust else 'NEGATIVE (CLEAN)'}</text>
            
            <!-- Telemetry Cards Right -->
            <rect x="640" y="95" width="165" height="210" rx="10" fill="rgba(15, 23, 42, 0.9)" stroke="#334155" stroke-width="1.5"/>
            <text x="722" y="122" fill="#f8fafc" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">CHEMICAL SIGNATURE</text>
            <text x="655" y="152" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">COMPOUND:</text>
            <text x="655" y="170" fill="{peak_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="12.5" font-weight="800">{'Iron(III) Oxide · Rust' if is_rust else 'Epoxy Polymer Intact'}</text>
            
            <text x="655" y="200" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">ABSORPTION DEPTH:</text>
            <text x="655" y="218" fill="{peak_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">{'0.74 AU (HIGH)' if is_rust else '0.02 AU (CLEAR)'}</text>
            
            <text x="655" y="248" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">CLASSIFICATION CONF:</text>
            <text x="655" y="266" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">99.4% Match</text>
        </svg>"""

    elif node_id == "sac":
        alert_badge = """
        <rect x="500" y="24" width="280" height="36" rx="8" fill="#450a0a" stroke="#ef4444" stroke-width="1.5"/>
        <text x="640" y="46" fill="#fca5a5" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">⚠️ MESH DELTA: 4.8 m² RUST AREA DETECTED</text>
        """ if is_rust else """
        <rect x="500" y="24" width="280" height="36" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
        <text x="640" y="46" fill="#6ee7b7" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">🟢 SURFACE AREA IN FULL CAD EQUILIBRIUM</text>
        """
        mesh_col = "#ef4444" if is_rust else "#059669"
        delta_val = "+4.8 m² DEGRADED" if is_rust else "0.0 m² (Δ = 0%)"
        delta_col = "#ef4444" if is_rust else "#10b981"
        return f"""<svg width="100%" height="100%" viewBox="0 0 840 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="sacGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.8"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="#030712"/>
            <rect width="100%" height="100%" fill="url(#sacGrid)"/>
            
            {alert_badge}
            
            <!-- Delaunay Finite Element Triangulation Mesh Wireframe -->
            <g stroke="{mesh_col}" stroke-width="1.5" fill="none" opacity="0.85">
                <polygon points="250,110 320,150 280,220"/>
                <polygon points="320,150 400,120 420,190"/>
                <polygon points="280,220 320,150 420,190"/>
                <polygon points="280,220 350,280 420,190"/>
                <polygon points="400,120 490,130 420,190"/>
                <polygon points="490,130 540,190 420,190"/>
                <polygon points="420,190 540,190 480,270"/>
                <polygon points="350,280 420,190 480,270"/>
                <polygon points="480,270 560,260 540,190"/>
                <polygon points="250,110 320,150 400,120"/>
            </g>
            <!-- Vertex nodes -->
            <g fill="#38bdf8">
                <circle cx="250" cy="110" r="4"/><circle cx="320" cy="150" r="4"/><circle cx="400" cy="120" r="4"/>
                <circle cx="490" cy="130" r="4"/><circle cx="540" cy="190" r="4"/><circle cx="280" cy="220" r="4"/>
                <circle cx="420" cy="190" r="5" fill="{mesh_col}"/><circle cx="350" cy="280" r="4"/>
                <circle cx="480" cy="270" r="4"/><circle cx="560" cy="260" r="4"/>
            </g>
            
            <text x="390" y="80" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">DELAUNAY FINITE-ELEMENT TRIANGULATION ENGINE</text>
            
            <!-- Integration Formula Callout -->
            <rect x="290" y="305" width="220" height="40" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#10b981" stroke-width="1.2"/>
            <text x="400" y="330" fill="#a7f3d0" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">Surface Area A = ∬ √(1 + (∂z/∂x)² + (∂z/∂y)²) dA</text>
            
            <!-- Telemetry Cards Left -->
            <rect x="40" y="90" width="170" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="125" y="113" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">MESH VERTICES</text>
            <text x="125" y="138" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="16" font-weight="800" text-anchor="middle">42,850 Vertices</text>
            
            <rect x="40" y="170" width="170" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#10b981" stroke-width="1.5"/>
            <text x="125" y="193" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">COMPUTATION LATENCY</text>
            <text x="125" y="218" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="16" font-weight="800" text-anchor="middle">&lt; 140 ms</text>
            
            <rect x="40" y="250" width="170" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="{delta_col}" stroke-width="1.5"/>
            <text x="125" y="273" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">DELTA SURFACE AREA</text>
            <text x="125" y="298" fill="{delta_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800" text-anchor="middle">{delta_val}</text>
            
            <!-- Telemetry Cards Right -->
            <rect x="610" y="90" width="190" height="225" rx="10" fill="rgba(15, 23, 42, 0.9)" stroke="#334155" stroke-width="1.5"/>
            <text x="705" y="115" fill="#f8fafc" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">GEOMETRIC PROFILING</text>
            <text x="630" y="145" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">TRIANGULAR FACETS:</text>
            <text x="630" y="165" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="14" font-weight="800">85,210 Polygons</text>
            
            <text x="630" y="195" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">BASELINE CALIBRATION:</text>
            <text x="630" y="215" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">MSC-TNK-B3 Scantling</text>
            
            <text x="630" y="245" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">OUTPUT DESTINATION:</text>
            <text x="630" y="265" fill="#a855f7" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800">VTL &amp; Digital Twin (DT)</text>
        </svg>"""

    elif node_id == "vtl":
        alert_badge = """
        <rect x="500" y="24" width="280" height="36" rx="8" fill="#450a0a" stroke="#ef4444" stroke-width="1.5"/>
        <text x="640" y="46" fill="#fca5a5" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">⚠️ REMAINING STEEL: 16.2mm (-1.8mm DELTA)</text>
        """ if is_rust else """
        <rect x="500" y="24" width="280" height="36" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
        <text x="640" y="46" fill="#6ee7b7" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">🟢 100% CLASS COMPLIANT: 18.0mm STEEL</text>
        """
        scant_val = "16.2 mm (-1.8mm loss)" if is_rust else "18.0 mm (nominal)"
        scant_col = "#ef4444" if is_rust else "#10b981"
        return f"""<svg width="100%" height="100%" viewBox="0 0 840 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="vtlGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.8"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="#030712"/>
            <rect width="100%" height="100%" fill="url(#vtlGrid)"/>
            
            {alert_badge}
            
            <!-- Naval Blueprint Vessel Scantling Cross-Section -->
            <rect x="230" y="80" width="350" height="230" rx="10" fill="#061224" stroke="#1e3a8a" stroke-width="2"/>
            <text x="245" y="105" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800">DNV-GL SCANTLING PLAN · FRAME 38 PORT BULKHEAD</text>
            
            <!-- Steel Plate Tolerance Ruler -->
            <rect x="260" y="130" width="290" height="40" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1.5"/>
            <rect x="260" y="130" width="{'205' if is_rust else '255'}" height="40" rx="6" fill="{'#ea580c' if is_rust else '#059669'}" opacity="0.65"/>
            
            <!-- Steel Thickness Measurements -->
            <text x="270" y="155" fill="#ffffff" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800">PLATE THICKNESS: {scant_val}</text>
            
            <!-- Minimum Class Renewal Limit Line -->
            <line x1="430" y1="120" x2="430" y2="180" stroke="#ef4444" stroke-width="2" stroke-dasharray="3 3"/>
            <text x="435" y="195" fill="#f87171" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="800">RENEWAL MIN: 14.5 mm</text>
            
            <!-- Scantling Table Records -->
            <g fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5">
                <text x="260" y="230">CLASS REGISTRY:</text> <text x="400" y="230" fill="#f8fafc" font-weight="700">DNV-GL 100 A5 CONTAINER SHIP</text>
                <text x="260" y="255">STEEL GRADE:</text> <text x="400" y="255" fill="#f8fafc" font-weight="700">NV DH36 HIGH-STRENGTH MARITIME STEEL</text>
                <text x="260" y="280">COATING SYSTEM:</text> <text x="400" y="280" fill="#f8fafc" font-weight="700">EPOXY 320μm DFT (2-COAT NOMINAL)</text>
            </g>
            
            <!-- Telemetry Cards Left -->
            <rect x="35" y="80" width="165" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="117" y="103" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">RECORD DATABASE</text>
            <text x="117" y="128" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="15" font-weight="800" text-anchor="middle">VTL Cloud SQL</text>
            
            <rect x="35" y="160" width="165" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="{scant_col}" stroke-width="1.5"/>
            <text x="117" y="183" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">MARGIN ABOVE MINIMUM</text>
            <text x="117" y="208" fill="{scant_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="15" font-weight="800" text-anchor="middle">{'+1.7 mm (ALERT)' if is_rust else '+3.5 mm (SAFE)'}</text>
            
            <rect x="35" y="240" width="165" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#10b981" stroke-width="1.5"/>
            <text x="117" y="263" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">TWIN SYNCHRONIZATION</text>
            <text x="117" y="288" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="14" font-weight="800" text-anchor="middle">LIVE CAD LINK</text>
            
            <!-- Telemetry Cards Right -->
            <rect x="610" y="80" width="190" height="230" rx="10" fill="rgba(15, 23, 42, 0.9)" stroke="#334155" stroke-width="1.5"/>
            <text x="705" y="105" fill="#f8fafc" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">TECHNICAL LIBRARY</text>
            <text x="630" y="135" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">COMPLIANCE CODE:</text>
            <text x="630" y="155" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">IACS UR S11A</text>
            
            <text x="630" y="185" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">INSPECTION CADENCE:</text>
            <text x="630" y="205" fill="#f8fafc" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">Continuous + 5-Yr Survey</text>
            
            <text x="630" y="235" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">CLASS RECOMMENDATION:</text>
            <text x="630" y="255" fill="{scant_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="11.5" font-weight="800">{'Drydock Coating Repair' if is_rust else 'Maintain Normal Cadence'}</text>
        </svg>"""

    elif node_id == "samm":
        alert_badge = """
        <rect x="500" y="24" width="290" height="36" rx="8" fill="#450a0a" stroke="#ef4444" stroke-width="1.5"/>
        <text x="645" y="46" fill="#fca5a5" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">🔴 WORK ORDER DISPATCHED: WP-2026-B3</text>
        """ if is_rust else """
        <rect x="500" y="24" width="290" height="36" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
        <text x="645" y="46" fill="#6ee7b7" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">🟢 FLEET CBM: NO DRY-DOCK WORK ORDERS</text>
        """
        wo_status = "URGENT DISPATCH" if is_rust else "NONE PENDING"
        wo_col = "#ef4444" if is_rust else "#10b981"
        return f"""<svg width="100%" height="100%" viewBox="0 0 840 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="sammGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.8"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="#030712"/>
            <rect width="100%" height="100%" fill="url(#sammGrid)"/>
            
            {alert_badge}
            
            <!-- Decision Logic & Work Order Engine Flowchart -->
            <rect x="230" y="80" width="350" height="230" rx="10" fill="#090d16" stroke="#8b5cf6" stroke-width="2"/>
            <text x="405" y="105" fill="#c084fc" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">CONDITION-BASED MAINTENANCE (CBM) DECISION ENGINE</text>
            
            <!-- Workflow Steps in SAMM -->
            <g transform="translate(250, 120)">
                <rect width="130" height="40" rx="6" fill="#1e1b4b" stroke="#8b5cf6" stroke-width="1.5"/>
                <text x="65" y="24" fill="#e9d5ff" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">1. INGEST TWIN DELTA</text>
                
                <line x1="130" y1="20" x2="170" y2="20" stroke="#8b5cf6" stroke-width="2"/>
                
                <rect x="170" y="0" width="130" height="40" rx="6" fill="#1e1b4b" stroke="#8b5cf6" stroke-width="1.5"/>
                <text x="235" y="24" fill="#e9d5ff" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">2. COST-RISK EVAL</text>
                
                <line x1="235" y1="40" x2="235" y2="75" stroke="#8b5cf6" stroke-width="2"/>
                
                <rect x="170" y="75" width="130" height="40" rx="6" fill="{'#450a0a' if is_rust else '#064e3b'}" stroke="{wo_col}" stroke-width="1.8"/>
                <text x="235" y="98" fill="{wo_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">3. WORK ORDER</text>
                
                <line x1="170" y1="95" x2="130" y2="95" stroke="#8b5cf6" stroke-width="2"/>
                
                <rect x="0" y="75" width="130" height="40" rx="6" fill="#1e1b4b" stroke="#8b5cf6" stroke-width="1.5"/>
                <text x="65" y="98" fill="#e9d5ff" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">4. SHIP ACTION</text>
            </g>
            
            <text x="405" y="285" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="700" text-anchor="middle">OPTIMIZED FOR MINIMUM DRYDOCK TIME &amp; ZERO CLASS NON-CONFORMITY</text>
            
            <!-- Telemetry Cards Left -->
            <rect x="35" y="80" width="165" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#8b5cf6" stroke-width="1.5"/>
            <text x="117" y="103" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">POLICY REGIME</text>
            <text x="117" y="128" fill="#c084fc" font-family="'Barlow Semi Condensed', sans-serif" font-size="14" font-weight="800" text-anchor="middle">Dynamic CBM</text>
            
            <rect x="35" y="160" width="165" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="{wo_col}" stroke-width="1.5"/>
            <text x="117" y="183" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">DISPATCH STATUS</text>
            <text x="117" y="208" fill="{wo_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800" text-anchor="middle">{wo_status}</text>
            
            <rect x="35" y="240" width="165" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#10b981" stroke-width="1.5"/>
            <text x="117" y="263" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">VESSEL AVAILABILITY</text>
            <text x="117" y="288" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="15" font-weight="800" text-anchor="middle">{'94.2%' if is_rust else '99.8%'}</text>
            
            <!-- Telemetry Cards Right -->
            <rect x="610" y="80" width="190" height="230" rx="10" fill="rgba(15, 23, 42, 0.9)" stroke="#334155" stroke-width="1.5"/>
            <text x="705" y="105" fill="#f8fafc" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">WORK ORDER SPECS</text>
            <text x="630" y="135" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">TARGET ASSET:</text>
            <text x="630" y="155" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">Ballast Tank B-3 Port</text>
            
            <text x="630" y="185" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">ACTION TYPE:</text>
            <text x="630" y="205" fill="{wo_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800">{'Spot Hydroblast &amp; Recoat' if is_rust else 'Routine Bi-Monthly Audit'}</text>
            
            <text x="630" y="235" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">EST. REPAIR TIME:</text>
            <text x="630" y="255" fill="#f8fafc" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">{'18 Hours in Port' if is_rust else 'Zero Downtime'}</text>
        </svg>"""

    elif node_id == "cms":
        alert_badge = """
        <rect x="500" y="24" width="290" height="36" rx="8" fill="#450a0a" stroke="#ef4444" stroke-width="1.5"/>
        <text x="645" y="46" fill="#fca5a5" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">⚠️ RUL DROP: ACCELERATED DECAY PREDICTED</text>
        """ if is_rust else """
        <rect x="500" y="24" width="290" height="36" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
        <text x="645" y="46" fill="#6ee7b7" font-family="'Barlow Semi Condensed', sans-serif" font-size="11" font-weight="800" text-anchor="middle">🟢 FLEET CORROSION INDEX: EXCELLENT (98/100)</text>
        """
        rul_val = "2.1 YEARS (CRITICAL)" if is_rust else "8.4 YEARS (NOMINAL)"
        rul_col = "#ef4444" if is_rust else "#10b981"
        curve_path = "M 250 140 Q 350 150 420 220 T 560 270" if is_rust else "M 250 140 Q 380 160 480 180 T 560 200"
        return f"""<svg width="100%" height="100%" viewBox="0 0 840 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="cmsGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.8"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="#030712"/>
            <rect width="100%" height="100%" fill="url(#cmsGrid)"/>
            
            {alert_badge}
            
            <!-- Predictive Degradation & RUL Forecast Curve Chart -->
            <rect x="230" y="80" width="350" height="230" rx="10" fill="#090d16" stroke="#059669" stroke-width="2"/>
            <text x="405" y="105" fill="#34d399" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">REMAINING USEFUL LIFE (RUL) WEIBULL PROJECTION</text>
            
            <!-- Chart axes -->
            <line x1="250" y1="120" x2="250" y2="280" stroke="#334155" stroke-width="1.2"/>
            <line x1="250" y1="280" x2="560" y2="280" stroke="#334155" stroke-width="1.2"/>
            <text x="245" y="130" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700" text-anchor="end">100%</text>
            <text x="245" y="200" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700" text-anchor="end">50%</text>
            <text x="245" y="275" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700" text-anchor="end">0%</text>
            <text x="250" y="295" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700">Year 0</text>
            <text x="400" y="295" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700">Year 5</text>
            <text x="540" y="295" fill="#64748b" font-family="'Barlow Semi Condensed', sans-serif" font-size="9" font-weight="700">Year 10</text>
            
            <!-- Degradation Curve -->
            <path d="{curve_path}" fill="none" stroke="{rul_col}" stroke-width="3"/>
            
            <!-- Renewal Limit Threshold -->
            <line x1="250" y1="240" x2="560" y2="240" stroke="#ef4444" stroke-width="1" stroke-dasharray="3 3"/>
            <text x="560" y="235" fill="#f87171" font-family="'Barlow Semi Condensed', sans-serif" font-size="8.5" font-weight="700" text-anchor="end">MIN THRESHOLD</text>
            
            <!-- Telemetry Cards Left -->
            <rect x="35" y="80" width="165" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#10b981" stroke-width="1.5"/>
            <text x="117" y="103" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">FLEET ANALYTICS</text>
            <text x="117" y="128" fill="#34d399" font-family="'Barlow Semi Condensed', sans-serif" font-size="14" font-weight="800" text-anchor="middle">HMS Live Dashboard</text>
            
            <rect x="35" y="160" width="165" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="{rul_col}" stroke-width="1.5"/>
            <text x="117" y="183" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">PREDICTED RUL</text>
            <text x="117" y="208" fill="{rul_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">{rul_val}</text>
            
            <rect x="35" y="240" width="165" height="65" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="117" y="263" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10" font-weight="700" text-anchor="middle">ANODIC PROTECTION</text>
            <text x="117" y="288" fill="#38bdf8" font-family="'Barlow Semi Condensed', sans-serif" font-size="14" font-weight="800" text-anchor="middle">-850 mV (POLARIZED)</text>
            
            <!-- Telemetry Cards Right -->
            <rect x="610" y="80" width="190" height="230" rx="10" fill="rgba(15, 23, 42, 0.9)" stroke="#334155" stroke-width="1.5"/>
            <text x="705" y="105" fill="#f8fafc" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" text-anchor="middle">AWARENESS TELEMETRY</text>
            <text x="630" y="135" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">CORROSION RATE:</text>
            <text x="630" y="155" fill="{rul_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">{'0.38 mm/yr (HIGH)' if is_rust else '0.04 mm/yr (LOW)'}</text>
            
            <text x="630" y="185" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">FLEET CORROSION INDEX:</text>
            <text x="630" y="205" fill="{rul_col}" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">{'Grade C (Action Needed)' if is_rust else 'Grade A+ (Optimal)'}</text>
            
            <text x="630" y="235" fill="#94a3b8" font-family="'Barlow Semi Condensed', sans-serif" font-size="10.5" font-weight="700">ENTERPRISE API SYNC:</text>
            <text x="630" y="255" fill="#10b981" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800">SAP PM / DNV Veracity</text>
        </svg>"""

    return ""

def encode_svg_to_data_uri(svg_code: str) -> str:
    """Encode SVG string to base64 Data URI."""
    encoded = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


def render_image_slot(node_id: str, meta: Dict[str, Any]) -> html.Div:
    """Render a clean, focused technical specification and telemetry panel for active nodes."""
    title_display = meta.get('title') or ('LRMS' if node_id == 'samm' else 'HMS' if node_id == 'cms' else node_id.upper())
    desc_display = meta.get('desc') or "Active component in digital twin architecture."
    outputs = meta.get('gives', [])

    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center",
            "backgroundColor": "#020617",
            "padding": "32px 24px",
            "width": "100%",
            "minHeight": "480px",
            "overflow": "hidden",
        },
        children=[
            html.Div(
                style={
                    "border": "1.5px solid #334155",
                    "borderRadius": "16px",
                    "padding": "36px 32px",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "18px",
                    "backgroundColor": "#0b1120",
                    "maxWidth": "780px",
                    "width": "100%",
                    "boxShadow": "0 10px 30px rgba(0,0,0,0.5)",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "borderBottom": "1px solid #1e293b", "paddingBottom": "14px"},
                        children=[
                            html.Div(
                                children=[
                                    html.Span("DIGITAL TWIN TELEMETRY COMPONENT", style={"fontSize": "11px", "fontWeight": "800", "color": "#38bdf8", "letterSpacing": "1px", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                                    html.H3(title_display, style={"fontSize": "22px", "fontWeight": "800", "color": "#f8fafc", "margin": "2px 0 0 0", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                                ],
                            ),
                            html.Span("🟢 COMPONENT ONLINE", style={"fontSize": "11px", "fontWeight": "800", "color": "#34d399", "backgroundColor": "#064e3b", "padding": "4px 10px", "borderRadius": "6px", "border": "1px solid #10b981"}),
                        ],
                    ),
                    html.P(desc_display, style={"fontSize": "13.5px", "color": "#cbd5e1", "lineHeight": "1.5", "margin": "0"}),
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                        children=[
                            html.Span("OUTPUT DATA FEEDS & PIPELINE INTERFACES", style={"fontSize": "10.5px", "fontWeight": "800", "color": "#94a3b8", "letterSpacing": "0.8px", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                            html.Div(
                                style={"display": "flex", "flexWrap": "wrap", "gap": "8px"},
                                children=[
                                    html.Span(g, style={"fontSize": "11.5px", "fontWeight": "700", "color": "#38bdf8", "backgroundColor": "#0f172a", "padding": "5px 12px", "borderRadius": "6px", "border": "1px solid #1e293b"})
                                    for g in outputs
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "borderTop": "1px solid #1e293b", "paddingTop": "12px", "fontSize": "11.5px", "color": "#64748b"},
                        children=[
                            html.Span("Interface: REST / WebSocket Event Bus"),
                            html.Span("Status: Synchronized with Digital Twin", style={"color": "#34d399", "fontWeight": "700"}),
                        ],
                    ),
                ],
            ),
        ],
    )


def render_custom_or_slot(node_id: str, meta: Dict[str, Any], user_dropped: Optional[Dict[str, str]] = None) -> html.Div:
    """Render purely the inspection image if configured, or a clean slot if waiting for an image."""
    user_dropped = user_dropped or {}
    custom_img = user_dropped.get(node_id)
    if not custom_img:
        if node_id == "hyp":
            custom_img = IMAGE_DATA.get("hyperspectral_cubert") or IMAGE_DATA.get("hyp")
        elif node_id in ("twin", "dt"):
            custom_img = IMAGE_DATA.get("dt_clean")
        elif node_id == "tank":
            custom_img = IMAGE_DATA.get("clean")
        else:
            custom_img = IMAGE_DATA.get(node_id)
    if custom_img:
        return html.Div(
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "backgroundColor": "#020617",
                "padding": "24px",
                "width": "100%",
                "minHeight": "450px",
                "overflow": "hidden",
            },
            children=[
                html.Img(
                    src=custom_img,
                    alt=f"{node_id.upper()} Sensor Capture",
                    style={
                        "maxWidth": "100%",
                        "maxHeight": "calc(88vh - 130px)",
                        "width": "auto",
                        "height": "auto",
                        "objectFit": "contain",
                        "borderRadius": "12px",
                        "boxShadow": "0 12px 40px rgba(0, 0, 0, 0.8)",
                        "border": "1.5px solid #1e293b",
                        "display": "block",
                    },
                ),
            ],
        )
    return render_image_slot(node_id, meta)


def build_placeholder_dialog(node_id: str, is_rust: bool = False, user_dropped: Optional[Dict[str, str]] = None) -> html.Div:
    meta = NODE_MODAL_METADATA.get(node_id, {})
    return render_custom_or_slot(node_id, meta, user_dropped)
    svg_code = get_placeholder_svg(node_id, is_rust)
    svg_uri = encode_svg_to_data_uri(svg_code)

    telemetry = details.get("telemetry_rust" if is_rust else "telemetry_nominal", [])
    specs = details.get("specs", [])
    pipeline = details.get("pipeline", [])

    border_col = "#ef4444" if is_rust else "#38bdf8"

    # When a real image/picture is provided for the sensor, show NOTHING BUT THE IMAGE
    custom_img = IMAGE_DATA.get("hyperspectral_cubert") if node_id == "hyp" else IMAGE_DATA.get(node_id)
    if custom_img:
        return html.Div(
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "backgroundColor": "#020617",
                "padding": "24px",
                "width": "100%",
                "minHeight": "450px",
                "overflow": "hidden",
            },
            children=[
                html.Img(
                    src=custom_img,
                    alt=f"{node_id.upper()} Sensor Capture",
                    style={
                        "maxWidth": "100%",
                        "maxHeight": "calc(88vh - 130px)",
                        "width": "auto",
                        "height": "auto",
                        "objectFit": "contain",
                        "borderRadius": "12px",
                        "boxShadow": "0 12px 40px rgba(0, 0, 0, 0.8)",
                        "border": "1.5px solid #1e293b",
                        "display": "block",
                    },
                ),
            ],
        )

    return html.Div(
        style={"display": "flex", "flexDirection": "column", "width": "100%", "overflow": "hidden"},
        children=[
            # Simulation Control Bar
            html.Div(
                style={
                    "backgroundColor": "#1e293b",
                    "padding": "12px 24px",
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "borderBottom": "1px solid #334155",
                    "flexWrap": "wrap",
                    "gap": "12px",
                },
                children=[
                    html.Div(
                        children=[
                            html.Span(
                                f"{node_id.upper()} TELEMETRY & SYSTEM CONDITION: ",
                                style={
                                    "fontSize": "11.5px",
                                    "fontWeight": "800",
                                    "letterSpacing": "1px",
                                    "color": "#94a3b8",
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                },
                            ),
                            html.Span(
                                "Live sensor telemetry reflects nominal baseline state."
                                if not is_rust else
                                "Defect state active on physical ship. System telemetry reflects live defect feedback loop.",
                                style={"fontSize": "12.5px", "color": "#cbd5e1"},
                            ),
                        ]
                    ),
                    html.Div(
                        style={"display": "flex", "gap": "10px"},
                        children=[
                            html.Button(
                                "⚠️ Trigger Rust Defect",
                                id={"type": "panel-sim-rust-btn", "index": 1},
                                n_clicks=0,
                                style={
                                    "minHeight": "40px",
                                    "padding": "8px 20px",
                                    "borderRadius": "8px",
                                    "border": "2px solid #ef4444",
                                    "backgroundColor": "#ef4444" if is_rust else "#0f172a",
                                    "color": "#ffffff" if is_rust else "#f87171",
                                    "fontSize": "13.5px",
                                    "fontWeight": "800",
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "cursor": "pointer",
                                    "boxShadow": "0 0 14px rgba(239, 68, 68, 0.45)" if is_rust else "none",
                                },
                            ),
                            html.Button(
                                "🟢 Nominal Baseline",
                                id={"type": "panel-sim-clean-btn", "index": 1},
                                n_clicks=0,
                                style={
                                    "minHeight": "40px",
                                    "padding": "8px 20px",
                                    "borderRadius": "8px",
                                    "border": "2px solid #10b981",
                                    "backgroundColor": "#10b981" if not is_rust else "#0f172a",
                                    "color": "#ffffff" if not is_rust else "#34d399",
                                    "fontSize": "13.5px",
                                    "fontWeight": "800",
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "cursor": "pointer",
                                    "boxShadow": "0 0 14px rgba(16, 185, 129, 0.45)" if not is_rust else "none",
                                },
                            ),
                        ],
                    ),
                ],
            ),

            # Scrollable Body Viewport
            html.Div(
                style={"backgroundColor": "#020617", "padding": "20px 24px", "display": "flex", "flexDirection": "column", "gap": "16px", "overflowY": "auto", "maxHeight": "calc(90vh - 160px)"},
                children=[
                    # Blueprint Graphic Card
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "backgroundColor": "#0f172a",
                            "borderRadius": "14px",
                            "border": f"2px solid {border_col}",
                            "overflow": "hidden",
                        },
                        children=[
                            html.Img(
                                src=IMAGE_DATA.get("hyperspectral_cubert") if (node_id == "hyp" and IMAGE_DATA.get("hyperspectral_cubert")) else svg_uri,
                                alt="Cubert Hyperspectral Real-Time Capture" if node_id == "hyp" else f"{node_id.upper()} Engineering Blueprint Graphic",
                                style={"width": "100%", "height": "440px", "objectFit": "contain", "display": "block", "backgroundColor": "#181818" if node_id == "hyp" else "#030712"},
                            ),
                        ],
                    ),

                    # 3-Column Engineering Detail Grid
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))", "gap": "14px"},
                        children=[
                            # Col 1: Hardware Specifications
                            html.Div(
                                style={"backgroundColor": "#0f172a", "borderRadius": "12px", "padding": "16px", "border": "1.5px solid #1e293b", "display": "flex", "flexDirection": "column", "gap": "8px"},
                                children=[
                                    html.Span("⚙️ HARDWARE & ENGINE SPECIFICATIONS", style={"fontSize": "11.5px", "fontWeight": "800", "color": "#38bdf8", "letterSpacing": "0.8px"}),
                                    html.Div(
                                        style={"display": "flex", "flexDirection": "column", "gap": "6px", "marginTop": "4px"},
                                        children=[
                                            html.Div(style={"display": "flex", "justifyContent": "space-between", "fontSize": "12px"}, children=[html.Span(k, style={"color": "#94a3b8", "fontWeight": "700"}), html.Span(v, style={"color": "#f8fafc", "fontWeight": "700"})])
                                            for k, v in specs
                                        ]
                                    ),
                                ]
                            ),

                            # Col 2: Live Telemetry Metrics
                            html.Div(
                                style={"backgroundColor": "#0f172a", "borderRadius": "12px", "padding": "16px", "border": f"1.5px solid {'#ef4444' if is_rust else '#10b981'}", "display": "flex", "flexDirection": "column", "gap": "8px"},
                                children=[
                                    html.Span("📡 REAL-TIME TELEMETRY STREAM", style={"fontSize": "11.5px", "fontWeight": "800", "color": "#f87171" if is_rust else "#34d399", "letterSpacing": "0.8px"}),
                                    html.Div(
                                        style={"display": "flex", "flexDirection": "column", "gap": "6px", "marginTop": "4px"},
                                        children=[
                                            html.Div(style={"display": "flex", "justifyContent": "space-between", "fontSize": "12px"}, children=[html.Span(k, style={"color": "#94a3b8", "fontWeight": "700"}), html.Span(v, style={"color": "#f87171" if is_rust and ('⚠️' in v or '🔴' in v) else '#38bdf8' if ('mm' in v or 'Vertices' in v) else '#10b981', "fontWeight": "800"})])
                                            for k, v in telemetry
                                        ]
                                    ),
                                ]
                            ),

                            # Col 3: Pipeline Links
                            html.Div(
                                style={"backgroundColor": "#0f172a", "borderRadius": "12px", "padding": "16px", "border": "1.5px solid #1e293b", "display": "flex", "flexDirection": "column", "gap": "8px"},
                                children=[
                                    html.Span("🔗 DIGITAL TWIN PIPELINE TOPOLOGY", style={"fontSize": "11.5px", "fontWeight": "800", "color": "#a855f7", "letterSpacing": "0.8px"}),
                                    html.Div(
                                        style={"display": "flex", "flexDirection": "column", "gap": "6px", "marginTop": "4px"},
                                        children=[
                                            html.Div(style={"display": "flex", "justifyContent": "space-between", "fontSize": "12px"}, children=[html.Span(k, style={"color": "#94a3b8", "fontWeight": "700"}), html.Span(v, style={"color": "#c084fc", "fontWeight": "700"})])
                                            for k, v in pipeline
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                ],
            ),

            # Footer
            html.Div(
                style={
                    "backgroundColor": "#0f172a",
                    "padding": "12px 24px",
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "borderTop": "1px solid #1e293b",
                    "fontSize": "11.5px",
                    "color": "#94a3b8",
                    "fontWeight": "600",
                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                },
                children=[
                    html.Span(f"DIGITAL TWIN PIPELINE COMPONENT: {meta.get('title', node_id.upper())}"),
                    html.Span("STATUS: CONNECTED & SYNCHRONIZED (<180ms)", style={"color": "#38bdf8", "fontWeight": "800"}),
                ],
            ),
        ],
    )


# =============================================================================
# MODAL BUILDER (SCREEN-COVERING POP-UP FOR BALLAST TANK & DIGITAL TWIN)
# =============================================================================

def build_modal_dialog(sc: str = "clean", phase: int = 3, target_node: str = "tank", user_dropped: Optional[Dict[str, str]] = None) -> html.Div:
    """Build the interior single-asset contents of the screen-covering inspector modal.
    When Ballast Tank is selected, it shows ONLY the Physical Ship Asset.
    When Digital Twin is selected, it shows ONLY the Virtual Digital Twin CAD Mesh.
    """
    is_rust = (sc == "rust")
    is_twin = (target_node == "twin")

    if is_twin:
        twin_img = IMAGE_DATA.get("dt_rust" if is_rust else "dt_clean") or get_digital_twin_svg_uri(sc)
        health_score = 42 if is_rust else 98
        health_color = "#ef4444" if is_rust else "#10b981"

        return html.Div(
            style={"display": "flex", "flexDirection": "column", "width": "100%", "overflow": "hidden"},
            children=[
                # Simulation Control Bar
                html.Div(
                    style={
                        "backgroundColor": "#1e293b",
                        "padding": "12px 24px",
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "borderBottom": "1px solid #334155",
                        "flexWrap": "wrap",
                        "gap": "12px",
                    },
                    children=[
                        html.Div(
                            children=[
                                html.Span(
                                    "DIGITAL TWIN TELEMETRY & CAD MESH MONITORING: ",
                                    style={
                                        "fontSize": "11.5px",
                                        "fontWeight": "800",
                                        "letterSpacing": "1px",
                                        "color": "#94a3b8",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    },
                                ),
                                html.Span(
                                    "Virtual CAD replica synchronized with the physical Ballast Tank. Continuous mesh profiling & delta detection."
                                    if not is_rust else
                                    "⚠️ Active rust defect detected on physical ship. CAD mesh reflects -1.8mm plate recess @ Frame 38.",
                                    style={"fontSize": "12.5px", "color": "#fca5a5" if is_rust else "#cbd5e1"},
                                ),
                            ]
                        ),
                        html.Div(
                            style={"display": "flex", "gap": "10px"},
                            children=[
                                html.Button(
                                    "⚠️ Trigger Rust Defect",
                                    id={"type": "panel-sim-rust-btn", "index": 1},
                                    n_clicks=0,
                                    style={
                                        "minHeight": "40px",
                                        "padding": "8px 20px",
                                        "borderRadius": "8px",
                                        "border": "2px solid #ef4444",
                                        "backgroundColor": "#ef4444" if is_rust else "#0f172a",
                                        "color": "#ffffff" if is_rust else "#f87171",
                                        "fontSize": "13.5px",
                                        "fontWeight": "800",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                        "cursor": "pointer",
                                        "boxShadow": "0 0 14px rgba(239, 68, 68, 0.45)" if is_rust else "none",
                                    },
                                ),
                                html.Button(
                                    "🟢 Nominal Baseline",
                                    id={"type": "panel-sim-clean-btn", "index": 1},
                                    n_clicks=0,
                                    style={
                                        "minHeight": "40px",
                                        "padding": "8px 20px",
                                        "borderRadius": "8px",
                                        "border": "2px solid #10b981",
                                        "backgroundColor": "#10b981" if not is_rust else "#0f172a",
                                        "color": "#ffffff" if not is_rust else "#34d399",
                                        "fontSize": "13.5px",
                                        "fontWeight": "800",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                        "cursor": "pointer",
                                        "boxShadow": "0 0 14px rgba(16, 185, 129, 0.45)" if not is_rust else "none",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),

                # Single Viewport: ONLY Digital Twin CAD Mesh Model
                html.Div(
                    style={"backgroundColor": "#020617", "padding": "20px 24px", "display": "flex", "flexDirection": "column", "gap": "14px", "overflowY": "auto", "maxHeight": "calc(90vh - 160px)"},
                    children=[
                        html.Div(
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "10px",
                                "backgroundColor": "#0f172a",
                                "borderRadius": "14px",
                                "padding": "16px",
                                "border": f"2px solid {'#ef4444' if is_rust else '#38bdf8'}",
                            },
                            children=[
                                html.Div(
                                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                                    children=[
                                        html.Span(
                                            "🌐 VIRTUAL ASSET: 3D DIGITAL TWIN CAD MESH REPLICA",
                                            style={
                                                "fontSize": "12px",
                                                "fontWeight": "800",
                                                "color": "#38bdf8",
                                                "letterSpacing": "1px",
                                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            },
                                        ),
                                        html.Span(
                                            "⚠️ RUST DEFECT DETECTED IN CAD MESH" if is_rust else "🟢 TWIN SYNCHRONIZED (NOMINAL)",
                                            style={
                                                "fontSize": "11.5px",
                                                "fontWeight": "800",
                                                "color": "#f87171" if is_rust else "#34d399",
                                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            },
                                        ),
                                    ],
                                ),
                                html.Div(
                                    style={
                                        "position": "relative",
                                        "height": "440px",
                                        "borderRadius": "10px",
                                        "overflow": "hidden",
                                        "backgroundColor": "#030712",
                                        "border": "1.5px solid #1e293b",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                    },
                                    children=[
                                        html.Img(
                                            src=twin_img,
                                            alt="Digital Twin 3D CAD Mesh Model",
                                            style={"width": "100%", "height": "100%", "objectFit": "contain", "display": "block"},
                                        ),
                                    ],
                                ),

                                # Health Score Gauge Card
                                html.Div(
                                    style={
                                        "backgroundColor": "#1e293b",
                                        "border": f"1.5px solid {health_color}",
                                        "borderRadius": "10px",
                                        "padding": "12px 18px",
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "gap": "6px",
                                    },
                                    children=[
                                        html.Div(
                                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "baseline"},
                                            children=[
                                                html.Span(
                                                    "TWIN STRUCTURAL INTEGRITY HEALTH SCORE",
                                                    style={"fontSize": "11.5px", "fontWeight": "800", "letterSpacing": "1px", "color": "#94a3b8", "fontFamily": "'Barlow Semi Condensed', sans-serif"},
                                                ),
                                                html.Span(
                                                    f"{health_score}% ({'CRITICAL DEGRADATION' if is_rust else 'NOMINAL INTEGRITY'})",
                                                    style={"fontSize": "15px", "fontWeight": "800", "color": health_color, "fontFamily": "'Barlow Semi Condensed', sans-serif"},
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            style={"width": "100%", "height": "8px", "backgroundColor": "#0f172a", "borderRadius": "4px", "overflow": "hidden"},
                                            children=[
                                                html.Div(style={"width": f"{health_score}%", "height": "100%", "backgroundColor": health_color, "borderRadius": "4px", "transition": "width 0.4s ease"}),
                                            ],
                                        ),
                                    ],
                                ),

                                # Physical Asset Navigation Bridge Card
                                html.Div(
                                    style={
                                        "backgroundColor": "#1e293b",
                                        "border": "1.5px solid #334155",
                                        "borderRadius": "10px",
                                        "padding": "12px 18px",
                                        "display": "flex",
                                        "justifyContent": "space-between",
                                        "alignItems": "center",
                                        "flexWrap": "wrap",
                                        "gap": "10px",
                                    },
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Span("PHYSICAL ASSET LINK: ", style={"fontSize": "11px", "fontWeight": "800", "color": "#94a3b8", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                                                html.Span("Real MSC Vessel Cargo Compartment B-3", style={"fontSize": "13px", "fontWeight": "700", "color": "#ffffff"}),
                                                html.Div(
                                                    "🔴 Physical rust defect active on ship bulkhead" if is_rust else "🟢 Physical ship bulkhead nominal (18.0mm steel)",
                                                    style={"fontSize": "12px", "color": "#f87171" if is_rust else "#34d399", "fontWeight": "600", "marginTop": "2px"}
                                                ),
                                            ]
                                        ),
                                        html.Button(
                                            "⚓ View Physical Ballast Tank →",
                                            id={"type": "open-modal-btn", "index": "tank"},
                                            n_clicks=0,
                                            style={
                                                "backgroundColor": "#0284c7",
                                                "color": "#ffffff",
                                                "border": "none",
                                                "borderRadius": "8px",
                                                "padding": "9px 20px",
                                                "fontSize": "13px",
                                                "fontWeight": "800",
                                                "cursor": "pointer",
                                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            }
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                ),

                # Footer
                html.Div(
                    style={
                        "backgroundColor": "#0f172a",
                        "padding": "12px 24px",
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "borderTop": "1px solid #1e293b",
                        "fontSize": "11.5px",
                        "color": "#94a3b8",
                        "fontWeight": "600",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                    },
                    children=[
                        html.Span("CAD MODEL: MSC-TNK-B3-V2.1 · 42,850 Vertices · Surface Area Library (SAC) Delta Detection"),
                        html.Span("PHYSICAL BALLAST TANK LINK: SYNCHRONIZED (<180ms)", style={"color": "#38bdf8", "fontWeight": "800"}),
                    ],
                ),
            ],
        )

    elif target_node == "tank":
        # Ballast Tank: ONLY Physical Asset (The Ship / Ballast Tank)
        tank_img = IMAGE_DATA.get("rust" if is_rust else "clean", "")

        return html.Div(
            style={"display": "flex", "flexDirection": "column", "width": "100%", "overflow": "hidden"},
            children=[
                # Simulation Control Bar
                html.Div(
                    style={
                        "backgroundColor": "#1e293b",
                        "padding": "12px 24px",
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "borderBottom": "1px solid #334155",
                        "flexWrap": "wrap",
                        "gap": "12px",
                    },
                    children=[
                        html.Div(
                            children=[
                                html.Span(
                                    "INTERACTIVE SHIP CONDITION SIMULATION: ",
                                    style={
                                        "fontSize": "11.5px",
                                        "fontWeight": "800",
                                        "letterSpacing": "1px",
                                        "color": "#94a3b8",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    },
                                ),
                                html.Span(
                                    "Toggle physical tank defect to observe corrosion detection and propagation into the Digital Twin."
                                    if not is_rust else
                                    "Rust defect active on physical ship. Inspection sensors broadcasting oxidation telemetry to Digital Twin.",
                                    style={"fontSize": "12.5px", "color": "#cbd5e1"},
                                ),
                            ]
                        ),
                        html.Div(
                            style={"display": "flex", "gap": "10px"},
                            children=[
                                html.Button(
                                    "⚠️ Trigger Rust Defect",
                                    id={"type": "panel-sim-rust-btn", "index": 1},
                                    n_clicks=0,
                                    style={
                                        "minHeight": "40px",
                                        "padding": "8px 20px",
                                        "borderRadius": "8px",
                                        "border": "2px solid #ef4444",
                                        "backgroundColor": "#ef4444" if is_rust else "#0f172a",
                                        "color": "#ffffff" if is_rust else "#f87171",
                                        "fontSize": "13.5px",
                                        "fontWeight": "800",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                        "cursor": "pointer",
                                        "boxShadow": "0 0 14px rgba(239, 68, 68, 0.45)" if is_rust else "none",
                                    },
                                ),
                                html.Button(
                                    "🟢 Nominal Baseline",
                                    id={"type": "panel-sim-clean-btn", "index": 1},
                                    n_clicks=0,
                                    style={
                                        "minHeight": "40px",
                                        "padding": "8px 20px",
                                        "borderRadius": "8px",
                                        "border": "2px solid #10b981",
                                        "backgroundColor": "#10b981" if not is_rust else "#0f172a",
                                        "color": "#ffffff" if not is_rust else "#34d399",
                                        "fontSize": "13.5px",
                                        "fontWeight": "800",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                        "cursor": "pointer",
                                        "boxShadow": "0 0 14px rgba(16, 185, 129, 0.45)" if not is_rust else "none",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),

                # Single Viewport: ONLY Physical Ship / Ballast Tank
                html.Div(
                    style={"backgroundColor": "#020617", "padding": "20px 24px", "display": "flex", "flexDirection": "column", "gap": "14px", "overflowY": "auto", "maxHeight": "calc(90vh - 160px)"},
                    children=[
                        html.Div(
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "10px",
                                "backgroundColor": "#0f172a",
                                "borderRadius": "14px",
                                "padding": "16px",
                                "border": f"2px solid {'#ef4444' if is_rust else '#334155'}",
                            },
                            children=[
                                html.Div(
                                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                                    children=[
                                        html.Span(
                                            "⚓ PHYSICAL ASSET: REAL MSC VESSEL (BALLAST TANK B-3)",
                                            style={
                                                "fontSize": "12px",
                                                "fontWeight": "800",
                                                "color": "#38bdf8",
                                                "letterSpacing": "1px",
                                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            },
                                        ),
                                        html.Span(
                                            "🔴 CORROSION DETECTED @ LOWER BULKHEAD" if is_rust else "🟢 INTACT STEEL & PROTECTIVE EPOXY (18.0mm)",
                                            style={
                                                "fontSize": "11.5px",
                                                "fontWeight": "800",
                                                "color": "#f87171" if is_rust else "#34d399",
                                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            },
                                        ),
                                    ],
                                ),
                                html.Div(
                                    style={
                                        "position": "relative",
                                        "height": "440px",
                                        "borderRadius": "10px",
                                        "overflow": "hidden",
                                        "backgroundColor": "#020617",
                                        "border": "1.5px solid #1e293b",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                    },
                                    children=[
                                        html.Img(
                                            src=tank_img,
                                            alt="Real MSC Vessel Ballast Tank",
                                            style={"width": "100%", "height": "100%", "objectFit": "cover", "display": "block"},
                                        ),
                                        html.Div(
                                            "🔴 CORROSION & PITTING DETECTED: -1.8mm THICKNESS LOSS"
                                            if is_rust else
                                            "⚓ INTACT STEEL & PROTECTIVE EPOXY COATING",
                                            style={
                                                "position": "absolute",
                                                "bottom": "12px",
                                                "left": "14px",
                                                "backgroundColor": "rgba(15, 23, 42, 0.92)",
                                                "color": "#f87171" if is_rust else "#34d399",
                                                "padding": "6px 14px",
                                                "borderRadius": "6px",
                                                "fontSize": "12px",
                                                "fontWeight": "800",
                                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                "border": f"1px solid {'#ef4444' if is_rust else '#334155'}",
                                            },
                                        ),
                                    ],
                                ),
                                html.Div(
                                    style={
                                        "fontSize": "11.5px",
                                        "color": "#94a3b8",
                                        "display": "flex",
                                        "justifyContent": "space-between",
                                        "fontWeight": "600",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                        "padding": "4px 2px",
                                    },
                                    children=[
                                        html.Span("MOUNTED SENSORS: LiDAR LD-01 · Hyper HS-01 · Optical CAM-02"),
                                        html.Span("COMPARTMENT: Frame 38 Lower Bulkhead · Capacity 1,280 m³ Seawater"),
                                    ],
                                ),

                                # Digital Twin (DT) Synchronization Bridge Card
                                html.Div(
                                    style={
                                        "backgroundColor": "#1e293b",
                                        "border": f"1.5px solid {'#ef4444' if is_rust else '#38bdf8'}",
                                        "borderRadius": "10px",
                                        "padding": "12px 18px",
                                        "display": "flex",
                                        "justifyContent": "space-between",
                                        "alignItems": "center",
                                        "flexWrap": "wrap",
                                        "gap": "10px",
                                    },
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Span("DIGITAL TWIN (DT) SYNCHRONIZATION: ", style={"fontSize": "11px", "fontWeight": "800", "color": "#94a3b8", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                                                html.Span("Virtual CAD Mesh Replica (MSC-TNK-B3-V2.1)", style={"fontSize": "13px", "fontWeight": "700", "color": "#ffffff"}),
                                                html.Div(
                                                    "⚠️ CAD MESH ALERT: Rust defect synchronized (-1.8mm recess @ Frame 38)" if is_rust else "🟢 CAD MESH NOMINAL: Bulkhead geometry intact (Health: 98%)",
                                                    style={"fontSize": "12px", "color": "#f87171" if is_rust else "#34d399", "fontWeight": "600", "marginTop": "2px"}
                                                ),
                                            ]
                                        ),
                                        html.Button(
                                            "🔍 View Digital Twin (DT) CAD Mesh →",
                                            id={"type": "open-modal-btn", "index": "twin"},
                                            n_clicks=0,
                                            style={
                                                "backgroundColor": "#2563eb",
                                                "color": "#ffffff",
                                                "border": "none",
                                                "borderRadius": "8px",
                                                "padding": "9px 20px",
                                                "fontSize": "13px",
                                                "fontWeight": "800",
                                                "cursor": "pointer",
                                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            }
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                ),

                # Footer
                html.Div(
                    style={
                        "backgroundColor": "#0f172a",
                        "padding": "12px 24px",
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "borderTop": "1px solid #1e293b",
                        "fontSize": "11.5px",
                        "color": "#94a3b8",
                        "fontWeight": "600",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                    },
                    children=[
                        html.Span("PHYSICAL ASSET: MSC Vessel Cargo Hold Compartment B-3 Lower Bulkhead"),
                        html.Span("DIGITAL TWIN BRIDGE: ACTIVE (<180ms)", style={"color": "#38bdf8", "fontWeight": "800"}),
                    ],
                ),
            ],
        )
    else:
        # Dedicated Engineering Blueprint & Telemetry for non-tank/twin nodes
        return build_placeholder_dialog(target_node, is_rust, user_dropped)


# =============================================================================
# CALLBACKS
# =============================================================================

# 1. Update Phase Store based on Buttons
@app.callback(
    Output("current-phase", "data"),
    [
        Input("btn-phase-1", "n_clicks"),
        Input("btn-phase-2", "n_clicks"),
        Input("btn-phase-3", "n_clicks"),
        Input("btn-phase-4", "n_clicks"),
        Input("btn-phase-4_5", "n_clicks"),
        Input("btn-prev-phase", "n_clicks"),
        Input("btn-next-phase", "n_clicks"),
        Input("svg-phase-sync-input", "value"),
    ],
    State("current-phase", "data"),
    prevent_initial_call=True,
)
def handle_phase_switch(p1, p2, p3, p4, p4_5, prev_click, next_click, svg_phase, current_phase):
    trig_id = callback_context.triggered_id
    if not trig_id:
        return current_phase or 1

    current = current_phase or 1
    phase_keys = [1, 2, 3, 4, 4.5]
    if current not in phase_keys:
        try:
            current = float(current) if "." in str(current) else int(current)
        except Exception:
            current = 1

    cur_idx = phase_keys.index(current) if current in phase_keys else 0

    if trig_id == "btn-phase-1":
        return 1
    elif trig_id == "btn-phase-2":
        return 2
    elif trig_id == "btn-phase-3":
        return 3
    elif trig_id == "btn-phase-4":
        return 4
    elif trig_id == "btn-phase-4_5":
        return 4.5
    elif trig_id == "btn-prev-phase":
        if prev_click and prev_click > 0 and cur_idx > 0:
            return phase_keys[cur_idx - 1]
    elif trig_id == "btn-next-phase":
        if next_click and next_click > 0 and cur_idx < len(phase_keys) - 1:
            return phase_keys[cur_idx + 1]
    elif trig_id == "svg-phase-sync-input":
        try:
            val = float(svg_phase) if "." in str(svg_phase) else int(svg_phase)
            if val in phase_keys:
                return val
        except Exception:
            return current

    return current


# 2. Update Selected Node Store
@app.callback(
    Output("selected-node", "data"),
    [
        Input("svg-selected-sync-input", "value"),
        Input("btn-clear-selection", "n_clicks"),
        Input("current-phase", "data"),
        Input("phase3-view-mode", "data"),
        Input({"type": "node-list-item", "index": dash.ALL}, "n_clicks"),
        Input({"type": "back-to-overview-btn", "index": dash.ALL}, "n_clicks"),
        Input("btn-close-modal", "n_clicks"),
        Input({"type": "open-modal-btn", "index": dash.ALL}, "n_clicks"),
    ],
    State("selected-node", "data"),
    prevent_initial_call=True,
)
def handle_node_selection(svg_node, clear_clicks, phase, view_mode, list_item_clicks, back_clicks, close_modal_clicks, open_modal_clicks, current_sel):
    trig_id = callback_context.triggered_id
    if not trig_id:
        return current_sel

    # Modal close button deselects node
    if trig_id == "btn-close-modal":
        return None

    # Phase change or view mode change triggers immediate deselect
    if trig_id in ("current-phase", "phase3-view-mode"):
        return None

    # Clear button clicked
    if trig_id == "btn-clear-selection":
        if clear_clicks and clear_clicks > 0:
            return None
        return current_sel

    # Pattern matching buttons
    if isinstance(trig_id, dict):
        t_type = trig_id.get("type")
        if t_type == "open-modal-btn":
            if any(c and c > 0 for c in (open_modal_clicks or [])):
                target_idx = trig_id.get("index")
                return target_idx if target_idx else "tank"
            return current_sel
        elif t_type == "back-to-overview-btn":
            if any(c and c > 0 for c in (back_clicks or [])):
                return None
            return current_sel
        elif t_type == "node-list-item":
            if any(c and c > 0 for c in (list_item_clicks or [])):
                clicked_id = trig_id.get("index")
                if clicked_id == current_sel:
                    return None
                return clicked_id
            return current_sel

    # Triggered by clicking bubble on the fluid SVG stage
    if trig_id == "svg-selected-sync-input":
        val = svg_node.strip() if svg_node else None
        return val if val else None

    return current_sel


# 2b. Control Full-Screen Screen-Covering Pop-up Modal Visibility
@app.callback(
    Output("tank-twin-modal", "style"),
    [
        Input("selected-node", "data"),

        Input("btn-close-modal", "n_clicks"),
        Input({"type": "open-modal-btn", "index": dash.ALL}, "n_clicks"),
    ],
    prevent_initial_call=False,
)
def control_modal_visibility(selected_node, close_clicks, open_clicks):
    trig = callback_context.triggered_id
    hidden_style = {
        "position": "fixed",
        "inset": "0",
        "width": "100vw",
        "height": "100vh",
        "backgroundColor": "rgba(2, 6, 23, 0.88)",
        "backdropFilter": "blur(10px)",
        "WebkitBackdropFilter": "blur(10px)",
        "zIndex": 99999,
        "display": "none",
        "alignItems": "center",
        "justifyContent": "center",
        "padding": "24px",
        "boxSizing": "border-box",
    }
    visible_style = {
        "position": "fixed",
        "inset": "0",
        "width": "100vw",
        "height": "100vh",
        "backgroundColor": "rgba(2, 6, 23, 0.88)",
        "backdropFilter": "blur(10px)",
        "WebkitBackdropFilter": "blur(10px)",
        "zIndex": 99999,
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
        "padding": "24px",
        "boxSizing": "border-box",
    }
    if trig == "btn-close-modal":
        return hidden_style
    if isinstance(trig, dict) and trig.get("type") == "open-modal-btn":
        if any(c and c > 0 for c in (open_clicks or [])):
            return visible_style
    if selected_node:
        return visible_style
    return hidden_style


def build_point_cloud_pipeline_dialog() -> html.Div:
    """Build the interior modal dialog for the LiDAR Point Cloud -> SAC Pipeline and Software Manual."""
    from sac_manual import build_point_cloud_pipeline_component
    lidar_img = IMAGE_DATA.get("lidar", "")
    sac_img = IMAGE_DATA.get("sac", "")
    remesh_img = IMAGE_DATA.get("blender_remesh") or IMAGE_DATA.get("blender", "")
    return build_point_cloud_pipeline_component(lidar_img, sac_img, remesh_img)


# 2c. Update Full-Screen Modal Header Titles, Status Badge, and Body Contents
@app.callback(
    [
        Output("modal-header-titles", "children"),
        Output("modal-header-status-badge", "children"),
        Output("modal-header-status-badge", "style"),
        Output("modal-body-container", "children"),
    ],
    [
        Input("ship-scenario", "data"),
        Input("current-phase", "data"),
        Input("selected-node", "data"),
        Input("user-dropped-images", "data"),
    ],
)
def update_modal_content(scenario, phase, selected_node, user_dropped=None):
    sc = scenario or "clean"
    is_rust = (sc == "rust")
    target = selected_node or "tank"

    if target in ("ast_system_model", "ast_slide"):
        titles = [
            html.Span("MBSE & DATA STACK ARCHITECTURE", style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#2563eb", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
            html.H2("AST System Model: Formal Systems Engineering & Enterprise Data Stack", style={"fontSize": "22px", "fontWeight": "800", "color": "#ffffff", "margin": "2px 0 0 0", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
            html.Span("Ontological Semantics · Taxonomic Classification · Relational Schema · SysML 2.0 Digital Thread · Algedonic Closed-Loop", style={"fontSize": "12px", "color": "#94a3b8"}),
        ]
        badge_text = "📐 MBSE ARCHITECTURE SPECIFICATION"
        badge_style = {"backgroundColor": "#eff6ff", "color": "#2563eb", "border": "1.5px solid #bfdbfe", "borderRadius": "8px", "padding": "6px 14px", "fontWeight": "800", "fontSize": "12px"}
        ast_img_src = IMAGE_DATA.get("ast_system_model") or IMAGE_DATA.get("ast_slide", "")
        body_content = html.Div(
            style={"display": "flex", "flexDirection": "column", "width": "100%", "gap": "14px", "maxHeight": "calc(88vh - 80px)", "overflowY": "auto", "padding": "8px"},
            children=[
                html.Div(
                    style={"backgroundColor": "#0f172a", "borderRadius": "12px", "border": "2px solid #2563eb", "overflow": "hidden", "display": "flex", "alignItems": "center", "justifyContent": "center", "boxShadow": "0 4px 14px rgba(0,0,0,0.25)", "minHeight": "450px"},
                    children=[
                        html.Img(src=ast_img_src, style={"width": "100%", "height": "auto", "maxHeight": "560px", "objectFit": "contain", "display": "block"}) if ast_img_src else html.Div("AST System Model", style={"color": "#64748b", "padding": "20px"}),
                    ],
                ),
            ],
        )
        return titles, badge_text, badge_style, body_content

    if target in ("point_cloud", "point-cloud", "pipeline_lidar_sac"):
        titles = [
            html.Span(
                "DATA PIPELINE · LIDAR POINT CLOUD TO SURFACE AREA CALCULATION (SAC)",
                style={
                    "fontSize": "11px",
                    "fontWeight": "800",
                    "letterSpacing": "1.2px",
                    "color": "#38bdf8",
                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                },
            ),
            html.H2(
                "Point Cloud to Surface Mesh Transformation Pipeline",
                style={
                    "fontSize": "22px",
                    "fontWeight": "800",
                    "color": "#ffffff",
                    "margin": "2px 0 0 0",
                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                },
            ),
            html.Span(
                "Multi-stage software manual converting raw .e57 point clouds into validated watertight 3D meshes",
                style={"fontSize": "12px", "color": "#94a3b8"},
            ),
        ]
        badge_text = "🟢 ACCEPTANCE RULE: CONFIDENCE > 0.83"
        badge_style = {
            "backgroundColor": "#064e3b",
            "color": "#34d399",
            "border": "1.5px solid #10b981",
            "borderRadius": "8px",
            "padding": "6px 14px",
            "fontWeight": "800",
            "fontSize": "12px",
            "letterSpacing": "0.5px",
            "fontFamily": "'Barlow Semi Condensed', sans-serif",
        }
        body_content = build_point_cloud_pipeline_dialog()
        return titles, badge_text, badge_style, body_content

    if target == "twin":
        titles = [
            html.Span(
                "VIRTUAL ASSET · 3D DIGITAL TWIN REPLICA",
                style={
                    "fontSize": "11px",
                    "fontWeight": "800",
                    "letterSpacing": "1.2px",
                    "color": "#34d399",
                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                },
            ),
            html.H2(
                "Digital Twin (DT): 3D CAD Mesh Model",
                style={
                    "fontSize": "22px",
                    "fontWeight": "800",
                    "color": "#ffffff",
                    "margin": "2px 0 0 0",
                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                },
            ),
            html.Span(
                "MSC-TNK-B3-V2.1 · 42,850 Vertices · Real-time bidirectional telemetry sync (<180ms latency)",
                style={"fontSize": "12px", "color": "#94a3b8"},
            ),
        ]
        badge_text = "⚠️ RUST DEFECT DETECTED IN CAD MESH (HEALTH: 42%)" if is_rust else "🟢 TWIN SYNCHRONIZED · BULKHEAD NOMINAL (HEALTH: 98%)"
        badge_style = {
            "backgroundColor": "#450a0a" if is_rust else "#064e3b",
            "color": "#f87171" if is_rust else "#34d399",
            "border": f"1.5px solid {'#ef4444' if is_rust else '#10b981'}",
            "borderRadius": "8px",
            "padding": "6px 14px",
            "fontWeight": "800",
            "fontSize": "12px",
            "letterSpacing": "0.5px",
            "fontFamily": "'Barlow Semi Condensed', sans-serif",
        }
        body_content = build_modal_dialog(sc, phase or 3, "twin", user_dropped)
    elif target == "tank":
        titles = [
            html.Span(
                "PHYSICAL ASSET · MSC VESSEL CARGO COMPARTMENT B-3",
                style={
                    "fontSize": "11px",
                    "fontWeight": "800",
                    "letterSpacing": "1.2px",
                    "color": "#38bdf8",
                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                },
            ),
            html.H2(
                "MSC Ballast Tank B-3 Inspection",
                style={
                    "fontSize": "22px",
                    "fontWeight": "800",
                    "color": "#ffffff",
                    "margin": "2px 0 0 0",
                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                },
            ),
            html.Span(
                "Frame 38 Lower Bulkhead · Mounts LiDAR LD-01, Hyperspectral HS-01 & 4K Video telemetry stream",
                style={"fontSize": "12px", "color": "#94a3b8"},
            ),
        ]
        badge_text = "🔴 CORROSION DEFECT DETECTED ON SHIP BULKHEAD" if is_rust else "🟢 INTACT STEEL & PROTECTIVE EPOXY COATING (18.0mm)"
        badge_style = {
            "backgroundColor": "#450a0a" if is_rust else "#064e3b",
            "color": "#f87171" if is_rust else "#34d399",
            "border": f"1.5px solid {'#ef4444' if is_rust else '#10b981'}",
            "borderRadius": "8px",
            "padding": "6px 14px",
            "fontWeight": "800",
            "fontSize": "12px",
            "letterSpacing": "0.5px",
            "fontFamily": "'Barlow Semi Condensed', sans-serif",
        }
        body_content = build_modal_dialog(sc, phase or 3, "tank", user_dropped)
    else:
        meta = NODE_MODAL_METADATA.get(target, {
            "super_title": "DIGITAL TWIN PIPELINE COMPONENT",
            "title": f"Component: {target.upper()}",
            "subtitle": "Active component in the Digital Twin architecture",
            "clean_badge": "🟢 SYSTEM COMPONENT NOMINAL",
            "clean_badge_style": {"backgroundColor": "#064e3b", "color": "#34d399", "border": "1.5px solid #10b981"},
            "rust_badge": "⚠️ DEFECT EVENT PROPAGATED",
            "rust_badge_style": {"backgroundColor": "#450a0a", "color": "#f87171", "border": "1.5px solid #ef4444"},
        })
        titles = [
            html.Span(
                meta["super_title"],
                style={
                    "fontSize": "11px",
                    "fontWeight": "800",
                    "letterSpacing": "1.2px",
                    "color": "#38bdf8",
                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                },
            ),
            html.H2(
                meta["title"],
                style={
                    "fontSize": "22px",
                    "fontWeight": "800",
                    "color": "#ffffff",
                    "margin": "2px 0 0 0",
                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                },
            ),
            html.Span(
                meta["subtitle"],
                style={"fontSize": "12px", "color": "#94a3b8"},
            ),
        ]
        badge_text = meta["rust_badge"] if is_rust else meta["clean_badge"]
        badge_style = {
            **(meta["rust_badge_style"] if is_rust else meta["clean_badge_style"]),
            "borderRadius": "8px",
            "padding": "6px 14px",
            "fontWeight": "800",
            "fontSize": "12px",
            "letterSpacing": "0.5px",
            "fontFamily": "'Barlow Semi Condensed', sans-serif",
        }
        body_content = build_modal_dialog(sc, phase or 3, target, user_dropped)

    return titles, badge_text, badge_style, body_content

# 2d. Handle Drag-and-Drop Image Upload, Replacement, or Reset in Inspector Modal
@app.callback(
    Output("user-dropped-images", "data"),
    [
        Input({"type": "dropzone-upload", "index": ALL}, "contents"),
        Input({"type": "replace-upload", "index": ALL}, "contents"),
        Input({"type": "clear-image-btn", "index": ALL}, "n_clicks"),
    ],
    [
        State({"type": "dropzone-upload", "index": ALL}, "id"),
        State({"type": "replace-upload", "index": ALL}, "id"),
        State({"type": "clear-image-btn", "index": ALL}, "id"),
        State("user-dropped-images", "data"),
    ],
    prevent_initial_call=True,
)
def handle_user_dropped_images(drop_contents, replace_contents, clear_clicks, drop_ids, replace_ids, clear_ids, current_store):
    store = dict(current_store or {})
    trig = callback_context.triggered_id
    if not trig:
        return no_update

    # 1. Dropped or chosen via dropzone
    for contents, cid in zip(drop_contents, drop_ids):
        if contents and trig == cid:
            node_id = cid["index"]
            store[node_id] = contents
            save_uploaded_image_file(node_id, contents)
            return store

    # 2. Replaced via replace upload button
    for contents, cid in zip(replace_contents, replace_ids):
        if contents and trig == cid:
            node_id = cid["index"]
            store[node_id] = contents
            save_uploaded_image_file(node_id, contents)
            return store

    # 3. Cleared via reset button
    for clicks, cid in zip(clear_clicks, clear_ids):
        if clicks and trig == cid:
            node_id = cid["index"]
            store.pop(node_id, None)
            remove_uploaded_image_file(node_id)
            return store

    return no_update


# 3. Highlight the Active Phase Button in Amber
@app.callback(
    [Output(f"btn-phase-{str(p).replace('.', '_')}", "style") for p in [1, 2, 3, 4, 4.5]],
    Input("current-phase", "data"),
)
def update_phase_button_styles(current_phase):
    phase = current_phase or 1
    try:
        phase = float(phase) if "." in str(phase) else int(phase)
    except Exception:
        phase = 1

    styles = []
    for p in [1, 2, 3, 4, 4.5]:
        if p == phase:
            styles.append({
                "minHeight": "60px",
                "padding": "10px 14px",
                "borderRadius": "12px",
                "border": "2.5px solid #d97706",
                "backgroundColor": "#f59e0b",
                "color": "#ffffff",
                "cursor": "pointer",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "alignItems": "flex-start",
                "textAlign": "left",
                "boxShadow": "0 6px 18px rgba(245, 158, 11, 0.35)",
                "transform": "translateY(-1px)",
                "transition": "all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1)",
            })
        else:
            styles.append({
                "minHeight": "60px",
                "padding": "10px 14px",
                "borderRadius": "12px",
                "border": "2px solid #e2e8f0",
                "backgroundColor": "#ffffff",
                "color": "#0f172a",
                "cursor": "pointer",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "alignItems": "flex-start",
                "textAlign": "left",
                "boxShadow": "none",
                "transform": "none",
                "transition": "all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1)",
            })

    return styles


# 4. Phase 3 View Mode Toggle Callback (Graph vs Ship Simulation)
@app.callback(
    Output("phase3-view-mode", "data"),
    [
        Input("btn-view-graph", "n_clicks"),
        Input("btn-view-ship", "n_clicks"),
        Input({"type": "open-ship-sim-btn", "index": dash.ALL}, "n_clicks"),
        Input({"type": "return-to-graph-btn", "index": dash.ALL}, "n_clicks"),
        Input("current-phase", "data"),
    ],
    State("phase3-view-mode", "data"),
    prevent_initial_call=True,
)
def update_phase3_view_mode(btn_graph, btn_ship, open_sim_clicks, return_clicks, phase, current_mode):
    trig_id = callback_context.triggered_id
    if not trig_id:
        return current_mode or "graph"

    return "graph"


# 5. Left Panel Always Displays Graph Canvas (No Separate Tab)
@app.callback(
    [
        Output("phase3-mode-bar", "style"),
        Output("cytoscape-container", "style"),
        Output("ship-simulation-container", "style"),
        Output("btn-view-graph", "style"),
        Output("btn-view-ship", "style"),
    ],
    [
        Input("current-phase", "data"),
        Input("phase3-view-mode", "data"),
    ],
)
def sync_left_panel_views(phase, view_mode):
    # Always keep the architecture graph stage visible at full width.
    # No separate tab switcher is displayed.
    return (
        {"display": "none"},
        {"display": "block", "width": "100%"},
        {"display": "none"},
        {"display": "none"},
        {"display": "none"},
    )


# 6. Ship Simulation Scenario State Store (Clean, Rust)
@app.callback(
    Output("ship-scenario", "data"),
    [
        Input("btn-sim-rust", "n_clicks"),
        Input("btn-sim-clean", "n_clicks"),
        Input({"type": "panel-sim-rust-btn", "index": dash.ALL}, "n_clicks"),
        Input({"type": "panel-sim-clean-btn", "index": dash.ALL}, "n_clicks"),
        Input("selected-node", "data"),

        Input("current-phase", "data"),
    ],
    State("ship-scenario", "data"),
    prevent_initial_call=True,
)
def handle_ship_simulation_actions(rust_c, clean_c, panel_rust, panel_clean, selected_node, current_phase, current_sc):
    trig_id = callback_context.triggered_id
    if not trig_id:
        return current_sc or "clean"

    # Selecting Ballast Tank ALWAYS starts on baseline "clean"
    if trig_id == "selected-node":
        if selected_node == "tank":
            return "clean"
        elif selected_node == "twin":
            # Preserve current scenario so rust defect triggered on physical tank carries over to twin
            return current_sc or "clean"
        return current_sc or "clean"

    # Changing phase resets to clean baseline
    if trig_id == "current-phase":
        return "clean"

    if isinstance(trig_id, dict):
        t_type = trig_id.get("type")
        if t_type == "panel-sim-rust-btn":
            return "rust"
        elif t_type == "panel-sim-clean-btn":
            return "clean"
        return current_sc or "clean"

    if trig_id == "btn-sim-rust":
        if rust_c and rust_c > 0:
            return "rust"
    elif trig_id == "btn-sim-clean":
        if clean_c and clean_c > 0:
            return "clean"

    return current_sc or "clean"


# 7. Render Ship Visual with Dual-Layered Cross-Fade, Real Ship vs Digital Twin, and Provenance HUD
@app.callback(
    [
        Output("ship-img-baseline", "style"),
        Output("ship-img-rust", "style"),
        Output("sensor-laser-sweep", "className"),
        Output("real-ship-defect-callout", "style"),
        Output("real-ship-status-badge", "children"),
        Output("real-ship-status-badge", "style"),
        Output("real-ship-card", "style"),
        Output("dt-img-baseline", "style"),
        Output("dt-img-rust", "style"),
        Output("dt-scanner-sweep", "className"),
        Output("digital-twin-defect-callout", "style"),
        Output("digital-twin-status-badge", "children"),
        Output("digital-twin-status-badge", "style"),
        Output("digital-twin-card", "style"),
        Output("provenance-hud-container", "children"),
        Output("btn-sim-rust", "style"),
        Output("btn-sim-clean", "style"),
    ],
    Input("ship-scenario", "data"),
)
def update_ship_simulation_display(scenario):
    sc = scenario or "clean"
    is_rust = (sc == "rust")

    baseline_style = {
        "position": "absolute",
        "inset": "0",
        "width": "100%",
        "height": "100%",
        "objectFit": "contain",
        "display": "block",
        "transition": "opacity 0.65s cubic-bezier(0.4, 0, 0.2, 1)",
        "opacity": 0.0 if is_rust else 1.0,
        "pointerEvents": "none",
    }

    rust_style = {
        "position": "absolute",
        "inset": "0",
        "width": "100%",
        "height": "100%",
        "objectFit": "contain",
        "display": "block",
        "transition": "opacity 0.65s cubic-bezier(0.4, 0, 0.2, 1)",
        "opacity": 1.0 if is_rust else 0.0,
        "pointerEvents": "none",
    }

    sweep_class = "scanner-beam active-sweep" if is_rust else "scanner-beam"

    # Real Ship Defect Callout on Bulkhead (Handled directly within the high-res engineering graphic)
    callout_style = {
        "display": "none",
    }

    # Real ship card style & status badge
    real_ship_badge_text = "⚠️ PHYSICAL: CORROSION ON BULKHEAD (FRAME 38)" if is_rust else "🟢 PHYSICAL: NOMINAL BASELINE"
    real_ship_badge_style = {
        "fontSize": "11px",
        "fontWeight": "800",
        "backgroundColor": "#dc2626" if is_rust else "#059669",
        "color": "#ffffff",
        "padding": "3px 10px",
        "borderRadius": "6px",
        "fontFamily": "'Barlow Semi Condensed', sans-serif",
        "letterSpacing": "0.5px",
        "boxShadow": "0 0 10px rgba(239, 68, 68, 0.5)" if is_rust else "none",
    }

    real_ship_card_style = {
        "backgroundColor": "#0f172a",
        "borderRadius": "14px",
        "border": "2.5px solid #ef4444" if is_rust else "2px solid #334155",
        "boxShadow": "0 8px 24px rgba(239, 68, 68, 0.25)" if is_rust else "0 8px 24px rgba(0, 0, 0, 0.12)",
        "overflow": "hidden",
        "display": "flex",
        "flexDirection": "column",
        "position": "relative",
        "transition": "all 0.4s ease",
    }

    # Digital Twin: 3D CAD Tank Model Layering
    dt_baseline_style = {
        "position": "absolute",
        "inset": "0",
        "width": "100%",
        "height": "100%",
        "objectFit": "contain",
        "display": "block",
        "transition": "opacity 0.65s cubic-bezier(0.4, 0, 0.2, 1)",
        "opacity": 0.0 if is_rust else 1.0,
        "pointerEvents": "none",
    }

    dt_rust_style = {
        "position": "absolute",
        "inset": "0",
        "width": "100%",
        "height": "100%",
        "objectFit": "contain",
        "display": "block",
        "transition": "opacity 0.65s cubic-bezier(0.4, 0, 0.2, 1)",
        "opacity": 1.0 if is_rust else 0.0,
        "pointerEvents": "none",
    }

    dt_sweep_class = "scanner-beam dt-active-sweep" if is_rust else "scanner-beam"

    # Digital Twin Defect Callout Marker (Integrated directly into the 3D CAD mesh graphic)
    dt_callout_style = {
        "display": "none",
    }

    dt_badge_text = "⚠️ TWIN: RUST DEFECT DETECTED IN CAD MESH" if is_rust else "🟢 TWIN: SYNCHRONIZED (NOMINAL)"
    dt_badge_style = {
        "fontSize": "11px",
        "fontWeight": "800",
        "backgroundColor": "#dc2626" if is_rust else "#059669",
        "color": "#ffffff",
        "padding": "3px 10px",
        "borderRadius": "6px",
        "fontFamily": "'Barlow Semi Condensed', sans-serif",
        "letterSpacing": "0.5px",
        "boxShadow": "0 0 10px rgba(239, 68, 68, 0.5)" if is_rust else "none",
    }

    dt_card_style = {
        "backgroundColor": "#030712",
        "borderRadius": "14px",
        "border": "2.5px solid #ef4444" if is_rust else "2px solid #1e293b",
        "boxShadow": "0 8px 24px rgba(239, 68, 68, 0.25)" if is_rust else "0 8px 24px rgba(0, 0, 0, 0.12)",
        "overflow": "hidden",
        "display": "flex",
        "flexDirection": "column",
        "position": "relative",
        "transition": "all 0.4s ease",
    }

    hud_children = render_provenance_hud(sc)

    btn_rust_style = {
        "minHeight": "52px",
        "padding": "10px 22px",
        "borderRadius": "10px",
        "border": "2.5px solid #dc2626" if is_rust else "2px solid #ef4444",
        "backgroundColor": "#ef4444" if is_rust else "#fef2f2",
        "color": "#ffffff" if is_rust else "#b91c1c",
        "fontSize": "15px",
        "fontWeight": "800",
        "fontFamily": "'Barlow Semi Condensed', sans-serif",
        "cursor": "pointer",
        "boxShadow": "0 4px 14px rgba(239, 68, 68, 0.4)" if is_rust else "none",
        "transform": "translateY(-1px)" if is_rust else "none",
    }

    btn_clean_style = {
        "minHeight": "52px",
        "padding": "10px 20px",
        "borderRadius": "10px",
        "border": "2.5px solid #059669" if not is_rust else "2px solid #cbd5e1",
        "backgroundColor": "#10b981" if not is_rust else "#ffffff",
        "color": "#ffffff" if not is_rust else "#475569",
        "fontSize": "15px",
        "fontWeight": "800",
        "fontFamily": "'Barlow Semi Condensed', sans-serif",
        "cursor": "pointer",
        "boxShadow": "0 4px 14px rgba(16, 185, 129, 0.3)" if not is_rust else "none",
        "transform": "translateY(-1px)" if not is_rust else "none",
    }

    return (
        baseline_style,
        rust_style,
        sweep_class,
        callout_style,
        real_ship_badge_text,
        real_ship_badge_style,
        real_ship_card_style,
        dt_baseline_style,
        dt_rust_style,
        dt_sweep_class,
        dt_callout_style,
        dt_badge_text,
        dt_badge_style,
        dt_card_style,
        hud_children,
        btn_rust_style,
        btn_clean_style,
    )


# 8. (Retired) Cytoscape Elements Update - Replaced by 60fps RAF SVG Diagram Engine
# Elements are now smoothly interpolated directly on the GPU via SVG stage.


# 9. Update Notes Panel Content and Prev/Next Button Disabled States
@app.callback(
    [
        Output("notes-panel-content", "children"),
        Output("btn-prev-phase", "disabled"),
        Output("btn-prev-phase", "style"),
        Output("btn-next-phase", "disabled"),
        Output("btn-next-phase", "style"),
    ],
    [
        Input("current-phase", "data"),
        Input("selected-node", "data"),

        Input("phase3-view-mode", "data"),
        Input("ship-scenario", "data"),
    ],
)
def update_notes_panel(current_phase, selected_node, view_mode, ship_scenario):
    phase = current_phase or 1
    try:
        phase = float(phase) if "." in str(phase) else int(phase)
    except Exception:
        phase = 1

    phase_info = CONTENT["phases"].get(phase, CONTENT["phases"][1])

    phase_keys = [1, 2, 3, 4, 4.5]
    cur_idx = phase_keys.index(phase) if phase in phase_keys else 0
    is_prev_disabled = (cur_idx <= 0)
    is_next_disabled = (cur_idx >= len(phase_keys) - 1)

    prev_style = {
        "minHeight": "56px",
        "borderRadius": "10px",
        "border": "2px solid #cbd5e1" if not is_prev_disabled else "2px solid #e2e8f0",
        "backgroundColor": "#ffffff" if not is_prev_disabled else "#f1f5f9",
        "color": "#0f172a" if not is_prev_disabled else "#94a3b8",
        "fontSize": "16px",
        "fontWeight": "700",
        "fontFamily": "'Barlow Semi Condensed', sans-serif",
        "cursor": "pointer" if not is_prev_disabled else "not-allowed",
        "opacity": 1.0 if not is_prev_disabled else 0.5,
    }

    next_style = {
        "minHeight": "56px",
        "borderRadius": "10px",
        "border": "2px solid #0f172a" if not is_next_disabled else "2px solid #e2e8f0",
        "backgroundColor": "#0f172a" if not is_next_disabled else "#f1f5f9",
        "color": "#ffffff" if not is_next_disabled else "#94a3b8",
        "fontSize": "16px",
        "fontWeight": "700",
        "fontFamily": "'Barlow Semi Condensed', sans-serif",
        "cursor": "pointer" if not is_next_disabled else "not-allowed",
        "opacity": 1.0 if not is_next_disabled else 0.5,
    }

    sc = ship_scenario or "clean"
    is_rust = (sc == "rust")

    # Case A: User selected Ballast Tank (Physical Asset)
    if selected_node == "tank":
        node = CONTENT["nodes"]["tank"]
        receives_from, sends_to = get_node_connections("tank", phase)
        tank_img = IMAGE_DATA.get("rust" if is_rust else "clean", "")

        content = html.Div(
            className="panel-slide-anim",
            style={"display": "flex", "flexDirection": "column", "gap": "16px"},
            children=[
                # Back to overview button
                html.Button(
                    "← Back to phase overview",
                    id={"type": "back-to-overview-btn", "index": 0},
                    n_clicks=0,
                    style={
                        "minHeight": "44px",
                        "padding": "8px 16px",
                        "borderRadius": "10px",
                        "border": "2px solid #d97706",
                        "backgroundColor": "#fffbeb",
                        "color": "#b45309",
                        "fontSize": "14px",
                        "fontWeight": "700",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                        "cursor": "pointer",
                        "textAlign": "left",
                    },
                ),

                # Header & Badges
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Div(
                            style={"display": "flex", "alignItems": "center", "justifyContent": "space-between", "flexWrap": "wrap", "gap": "6px"},
                            children=[
                                html.Span(
                                    "BALLAST TANK & SENSORS",
                                    style={
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "letterSpacing": "1.2px",
                                        "color": "#b91c1c",
                                        "backgroundColor": "rgba(254, 242, 242, 0.75)",
                                        "border": "1.5px solid #ef4444",
                                        "borderRadius": "6px",
                                        "padding": "3px 8px",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    },
                                ),
                                html.Span(
                                    "🔴 CORROSION DEFECT DETECTED" if is_rust else "🟢 NOMINAL COATING BASELINE",
                                    style={
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "color": "#b91c1c" if is_rust else "#047857",
                                        "backgroundColor": "#fef2f2" if is_rust else "#f0fdf4",
                                        "border": f"1.5px solid {'#ef4444' if is_rust else '#10b981'}",
                                        "borderRadius": "6px",
                                        "padding": "3px 8px",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    },
                                ),
                            ],
                        ),
                        html.H2(
                            "Ballast Tank",
                            style={
                                "fontSize": "28px",
                                "fontWeight": "800",
                                "color": "#0f172a",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                "lineHeight": 1.1,
                                "margin": "0",
                            },
                        ),
                        html.Span(
                            "Real MSC Vessel Cargo Hold Compartment B-3 (Port Bulkhead)",
                            style={"fontSize": "12.5px", "color": "#64748b", "fontWeight": "600"},
                        ),
                    ],
                ),

                # Screen-Covering Inspector Modal Launch Card
                html.Div(
                    style={
                        "backgroundColor": "#f0fdf4" if not is_rust else "#fef2f2",
                        "border": f"1.5px solid {'#ef4444' if is_rust else '#10b981'}",
                        "borderRadius": "12px",
                        "padding": "16px",
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "10px",
                    },
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                            children=[
                                html.Span(
                                    "BALLAST TANK FULL-SCREEN INSPECTOR",
                                    style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#b91c1c" if is_rust else "#0369a1", "fontFamily": "'Barlow Semi Condensed', sans-serif"},
                                ),
                                html.Span(
                                    "🔴 DEFECT ACTIVE" if is_rust else "🟢 NOMINAL BASELINE",
                                    style={"fontSize": "11px", "fontWeight": "800", "color": "#b91c1c" if is_rust else "#047857"},
                                ),
                            ],
                        ),
                        html.P(
                            "The pop-up covers the full screen with high-resolution inspection of the real ship and physical Ballast Tank with rust simulation.",
                            style={"fontSize": "13px", "lineHeight": "1.45", "color": "#334155", "margin": "0"},
                        ),
                        html.Div(
                            style={
                                "position": "relative",
                                "height": "200px",
                                "borderRadius": "8px",
                                "overflow": "hidden",
                                "backgroundColor": "#020617",
                                "border": "1.5px solid #1e293b",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                            },
                            children=[
                                html.Img(src=tank_img, style={"width": "100%", "height": "100%", "objectFit": "contain", "display": "block"})
                            ]
                        ) if tank_img else None,
                        html.Button(
                            "🔍 Open Ballast Tank (Ship) Inspector",
                            id={"type": "open-modal-btn", "index": "tank"},
                            n_clicks=0,
                            style={
                                "minHeight": "46px",
                                "padding": "10px 18px",
                                "borderRadius": "10px",
                                "border": "2px solid #0f172a",
                                "backgroundColor": "#0f172a",
                                "color": "#ffffff",
                                "fontSize": "14px",
                                "fontWeight": "800",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                "cursor": "pointer",
                                "boxShadow": "0 4px 14px rgba(0, 0, 0, 0.15)",
                            },
                        ),
                    ],
                ),

                # Description
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Span("DESCRIPTION", style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#64748b", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                        html.P(node["description"], style={"fontSize": "14px", "lineHeight": "1.5", "color": "#1e293b", "margin": "0"}),
                    ],
                ),

                # What it provides
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Span("WHAT IT PROVIDES", style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#64748b", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                        html.Div(
                            style={"display": "flex", "flexWrap": "wrap", "gap": "6px"},
                            children=[
                                html.Span(item, style={"fontSize": "12.5px", "fontWeight": "600", "color": "#0f172a", "backgroundColor": "#f1f5f9", "border": "1px solid #cbd5e1", "borderRadius": "6px", "padding": "4px 8px"})
                                for item in node["provides"]
                            ],
                        ),
                    ],
                ),

                # Connections
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "8px", "paddingTop": "8px", "borderTop": "1px solid #e2e8f0"},
                    children=[
                        html.Span(f"CONNECTIONS IN {phase_info['name'].upper()}", style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#64748b", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                        html.Div(
                            style={"fontSize": "13px", "color": "#334155"},
                            children=[
                                html.Div(f"• Receives from: {', '.join(receives_from) if receives_from else 'None'}"),
                                html.Div(f"• Sends to: {', '.join(sends_to) if sends_to else 'None'}"),
                            ],
                        ),
                    ],
                ),
            ],
        )
        return content, is_prev_disabled, prev_style, is_next_disabled, next_style

    # Case B: User selected Digital Twin (Virtual Asset)
    if selected_node == "twin":
        node = CONTENT["nodes"]["twin"]
        receives_from, sends_to = get_node_connections("twin", phase)
        twin_img = IMAGE_DATA.get("dt_rust" if is_rust else "dt_clean", "")
        health_score = 42 if is_rust else 98
        health_color = "#ef4444" if is_rust else "#10b981"

        content = html.Div(
            className="panel-slide-anim",
            style={"display": "flex", "flexDirection": "column", "gap": "16px"},
            children=[
                # Back to overview button
                html.Button(
                    "← Back to phase overview",
                    id={"type": "back-to-overview-btn", "index": 0},
                    n_clicks=0,
                    style={
                        "minHeight": "44px",
                        "padding": "8px 16px",
                        "borderRadius": "10px",
                        "border": "2px solid #d97706",
                        "backgroundColor": "#fffbeb",
                        "color": "#b45309",
                        "fontSize": "14px",
                        "fontWeight": "700",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                        "cursor": "pointer",
                        "textAlign": "left",
                    },
                ),

                # Header & Badges
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Div(
                            style={"display": "flex", "alignItems": "center", "justifyContent": "space-between", "flexWrap": "wrap", "gap": "6px"},
                            children=[
                                html.Span(
                                    "DIGITAL TWIN",
                                    style={
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "letterSpacing": "1.2px",
                                        "color": "#1d4ed8",
                                        "backgroundColor": "rgba(239, 246, 255, 0.75)",
                                        "border": "1.5px solid #3b82f6",
                                        "borderRadius": "6px",
                                        "padding": "3px 8px",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    },
                                ),
                                html.Span(
                                    "⚠️ RUST DEFECT IN CAD MESH" if is_rust else "🟢 SYNCHRONIZED (NOMINAL)",
                                    style={
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "color": "#b91c1c" if is_rust else "#047857",
                                        "backgroundColor": "#fef2f2" if is_rust else "#f0fdf4",
                                        "border": f"1.5px solid {'#ef4444' if is_rust else '#10b981'}",
                                        "borderRadius": "6px",
                                        "padding": "3px 8px",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    },
                                ),
                            ],
                        ),
                        html.H2(
                            "DT (Digital Twin)",
                            style={
                                "fontSize": "28px",
                                "fontWeight": "800",
                                "color": "#0f172a",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                "lineHeight": 1.1,
                                "margin": "0",
                            },
                        ),
                        html.Span(
                            "Virtual Replica synchronized with physical Ballast Tank B-3",
                            style={"fontSize": "12.5px", "color": "#64748b", "fontWeight": "600"},
                        ),
                    ],
                ),

                # Screen-Covering Inspector Modal Launch Card
                html.Div(
                    style={
                        "backgroundColor": "#f0fdf4" if not is_rust else "#fef2f2",
                        "border": f"1.5px solid {'#ef4444' if is_rust else '#10b981'}",
                        "borderRadius": "12px",
                        "padding": "16px",
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "10px",
                    },
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                            children=[
                                html.Span(
                                    "DIGITAL TWIN FULL-SCREEN INSPECTOR",
                                    style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#b91c1c" if is_rust else "#1d4ed8", "fontFamily": "'Barlow Semi Condensed', sans-serif"},
                                ),
                                html.Span(
                                    "🔴 DEFECT DETECTED" if is_rust else "🟢 TWIN SYNCHRONIZED",
                                    style={"fontSize": "11px", "fontWeight": "800", "color": "#b91c1c" if is_rust else "#047857"},
                                ),
                            ],
                        ),
                        html.P(
                            "The pop-up covers the full screen with high-resolution inspection of the virtual Digital Twin 3D CAD mesh with live defect simulation.",
                            style={"fontSize": "13px", "lineHeight": "1.45", "color": "#334155", "margin": "0"},
                        ),
                        html.Div(
                            style={
                                "position": "relative",
                                "height": "200px",
                                "borderRadius": "8px",
                                "overflow": "hidden",
                                "backgroundColor": "#020617",
                                "border": "1.5px solid #1e293b",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                            },
                            children=[
                                html.Img(src=twin_img, style={"width": "100%", "height": "100%", "objectFit": "contain", "display": "block"})
                            ]
                        ) if twin_img else None,
                        html.Button(
                            "🔍 Open 3D Digital Twin (DT) Inspector",
                            id={"type": "open-modal-btn", "index": "twin"},
                            n_clicks=0,
                            style={
                                "minHeight": "46px",
                                "padding": "10px 18px",
                                "borderRadius": "10px",
                                "border": "2px solid #0f172a",
                                "backgroundColor": "#0f172a",
                                "color": "#ffffff",
                                "fontSize": "14px",
                                "fontWeight": "800",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                "cursor": "pointer",
                                "boxShadow": "0 4px 14px rgba(0, 0, 0, 0.15)",
                            },
                        ),
                    ],
                ),

                # Description
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Span("DESCRIPTION", style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#64748b", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                        html.P(node["description"], style={"fontSize": "14px", "lineHeight": "1.5", "color": "#1e293b", "margin": "0"}),
                    ],
                ),

                # What it provides
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Span("WHAT IT PROVIDES", style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#64748b", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                        html.Div(
                            style={"display": "flex", "flexWrap": "wrap", "gap": "6px"},
                            children=[
                                html.Span(item, style={"fontSize": "12.5px", "fontWeight": "600", "color": "#0f172a", "backgroundColor": "#f1f5f9", "border": "1px solid #cbd5e1", "borderRadius": "6px", "padding": "4px 8px"})
                                for item in node["provides"]
                            ],
                        ),
                    ],
                ),

                # Connections
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "8px", "paddingTop": "8px", "borderTop": "1px solid #e2e8f0"},
                    children=[
                        html.Span(f"CONNECTIONS IN {phase_info['name'].upper()}", style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#64748b", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                        html.Div(
                            style={"fontSize": "13px", "color": "#334155"},
                            children=[
                                html.Div(f"• Receives from: {', '.join(receives_from) if receives_from else 'None'}"),
                                html.Div(f"• Sends to: {', '.join(sends_to) if sends_to else 'None'}"),
                            ],
                        ),
                    ],
                ),
            ],
        )
        return content, is_prev_disabled, prev_style, is_next_disabled, next_style

    # Case C: Other Nodes Selected in Graph View
    if selected_node and selected_node in CONTENT["nodes"]:
        node = CONTENT["nodes"][selected_node]
        group_id = node.get("group")
        group_info = CONTENT["groups"].get(group_id, {}) if group_id else None

        receives_from, sends_to = get_node_connections(selected_node, phase)

        group_label = group_info["label"] if group_info else "External"
        group_border = group_info["border_color"] if group_info else "#f59e0b"
        group_text = group_info["text_color"] if group_info else "#b45309"
        group_bg = group_info["bg_color"] if group_info else "rgba(254, 243, 199, 0.4)"

        node_img = IMAGE_DATA.get(selected_node)
        if selected_node == "hyp":
            node_img = IMAGE_DATA.get("hyperspectral_cubert") or IMAGE_DATA.get("hyp")

        img_card_c = html.Div(
            style={
                "backgroundColor": "#0f172a",
                "borderRadius": "12px",
                "border": "2px solid #38bdf8",
                "overflow": "hidden",
                "display": "flex",
                "flexDirection": "column",
                "boxShadow": "0 6px 18px rgba(0,0,0,0.25)",
            },
            children=[
                html.Div(
                    style={
                        "backgroundColor": "#1e293b",
                        "padding": "8px 12px",
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "borderBottom": "1px solid #334155",
                    },
                    children=[
                        html.Span(
                            f"📸 {node['label'].upper()} SENSOR CAPTURE",
                            style={"fontSize": "11.5px", "fontWeight": "800", "color": "#38bdf8", "fontFamily": "'Barlow Semi Condensed', sans-serif"},
                        ),
                        html.Span(
                            "CLICK TO ENLARGE",
                            style={"fontSize": "10.5px", "fontWeight": "800", "color": "#94a3b8", "backgroundColor": "#0f172a", "padding": "2px 6px", "borderRadius": "4px"},
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "position": "relative",
                        "height": "220px",
                        "backgroundColor": "#020617",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                    },
                    children=[
                        html.Img(src=node_img, style={"width": "100%", "height": "100%", "objectFit": "contain", "display": "block"}),
                    ],
                ),
                html.Button(
                    "🔍 Open Full-Screen Image Inspector",
                    id={"type": "open-modal-btn", "index": selected_node},
                    n_clicks=0,
                    style={
                        "padding": "10px 14px",
                        "backgroundColor": "#0f172a",
                        "border": "none",
                        "borderTop": "1px solid #1e293b",
                        "color": "#38bdf8",
                        "fontSize": "13px",
                        "fontWeight": "800",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                        "cursor": "pointer",
                    },
                ),
            ],
        ) if node_img else None

        content = html.Div(
            className="panel-slide-anim",
            style={"display": "flex", "flexDirection": "column", "gap": "18px"},
            children=[
                # "Back to phase overview" Button
                html.Button(
                    "← Back to phase overview",
                    id={"type": "back-to-overview-btn", "index": 0},
                    n_clicks=0,
                    style={
                        "minHeight": "48px",
                        "padding": "8px 16px",
                        "borderRadius": "10px",
                        "border": "2px solid #d97706",
                        "backgroundColor": "#fffbeb",
                        "color": "#b45309",
                        "fontSize": "15px",
                        "fontWeight": "700",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                        "cursor": "pointer",
                        "textAlign": "left",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "8px",
                    },
                ),

                # Node Header & Group Badge
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Div(
                            style={"display": "flex", "alignItems": "center", "gap": "10px"},
                            children=[
                                html.Span(
                                    group_label.upper(),
                                    style={
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "letterSpacing": "1.2px",
                                        "color": group_text,
                                        "backgroundColor": group_bg,
                                        "border": f"1.5px solid {group_border}",
                                        "borderRadius": "6px",
                                        "padding": "3px 8px",
                                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    },
                                ),
                                html.Span(
                                    node["sublabel"],
                                    style={
                                        "fontSize": "13px",
                                        "color": "#64748b",
                                        "fontWeight": "600",
                                    },
                                ),
                            ],
                        ),
                        html.H2(
                            node["label"],
                            style={
                                "fontSize": "30px",
                                "fontWeight": "800",
                                "color": "#0f172a",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                "lineHeight": 1.1,
                            },
                        ),
                    ],
                ),

                img_card_c,

                # Description Section
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                    children=[
                        html.Span(
                            "DESCRIPTION",
                            style={
                                "fontSize": "11px",
                                "fontWeight": "800",
                                "letterSpacing": "1.2px",
                                "color": "#64748b",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                            },
                        ),
                        html.P(
                            node["description"],
                            style={
                                "fontSize": "15px",
                                "lineHeight": "1.5",
                                "color": "#1e293b",
                            },
                        ),
                        html.Button(
                            "☁️ Inspect 'Point Cloud' Pipeline (LiDAR → SAC)",
                            id={"type": "open-modal-btn", "index": "point_cloud"},
                            n_clicks=0,
                            style={
                                "minHeight": "40px",
                                "padding": "8px 14px",
                                "borderRadius": "8px",
                                "border": "none",
                                "backgroundColor": "#0284c7",
                                "color": "#ffffff",
                                "fontSize": "13px",
                                "fontWeight": "800",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                "cursor": "pointer",
                                "marginTop": "6px",
                            },
                        ) if selected_node in ("lidar", "sac") else None,
                    ],
                ),

                # What it provides Section
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "8px"},
                    children=[
                        html.Span(
                            "WHAT IT PROVIDES",
                            style={
                                "fontSize": "11px",
                                "fontWeight": "800",
                                "letterSpacing": "1.2px",
                                "color": "#64748b",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                            },
                        ),
                        html.Div(
                            style={"display": "flex", "flexWrap": "wrap", "gap": "8px"},
                            children=[
                                html.Span(
                                    item,
                                    style={
                                        "fontSize": "13px",
                                        "fontWeight": "600",
                                        "color": "#0f172a",
                                        "backgroundColor": "#f1f5f9",
                                        "border": "1px solid #cbd5e1",
                                        "borderRadius": "8px",
                                        "padding": "5px 10px",
                                    },
                                )
                                for item in node["provides"]
                            ],
                        ),
                    ],
                ),

                # Current Phase Connections Section
                html.Div(
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "10px",
                        "paddingTop": "8px",
                        "borderTop": "1px solid #e2e8f0",
                    },
                    children=[
                        html.Span(
                            f"CONNECTIONS IN {phase_info['name'].upper()}",
                            style={
                                "fontSize": "11px",
                                "fontWeight": "800",
                                "letterSpacing": "1.2px",
                                "color": "#64748b",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                            },
                        ),
                        html.Div(
                            style={"display": "flex", "flexDirection": "column", "gap": "4px"},
                            children=[
                                html.Span("Receives from:", style={"fontSize": "13px", "fontWeight": "700", "color": "#475569"}),
                                html.Ul(
                                    style={"paddingLeft": "20px", "fontSize": "14px", "color": "#0f172a"},
                                    children=[
                                        html.Li(r, style={"marginBottom": "3px"})
                                        for r in receives_from
                                    ] if receives_from else [
                                        html.Li("None in this phase", style={"color": "#94a3b8", "fontStyle": "italic"})
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            style={"display": "flex", "flexDirection": "column", "gap": "4px"},
                            children=[
                                html.Span("Sends to:", style={"fontSize": "13px", "fontWeight": "700", "color": "#475569"}),
                                html.Ul(
                                    style={"paddingLeft": "20px", "fontSize": "14px", "color": "#0f172a"},
                                    children=[
                                        html.Li(s, style={"marginBottom": "3px"})
                                        for s in sends_to
                                    ] if sends_to else [
                                        html.Li("None in this phase", style={"color": "#94a3b8", "fontStyle": "italic"})
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )
        return content, is_prev_disabled, prev_style, is_next_disabled, next_style

    # Case D: Phase Overview (Nothing Selected)
    visible_node_ids = list(CONTENT["positions"].get(phase, {}).keys())

    phase4_5_special_card = None

    phase2_special_card = None
    if phase == 2:
        phase2_special_card = html.Div(
            style={
                "backgroundColor": "#f0f9ff",
                "borderRadius": "12px",
                "border": "1.5px solid #0284c7",
                "padding": "12px 14px",
                "display": "flex",
                "flexDirection": "column",
                "gap": "8px",
                "marginTop": "8px",
            },
            children=[
                html.Div(
                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                    children=[
                        html.Span("POINT CLOUD PIPELINE", style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#0284c7", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                        html.Span("🟢 CONFIDENCE > 0.83", style={"fontSize": "11px", "fontWeight": "800", "color": "#059669"}),
                    ],
                ),
                html.P(
                    "LiDAR point cloud feeds the SAC surface area calculation engine. Inspect the transformation pipeline & software manual:",
                    style={"fontSize": "13px", "lineHeight": "1.4", "color": "#334155", "margin": "0"},
                ),
                html.Button(
                    "☁️ Open LiDAR ➔ SAC Software Manual",
                    id={"type": "open-modal-btn", "index": "point_cloud"},
                    n_clicks=0,
                    style={
                        "minHeight": "40px",
                        "padding": "8px 14px",
                        "borderRadius": "8px",
                        "border": "none",
                        "backgroundColor": "#0284c7",
                        "color": "#ffffff",
                        "fontSize": "13.5px",
                        "fontWeight": "800",
                        "fontFamily": "'Barlow Semi Condensed', sans-serif",
                        "cursor": "pointer",
                    },
                ),
            ],
        )

    phase3_special_card = None
    if phase == 3:
        phase3_special_card = html.Div(
            style={
                "backgroundColor": "#f0fdf4" if not is_rust else "#fef2f2",
                "borderRadius": "12px",
                "border": f"1.5px solid {'#ef4444' if is_rust else '#10b981'}",
                "padding": "12px 14px",
                "display": "flex",
                "flexDirection": "column",
                "gap": "8px",
            },
            children=[
                html.Div(
                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                    children=[
                        html.Span("LIVE TWIN SYNCHRONIZATION", style={"fontSize": "11px", "fontWeight": "800", "letterSpacing": "1.2px", "color": "#b91c1c" if is_rust else "#047857", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                        html.Span("🔴 CORROSION ACTIVE" if is_rust else "🟢 TWIN SYNCHRONIZED", style={"fontSize": "11px", "fontWeight": "800", "color": "#b91c1c" if is_rust else "#047857"}),
                    ],
                ),
                html.P(
                    "Click on either Ballast Tank or DT in the diagram to inspect photos, 3D CAD mesh, and trigger rust defect simulation:",
                    style={"fontSize": "13px", "lineHeight": "1.4", "color": "#334155", "margin": "0"},
                ),
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px"},
                    children=[
                        html.Button(
                            "⚓ Ballast Tank (Physical)",
                            id={"type": "node-list-item", "index": "tank"},
                            n_clicks=0,
                            style={
                                "minHeight": "38px",
                                "borderRadius": "8px",
                                "border": "1.5px solid #cbd5e1",
                                "backgroundColor": "#ffffff",
                                "color": "#0f172a",
                                "fontSize": "12.5px",
                                "fontWeight": "700",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                "cursor": "pointer",
                            },
                        ),
                        html.Button(
                            "🌐 Digital Twin (Virtual)",
                            id={"type": "node-list-item", "index": "twin"},
                            n_clicks=0,
                            style={
                                "minHeight": "38px",
                                "borderRadius": "8px",
                                "border": "1.5px solid #cbd5e1",
                                "backgroundColor": "#ffffff",
                                "color": "#0f172a",
                                "fontSize": "12.5px",
                                "fontWeight": "700",
                                "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                "cursor": "pointer",
                            },
                        ),
                    ],
                ),
            ],
        )

    content = html.Div(
        className="panel-slide-anim",
        style={"display": "flex", "flexDirection": "column", "gap": "18px"},
        children=[
            # Phase Eyebrow & Title
            html.Div(
                style={"display": "flex", "flexDirection": "column", "gap": "4px"},
                children=[
                    html.Span(
                        f"{phase_info['name'].upper()} OVERVIEW",
                        style={
                            "fontSize": "11.5px",
                            "fontWeight": "800",
                            "letterSpacing": "1.4px",
                            "color": "#d97706",
                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                        },
                    ),
                    html.H2(
                        phase_info["title"],
                        style={
                            "fontSize": "28px",
                            "fontWeight": "800",
                            "color": "#0f172a",
                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                            "lineHeight": 1.15,
                        },
                    ),
                ],
            ),

            # Phase 2 Feature Card (Point Cloud Pipeline)
            phase2_special_card,

            # Phase 3 Feature Card (Direct Tank & Twin Quick Inspector)
            phase3_special_card,

            # Phase 4.5 Feature Card (MBSE & Data Stack)
            phase4_5_special_card,

            # Phase Description
            html.P(
                phase_info["description"],
                style={
                    "fontSize": "15px",
                    "lineHeight": "1.55",
                    "color": "#334155",
                    "backgroundColor": "#f8fafc",
                    "padding": "14px",
                    "borderRadius": "10px",
                    "border": "1px solid #e2e8f0",
                    "display": "block" if phase_info.get("description") else "none",
                },
            ),

            # List of Nodes in this Phase
            html.Div(
                style={"display": "flex", "flexDirection": "column", "gap": "10px"},
                children=[
                    html.Div(
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                        children=[
                            html.Span(
                                f"ACTIVE NODES IN THIS PHASE ({len(visible_node_ids)})",
                                style={
                                    "fontSize": "11px",
                                    "fontWeight": "800",
                                    "letterSpacing": "1.2px",
                                    "color": "#64748b",
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                },
                            ),
                            html.Span("Tap to inspect", style={"fontSize": "12px", "color": "#94a3b8"}),
                        ],
                    ),
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "gap": "8px"},
                        children=[
                            html.Div(
                                "AST System Model · 3 Tiers & SysML Digital Thread",
                                style={"fontSize": "12px", "fontWeight": "700", "color": "#2563eb", "backgroundColor": "#eff6ff", "border": "1px solid #bfdbfe", "padding": "6px 12px", "borderRadius": "6px"}
                            ) if phase == 4.5 else html.Span(
                                "None",
                                style={"fontSize": "12px", "color": "#94a3b8", "fontStyle": "italic"}
                            )
                        ] if len(visible_node_ids) == 0 else [
                            html.Button(
                                id={"type": "node-list-item", "index": nid},
                                n_clicks=0,
                                style={
                                    "padding": "10px 14px",
                                    "borderRadius": "10px",
                                    "border": "1.5px solid #e2e8f0",
                                    "backgroundColor": "#ffffff",
                                    "cursor": "pointer",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "space-between",
                                    "textAlign": "left",
                                    "transition": "all 0.15s ease",
                                },
                                children=[
                                    html.Div(
                                        style={"display": "flex", "alignItems": "center", "gap": "10px"},
                                        children=[
                                            html.Span(
                                                CONTENT["nodes"][nid]["label"],
                                                style={
                                                    "fontSize": "15px",
                                                    "fontWeight": "700",
                                                    "color": "#0f172a",
                                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                                },
                                            ),
                                            html.Span(
                                                CONTENT["nodes"][nid]["sublabel"],
                                                style={"fontSize": "12.5px", "color": "#64748b"},
                                            ),
                                        ],
                                    ),
                                    html.Span(
                                        (CONTENT["groups"].get(CONTENT["nodes"][nid].get("group"), {}).get("label") or "External").upper(),
                                        style={
                                            "fontSize": "10px",
                                            "fontWeight": "800",
                                            "letterSpacing": "1px",
                                            "color": CONTENT["groups"].get(CONTENT["nodes"][nid].get("group"), {}).get("text_color") or "#b45309",
                                            "backgroundColor": CONTENT["groups"].get(CONTENT["nodes"][nid].get("group"), {}).get("bg_color") or "#fef3c7",
                                            "padding": "3px 7px",
                                            "borderRadius": "5px",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                        },
                                    ),
                                ],
                            )
                            for nid in visible_node_ids
                        ],
                    ),
                ],
            ),
        ],
    )

    return content, is_prev_disabled, prev_style, is_next_disabled, next_style


# 10. Clientside Callback for Fluid SVG Diagram Phase Animation & Node Selection Sync
app.clientside_callback(
    """
    function(phase, selectedNode, scenario) {
        if (window.goToPhase && phase) {
            window.goToPhase(phase);
        }
        if (window.selectNodeInternal) {
            window.selectNodeInternal(selectedNode);
        }
        if (window.setScenario) {
            window.setScenario(scenario);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("dummy-clientside-anim", "children"),
    [
        Input("current-phase", "data"),
        Input("selected-node", "data"),

        Input("ship-scenario", "data"),
    ],
)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    host = CONTENT["app"].get("host", "127.0.0.1")
    port = CONTENT["app"].get("port", 8056)
    try:
        import export_to_html
        print("Auto-compiling standalone HTML file (digital_twin_story.html) with embedded images...")
        export_to_html.generate_html()
    except Exception as e:
        print(f"Note on HTML export: {e}")
    print(f"Starting Digital Twin Story Timeline app on http://{host}:{port} ...")
    app.run(host=host, port=port, debug=False)
