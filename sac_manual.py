"""Surface Area Calculation (SAC) Project Software Manual & Visual Comparison.
Provides both native Dash component trees and standalone HTML string generation
for the LiDAR Point Cloud -> SAC transformation pipeline.
Layout: 2-column side-by-side (Images on one side, short & brief summary on the other side, no heavy scrolling).
"""
from typing import Optional
from dash import html

def build_point_cloud_pipeline_component(img_lidar: str = "", img_sac: str = "") -> html.Div:
    """Generate the compact 2-column native Dash component tree for the LiDAR -> SAC Pipeline."""
    return html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(360px, 1fr))",
            "gap": "18px",
            "width": "100%",
            "maxHeight": "calc(88vh - 80px)",
            "overflowY": "auto",
            "padding": "4px",
            "color": "#1e293b",
            "boxSizing": "border-box",
        },
        children=[
            # LEFT COLUMN: Visual Images (LiDAR & SAC)
            html.Div(
                style={"display": "flex", "flexDirection": "column", "gap": "14px"},
                children=[
                    # Image 1: LiDAR Point Cloud
                    html.Div(
                        style={
                            "backgroundColor": "#0f172a",
                            "borderRadius": "12px",
                            "border": "2px solid #0284c7",
                            "overflow": "hidden",
                            "display": "flex",
                            "flexDirection": "column",
                            "boxShadow": "0 4px 14px rgba(0,0,0,0.25)",
                        },
                        children=[
                            html.Div(
                                style={
                                    "backgroundColor": "#1e293b",
                                    "padding": "8px 14px",
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "borderBottom": "1px solid #334155",
                                },
                                children=[
                                    html.Span(
                                        "📸 STEP 1: LIDAR RAW POINT CLOUD (.E57)",
                                        style={
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontSize": "12.5px",
                                            "fontWeight": "800",
                                            "color": "#38bdf8",
                                        },
                                    ),
                                    html.Span(
                                        "INPUT DATA",
                                        style={
                                            "fontSize": "10.5px",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontWeight": "800",
                                            "padding": "2px 7px",
                                            "borderRadius": "4px",
                                            "backgroundColor": "#0c4a6e",
                                            "color": "#7dd3fc",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "position": "relative",
                                    "height": "200px",
                                    "backgroundColor": "#020617",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "overflow": "hidden",
                                },
                                children=[
                                    html.Img(
                                        src=img_lidar,
                                        alt="LiDAR Point Cloud",
                                        style={"width": "100%", "height": "100%", "objectFit": "contain", "display": "block"},
                                    ) if img_lidar else html.Div("LiDAR Image Slot", style={"color": "#64748b", "fontSize": "13px"}),
                                    html.Div(
                                        "CloudCompare · ΔX/ΔY/ΔZ Extents · Coordinates",
                                        style={
                                            "position": "absolute",
                                            "bottom": "6px",
                                            "left": "8px",
                                            "backgroundColor": "rgba(15, 23, 42, 0.9)",
                                            "padding": "3px 8px",
                                            "borderRadius": "4px",
                                            "border": "1px solid #0284c7",
                                            "color": "#38bdf8",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontSize": "10.5px",
                                            "fontWeight": "700",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Image 2: SAC Reconstructed Mesh
                    html.Div(
                        style={
                            "backgroundColor": "#0f172a",
                            "borderRadius": "12px",
                            "border": "2px solid #10b981",
                            "overflow": "hidden",
                            "display": "flex",
                            "flexDirection": "column",
                            "boxShadow": "0 4px 14px rgba(0,0,0,0.25)",
                        },
                        children=[
                            html.Div(
                                style={
                                    "backgroundColor": "#1e293b",
                                    "padding": "8px 14px",
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "borderBottom": "1px solid #334155",
                                },
                                children=[
                                    html.Span(
                                        "📐 STEP 2: SAC RECONSTRUCTED 3D SURFACE MESH",
                                        style={
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontSize": "12.5px",
                                            "fontWeight": "800",
                                            "color": "#34d399",
                                        },
                                    ),
                                    html.Span(
                                        "PROCESSED MODEL",
                                        style={
                                            "fontSize": "10.5px",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontWeight": "800",
                                            "padding": "2px 7px",
                                            "borderRadius": "4px",
                                            "backgroundColor": "#064e3b",
                                            "color": "#6ee7b7",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "position": "relative",
                                    "height": "200px",
                                    "backgroundColor": "#020617",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "overflow": "hidden",
                                },
                                children=[
                                    html.Img(
                                        src=img_sac,
                                        alt="SAC Reconstructed Mesh",
                                        style={"width": "100%", "height": "100%", "objectFit": "contain", "display": "block"},
                                    ) if img_sac else html.Div("SAC Image Slot", style={"color": "#64748b", "fontSize": "13px"}),
                                    html.Div(
                                        "Blender 4.5 · Voxel Remesh: 0.15m · Watertight Manifold",
                                        style={
                                            "position": "absolute",
                                            "bottom": "6px",
                                            "left": "8px",
                                            "backgroundColor": "rgba(15, 23, 42, 0.9)",
                                            "padding": "3px 8px",
                                            "borderRadius": "4px",
                                            "border": "1px solid #10b981",
                                            "color": "#34d399",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontSize": "10.5px",
                                            "fontWeight": "700",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # RIGHT COLUMN: Short & Brief Executive Summary
            html.Div(
                style={"display": "flex", "flexDirection": "column", "gap": "12px"},
                children=[
                    # Card 1: Purpose & Connection
                    html.Div(
                        style={
                            "backgroundColor": "#ffffff",
                            "borderRadius": "12px",
                            "padding": "14px 16px",
                            "border": "1px solid #e2e8f0",
                            "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "6px",
                        },
                        children=[
                            html.Div(
                                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                                children=[
                                    html.Span(
                                        "🎯 PURPOSE: LIDAR ➔ SAC CONNECTION",
                                        style={"fontFamily": "'Barlow Semi Condensed', sans-serif", "fontSize": "13px", "fontWeight": "800", "color": "#0f172a", "letterSpacing": "0.5px"},
                                    ),
                                    html.Span(
                                        "CONFIDENCE > 0.83",
                                        style={"backgroundColor": "#dcfce7", "border": "1px solid #10b981", "color": "#047857", "padding": "2px 8px", "borderRadius": "6px", "fontFamily": "'Barlow Semi Condensed', sans-serif", "fontSize": "11px", "fontWeight": "800"},
                                    ),
                                ],
                            ),
                            html.P(
                                "LiDAR scans provide raw 3D coordinate points (X, Y, Z) but cannot directly yield surface area due to sensor noise, reflections, and blind spots. "
                                "The point cloud is transformed step-by-step into a watertight polygon mesh to calculate verified tank surface area.",
                                style={"fontSize": "12.5px", "lineHeight": "1.45", "color": "#334155", "margin": "0"},
                            ),
                        ],
                    ),

                    # Card 2: 3-Stage Software Pipeline
                    html.Div(
                        style={
                            "backgroundColor": "#ffffff",
                            "borderRadius": "12px",
                            "padding": "14px 16px",
                            "border": "1px solid #e2e8f0",
                            "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "8px",
                        },
                        children=[
                            html.Span(
                                "⚙️ 3-STAGE SOFTWARE WORKFLOW (STEPS 1–12)",
                                style={"fontFamily": "'Barlow Semi Condensed', sans-serif", "fontSize": "12.5px", "fontWeight": "800", "color": "#0f172a", "letterSpacing": "0.5px"},
                            ),
                            html.Div(
                                style={"display": "flex", "flexDirection": "column", "gap": "6px", "fontSize": "12px", "lineHeight": "1.4"},
                                children=[
                                    html.Div(
                                        [
                                            html.Strong("1. CloudCompare (Steps 1–4): ", style={"color": "#0369a1"}),
                                            "Opens .e57, computes surface normals (MST Plane), reconstructs Poisson mesh (octree depth 10/11), and filters noise via scalar-field density. Saves _RawMesh & _SFilter.",
                                        ],
                                        style={"backgroundColor": "#f0f9ff", "borderLeft": "3.5px solid #0284c7", "padding": "7px 10px", "borderRadius": "0 6px 6px 0", "color": "#1e293b"},
                                    ),
                                    html.Div(
                                        [
                                            html.Strong("2. Blender 4.5 (Steps 5–7): ", style={"color": "#15803d"}),
                                            "Imports .ply, sets origin to geometry, applies ",
                                            html.Strong("Voxel Remesh (0.15m)"),
                                            " for uniform manifold faces, and verifies 3D shell surface area. Saves _SFilter_Remesh.",
                                        ],
                                        style={"backgroundColor": "#f0fdf4", "borderLeft": "3.5px solid #16a34a", "padding": "7px 10px", "borderRadius": "0 6px 6px 0", "color": "#1e293b"},
                                    ),
                                    html.Div(
                                        [
                                            html.Strong("3. Developed Application (Steps 8–12): ", style={"color": "#c2410c"}),
                                            "Compares raw vs remeshed models, verifies boundary consistency, and certifies area calculation for MSC monthly reporting.",
                                        ],
                                        style={"backgroundColor": "#fff7ed", "borderLeft": "3.5px solid #ea580c", "padding": "7px 10px", "borderRadius": "0 6px 6px 0", "color": "#1e293b"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Card 3: Categorization & Acceptance Standard
                    html.Div(
                        style={
                            "backgroundColor": "#ffffff",
                            "borderRadius": "12px",
                            "padding": "12px 16px",
                            "border": "1px solid #e2e8f0",
                            "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "8px",
                        },
                        children=[
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "10px", "fontSize": "11.5px"},
                                children=[
                                    html.Div(
                                        style={"backgroundColor": "#f8fafc", "border": "1px solid #e2e8f0", "borderRadius": "8px", "padding": "8px 10px"},
                                        children=[
                                            html.Strong("🗂️ TANK CATEGORIZATION:", style={"color": "#0f172a", "fontFamily": "'Barlow Semi Condensed', sans-serif", "fontSize": "12px"}),
                                            html.Div("MSC Tanksdataset classified into Types A, B, C, D by geometric complexity.", style={"color": "#475569", "marginTop": "2px"}),
                                        ],
                                    ),
                                    html.Div(
                                        style={"backgroundColor": "#f8fafc", "border": "1px solid #e2e8f0", "borderRadius": "8px", "padding": "8px 10px"},
                                        children=[
                                            html.Strong("🏷️ NAMING & RULE:", style={"color": "#0f172a", "fontFamily": "'Barlow Semi Condensed', sans-serif", "fontSize": "12px"}),
                                            html.Div([
                                                html.Code("Dataset_TankName_OctreeDepth_ProcessStep"),
                                                html.Br(),
                                                html.Strong("Confidence > 0.83", style={"color": "#047857"}),
                                                " for acceptance.",
                                            ], style={"color": "#475569", "marginTop": "2px"}),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def generate_point_cloud_modal_html(img_lidar: str = "", img_sac: str = "") -> str:
    """Generate the short & brief 2-column HTML modal string for export_to_html.py."""
    return f"""
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:18px; width:100%; max-height:calc(88vh - 80px); overflow-y:auto; padding:4px; color:#1e293b; box-sizing:border-box;">
        
        <!-- LEFT COLUMN: Visual Images (LiDAR & SAC) -->
        <div style="display:flex; flex-direction:column; gap:14px;">
            <!-- Image 1: LiDAR Point Cloud -->
            <div style="background:#0f172a; border-radius:12px; border:2px solid #0284c7; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 4px 14px rgba(0,0,0,0.25);">
                <div style="background:#1e293b; padding:8px 14px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12.5px; font-weight:800; color:#38bdf8;">
                        📸 STEP 1: LIDAR RAW POINT CLOUD (.E57)
                    </span>
                    <span style="font-size:10.5px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; padding:2px 7px; border-radius:4px; background:#0c4a6e; color:#7dd3fc;">
                        INPUT DATA
                    </span>
                </div>
                <div style="position:relative; height:200px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden;">
                    {f'<img src="{img_lidar}" alt="LiDAR Point Cloud" style="width:100%; height:100%; object-fit:contain; display:block;" />' if img_lidar else '<div style="color:#64748b; font-size:13px;">LiDAR Image Slot</div>'}
                    <div style="position:absolute; bottom:6px; left:8px; background:rgba(15, 23, 42, 0.9); padding:3px 8px; border-radius:4px; border:1px solid #0284c7; color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; font-size:10.5px; font-weight:700;">
                        CloudCompare · ΔX/ΔY/ΔZ Extents · Coordinates
                    </div>
                </div>
            </div>

            <!-- Image 2: SAC Reconstructed Mesh -->
            <div style="background:#0f172a; border-radius:12px; border:2px solid #10b981; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 4px 14px rgba(0,0,0,0.25);">
                <div style="background:#1e293b; padding:8px 14px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12.5px; font-weight:800; color:#34d399;">
                        📐 STEP 2: SAC RECONSTRUCTED 3D SURFACE MESH
                    </span>
                    <span style="font-size:10.5px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; padding:2px 7px; border-radius:4px; background:#064e3b; color:#6ee7b7;">
                        PROCESSED MODEL
                    </span>
                </div>
                <div style="position:relative; height:200px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden;">
                    {f'<img src="{img_sac}" alt="SAC Reconstructed Mesh" style="width:100%; height:100%; object-fit:contain; display:block;" />' if img_sac else '<div style="color:#64748b; font-size:13px;">SAC Image Slot</div>'}
                    <div style="position:absolute; bottom:6px; left:8px; background:rgba(15, 23, 42, 0.9); padding:3px 8px; border-radius:4px; border:1px solid #10b981; color:#34d399; font-family:'Barlow Semi Condensed',sans-serif; font-size:10.5px; font-weight:700;">
                        Blender 4.5 · Voxel Remesh: 0.15m · Watertight Manifold
                    </div>
                </div>
            </div>
        </div>

        <!-- RIGHT COLUMN: Short & Brief Executive Summary -->
        <div style="display:flex; flex-direction:column; gap:12px;">
            <!-- Card 1: Purpose & Connection -->
            <div style="background:#ffffff; border-radius:12px; padding:14px 16px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,0.05); display:flex; flex-direction:column; gap:6px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800; color:#0f172a; letter-spacing:0.5px;">
                        🎯 PURPOSE: LIDAR ➔ SAC CONNECTION
                    </span>
                    <span style="background:#dcfce7; border:1px solid #10b981; color:#047857; padding:2px 8px; border-radius:6px; font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800;">
                        CONFIDENCE &gt; 0.83
                    </span>
                </div>
                <p style="font-size:12.5px; line-height:1.45; color:#334155; margin:0;">
                    LiDAR scans provide raw 3D coordinate points ($X,Y,Z$) but cannot directly yield surface area due to sensor noise, reflections, and blind spots. 
                    The point cloud is transformed step-by-step into a watertight polygon mesh to calculate verified tank surface area.
                </p>
            </div>

            <!-- Card 2: 3-Stage Software Pipeline -->
            <div style="background:#ffffff; border-radius:12px; padding:14px 16px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,0.05); display:flex; flex-direction:column; gap:8px;">
                <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12.5px; font-weight:800; color:#0f172a; letter-spacing:0.5px;">
                    ⚙️ 3-STAGE SOFTWARE WORKFLOW (STEPS 1–12)
                </span>
                <div style="display:flex; flex-direction:column; gap:6px; font-size:12px; line-height:1.4;">
                    <div style="background:#f0f9ff; border-left:3.5px solid #0284c7; padding:7px 10px; border-radius:0 6px 6px 0; color:#1e293b;">
                        <strong style="color:#0369a1;">1. CloudCompare (Steps 1–4):</strong> Opens <code>.e57</code>, computes surface normals (MST Plane), reconstructs Poisson mesh (octree depth 10/11), and filters noise using scalar field density. Saves <code>_RawMesh</code> &amp; <code>_SFilter</code>.
                    </div>
                    <div style="background:#f0fdf4; border-left:3.5px solid #16a34a; padding:7px 10px; border-radius:0 6px 6px 0; color:#1e293b;">
                        <strong style="color:#15803d;">2. Blender 4.5 (Steps 5–7):</strong> Imports <code>.ply</code>, sets origin to geometry, applies <strong>Voxel Remesh (0.15m)</strong> for uniform manifold faces, and checks 3D shell surface area. Saves <code>_SFilter_Remesh</code>.
                    </div>
                    <div style="background:#fff7ed; border-left:3.5px solid #ea580c; padding:7px 10px; border-radius:0 6px 6px 0; color:#1e293b;">
                        <strong style="color:#c2410c;">3. Developed Application (Steps 8–12):</strong> Compares raw vs remeshed models, verifies boundary consistency, and certifies area calculation for MSC monthly reporting.
                    </div>
                </div>
            </div>

            <!-- Card 3: Categorization & Acceptance Standard -->
            <div style="background:#ffffff; border-radius:12px; padding:12px 16px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,0.05); display:flex; flex-direction:column; gap:8px;">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:11.5px;">
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:8px 10px;">
                        <strong style="color:#0f172a; font-family:'Barlow Semi Condensed',sans-serif; font-size:12px;">🗂️ TANK CATEGORIZATION:</strong>
                        <div style="color:#475569; margin-top:2px;">
                            MSC <code>Tanksdataset</code> classified into <strong>Types A, B, C, D</strong> by geometric complexity.
                        </div>
                    </div>
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:8px 10px;">
                        <strong style="color:#0f172a; font-family:'Barlow Semi Condensed',sans-serif; font-size:12px;">🏷️ NAMING &amp; RULE:</strong>
                        <div style="color:#475569; margin-top:2px;">
                            <code>Dataset_TankName_OctreeDepth_ProcessStep</code><br/>
                            <strong style="color:#047857;">Rule: Confidence &gt; 0.83</strong> required for area certification.
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </div>
    """
