# Runtime 适配性审查（详细对照表 + 扫描命令）

> SKILL.md 在「Runtime 适配性审查」章节会引用本文件。Phase 1 基线评估时跑红灯扫描需要查这里。

---

## 背景

花叔的 skills 基于 Anthropic 开放的 [Agent Skills](https://agentskills.io) 协议，应当能在 Claude Code、Codex、Cursor、OpenClaw、Hermes Agent、CodeBuddy、Workbuddy、Gemini CLI、OpenCode 等 50+ skills-compatible runtime 上通用。

这是 skill 分发力的根本——一个被误判为「单一 runtime 绑定」的 skill，会被其他 agent 直接拒绝安装（实例：nuwa-skill 因 README 写「在 Claude Code 里使用」被 Marvis agent 拒绝）。

**适用范围**：除非 skill 名字明确声明绑定单一 runtime（如 `huashu-slides-codex`、`xxx-for-claude-code`），所有 skill 必须通过本审查。

---

## 红灯信号（出现即扣分，必须在 P0 优化轮修复）

| 红灯类型 | 典型表现 | 危害 |
|---|---|---|
| Badge 钉死 | `[![Claude Code Skill]]`、`[![Cursor Only]]` 之类的单一 runtime badge | 视觉上首屏定调，其他 runtime 用户直接退出 |
| 措辞钉死 | 「在 Claude Code 里」「Cursor 用户可以」「Codex 中使用」「Claude Code skill」 | 让 agent 解析时误判为"不是给我用的" |
| 安装命令钉死 | 只给 `~/.claude/skills/` 路径、只给 `/plugin install`、只给某 runtime 私有 CLI | 不知道这是 Claude Code 命令的 agent 会拒绝 |
| 工具调用钉死 | 工作流里硬编码 `mcp__claude-in-chrome__*`、`PostToolUse hook` 等单 runtime 能力，且不给替代方案 | 其他 runtime 没这些工具 → 流程跑不通 |
| 路径硬编码 | `~/.claude/skills/xxx/`、`.claude/agents/yyy` 作为唯一路径 | 其他 runtime 用 `~/.cursor/skills/` `~/.codex/skills/` |

---

## 绿灯措辞（推荐改写）

| 红灯 | 绿灯 |
|---|---|
| "在 Claude Code 里" | "在你的 agent 里" / "在任何 skills-compatible runtime 中" |
| "Claude Code skill" | "Agent Skill" |
| "Claude Code 用户" | "skills-aware agent 用户" |
| 单一 badge 钉死 | `Agent Skills Standard` + `skills.sh Compatible` + `Multi-Runtime` 三个中立 badge |
| 只给 `npx skills add ...` 一行 | 三层结构：① 自动检测的一行命令 ② 折叠展开的各 runtime 手动路径 ③ 「作为参考资料 cat 进 context」fallback |
| 工具名硬编码 | "用一个 browser automation 工具（例如 Claude 的 chrome MCP、Playwright 等）" |

---

## 例外清单（允许的「Claude Code 痕迹」）

不是所有 Claude-Code 相关字符都要清除。下面这些是**正当出现**的，不算红灯：

1. **Frontmatter `description` 里的中英文触发词**——这是 skill 入口，其他 runtime 解析 frontmatter 时同样能匹配
2. **花叔生态内部联动的 skill 名引用**——如「调用 huashu-design」「跟 darwin-skill 配套」
3. **明确标注的 runtime-specific 章节**——如「### 仅 Claude Code 优化（按需触发）」+ 解释清楚是 nice-to-have
4. **commit message、changelog、内部脚本**——不属于用户读到的 skill 内容
5. **引用/演示该 pattern 本身**——讲解红灯规则、列反例、给出 grep 命令时，必然要字面写出「在 Claude Code 里」「Claude Code skill」这些措辞。这是**把措辞当被描述的对象**，不是**把单 runtime 当指令要求读者用**，属假阳性。典型受害者是 darwin-skill 自己（本审查章节就含这些字样）。

**真红灯 vs 假阳性判别**：

| | 真红灯（须修） | 假阳性（不修） |
|---|---|---|
| 性质 | 把单 runtime 当**指令**：「在 Claude Code 里运行 X」「这是 Claude Code skill」 | 把这些措辞当**被描述的对象** |
| 出现位置 | 工作流步骤、首屏定调、安装说明 | grep 命令本身、反例清单里引用的反例、「『Claude Code skill』是红灯措辞」这类元陈述、本对照表 |
| 处理 | 进 P0 runtime drift 修复 | 记 `runtime_scan=false_positive`，不改 |

**扫描后必须人工读命中行的上下文**再定性——禁止机械按 grep 命中行数定 P0，否则任何讲解 runtime 中立性的 skill（含 darwin-skill 本身）都会永远判自己红灯、陷入自审死循环。

---

## 审查时机

- **Phase 1 基线评估时**：每个 skill 跑一次红灯扫描，命中项以 `runtime_warn=N` 形式写入 results.tsv 的 `note` 列（不新增列、保持向后兼容）
- **Phase 2 优化循环时**：红灯命中数 ≥ 1 的 skill，强制把第一轮优化方向定为 P0「runtime drift 修复」（详见 SKILL.md 优化策略库的 P0 章节），优先于其他维度
- **Phase 3 汇总报告时**：单独一栏「runtime 中立度」展示修复进度（命中数从 X → 0）

---

## 红灯扫描快速命令

```bash
# 在 skill 目录跑这个 grep，输出即红灯命中
grep -nE "(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)" SKILL.md README.md 2>/dev/null
```

输出非空 = 该 skill 未通过 gate，必须在优化循环里修复。
