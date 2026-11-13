# Digital Twin Story Timeline — MSC Ballast Tank Inspection

An interactive architectural timeline and simulation platform tracking the journey of the MSC Ballast Tank digital twin through 4 foundational phases:

1. **Phase 1: Separate Projects (Independent Foundation)**: Establishes the physical Ballast Tank and its onboard sensor array (3D LiDAR scanner, RGB/optical camera, and Hyperspectral chemical scanner).
2. **Phase 2: Connected Projects (Early Integration)**: Connects the LiDAR point cloud directly to the SAC (Surface Area Calculation) engine, which feeds verified scantling models to the VTL (Virtual Technical Library).
3. **Phase 3: The Digital Twin (Full Synchronization)**: Live bidirectional synchronization between the physical Ballast Tank and the virtual 3D CAD mesh, featuring interactive corrosion simulation (-1.8mm plate recess @ Frame 38).
4. **Phase 4: Beyond the Twin (External Expansion)**: DT feeds HMS (Hull Maintenance System) for fleet awareness and LRMS (Long Range Maintenance Schedule) for maintenance decisions.

---

## 🌐 Instant Web Hosting (GitHub Pages / Vercel / Netlify)

The entire application is bundled as a single, self-contained [`index.html`](index.html) file with all styling, scripts, and high-definition image assets embedded directly as base64 data URIs. No external dependencies, server runtime, or database required.

### Deploy to GitHub Pages in 3 Steps:
1. Push this repository to GitHub.
2. In your repo on GitHub, go to **Settings** ➔ **Pages**.
3. Under **Build and deployment** ➔ **Branch**, select `main` and `/ (root)`, then click **Save**.
4. Your website is live in ~60 seconds at `https://<your-username>.github.io/<your-repo-name>/`.

---

## 🐍 Local Python / Dash Application

You can also run the full interactive Python Dash server:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the application
python story_app.py
```

Open your browser to `http://127.0.0.1:8050/`.
