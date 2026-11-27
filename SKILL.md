---
name: gb2md
description: 把 GB 国家标准 PDF（食品安全国家标准 GB 5009 系列、GB 316xx 卫生规范等）忠实转换为整理好格式的 Markdown，内容忠于原文、只排版不改写。PDF 解析引擎可选且随时可切换：①AI 助手内置 PDF 能力（文字清晰的 PDF；扫描件由随附脚本 scripts/pdf_extract.py 判定文本层并强制渲染 OCR）；②MinerU（调用官方技能 mineru-document-extractor，用 mineru-open-api extract 保留表格/公式/OCR，需配置 token）。安装/首次运行让用户二选一，之后可随时重新选择引擎、随时配置或更换/清除 MinerU 的 API token（token 不落明文，仅存于 mineru 配置或环境变量，状态记录在 templates/ENGINE.md）。转换后按 FORMATTING.md 逐项检查整理：图片/图谱转 base64 并统一置于文末（正文用引用式 ![alt][ref]）、中英文/中文与公式/化学式/行内公式之间加空格、简单公式化学式数据用 Markdown 复杂公式保留 LaTeX、标点与国际单位按 GB 3100、范围号用半角~、简化 LaTeX 删除多余空格、修复标题层级与丢失章节编号、附录属性仅在原文标注时才写、提示缺失的前言。当用户说"把 GB 标准转 Markdown""pdf 转 markdown 并整理格式""转换食品安全国家标准""切换 PDF 引擎""配置 mineru/token"等时使用。
user-invocable: true
---

# GB2MD（GB 标准 PDF → 格式化 Markdown）

将一份 GB 国家标准 PDF 忠实转换为结构清晰、格式规范的 Markdown。只整理排版与规范，内容一律忠于原文，不改写、不发散、不补数值。

## 0. 选择 PDF 解析引擎（首次必做，之后可随时重配，见 §5）

技能安装或首次加载时，先让用户在两种引擎中二选一，并把选择记入 `templates/ENGINE.md`（机制见 §5）。向用户简要说明差异后，请用户选择：

- **选项 A — AI 助手内置 PDF 解析能力**：适合文字层清晰的 PDF；对扫描件由随附脚本判定后强制渲染、再由 AI 视觉 OCR。无需任何外部账号/联网配置。
- **选项 B — MinerU**：版面、表格、公式识别更强，适合复杂国标。依赖官方技能 mineru-document-extractor，需配置 token。

安装提示文案示例：

> GB2MD 已安装。请选择 PDF 解析方式：A 内置（开箱即用，扫描件走 OCR）；B MinerU（版面/表格更强，需配置）。以后随时可说「切换引擎」或「配置 mineru」来更改。

### A. 内置引擎（随附脚本）

脚本 `scripts/pdf_extract.py` 零配置运行：自动检测并安装依赖 PyMuPDF；安装失败时脚本返回退出码 2，AI 助手自动降级用内置解析/图像识别能力完成同样任务，流程不中断、用户无感。

### B. MinerU 引擎（引导配置官方技能）

引导用户安装并配置官方技能 **mineru-document-extractor**：<https://modelscope.cn/skills/@mineru-extract/mineru-document-extractor>（CLI 为 `mineru-open-api`，源自 OpenDataLab/MinerU）。要点：

1. 安装 CLI：`npm install -g mineru-open-api`（或按官方技能页其他方式）。
2. 配置 Token：GB 标准含表格/公式，**必须用 `extract` 精准模式（需 token）**；`flash-extract` 不支持表格，勿用。在 <https://mineru.net/apiManage/token> 创建 Token，再 `mineru-open-api auth` 交互配置，或设置环境变量 `MINERU_TOKEN`。
3. 验证：`mineru-open-api auth --verify`，或对样例 `mineru-open-api extract "<样例.pdf>" -o ./out/`。

> 详细参数、模型选择（vlm/pipeline）、报错排查以官方技能页为准。

## 1. 解析 PDF（按 ENGINE.md 中当前引擎）

### engine = builtin
1. 判定文本层：`python scripts/pdf_extract.py "<pdf>" --analyze`，查看结尾 `DECISION: TEXT` 或 `DECISION: OCR`。
2. `DECISION: TEXT` → 直接提取文本层内容。
3. `DECISION: OCR`（扫描件/乱码）→ 强制渲染：`python scripts/pdf_extract.py "<pdf>" --render -o pages --dpi 300`，再把每页 PNG 交给 AI 图像识别（视觉 OCR），要求「逐字完整提取、保留条款编号/公式/表格原样、不总结、不改写」。
4. 脚本退出码 2 → 自动改用 AI 内置文档解析/图像识别，不中断。

### engine = mineru
1. 不对 PDF 做任何预处理，直接提交 MinerU：`mineru-open-api extract "<pdf>" -o "<输出目录>"`（用 `extract`，不用 `flash-extract`，以保留表格/公式/OCR）。
2. 取回 MinerU 生成的 `full.md` 与 `images/` 目录。
3. 若提示无 token/401 → 走 §5「配置 MinerU API」补配后重试。

> 含中文或空格的路径务必加英文双引号。

## 2. 转换后检查与格式整理（核心）

把解析得到的原始 Markdown 按下列规则整理；权威细则与交付清单见 `FORMATTING.md`：

1. **图片/图谱 → base64，统一置文末**：正文用引用式 `![图题][fig-x]`，文末「图片 base64」区集中 `[fig-x]: data:...`。校验每条 base64 段内无任何空白、魔数与 marker 完整、引用一一对应。
2. **间距**：中文与英文、数字、公式、化学式、行内公式之间各加一个半角空格。
3. **公式/化学式/数据**：简单者转 Markdown/Unicode（`H₂O`、`pH`、`-18 ℃`），复杂计算式保留 LaTeX（`$$...$$` 带国标公式编号）。
4. **标点与国际单位**：全角标点；范围号统一用半角 `~`（不用全角 `～`）；国际单位按 **GB 3100**（数值与单位间空格、真减号 `-`、`℃`/组合单位规范）。
5. **简化 LaTeX**：删除 `\mathrm { C } _ { 2 0 }` 之类多余空格，还原被误识别成 `$…℃$` 的纯数值温度。
6. **引擎共性缺陷修复**：标题层级提升为 `#`/`##`/`###`、补回丢失的章节编号、删除跨页页眉残留、编号与正文补空格、半角括号转全角；**提示缺失的「前言」页**需手动补录。
7. **附录属性**：仅当原文明确标注「规范性／资料性」时才写属性，如 `# 附录A（资料性） ××××`；原文未注明时只写 `# 附录A ××××`，**不自行添加**。

> 处理含中文路径的文件、或做 base64 改写时，用 Python（正则）而非 `sed`；脚本里不硬编码中文路径，命令行参数传入并加引号。

## 3. 信息头

按 `templates/HEADER_TEMPLATE.md` 在文件开头生成「项目/信息」元数据表（标准号、年代号、名称、发布部门、发布/实施日期、文件类型等）。封面取发布/实施日期与发布部门；代替关系、提出/归口/起草单位多来自「前言」——MinerU 未提取前言时，对应字段标「⚠️暂未获取」并在交付说明提示。

## 4. 保存与交付

- 输出 `.md` 与源 PDF 同名（仅扩展名变），保存到 PDF 同目录或用户指定目录。
- 用文件交付能力（如 SendUserFile / 文件卡片）展示，路径为绝对路径。
- 可选：交付前询问是否再导出 Word（.docx）；需要时调用 Word 转换能力，Word 中 LaTeX 公式转为可编辑公式或清晰图片。

## 5. 配置与切换（随时可用，不限首次）

引擎选择与 MinerU API 可随时更改，无需重装技能。当前配置持久化在 `templates/ENGINE.md`：

- **判定**：`templates/` 下存在 `ENGINE.md`（无 `_TEMPLATE` 后缀）＝已配置，直接读取其 `engine` 字段决定走内置还是 MinerU；仅有 `ENGINE_TEMPLATE.md` 或两者皆无＝未配置，按 §0 走首次选择并把结果写入 `ENGINE.md`。
- **触发**：出现「切换引擎 / 换解析方式 / 配置 PDF 处理 / 重新配置 / 配置 mineru / 设置或更换 token / 改 api / 清除 token / 当前用什么引擎 / 查看配置」等任一意图时，立即进入对应动作（即便本会话此前已选过）。
- **动作**：
  1. 切换引擎（内置 ↔ MinerU）：让用户重选 A/B，更新 `ENGINE.md` 的 `engine`；若切到 mineru 而 `mineru_api.configured` 为 false，接着走「配置 MinerU API」。
  2. 配置/更换 MinerU API：引导 `mineru-open-api auth` 交互录入，或 `export MINERU_TOKEN=...`；更新 `ENGINE.md` 的 `mineru_api.configured=true` 与 `source`（`auth` 或 `env`）。
  3. 验证/查看：`mineru-open-api auth --verify`，并结合 `ENGINE.md` 告知用户当前引擎与 token 来源（脱敏，不显示 token 明文）。
  4. 清除：删除 `~/.mineru/config.yaml` 中 token 或 unset `MINERU_TOKEN`，并把 `ENGINE.md` 的 `mineru_api.configured=false`、`source=none`。
- **安全**：**严禁把明文 token 写入 `ENGINE.md`、仓库文件或对话**；token 仅存于 `~/.mineru/config.yaml`（auth）或环境变量（`MINERU_TOKEN`）。`ENGINE.md` 只记录引擎与「是否已配置/来源」状态。
- **不落盘选项**：若用户未要求「记住」，可只在当前会话记住选择、不写 `ENGINE.md`。

`ENGINE.md` 字段示例（无明文 token）：

```yaml
engine: mineru             # builtin | mineru
mineru_api:
  configured: true         # true | false
  source: auth             # env | auth | none
last_set: 2026-11-27
```

## 注意事项

- GB 原文是权威来源：任何与原文不一致以原文为准；只整理格式，不改含义、不补数值；不确定处标「⚠️暂未获取」。
- base64 内嵌会使文件较大，但保持单文件自包含（图片一律 base64、不保留外部 images 目录）；务必执行「无空白 + marker 完整」校验，否则图片破损。
- MinerU 务必用 `extract`（非 `flash-extract`），否则国标表格不被识别。
- 引擎与 MinerU API 可**随时切换/重配**（见 §5），不是仅首次；配置状态记在 `templates/ENGINE.md`，token 永不落明文。
- 交付前逐条核对 `FORMATTING.md` 末尾「交付前校验清单」。
