#!/usr/bin/env python3
"""Pre-OCR quality report for a scanned PDF.

Usage:
    python assess_scanned_pdf.py <file.pdf> [--pages 1,34,67] [--ocr]

Checks:
  - text-layer presence (PDF type: text-based vs scanned)
  - embedded image resolution + effective DPI
  - clarity via Laplacian variance
  - rotated light-watermark detection (Hough lines + gray sampling)
  - optional: RapidOCR probe of one page (needs rapidocr_onnxruntime)

Handles Chinese paths (imdecode) and OpenCV 5 HoughLinesP shape.
Deps: pip install pymupdf opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple
"""
import argparse
import math
import os
import sys
import tempfile


def imread_cn(path, flags=None):
    import cv2
    import numpy as np
    if flags is None:
        flags = cv2.IMREAD_GRAYSCALE
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), flags)


def check_text_layer(doc, n=10):
    text_pages = 0
    for i in range(min(n, doc.page_count)):
        if len(doc[i].get_text().strip()) > 20:
            text_pages += 1
    return text_pages, min(n, doc.page_count)


def image_report(doc, page_no):
    """Return (xref, w, h, dpi) for the page's first embedded image."""
    page = doc[page_no]
    imgs = page.get_images(full=True)
    if not imgs:
        return None
    xref, w, h = imgs[0][0], imgs[0][2], imgs[0][3]
    pr = page.rect
    dpi = w / (pr.width / 72.0)
    return xref, w, h, dpi


def clarity_and_watermark(img_path):
    """Return (laplacian_variance, watermark_dict_or_None)."""
    import cv2
    import numpy as np
    gray = imread_cn(img_path)
    lap = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Rotated light watermark: long diagonal Hough segments + gray sampling.
    _, bw = cv2.threshold(gray, 215, 255, cv2.THRESH_BINARY_INV)
    lines = cv2.HoughLinesP(bw, 1, np.pi / 720, threshold=80,
                            minLineLength=250, maxLineGap=40)
    diag_count, diag_gray = 0, []
    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l  # OpenCV 5 returns (N,4); older wraps in l[0]
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180
            if (120 <= ang <= 150) or (30 <= ang <= 60):  # diagonal
                n = max(abs(x2 - x1), abs(y2 - y1))
                xs = np.linspace(x1, x2, n).astype(int)
                ys = np.linspace(y1, y2, n).astype(int)
                diag_count += 1
                diag_gray.extend(gray[ys, xs].tolist())
    wm = None
    if diag_count:
        med = float(np.median(diag_gray))
        if 130 <= med <= 235:  # lighter than body text (<100)
            wm = {
                "diagonal_segments": diag_count,
                "median_gray_on_lines": round(med, 1),
                "verdict": "light diagonal watermark likely "
                           "(~%d%% opacity)" % round((255 - med) / 255 * 100),
            }
    return round(lap, 0), wm


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", help="path to the scanned PDF")
    ap.add_argument("--pages", default="1,34,67", help="comma list of 1-based pages")
    ap.add_argument("--ocr", action="store_true", help="also run a RapidOCR probe")
    args = ap.parse_args()

    import fitz
    doc = fitz.open(args.pdf)
    print(f"pages: {doc.page_count}")

    tp, n = check_text_layer(doc)
    verdict = ("TEXT-BASED: skip OCR, use pymupdf4llm"
               if tp == n else "SCANNED: OCR path")
    print(f"text-layer pages (first {n}): {tp}/{n} -> {verdict}")
    if tp == n:
        doc.close()
        return

    tmp = tempfile.mkdtemp(prefix="pdf_assess_")
    for pno in [int(p) - 1 for p in args.pages.split(",")]:
        if not (0 <= pno < doc.page_count):
            continue
        r = image_report(doc, pno)
        if not r:
            print(f"page {pno+1}: no embedded image")
            continue
        xref, w, h, dpi = r
        pix = fitz.Pixmap(doc, xref)
        if pix.n > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        png = os.path.join(tmp, f"p{pno+1}.png")
        pix.save(png)
        lap, wm = clarity_and_watermark(png)
        clarity = "sharp" if lap > 500 else ("ok" if lap > 150 else "BLURRY")
        print(f"page {pno+1}: {w}x{h}px, {dpi:.0f} DPI, clarity={lap:.0f} ({clarity})")
        if wm:
            print(f"   watermark: {wm['diagonal_segments']} diagonal segments, "
                  f"gray~{wm['median_gray_on_lines']} -> {wm['verdict']}")
        else:
            print("   watermark: none detected")
        if args.ocr:
            try:
                from rapidocr_onnxruntime import RapidOCR
                res, _ = RapidOCR()(png)
                if res:
                    scores = [float(r[2]) for r in res]
                    print(f"   OCR probe: {len(res)} blocks, "
                          f"mean conf {sum(scores)/len(scores):.3f}")
            except ImportError:
                print("   (rapidocr_onnxruntime not installed; skip OCR probe)")
    doc.close()


if __name__ == "__main__":
    main()
