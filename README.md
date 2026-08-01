# Professional Translation Skill

一套可复用的专业翻译技能包，将出版级翻译的完整方法论沉淀为可执行流程：从译前任务界定、术语体系搭建，到译中语义与语气把控，再到译后四轮审校与项目管理规范，全部固化为可复用的工作流、检查清单和实战脚本。

**适用场景**：长篇幅出版物、医学/法律/技术文档、合同与学术材料的专业翻译，以及任何需要术语一致、事实可核、决定可追溯的翻译任务。

**核心信条**：不猜测、不擅改、有依据、可复核。

## 包含内容

```
professional-translation/
├── SKILL.md                          # 触发说明 + 核心规则 + 四阶段工作流
├── scripts/                          # 可执行脚本（已测试）
│   ├── docx_replace_text.py          #   docx 文本替换，保留 run 格式
│   ├── normalize_dates.py            #   日期规范化（中文数字→阿拉伯，保护专名）
│   └── make_version_readme.py        #   版本清单 + 修改日志生成器
├── references/                       # 参考文档（按需加载）
│   ├── source-extraction.md          #   扫描PDF → 文字层 OCR 流水线
│   ├── task-boundary.md              #   译前边界确认清单
│   ├── review-checklists.md          #   四轮审校清单
│   └── project-lessons.md            #   实战教训（11条错误→规则）
└── assets/                           # 模板资源
    ├── glossary_template.json        #   术语表模板
    └── style_guide_template.md       #   风格指南模板
```

## 四阶段工作流

1. **译前**：任务边界确认（类型/读者/变体/交付规范）→ 建术语表 + 风格指南
2. **译中**：以意义单元+逻辑关系为单位；语气强度零容错（must/should/may）；事实零误差；原文有疑不擅改
3. **译后**：四轮审校（双语对照 → 术语事实 → 单语通读 → 格式交付）
4. **项目管理**：主文件唯一基准；版本清单 + 修改日志；规范化脚本接入主流水线

## 核心规则（实战教训沉淀）

1. 主文件唯一基准：内容修改只改主文件，格式版一律从主文件重新生成
2. 一切翻译改动先对照原文：编辑意见/AI意见 = 待核对提议，不是事实
3. 术语表是活文档：正文改术语必须同步表
4. 规范化脚本接入主流水线，目标=主文件，改后立即验证
5. 版本清单 + 修改日志（时间/位置/原因/依据页码）
6. 文本替换逐 run 保留格式（重建前检查 runs 数）
7. 需求冲突先问优先级
8. 不可验证指标不假装精确
9. 每阶段主动复盘，不等被追问
10. 编辑文件后立即运行验证

## 安装

将 `professional-translation/` 目录放入 OpenClaw 的 skills 目录即可被识别；或直接使用打包文件 `professional-translation.skill`。

## 脚本用法

```bash
# docx 文本替换（保留格式）
python3 scripts/docx_replace_text.py <file.docx> <old_text> <new_text> [--all]

# 日期规范化（中文数字年月日 → 阿拉伯；世纪 → 中文；保护《失落的二月》类专名）
python3 scripts/normalize_dates.py <input.docx> [output.docx]

# 版本清单 + 修改日志生成
python3 scripts/make_version_readme.py <project_dir> [--md-backup <backup.md>]
```

## License

MIT
