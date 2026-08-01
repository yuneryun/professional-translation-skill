# 扫描 PDF → 文字层提取流水线

来源: 《World War C》项目（98页纯扫描PDF，无视觉模型环境）

## 诊断
```python
from pypdf import PdfReader
r = PdfReader('doc.pdf')
t = r.pages[0].extract_text()
print(bool(t))  # False = 纯扫描件，需 OCR
```

## 流水线步骤
1. **去水印**：水印干扰 OCR → 生成去水印版
2. **分页渲染**：pdf2image / Ghostscript 将每页转 PNG
3. **分块 OCR**：整页识别差 → 切成小块多块并行识别后拼接
4. **高清重渲染**：Ghostscript 重渲染提高清晰度后再 OCR（提升明显）
5. **合并文字层**：各页结果合并为带文字层 PDF（后续全程比对基准）
6. **生成 OCR 初稿 docx**：作为翻译输入底稿
7. **脚注专项**：脚注区字号小 → 单独高清裁剪重扫

## 铁律
- **译文必须以"带文字层PDF"为最终参照，OCR docx 只作输入**
- OCR 会丢词/漏句（本项目实例：zombie 丢词、整句"打一针"漏扫）→ 复核时必须回文字层 PDF 比对
- 无视觉模型时，OCR 缺口只能靠文字层比对 + 人工

## 关键页定位技巧
用 pypdf 在文字层按关键词搜页码，建立"复核句→页码"索引表，供全程引用：
```python
for i, page in enumerate(r.pages):
    if 'keyword' in (page.extract_text() or '').lower():
        print(f'page {i+1}')
```
