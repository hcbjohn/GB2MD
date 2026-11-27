# GB2MD

**GB to Markdown** — 把 GB 国家标准 PDF（食品安全国家标准等）忠实转换并整理成格式规范 Markdown 的 AI 技能。

**它解决什么问题：** 你手头有一份国标 PDF（如 GB 5009.229-2025《食品中酸价的测定》、GB 31661-2025《调制肉制品生产卫生规范》），想把它变成一份干净、规范、可直接归档检索的 Markdown？把 PDF 发给 AI 助手，它会自动识别文字（扫描件走 OCR）、套用标准格式规则，输出整理好的 Markdown。

**给小白看的重点：** 你不需要懂编程、不需要装 Python、不需要碰命令行。技术活由 AI 助手在后台自动完成。

## 功能

- 把 GB 标准 PDF 忠实转换为结构化 Markdown，内容忠于原文，只排版不改写。
- 两种 PDF 解析引擎可选：**AI 内置**（开箱即用，扫描件自动 OCR）/ **MinerU**（版面、表格、公式识别更强）；**可随时切换**，不限首次。
- **MinerU 的 API token 可随时配置 / 更换 / 清除**（token 不落明文，仅由 mineru 官方 CLI 或环境变量保管）。
- 图片、图谱转 base64 内嵌，且 **base64 统一放在文末**，正文只留引用，保持单文件自包含。
- 自动规范：中英文/中文与公式/化学式之间加空格；简单公式用 Markdown、复杂公式用 LaTeX；标点与国际单位按 **GB 3100**（范围号用半角 `~`）；简化 LaTeX 删除多余空格。
- 自动修复解析常见缺陷：标题层级、丢失的章节编号、跨页页眉残留、OCR 负号/温度；附录属性仅在原文标注时才写。
- 自动生成标准元数据信息头（标准号/发布部门/日期等）。

## 安装

在任意支持技能的 AI 助手软件（千问办公、QwenWork、豆包等）聊天框输入：

```text
安装技能 https://github.com/<你的用户名>/GB2MD
```

或手动下载本仓库 ZIP（Code → Download ZIP）解压后导入技能文件夹。

## 使用

1. 在聊天框选中技能「GB2MD」，把国标 PDF 拖进去。
2. 首次使用时，AI 会让你选 PDF 解析方式：
   - **内置**（默认推荐，无需配置）：文字清晰的 PDF 直接读；扫描件自动渲染做 OCR。
   - **MinerU**（可选，需配置）：版面/表格/公式识别更强；AI 会引导你安装并配置官方 MinerU 技能（见下）。
3. 转换完成后，AI 按格式规则整理并交付 Markdown（与 PDF 同名）。中间只会问你「选哪种引擎、要不要补前言 / 导出 Word」这类点一下就能答的事。

## 随时切换引擎 / 配置 MinerU API

不需要重装，也不限于首次——任何时候你对 AI 说一句即可重新配置：

- 切换引擎：「切换 PDF 解析方式」「改用内置」「改用 MinerU」
- 配置/更换 token：「配置 mineru」「换 mineru token」「设置 API key」
- 查看/清除：「当前用的什么引擎」「mineru token 配好了吗」「清除 mineru 配置」

技能把当前选择记在 `templates/ENGINE.md`（`engine: builtin|mineru`、是否已配置 token、token 来源）。**token 本身绝不写进这个文件、仓库或对话**，只由 `mineru-open-api auth`（存 `~/.mineru/config.yaml`）或环境变量 `MINERU_TOKEN` 保管；`ENGINE.md` 只记录「状态和来源」。

## MinerU 引擎（可选）的配置

选 MinerU 时，本技能调用广泛使用的官方解析技能：

> **MinerU Document Extractor**（`mineru-document-extractor`，CLI `mineru-open-api`）
> 技能主页：https://modelscope.cn/skills/@mineru-extract/mineru-document-extractor
> 上游：https://github.com/opendatalab/MinerU-Ecosystem · Token：https://mineru.net/apiManage/token

简要步骤（AI 会自动引导，最终用户通常无需手动执行）：

1. 安装 CLI：`npm install -g mineru-open-api`
2. 创建并配置 Token：在 mineru.net 创建 Token，运行 `mineru-open-api auth`，或设置环境变量 `MINERU_TOKEN`
3. 转换：`mineru-open-api extract "<国标.pdf>" -o <目录>`（GB 标准请用 `extract` 精准模式；`flash-extract` 不支持表格，勿用）

> 想随时改 token 或退回内置引擎，参考上一节，随时可重配。

## 致谢 / 第三方

- 本技能的可选 **MinerU 解析路径基于 MinerU 官方 Document Extractor 技能** `@mineru-extract/mineru-document-extractor`（OpenDataLab / MinerU 出品，CLI `mineru-open-api`）。PDF 的高精度版面/表格/公式解析能力由该官方技能提供；GB2MD 在其之上负责「格式整理与规范」。技能地址：https://modelscope.cn/skills/@mineru-extract/mineru-document-extractor
- 内置引擎路径使用 PyMuPDF 渲染页面 + AI 视觉识别完成 OCR。

## 目录结构

```
GB2MD/
├── SKILL.md                  # 技能定义（主流程，含 §5 配置与切换，必读）
├── README.md                 # 本说明
├── FORMATTING.md             # 转换后格式规范与交付校验清单（权威细则）
├── LICENSE                   # 许可协议
├── templates/
│   ├── HEADER_TEMPLATE.md    # 标准信息头元数据表模板（可自定义）
│   ├── ENGINE_TEMPLATE.md    # 解析引擎配置模板（未配置态；选定后由技能写 ENGINE.md）
│   └── ENGINE.md             # 运行时生成的当前配置（engine / mineru 状态；不含明文 token）
└── scripts/
    └── pdf_extract.py        # 内置引擎：文本层判定 + 强制渲染 OCR（零配置，依赖自动安装，失败自动降级）
```

## 依赖

- 内置引擎脚本由 AI 助手本地自动执行，自动检测并安装依赖 PyMuPDF；失败时自动降级到 AI 内置解析/图像识别，用户无感。
- MinerU 引擎需 Node.js（`npm`）与 mineru.net Token，仅在选择 MinerU 时需要；AI 会引导，可随时更换或清除。
- 其余（Markdown 生成、base64 内嵌、格式校验）由 AI 助手内置能力完成。

## 许可

见 [LICENSE](LICENSE)。
