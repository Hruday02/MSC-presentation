# Test SVG generator for Ship Tank & Sensors
def generate_test_svg(scenario="rust"):
    rust_elements = ""
    if scenario == "rust":
        rust_elements = """
        <!-- Rust & Corrosion Patches -->
        <g id="rust-defect" filter="url(#drop-shadow)">
            <!-- Outer corrosion halo -->
            <path d="M 720 270 Q 745 260 765 275 Q 780 295 765 320 Q 740 345 715 330 Q 700 305 720 270 Z" fill="#7c2d12" opacity="0.9" />
            <!-- Inner pitting & oxidation -->
            <path d="M 725 280 Q 745 272 760 285 Q 770 302 758 318 Q 738 335 722 322 Q 712 300 725 280 Z" fill="#c2410c" />
            <path d="M 732 290 Q 748 285 754 295 Q 760 308 750 314 Q 738 320 730 310 Q 724 298 732 290 Z" fill="#ea580c" />
            <!-- Rust droplets & running stains -->
            <path d="M 735 325 Q 736 345 737 365" stroke="#9a3412" stroke-width="3" stroke-linecap="round" opacity="0.8" />
            <path d="M 748 322 Q 750 350 749 375" stroke="#7c2d12" stroke-width="3.5" stroke-linecap="round" opacity="0.85" />
            <path d="M 760 315 Q 762 338 761 355" stroke="#c2410c" stroke-width="2.5" stroke-linecap="round" opacity="0.75" />
            <!-- Pulsing defect target rings -->
            <circle cx="742" cy="302" r="28" stroke="#ef4444" stroke-width="2.5" fill="none" opacity="0.8" stroke-dasharray="4 3" />
            <circle cx="742" cy="302" r="16" stroke="#f59e0b" stroke-width="2" fill="rgba(239, 68, 68, 0.2)" />
            <circle cx="742" cy="302" r="5" fill="#ef4444" />
        </g>
        """
    print(f"Generated scenario {scenario}, length: {len(rust_elements)}")

generate_test_svg("rust")
generate_test_svg("clean")
