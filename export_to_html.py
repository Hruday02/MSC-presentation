import os
import base64
from pathlib import Path
import story_app

def generate_html():
    # Load all images as base64
    img_data = {}
    for k, p in story_app.IMAGE_PATHS.items():
        if p and os.path.exists(p):
            try:
                ext = Path(p).suffix.lower().replace(".", "")
                mime = "image/svg+xml" if ext == "svg" else "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
                with open(p, "rb") as f:
                    img_data[k] = f"data:{mime};base64,{base64.b64encode(f.read()).decode('utf-8')}"
            except Exception as e:
                print(f"Warning loading {k}: {e}")
        else:
            img_data[k] = ""


    # Scan project's uploads/ directory for cross-system uploaded images
    uploads_dir = Path(__file__).parent / "uploads"
    if uploads_dir.is_dir():
        for cand in uploads_dir.iterdir():
            if cand.is_file() and cand.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
                k = cand.stem.lower()
                try:
                    ext = cand.suffix.lower().replace(".", "")
                    mime = "image/svg+xml" if ext == "svg" else "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
                    with open(cand, "rb") as fl:
                        b64 = base64.b64encode(fl.read()).decode("utf-8")
                        img_data[k] = f"data:{mime};base64,{b64}"
                        if k in ("samm", "lrms"):
                            img_data["samm"] = img_data[k]
                            img_data["lrms"] = img_data[k]
                        elif k in ("cms", "hms"):
                            img_data["cms"] = img_data[k]
                            img_data["hms"] = img_data[k]
                except Exception as ex:
                    print(f"Notice reading uploaded {cand}: {ex}")

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Twin Story Timeline</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background-color: #f8fafc;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #0f172a;
            -webkit-font-smoothing: antialiased;
            user-select: none;
            padding: 24px 32px 36px 32px;
            max-width: 1640px;
            margin: 0 auto;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            gap: 18px;
        }}

        /* App Header */
        header {{
            display: flex;
            justifyContent: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            background: #ffffff;
            padding: 20px 24px;
            border-radius: 14px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}
        .eyebrow {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: #2563eb;
        }}
        h1 {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: clamp(26px, 2.5vw, 34px);
            font-weight: 800;
            color: #0f172a;
            line-height: 1.15;
            margin-top: 2px;
        }}

        /* Phase Navigation Buttons */
        .phase-tabs {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .phase-tab-btn {{
            appearance: none;
            border: 1.5px solid #cbd5e1;
            background: #ffffff;
            color: #334155;
            border-radius: 10px;
            padding: 8px 16px;
            cursor: pointer;
            text-align: left;
            display: flex;
            flex-direction: column;
            gap: 2px;
            transition: all 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        .phase-tab-btn .p-num {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #64748b;
        }}
        .phase-tab-btn .p-title {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
        }}
        .phase-tab-btn:hover {{
            border-color: #2563eb;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
        }}
        .phase-tab-btn.active {{
            background: #eff6ff;
            border-color: #2563eb;
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
        }}
        .phase-tab-btn.active .p-num {{ color: #2563eb; }}
        .phase-tab-btn.active .p-title {{ color: #1d4ed8; font-weight: 800; }}

        /* Main Workspace Grid */
        main {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) 420px;
            gap: 20px;
            flex: 1;
        }}
        @media (max-width: 1080px) {{
            main {{ grid-template-columns: 1fr; }}
        }}

        /* Stage & Drafting Sheet Aesthetics */
        .stage {{
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
            display: flex;
            flex-direction: column;
        }}
        .stage svg {{
            width: 100%;
            height: 100%;
            display: block;
            touch-action: manipulation;
        }}
        .hint {{
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
        }}

        /* Phase 3 View Mode Toggle Header */
        .view-mode-bar {{
            display: none;
            background: #ffffff;
            padding: 10px 18px;
            border-bottom: 1px solid #e2e8f0;
            justify-content: space-between;
            align-items: center;
        }}
        .mode-btn {{
            padding: 6px 14px;
            border-radius: 8px;
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            border: 1.5px solid #cbd5e1;
            background: #ffffff;
            color: #475569;
            transition: all 0.2s;
        }}
        .mode-btn.active {{
            background: #2563eb;
            color: #ffffff;
            border-color: #2563eb;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
        }}

        /* Simulation Canvas Viewport */
        .sim-viewport {{
            display: none;
            flex-direction: column;
            width: 100%;
            height: 100%;
            background: #030712;
            padding: 18px;
            gap: 12px;
            overflow-y: auto;
        }}
        .sim-action-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #1e293b;
            padding: 10px 16px;
            border-radius: 10px;
            border: 1px solid #334155;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .sim-action-btn {{
            padding: 8px 18px;
            border-radius: 8px;
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 13px;
            font-weight: 800;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s;
        }}
        .btn-rust {{ background: #450a0a; color: #f87171; border-color: #ef4444; }}
        .btn-rust.active {{ background: #ef4444; color: #ffffff; box-shadow: 0 0 14px rgba(239, 68, 68, 0.45); }}
        .btn-clean {{ background: #064e3b; color: #34d399; border-color: #10b981; }}
        .btn-clean.active {{ background: #10b981; color: #ffffff; box-shadow: 0 0 14px rgba(16, 185, 129, 0.45); }}

        /* SVG Nodes & Elements */
        .node {{ cursor: pointer; }}
        .node .body {{
            stroke-width: 2.5px;
            transition: stroke-width .22s cubic-bezier(0.34, 1.56, 0.64, 1), filter .22s ease, stroke .22s ease;
        }}
        .node:hover .body {{
            stroke-width: 3.5px;
            filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.12));
        }}
        .node.selected .body {{
            stroke: #d97706 !important;
            stroke-width: 5.5px !important;
            filter: drop-shadow(0 0 12px rgba(245, 158, 11, 0.65));
        }}
        .node .glow-ring {{
            fill: none;
            stroke: #f59e0b;
            stroke-width: 4px;
            opacity: 0;
            transition: opacity .25s ease;
        }}
        .node.selected .glow-ring {{
            opacity: 0.55;
            animation: nodePulse 2s infinite ease-in-out;
        }}
        @keyframes nodePulse {{
            0%, 100% {{ stroke-width: 4px; opacity: 0.55; }}
            50% {{ stroke-width: 7px; opacity: 0.25; }}
        }}

        .node .label {{
            font-family: 'Barlow Semi Condensed', 'Arial Narrow', sans-serif;
            font-weight: 700;
            font-size: 13.5px;
            fill: #0f172a;
            text-anchor: middle;
            pointer-events: none;
        }}
        .node .sub {{
            font-family: 'Barlow Semi Condensed', 'Arial Narrow', sans-serif;
            font-weight: 600;
            font-size: 11px;
            fill: #64748b;
            text-anchor: middle;
            pointer-events: none;
        }}
        .node.k-samm .label, .node.k-cms .label {{ fill: #ffffff; }}
        .node.k-samm .sub, .node.k-cms .sub {{ fill: rgba(255, 255, 255, 0.95); }}
        .node.k-samm .sub {{ font-size: 7.8px; font-weight: 700; letter-spacing: -0.2px; }}
        .node.k-cms .sub {{ font-size: 8.5px; font-weight: 700; letter-spacing: -0.2px; }}

        .dim {{ opacity: 0.20 !important; transition: opacity .3s ease; }}
        .node, .edge, .group-box {{ transition: opacity .3s ease; }}

        /* Edges */
        .clickable-pipeline-edge {{
            cursor: pointer;
        }}
        .clickable-pipeline-edge .elabel-bg {{
            transition: all 0.2s ease;
        }}
        .clickable-pipeline-edge:hover .edge-path {{
            stroke: #0284c7 !important;
            stroke-width: 3.5px !important;
            filter: drop-shadow(0 0 10px rgba(2, 132, 199, 0.75));
        }}
        .clickable-pipeline-edge:hover .elabel-bg {{
            fill: #0284c7 !important;
            stroke: #38bdf8 !important;
        }}
        .clickable-pipeline-edge:hover .elabel {{
            fill: #ffffff !important;
            font-weight: 800 !important;
        }}

        .edge path {{
            stroke: #2563eb;
            stroke-width: 2.5px;
            fill: none;
            transition: stroke 0.25s, stroke-width 0.25s;
        }}
        .edge.feedback path {{
            stroke: #94a3b8;
            stroke-width: 2px;
            stroke-dasharray: 6 4;
        }}
        .edge.hot path {{
            stroke: #d97706 !important;
            stroke-width: 4px !important;
        }}
        .edge .elabel {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 10.5px;
            font-weight: 700;
            fill: #1e293b;
            text-anchor: middle;
            pointer-events: none;
        }}
        .edge .elabel-bg {{
            fill: #ffffff;
            stroke: #cbd5e1;
            stroke-width: 1px;
            rx: 4px;
        }}
        .edge.hot .elabel {{ fill: #b45309; }}
        .edge.hot .elabel-bg {{ stroke: #f59e0b; fill: #fffbeb; }}

        /* Group Boxes */
        .group-box {{ pointer-events: none; }}
        .group-box rect.group-bg {{ stroke-dasharray: 6 4; stroke-width: 2px; }}
        .group-box text.group-title {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-weight: 800;
            font-size: 13px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            text-anchor: middle;
        }}

        /* Notes Sidebar */
        .notes-panel {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
            overflow-y: auto;
        }}
        .notes-tag {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: #2563eb;
        }}
        .notes-title {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 26px;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.15;
        }}
        .notes-desc {{
            font-size: 14px;
            line-height: 1.55;
            color: #334155;
            background: #f8fafc;
            padding: 14px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }}
        .pill-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 4px;
        }}
        .node-pill {{
            font-size: 12.5px;
            padding: 6px 12px;
            border-radius: 8px;
            background: #f1f5f9;
            color: #0f172a;
            border: 1px solid #cbd5e1;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .node-pill:hover {{
            background: #e2e8f0;
            border-color: #2563eb;
            color: #2563eb;
        }}

        .inspect-action-btn {{
            margin-top: 6px;
            padding: 12px 16px;
            background: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 15px;
            font-weight: 800;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s;
        }}
        .inspect-action-btn:hover {{
            background: #1d4ed8;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
        }}

        .footer-nav {{
            margin-top: auto;
            display: flex;
            gap: 10px;
            padding-top: 10px;
        }}
        .nav-btn {{
            flex: 1;
            padding: 11px 14px;
            border-radius: 10px;
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 14.5px;
            font-weight: 700;
            cursor: pointer;
            border: 1.5px solid #cbd5e1;
            background: #ffffff;
            color: #0f172a;
        }}
        .nav-btn.primary {{
            background: #2563eb;
            border-color: #2563eb;
            color: #ffffff;
            font-weight: 800;
        }}
        .nav-btn:disabled {{
            opacity: 0.35;
            cursor: default;
        }}

        /* Full Screen Modal Viewport with Smooth Physics Animation */
        .modal-overlay {{
            display: flex;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.28s cubic-bezier(0.16, 1, 0.3, 1);
            position: fixed;
            inset: 0;
            background: rgba(2, 6, 23, 0.88);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 24px;
        }}
        .modal-overlay.active {{
            opacity: 1;
            pointer-events: auto;
        }}
        .modal-card {{
            background: #020617;
            border: 1.5px solid #334155;
            border-radius: 16px;
            width: 100%;
            max-width: 1280px;
            max-height: 94vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.85);
            transform: scale(0.95) translateY(14px);
            transition: transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        .modal-overlay.active .modal-card {{
            transform: scale(1) translateY(0);
        }}

        /* Smooth View Transitions */
        .view-enter-anim {{
            animation: viewFadeSlide 0.38s cubic-bezier(0.16, 1, 0.3, 1) both;
        }}
        @keyframes viewFadeSlide {{
            0% {{
                opacity: 0;
                transform: translateY(12px) scale(0.995);
            }}
            100% {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}

        /* Notes Panel Slide In */
        .panel-slide-anim {{
            animation: panelSlideIn 0.32s cubic-bezier(0.16, 1, 0.3, 1) both;
        }}
        @keyframes panelSlideIn {{
            0% {{
                opacity: 0;
                transform: translateX(14px);
            }}
            100% {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        /* Laser Scanner Beam Sweep across Tank */
        .scanner-beam {{
            position: absolute;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.95), rgba(249, 115, 22, 0.95), transparent);
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.9), 0 0 32px rgba(249, 115, 22, 0.7);
            opacity: 0;
            pointer-events: none;
            z-index: 10;
        }}
        .active-sweep {{
            animation: sweepAnimation 1.1s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }}
        .dt-active-sweep {{
            animation: sweepAnimation 1.1s 0.22s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }}
        @keyframes sweepAnimation {{
            0% {{ top: 12%; opacity: 0; }}
            20% {{ opacity: 0.95; }}
            80% {{ opacity: 0.95; }}
            100% {{ top: 88%; opacity: 0; }}
        }}

        /* Pulsing Alert Badge */
        @keyframes alertPulseGlow {{
            0%, 100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); }}
            50% {{ box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }}
        }}
        .pulse-alert-badge {{
            animation: alertPulseGlow 2s infinite ease-in-out;
        }}
        .modal-header {{
            background: #1e293b;
            padding: 16px 24px;
            border-bottom: 1px solid #334155;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .modal-title-text {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
        }}
        .modal-close {{
            background: none;
            border: none;
            color: #94a3b8;
            font-size: 28px;
            cursor: pointer;
            line-height: 1;
        }}
        .modal-close:hover {{ color: #ffffff; }}

        .modal-body {{
            padding: 24px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            background: #020617;
            overflow-y: auto;
            max-height: calc(94vh - 75px);
            min-height: 480px;
        }}
        .modal-body img {{
            max-width: 100%;
            max-height: calc(88vh - 130px);
            object-fit: contain;
            border-radius: 12px;
            border: 1.5px solid #1e293b;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.8);
            display: block;
            margin: auto;
        }}

        /* Clean Image Slot (No mock telemetry, only space for the image) */
        .image-slot-container {{
            border: 2px dashed #334155;
            border-radius: 16px;
            padding: 56px 36px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 16px;
            background: #0b0f19;
            max-width: 720px;
            width: 100%;
        }}
        .image-slot-container h3 {{
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 22px;
            font-weight: 800;
            color: #f8fafc;
        }}
        .image-slot-container p {{
            font-size: 13.5px;
            color: #94a3b8;
            max-width: 500px;
        }}
        .image-slot-container .code-badge {{
            font-size: 12px;
            font-family: monospace;
            background: #030712;
            color: #38bdf8;
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid #1e293b;
        }}
    </style>
</head>
<body>

<!-- Header -->
<header>
    <div>
        <div class="eyebrow">MSC BALLAST TANK DIGITAL TWIN &middot; PROOF OF CONCEPT</div>
        <h1>From separate projects to one digital twin</h1>
    </div>
    <div class="phase-tabs" id="phase-tabs"></div>
</header>

<!-- Main Grid -->
<main>
    <!-- Left Stage -->
    <section class="stage">
        <!-- Phase 3 View Mode Bar -->
        <div class="view-mode-bar" id="view-mode-bar">
            <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800; color:#64748b; letter-spacing:1px;">PHASE 3 VIEW:</span>
            <div style="display:flex; gap:8px;">
                <button class="mode-btn active" id="btn-mode-graph">Architecture Graph</button>
                <button class="mode-btn" id="btn-mode-sim">🚢 Ship &amp; Ballast Tank Simulation</button>
            </div>
        </div>

        <!-- Diagram SVG Mount -->
        <div id="svg-diagram-mount" style="width:100%; height:100%; position:relative;">
            <svg id="svg" viewBox="0 0 1000 620" preserveAspectRatio="xMidYMid meet">
                <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M 0 1 L 9 5 L 0 9 z" fill="#2563eb"/></marker>
                    <marker id="arrow-start" viewBox="0 0 10 10" refX="1" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto"><path d="M 9 1 L 0 5 L 9 9 z" fill="#2563eb"/></marker>
                    <marker id="arrow-feedback" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M 0 1 L 9 5 L 0 9 z" fill="#94a3b8"/></marker>
                    <marker id="arrow-hot" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" orient="auto-start-reverse"><path d="M 0 1 L 9 5 L 0 9 z" fill="#d97706"/></marker>
                    <marker id="arrow-start-hot" viewBox="0 0 10 10" refX="1" refY="5" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" orient="auto"><path d="M 9 1 L 0 5 L 9 9 z" fill="#d97706"/></marker>
                </defs>
                <g id="groups"></g>
                <g id="edges"></g>
                <g id="nodes"></g>
                <!-- ======================================================== -->
                <!-- PHASE 4.5: AST SYSTEM MODEL & MBSE ARCHITECTURE BLUEPRINT -->
                <!-- Scaled & Compacted to fit strictly within Y <= 504        -->
                <!-- ======================================================== -->
    <!-- ======================================================== -->
    <!-- PHASE 4.5: AST SYSTEM MODEL                                -->
    <!-- Direct, authentic visualization of the AST System Model    -->
    <!-- No fabricated details; no link between SAC and VTL        -->
    <!-- ======================================================== -->
    <g id="phase45-placeholder" style="display:none;">
        <!-- Canvas Title -->
        <text x="36" y="38" font-family="'Barlow Semi Condensed', sans-serif" font-size="26" font-weight="800" fill="#0f172a">AST System Model</text>

        <!-- ========================================================= -->
        <!-- LEFT: THREE TIERS WITH PERSISTENCE & ALGEDONIC BUSES       -->
        <!-- ========================================================= -->
        <!-- Persistence Arrow (Left, pointing DOWN) -->
        <g id="p45-bus-persistence">
            <rect x="36" y="58" width="22" height="392" rx="4" fill="#0f2942" stroke="#1e3a5f" stroke-width="1"/>
            <polygon points="31,450 63,450 47,476" fill="#0f2942" stroke="#1e3a5f" stroke-width="1"/>
            <text x="47" y="80" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">P</text>
            <text x="47" y="116" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">e</text>
            <text x="47" y="152" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">r</text>
            <text x="47" y="188" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">s</text>
            <text x="47" y="224" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">i</text>
            <text x="47" y="260" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">s</text>
            <text x="47" y="296" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">t</text>
            <text x="47" y="332" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">e</text>
            <text x="47" y="368" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">n</text>
            <text x="47" y="404" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">c</text>
            <text x="47" y="440" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">e</text>
        </g>

        <!-- Tier 1: Ontology Semantic Representation (Orange) -->
        <g id="p45-tier-1" style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
            <rect x="70" y="58" width="374" height="132" rx="8" fill="#ffffff" stroke="#fdba74" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.03))" />
            <rect x="70" y="58" width="374" height="32" rx="8" fill="#fff7ed" stroke="#fdba74" stroke-width="1" />
            <rect x="70" y="78" width="374" height="12" fill="#fff7ed" />
            <!-- Number badge -->
            <rect x="78" y="64" width="20" height="20" rx="4" fill="#ea580c" />
            <text x="88" y="78" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">1</text>
            <!-- Title -->
            <text x="106" y="79" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800" fill="#9a3412">Ontology Semantic Representation</text>
            <!-- Verbatim Slide Body Text -->
            <text x="82" y="106" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">Encodes system entities, their relationships, and constraints in a formal</text>
            <text x="82" y="122" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">semantic model. Answers the question: what exists in this system and</text>
            <text x="82" y="138" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">how do system relationships, dependencies, and decision objectives</text>
            <text x="82" y="154" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">connect to one another?</text>
        </g>

        <!-- Tier 2: Taxonomy Hierarchical Classification (Medium Blue) -->
        <g id="p45-tier-2" style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
            <rect x="70" y="200" width="374" height="132" rx="8" fill="#ffffff" stroke="#bae6fd" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.03))" />
            <rect x="70" y="200" width="374" height="32" rx="8" fill="#f0f9ff" stroke="#bae6fd" stroke-width="1" />
            <rect x="70" y="220" width="374" height="12" fill="#f0f9ff" />
            <!-- Number badge -->
            <rect x="78" y="206" width="20" height="20" rx="4" fill="#0284c7" />
            <text x="88" y="220" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">2</text>
            <!-- Title -->
            <text x="106" y="221" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800" fill="#0369a1">Taxonomy Hierarchical Classification</text>
            <!-- Verbatim Slide Body Text -->
            <text x="82" y="248" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">Organizes system elements into typed classes with inheritance. Enables</text>
            <text x="82" y="264" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">structured reasoning about failure modes, behaviors, and decision</text>
            <text x="82" y="280" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">categories across levels of abstraction.</text>
        </g>

        <!-- Tier 3: Schema Data Structure and Relational Encoding (Cyan / Teal) -->
        <g id="p45-tier-3" style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
            <rect x="70" y="342" width="374" height="132" rx="8" fill="#ffffff" stroke="#99f6e4" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.03))" />
            <rect x="70" y="342" width="374" height="32" rx="8" fill="#f0fdfa" stroke="#99f6e4" stroke-width="1" />
            <rect x="70" y="362" width="374" height="12" fill="#f0fdfa" />
            <!-- Number badge -->
            <rect x="78" y="348" width="20" height="20" rx="4" fill="#0d9488" />
            <text x="88" y="362" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">3</text>
            <!-- Title -->
            <text x="106" y="363" font-family="'Barlow Semi Condensed', sans-serif" font-size="13" font-weight="800" fill="#0f766e">Schema Data Structure and Relational Encoding</text>
            <!-- Verbatim Slide Body Text -->
            <text x="82" y="390" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">Translates ontological and taxonomic knowledge into structured, queryable,</text>
            <text x="82" y="406" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">and traceable data linked to system requirements and observed states.</text>
            <text x="82" y="422" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">Establishes traceability links between system states, requirements,</text>
            <text x="82" y="438" font-family="'Inter', sans-serif" font-size="10.2" fill="#1e293b">and observations.</text>
        </g>

        <!-- Algedonic Arrow (Right, pointing UP) -->
        <g id="p45-bus-algedonic">
            <polygon points="449,84 481,84 465,58" fill="#0f2942" stroke="#1e3a5f" stroke-width="1"/>
            <rect x="454" y="84" width="22" height="392" rx="4" fill="#0f2942" stroke="#1e3a5f" stroke-width="1"/>
            <text x="465" y="118" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">A</text>
            <text x="465" y="158" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">l</text>
            <text x="465" y="198" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">g</text>
            <text x="465" y="238" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">e</text>
            <text x="465" y="278" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">d</text>
            <text x="465" y="318" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">o</text>
            <text x="465" y="358" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">n</text>
            <text x="465" y="398" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">i</text>
            <text x="465" y="438" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">c</text>
        </g>

        <!-- ========================================================= -->
        <!-- CENTER: BIDIRECTIONAL CONNECTOR                            -->
        <!-- ========================================================= -->
        <g id="p45-double-arrow">
            <polygon points="492,266 502,256 502,262 522,262 522,256 532,266 522,276 522,270 502,270 502,276" fill="#10b981" stroke="#059669" stroke-width="1.5" />
        </g>

        <!-- ========================================================= -->
        <!-- RIGHT TOP: SYSTEM NODES RUNTIME ARCHITECTURE               -->
        <!-- NO LINK BETWEEN SAC AND VTL                               -->
        <!-- ========================================================= -->
        <g id="p45-runtime-nodes">
            <!-- Connecting Paths -->
            <!-- LIDAR -> SAC -->
            <path d="M 584 92 L 584 108" fill="none" stroke="#64748b" stroke-width="1.5"/>
            <polygon points="581,104 584,111 587,104" fill="#64748b"/>

            <!-- SAC -> DT (Direct connection, NO link between SAC and VTL!) -->
            <path d="M 628 126 C 656 126, 656 181, 684 181" fill="none" stroke="#2563eb" stroke-width="1.5"/>
            <polygon points="680,178 687,181 680,184" fill="#2563eb"/>

            <!-- VTL -> DT (Direct connection) -->
            <path d="M 628 181 L 684 181" fill="none" stroke="#2563eb" stroke-width="1.5"/>
            <polygon points="680,178 687,181 680,184" fill="#2563eb"/>

            <!-- Hyper -> Tank -->
            <path d="M 728 92 L 728 108" fill="none" stroke="#64748b" stroke-width="1.5"/>
            <polygon points="725,104 728,111 731,104" fill="#64748b"/>

            <!-- RGB/Video -> Tank -->
            <path d="M 872 92 L 872 126 L 772 126" fill="none" stroke="#64748b" stroke-width="1.5"/>
            <polygon points="776,123 768,126 776,129" fill="#64748b"/>

            <!-- Tank <==> DT Bidirectional Sync -->
            <line x1="728" y1="144" x2="728" y2="163" stroke="#0284c7" stroke-width="2"/>
            <polygon points="724,148 728,141 732,148" fill="#0284c7"/>
            <polygon points="724,159 728,166 732,159" fill="#0284c7"/>

            <!-- DT -> SAMM & DT -> CMS -->
            <path d="M 772 181 L 805 181 L 805 126 L 828 126" fill="none" stroke="#64748b" stroke-width="1.5"/>
            <polygon points="824,123 831,126 824,129" fill="#64748b"/>

            <path d="M 772 181 L 828 181" fill="none" stroke="#16a34a" stroke-width="1.5"/>
            <polygon points="824,178 831,181 824,184" fill="#16a34a"/>

            <!-- Nodes -->
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
                <rect x="540" y="110" width="88" height="34" rx="6" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
                <text x="584" y="131" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">SAC</text>
            </g>

            <!-- Tank -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('tank');">
                <ellipse cx="728" cy="127" rx="44" ry="17" fill="#ffffff" stroke="#1e293b" stroke-width="1.8" />
                <text x="728" y="131" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">Tank</text>
            </g>

            <!-- SAMM (Solid Blue Box) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('lrms');">
                <rect x="828" y="110" width="88" height="34" rx="6" fill="#2563eb" stroke="#1d4ed8" stroke-width="1.5" />
                <text x="872" y="131" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">SAMM</text>
            </g>

            <!-- VTL -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('vtl');">
                <rect x="540" y="164" width="88" height="34" rx="6" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
                <text x="584" y="185" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#0f172a" text-anchor="middle">VTL</text>
            </g>

            <!-- DT (Oval) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('twin');">
                <ellipse cx="728" cy="181" rx="44" ry="17" fill="#eff6ff" stroke="#2563eb" stroke-width="2" />
                <text x="728" y="185" font-family="'Barlow Semi Condensed', sans-serif" font-size="12.5" font-weight="800" fill="#1d4ed8" text-anchor="middle">DT</text>
            </g>

            <!-- CMS (Solid Green Box) -->
            <g style="cursor:pointer;" onclick="if(window.openModal) openModal('hms');">
                <rect x="828" y="164" width="88" height="34" rx="6" fill="#16a34a" stroke="#15803d" stroke-width="1.5" />
                <text x="872" y="185" font-family="'Barlow Semi Condensed', sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle">CMS</text>
            </g>
        </g>

        <!-- ========================================================= -->
        <!-- RIGHT BOTTOM: TRADITIONAL SYSML DIAGRAM TREE               -->
        <!-- Exact 9 diagrams and 3-color taxonomy from slide           -->
        <!-- ========================================================= -->
        <g id="p45-sysml-tree" style="cursor:pointer;" onclick="if(window.openModal) openModal('ast_system_model');">
            <!-- Root Label (Rotated vertically) -->
            <text x="576" y="328" transform="rotate(-90 576 328)" font-family="'Barlow Semi Condensed', sans-serif" font-size="11.5" font-weight="800" fill="#475569" text-anchor="middle" letter-spacing="0.8">Traditional SysML Diagram</text>

            <!-- Tree Hierarchy Lines -->
            <line x1="594" y1="228" x2="594" y2="420" stroke="#94a3b8" stroke-width="1.4"/>

            <line x1="594" y1="228" x2="614" y2="228" stroke="#94a3b8" stroke-width="1.4"/>
            <line x1="594" y1="252" x2="614" y2="252" stroke="#94a3b8" stroke-width="1.4"/>
            <line x1="594" y1="276" x2="614" y2="276" stroke="#94a3b8" stroke-width="1.4"/>
            <line x1="594" y1="300" x2="614" y2="300" stroke="#94a3b8" stroke-width="1.4"/>
            <line x1="594" y1="324" x2="614" y2="324" stroke="#94a3b8" stroke-width="1.4"/>
            <line x1="594" y1="348" x2="614" y2="348" stroke="#94a3b8" stroke-width="1.4"/>
            <line x1="594" y1="372" x2="614" y2="372" stroke="#94a3b8" stroke-width="1.4"/>
            <line x1="594" y1="396" x2="614" y2="396" stroke="#94a3b8" stroke-width="1.4"/>
            <line x1="594" y1="420" x2="614" y2="420" stroke="#94a3b8" stroke-width="1.4"/>

            <!-- 1. Use Case Diagram (SysML 2.0 / Purple) -->
            <rect x="614" y="217" width="156" height="21" rx="4" fill="#faf5ff" stroke="#c084fc" stroke-width="1.1"/>
            <text x="692" y="232" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">Use Case Diagram</text>

            <!-- 2. State Machine Diagram (SysML 2.0 / Purple) -->
            <rect x="614" y="241" width="156" height="21" rx="4" fill="#faf5ff" stroke="#c084fc" stroke-width="1.1"/>
            <text x="692" y="256" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">State Machine Diagram</text>

            <!-- 3. Sequence Diagram (SysML 2.0 / Purple) -->
            <rect x="614" y="265" width="156" height="21" rx="4" fill="#faf5ff" stroke="#c084fc" stroke-width="1.1"/>
            <text x="692" y="280" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">Sequence Diagram</text>

            <!-- 4. Activity Diagram (Modified UML / Green) -->
            <rect x="614" y="289" width="156" height="21" rx="4" fill="#f0fdf4" stroke="#86efac" stroke-width="1.1"/>
            <text x="692" y="304" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#15803d" text-anchor="middle">Activity Diagram</text>

            <!-- 5. Requirement Diagram (Non-Diagram / Pink) -->
            <rect x="614" y="313" width="156" height="21" rx="4" fill="#fff1f2" stroke="#fda4af" stroke-width="1.3"/>
            <text x="692" y="328" font-family="'Inter', sans-serif" font-size="9.2" font-weight="800" fill="#be123c" text-anchor="middle">Requirement Diagram</text>

            <!-- 6. Package Diagram (SysML 2.0 / Purple) -->
            <rect x="614" y="337" width="156" height="21" rx="4" fill="#faf5ff" stroke="#c084fc" stroke-width="1.1"/>
            <text x="692" y="352" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">Package Diagram</text>

            <!-- 7. Block Definition Diagram (Modified UML / Green) -->
            <rect x="614" y="361" width="156" height="21" rx="4" fill="#f0fdf4" stroke="#86efac" stroke-width="1.1"/>
            <text x="692" y="376" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#15803d" text-anchor="middle">Block Definition Diagram</text>

            <!-- 8. Internal Block Diagram (Modified UML / Green) -->
            <rect x="614" y="385" width="156" height="21" rx="4" fill="#f0fdf4" stroke="#86efac" stroke-width="1.1"/>
            <text x="692" y="400" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#15803d" text-anchor="middle">Internal Block Diagram</text>

            <!-- 9. Parametric Diagram (Non-Diagram / Pink) -->
            <rect x="614" y="409" width="156" height="21" rx="4" fill="#fff1f2" stroke="#fda4af" stroke-width="1.1"/>
            <text x="692" y="424" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#be123c" text-anchor="middle">Parametric Diagram</text>
        </g>

        <!-- Digital Thread Execution Curved Arrow (Requirement Diagram -> DT) -->
        <g id="p45-digital-thread-arrow">
            <path d="M 770 324 C 805 324, 805 212, 755 200" fill="none" stroke="#16a34a" stroke-width="3.5" stroke-linecap="round"/>
            <polygon points="752,206 746,197 755,194" fill="#16a34a"/>
        </g>

        <!-- SysML Legend (Exact 3 categories from slide) -->
        <g id="p45-legend" transform="translate(560, 446)">
            <!-- Non-Diagram -->
            <rect x="0" y="0" width="108" height="24" rx="5" fill="#fff1f2" stroke="#fda4af" stroke-width="1"/>
            <circle cx="14" cy="12" r="4.5" fill="#f43f5e"/>
            <text x="26" y="16" font-family="'Inter', sans-serif" font-size="9.5" font-weight="700" fill="#be123c">Non-Diagram</text>

            <!-- SysML 2.0 -->
            <rect x="122" y="0" width="98" height="24" rx="5" fill="#faf5ff" stroke="#c084fc" stroke-width="1"/>
            <circle cx="136" cy="12" r="4.5" fill="#a855f7"/>
            <text x="148" y="16" font-family="'Inter', sans-serif" font-size="9.5" font-weight="700" fill="#6b21a8">SysML 2.0</text>

            <!-- Modified UML -->
            <rect x="234" y="0" width="112" height="24" rx="5" fill="#f0fdf4" stroke="#86efac" stroke-width="1"/>
            <circle cx="248" cy="12" r="4.5" fill="#22c55e"/>
            <text x="260" y="16" font-family="'Inter', sans-serif" font-size="9.5" font-weight="700" fill="#15803d">Modified UML</text>
        </g>
    </g>    </g>
            </svg>
            <div class="hint">Tap a node for details &middot; Arrow keys change phase</div>
        </div>

        <!-- Simulation Viewport -->
        <div class="sim-viewport" id="sim-viewport">
            <div class="sim-action-bar">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:15px; font-weight:800; color:#ffffff;">BALLAST TANK B-3 REAL-TIME TWIN SIMULATION</span>
                    <span id="sim-status-badge" style="font-size:11px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; padding:4px 10px; border-radius:6px; background:#064e3b; color:#34d399; border:1px solid #10b981;">🟢 BULKHEAD NOMINAL (18.0mm)</span>
                </div>
                <div style="display:flex; gap:10px;">
                    <button class="sim-action-btn btn-rust" id="btn-trigger-rust">⚠️ Simulate Rust Defect</button>
                    <button class="sim-action-btn btn-clean active" id="btn-trigger-clean">🟢 Restore Clean Bulkhead</button>
                </div>
            </div>
            <div id="sim-svg-container" style="flex:1; border-radius:12px; overflow:hidden; border:1px solid #1e293b;"></div>
        </div>
    </section>

    <!-- Right Sidebar Notes Panel -->
    <aside class="notes-panel" id="notes-panel"></aside>
</main>

<!-- Screen-Covering Modal Popup -->
<div class="modal-overlay" id="modal-overlay">
    <div class="modal-card">
        <div class="modal-header" style="background:#0f172a; padding:16px 24px; border-bottom:1px solid #1e293b; display:flex; justify-content:space-between; align-items:center;">
            <div id="modal-header-titles" style="display:flex; flex-direction:column; gap:3px;">
                <span id="modal-super-title" style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; letter-spacing:1.2px; color:#38bdf8;">COMPONENT INSPECTION</span>
                <h2 id="modal-title-text" style="font-family:'Barlow Semi Condensed',sans-serif; font-size:22px; font-weight:800; color:#ffffff; margin:0;">Component Inspection</h2>
                <span id="modal-subtitle" style="font-size:12px; color:#94a3b8;">Detailed component analysis and telemetry</span>
            </div>
            <div style="display:flex; align-items:center; gap:14px;">
                <div id="modal-header-status-badge" style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800; padding:6px 14px; border-radius:8px;"></div>
                <button class="modal-close" id="btn-modal-close" style="min-height:38px; padding:6px 16px; border-radius:8px; border:1.5px solid #475569; background:#1e293b; color:#ffffff; font-size:13px; font-weight:800; cursor:pointer;">&times; Close</button>
            </div>
        </div>
        <div class="modal-body" id="modal-body-container" style="padding:0; background:#020617; overflow-y:auto; max-height:calc(92vh - 80px);"></div>
    </div>
</div>

<script>
// =============================================================================
// SENSOR & COMPONENT INSPECTION IMAGES CONFIGURATION
// To add or replace an image, simply paste your Base64 string or local file path:
// =============================================================================

// Place LiDAR image here
const IMAGE_LIDAR = "{img_data.get('lidar', '')}";

// Place RGB / Video camera image here
const IMAGE_RGB = "{img_data.get('rgb', '')}";

// Place Hyperspectral camera image here
const IMAGE_HYP = "{img_data.get('hyp', '') or img_data.get('hyperspectral_cubert', '')}";

// Place SAC (Surface Area Calculation) image here
const IMAGE_SAC = "{img_data.get('sac', '')}";
const IMAGE_AST_SLIDE = "{img_data.get('ast_system_model', '')}";
const IMAGE_BLENDER = "{img_data.get('blender_remesh', '') or img_data.get('blender', '')}";

// Place VTL (Virtual Technical Library) image here
const IMAGE_VTL = "{img_data.get('vtl', '')}";

// Place LRMS (Long Range Maintenance Schedule) image here
const IMAGE_LRMS = "{img_data.get('lrms', '') or img_data.get('samm', '')}";
const IMAGE_SAMM = IMAGE_LRMS;

// Place HMS (Hull Maintenance System) image here
const IMAGE_HMS = "{img_data.get('hms', '') or img_data.get('cms', '')}";
const IMAGE_CMS = IMAGE_HMS;

// Place Real Tank images here
const IMAGE_TANK_CLEAN = "{img_data.get('clean', '')}";
const IMAGE_TANK_RUST = "{img_data.get('rust', '')}";

// Place Digital Twin 3D CAD mesh images here
const IMAGE_TWIN_CLEAN = "{img_data.get('dt_clean', '')}";
const IMAGE_TWIN_RUST = "{img_data.get('dt_rust', '')}";

const SENSOR_IMAGES = {{
    lidar: IMAGE_LIDAR,
    rgb: IMAGE_RGB,
    hyp: IMAGE_HYP,
    sac: IMAGE_SAC,
    ast_system_model: IMAGE_AST_SLIDE,
    ast_slide: IMAGE_AST_SLIDE,
    blender: IMAGE_BLENDER,
    blender_remesh: IMAGE_BLENDER,
    vtl: IMAGE_VTL,
    lrms: IMAGE_LRMS,
    samm: IMAGE_LRMS,
    hms: IMAGE_HMS,
    cms: IMAGE_HMS,
    tank: IMAGE_TANK_CLEAN,
    twin: IMAGE_TWIN_CLEAN,
}};

/* Phases Configuration matching story_app.py */
const PHASES = {{
    1: {{
        name: "Phase 1",
        title: "Separate projects",
        subtitle: "Independent Foundation",
        description: "The initial phase establishes the physical Ballast Tank with onboard sensors (LiDAR, RGB/Video, Hyper) alongside separate computation prototypes (SAC and VTL). All modules operate as independent projects without interconnecting pipelines."
    }},
    2: {{
        name: "Phase 2",
        title: "Connected projects",
        subtitle: "Early Integration",
        description: "The first integration links form between scanning, computation, and the digital twin. LiDAR feeds point clouds into SAC, which transfers surface mesh models directly to the Digital Twin (DT) alongside VTL scantling records. SAC and VTL now directly connect and feed the emergent Digital Twin foundation."
    }},
    3: {{
        name: "Phase 3",
        title: "The digital twin",
        subtitle: "Full Digital Synchronization",
        description: "The complete digital twin architecture is live. All three sensors (LiDAR, RGB/Video, Hyper) monitor the physical Ballast Tank, while VTL feeds structural records to the Digital Twin (DT). DT maintains continuous real-time bidirectional synchronization with the Ballast Tank."
    }},
    4: {{
        name: "Phase 4",
        title: "Beyond the twin",
        subtitle: "External Expansion & Decision Support",
        description: "Beyond the twin: LRMS and HMS act as the next link for the digital twin. DT feeds HMS (Hull Maintenance System) for fleet-wide awareness and analytics, while LRMS (Long Range Maintenance Schedule) provides decision support directing maintenance actions back to the physical Ballast Tank."
    }},
    4.5: {{
        name: "Phase 4.5",
        title: "AST System Model",
        subtitle: "MBSE & Enterprise Data Architecture Framework",
        description: "Formalizes the enterprise data foundation and systems engineering architecture for the Autonomous / Advanced Ship Technology (AST) Digital Twin. Connects the semantic ontology, hierarchical taxonomy, and relational schema through SysML 2.0 digital thread execution and algedonic closed-loop feedback directly into operational twin telemetry."
    }}
}};

/* SVG Nodes Specification matching story_app.py */
const SVG_NODES = {{
    lidar: {{ group: "sensors", label: "LIDAR", sub: "3D laser scan", shape: "rect", w: 116, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", name: "LD-01 3D Conical LiDAR Scanner", about: "Conical 3D laser scanner mounted on tank ceiling dome producing 1.2M points/sec.", gives: ["3D Point Cloud", "Surface Profile"] }},
    rgb:   {{ group: "sensors", label: "RGB/Video", sub: "visual images", shape: "rect", w: 116, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", name: "RGB & Video Camera", about: "High-resolution 4K optical camera stream capturing physical surface texture and visual coating condition.", gives: ["4K Video Feed", "Surface Orthophotos"] }},
    hyp:   {{ group: "sensors", label: "Hyper", sub: "surface condition", shape: "rect", w: 116, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", name: "Hyperspectral Imager (Auto_000_1123.cu3s)", about: "Cubert VNIR hyperspectral scanner detecting chemical oxidation and coating degradation signatures.", gives: ["Spectral Tensors", "Fe₂O₃ Oxidation Maps"] }},
    sac:   {{ group: "computation", label: "SAC", sub: "surface area", shape: "rect", w: 116, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", name: "Surface Area Engine (SAC)", about: "Computes 3D surface area Delaunay meshes and compares real-time scans against baseline CAD scantling.", gives: ["3D Mesh Model", "Surface Area Delta"] }},
    vtl:   {{ group: "computation", label: "VTL Prototype", sub: "technical library", shape: "rect", w: 130, h: 62, rx: 10, fill: "#ffffff", stroke: "#1e293b", name: "VTL Prototype: Virtual Technical Library", about: "Stores vessel scantling plans, DNV-GL class records, and coating decay curves.", gives: ["Scantling Compliance", "Tank Records"] }},
    tank:  {{ group: "sensors", label: "Ballast Tank", sub: "", shape: "ellipse", rx: 65, ry: 38, fill: "#ffffff", stroke: "#1e293b", name: "MSC Ballast Tank B-3", about: "The physical cargo tank compartment on board the vessel.", gives: ["Physical Inspection Data", "Ultrasound Scantling"] }},
    twin:  {{ group: "dtsync", label: "DT", sub: "digital twin", shape: "ellipse", rx: 59, ry: 38, fill: "#ffffff", stroke: "#1e293b", name: "Digital Twin (DT)", about: "A virtual 3D replica of the ballast tank kept continuously synchronized with the physical asset.", gives: ["Synchronized 3D Mesh", "Real-Time Telemetry"] }},
    samm:  {{ group: "decision", label: "LRMS", sub: "Long Range Maintenance Schedule", shape: "rect", w: 126, h: 62, rx: 10, fill: "#0284c7", stroke: "#0369a1", name: "LRMS: Long Range Maintenance Schedule", about: "Condition-Based Maintenance policy engine that optimizes drydock work packs and repair ROI.", gives: ["Maintenance Schedule", "Repair Work Packs"] }},
    cms:   {{ group: "decision", label: "HMS", sub: "Hull Maintenance System", shape: "rect", w: 126, h: 62, rx: 10, fill: "#10b981", stroke: "#059669", name: "HMS: Hull Maintenance System", about: "Fleet-wide corrosion predictive analytics and remaining useful life (RUL) modeling.", gives: ["Hull Health Index", "Fleet Predictive RUL"] }}
}};

/* Group Bounding Boxes matching story_app.py */
const SVG_GROUPS = {{
    sensors:     {{ label: "Ballast Tank & Sensors", stroke: "#ef4444", fill: "rgba(254, 242, 242, 0.45)", text: "#b91c1c", badgeAlign: "top-center" }},
    computation: {{ label: "Computation", stroke: "#10b981", fill: "rgba(240, 253, 244, 0.45)", text: "#047857", badgeAlign: "bottom-center" }},
    dtsync:      {{ label: "Digital Twin", stroke: "#3b82f6", fill: "rgba(239, 246, 255, 0.45)", text: "#1d4ed8", badgeAlign: "top-center" }},
    decision:    {{ label: "Beyond the Twin", stroke: "#8b5cf6", fill: "rgba(245, 243, 255, 0.45)", text: "#6d28d9", badgeAlign: "top-center" }}
}};

/* Layout coordinates per Phase matching story_app.py */
const SVG_LAYOUT = {{
    1: {{
        lidar: [400, 130], rgb: [520, 130], hyp: [640, 130],
        tank: [520, 265],
        sac: [180, 205], vtl: [220, 410]
    }},
    2: {{
        lidar: [400, 130], rgb: [520, 130], hyp: [640, 130],
        tank: [520, 265],
        sac: [180, 205], vtl: [220, 410],
        twin: [520, 475]
    }},
    3: {{
        lidar: [400, 130], rgb: [520, 130], hyp: [640, 130],
        tank: [520, 265],
        sac: [180, 205], vtl: [220, 410],
        twin: [520, 475]
    }},
    4: {{
        lidar: [400, 130], rgb: [520, 130], hyp: [640, 130],
        tank: [520, 265],
        sac: [180, 205], vtl: [220, 410],
        twin: [520, 475],
        samm: [820, 335], cms: [820, 475]
    }},
    4.5: {{}}
}};

const PHASE_ORDER = [1, 2, 3, 4, 4.5];

/* Directed Edges matching story_app.py */
const SVG_EDGES = [
    {{ a: "lidar", b: "sac", label: "point cloud", phases: [2, 3, 4] }},
    {{ a: "sac", b: "twin", label: "area + model", phases: [2, 3, 4], curve: 20 }},
    {{ a: "lidar", b: "tank", label: "", phases: [3, 4], bidirectional: true }},
    {{ a: "rgb", b: "tank", label: "", phases: [3, 4], bidirectional: true }},
    {{ a: "hyp", b: "tank", label: "", phases: [3, 4], bidirectional: true }},
    {{ a: "tank", b: "twin", label: "sync", phases: [3, 4], bidirectional: true }},
    {{ a: "vtl", b: "twin", label: "tank records", phases: [2, 3, 4] }},
    {{ a: "twin", b: "cms", label: "twin data", phases: [4] }},
    {{ a: "samm", b: "tank", label: "actions", phases: [4] }},
    {{ a: "cms", b: "vtl", label: "", phases: [4], dashed: true, curve: -140 }},
    {{ a: "samm", b: "cms", label: "", phases: [4], bidirectional: true }}
];

const svgNS = "http://www.w3.org/2000/svg";
let currentPhase = 1;
let selectedNode = null;
let currentScenario = "clean";
let viewMode = "graph";
const pos = {{}};
const nodeEls = {{}}, groupEls = {{}}, edgeEls = [];

for (const id in SVG_NODES) {{
    const start = SVG_LAYOUT[1][id] || SVG_LAYOUT[3][id] || SVG_LAYOUT[4][id] || [500, 300];
    pos[id] = {{ x: start[0], y: start[1], o: SVG_LAYOUT[1][id] ? 1 : 0 }};
}}

function svgEl(tag, attrs, parent) {{
    const el = document.createElementNS(svgNS, tag);
    for (const k in attrs) el.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(el);
    return el;
}}

function initDiagram() {{
    // Restore any previously dropped images from browser localStorage
    for (const id in SVG_NODES) {{
        try {{
            const cached = localStorage.getItem('dt_user_img_' + id);
            if (cached && cached.length > 20) {{
                SENSOR_IMAGES[id] = cached;
            }}
        }} catch(e) {{}}
    }}

    const gGroups = document.getElementById("groups");
    const gEdges = document.getElementById("edges");
    const gNodes = document.getElementById("nodes");
    gGroups.innerHTML = "";
    gEdges.innerHTML = "";
    gNodes.innerHTML = "";

    // 1. Build Group Boxes
    for (const gid in SVG_GROUPS) {{
        const grp = SVG_GROUPS[gid];
        const gg = svgEl("g", {{ class: "group-box g-" + gid }}, gGroups);
        const rect = svgEl("rect", {{ class: "group-bg", rx: 14, ry: 14, fill: grp.fill, stroke: grp.stroke }}, gg);
        const text = svgEl("text", {{ class: "group-title", fill: grp.text }}, gg);
        text.textContent = grp.label;
        groupEls[gid] = {{ g: gg, rect, text }};
    }}

    // 2. Build Edges
    SVG_EDGES.forEach(e => {{
        const eg = svgEl("g", {{ class: "edge" + (e.dashed ? " feedback" : "") }}, gEdges);
        const path = svgEl("path", {{ class: "edge-path" }}, eg);
        let bg = null, tx = null;
        if (e.label) {{
            bg = svgEl("rect", {{ class: "elabel-bg", height: 18 }}, eg);
            tx = svgEl("text", {{ class: "elabel" }}, eg);
            tx.textContent = e.label;
        }}
        if (e.label === "point cloud" || (e.a === "lidar" && e.b === "sac")) {{
            eg.style.cursor = "pointer";
            eg.classList.add("clickable-pipeline-edge");
            eg.setAttribute("role", "button");
            eg.setAttribute("tabindex", "0");
            eg.setAttribute("title", "Click to inspect LiDAR ➔ SAC Point Cloud Surface Area Pipeline");
            eg.addEventListener("click", function(evt) {{
                evt.stopPropagation();
                openPointCloudModal();
            }});
            if (bg) {{ bg.style.cursor = "pointer"; }}
            if (tx) {{ tx.style.cursor = "pointer"; }}
        }}
        edgeEls.push({{ a: e.a, b: e.b, label: e.label, phases: e.phases, curve: e.curve || 0, dashed: e.dashed, bidirectional: e.bidirectional, g: eg, path, bg, tx }});
    }});

    // 3. Build Nodes
    for (const id in SVG_NODES) {{
        const n = SVG_NODES[id];
        const ng = svgEl("g", {{ class: "node k-" + id, role: "button" }}, gNodes);

        if (n.shape === "ellipse") {{
            svgEl("ellipse", {{ class: "glow-ring", rx: n.rx + 6, ry: n.ry + 6 }}, ng);
            svgEl("ellipse", {{ class: "body", rx: n.rx, ry: n.ry, fill: n.fill, stroke: n.stroke }}, ng);
        }} else {{
            svgEl("rect", {{ class: "glow-ring", x: -n.w / 2 - 5, y: -n.h / 2 - 5, width: n.w + 10, height: n.h + 10, rx: n.rx + 4, ry: n.rx + 4 }}, ng);
            svgEl("rect", {{ class: "body", x: -n.w / 2, y: -n.h / 2, width: n.w, height: n.h, rx: n.rx, ry: n.rx, fill: n.fill, stroke: n.stroke }}, ng);
        }}

        const t = svgEl("text", {{ class: "label", y: n.sub ? -4 : 4 }}, ng);
        t.textContent = n.label;
        if (n.sub) {{
            const s = svgEl("text", {{ class: "sub", y: 16 }}, ng);
            s.textContent = n.sub;
        }}

        ng.addEventListener("click", (evt) => {{
            evt.stopPropagation();
            selectNode(id);
            openModal(id);
        }});
        nodeEls[id] = ng;
    }}

    document.getElementById("svg").addEventListener("click", () => {{
        if (selectedNode) selectNode(null);
    }});

    draw();
    highlight();
}}

function clipBoundary(xA, yA, xB, yB, node) {{
    const dx = xB - xA, dy = yB - yA, d = Math.hypot(dx, dy) || 1;
    const ux = dx / d, uy = dy / d;
    if (node.shape === "ellipse") {{
        const scale = 1.0 / Math.sqrt(Math.pow(ux / node.rx, 2) + Math.pow(uy / node.ry, 2));
        return {{ x: xA + ux * scale, y: yA + uy * scale }};
    }} else {{
        const hw = node.w / 2, hh = node.h / 2;
        const tx = ux !== 0 ? Math.abs(hw / ux) : 1e9;
        const ty = uy !== 0 ? Math.abs(hh / uy) : 1e9;
        const t = Math.min(tx, ty);
        return {{ x: xA + ux * (t + 1), y: yA + uy * (t + 1) }};
    }}
}}

function draw() {{
    const p45El = document.getElementById("phase45-placeholder");
    if (p45El) {{
        p45El.style.display = (currentPhase === 4.5) ? "" : "none";
    }}

    // 1. Draw Nodes
    for (const id in SVG_NODES) {{
        const p = pos[id], el = nodeEls[id];
        if (!el) continue;
        el.setAttribute("transform", `translate(${{p.x}},${{p.y}})`);
        el.setAttribute("opacity", p.o.toFixed(3));
        el.style.display = p.o < 0.02 ? "none" : "";
    }}

    // 2. Draw Group Boxes
    for (const gid in SVG_GROUPS) {{
        const grp = SVG_GROUPS[gid];
        const grpEl = groupEls[gid];
        if (!grpEl) continue;

        const childIds = Object.keys(SVG_NODES).filter(nid => SVG_NODES[nid].group === gid);
        const visChildren = childIds.filter(nid => pos[nid] && pos[nid].o > 0.02);

        if (visChildren.length === 0) {{
            grpEl.g.style.display = "none";
            continue;
        }}
        grpEl.g.style.display = "";

        let minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9, maxO = 0;
        visChildren.forEach(nid => {{
            const p = pos[nid], n = SVG_NODES[nid];
            const hw = (n.shape === "ellipse" ? n.rx : n.w / 2);
            const hh = (n.shape === "ellipse" ? n.ry : n.h / 2);
            minX = Math.min(minX, p.x - hw);
            maxX = Math.max(maxX, p.x + hw);
            minY = Math.min(minY, p.y - hh);
            maxY = Math.max(maxY, p.y + hh);
            maxO = Math.max(maxO, p.o);
        }});

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

        if (grp.badgeAlign === "bottom-center") {{
            grpEl.text.setAttribute("x", (minX + maxX) / 2);
            grpEl.text.setAttribute("y", maxY - 10);
        }} else {{
            grpEl.text.setAttribute("x", (minX + maxX) / 2);
            grpEl.text.setAttribute("y", minY + 15);
        }}
    }}

    // 3. Draw Edges
    edgeEls.forEach(e => {{
        const on = e.phases.includes(currentPhase);
        const A = pos[e.a], B = pos[e.b];
        const vis = on ? Math.min(A.o, B.o) : 0;
        e.g.style.display = vis < 0.02 ? "none" : "";
        e.g.setAttribute("opacity", vis.toFixed(3));
        if (vis < 0.02) return;

        const nodeA = SVG_NODES[e.a], nodeB = SVG_NODES[e.b];
        const pA = clipBoundary(A.x, A.y, B.x, B.y, nodeA);
        const pB = clipBoundary(B.x, B.y, A.x, A.y, nodeB);

        const x1 = pA.x, y1 = pA.y, x2 = pB.x, y2 = pB.y;
        const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;

        if (e.a === "cms" && e.b === "vtl") {{
            // Clear, elegant arc below Digital Twin with 40px+ clearance so it touches nothing else
            const sx = A.x - 30, sy = A.y + 31;
            const ex = B.x, ey = B.y + 31;
            const cx = (sx + ex) / 2, cy = 630;
            e.path.setAttribute("d", `M ${{sx}} ${{sy}} Q ${{cx}} ${{cy}} ${{ex}} ${{ey}}`);
        }} else if (e.curve) {{
            const dx = x2 - x1, dy = y2 - y1, d = Math.hypot(dx, dy) || 1;
            const nx = -dy / d, ny = dx / d;
            const cx = mx + nx * e.curve, cy = my + ny * e.curve;
            e.path.setAttribute("d", `M ${{x1}} ${{y1}} Q ${{cx}} ${{cy}} ${{x2}} ${{y2}}`);
            if (e.tx) {{
                e.tx.setAttribute("x", cx);
                e.tx.setAttribute("y", cy + 4);
                const tw = e.label.length * 6.8 + 12;
                e.bg.setAttribute("x", cx - tw / 2);
                e.bg.setAttribute("y", cy - 9);
                e.bg.setAttribute("width", tw);
            }}
        }} else {{
            e.path.setAttribute("d", `M ${{x1}} ${{y1}} L ${{x2}} ${{y2}}`);
            if (e.tx) {{
                e.tx.setAttribute("x", mx);
                e.tx.setAttribute("y", my + 4);
                const tw = e.label.length * 6.8 + 12;
                e.bg.setAttribute("x", mx - tw / 2);
                e.bg.setAttribute("y", my - 9);
                e.bg.setAttribute("width", tw);
            }}
        }}

        if (e.bidirectional) {{
            e.path.setAttribute("marker-start", "url(#arrow-start)");
            e.path.setAttribute("marker-end", "url(#arrow)");
        }} else if (e.dashed) {{
            e.path.setAttribute("stroke-dasharray", "6 4");
            e.path.setAttribute("marker-end", "url(#arrow-feedback)");
            e.path.removeAttribute("marker-start");
        }} else {{
            e.path.setAttribute("marker-end", "url(#arrow)");
            e.path.removeAttribute("marker-start");
        }}
    }});
}}

let anim = null;
function goToPhase(targetPhase) {{
    const target = parseFloat(targetPhase);
    if (!PHASES[target]) return;
    const p = target;
    currentPhase = p;
    if (selectedNode && (!SVG_LAYOUT[p] || !SVG_LAYOUT[p][selectedNode])) {{
        selectedNode = null;
    }}

    const from = {{}};
    for (const id in pos) from[id] = {{ ...pos[id] }};
    const to = {{}};
    for (const id in pos) {{
        const t = SVG_LAYOUT[p] ? SVG_LAYOUT[p][id] : null;
        to[id] = t ? {{ x: t[0], y: t[1], o: 1 }} : {{ x: from[id].x, y: from[id].y, o: 0 }};
        if (t && from[id].o < 0.02) {{
            from[id].x = t[0];
            from[id].y = t[1];
        }}
    }}

    if (anim) cancelAnimationFrame(anim);
    const dur = 650;
    const t0 = performance.now();
    // High-performance cubic ease-in-out curve
    const ease = t => t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2;

    const step = function(now) {{
        const k = Math.min(1, (now - t0) / dur);
        const e = ease(k);
        for (const id in pos) {{
            pos[id].x = from[id].x + (to[id].x - from[id].x) * e;
            pos[id].y = from[id].y + (to[id].y - from[id].y) * e;
            pos[id].o = from[id].o + (to[id].o - from[id].o) * e;
        }}
        draw();
        if (k < 1) {{
            anim = requestAnimationFrame(step);
        }}
    }};
    anim = requestAnimationFrame(step);

    renderTabs();
    highlight();
    renderNotes();

    const viewBar = document.getElementById("view-mode-bar");
    if (currentPhase === 3) {{
        viewBar.style.display = "flex";
    }} else {{
        viewBar.style.display = "none";
        switchViewMode("graph");
    }}
}}

function renderTabs() {{
    const bar = document.getElementById("phase-tabs");
    bar.innerHTML = "";
    PHASE_ORDER.forEach(pKey => {{
        const p = PHASES[pKey];
        const btn = document.createElement("button");
        btn.className = "phase-tab-btn" + (pKey === currentPhase ? " active" : "");
        btn.innerHTML = `<span class="p-num">${{p.name}}</span><span class="p-title">${{p.title}}</span>`;
        btn.addEventListener("click", () => goToPhase(pKey));
        bar.appendChild(btn);
    }});
}}

function highlight() {{
    for (const id in nodeEls) {{
        nodeEls[id].classList.toggle("selected", id === selectedNode);
        const related = !selectedNode || id === selectedNode || SVG_EDGES.some(e => e.phases.includes(currentPhase) && ((e.a === selectedNode && e.b === id) || (e.b === selectedNode && e.a === id)));
        nodeEls[id].classList.toggle("dim", !related);
    }}
    edgeEls.forEach(e => {{
        const hot = selectedNode && (e.a === selectedNode || e.b === selectedNode);
        e.g.classList.toggle("hot", !!hot);
        e.g.classList.toggle("dim", !!selectedNode && !hot);
        if (e.bidirectional) {{
            e.path.setAttribute("marker-start", hot ? "url(#arrow-start-hot)" : "url(#arrow-start)");
            e.path.setAttribute("marker-end", hot ? "url(#arrow-hot)" : "url(#arrow)");
        }} else if (e.dashed) {{
            e.path.setAttribute("marker-end", hot ? "url(#arrow-hot)" : "url(#arrow-feedback)");
            e.path.removeAttribute("marker-start");
        }} else {{
            e.path.setAttribute("marker-end", hot ? "url(#arrow-hot)" : "url(#arrow)");
            e.path.removeAttribute("marker-start");
        }}
    }});
}}

function renderNotes() {{
    const box = document.getElementById("notes-panel");
    box.classList.remove("panel-slide-anim");
    void box.offsetWidth;
    box.classList.add("panel-slide-anim");
    const P = PHASES[currentPhase];
    const curIdx = PHASE_ORDER.indexOf(currentPhase);
    const prevPhase = curIdx > 0 ? PHASE_ORDER[curIdx - 1] : null;
    const nextPhase = curIdx < PHASE_ORDER.length - 1 ? PHASE_ORDER[curIdx + 1] : null;

    const nav = `
        <div class="footer-nav">
            <button class="nav-btn" id="btn-prev" ${{prevPhase === null ? "disabled" : ""}}>Previous</button>
            <button class="nav-btn primary" id="btn-next" ${{nextPhase === null ? "disabled" : ""}}>Next Phase</button>
        </div>`;

    if (!selectedNode) {{
        const visibleIds = Object.keys(SVG_LAYOUT[currentPhase] || {{}});
        box.innerHTML = `
            <div>
                <div class="notes-tag">${{P.name.toUpperCase()}} &middot; ARCHITECTURE OVERVIEW</div>
                <h2 class="notes-title">${{P.subtitle}}</h2>
            </div>
            <p class="notes-desc">${{P.description}}</p>
            <div>
                <div style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#64748b; letter-spacing:1px; margin-bottom:6px;">ACTIVE NODES IN THIS PHASE (${{visibleIds.length}})</div>
                <div class="pill-group">
                    ${{visibleIds.length > 0 ? visibleIds.map(id => `<button class="node-pill" onclick="selectNode('${{id}}'); openModal('${{id}}');">${{SVG_NODES[id].name}}</button>`).join("") : (currentPhase === 4.5 ? '<span style="color:#2563eb; font-size:12px; font-weight:700; background:#eff6ff; border:1px solid #bfdbfe; padding:4px 10px; border-radius:6px;">AST System Model &middot; 3 Tiers &amp; SysML Digital Thread</span>' : '<span style="color:#94a3b8; font-size:12px; font-style:italic;">None</span>')}}
                </div>
            </div>

            ${{currentPhase === 1 ? `
            <div style="margin-top:14px; background:#f8fafc; border:1.5px solid #cbd5e1; border-radius:12px; padding:14px; display:flex; flex-direction:column; gap:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#475569; letter-spacing:1px;">PHYSICAL ASSET &amp; SENSORS</span>
                    <span style="font-size:11px; font-weight:800; color:#2563eb; background:#eff6ff; padding:2px 6px; border-radius:4px;">PHASE 1 FOUNDATION</span>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                    <div style="background:#0f172a; border-radius:8px; overflow:hidden; border:1px solid #334155; height:110px; display:flex; align-items:center; justify-content:center; cursor:pointer;" onclick="selectNode('tank'); openModal('tank');" title="Click to inspect Ballast Tank">
                        <img src="${{IMAGE_TANK_CLEAN}}" alt="Tank" style="width:100%; height:100%; object-fit:cover;" />
                    </div>
                    <div style="background:#0f172a; border-radius:8px; overflow:hidden; border:1px solid #0284c7; height:110px; display:flex; align-items:center; justify-content:center; cursor:pointer;" onclick="selectNode('lidar'); openModal('lidar');" title="Click to inspect LiDAR">
                        <img src="${{IMAGE_LIDAR}}" alt="LiDAR" style="width:100%; height:100%; object-fit:contain;" />
                    </div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748b; font-weight:700;">
                    <span>⚓ Ballast Tank B-3</span>
                    <span>📸 LiDAR Scan (.e57)</span>
                </div>
            </div>` : ""}}

            ${{currentPhase === 2 ? `
            <div style="margin-top:14px; background:#f0f9ff; border:1.5px solid #0284c7; border-radius:12px; padding:14px; display:flex; flex-direction:column; gap:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#0284c7; letter-spacing:1px;">INTEGRATION PIPELINE</span>
                    <span style="font-size:11px; font-weight:800; color:#059669; background:#dcfce7; padding:2px 6px; border-radius:4px;">CONFIDENCE &gt; 0.83</span>
                </div>
                <p style="font-size:12.5px; color:#334155; margin:0; line-height:1.4;">
                    LiDAR point cloud connects to SAC surface area calculation engine:
                </p>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; cursor:pointer;" onclick="openPointCloudModal()" title="Click to open LiDAR ➔ SAC Software Manual">
                    <div style="background:#0f172a; border-radius:8px; overflow:hidden; border:1px solid #0284c7; height:100px; display:flex; align-items:center; justify-content:center;">
                        <img src="${{IMAGE_LIDAR}}" alt="LiDAR Scan" style="width:100%; height:100%; object-fit:contain;" />
                    </div>
                    <div style="background:#0f172a; border-radius:8px; overflow:hidden; border:1px solid #10b981; height:100px; display:flex; align-items:center; justify-content:center;">
                        <img src="${{IMAGE_SAC}}" alt="SAC Mesh" style="width:100%; height:100%; object-fit:contain;" />
                    </div>
                </div>
                <button class="inspect-action-btn" style="background:#0284c7; border-color:#0284c7; padding:10px 14px; font-size:13px;" onclick="openPointCloudModal()">
                    ☁️ Open LiDAR ➔ SAC Software Manual
                </button>
            </div>` : ""}}

            ${{currentPhase === 3 ? `
            <div style="margin-top:14px; background:#eff6ff; border:1.5px solid #3b82f6; border-radius:12px; padding:14px; display:flex; flex-direction:column; gap:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#1d4ed8; letter-spacing:1px;">DIGITAL TWIN SYNCHRONIZATION</span>
                    <span style="font-size:11px; font-weight:800; color:#059669; background:#dcfce7; padding:2px 6px; border-radius:4px;">REAL-TIME SYNC</span>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; cursor:pointer;" onclick="switchViewMode('sim')" title="Click to open simulation view">
                    <div style="background:#0f172a; border-radius:8px; overflow:hidden; border:1px solid #334155; height:100px; display:flex; align-items:center; justify-content:center;">
                        <img src="${{currentScenario === 'rust' ? IMAGE_TANK_RUST : IMAGE_TANK_CLEAN}}" alt="Ship Tank" style="width:100%; height:100%; object-fit:contain;" />
                    </div>
                    <div style="background:#0f172a; border-radius:8px; overflow:hidden; border:1px solid #38bdf8; height:100px; display:flex; align-items:center; justify-content:center;">
                        <img src="${{currentScenario === 'rust' ? IMAGE_TWIN_RUST : IMAGE_TWIN_CLEAN}}" alt="Digital Twin" style="width:100%; height:100%; object-fit:contain;" />
                    </div>
                </div>
                <button class="inspect-action-btn" style="background:#2563eb; border-color:#2563eb; padding:10px 14px;" onclick="switchViewMode('sim')">
                    🌐 Open Interactive Dual-Asset Simulation
                </button>
            </div>` : ""}}

                        ${{currentPhase === 4.5 ? `
            <div style="margin-top:14px; background:#ffffff; border:1px solid #cbd5e1; border-radius:12px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,0.04); display:flex; flex-direction:column; gap:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800; color:#0f172a; letter-spacing:0.8px;">AST SYSTEM MODEL &bull; ARCHITECTURE TIERS</span>
                    <span style="font-size:10.5px; font-weight:800; color:#2563eb; background:#eff6ff; padding:2px 8px; border-radius:4px; border:1px solid #bfdbfe;">MBSE FOUNDATION</span>
                </div>

                ${{IMAGE_AST_SLIDE ? `
                <div style="background:#0f172a; border-radius:8px; overflow:hidden; border:1.5px solid #38bdf8; position:relative; cursor:pointer;" onclick="openModal('ast_system_model');" title="Click to inspect original slide in HD">
                    <img src="${{IMAGE_AST_SLIDE}}" alt="AST System Model Slide" style="width:100%; height:140px; object-fit:contain; display:block;" />
                    <div style="position:absolute; bottom:6px; right:8px; background:rgba(15,23,42,0.85); color:#38bdf8; font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:4px; border:1px solid #0284c7;">
                        🔍 View Full-Res Slide
                    </div>
                </div>` : ''}}

                <div style="background:#fff7ed; border-left:4px solid #ea580c; border-radius:0 8px 8px 0; padding:10px 12px; display:flex; flex-direction:column; gap:4px;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12.5px; font-weight:800; color:#c2410c;">1. Ontology Semantic Representation</span>
                    <div style="font-size:11.5px; color:#334155; line-height:1.45;">
                        Encodes system entities, their relationships, and constraints in a formal semantic model. Answers the question: what exists in this system and how do system relationships, dependencies, and decision objectives connect to one another?
                    </div>
                </div>

                <div style="background:#f0f9ff; border-left:4px solid #0284c7; border-radius:0 8px 8px 0; padding:10px 12px; display:flex; flex-direction:column; gap:4px;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12.5px; font-weight:800; color:#0369a1;">2. Taxonomy Hierarchical Classification</span>
                    <div style="font-size:11.5px; color:#334155; line-height:1.45;">
                        Organizes system elements into typed classes with inheritance. Enables structured reasoning about failure modes, behaviors, and decision categories across levels of abstraction.
                    </div>
                </div>

                <div style="background:#f0fdfa; border-left:4px solid #0d9488; border-radius:0 8px 8px 0; padding:10px 12px; display:flex; flex-direction:column; gap:4px;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12.5px; font-weight:800; color:#0f766e;">3. Schema Data Structure and Relational Encoding</span>
                    <div style="font-size:11.5px; color:#334155; line-height:1.45;">
                        Translates ontological and taxonomic knowledge into structured, queryable, and traceable data linked to system requirements and observed states. Establishes traceability links between system states, requirements, and observations.
                    </div>
                </div>

                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 12px; display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                    <div>
                        <div style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#0e3a53;">&darr; PERSISTENCE</div>
                        <div style="font-size:10.5px; color:#64748b; margin-top:2px;">Downward multi-temporal revision storage across vessel service life.</div>
                    </div>
                    <div>
                        <div style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#0e3a53;">&uarr; ALGEDONIC FEEDBACK</div>
                        <div style="font-size:10.5px; color:#64748b; margin-top:2px;">Upward cybernetic signals alerting when states deviate from safety rules.</div>
                    </div>
                </div>

                <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; gap:4px;">
                    <div style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:800; color:#15803d;">
                        🔄 SYSML 2.0 DIGITAL THREAD &rarr; DIGITAL TWIN (DT)
                    </div>
                    <div style="font-size:11px; color:#334155; line-height:1.4;">
                        Bidirectional semantic link connects formal MBSE models (Behavior, Requirements, Structure) into live runtime execution within the operational Digital Twin.
                    </div>
                </div>
            </div>` : ""}}

            ${{nav}}`;
    }} else {{
        const n = SVG_NODES[selectedNode];
        let previewImg = SENSOR_IMAGES[selectedNode];
        let previewBadge = n.name.toUpperCase();
        if (selectedNode === "twin" || selectedNode === "dt") {{
            previewImg = currentScenario === "rust" ? IMAGE_TWIN_RUST : IMAGE_TWIN_CLEAN;
            previewBadge = currentScenario === "rust" ? "⚠️ DIGITAL TWIN CAD (RUST DETECTED)" : "🟢 DIGITAL TWIN CAD (NOMINAL)";
        }} else if (selectedNode === "tank") {{
            previewImg = currentScenario === "rust" ? IMAGE_TANK_RUST : IMAGE_TANK_CLEAN;
            previewBadge = currentScenario === "rust" ? "🔴 BALLAST TANK SHIP CUTAWAY (CORROSION)" : "🟢 BALLAST TANK SHIP CUTAWAY (NOMINAL)";
        }} else if (selectedNode === "lidar") {{
            previewBadge = "📸 LIDAR POINT CLOUD SCAN (.E57)";
        }} else if (selectedNode === "sac") {{
            previewBadge = "📐 SAC RECONSTRUCTED 3D SURFACE MESH";
        }} else if (selectedNode === "hyp") {{
            previewBadge = "🌈 HYPERSPECTRAL CAMERA SENSOR";
        }}

        const imgCardHtml = (previewImg && previewImg.length > 20) ? `
            <div style="background:#0f172a; border-radius:12px; border:2px solid #38bdf8; overflow:hidden; display:flex; flex-direction:column; margin-top:8px; box-shadow:0 6px 18px rgba(0,0,0,0.25);">
                <div style="background:#1e293b; padding:8px 12px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:800; color:#38bdf8; letter-spacing:0.8px;">
                        ${{previewBadge}}
                    </span>
                    <span style="font-size:10.5px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; color:#94a3b8; background:#0f172a; padding:2px 6px; border-radius:4px;">
                        CLICK TO ENLARGE
                    </span>
                </div>
                <div style="position:relative; height:240px; background:#020617; display:flex; align-items:center; justify-content:center; cursor:pointer;" onclick="openModal('${{selectedNode}}')" title="Click to view full screen">
                    <img src="${{previewImg}}" alt="${{n.name}}" style="width:100%; height:100%; object-fit:contain; display:block;" />
                    <div style="position:absolute; bottom:8px; right:8px; background:rgba(15, 23, 42, 0.88); padding:3px 8px; border-radius:6px; color:#cbd5e1; font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:700; border:1px solid #334155;">
                        🔍 Click for Full Screen View
                    </div>
                </div>
            </div>` : `
            <div style="background:#0f172a; border-radius:12px; border:1.5px solid #334155; overflow:hidden; display:flex; flex-direction:column; margin-top:8px; box-shadow:0 4px 14px rgba(0,0,0,0.25);">
                <div style="background:#1e293b; padding:8px 12px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:800; color:#38bdf8; letter-spacing:0.8px;">
                        ${{selectedNode === "rgb" ? "4K OPTICAL STREAM &amp; TEXTURE HUD" : (selectedNode === "vtl" ? "DNV-GL SCANTLING &amp; CAD BASELINE" : (selectedNode === "samm" ? "LRMS MAINTENANCE POLICY ENGINE" : "HMS FLEET PREDICTIVE RUL"))}}
                    </span>
                    <span style="font-size:10.5px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; color:#34d399; background:#064e3b; padding:2px 6px; border-radius:4px;">
                        ONLINE
                    </span>
                </div>
                <div style="padding:18px 16px; background:#020617; display:flex; flex-direction:column; gap:10px; cursor:pointer;" onclick="openModal('${{selectedNode}}')" title="Click to view full technical specification">
                    <div style="font-family:'Barlow Semi Condensed',sans-serif; font-size:16px; font-weight:800; color:#f8fafc;">
                        ${{n.name}}
                    </div>
                    <div style="font-size:12px; color:#94a3b8; line-height:1.4;">
                        ${{n.about}}
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-top:4px;">
                        ${{n.gives.map(g => `<div style="background:#1e293b; color:#38bdf8; padding:5px 8px; border-radius:6px; font-size:11px; font-weight:700; border:1px solid #334155; text-align:center;">${{g}}</div>`).join("")}}
                    </div>
                    <div style="margin-top:6px; display:flex; justify-content:space-between; align-items:center; font-size:11px; color:#64748b; border-top:1px solid #1e293b; padding-top:8px;">
                        <span>Protocol: <strong>JSON / WebSocket</strong></span>
                        <span style="color:#38bdf8; font-weight:700;">Open Technical Spec &rarr;</span>
                    </div>
                </div>
            </div>`;

        box.innerHTML = `
            <div>
                <div class="notes-tag">PHASE ${{currentPhase}} &middot; ${{n.group.toUpperCase()}}</div>
                <h2 class="notes-title">${{n.name}}</h2>
            </div>

            ${{imgCardHtml}}

            <p class="notes-desc">${{n.about}}</p>
            <div>
                <div style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#64748b; letter-spacing:1px; margin-bottom:6px;">OUTPUTS / DATA FEEDS</div>
                <div class="pill-group">
                    ${{n.gives.map(g => `<span class="node-pill" style="cursor:default;">${{g}}</span>`).join("")}}
                </div>
            </div>

            <button class="inspect-action-btn" onclick="openModal('${{selectedNode}}')">
                🔍 Open Full-Screen Image Inspector
            </button>
            ${{(selectedNode === "lidar" || selectedNode === "sac") ? `
            <button class="inspect-action-btn" style="background:#0284c7; border-color:#0284c7; margin-top:8px;" onclick="openPointCloudModal()">
                ☁️ Inspect 'Point Cloud' Pipeline (LiDAR → SAC)
            </button>` : ""}}

            <button class="node-pill" style="margin-top:10px; align-self:flex-start;" onclick="selectNode(null)">
                &larr; Back to Phase Overview
            </button>
            ${{nav}}`;
    }}

    document.getElementById("btn-prev")?.addEventListener("click", () => {{
        if (prevPhase !== null) goToPhase(prevPhase);
    }});
    document.getElementById("btn-next")?.addEventListener("click", () => {{
        if (nextPhase !== null) goToPhase(nextPhase);
    }});
}}

function selectNode(id) {{
    selectedNode = (id && id === selectedNode) ? null : id;
    highlight();
    renderNotes();
}}

/* Modal popup: NOTHING BUT THE IMAGE */

function openPointCloudModal() {{
    const modal = document.getElementById("modal-overlay");
    const title = document.getElementById("modal-title-text");
    const body = document.getElementById("modal-body-container");
    title.textContent = "Point Cloud to Surface Mesh Pipeline (LiDAR ➔ SAC)";

    body.innerHTML = `
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:18px; width:100%; max-height:calc(88vh - 80px); overflow-y:auto; padding:4px; color:#1e293b; box-sizing:border-box;">
            
            <!-- LEFT COLUMN: Visual Images (LiDAR & SAC) -->
            <div style="display:flex; flex-direction:column; gap:12px;">
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
                        ${{IMAGE_LIDAR ? `<img src="${{IMAGE_LIDAR}}" alt="LiDAR Point Cloud" style="width:100%; height:100%; object-fit:contain; display:block;" />` : '<div style="color:#64748b; font-size:13px;">LiDAR Image Slot</div>'}}
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
                    <div style="position:relative; height:185px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden;">
                        ${{IMAGE_SAC ? `<img src="${{IMAGE_SAC}}" alt="SAC Reconstructed Mesh" style="width:100%; height:100%; object-fit:contain; display:block;" />` : '<div style="color:#64748b; font-size:13px;">SAC Image Slot</div>'}}
                        <div style="position:absolute; bottom:6px; left:8px; background:rgba(15, 23, 42, 0.9); padding:3px 8px; border-radius:4px; border:1px solid #10b981; color:#34d399; font-family:'Barlow Semi Condensed',sans-serif; font-size:10.5px; font-weight:700;">
                            Poisson Mesh · Octree Depth 10/11 · Watertight Shell
                        </div>
                    </div>
                </div>

                <!-- Image 3: Blender 4.5 Voxel Remesh & Interior Mesh -->
                <div style="background:#0f172a; border-radius:12px; border:2px solid #8b5cf6; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 4px 14px rgba(0,0,0,0.25);">
                    <div style="background:#1e293b; padding:8px 14px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12.5px; font-weight:800; color:#c084fc;">
                            🧊 STEP 3: BLENDER 4.5 VOXEL REMESH (0.15m)
                        </span>
                        <span style="font-size:10.5px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; padding:2px 7px; border-radius:4px; background:#4c1d95; color:#e9d5ff;">
                            MANIFOLD CAVITY
                        </span>
                    </div>
                    <div style="position:relative; height:185px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden;">
                        ${{IMAGE_BLENDER ? `<img src="${{IMAGE_BLENDER}}" alt="Blender Voxel Remesh Interior" style="width:100%; height:100%; object-fit:contain; display:block;" />` : '<div style="color:#64748b; font-size:13px;">Blender Remesh Image Slot</div>'}}
                        <div style="position:absolute; bottom:6px; left:8px; background:rgba(15, 23, 42, 0.9); padding:3px 8px; border-radius:4px; border:1px solid #8b5cf6; color:#c084fc; font-family:'Barlow Semi Condensed',sans-serif; font-size:10.5px; font-weight:700;">
                            Blender 4.5 &middot; Interior Compartment &middot; Watertight Manifold Topology
                        </div>
                    </div>
                </div>
            </div>

            <!-- RIGHT COLUMN: Short & Brief Executive Summary -->
            <div style="display:flex; flex-direction:column; gap:10px;">
                <!-- Card 1: Purpose & Connection -->
                <div style="background:#ffffff; border-radius:12px; padding:12px 16px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,0.05); display:flex; flex-direction:column; gap:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800; color:#0f172a; letter-spacing:0.5px;">
                            🎯 PURPOSE: LIDAR ➔ SAC CONNECTION
                        </span>
                        <span style="background:#dcfce7; border:1px solid #10b981; color:#047857; padding:2px 8px; border-radius:6px; font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800;">
                            CONFIDENCE &gt; 0.83
                        </span>
                    </div>
                    <p style="font-size:12px; line-height:1.45; color:#334155; margin:0;">
                        LiDAR scans provide raw 3D coordinate points ($X,Y,Z$) but cannot directly yield surface area due to sensor noise, reflections, and blind spots. 
                        The point cloud is transformed step-by-step into a watertight polygon mesh to calculate verified tank surface area.
                    </p>
                </div>

                <!-- Card 2: 3-Stage Software Pipeline -->
                <div style="background:#ffffff; border-radius:12px; padding:12px 16px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,0.05); display:flex; flex-direction:column; gap:8px;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12.5px; font-weight:800; color:#0f172a; letter-spacing:0.5px;">
                        ⚙️ 3-STAGE SOFTWARE WORKFLOW (STEPS 1–12)
                    </span>
                    <div style="display:flex; flex-direction:column; gap:6px; font-size:11.5px; line-height:1.4;">
                        <div style="background:#f0f9ff; border-left:3.5px solid #0284c7; padding:6px 10px; border-radius:0 6px 6px 0; color:#1e293b;">
                            <strong style="color:#0369a1;">1. CloudCompare (Steps 1–4):</strong> Opens <code>.e57</code>, computes surface normals (MST Plane), reconstructs Poisson mesh (octree depth 10/11), and filters noise using scalar field density. Saves <code>_RawMesh</code> &amp; <code>_SFilter</code>.
                        </div>
                        <div style="background:#f0fdf4; border-left:3.5px solid #16a34a; padding:6px 10px; border-radius:0 6px 6px 0; color:#1e293b;">
                            <strong style="color:#15803d;">2. Blender 4.5 (Steps 5–7):</strong> Imports <code>.ply</code>, sets origin to geometry, applies <strong>Voxel Remesh (0.15m)</strong> for uniform manifold faces, and checks 3D shell surface area. Saves <code>_SFilter_Remesh</code>.
                        </div>
                        <div style="background:#fff7ed; border-left:3.5px solid #ea580c; padding:6px 10px; border-radius:0 6px 6px 0; color:#1e293b;">
                            <strong style="color:#c2410c;">3. Developed Application (Steps 8–12):</strong> Compares raw vs remeshed models, verifies boundary consistency, and certifies area calculation for MSC monthly reporting.
                        </div>
                    </div>
                </div>

                <!-- Card 3: Categorization & Acceptance Standard -->
                <div style="background:#ffffff; border-radius:12px; padding:10px 14px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,0.05); display:flex; flex-direction:column; gap:6px;">
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:11px;">
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:6px 8px;">
                            <strong style="color:#0f172a; font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px;">🗂️ TANK CATEGORIZATION:</strong>
                            <div style="color:#475569; margin-top:2px;">
                                MSC <code>Tanksdataset</code> classified into <strong>Types A, B, C, D</strong> by geometric complexity.
                            </div>
                        </div>
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:6px 8px;">
                            <strong style="color:#0f172a; font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px;">🏷️ NAMING &amp; RULE:</strong>
                            <div style="color:#475569; margin-top:2px;">
                                <code>Dataset_TankName_OctreeDepth_ProcessStep</code><br/>
                                <strong style="color:#047857;">Rule: Confidence &gt; 0.83</strong> required for area certification.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    `;
    modal.classList.add("active");
}}

function openModal(nodeId) {{
    if (!nodeId) return;
    if (nodeId === "point_cloud" || nodeId === "point-cloud" || nodeId === "pipeline_lidar_sac") {{
        openPointCloudModal();
        return;
    }}
    if (nodeId === "ast_system_model" || nodeId === "ast_slide") {{
        superTitle.textContent = "MBSE & DATA STACK ARCHITECTURE";
        superTitle.style.color = "#2563eb";
        titleText.textContent = "AST System Model: Formal Systems Engineering & Enterprise Data Stack";
        subtitle.textContent = "Ontological Semantics · Taxonomic Classification · Relational Schema · SysML 2.0 Digital Thread · Algedonic Closed-Loop";
        badge.style.display = "inline-block";
        badge.style.backgroundColor = "#eff6ff";
        badge.style.color = "#2563eb";
        badge.style.border = "1.5px solid #bfdbfe";
        badge.textContent = "📐 MBSE ARCHITECTURE SPECIFICATION";

        body.innerHTML = `
            <div style="display:flex; flex-direction:column; width:100%; gap:14px; max-height:calc(88vh - 80px); overflow-y:auto; padding:8px;">
                <div style="background:#0f172a; border-radius:12px; border:2px solid #2563eb; overflow:hidden; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 14px rgba(0,0,0,0.25); min-height:450px;">
                    <img src="${{IMAGE_AST_SLIDE}}" alt="AST System Model" style="width:100%; height:auto; max-height:560px; object-fit:contain; display:block;" />
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;">
                    <div style="background:#fff7ed; border-left:3.5px solid #ea580c; padding:10px 12px; border-radius:0 6px 6px 0;">
                        <strong style="color:#c2410c; font-size:12.5px;">1. Ontology Semantic Representation</strong>
                        <p style="font-size:11.5px; color:#334155; margin:6px 0 0 0; line-height:1.45;">Encodes system entities, their relationships, and constraints in a formal semantic model. Answers the question: what exists in this system and how do system relationships, dependencies, and decision objectives connect to one another?</p>
                    </div>
                    <div style="background:#f0f9ff; border-left:3.5px solid #0284c7; padding:10px 12px; border-radius:0 6px 6px 0;">
                        <strong style="color:#0369a1; font-size:12.5px;">2. Taxonomy Hierarchical Classification</strong>
                        <p style="font-size:11.5px; color:#334155; margin:6px 0 0 0; line-height:1.45;">Organizes system elements into typed classes with inheritance. Enables structured reasoning about failure modes, behaviors, and decision categories across levels of abstraction.</p>
                    </div>
                    <div style="background:#f0fdfa; border-left:3.5px solid #0d9488; padding:10px 12px; border-radius:0 6px 6px 0;">
                        <strong style="color:#0f766e; font-size:12.5px;">3. Schema Data Structure and Relational Encoding</strong>
                        <p style="font-size:11.5px; color:#334155; margin:6px 0 0 0; line-height:1.45;">Translates ontological and taxonomic knowledge into structured, queryable, and traceable data linked to system requirements and observed states. Establishes traceability links between system states, requirements, and observations.</p>
                    </div>
                </div>
            </div>
        `;
        modal.classList.add("active");
        return;
    }}

    const modal = document.getElementById("modal-overlay");
    const superTitle = document.getElementById("modal-super-title");
    const titleText = document.getElementById("modal-title-text");
    const subtitle = document.getElementById("modal-subtitle");
    const badge = document.getElementById("modal-header-status-badge");
    const body = document.getElementById("modal-body-container");

    const isRust = currentScenario === "rust";
    const rustColor = isRust ? "#ef4444" : "#10b981";

    if (nodeId === "twin") {{
        superTitle.textContent = "VIRTUAL ASSET · 3D DIGITAL TWIN REPLICA";
        superTitle.style.color = "#34d399";
        titleText.textContent = "Digital Twin (DT): 3D CAD Mesh Model";
        subtitle.textContent = "MSC-TNK-B3-V2.1 · 42,850 Vertices · Real-time bidirectional telemetry sync (<180ms latency)";
        badge.style.display = "inline-block";
        badge.style.backgroundColor = isRust ? "#450a0a" : "#064e3b";
        badge.style.color = isRust ? "#f87171" : "#34d399";
        badge.style.border = `1.5px solid ${{isRust ? '#ef4444' : '#10b981'}}`;
        badge.textContent = isRust ? "⚠️ RUST DEFECT DETECTED IN CAD MESH (HEALTH: 42%)" : "🟢 TWIN SYNCHRONIZED · BULKHEAD NOMINAL (HEALTH: 98%)";

        const twinImg = isRust ? IMAGE_TWIN_RUST : IMAGE_TWIN_CLEAN;
        body.innerHTML = `
            <div style="display:flex; flex-direction:column; width:100%;">
                <div style="background:#1e293b; padding:12px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; flex-wrap:wrap; gap:12px;">
                    <div>
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:800; letter-spacing:1px; color:#94a3b8;">DIGITAL TWIN TELEMETRY &amp; CAD MESH MONITORING: </span>
                        <strong style="color:${{isRust ? '#f87171' : '#34d399'}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px;">${{isRust ? '⚠️ DEFECT EVENT ACTIVE' : '🟢 CONTINUOUS SYNC NOMINAL'}}</strong>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button onclick="setScenario('clean'); openModal('twin');" style="padding:6px 14px; border-radius:6px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:12px; cursor:pointer; background:${{!isRust ? '#10b981' : '#1e293b'}}; color:#ffffff; border:1px solid ${{!isRust ? '#10b981' : '#475569'}};">Reset Nominal</button>
                        <button onclick="setScenario('rust'); openModal('twin');" style="padding:6px 14px; border-radius:6px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:12px; cursor:pointer; background:${{isRust ? '#dc2626' : '#1e293b'}}; color:#ffffff; border:1px solid ${{isRust ? '#ef4444' : '#475569'}};">Trigger Corrosion Defect</button>
                    </div>
                </div>
                <div style="position:relative; height:460px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden; padding:16px;">
                    <img src="${{twinImg}}" alt="Digital Twin CAD Mesh" style="width:100%; height:100%; object-fit:contain; display:block; border-radius:10px; border:1.5px solid #1e293b;" />
                    <div style="position:absolute; bottom:24px; left:28px; background:rgba(15, 23, 42, 0.92); padding:6px 14px; border-radius:8px; border:1.5px solid ${{rustColor}}; color:${{rustColor}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800;">
                        ${{isRust ? '⚠️ CAD MESH REFLECTS -1.8mm CORROSION RECESS @ FRAME 38' : '🟢 BULKHEAD NOMINAL (18.0mm INTACT COATING)'}}
                    </div>
                    <div style="position:absolute; top:24px; right:28px; background:rgba(15, 23, 42, 0.88); padding:5px 12px; border-radius:6px; color:#cbd5e1; font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:700; border:1px solid #334155;">
                        Model: MSC-TNK-B3-V2.1 &middot; 42,850 Vertices
                    </div>
                </div>
                <div style="background:#0f172a; padding:14px 24px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                    <span style="color:#94a3b8; font-size:12.5px;">Real-time sync latency: <strong>&lt;180ms</strong> &middot; Mesh resolution: <strong>0.15m Voxel</strong></span>
                    <span style="color:${{rustColor}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:14px; font-weight:800;">Structural Health: ${{isRust ? '42% (Degraded)' : '98% (Nominal)'}}</span>
                </div>
            </div>
        `;
    }} else if (nodeId === "tank") {{
        superTitle.textContent = "PHYSICAL ASSET · MSC VESSEL CARGO COMPARTMENT B-3";
        superTitle.style.color = "#38bdf8";
        titleText.textContent = "MSC Ballast Tank B-3 Inspection View";
        subtitle.textContent = "Frame 38 Lower Bulkhead · Mounts LiDAR LD-01, Hyperspectral HS-01 & 4K Video";
        badge.style.display = "inline-block";
        badge.style.backgroundColor = isRust ? "#450a0a" : "#064e3b";
        badge.style.color = isRust ? "#f87171" : "#34d399";
        badge.style.border = `1.5px solid ${{isRust ? '#ef4444' : '#10b981'}}`;
        badge.textContent = isRust ? "🔴 CORROSION DEFECT DETECTED ON BULKHEAD (-1.8mm LOSS)" : "🟢 INTACT STEEL & PROTECTIVE EPOXY COATING (18.0mm)";

        const tankImg = isRust ? IMAGE_TANK_RUST : IMAGE_TANK_CLEAN;
        body.innerHTML = `
            <div style="display:flex; flex-direction:column; width:100%;">
                <div style="background:#1e293b; padding:12px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; flex-wrap:wrap; gap:12px;">
                    <div>
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:800; letter-spacing:1px; color:#94a3b8;">PHYSICAL TANK STATUS: </span>
                        <strong style="color:${{isRust ? '#f87171' : '#34d399'}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px;">${{isRust ? '🔴 ACTIVE CORROSION OBSERVED' : '🟢 CLEAN STEEL BASELINE'}}</strong>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button onclick="setScenario('clean'); openModal('tank');" style="padding:6px 14px; border-radius:6px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:12px; cursor:pointer; background:${{!isRust ? '#10b981' : '#1e293b'}}; color:#ffffff; border:1px solid ${{!isRust ? '#10b981' : '#475569'}};">Reset Nominal</button>
                        <button onclick="setScenario('rust'); openModal('tank');" style="padding:6px 14px; border-radius:6px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:12px; cursor:pointer; background:${{isRust ? '#dc2626' : '#1e293b'}}; color:#ffffff; border:1px solid ${{isRust ? '#ef4444' : '#475569'}};">Trigger Corrosion Defect</button>
                    </div>
                </div>
                <div style="position:relative; height:460px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden; padding:16px;">
                    <img src="${{tankImg}}" alt="Ballast Tank Inspection" style="width:100%; height:100%; object-fit:contain; display:block; border-radius:10px; border:1.5px solid #1e293b;" />
                    <div style="position:absolute; bottom:24px; left:28px; background:rgba(15, 23, 42, 0.92); padding:6px 14px; border-radius:8px; border:1.5px solid ${{rustColor}}; color:${{rustColor}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800;">
                        ${{isRust ? '🔴 FRAME 38: -1.8mm STEEL THICKNESS LOSS (PITTING CORROSION)' : '🟢 FRAME 38: NOMINAL 18.0mm STEEL (PROTECTIVE EPOXY INTACT)'}}
                    </div>
                    <div style="position:absolute; top:24px; right:28px; background:rgba(15, 23, 42, 0.88); padding:5px 12px; border-radius:6px; color:#cbd5e1; font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:700; border:1px solid #334155;">
                        Steel Grade NV DH36 &middot; Scantling Plan 18.0mm
                    </div>
                </div>
                <div style="background:#0f172a; padding:14px 24px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                    <span style="color:#94a3b8; font-size:12.5px;">Location: <strong>Compartment B-3, Frame 38</strong> &middot; Class Society: <strong>DNV-GL Registry</strong></span>
                    <span style="color:${{rustColor}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:14px; font-weight:800;">Plate Thickness: ${{isRust ? '16.2 mm (-1.8mm)' : '18.0 mm (Nominal)'}}</span>
                </div>
            </div>
        `;
    }} else if (nodeId === "lidar") {{
        superTitle.textContent = "EDGE SENSOR · OPTICAL TIME-OF-FLIGHT SENSOR";
        superTitle.style.color = "#38bdf8";
        titleText.textContent = "LD-01 3D Conical LiDAR Laser Scanner";
        subtitle.textContent = "Mounted on Tank Ceiling Dome · 1.2M points/sec · ±0.8mm depth accuracy · Point cloud output to SAC";
        badge.style.display = "inline-block";
        badge.style.backgroundColor = "#0c4a6e";
        badge.style.color = "#38bdf8";
        badge.style.border = "1.5px solid #0284c7";
        badge.textContent = "🔵 3D LASER SCANNING ACTIVE · POINT CLOUD BUFFER NOMINAL";

        body.innerHTML = `
            <div style="display:flex; flex-direction:column; width:100%;">
                <div style="background:#1e293b; padding:12px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800; color:#38bdf8;">RAW POINT CLOUD ACQUISITION MATRIX</span>
                    <button onclick="openPointCloudModal();" style="padding:6px 14px; border-radius:6px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:12px; cursor:pointer; background:#0284c7; color:#ffffff; border:1px solid #0284c7;">☁️ Open Point Cloud ➔ SAC Pipeline</button>
                </div>
                <div style="position:relative; height:460px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden; padding:16px;">
                    <img src="${{IMAGE_LIDAR}}" alt="LiDAR Point Cloud" style="width:100%; height:100%; object-fit:contain; display:block; border-radius:10px; border:1.5px solid #0284c7;" />
                    <div style="position:absolute; bottom:24px; left:28px; background:rgba(15, 23, 42, 0.92); padding:6px 14px; border-radius:8px; border:1.5px solid #0284c7; color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800;">
                        CloudCompare &middot; ΔX/ΔY/ΔZ Extents: 5.627m &middot; Coordinate Point Matrix (.e57)
                    </div>
                </div>
                <div style="background:#0f172a; padding:14px 24px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#94a3b8; font-size:12.5px;">Scanner: <strong>Ouster/Velodyne Marine 360°</strong> &middot; Pulse Rate: <strong>1.248M pts/sec</strong></span>
                    <button onclick="openPointCloudModal();" style="background:none; border:none; color:#38bdf8; font-weight:800; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; cursor:pointer; text-decoration:underline;">View LiDAR ➔ SAC Connection &amp; Summary &rarr;</button>
                </div>
            </div>
        `;
    }} else if (nodeId === "sac") {{
        superTitle.textContent = "COMPUTATION · FINITE ELEMENT GEOMETRIC ENGINE";
        superTitle.style.color = "#34d399";
        titleText.textContent = "SAC: Surface Area Library & Mesh Geometry Engine";
        subtitle.textContent = "Delaunay Triangulation · Volumetric & Surface Area Integration · Confidence > 0.83 Rule";
        badge.style.display = "inline-block";
        badge.style.backgroundColor = "#064e3b";
        badge.style.color = "#34d399";
        badge.style.border = "1.5px solid #10b981";
        badge.textContent = "🟢 ACCEPTANCE RULE: CONFIDENCE > 0.83";

        body.innerHTML = `
            <div style="display:flex; flex-direction:column; width:100%;">
                <div style="background:#1e293b; padding:12px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800; color:#34d399;">RECONSTRUCTED WATERTIGHT 3D SURFACE MESH</span>
                    <button onclick="openPointCloudModal();" style="padding:6px 14px; border-radius:6px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; font-size:12px; cursor:pointer; background:#10b981; color:#ffffff; border:1px solid #10b981;">☁️ Open Point Cloud ➔ SAC Pipeline</button>
                </div>
                <div style="position:relative; height:460px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden; padding:16px;">
                    <img src="${{IMAGE_SAC}}" alt="SAC Reconstructed Mesh" style="width:100%; height:100%; object-fit:contain; display:block; border-radius:10px; border:1.5px solid #10b981;" />
                    <div style="position:absolute; bottom:24px; left:28px; background:rgba(15, 23, 42, 0.92); padding:6px 14px; border-radius:8px; border:1.5px solid #10b981; color:#34d399; font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800;">
                        Blender 4.5 &middot; Voxel Remesh 0.15m &middot; Watertight Manifold Shell Area Certified
                    </div>
                </div>
                <div style="background:#0f172a; padding:14px 24px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#94a3b8; font-size:12.5px;">Mesh Algorithm: <strong>Poisson Reconstruction (Octree 10/11)</strong> &middot; Voxel Mode: <strong>0.15m</strong></span>
                    <button onclick="openPointCloudModal();" style="background:none; border:none; color:#34d399; font-weight:800; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; cursor:pointer; text-decoration:underline;">View LiDAR ➔ SAC Connection &amp; Summary &rarr;</button>
                </div>
            </div>
        `;
    }} else if (nodeId === "hyp") {{
        superTitle.textContent = "EDGE SENSOR · CHEMICAL SPECTRAL IMAGING";
        superTitle.style.color = "#38bdf8";
        titleText.textContent = "Cubert Hyperspectral Chemical Scanner (Auto_000_1123.cu3s)";
        subtitle.textContent = "450 - 850 nm VNIR Spectral Domain · Multi-Point Raw Spectral Profiling & Fe₂O₃ Oxidation Detection";
        badge.style.display = "inline-block";
        badge.style.backgroundColor = isRust ? "#450a0a" : "#064e3b";
        badge.style.color = isRust ? "#f87171" : "#34d399";
        badge.style.border = `1.5px solid ${{isRust ? '#ef4444' : '#10b981'}}`;
        badge.textContent = isRust ? "🔴 RAW SPECTRAL PEAK DETECTED (710 - 770 nm OXIDATION)" : "🟢 SPECTRAL SCAN CLEAR · NOMINAL COATING REFLECTANCE";

        body.innerHTML = `
            <div style="display:flex; flex-direction:column; width:100%;">
                <div style="position:relative; height:460px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden; padding:16px;">
                    <img src="${{IMAGE_HYP}}" alt="Hyperspectral Capture" style="width:100%; height:100%; object-fit:contain; display:block; border-radius:10px; border:1.5px solid #38bdf8;" />
                    <div style="position:absolute; bottom:24px; left:28px; background:rgba(15, 23, 42, 0.92); padding:6px 14px; border-radius:8px; border:1.5px solid #38bdf8; color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800;">
                        Cubert VNIR Hyperspectral Camera &middot; Spectral Tensor Cube
                    </div>
                </div>
                <div style="background:#0f172a; padding:14px 24px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#94a3b8; font-size:12.5px;">Spectral Bands: <strong>450nm – 850nm</strong> &middot; Target: <strong>Iron Oxide (Rust) Signature Detection</strong></span>
                    <span style="color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800;">Fe₂O₃ Spectral Peak: 735nm</span>
                </div>
            </div>
        `;
    }} else {{
        const n = SVG_NODES[nodeId] || {{ name: nodeId.toUpperCase(), about: "Active pipeline component", gives: [] }};
        superTitle.textContent = "DIGITAL TWIN ARCHITECTURE COMPONENT";
        superTitle.style.color = "#94a3b8";
        titleText.textContent = n.name;
        subtitle.textContent = n.about;
        badge.style.display = "inline-block";
        badge.style.backgroundColor = "#064e3b";
        badge.style.color = "#34d399";
        badge.style.border = "1.5px solid #10b981";
        badge.textContent = "🟢 COMPONENT ONLINE & SYNCHRONIZED";

        if (nodeId === "rgb") {{
            superTitle.textContent = "OPTICAL EDGE SENSOR · 4K VIDEO INSPECTION";
            superTitle.style.color = "#38bdf8";
            titleText.textContent = "RGB & High-Resolution Video Camera";
            subtitle.textContent = "Tank Dome Ceiling Mount · 3840×2160 UHD @ 60 FPS · IP68 Submersible · Real-Time Optical Texture Stream";
            badge.style.display = "inline-block";
            badge.style.backgroundColor = isRust ? "#450a0a" : "#064e3b";
            badge.style.color = isRust ? "#f87171" : "#34d399";
            badge.style.border = `1.5px solid ${{isRust ? '#ef4444' : '#10b981'}}`;
            badge.textContent = isRust ? "⚠️ SURFACE DEFECT DETECTED: OXIDATION & BLISTERING" : "🟢 OPTICAL STREAM NOMINAL · PROTECTIVE COATING INTACT";

            body.innerHTML = `
                <div style="display:flex; flex-direction:column; width:100%; color:#f8fafc;">
                    <div style="background:#1e293b; padding:12px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; flex-wrap:wrap; gap:12px;">
                        <div>
                            <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:800; letter-spacing:1px; color:#94a3b8;">OPTICAL TELEMETRY STREAM: </span>
                            <strong style="color:${{isRust ? '#f87171' : '#34d399'}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px;">${{isRust ? '⚠️ RUST CHROMATICITY DETECTED' : '🟢 CLEAR OPTICAL BASELINE'}}</strong>
                        </div>
                        <div style="font-family:monospace; font-size:11.5px; color:#38bdf8; background:#020617; padding:4px 12px; border-radius:6px; border:1px solid #334155;">
                            STREAM: 4K UHD 60fps &middot; BITRATE: 45 Mbps
                        </div>
                    </div>
                    <div style="position:relative; height:460px; background:#020617; display:flex; align-items:center; justify-content:center; overflow:hidden; padding:24px;">
                        <!-- Camera Telemetry Viewport -->
                        <div style="width:100%; max-width:820px; height:100%; border:1.5px solid #38bdf8; border-radius:12px; background:radial-gradient(ellipse at center, #0f172a 0%, #020617 100%); position:relative; display:flex; flex-direction:column; justify-content:space-between; padding:20px; box-sizing:border-box;">
                            <!-- Top HUD Bar -->
                            <div style="display:flex; justify-content:space-between; align-items:center; font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; color:#38bdf8;">
                                <span>[CAM-01: TANK B-3 BULKHEAD]</span>
                                <span>REC &bull; 00:42:18:04</span>
                                <span>ISO 400 &middot; F/2.8 &middot; 1/250s</span>
                            </div>
                            <!-- Crosshair Center -->
                            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); pointer-events:none; text-align:center;">
                                <div style="width:80px; height:80px; border:1px solid rgba(56, 189, 248, 0.4); border-radius:50%; margin:0 auto; display:flex; align-items:center; justify-content:center;">
                                    <div style="width:8px; height:8px; background:${{isRust ? '#ef4444' : '#10b981'}}; border-radius:50%;"></div>
                                </div>
                                <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:${{isRust ? '#fca5a5' : '#6ee7b7'}}; margin-top:6px; display:block;">
                                    ${{isRust ? '⚠️ CHROMATIC SHIFT: 18.4° (OXIDIZED OCHRE #b91c1c)' : '🟢 SURFACE HUE: 142.1° (COATING EPOXY NOMINAL)'}}
                                </span>
                            </div>
                            <!-- Bottom HUD Specs -->
                            <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; background:rgba(15, 23, 42, 0.85); padding:12px; border-radius:8px; border:1px solid #334155;">
                                <div>
                                    <span style="font-size:10px; color:#94a3b8; display:block;">SURFACE TEXTURE</span>
                                    <strong style="color:#f8fafc; font-size:12.5px;">${{isRust ? 'Rough / Exfoliating' : 'Smooth / High-Gloss'}}</strong>
                                </div>
                                <div>
                                    <span style="font-size:10px; color:#94a3b8; display:block;">COATING COVERAGE</span>
                                    <strong style="color:${{isRust ? '#f87171' : '#34d399'}}; font-size:12.5px;">${{isRust ? '84.2% (Degraded)' : '99.4% (Nominal)'}}</strong>
                                </div>
                                <div>
                                    <span style="font-size:10px; color:#94a3b8; display:block;">ORTHOPHOTO MAP</span>
                                    <strong style="color:#38bdf8; font-size:12.5px;">Geo-Referenced to Tank CAD</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div style="background:#0f172a; padding:14px 24px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                        <span style="color:#94a3b8; font-size:12.5px;">Lens: <strong>Wide-Angle Marine Sapphire Glass (110° FoV)</strong> &middot; Sensor: <strong>Sony IMX Exmor 1/1.8"</strong></span>
                        <span style="color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800;">Feeds to: SAC Mesh Texture &amp; Operator Verification</span>
                    </div>
                </div>
            `;
        }} else if (nodeId === "vtl") {{
            superTitle.textContent = "TECHNICAL DATABASE · SCANTLING & CLASS RECORDS";
            superTitle.style.color = "#34d399";
            titleText.textContent = "VTL Prototype: Virtual Technical Library";
            subtitle.textContent = "DNV-GL Class Registry · Scantling Baseline Plans · Steel Degradation Models · Compartment Frame 38";
            badge.style.display = "inline-block";
            badge.style.backgroundColor = "#064e3b";
            badge.style.color = "#34d399";
            badge.style.border = "1.5px solid #10b981";
            badge.textContent = "🟢 CLASS REGISTRY COMPLIANT &middot; DNV-GL CERTIFIED";

            body.innerHTML = `
                <div style="display:flex; flex-direction:column; width:100%; color:#f8fafc;">
                    <div style="background:#1e293b; padding:12px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; flex-wrap:wrap; gap:12px;">
                        <div>
                            <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:800; letter-spacing:1px; color:#94a3b8;">VTL SPECIFICATION DOSSIER: </span>
                            <strong style="color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px;">DNV-GL SHIP RULES PT.3 CH.3</strong>
                        </div>
                        <div style="font-family:monospace; font-size:11.5px; color:#34d399; background:#020617; padding:4px 12px; border-radius:6px; border:1px solid #334155;">
                            DOC ID: VTL-MSC-TNK-B3-REV4
                        </div>
                    </div>
                    <div style="position:relative; min-height:460px; background:#020617; display:flex; align-items:center; justify-content:center; padding:24px;">
                        <!-- Scantling Blueprint Panel -->
                        <div style="width:100%; max-width:820px; border:1.5px solid #334155; border-radius:12px; background:#0b1120; padding:24px; display:flex; flex-direction:column; gap:16px;">
                            <div style="border-bottom:1px solid #1e293b; padding-bottom:12px; display:flex; justify-content:space-between; align-items:flex-end;">
                                <div>
                                    <span style="font-size:11px; color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; letter-spacing:1px;">STRUCTURAL SCANTLING SPECIFICATION</span>
                                    <h3 style="font-size:20px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; color:#f8fafc; margin-top:2px;">Cargo Tank Compartment B-3 (Frame 36–42)</h3>
                                </div>
                                <span style="font-size:12px; color:#94a3b8;">Classification: <strong>DNV-GL NV DH36</strong></span>
                            </div>

                            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px;">
                                <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #1e293b;">
                                    <span style="font-size:11px; color:#94a3b8;">NOMINAL SCANTLING THICKNESS</span>
                                    <div style="font-size:18px; font-weight:800; color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; margin-top:2px;">18.0 mm</div>
                                    <span style="font-size:11px; color:#64748b;">Design as-built plan thickness</span>
                                </div>
                                <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #1e293b;">
                                    <span style="font-size:11px; color:#94a3b8;">CORROSION DIMINUTION LIMIT</span>
                                    <div style="font-size:18px; font-weight:800; color:#f59e0b; font-family:'Barlow Semi Condensed',sans-serif; margin-top:2px;">15.5 mm (-2.5 mm Max)</div>
                                    <span style="font-size:11px; color:#64748b;">DNV-GL mandatory steel renewal limit</span>
                                </div>
                                <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #1e293b;">
                                    <span style="font-size:11px; color:#94a3b8;">PROTECTIVE COATING SYSTEM</span>
                                    <div style="font-size:18px; font-weight:800; color:#34d399; font-family:'Barlow Semi Condensed',sans-serif; margin-top:2px;">2 &times; 160 &mu;m Pure Epoxy</div>
                                    <span style="font-size:11px; color:#64748b;">IMO PSPC Compliant Marine Barrier</span>
                                </div>
                            </div>

                            <div style="background:#0f172a; border-radius:8px; padding:14px; border:1px solid #1e293b; display:flex; flex-direction:column; gap:8px;">
                                <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800; color:#94a3b8; letter-spacing:0.8px;">DIGITAL TWIN INTEGRATION ROLE</span>
                                <p style="font-size:12.5px; color:#cbd5e1; margin:0; line-height:1.5;">
                                    The VTL provides the formal baseline CAD geometry against which LiDAR Delaunay surface reconstructions (SAC) are continuously compared. 
                                    When surface loss exceeds 1.8mm at Frame 38, VTL flags the condition and feeds technical structural compliance records directly to the Digital Twin and HMS.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div style="background:#0f172a; padding:14px 24px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                        <span style="color:#94a3b8; font-size:12.5px;">CAD Registry: <strong>STEP / IGES / IFC Marine Standard</strong> &middot; Survey Cycle: <strong>5-Year Special Survey</strong></span>
                        <span style="color:#34d399; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800;">Synchronized to Digital Twin CAD Core</span>
                    </div>
                </div>
            `;
        }} else if (nodeId === "samm" || nodeId === "lrms") {{
            superTitle.textContent = "FLEET DECISION LAYER · MAINTENANCE OPTIMIZATION";
            superTitle.style.color = "#38bdf8";
            titleText.textContent = "LRMS: Long Range Maintenance Schedule";
            subtitle.textContent = "Condition-Based Maintenance (CBM) Policy Engine · Drydock Work Pack Optimization · Repair ROI Modeling";
            badge.style.display = "inline-block";
            badge.style.backgroundColor = isRust ? "#450a0a" : "#064e3b";
            badge.style.color = isRust ? "#f87171" : "#34d399";
            badge.style.border = `1.5px solid ${{isRust ? '#ef4444' : '#10b981'}}`;
            badge.textContent = isRust ? "⚠️ ACTION DISPATCHED: DRYDOCK WORK PACK #4092 GENERATED" : "🟢 LRMS POLICY NOMINAL &middot; NO IMMEDIATE STEEL INTERVENTION";

            body.innerHTML = `
                <div style="display:flex; flex-direction:column; width:100%; color:#f8fafc;">
                    <div style="background:#1e293b; padding:12px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; flex-wrap:wrap; gap:12px;">
                        <div>
                            <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:800; letter-spacing:1px; color:#94a3b8;">CBM POLICY STATUS: </span>
                            <strong style="color:${{isRust ? '#f87171' : '#34d399'}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px;">${{isRust ? '⚠️ WORK PACK WP-B3-2026 DISPATCHED' : '🟢 MAINTENANCE SCHEDULE ON TRACK'}}</strong>
                        </div>
                        <div style="font-family:monospace; font-size:11.5px; color:#38bdf8; background:#020617; padding:4px 12px; border-radius:6px; border:1px solid #334155;">
                            POLICY: CONDITION-BASED MAINTENANCE (CBM)
                        </div>
                    </div>
                    <div style="position:relative; min-height:460px; background:#020617; display:flex; align-items:center; justify-content:center; padding:24px;">
                        <!-- Maintenance Operations Panel -->
                        <div style="width:100%; max-width:820px; border:1.5px solid #334155; border-radius:12px; background:#0b1120; padding:24px; display:flex; flex-direction:column; gap:16px;">
                            <div style="border-bottom:1px solid #1e293b; padding-bottom:12px; display:flex; justify-content:space-between; align-items:flex-end;">
                                <div>
                                    <span style="font-size:11px; color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; letter-spacing:1px;">DRYDOCK &amp; VOYAGE INTERVENTION PLANNER</span>
                                    <h3 style="font-size:20px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; color:#f8fafc; margin-top:2px;">Tank B-3 Condition-Based Work Schedule</h3>
                                </div>
                                <span style="font-size:12px; color:#94a3b8;">Schedule Window: <strong>Next Drydock (Q3 2026)</strong></span>
                            </div>

                            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px;">
                                <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #1e293b;">
                                    <span style="font-size:11px; color:#94a3b8;">RECOMMENDED INTERVENTION</span>
                                    <div style="font-size:16px; font-weight:800; color:${{isRust ? '#ef4444' : '#34d399'}}; font-family:'Barlow Semi Condensed',sans-serif; margin-top:2px;">
                                        ${{isRust ? 'Sa 2.5 Hydro-Blast &amp; Recoat' : 'Routine Spot Inspection Only'}}
                                    </div>
                                    <span style="font-size:11px; color:#64748b;">Targeted Frame 38 repair pack</span>
                                </div>
                                <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #1e293b;">
                                    <span style="font-size:11px; color:#94a3b8;">DRYDOCK COST AVOIDANCE</span>
                                    <div style="font-size:16px; font-weight:800; color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; margin-top:2px;">68% Cost Savings</div>
                                    <span style="font-size:11px; color:#64748b;">Vs emergency plate cropping &amp; renewal</span>
                                </div>
                                <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #1e293b;">
                                    <span style="font-size:11px; color:#94a3b8;">BIDIRECTIONAL LINK</span>
                                    <div style="font-size:16px; font-weight:800; color:#a855f7; font-family:'Barlow Semi Condensed',sans-serif; margin-top:2px;">Direct to HMS &amp; Tank</div>
                                    <span style="font-size:11px; color:#64748b;">Actions flow directly to ballast asset</span>
                                </div>
                            </div>

                            <div style="background:#0f172a; border-radius:8px; padding:14px; border:1px solid #1e293b; display:flex; flex-direction:column; gap:8px;">
                                <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800; color:#94a3b8; letter-spacing:0.8px;">OPERATIONAL IMPACT SUMMARY</span>
                                <p style="font-size:12.5px; color:#cbd5e1; margin:0; line-height:1.5;">
                                    LRMS acts as the decision-making counterpart to the Digital Twin. While the Digital Twin visualizes and monitors the physical state in real time, 
                                    LRMS translates defect telemetry into concrete drydock maintenance work packs, preventing catastrophic steel wastage and optimizing vessel operational uptime.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div style="background:#0f172a; padding:14px 24px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                        <span style="color:#94a3b8; font-size:12.5px;">Integration: <strong>Enterprise ERP / Drydock Work Management System</strong></span>
                        <span style="color:#38bdf8; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800;">Bidirectional Maintenance &amp; Hull Loop</span>
                    </div>
                </div>
            `;
        }} else if (nodeId === "cms" || nodeId === "hms") {{
            superTitle.textContent = "FLEET PREDICTIVE LAYER · HULL HEALTH ANALYTICS";
            superTitle.style.color = "#34d399";
            titleText.textContent = "HMS: Hull Maintenance System";
            subtitle.textContent = "Fleet-Wide Predictive Analytics · Remaining Useful Life (RUL) Modeling · Structural Degradation Forecasting";
            badge.style.display = "inline-block";
            badge.style.backgroundColor = isRust ? "#450a0a" : "#064e3b";
            badge.style.color = isRust ? "#f87171" : "#34d399";
            badge.style.border = `1.5px solid ${{isRust ? '#ef4444' : '#10b981'}}`;
            badge.textContent = isRust ? "⚠️ RUL UPDATED: EXPEDITE LOCALIZED COATING REPAIR" : "🟢 FLEET HULL HEALTH INDEX (HHI): 94.2 / 100 NOMINAL";

            body.innerHTML = `
                <div style="display:flex; flex-direction:column; width:100%; color:#f8fafc;">
                    <div style="background:#1e293b; padding:12px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; flex-wrap:wrap; gap:12px;">
                        <div>
                            <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11.5px; font-weight:800; letter-spacing:1px; color:#94a3b8;">FLEET ANALYTICS STREAM: </span>
                            <strong style="color:${{isRust ? '#f87171' : '#34d399'}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px;">${{isRust ? '⚠️ STRUCTURAL DEGRADATION DETECTED' : '🟢 FLEET LEADING HEALTH PROFILE'}}</strong>
                        </div>
                        <div style="font-family:monospace; font-size:11.5px; color:#34d399; background:#020617; padding:4px 12px; border-radius:6px; border:1px solid #334155;">
                            CORROSION MODEL: MODIFIED POWER-LAW
                        </div>
                    </div>
                    <div style="position:relative; min-height:460px; background:#020617; display:flex; align-items:center; justify-content:center; padding:24px;">
                        <!-- Fleet Analytics Dashboard Panel -->
                        <div style="width:100%; max-width:820px; border:1.5px solid #334155; border-radius:12px; background:#0b1120; padding:24px; display:flex; flex-direction:column; gap:16px;">
                            <div style="border-bottom:1px solid #1e293b; padding-bottom:12px; display:flex; justify-content:space-between; align-items:flex-end;">
                                <div>
                                    <span style="font-size:11px; color:#34d399; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; letter-spacing:1px;">FLEET INTEGRITY MANAGEMENT</span>
                                    <h3 style="font-size:20px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:800; color:#f8fafc; margin-top:2px;">Hull Maintenance System (HMS) Analytics</h3>
                                </div>
                                <span style="font-size:12px; color:#94a3b8;">Vessel Asset: <strong>MSC Ballast Tank B-3</strong></span>
                            </div>

                            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px;">
                                <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #1e293b;">
                                    <span style="font-size:11px; color:#94a3b8;">HULL HEALTH INDEX (HHI)</span>
                                    <div style="font-size:18px; font-weight:800; color:${{isRust ? '#f87171' : '#34d399'}}; font-family:'Barlow Semi Condensed',sans-serif; margin-top:2px;">
                                        ${{isRust ? '64.8 / 100' : '94.2 / 100'}}
                                    </div>
                                    <span style="font-size:11px; color:#64748b;">Fleet median: 91.0 / 100</span>
                                </div>
                                <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #1e293b;">
                                    <span style="font-size:11px; color:#94a3b8;">REMAINING USEFUL LIFE (RUL)</span>
                                    <div style="font-size:18px; font-weight:800; color:${{isRust ? '#f59e0b' : '#38bdf8'}}; font-family:'Barlow Semi Condensed',sans-serif; margin-top:2px;">
                                        ${{isRust ? '8.4 Years (Accelerated)' : '14.8 Years (Nominal)'}}
                                    </div>
                                    <span style="font-size:11px; color:#64748b;">Calibrated against Cubert VNIR &amp; LiDAR</span>
                                </div>
                                <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #1e293b;">
                                    <span style="font-size:11px; color:#94a3b8;">CLASS COMPLIANCE FORECAST</span>
                                    <div style="font-size:18px; font-weight:800; color:#34d399; font-family:'Barlow Semi Condensed',sans-serif; margin-top:2px;">100% Survey Ready</div>
                                    <span style="font-size:11px; color:#64748b;">Zero class conditions of survey</span>
                                </div>
                            </div>

                            <div style="background:#0f172a; border-radius:8px; padding:14px; border:1px solid #1e293b; display:flex; flex-direction:column; gap:8px;">
                                <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:12px; font-weight:800; color:#94a3b8; letter-spacing:0.8px;">ENTERPRISE EXPANSION &amp; FLEET FEDERATION</span>
                                <p style="font-size:12.5px; color:#cbd5e1; margin:0; line-height:1.5;">
                                    HMS ingests the 3D Digital Twin mesh data to evaluate long-term wear curves across all identical sister vessels in the fleet. 
                                    By cross-referencing paint condition data from VTL with real-time sensor streams, HMS enables proactive drydock procurement months in advance.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div style="background:#0f172a; padding:14px 24px; border-top:1px solid #334155; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                        <span style="color:#94a3b8; font-size:12.5px;">Analytics Engine: <strong>Predictive Hull Degradation Neural Model</strong> &middot; Data Scope: <strong>Fleet-Wide</strong></span>
                        <span style="color:#34d399; font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800;">Enterprise DT Telemetry Integrated</span>
                    </div>
                </div>
            `;
        }} else {{
            const varName = nodeId === "samm" ? "LRMS" : nodeId === "cms" ? "HMS" : nodeId.toUpperCase();
            body.innerHTML = `
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:48px 24px; width:100%;">
                    <div class="image-slot-container" style="max-width:680px; width:100%; border:1.5px solid #334155; border-radius:16px; padding:40px 32px; display:flex; flex-direction:column; align-items:center; text-align:center; background:#0f172a;">
                        <h3 style="font-family:'Barlow Semi Condensed',sans-serif; font-size:22px; color:#f8fafc; margin-bottom:8px;">${{n.name}}</h3>
                        <p style="color:#94a3b8; font-size:13.5px; line-height:1.5; margin-bottom:18px;">${{n.about}}</p>
                        <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:8px; margin-bottom:16px;">
                            ${{n.gives.map(g => `<span style="background:#1e293b; color:#38bdf8; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:700; border:1px solid #334155;">${{g}}</span>`).join('')}}
                        </div>
                        <div class="code-badge" style="background:#020617; border:1px solid #334155; padding:6px 14px; border-radius:6px; font-family:monospace; color:#38bdf8; font-size:12px;">Telemetry Stream: Synchronized &middot; Interface: REST / WebSocket API</div>
                    </div>
                </div>
            `;
        }}
    }}

    modal.classList.add("active");
}}

document.getElementById("btn-modal-close").addEventListener("click", () => {{
    document.getElementById("modal-overlay").classList.remove("active");
}});
document.getElementById("modal-overlay").addEventListener("click", (e) => {{
    if (e.target.id === "modal-overlay") document.getElementById("modal-overlay").classList.remove("active");
}});

/* Phase 3 Simulation View Switcher */
function switchViewMode(mode) {{
    viewMode = mode;
    const diagView = document.getElementById("svg-diagram-mount");
    const simView = document.getElementById("sim-viewport");
    const btnGraph = document.getElementById("btn-mode-graph");
    const btnSim = document.getElementById("btn-mode-sim");

    if (mode === "sim") {{
        diagView.style.display = "none";
        simView.style.display = "flex";
        simView.classList.remove("view-enter-anim");
        void simView.offsetWidth;
        simView.classList.add("view-enter-anim");
        btnGraph.classList.remove("active");
        btnSim.classList.add("active");
        renderSimSvg();
    }} else {{
        diagView.style.display = "block";
        diagView.classList.remove("view-enter-anim");
        void diagView.offsetWidth;
        diagView.classList.add("view-enter-anim");
        simView.style.display = "none";
        btnGraph.classList.add("active");
        btnSim.classList.remove("active");
    }}
}}

document.getElementById("btn-mode-graph").addEventListener("click", () => switchViewMode("graph"));
document.getElementById("btn-mode-sim").addEventListener("click", () => switchViewMode("sim"));

function setScenario(sc) {{
    currentScenario = sc;
    document.getElementById("btn-trigger-rust").classList.toggle("active", sc === "rust");
    document.getElementById("btn-trigger-clean").classList.toggle("active", sc === "clean");
    const badge = document.getElementById("sim-status-badge");
    if (sc === "rust") {{
        badge.textContent = "⚠️ RUST DEFECT DETECTED @ FRAME 38 (16.2mm)";
        badge.style.background = "#450a0a";
        badge.style.color = "#f87171";
        badge.style.borderColor = "#ef4444";
    }} else {{
        badge.textContent = "🟢 BULKHEAD NOMINAL (18.0mm)";
        badge.style.background = "#064e3b";
        badge.style.color = "#34d399";
        badge.style.borderColor = "#10b981";
    }}
    renderSimSvg();
}}

document.getElementById("btn-trigger-rust").addEventListener("click", () => setScenario("rust"));
document.getElementById("btn-trigger-clean").addEventListener("click", () => setScenario("clean"));

function renderSimSvg() {{
    const container = document.getElementById("sim-svg-container");
    const isRust = currentScenario === "rust";
    const rustColor = isRust ? "#ef4444" : "#10b981";
    const thickness = isRust ? "16.2 mm (-1.8mm recess)" : "18.0 mm (nominal)";
    const tankImg = isRust ? IMAGE_TANK_RUST : IMAGE_TANK_CLEAN;
    const twinImg = isRust ? IMAGE_TWIN_RUST : IMAGE_TWIN_CLEAN;

    container.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:16px; width:100%; height:100%; overflow-y:auto; padding:12px;">
            <!-- Side-by-Side Dual Card View: Real Ship vs Digital Twin CAD -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:18px;">
                
                <!-- Card 1: Physical Asset (Ballast Tank B-3 Cutaway) -->
                <div style="background:#0f172a; border-radius:14px; border:2.5px solid ${{isRust ? '#ef4444' : '#334155'}}; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 8px 24px rgba(0,0,0,0.3);">
                    <div style="background:#1e293b; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800; color:#f8fafc;">⚓ REAL SHIP: BALLAST TANK B-3 CUTAWAY</span>
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; padding:3px 10px; border-radius:6px; background:${{isRust ? '#dc2626' : '#059669'}}; color:#ffffff;">
                            ${{isRust ? '⚠️ CORROSION @ FRAME 38' : '🟢 NOMINAL BASELINE'}}
                        </span>
                    </div>
                    <div style="position:relative; height:340px; background:#020617; display:flex; align-items:center; justify-content:center; cursor:pointer;" onclick="openModal('tank')">
                        ${{tankImg ? `<img src="${{tankImg}}" alt="Real MSC Ballast Tank" style="width:100%; height:100%; object-fit:contain; display:block;" />` : '<div style=\"color:#64748b;\">No Image Available</div>'}}
                        <div style="position:absolute; bottom:12px; left:12px; background:rgba(15, 23, 42, 0.9); padding:5px 12px; border-radius:6px; border:1px solid ${{rustColor}}; color:${{rustColor}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800;">
                            ${{isRust ? '🔴 CORROSION DETECTED: -1.8mm THICKNESS LOSS' : '⚓ INTACT STEEL & PROTECTIVE EPOXY'}}
                        </div>
                        <div style="position:absolute; top:12px; right:12px; background:rgba(15, 23, 42, 0.85); padding:4px 8px; border-radius:6px; color:#94a3b8; font-size:11px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:700;">
                            🔍 Click to Enlarge
                        </div>
                    </div>
                </div>

                <!-- Card 2: Virtual Digital Twin 3D CAD Mesh -->
                <div style="background:#0f172a; border-radius:14px; border:2.5px solid ${{isRust ? '#ef4444' : '#38bdf8'}}; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 8px 24px rgba(0,0,0,0.3);">
                    <div style="background:#1e293b; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:13px; font-weight:800; color:#38bdf8;">🌐 DIGITAL TWIN: 3D CAD MESH &amp; TELEMETRY</span>
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; padding:3px 10px; border-radius:6px; background:${{isRust ? '#450a0a' : '#064e3b'}}; color:${{isRust ? '#f87171' : '#34d399'}}; border:1px solid ${{rustColor}};">
                            ${{isRust ? '⚠️ ACTIVE RUST IN CAD MESH (HEALTH: 42%)' : '🟢 SYNCHRONIZED (HEALTH: 98%)'}}
                        </span>
                    </div>
                    <div style="position:relative; height:340px; background:#020617; display:flex; align-items:center; justify-content:center; cursor:pointer;" onclick="openModal('twin')">
                        ${{twinImg ? `<img src="${{twinImg}}" alt="Digital Twin 3D CAD Model" style="width:100%; height:100%; object-fit:contain; display:block;" />` : '<div style=\"color:#64748b;\">No Image Available</div>'}}
                        <div style="position:absolute; bottom:12px; left:12px; background:rgba(15, 23, 42, 0.9); padding:5px 12px; border-radius:6px; border:1px solid ${{rustColor}}; color:${{rustColor}}; font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800;">
                            ${{isRust ? '⚠️ CAD MESH REFLECTS -1.8mm LOSS @ FR 38' : '🟢 BULKHEAD NOMINAL (18.0mm)'}}
                        </div>
                        <div style="position:absolute; top:12px; right:12px; background:rgba(15, 23, 42, 0.85); padding:4px 8px; border-radius:6px; color:#94a3b8; font-size:11px; font-family:'Barlow Semi Condensed',sans-serif; font-weight:700;">
                            🔍 Click to Enlarge
                        </div>
                    </div>
                </div>

            </div>

            <!-- Engineering Telemetry HUD Bar -->
            <div style="background:#0f172a; border-radius:12px; border:1px solid #334155; padding:14px 20px; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:16px;">
                <div style="display:flex; flex-direction:column; gap:4px;">
                    <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#94a3b8; letter-spacing:1px;">SYNCHRONIZATION TELEMETRY</span>
                    <span style="font-family:'Inter',sans-serif; font-size:13px; color:#f8fafc;">Real-time bidirectional sync &middot; Latency: <strong>&lt;180ms</strong> &middot; Model: <strong>MSC-TNK-B3-V2.1</strong></span>
                </div>
                <div style="display:flex; gap:24px;">
                    <div style="display:flex; flex-direction:column; gap:2px;">
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#94a3b8;">PLATE THICKNESS (FR 38)</span>
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:20px; font-weight:800; color:${{rustColor}};">${{thickness}}</span>
                    </div>
                    <div style="display:flex; flex-direction:column; gap:2px;">
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:11px; font-weight:800; color:#94a3b8;">STRUCTURAL INTEGRITY</span>
                        <span style="font-family:'Barlow Semi Condensed',sans-serif; font-size:20px; font-weight:800; color:${{rustColor}};">${{isRust ? '42% (Degraded)' : '98% (Nominal)'}}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}}

/* Keyboard Navigation (Arrow Keys) */
window.addEventListener('keydown', (e) => {{
    if (e.target.closest && e.target.closest("button, [role=button], input")) return;
    const curIdx = PHASE_ORDER.indexOf(currentPhase);
    if (e.key === 'ArrowLeft' && curIdx > 0) goToPhase(PHASE_ORDER[curIdx - 1]);
    if (e.key === 'ArrowRight' && curIdx < PHASE_ORDER.length - 1) goToPhase(PHASE_ORDER[curIdx + 1]);
    if (e.key === 'Escape') {{
        document.getElementById("modal-overlay").classList.remove("active");
        if (selectedNode) selectNode(null);
    }}
}});

// Startup
initDiagram();
goToPhase(1);
</script>

</body>
</html>'''

    import shutil
    output_path = os.environ.get("OUTPUT_HTML_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "digital_twin_story.html")
    alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dt-story.html")
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    brain_path = os.path.join(r"C:\Users\hruda\.gemini\antigravity-cli\brain\b51f71d1-147f-44d7-b87c-b1b7b9cac7f5", "digital_twin_story.html")

    for p in (output_path, alt_path, index_path, brain_path):
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Wrote {p} ({os.path.getsize(p)} bytes)")
        except Exception as e:
            print(f"Notice writing {p}: {e}")

    return output_path

if __name__ == "__main__":
    generate_html()
