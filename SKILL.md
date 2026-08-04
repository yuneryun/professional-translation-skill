---
name: scanned-pdf-pipeline
description: "Use when OCRing scanned PDFs: assess, watermark, correct, per-stage QA gates."
version: 3.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, OCR, Scanned, Documents, Watermark, Pipeline, QA, Verification, Translation, Medical]
    related_skills: [ocr-and-documents, pdf, docx]
---

# 扫描 PDF → 专业译稿 端到端流水线（每阶段 QA 复核）

Use when the user hands over an image-only / scanned PDF (no text layer) and wants
high-accuracy extraction, professional translation, or both — especially rigorous
domains (medical / legal / academic / contracts). Merges the OCR pipeline (quality
assessment, watermark handling, dual-engine verification, LLM correction) with the
professional-translation methodology (task boundary, glossary, style guide, 4 review
rounds, master-file project management). If the PDF HAS a text layer, skip the OCR
part — extract with pymupdf/pymupdf4llm (accuracy ≈100%) and start at Phase 2.

## 核心原则（守不住这些，一切白做）

1. **不猜测、不擅改、有依据、可复核** — every edit checked against the original;
   editor/AI suggestions are PROPOSALS, not facts
2. **每阶段 QA gate** — pipeline does NOT proceed until the gate passes; failures
   bounce back to the previous stage with a problem list (user requirement)
3. **数字零容忍** — doses, years, percentages, dates, clause numbers: 100% verified
4. **双引擎互证** — never trust a single OCR engine; differences = suspicion list
5. **主文件唯一真源** — edit only the master; regenerate variants from it
6. **复核产物留痕** — every stage writes a 复核报告 (checked items / issues / resolution)
7. **最终验收权在用户** — automated checks assist; user spot-checks 3–5 pages at the end

## 端到端流程（执行 → 🛂复核 → 通过才进下一步）

### Phase 0 — 任务边界确认（动笔前必答）
From `references/task-boundary.md`:
- [ ] 文本类型与用途（合同/医学/学术/营销？尺度不同）
- [ ] 目标读者（专家/管理者/公众）· 语言变体（简繁/英式美式）
- [ ] 客户交付规范（术语偏好、格式模板、是否允许译注、保密）
- [ ] 通读全文识别主题/论点/指代/文体语域（禁止未懂上下文就逐句硬译）
- 🛂 **gate**: 边界问题全部有答案，冲突需求先问用户优先级（不擅自取舍）

### Phase 1 — 源提取（扫描 PDF）
先全页判型（`fitz` 遍历所有页，非抽查）：有文字层 → 直接提取结束；无 → OCR。

**1a. 质量评估**（先给用户准确率预期，再全量 OCR）
- 提取**原始嵌入图**（`fitz.Pixmap(doc, xref)`，勿用低倍渲染）
- 头/中/尾抽样 3–9 页：DPI（≥300 优）、清晰度（Laplacian var >500）、水印、语言探针
- **水印检测**：`cv2.HoughLinesP` 找斜向长线段 + 灰度采样（水印 150–230，正文 <100）——
  浅灰斜向水印 OCR 文本检测不到，必须图像法
- 详见 `scripts/assess_scanned_pdf.py` 与 `references/source-extraction.md`

**1b. 全量 OCR**（`rapidocr_onnxruntime`，约 4s/页 CPU）
- 逐页原图 → OCR → 按页保存（页码+块+置信度），标记 <0.9 的块
- 小字号区（脚注等）单独高清裁剪重扫
- **合并输出"带文字层 PDF"作为全程比对基准**（用户铁律：译文最终参照它，OCR docx 只作输入）

- 🛂 **gate（1a+1b）**:
  1. 水印扫描覆盖全文档（每页缩小图快速霍夫检测），报告异常页
  2. 覆盖率：每页识别量 vs 图像文字量，空白/漏页标记
  3. **双引擎交叉验证**：5–10% 随机页第二引擎（PaddleOCR/Tesseract）对比，差异逐个解决
  4. 通过标准：低置信块 <0.5% 且交叉一致率 >99%；不达标 → 差异页整页重识别

### Phase 2 — 译前准备
- **建术语表** `assets/glossary_template.json`（医学术语/人名/机构：标准译法+语境+禁用译法+来源+确认人）——术语来自原文提取 + 权威来源核实
- **建风格指南** `assets/style_guide_template.md`（日期/数字/单位/缩写/标点/人称/引语）
- 按章提取源文，保留脚注标记与段落编号；建"复核句→页码"索引表
- 🛂 **gate**: 术语表与风格指南经用户确认后锁定；正文改术语必须同步表（活文档）

### Phase 3 — 翻译
- **按意义单元翻译**（逻辑关系优先，非逐词）；保留逻辑/模态/事实/观点归属（"按雷德菲尔德的说法…"）
- **模态词零容忍**：must/shall/should/may/likely/typically — 可能≠确定，建议≠要求
- **事实零错误**：数字/单位/日期/条款号/专有名词不可改
- 原文有歧义：先核实；无法解决 → 保守处理 + 问题清单（不静默硬译）
- 原文错误不静默修正 → 用译注（translator note）标注
- 🛂 **gate**: 问题清单清零或用户裁决；无依据增译 = 零容忍（实例教训：编辑建议加"在公寓内"原文无此地点，被否）

### Phase 4 — 译后四轮复核（高风险文本加领域二审/隔夜再审）
From `references/review-checklists.md`:
1. **双语对照**：漏译/多译/误译/逻辑偏移/术语不一致/语气强度变化/无依据增译
2. **术语与事实专项**：数字小数点百分比货币单位换算、日期期限版本号、人名地名机构名品牌型号、法规条款号案件号文献出处、否定双重否定比较级范围词例外条款、缩写全称首次形式、引文脚注参考文献已有定译
3. **单语通读**：自然清晰无翻译腔、专业写作习惯、观点归属保留、引语口语 vs 叙述书面语
4. **格式与交付**：版式标题层级编号、表格图注粗斜体脚注位置、全半角标点、批注版本号客户模板

专项技巧：
- **回译检查**：关键条款/否定/条件/数值逻辑译回原文比对（不能替代双语审校）
- **OCR 坑排查**：复核时回带文字层 PDF 比对（OCR 会丢词漏句：zombie 丢词、整句漏扫）
- 🛂 **gate**: 4 轮全部通过；高风险文本有领域二审记录；数字 100% 与源文一致

### Phase 5 — 项目管理与交付
- **VERSION_README**：每个文件 = 是什么 + 状态（杜绝"终极版是哪个"）
- **变更日志**：每个改动 = 时间/位置/原因/源页码（可追溯）
- **主文件优先**：内容修改只改主文件；docx 文本替换用 `scripts/docx_replace_text.py`（逐 run 保留格式，重建前查 run 数）；`scripts/normalize_dates.py` 日期规范化只跑主文件、改后立即验证；改后重新导出 md 备份
- 交付 Markdown + Word + 准确率实测报告 + 各阶段复核报告
- 🛂 **gate（七项验收）**: 准确 / 完整（无漏译无增译）/ 一致 / 专业 / 自然 / 可追溯 / 合规 + **用户抽 3–5 页人工终检**

## 水印处理（实测结论 — 修正了原 skill 的"去水印"步骤）
- **浅色水印**（≤~30% 透明度，如 135° 浅灰大字）：**不要去水印**。A/B 实测 inpaint 后 OCR 更差
  （`deluge`→`delur`、`Georgia`→`Georgi`、`World War II`→`Worlc var Il`）。直接带水印 OCR，LLM 纠错修复污染字符
- **重水印**（深色覆盖正文）：才去水印，且先 A/B 测试确认有效再全量用
- 详见 `references/source-extraction.md`

## 实测数字（英文印刷体 342DPI 98 页样本）

| 项目 | 数值 |
|------|------|
| RapidOCR 平均置信度 | 98.4–98.5%（119 块 0 块 <0.9） |
| 浅水印（135° 灰~180 覆盖 2.5%） | 损失 ~0.5–1 点 |
| OCR+LLM 纠错后 | ~99%+ |
| 商业 OCR（ABBYY/Azure/Google）同类 | 99.5–99.8% |

## 环境踩坑（Windows / 中文路径 / deepseek）

- pip 直连超时 → 清华镜像 `-i https://pypi.tuna.tsinghua.edu.cn/simple`
- `cv2.imread` 中文路径失败 → `cv2.imdecode(np.fromfile(path, dtype=np.uint8), flag)`
- OpenCV 5 `HoughLinesP` 返回 (N,4) → 直接 `x1,y1,x2,y2 = l`
- heredoc 含 `&` 被 shell 误判 → 脚本写文件再 `python file.py`
- 质量评估不需要视觉模型（deepseek 无图像输入）：Laplacian + Hough + 置信度采样足够
- 无 LibreOffice/视觉模型时 OCR 缺口 → 带文字层 PDF 比对 + 人工（用户环境实测）

## Bundled Resources

### Scripts
- `scripts/assess_scanned_pdf.py` — OCR 前质量报告（判型/DPI/清晰度/水印/语言探针）
- `scripts/docx_replace_text.py` — docx 文本替换保留 run 格式（逐 run，先查 run 数）
- `scripts/normalize_dates.py` — 日期规范化（中文数字→阿拉伯、世纪→中文，保护时长/专名）
- `scripts/make_version_readme.py` — 生成版本清单 + 变更日志模板

### References
- `references/source-extraction.md` — 扫描 PDF → 文字层流水线（水印处理修正版）
- `references/task-boundary.md` — 译前任务边界清单（必答问题 + 术语统一原则）
- `references/review-checklists.md` — 译后四轮审校清单 + 回译/OCR 坑专项
- `references/project-lessons.md` — 真实项目教训（11 条错误→规则 + 成稿七项验收）
- `references/scanned-pdf-pipeline.md` — 原管线全流程 A/B 实验记录

### Assets
- `assets/glossary_template.json` — 术语表模板（medical_terms/people/institutions + 语境/禁用/来源/确认人）
- `assets/style_guide_template.md` — 风格指南模板（日期/数字/术语/专名/标点/语体/交付）
