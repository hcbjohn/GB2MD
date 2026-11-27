<!--
解析引擎配置模板（ENGINE_TEMPLATE.md）

由 GB2MD 技能读写，记录当前 PDF 解析引擎与 MinerU API 的配置状态。

判定（与 PROFILE 同机制）：
- 未配置：templates/ 下仅有本 ENGINE_TEMPLATE.md（无 ENGINE.md）→ 首次运行按 SKILL.md §0 引导用户选择引擎。
- 已配置：技能把用户选择写入同目录 ENGINE.md（去掉 _TEMPLATE 后缀），此后直接读取 ENGINE.md。
- 随时可改：用户任何时候说「切换引擎 / 配置 mineru / 换 token」等，技能覆盖更新 ENGINE.md（见 SKILL.md §5）。

⚠️ 安全：本文件及 ENGINE.md 一律禁止写入明文 token。
   MinerU 的 token 只能由 `mineru-open-api auth` 存于 ~/.mineru/config.yaml，或用环境变量
   MINERU_TOKEN 提供；这里只记录「是否已配置」和「来源」，不记录 token 本身。
-->

engine: builtin            # builtin（AI 助手内置 PDF 解析）| mineru
mineru_api:
  configured: false        # true | false（是否已配置可用 token）
  source: none             # env（MINERU_TOKEN）| auth（~/.mineru/config.yaml）| none
last_set:                  # 最近一次配置日期 YYYY-MM-DD，可留空
