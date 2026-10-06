#!/usr/bin/env python3
"""
Icon Generator for Call Recorder macOS App
Generates:
1. High-resolution macOS App Icon (SVG, PNG 1024x1024 down to 16x16, AppIcon.icns)
2. macOS Menu Bar icons (Idle Template, Recording Active, Paused)
3. Web Dashboard Brand Icon & Favicon (SVG and PNG)
"""

import os
import subprocess
import AppKit

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
WEB_DIR = os.path.join(PROJECT_DIR, "web")
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Main App Icon SVG (macOS Squircle with Sleek Modern Aesthetic)
# -------------------------------------------------------------
APP_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
  <defs>
    <!-- Background Gradients -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1E2330" />
      <stop offset="45%" stop-color="#131620" />
      <stop offset="100%" stop-color="#0A0B10" />
    </linearGradient>

    <radialGradient id="ambientGlow" cx="50%" cy="40%" r="65%">
      <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.22" />
      <stop offset="40%" stop-color="#8B5CF6" stop-opacity="0.14" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>

    <!-- Top Specular Border -->
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.28" />
      <stop offset="30%" stop-color="#FFFFFF" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.02" />
    </linearGradient>

    <!-- Microphone Capsule Gradients -->
    <linearGradient id="capsuleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="60%" stop-color="#E2E8F0" />
      <stop offset="100%" stop-color="#CBD5E1" />
    </linearGradient>

    <linearGradient id="capsuleInnerGlow" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.9" />
      <stop offset="100%" stop-color="#94A3B8" stop-opacity="0.1" />
    </linearGradient>

    <!-- Acoustic Wave Gradients -->
    <linearGradient id="waveGradInner" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="50%" stop-color="#6366F1" />
      <stop offset="100%" stop-color="#A855F7" />
    </linearGradient>

    <linearGradient id="waveGradOuter" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#60A5FA" stop-opacity="0.85" />
      <stop offset="50%" stop-color="#818CF8" stop-opacity="0.75" />
      <stop offset="100%" stop-color="#C084FC" stop-opacity="0.85" />
    </linearGradient>

    <!-- Cradle & Stand Gradient -->
    <linearGradient id="standGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#8B5CF6" />
    </linearGradient>

    <!-- Recording Indicator Dot Gradients -->
    <radialGradient id="recHalo" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FF3B30" stop-opacity="0.8" />
      <stop offset="50%" stop-color="#FF3B30" stop-opacity="0.3" />
      <stop offset="100%" stop-color="#FF3B30" stop-opacity="0" />
    </radialGradient>

    <linearGradient id="recGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF6961" />
      <stop offset="40%" stop-color="#FF3B30" />
      <stop offset="100%" stop-color="#C60B00" />
    </linearGradient>

    <!-- Soft Drop Shadow Filter for Squircle -->
    <filter id="squircleShadow" x="-10%" y="-10%" width="120%" height="125%">
      <feDropShadow dx="0" dy="24" stdDeviation="32" flood-color="#000000" flood-opacity="0.55" />
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.35" />
    </filter>

    <!-- Element Glow Filter -->
    <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- 1. Apple macOS Continuous Squircle Base -->
  <g filter="url(#squircleShadow)">
    <rect x="100" y="100" width="824" height="824" rx="185" ry="185" fill="url(#bgGrad)" />
    <!-- Ambient Radial Light -->
    <rect x="100" y="100" width="824" height="824" rx="185" ry="185" fill="url(#ambientGlow)" />
    <!-- Specular Beveled Inner Border -->
    <rect x="100" y="100" width="824" height="824" rx="185" ry="185" fill="none" stroke="url(#borderGrad)" stroke-width="3" />
  </g>

  <!-- 2. Acoustic Dialogue Waves (Left & Right) -->
  <g filter="url(#neonGlow)">
    <!-- Outer Waves -->
    <path d="M 285, 360 C 235, 435 235, 545 285, 620"
          fill="none" stroke="url(#waveGradOuter)" stroke-width="15" stroke-linecap="round" />
    <path d="M 739, 360 C 789, 435 789, 545 739, 620"
          fill="none" stroke="url(#waveGradOuter)" stroke-width="15" stroke-linecap="round" />

    <!-- Inner Waves -->
    <path d="M 345, 410 C 310, 455 310, 525 345, 570"
          fill="none" stroke="url(#waveGradInner)" stroke-width="16" stroke-linecap="round" />
    <path d="M 679, 410 C 714, 455 714, 525 679, 570"
          fill="none" stroke="url(#waveGradInner)" stroke-width="16" stroke-linecap="round" />
  </g>

  <!-- 3. Microphone Stand & Cradle -->
  <g filter="url(#neonGlow)">
    <!-- Cradle Arc cupping capsule bottom -->
    <path d="M 405, 480 C 405, 575 450, 608 512, 608 C 574, 608 619, 575 619, 480"
          fill="none" stroke="url(#standGrad)" stroke-width="18" stroke-linecap="round" />
    <!-- Vertical Stem -->
    <line x1="512" y1="608" x2="512" y2="676"
          stroke="url(#standGrad)" stroke-width="18" stroke-linecap="round" />
    <!-- Base Foot -->
    <line x1="436" y1="676" x2="588" y2="676"
          stroke="url(#standGrad)" stroke-width="18" stroke-linecap="round" />
  </g>

  <!-- 4. Central Microphone Capsule -->
  <g>
    <!-- Soft Drop Shadow under Capsule -->
    <rect x="444" y="340" width="136" height="236" rx="68" ry="68"
          fill="#000000" opacity="0.4" />
    <!-- Main Capsule Body -->
    <rect x="444" y="336" width="136" height="236" rx="68" ry="68"
          fill="url(#capsuleGrad)" />
    <!-- Subtle Inner Highlight Rim -->
    <rect x="447" y="339" width="130" height="230" rx="65" ry="65"
          fill="none" stroke="url(#capsuleInnerGlow)" stroke-width="3" />
    <!-- Minimalist Acoustic Slit / Mesh divider -->
    <line x1="462" y1="446" x2="562" y2="446"
          stroke="#94A3B8" stroke-width="4" stroke-linecap="round" opacity="0.6" />
    <circle cx="512" cy="400" r="5" fill="#94A3B8" opacity="0.5" />
    <circle cx="490" cy="400" r="4" fill="#94A3B8" opacity="0.4" />
    <circle cx="534" cy="400" r="4" fill="#94A3B8" opacity="0.4" />
  </g>

  <!-- 5. Vivid Ruby Recording Indicator Node -->
  <g>
    <!-- Ambient Halo Glow -->
    <circle cx="606" cy="336" r="46" fill="url(#recHalo)" />
    <!-- Outer Rim -->
    <circle cx="606" cy="336" r="23" fill="#131620" />
    <!-- Core Recording Dot -->
    <circle cx="606" cy="336" r="19" fill="url(#recGrad)" />
    <!-- Specular Highlight for Gem-like Glass Feel -->
    <circle cx="601" cy="331" r="5.5" fill="#FFFFFF" opacity="0.85" />
  </g>
</svg>
"""

# -------------------------------------------------------------
# 2. Menu Bar Icon SVGs (Minimalist Silhouette for macOS Status Bar)
# Canvas: 44x44 px (Retina @2x for 22x22 pt)
# -------------------------------------------------------------

# Idle State: Monochrome Template (macOS inverts in light/dark mode)
MENU_ICON_TEMPLATE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44" width="44" height="44">
  <!-- Central Microphone Capsule -->
  <rect x="17" y="7" width="10" height="17" rx="5" ry="5" fill="#000000" />
  
  <!-- Cradle Arc -->
  <path d="M 12.5, 18.5 C 12.5, 25 16.5, 28 22, 28 C 27.5, 28 31.5, 25 31.5, 18.5"
        fill="none" stroke="#000000" stroke-width="2.6" stroke-linecap="round" />
        
  <!-- Stem & Base Foot -->
  <line x1="22" y1="28" x2="22" y2="34" stroke="#000000" stroke-width="2.6" stroke-linecap="round" />
  <line x1="16" y1="34" x2="28" y2="34" stroke="#000000" stroke-width="2.6" stroke-linecap="round" />

  <!-- Acoustic Dialogue Waves (Left & Right) -->
  <path d="M 7.5, 14 C 5.5, 17.5 5.5, 22.5 7.5, 26"
        fill="none" stroke="#000000" stroke-width="2.3" stroke-linecap="round" />
  <path d="M 36.5, 14 C 38.5, 17.5 38.5, 22.5 36.5, 26"
        fill="none" stroke="#000000" stroke-width="2.3" stroke-linecap="round" />
</svg>
"""

# Recording State: Vivid Crimson Red with Active Recording Pulse
MENU_ICON_RECORDING_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44" width="44" height="44">
  <!-- Central Microphone Capsule in Vivid Red -->
  <rect x="17" y="7" width="10" height="17" rx="5" ry="5" fill="#EF4444" />
  
  <!-- Cradle Arc -->
  <path d="M 12.5, 18.5 C 12.5, 25 16.5, 28 22, 28 C 27.5, 28 31.5, 25 31.5, 18.5"
        fill="none" stroke="#EF4444" stroke-width="2.6" stroke-linecap="round" />
        
  <!-- Stem & Base Foot -->
  <line x1="22" y1="28" x2="22" y2="34" stroke="#EF4444" stroke-width="2.6" stroke-linecap="round" />
  <line x1="16" y1="34" x2="28" y2="34" stroke="#EF4444" stroke-width="2.6" stroke-linecap="round" />

  <!-- Acoustic Dialogue Waves -->
  <path d="M 7.5, 14 C 5.5, 17.5 5.5, 22.5 7.5, 26"
        fill="none" stroke="#EF4444" stroke-width="2.3" stroke-linecap="round" />
  <path d="M 36.5, 14 C 38.5, 17.5 38.5, 22.5 36.5, 26"
        fill="none" stroke="#EF4444" stroke-width="2.3" stroke-linecap="round" />

  <!-- Recording Pulse Dot Badge -->
  <circle cx="35" cy="7.5" r="5.5" fill="#B91C1C" />
  <circle cx="35" cy="7.5" r="4.2" fill="#FF453A" />
  <circle cx="33.8" cy="6.3" r="1.2" fill="#FFFFFF" opacity="0.9" />
</svg>
"""

# Paused State: Amber Yellow
MENU_ICON_PAUSED_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44" width="44" height="44">
  <!-- Central Microphone Capsule in Amber -->
  <rect x="17" y="7" width="10" height="17" rx="5" ry="5" fill="#F59E0B" />
  
  <!-- Cradle Arc -->
  <path d="M 12.5, 18.5 C 12.5, 25 16.5, 28 22, 28 C 27.5, 28 31.5, 25 31.5, 18.5"
        fill="none" stroke="#F59E0B" stroke-width="2.6" stroke-linecap="round" />
        
  <!-- Stem & Base Foot -->
  <line x1="22" y1="28" x2="22" y2="34" stroke="#F59E0B" stroke-width="2.6" stroke-linecap="round" />
  <line x1="16" y1="34" x2="28" y2="34" stroke="#F59E0B" stroke-width="2.6" stroke-linecap="round" />

  <!-- Acoustic Dialogue Waves -->
  <path d="M 7.5, 14 C 5.5, 17.5 5.5, 22.5 7.5, 26"
        fill="none" stroke="#F59E0B" stroke-width="2.3" stroke-linecap="round" />
  <path d="M 36.5, 14 C 38.5, 17.5 38.5, 22.5 36.5, 26"
        fill="none" stroke="#F59E0B" stroke-width="2.3" stroke-linecap="round" />

  <!-- Pause Indicator Badge -->
  <circle cx="35" cy="7.5" r="5.5" fill="#92400E" />
  <circle cx="35" cy="7.5" r="4.2" fill="#F59E0B" />
  <rect x="33.2" y="5.8" width="1.4" height="3.4" fill="#131620" rx="0.5" />
  <rect x="35.4" y="5.8" width="1.4" height="3.4" fill="#131620" rx="0.5" />
</svg>
"""


def render_svg_to_png(svg_string: str, output_path: str, width: int, height: int):
    """Renders SVG string to high-quality PNG at specified dimensions using AppKit."""
    data = AppKit.NSData.dataWithBytes_length_(svg_string.encode("utf-8"), len(svg_string))
    img = AppKit.NSImage.alloc().initWithData_(data)
    if not img:
        raise ValueError(f"Failed to load SVG data for {output_path}")

    bitmap = AppKit.NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
        None, width, height, 8, 4, True, False, AppKit.NSCalibratedRGBColorSpace, 0, 0
    )
    bitmap.setSize_(AppKit.NSMakeSize(width, height))

    AppKit.NSGraphicsContext.saveGraphicsState()
    ctx = AppKit.NSGraphicsContext.graphicsContextWithBitmapImageRep_(bitmap)
    AppKit.NSGraphicsContext.setCurrentContext_(ctx)
    ctx.setImageInterpolation_(AppKit.NSImageInterpolationHigh)

    rect = AppKit.NSMakeRect(0, 0, width, height)
    img.drawInRect_fromRect_operation_fraction_(rect, AppKit.NSZeroRect, AppKit.NSCompositeSourceOver, 1.0)
    AppKit.NSGraphicsContext.restoreGraphicsState()

    png_data = bitmap.representationUsingType_properties_(AppKit.NSPNGFileType, None)
    with open(output_path, "wb") as f:
        f.write(png_data)


def generate_icns(app_svg: str, output_icns_path: str):
    """Builds macOS AppIcon.icns containing all standard Apple iconset resolutions."""
    iconset_dir = "/tmp/CallRecorder.iconset"
    if os.path.exists(iconset_dir):
        subprocess.run(["rm", "-rf", iconset_dir])
    os.makedirs(iconset_dir, exist_ok=True)

    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    for sz, filename in sizes:
        dest = os.path.join(iconset_dir, filename)
        render_svg_to_png(app_svg, dest, sz, sz)

    cmd = ["iconutil", "-c", "icns", iconset_dir, "-o", output_icns_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running iconutil: {res.stderr}")
    else:
        print(f"Generated ICNS bundle: {output_icns_path}")

    subprocess.run(["rm", "-rf", iconset_dir])


def main():
    print("🎨 Generating Call Recorder Icons...")

    # 1. Save SVGs in assets
    with open(os.path.join(ASSETS_DIR, "app_icon.svg"), "w") as f:
        f.write(APP_ICON_SVG)

    with open(os.path.join(ASSETS_DIR, "menu_icon.svg"), "w") as f:
        f.write(MENU_ICON_TEMPLATE_SVG)

    with open(os.path.join(ASSETS_DIR, "menu_icon_recording.svg"), "w") as f:
        f.write(MENU_ICON_RECORDING_SVG)

    with open(os.path.join(ASSETS_DIR, "menu_icon_paused.svg"), "w") as f:
        f.write(MENU_ICON_PAUSED_SVG)

    # 2. Render App Icon PNGs (1024, 512, 128, 64)
    render_svg_to_png(APP_ICON_SVG, os.path.join(ASSETS_DIR, "app_icon_1024.png"), 1024, 1024)
    render_svg_to_png(APP_ICON_SVG, os.path.join(ASSETS_DIR, "app_icon_512.png"), 512, 512)
    render_svg_to_png(APP_ICON_SVG, os.path.join(ASSETS_DIR, "app_icon.png"), 512, 512)
    render_svg_to_png(APP_ICON_SVG, os.path.join(ASSETS_DIR, "app_icon_128.png"), 128, 128)
    render_svg_to_png(APP_ICON_SVG, os.path.join(ASSETS_DIR, "app_icon_64.png"), 64, 64)

    # 3. Build AppIcon.icns
    generate_icns(APP_ICON_SVG, os.path.join(ASSETS_DIR, "AppIcon.icns"))

    # 4. Render Menu Bar Icons (22x22 pt @1x, 44x44 px @2x Retina)
    render_svg_to_png(MENU_ICON_TEMPLATE_SVG, os.path.join(ASSETS_DIR, "menu_icon.png"), 22, 22)
    render_svg_to_png(MENU_ICON_TEMPLATE_SVG, os.path.join(ASSETS_DIR, "menu_icon@2x.png"), 44, 44)

    render_svg_to_png(MENU_ICON_RECORDING_SVG, os.path.join(ASSETS_DIR, "menu_icon_recording.png"), 22, 22)
    render_svg_to_png(MENU_ICON_RECORDING_SVG, os.path.join(ASSETS_DIR, "menu_icon_recording@2x.png"), 44, 44)

    render_svg_to_png(MENU_ICON_PAUSED_SVG, os.path.join(ASSETS_DIR, "menu_icon_paused.png"), 22, 22)
    render_svg_to_png(MENU_ICON_PAUSED_SVG, os.path.join(ASSETS_DIR, "menu_icon_paused@2x.png"), 44, 44)

    # 5. Copy & Render Web Assets (for dashboard header & favicon)
    with open(os.path.join(WEB_DIR, "icon.svg"), "w") as f:
        f.write(APP_ICON_SVG)

    with open(os.path.join(WEB_DIR, "favicon.svg"), "w") as f:
        f.write(APP_ICON_SVG)

    render_svg_to_png(APP_ICON_SVG, os.path.join(WEB_DIR, "icon.png"), 128, 128)
    render_svg_to_png(APP_ICON_SVG, os.path.join(WEB_DIR, "favicon.png"), 64, 64)

    print("✨ All icons generated successfully!")


if __name__ == "__main__":
    main()
