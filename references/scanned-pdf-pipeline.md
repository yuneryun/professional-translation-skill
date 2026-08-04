# Scanned-PDF Full Pipeline — walkthrough & verified findings

Session-proven on a 98-page English medical book: 342 DPI scans, diagonal
light-gray "EVPROJECTWORK" watermark on every page, user wanted accuracy
assessment first, then OCR/translation planning.

## The five stages

1. **Preflight** — PyMuPDF text-layer check. Text-based → pymupdf4llm (≈100%),
   done. Scanned → continue.
2. **Quality report** — extract ORIGINAL embedded images, compute DPI
   (px / (pt/72)), Laplacian clarity, watermark detection, RapidOCR language
   probe. Report expected accuracy to the user BEFORE the full OCR run.
3. **Full OCR** — RapidOCR per page (extract embedded image, never low-res
   render). Save (page, blocks, score); flag <0.9 for correction.
4. **LLM correction** — fix glued words / case / watermark-polluted chars.
5. **Translate & deliver** — glossary first (names, orgs), chapter by chapter.

## The A/B experiment that settled the watermark question

Same page (p34), two OCR runs:

| Version | Result |
|---------|--------|
| With watermark, direct OCR | 47 blocks, full sentences correct (`"ready to respond to a deluge of"`, `"The CDC was"`) |
| After cv2.inpaint (TELEA) of watermark mask | WORSE: `deluge`→`delur`, `Georgia`→`Georgi`, `malaria across`→`ma' ria a oss`, `World War II`→`Worlc var Il`, blocks fragmented 47→56 |

Why: the inpaint mask (dilated Hough lines) also erased covered body text;
inpainting hallucinated gray fill that OCR reads as noise. Light watermarks
(≈gray 180 on white 255, ~30% opacity, ~2.5% page coverage) are BELOW the
contrast band modern detectors read — they cost ~0.5–1 accuracy point, and
LLM context correction recovers most polluted characters.

**Rule: light watermark → OCR directly. Never inpaint.**
Heavy watermarks (dark, covering text) are the only case that justifies
preprocessing, and any removal method should be A/B-tested before committing.

## Accuracy expectations by document class (measured/industry)

| Class | Accuracy |
|-------|----------|
| Text-layer PDF + pymupdf | ~100% (not OCR) |
| English print scan, ≥300 DPI + RapidOCR | ~98–99% char |
| Same + light watermark | ~97.5–98.5% |
| Same + LLM correction | ~99%+ |
| Same class, ABBYY/Azure/Google | 99.5–99.8% |
| Handwriting / <200 DPI / heavy watermark | 75–95% (falls fast) |

## Detection blind spots (how the watermark was almost missed)

- OCR text-repeat detection → 0 hits (rotated text unreadable by OCR).
- Histogram band 100–200 → 1–2% (watermark lives in 150–230, body text <100).
- What worked: threshold 215 → `HoughLinesP` (minLineLength 250) → 41–60
  segments at 135° → gray sampling on the lines (median 179–185).

## Pitfalls (Windows / China)

- pip timeout → `-i https://pypi.tuna.tsinghua.edu.cn/simple`
- `cv2.imread` on Chinese paths → `cv2.imdecode(np.fromfile(path, ...))`
- OpenCV 5 `HoughLinesP` shape is (N,4): unpack `x1,y1,x2,y2 = l`; wrapping
  `l[0]` yields `numpy.int32` → TypeError.
- Terminal heredoc with `&` → misdetected as backgrounding; write script file.
- vision_analyze may be unavailable on the active provider — the assessment
  here is fully vision-free (Laplacian + Hough + OCR confidence).
