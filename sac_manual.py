"""Surface Area Calculation (SAC) Project Software Manual & Visual Comparison.
Provides both native Dash component trees and standalone HTML string generation
for the LiDAR Point Cloud -> SAC transformation pipeline.
"""
from typing import Optional
from dash import html

def build_point_cloud_pipeline_component(img_lidar: str = "", img_sac: str = "") -> html.Div:
    """Generate the full responsive native Dash component tree for the LiDAR Point Cloud -> SAC Pipeline.
    Uses pure Dash HTML components so no markdown parser or code block conversion can ever interfere.
    """
    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "gap": "20px",
            "width": "100%",
            "maxHeight": "calc(88vh - 120px)",
            "overflowY": "auto",
            "padding": "8px 12px 24px 6px",
            "color": "#1e293b",
            "boxSizing": "border-box",
        },
        children=[
            # Header Telemetry Card
            html.Div(
                style={
                    "background": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
                    "borderRadius": "14px",
                    "padding": "18px 22px",
                    "border": "1px solid #334155",
                    "color": "#ffffff",
                    "display": "flex",
                    "flexWrap": "wrap",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "gap": "16px",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                        children=[
                            html.Div(
                                style={"display": "flex", "alignItems": "center", "gap": "8px"},
                                children=[
                                    html.Span(
                                        "DATA PIPELINE",
                                        style={
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontSize": "11px",
                                            "fontWeight": "800",
                                            "letterSpacing": "1.2px",
                                            "backgroundColor": "#0284c7",
                                            "color": "#ffffff",
                                            "padding": "2px 8px",
                                            "borderRadius": "4px",
                                        },
                                    ),
                                    html.Span(
                                        "LIDAR SCANNING ➔ SURFACE AREA CALCULATION (SAC)",
                                        style={
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontSize": "12px",
                                            "color": "#94a3b8",
                                            "fontWeight": "700",
                                        },
                                    ),
                                ],
                            ),
                            html.H2(
                                "Point Cloud to Surface Mesh Transformation Pipeline",
                                style={
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "fontSize": "24px",
                                    "fontWeight": "800",
                                    "margin": "0",
                                    "color": "#f8fafc",
                                },
                            ),
                            html.P(
                                "Rigorous multi-stage software manual converting raw .e57 point clouds into validated watertight 3D meshes for tank surface area computation.",
                                style={"fontSize": "13px", "color": "#cbd5e1", "margin": "0", "lineHeight": "1.4"},
                            ),
                        ],
                    ),
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "alignItems": "flex-end", "gap": "6px"},
                        children=[
                            html.Div(
                                "🟢 ACCEPTANCE RULE: CONFIDENCE > 0.83",
                                style={
                                    "backgroundColor": "#064e3b",
                                    "border": "1.5px solid #10b981",
                                    "color": "#34d399",
                                    "padding": "6px 14px",
                                    "borderRadius": "8px",
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "fontSize": "12px",
                                    "fontWeight": "800",
                                    "letterSpacing": "0.5px",
                                },
                            ),
                            html.Span(
                                "Standardized Baseline: Steps 1–12 (All Tank Types)",
                                style={"fontSize": "11px", "color": "#94a3b8"},
                            ),
                        ],
                    ),
                ],
            ),

            # Dual Image Visual Showcase: LiDAR vs SAC Mesh
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(360px, 1fr))",
                    "gap": "18px",
                },
                children=[
                    # Card 1: LiDAR Point Cloud Capture
                    html.Div(
                        style={
                            "backgroundColor": "#0f172a",
                            "borderRadius": "14px",
                            "border": "2px solid #0284c7",
                            "overflow": "hidden",
                            "display": "flex",
                            "flexDirection": "column",
                            "boxShadow": "0 6px 20px rgba(0,0,0,0.25)",
                        },
                        children=[
                            html.Div(
                                style={
                                    "backgroundColor": "#1e293b",
                                    "padding": "10px 16px",
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
                                            "fontSize": "13px",
                                            "fontWeight": "800",
                                            "color": "#38bdf8",
                                        },
                                    ),
                                    html.Span(
                                        "INPUT DATA",
                                        style={
                                            "fontSize": "11px",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontWeight": "800",
                                            "padding": "2px 8px",
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
                                    "height": "320px",
                                    "backgroundColor": "#020617",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "overflow": "hidden",
                                },
                                children=[
                                    html.Img(
                                        src=img_lidar,
                                        alt="LiDAR Point Cloud Capture",
                                        style={"width": "100%", "height": "100%", "objectFit": "contain", "display": "block"},
                                    ) if img_lidar else html.Div("LiDAR Image Slot", style={"color": "#64748b", "fontSize": "13px"}),
                                    html.Div(
                                        "Distance & Coordinate Matrix · ΔX/ΔY/ΔZ Extents",
                                        style={
                                            "position": "absolute",
                                            "bottom": "10px",
                                            "left": "12px",
                                            "backgroundColor": "rgba(15, 23, 42, 0.9)",
                                            "padding": "4px 10px",
                                            "borderRadius": "6px",
                                            "border": "1px solid #0284c7",
                                            "color": "#38bdf8",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontSize": "11px",
                                            "fontWeight": "700",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "padding": "12px 16px",
                                    "backgroundColor": "#1e293b",
                                    "borderTop": "1px solid #334155",
                                    "fontSize": "12px",
                                    "color": "#cbd5e1",
                                    "lineHeight": "1.45",
                                },
                                children=[
                                    html.Strong("Raw LiDAR scan "),
                                    "delivered by MSC in ",
                                    html.Code("Tanksdataset", style={"backgroundColor": "#0f172a", "padding": "2px 6px", "borderRadius": "4px", "color": "#38bdf8"}),
                                    ". Millions of 3D spatial points with sensor noise and non-uniform density.",
                                ],
                            ),
                        ],
                    ),

                    # Card 2: SAC Reconstructed Surface Mesh
                    html.Div(
                        style={
                            "backgroundColor": "#0f172a",
                            "borderRadius": "14px",
                            "border": "2px solid #10b981",
                            "overflow": "hidden",
                            "display": "flex",
                            "flexDirection": "column",
                            "boxShadow": "0 6px 20px rgba(0,0,0,0.25)",
                        },
                        children=[
                            html.Div(
                                style={
                                    "backgroundColor": "#1e293b",
                                    "padding": "10px 16px",
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
                                            "fontSize": "13px",
                                            "fontWeight": "800",
                                            "color": "#34d399",
                                        },
                                    ),
                                    html.Span(
                                        "PROCESSED MODEL",
                                        style={
                                            "fontSize": "11px",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontWeight": "800",
                                            "padding": "2px 8px",
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
                                    "height": "320px",
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
                                        "Watertight Mesh · Voxel Remesh: 0.15m · Area Verified",
                                        style={
                                            "position": "absolute",
                                            "bottom": "10px",
                                            "left": "12px",
                                            "backgroundColor": "rgba(15, 23, 42, 0.9)",
                                            "padding": "4px 10px",
                                            "borderRadius": "6px",
                                            "border": "1px solid #10b981",
                                            "color": "#34d399",
                                            "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                            "fontSize": "11px",
                                            "fontWeight": "700",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "padding": "12px 16px",
                                    "backgroundColor": "#1e293b",
                                    "borderTop": "1px solid #334155",
                                    "fontSize": "12px",
                                    "color": "#cbd5e1",
                                    "lineHeight": "1.45",
                                },
                                children=[
                                    html.Strong("Cleaned manifold mesh "),
                                    "generated via CloudCompare (Poisson Recon & SF filter) and Blender 4.5. Continuous faces allow finite element area integration.",
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # Section 1: Purpose & The Engineering Challenge
            html.Div(
                style={
                    "backgroundColor": "#ffffff",
                    "borderRadius": "12px",
                    "padding": "18px 20px",
                    "border": "1px solid #e2e8f0",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "10px",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                        children=[
                            html.Span("🎯", style={"fontSize": "18px"}),
                            html.H3(
                                "Project Purpose: Why Raw Point Clouds Cannot Directly Yield Surface Area",
                                style={
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "fontSize": "18px",
                                    "fontWeight": "800",
                                    "color": "#0f172a",
                                    "margin": "0",
                                },
                            ),
                        ],
                    ),
                    html.P(
                        "The objective is to calculate the precise surface area of ship ballast tanks using high-definition LiDAR scanning. "
                        "However, raw point clouds cannot directly provide an accurate surface area because LiDAR returns are simply independent 3D coordinate points (X, Y, Z) without connected topology. Raw scans inherently contain:",
                        style={"fontSize": "13.5px", "lineHeight": "1.6", "color": "#334155", "margin": "0"},
                    ),
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))", "gap": "12px", "marginTop": "4px"},
                        children=[
                            html.Div(
                                style={"backgroundColor": "#f8fafc", "borderLeft": "3.5px solid #ef4444", "padding": "10px 14px", "borderRadius": "0 8px 8px 0", "fontSize": "12.5px", "color": "#475569"},
                                children=[
                                    html.Strong("1. Sensor Noise & Glare: ", style={"color": "#b91c1c"}),
                                    "High reflectivity off wet steel or standing water scatters scan points.",
                                ],
                            ),
                            html.Div(
                                style={"backgroundColor": "#f8fafc", "borderLeft": "3.5px solid #f59e0b", "padding": "10px 14px", "borderRadius": "0 8px 8px 0", "fontSize": "12.5px", "color": "#475569"},
                                children=[
                                    html.Strong("2. Shadowed Gaps: ", style={"color": "#d97706"}),
                                    "Stiffeners, brackets, and suction pipes create blind spots with missing points.",
                                ],
                            ),
                            html.Div(
                                style={"backgroundColor": "#f8fafc", "borderLeft": "3.5px solid #3b82f6", "padding": "10px 14px", "borderRadius": "0 8px 8px 0", "fontSize": "12.5px", "color": "#475569"},
                                children=[
                                    html.Strong("3. Density Gradients: ", style={"color": "#1d4ed8"}),
                                    "Far bulkheads exhibit sparse point spacing, while near dome areas are overdense.",
                                ],
                            ),
                            html.Div(
                                style={"backgroundColor": "#f8fafc", "borderLeft": "3.5px solid #10b981", "padding": "10px 14px", "borderRadius": "0 8px 8px 0", "fontSize": "12.5px", "color": "#475569"},
                                children=[
                                    html.Strong("4. Disconnected Points: ", style={"color": "#047857"}),
                                    "Area integration requires watertight polygon faces, not discrete coordinates.",
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # Section 2: Tank Categorization (Types A, B, C, D)
            html.Div(
                style={
                    "backgroundColor": "#ffffff",
                    "borderRadius": "12px",
                    "padding": "18px 20px",
                    "border": "1px solid #e2e8f0",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "10px",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                        children=[
                            html.Span("🗂️", style={"fontSize": "18px"}),
                            html.H3(
                                "Categorization of Tanks (Complexity Matrix)",
                                style={
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "fontSize": "18px",
                                    "fontWeight": "800",
                                    "color": "#0f172a",
                                    "margin": "0",
                                },
                            ),
                        ],
                    ),
                    html.P(
                        "Raw scan data delivered by MSC is cataloged in the Tanksdataset repository. "
                        "Because internal tank geometry varies widely, tanks are pre-classified into 4 complexity categories recorded in the Types of Tanks engineering matrix:",
                        style={"fontSize": "13.5px", "lineHeight": "1.6", "color": "#334155", "margin": "0"},
                    ),
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "10px", "marginTop": "4px"},
                        children=[
                            html.Div(
                                style={"backgroundColor": "#f8fafc", "border": "1px solid #e2e8f0", "borderRadius": "8px", "padding": "12px"},
                                children=[
                                    html.Div("TYPE A · SIMPLE", style={"fontFamily": "'Barlow Semi Condensed', sans-serif", "fontWeight": "800", "fontSize": "13px", "color": "#059669"}),
                                    html.Div("Flat planar boundary bulkheads with minimal structural obstruction. Straightforward Poisson reconstruction.", style={"fontSize": "12px", "color": "#475569", "marginTop": "4px"}),
                                ],
                            ),
                            html.Div(
                                style={"backgroundColor": "#f8fafc", "border": "1px solid #e2e8f0", "borderRadius": "8px", "padding": "12px"},
                                children=[
                                    html.Div("TYPE B · MODERATE", style={"fontFamily": "'Barlow Semi Condensed', sans-serif", "fontWeight": "800", "fontSize": "13px", "color": "#0284c7"}),
                                    html.Div("Contains standard vertical stiffeners and stringer frames. Requires selective SF density thresholding.", style={"fontSize": "12px", "color": "#475569", "marginTop": "4px"}),
                                ],
                            ),
                            html.Div(
                                style={"backgroundColor": "#f8fafc", "border": "1px solid #e2e8f0", "borderRadius": "8px", "padding": "12px"},
                                children=[
                                    html.Div("TYPE C · COMPLEX", style={"fontFamily": "'Barlow Semi Condensed', sans-serif", "fontWeight": "800", "fontSize": "13px", "color": "#d97706"}),
                                    html.Div("Deep corrugated bulkheads with longitudinal suction pipe runs. Higher octree depth (11) needed.", style={"fontSize": "12px", "color": "#475569", "marginTop": "4px"}),
                                ],
                            ),
                            html.Div(
                                style={"backgroundColor": "#f8fafc", "border": "1px solid #e2e8f0", "borderRadius": "8px", "padding": "12px"},
                                children=[
                                    html.Div("TYPE D · INTRICATE", style={"fontFamily": "'Barlow Semi Condensed', sans-serif", "fontWeight": "800", "fontSize": "13px", "color": "#dc2626"}),
                                    html.Div("Double bottom & hopper tanks with internal heating coils, wash bulkheads, and lightening holes (Steps 13+).", style={"fontSize": "12px", "color": "#475569", "marginTop": "4px"}),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # Section 3: The 3-Stage Software Workflow (Steps 1–12)
            html.Div(
                style={
                    "backgroundColor": "#ffffff",
                    "borderRadius": "12px",
                    "padding": "18px 20px",
                    "border": "1px solid #e2e8f0",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "14px",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                        children=[
                            html.Span("⚙️", style={"fontSize": "18px"}),
                            html.H3(
                                "Execution Workflow: Steps 1–12 Across the Three Software Tools",
                                style={
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "fontSize": "18px",
                                    "fontWeight": "800",
                                    "color": "#0f172a",
                                    "margin": "0",
                                },
                            ),
                        ],
                    ),

                    # Stage 1: CloudCompare
                    html.Div(
                        style={"border": "1px solid #bae6fd", "borderRadius": "10px", "padding": "16px", "backgroundColor": "#f0f9ff", "display": "flex", "flexDirection": "column", "gap": "10px"},
                        children=[
                            html.Div(
                                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "flexWrap": "wrap"},
                                children=[
                                    html.Span("STAGE 1: CLOUDCOMPARE (NORMALS COMPUTATION & POISSON RECONSTRUCTION)", style={"fontFamily": "'Barlow Semi Condensed', sans-serif", "fontSize": "15px", "fontWeight": "800", "color": "#0369a1"}),
                                    html.Span("STEPS 1 – 4", style={"fontSize": "11px", "fontWeight": "800", "backgroundColor": "#e0f2fe", "color": "#0284c7", "padding": "2px 8px", "borderRadius": "4px", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                                ],
                            ),
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "12px", "fontSize": "12.5px", "color": "#334155"},
                                children=[
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #e0f2fe"},
                                        children=[
                                            html.Strong("1. Compute Surface Normals: ", style={"color": "#0284c7"}),
                                            html.Ul(
                                                style={"margin": "6px 0 0 16px", "lineHeight": "1.5"},
                                                children=[
                                                    html.Li(["Open ", html.Code(".e57", style={"color": "#0369a1"}), " file and select the tank point cloud in DB tree."]),
                                                    html.Li("Edit > Normals > Compute with Plane as local surface model."),
                                                    html.Li("Octree: Auto · Orientation: Minimum Spanning Tree (MST)."),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #e0f2fe"},
                                        children=[
                                            html.Strong("2. Poisson Mesh Reconstruction: ", style={"color": "#0284c7"}),
                                            html.Ul(
                                                style={"margin": "6px 0 0 16px", "lineHeight": "1.5"},
                                                children=[
                                                    html.Li("Plugins > Poisson Recon with processed normals selected."),
                                                    html.Li("Octree Depth: 10 or 11 (balances detail vs scan noise)."),
                                                    html.Li("Enable Density / Scalar Field output to track confidence."),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #e0f2fe"},
                                        children=[
                                            html.Strong("3. Save Raw Binary Mesh: ", style={"color": "#0284c7"}),
                                            html.Ul(
                                                style={"margin": "6px 0 0 16px", "lineHeight": "1.5"},
                                                children=[
                                                    html.Li("Select reconstructed mesh in DB tree."),
                                                    html.Li(["Naming format: ", html.Code("Dataset_TankName_OctreeDepth_RawMesh")]),
                                                    html.Li("Save as binary CloudCompare file (.bin) for fast loading."),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #e0f2fe"},
                                        children=[
                                            html.Strong("4. Scalar Field Filtering: ", style={"color": "#0284c7"}),
                                            html.Ul(
                                                style={"margin": "6px 0 0 16px", "lineHeight": "1.5"},
                                                children=[
                                                    html.Li("Inspect SF Display Parameters slider (blue/green density)."),
                                                    html.Li("Edit > Scalar Fields > Filter by Value to purge noise/glare."),
                                                    html.Li(["Export cleaned mesh: ", html.Code("..._SFilter.ply")]),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Stage 2: Blender 4.5
                    html.Div(
                        style={"border": "1px solid #bbf7d0", "borderRadius": "10px", "padding": "16px", "backgroundColor": "#f0fdf4", "display": "flex", "flexDirection": "column", "gap": "10px"},
                        children=[
                            html.Div(
                                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "flexWrap": "wrap"},
                                children=[
                                    html.Span("STAGE 2: BLENDER 4.5 (VOXEL REMESHING & MANIFOLD REPAIR)", style={"fontFamily": "'Barlow Semi Condensed', sans-serif", "fontSize": "15px", "fontWeight": "800", "color": "#15803d"}),
                                    html.Span("STEPS 5 – 7", style={"fontSize": "11px", "fontWeight": "800", "backgroundColor": "#dcfce7", "color": "#16a34a", "padding": "2px 8px", "borderRadius": "4px", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                                ],
                            ),
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "12px", "fontSize": "12.5px", "color": "#334155"},
                                children=[
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #dcfce7"},
                                        children=[
                                            html.Strong("5. Import & Geometry Alignment: ", style={"color": "#16a34a"}),
                                            html.Ul(
                                                style={"margin": "6px 0 0 16px", "lineHeight": "1.5"},
                                                children=[
                                                    html.Li("File > Import > Stanford (.PLY) selecting SFilter file."),
                                                    html.Li("Apply Object > Set Origin > Origin to Geometry."),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #dcfce7"},
                                        children=[
                                            html.Strong("6. Voxel Remeshing: ", style={"color": "#16a34a"}),
                                            html.Ul(
                                                style={"margin": "6px 0 0 16px", "lineHeight": "1.5"},
                                                children=[
                                                    html.Li("Add Modifier > Generate > Remesh (Mode: Voxel)."),
                                                    html.Li(["Set ", html.Strong("Voxel Size = 0.15 m"), " for uniform polygon faces."]),
                                                    html.Li("Click Apply to commit watertight manifold geometry."),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #dcfce7"},
                                        children=[
                                            html.Strong("7. Shell Area Verification & Export: ", style={"color": "#16a34a"}),
                                            html.Ul(
                                                style={"margin": "6px 0 0 16px", "lineHeight": "1.5"},
                                                children=[
                                                    html.Li("Execute 3D > Check > Area for Shell."),
                                                    html.Li("Cross-reference area (m²) against MSC scantling envelope."),
                                                    html.Li(["Export Selection Only: ", html.Code("..._SFilter_Remesh.ply")]),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Stage 3: Developed Application
                    html.Div(
                        style={"border": "1px solid #fed7aa", "borderRadius": "10px", "padding": "16px", "backgroundColor": "#fff7ed", "display": "flex", "flexDirection": "column", "gap": "10px"},
                        children=[
                            html.Div(
                                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "flexWrap": "wrap"},
                                children=[
                                    html.Span("STAGE 3: DEVELOPED APPLICATION (CONFIDENCE EVALUATION & ACCEPTANCE CRITERIA)", style={"fontFamily": "'Barlow Semi Condensed', sans-serif", "fontSize": "15px", "fontWeight": "800", "color": "#c2410c"}),
                                    html.Span("STEPS 8 – 12", style={"fontSize": "11px", "fontWeight": "800", "backgroundColor": "#ffedd5", "color": "#ea580c", "padding": "2px 8px", "borderRadius": "4px", "fontFamily": "'Barlow Semi Condensed', sans-serif"}),
                                ],
                            ),
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "12px", "fontSize": "12.5px", "color": "#334155"},
                                children=[
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #ffedd5"},
                                        children=[
                                            html.Strong("8. Dual Dataset Load & Comparison: ", style={"color": "#ea580c"}),
                                            html.Ul(
                                                style={"margin": "6px 0 0 16px", "lineHeight": "1.5"},
                                                children=[
                                                    html.Li("Open developed Surface Calculation Application."),
                                                    html.Li("Load raw scan alongside remeshed model."),
                                                    html.Li("Execute comparison function to verify no shrinkage occurred."),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #ffedd5"},
                                        children=[
                                            html.Strong("9. Confidence Evaluation Rule: ", style={"color": "#ea580c"}),
                                            html.Div(
                                                style={"marginTop": "6px", "display": "flex", "flexDirection": "column", "gap": "6px"},
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.Strong("Confidence > 0.83: ACCEPTED!", style={"color": "#047857"}),
                                                            html.Br(),
                                                            "Mesh is validated as mathematically reliable. Accept surface area.",
                                                        ],
                                                        style={"backgroundColor": "#f0fdf4", "borderLeft": "3px solid #10b981", "padding": "6px 10px", "fontSize": "12px"},
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Strong("Confidence ≤ 0.83: REJECTED / REVISE", style={"color": "#b91c1c"}),
                                                            html.Br(),
                                                            "Return to step 10/11 to adjust SF filtering or octree depth.",
                                                        ],
                                                        style={"backgroundColor": "#fef2f2", "borderLeft": "3px solid #ef4444", "padding": "6px 10px", "fontSize": "12px"},
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style={"backgroundColor": "#ffffff", "padding": "12px", "borderRadius": "8px", "border": "1px solid #ffedd5"},
                                        children=[
                                            html.Strong("10. Batch Execution & MSC Reporting: ", style={"color": "#ea580c"}),
                                            html.Ul(
                                                style={"margin": "6px 0 0 16px", "lineHeight": "1.5"},
                                                children=[
                                                    html.Li("If confidence passes, initiate Start Batch for remaining tanks."),
                                                    html.Li(["Final certified output: ", html.Code("..._FinalArea")]),
                                                    html.Li("Monthly delivery to MSC: Comprehensive Word report & certified Excel spreadsheet."),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # Section 4: Standardized File Naming Convention Reference Table
            html.Div(
                style={
                    "backgroundColor": "#ffffff",
                    "borderRadius": "12px",
                    "padding": "18px 20px",
                    "border": "1px solid #e2e8f0",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "10px",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                        children=[
                            html.Span("🏷️", style={"fontSize": "18px"}),
                            html.H3(
                                "Standardized File Naming Convention & Lifecycle",
                                style={
                                    "fontFamily": "'Barlow Semi Condensed', sans-serif",
                                    "fontSize": "18px",
                                    "fontWeight": "800",
                                    "color": "#0f172a",
                                    "margin": "0",
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            "Every saved file throughout the entire pipeline must follow the strict format: ",
                            html.Code("Dataset_TankName_OctreeDepth_ProcessStep", style={"backgroundColor": "#f1f5f9", "padding": "2px 8px", "borderRadius": "4px", "color": "#0f172a", "fontWeight": "700"}),
                        ],
                        style={"fontSize": "12.5px", "color": "#475569", "lineHeight": "1.5"},
                    ),
                    html.Div(
                        style={"overflowX": "auto"},
                        children=[
                            html.Table(
                                style={"width": "100%", "borderCollapse": "collapse", "fontSize": "12.5px", "textAlign": "left"},
                                children=[
                                    html.Thead(
                                        html.Tr(
                                            style={"backgroundColor": "#f8fafc", "borderBottom": "2px solid #cbd5e1", "color": "#475569", "fontFamily": "'Barlow Semi Condensed', sans-serif"},
                                            children=[
                                                html.Th("PROCESSING STAGE", style={"padding": "10px 14px"}),
                                                html.Th("FILE NAME FORMAT", style={"padding": "10px 14px"}),
                                                html.Th("CONCRETE EXAMPLE", style={"padding": "10px 14px"}),
                                                html.Th("SOFTWARE TOOL", style={"padding": "10px 14px"}),
                                            ],
                                        )
                                    ),
                                    html.Tbody(
                                        [
                                            html.Tr(
                                                style={"borderBottom": "1px solid #e2e8f0"},
                                                children=[
                                                    html.Td("1. Raw Mesh", style={"padding": "10px 14px", "fontWeight": "700", "color": "#0369a1"}),
                                                    html.Td("Dataset_TankName_OctreeDepth_RawMesh", style={"padding": "10px 14px", "fontFamily": "monospace", "color": "#334155"}),
                                                    html.Td("Dataset01_TankA_Octree10_RawMesh", style={"padding": "10px 14px", "fontFamily": "monospace", "color": "#0284c7"}),
                                                    html.Td("CloudCompare (Poisson)", style={"padding": "10px 14px", "color": "#64748b"}),
                                                ],
                                            ),
                                            html.Tr(
                                                style={"borderBottom": "1px solid #e2e8f0", "backgroundColor": "#f8fafc"},
                                                children=[
                                                    html.Td("2. Scalar-Field Filtered", style={"padding": "10px 14px", "fontWeight": "700", "color": "#0284c7"}),
                                                    html.Td("Dataset_TankName_OctreeDepth_SFilter", style={"padding": "10px 14px", "fontFamily": "monospace", "color": "#334155"}),
                                                    html.Td("Dataset01_TankA_Octree10_SFilter", style={"padding": "10px 14px", "fontFamily": "monospace", "color": "#0284c7"}),
                                                    html.Td("CloudCompare (SF Filter)", style={"padding": "10px 14px", "color": "#64748b"}),
                                                ],
                                            ),
                                            html.Tr(
                                                style={"borderBottom": "1px solid #e2e8f0"},
                                                children=[
                                                    html.Td("3. Remeshed Mesh", style={"padding": "10px 14px", "fontWeight": "700", "color": "#15803d"}),
                                                    html.Td("Dataset_TankName_OctreeDepth_SFilter_Remesh", style={"padding": "10px 14px", "fontFamily": "monospace", "color": "#334155"}),
                                                    html.Td("Dataset01_TankA_Octree10_SFilter_Remesh", style={"padding": "10px 14px", "fontFamily": "monospace", "color": "#15803d"}),
                                                    html.Td("Blender 4.5 (Voxel 0.15m)", style={"padding": "10px 14px", "color": "#64748b"}),
                                                ],
                                            ),
                                            html.Tr(
                                                style={"backgroundColor": "#f0fdf4"},
                                                children=[
                                                    html.Td("4. Final Accepted Result", style={"padding": "10px 14px", "fontWeight": "800", "color": "#16a34a"}),
                                                    html.Td("Dataset_TankName_OctreeDepth_FinalArea", style={"padding": "10px 14px", "fontFamily": "monospace", "color": "#16a34a", "fontWeight": "700"}),
                                                    html.Td("Dataset01_TankA_Octree10_FinalArea", style={"padding": "10px 14px", "fontFamily": "monospace", "color": "#16a34a", "fontWeight": "700"}),
                                                    html.Td("Developed App (Conf > 0.83)", style={"padding": "10px 14px", "fontWeight": "700", "color": "#16a34a"}),
                                                ],
                                            ),
                                        ]
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
    """Generate the full responsive HTML modal for export_to_html.py standalone file."""
    return f"""
    <div style="display:flex; flex-direction:column; gap:20px; width:100%; max-height:calc(88vh - 120px); overflow-y:auto; padding:8px 12px 24px 6px; color:#1e293b;">
        <!-- Header Telemetry Card -->
        <div style="background:linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius:14px; padding:18px 22px; border:1px solid #334155; color:#ffffff; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:16px;">
            <div style="display:flex; flex-direction:column; gap:6px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; letter-spacing:1.2px; background:#0284c7; color:#ffffff; padding:2px 8px; border-radius:4px; text-transform:uppercase;">DATA PIPELINE</span>
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; color:#94a3b8; font-weight:700;">LIDAR SCANNING ➔ SURFACE AREA CALCULATION (SAC)</span>
                </div>
                <h2 style="font-family:'Barlow Semi Condensed',sans-serif; font-size:24px; font-weight:800; margin:0; color:#f8fafc;">
                    Point Cloud to Surface Mesh Transformation Pipeline
                </h2>
                <p style="font-size:13px; color:#cbd5e1; margin:0; line-height:1.4;">
                    Rigorous multi-stage software manual converting raw .e57 point clouds into validated watertight 3D meshes for tank surface area computation.
                </p>
            </div>
            <div style="display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
                <div style="background:#064e3b; border:1.5px solid #10b981; color:#34d399; padding:6px 14px; border-radius:8px; font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800; letter-spacing:0.5px;">
                    🟢 ACCEPTANCE RULE: CONFIDENCE &gt; 0.83
                </div>
                <span style="font-size:11px; color:#94a3b8; font-family:'Inter',sans-serif;">Standardized Baseline: Steps 1–12 (All Tank Types)</span>
            </div>
        </div>

        <!-- Dual Image Visual Showcase: LiDAR vs SAC Mesh -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:18px;">
            <!-- Card 1: LiDAR Point Cloud Capture -->
            <div style="background:#0f172a; border-radius:14px; border:2px solid #0284c7; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 6px 20px rgba(0,0,0,0.25);">
                <div style="background:#1e293b; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800; color:#38bdf8;">
                        📸 STEP 1: LIDAR RAW POINT CLOUD (.E57)
                    </span>
                    <span style="font-size:11px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; padding:2px 8px; border-radius:4px; background:#0c4a6e; color:#7dd3fc;">
                        INPUT DATA
                    </span>
                </div>
                <div style="position:relative; height:320px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden;">
                    {f'<img src="{img_lidar}" alt="LiDAR Point Cloud Capture" style="width:100%; height:100%; object-fit:contain; display:block;" />' if img_lidar else '<div style="color:#64748b; font-size:13px;">LiDAR Image Slot</div>'}
                    <div style="position:absolute; bottom:10px; left:12px; background:rgba(15, 23, 42, 0.9); padding:4px 10px; border-radius:6px; border:1px solid #0284c7; color:#38bdf8; font-family:\'Barlow Semi Condensed\',sans-serif; font-size:11px; font-weight:700;">
                        Distance &amp; Coordinate Matrix · ΔX/ΔY/ΔZ Extents
                    </div>
                </div>
                <div style="padding:12px 16px; background:#1e293b; border-top:1px solid #334155; font-size:12px; color:#cbd5e1; line-height:1.45;">
                    <strong>Raw LiDAR scan</strong> delivered by MSC in <code style="background:#0f172a; padding:2px 6px; border-radius:4px; color:#38bdf8;">Tanksdataset</code>. Millions of 3D spatial points with sensor noise and non-uniform density.
                </div>
            </div>

            <!-- Card 2: SAC Reconstructed Surface Mesh -->
            <div style="background:#0f172a; border-radius:14px; border:2px solid #10b981; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 6px 20px rgba(0,0,0,0.25);">
                <div style="background:#1e293b; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800; color:#34d399;">
                        📐 STEP 2: SAC RECONSTRUCTED 3D SURFACE MESH
                    </span>
                    <span style="font-size:11px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; padding:2px 8px; border-radius:4px; background:#064e3b; color:#6ee7b7;">
                        PROCESSED MODEL
                    </span>
                </div>
                <div style="position:relative; height:320px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden;">
                    {f'<img src="{img_sac}" alt="SAC Reconstructed Mesh" style="width:100%; height:100%; object-fit:contain; display:block;" />' if img_sac else '<div style="color:#64748b; font-size:13px;">SAC Image Slot</div>'}
                    <div style="position:absolute; bottom:10px; left:12px; background:rgba(15, 23, 42, 0.9); padding:4px 10px; border-radius:6px; border:1px solid #10b981; color:#34d399; font-family:\'Barlow Semi Condensed\',sans-serif; font-size:11px; font-weight:700;">
                        Watertight Mesh · Voxel Remesh: 0.15m · Area Verified
                    </div>
                </div>
                <div style="padding:12px 16px; background:#1e293b; border-top:1px solid #334155; font-size:12px; color:#cbd5e1; line-height:1.45;">
                    <strong>Cleaned manifold mesh</strong> generated via CloudCompare (Poisson Recon &amp; SF filter) and Blender 4.5. Continuous faces allow finite element area integration.
                </div>
            </div>
        </div>

        <!-- Section 1: Purpose & The Engineering Challenge -->
        <div style="background:#ffffff; border-radius:12px; padding:18px 20px; border:1px solid #e2e8f0; display:flex; flex-direction:column; gap:10px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:18px;">🎯</span>
                <h3 style="font-family:'Barlow Semi Condensed',sans-serif; font-size:18px; font-weight:800; color:#0f172a; margin:0;">
                    Project Purpose: Why Raw Point Clouds Cannot Directly Yield Surface Area
                </h3>
            </div>
            <p style="font-size:13.5px; line-height:1.6; color:#334155; margin:0;">
                The objective is to calculate the precise surface area of ship ballast tanks using high-definition LiDAR scanning. 
                However, raw point clouds <strong>cannot directly provide an accurate surface area</strong> because LiDAR returns are simply independent 3D coordinate points ($X, Y, Z$) without connected topology. Raw scans inherently contain:
            </p>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-top:4px;">
                <div style="background:#f8fafc; border-left:3.5px solid #ef4444; padding:10px 14px; border-radius:0 8px 8px 0; font-size:12.5px; color:#475569;">
                    <strong style="color:#b91c1c;">1. Sensor Noise &amp; Glare:</strong> High reflectivity off wet steel or standing water scatters scan points.
                </div>
                <div style="background:#f8fafc; border-left:3.5px solid #f59e0b; padding:10px 14px; border-radius:0 8px 8px 0; font-size:12.5px; color:#475569;">
                    <strong style="color:#d97706;">2. Shadowed Gaps:</strong> Stiffeners, brackets, and suction pipes create blind spots with missing points.
                </div>
                <div style="background:#f8fafc; border-left:3.5px solid #3b82f6; padding:10px 14px; border-radius:0 8px 8px 0; font-size:12.5px; color:#475569;">
                    <strong style="color:#1d4ed8;">3. Density Gradients:</strong> Far bulkheads exhibit sparse point spacing, while near dome areas are overdense.
                </div>
                <div style="background:#f8fafc; border-left:3.5px solid #10b981; padding:10px 14px; border-radius:0 8px 8px 0; font-size:12.5px; color:#475569;">
                    <strong style="color:#047857;">4. Disconnected Points:</strong> Area integration requires watertight polygon faces, not discrete coordinates.
                </div>
            </div>
        </div>

        <!-- Section 2: Tank Categorization -->
        <div style="background:#ffffff; border-radius:12px; padding:18px 20px; border:1px solid #e2e8f0; display:flex; flex-direction:column; gap:10px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:18px;">🗂️</span>
                <h3 style="font-family:'Barlow Semi Condensed',sans-serif; font-size:18px; font-weight:800; color:#0f172a; margin:0;">
                    Categorization of Tanks (Complexity Matrix)
                </h3>
            </div>
            <p style="font-size:13.5px; line-height:1.6; color:#334155; margin:0;">
                Raw scan data delivered by MSC is cataloged in the <code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; color:#0f172a;">Tanksdataset</code> repository. 
                Because internal tank geometry varies widely, tanks are pre-classified into 4 complexity categories recorded in the <code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; color:#0f172a;">Types of Tanks</code> engineering matrix:
            </p>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-top:4px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px;">
                    <div style="font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:13px; color:#059669;">TYPE A &middot; SIMPLE</div>
                    <div style="font-size:12px; color:#475569; margin-top:4px;">Flat planar boundary bulkheads with minimal structural obstruction. Straightforward Poisson reconstruction.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px;">
                    <div style="font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:13px; color:#0284c7;">TYPE B &middot; MODERATE</div>
                    <div style="font-size:12px; color:#475569; margin-top:4px;">Contains standard vertical stiffeners and stringer frames. Requires selective SF density thresholding.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px;">
                    <div style="font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:13px; color:#d97706;">TYPE C &middot; COMPLEX</div>
                    <div style="font-size:12px; color:#475569; margin-top:4px;">Deep corrugated bulkheads with longitudinal suction pipe runs. Higher octree depth (11) needed.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px;">
                    <div style="font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:13px; color:#dc2626;">TYPE D &middot; INTRICATE</div>
                    <div style="font-size:12px; color:#475569; margin-top:4px;">Double bottom &amp; hopper tanks with internal heating coils, wash bulkheads, and lightening holes (Steps 13+).</div>
                </div>
            </div>
        </div>

        <!-- Section 3: The 3-Stage Software Workflow -->
        <div style="background:#ffffff; border-radius:12px; padding:18px 20px; border:1px solid #e2e8f0; display:flex; flex-direction:column; gap:14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:18px;">⚙️</span>
                <h3 style="font-family:'Barlow Semi Condensed',sans-serif; font-size:18px; font-weight:800; color:#0f172a; margin:0;">
                    Execution Workflow: Steps 1–12 Across the Three Software Tools
                </h3>
            </div>

            <!-- Stage 1: CloudCompare -->
            <div style="border:1px solid #bae6fd; border-radius:10px; padding:16px; background:#f0f9ff; display:flex; flex-direction:column; gap:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:15px; font-weight:800; color:#0369a1;">
                        STAGE 1: CLOUDCOMPARE (NORMALS COMPUTATION &amp; POISSON RECONSTRUCTION)
                    </span>
                    <span style="font-size:11px; font-weight:800; background:#e0f2fe; color:#0284c7; padding:2px 8px; border-radius:4px; font-family:'Barlow Semi Condensed',sans-serif;">STEPS 1 – 4</span>
                </div>
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:12px; font-size:12.5px; color:#334155;">
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #e0f2fe;">
                        <strong style="color:#0284c7;">1. Compute Surface Normals:</strong>
                        <ul style="margin:6px 0 0 16px; line-height:1.5;">
                            <li>Open <code style="color:#0369a1;">.e57</code> file (<code>File &gt; Open</code>) and select the tank point cloud.</li>
                            <li>Go to <code>Edit &gt; Normals &gt; Compute</code>.</li>
                            <li>Local Surface Model: <strong>Plane</strong> (estimates surface orientation).</li>
                            <li>Octree: <strong>Auto</strong>; Orientation: <strong>Minimum Spanning Tree (MST)</strong> for uniform surface facing.</li>
                        </ul>
                    </div>
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #e0f2fe;">
                        <strong style="color:#0284c7;">2. Poisson Mesh Reconstruction:</strong>
                        <ul style="margin:6px 0 0 16px; line-height:1.5;">
                            <li>Select point cloud with computed normals (yellow border).</li>
                            <li>Open <code>Plugins &gt; PoissonRecon</code>.</li>
                            <li>Octree Depth: <strong>10 or 11</strong> (balances geometric resolution vs scan noise).</li>
                            <li>Enable <strong>Density Scalar Field</strong> output to track reconstruction confidence.</li>
                        </ul>
                    </div>
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #e0f2fe;">
                        <strong style="color:#0284c7;">3. Save Raw Binary Mesh:</strong>
                        <ul style="margin:6px 0 0 16px; line-height:1.5;">
                            <li>Select the reconstructed mesh in the CloudCompare DB tree.</li>
                            <li>Naming: <code>Dataset_TankName_OctreeDepth_RawMesh</code>.</li>
                            <li>Save as binary CloudCompare file (<code>.bin</code>) for fast loading.</li>
                        </ul>
                    </div>
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #e0f2fe;">
                        <strong style="color:#0284c7;">4. Scalar Field Filtering:</strong>
                        <ul style="margin:6px 0 0 16px; line-height:1.5;">
                            <li>Inspect <strong>SF Display Parameters</strong> slider (blue/green density range).</li>
                            <li><code>Edit &gt; Scalar Fields &gt; Filter by Value</code> to purge unreliable low-density noise.</li>
                            <li>Export cleaned model: <code>Dataset_TankName_OctreeDepth_SFilter.ply</code>.</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Stage 2: Blender 4.5 -->
            <div style="border:1px solid #bbf7d0; border-radius:10px; padding:16px; background:#f0fdf4; display:flex; flex-direction:column; gap:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:15px; font-weight:800; color:#15803d;">
                        STAGE 2: BLENDER 4.5 (VOXEL REMESHING &amp; MANIFOLD REPAIR)
                    </span>
                    <span style="font-size:11px; font-weight:800; background:#dcfce7; color:#16a34a; padding:2px 8px; border-radius:4px; font-family:'Barlow Semi Condensed',sans-serif;">STEPS 5 – 7</span>
                </div>
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:12px; font-size:12.5px; color:#334155;">
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #dcfce7;">
                        <strong style="color:#16a34a;">5. Import &amp; Geometry Alignment:</strong>
                        <ul style="margin:6px 0 0 16px; line-height:1.5;">
                            <li>Start Blender 4.5 and go to <code>File &gt; Import &gt; Stanford (.PLY)</code>.</li>
                            <li>Select <code>Dataset_TankName_OctreeDepth_SFilter.ply</code>.</li>
                            <li>Apply <code>Object &gt; Set Origin &gt; Origin to Geometry</code> to center transform matrix.</li>
                        </ul>
                    </div>
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #dcfce7;">
                        <strong style="color:#16a34a;">6. Voxel Remeshing:</strong>
                        <ul style="margin:6px 0 0 16px; line-height:1.5;">
                            <li>Add Modifier ➔ <code>Generate &gt; Remesh</code>.</li>
                            <li>Mode: <strong>Voxel</strong>.</li>
                            <li>Set <strong>Voxel Size = 0.15 m</strong> (creates uniform polygon face density).</li>
                            <li>Click <strong>Apply</strong> to commit manifold geometry.</li>
                        </ul>
                    </div>
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #dcfce7;">
                        <strong style="color:#16a34a;">7. Shell Area Verification &amp; Export:</strong>
                        <ul style="margin:6px 0 0 16px; line-height:1.5;">
                            <li>Select remeshed tank shell: <code>3D &gt; Check &gt; Area for Shell</code>.</li>
                            <li>Record surface area ($m^2$) and cross-reference against design limits.</li>
                            <li>Enable <strong>Selection Only</strong> and export to Stanford (.PLY).</li>
                            <li>Naming: <code>Dataset_TankName_OctreeDepth_SFilter_Remesh.ply</code>.</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Stage 3: Developed Surface Calculation Application -->
            <div style="border:1px solid #fed7aa; border-radius:10px; padding:16px; background:#fff7ed; display:flex; flex-direction:column; gap:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:15px; font-weight:800; color:#c2410c;">
                        STAGE 3: DEVELOPED APPLICATION (CONFIDENCE EVALUATION &amp; ACCEPTANCE CRITERIA)
                    </span>
                    <span style="font-size:11px; font-weight:800; background:#ffedd5; color:#ea580c; padding:2px 8px; border-radius:4px; font-family:'Barlow Semi Condensed',sans-serif;">STEPS 8 – 12</span>
                </div>
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:12px; font-size:12.5px; color:#334155;">
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #ffedd5;">
                        <strong style="color:#ea580c;">8. Dual Dataset Load &amp; Comparison:</strong>
                        <ul style="margin:6px 0 0 16px; line-height:1.5;">
                            <li>Open developed Surface Calculation Application.</li>
                            <li>Load raw scan <code>Dataset_TankName</code> alongside remeshed model <code>..._SFilter_Remesh</code>.</li>
                            <li>Execute comparison function to verify shell boundaries have not experienced shrinkage.</li>
                        </ul>
                    </div>
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #ffedd5;">
                        <strong style="color:#ea580c;">9. Confidence Evaluation Rule:</strong>
                        <div style="margin-top:6px; display:flex; flex-direction:column; gap:6px;">
                            <div style="background:#f0fdf4; border-left:3px solid #10b981; padding:6px 10px; font-size:12px;">
                                <strong style="color:#047857;">Confidence &gt; 0.83: ACCEPTED!</strong><br/>
                                Mesh is validated as mathematically reliable. Accept surface area.
                            </div>
                            <div style="background:#fef2f2; border-left:3px solid #ef4444; padding:6px 10px; font-size:12px;">
                                <strong style="color:#b91c1c;">Confidence &le; 0.83: REJECTED / REVISE</strong><br/>
                                Return to step 10/11 to adjust SF filtering or octree depth.
                            </div>
                        </div>
                    </div>
                    <div style="background:#ffffff; padding:12px; border-radius:8px; border:1px solid #ffedd5;">
                        <strong style="color:#ea580c;">10. Batch Execution &amp; MSC Reporting:</strong>
                        <ul style="margin:6px 0 0 16px; line-height:1.5;">
                            <li>If confidence passes, initiate <strong>Start Batch</strong> for remaining tanks.</li>
                            <li>Final certified output: <code>Dataset_TankName_OctreeDepth_FinalArea</code>.</li>
                            <li>Monthly delivery to MSC: One comprehensive Word document report and one certified Excel spreadsheet.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Section 4: Standardized File Naming Convention Reference Table -->
        <div style="background:#ffffff; border-radius:12px; padding:18px 20px; border:1px solid #e2e8f0; display:flex; flex-direction:column; gap:10px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:18px;">🏷️</span>
                <h3 style="font-family:'Barlow Semi Condensed',sans-serif; font-size:18px; font-weight:800; color:#0f172a; margin:0;">
                    Standardized File Naming Convention &amp; Lifecycle
                </h3>
            </div>
            <div style="font-size:12.5px; color:#475569; line-height:1.5;">
                Every saved file throughout the entire pipeline must follow the strict format: 
                <code style="background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#0f172a; font-weight:700;">Dataset_TankName_OctreeDepth_ProcessStep</code>
            </div>
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; font-size:12.5px; text-align:left;">
                    <thead>
                        <tr style="background:#f8fafc; border-bottom:2px solid #cbd5e1; color:#475569; font-family:'Barlow Semi Condensed',sans-serif;">
                            <th style="padding:10px 14px;">PROCESSING STAGE</th>
                            <th style="padding:10px 14px;">FILE NAME FORMAT</th>
                            <th style="padding:10px 14px;">CONCRETE EXAMPLE</th>
                            <th style="padding:10px 14px;">SOFTWARE TOOL</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom:1px solid #e2e8f0;">
                            <td style="padding:10px 14px; font-weight:700; color:#0369a1;">1. Raw Mesh</td>
                            <td style="padding:10px 14px; font-family:monospace; color:#334155;">Dataset_TankName_OctreeDepth_RawMesh</td>
                            <td style="padding:10px 14px; font-family:monospace; color:#0284c7;">Dataset01_TankA_Octree10_RawMesh</td>
                            <td style="padding:10px 14px; color:#64748b;">CloudCompare (Poisson)</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e2e8f0; background:#f8fafc;">
                            <td style="padding:10px 14px; font-weight:700; color:#0284c7;">2. Scalar-Field Filtered</td>
                            <td style="padding:10px 14px; font-family:monospace; color:#334155;">Dataset_TankName_OctreeDepth_SFilter</td>
                            <td style="padding:10px 14px; font-family:monospace; color:#0284c7;">Dataset01_TankA_Octree10_SFilter</td>
                            <td style="padding:10px 14px; color:#64748b;">CloudCompare (SF Filter)</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e2e8f0;">
                            <td style="padding:10px 14px; font-weight:700; color:#15803d;">3. Remeshed Mesh</td>
                            <td style="padding:10px 14px; font-family:monospace; color:#334155;">Dataset_TankName_OctreeDepth_SFilter_Remesh</td>
                            <td style="padding:10px 14px; font-family:monospace; color:#15803d;">Dataset01_TankA_Octree10_SFilter_Remesh</td>
                            <td style="padding:10px 14px; color:#64748b;">Blender 4.5 (Voxel 0.15m)</td>
                        </tr>
                        <tr style="background:#f0fdf4;">
                            <td style="padding:10px 14px; font-weight:800; color:#16a34a;">4. Final Accepted Result</td>
                            <td style="padding:10px 14px; font-family:monospace; color:#16a34a; font-weight:700;">Dataset_TankName_OctreeDepth_FinalArea</td>
                            <td style="padding:10px 14px; font-family:monospace; color:#16a34a; font-weight:700;">Dataset01_TankA_Octree10_FinalArea</td>
                            <td style="padding:10px 14px; font-weight:700; color:#16a34a;">Developed App (Conf &gt; 0.83)</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """
