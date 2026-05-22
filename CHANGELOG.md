# Darwin 修复更新记录

> 日期: 2026-05-22 | PR: https://github.com/alchaincyf/darwin-skill/pull/6
> 分支: fix/anchor-scoring-tehc | Fork: MuseFantasy/darwin-skill

---

## 变更总览

| 文件 | 操作 | 说明 |
|------|------|------|
| SKILL.md | 修改 +47/-6 | 评分规则、Phase 1/2、约束规则 |
| references/anchor-library/dimension-anchors.md | 新增 | 8维锚定示例 + TEHC 覆盖映射 |

---

## P0: 锚定评分替代 LLM 裸判

**问题**: Darwin 原版 Phase 1 使用"按维度打 1-10 分"自由评分。同一 skill 三
次评分三个结果，不同模型基线差 5-8 分。根因：把 autoresearch 的确定性指标
(val_bpb) 换成了 LLM 主观评分。

**修复**:
- 新增「锚定评分协议」: 每维度先读 3 档锚定示例，判断目标"最像哪个档位"
- Phase 1 步骤 2: "逐项打分" → "逐项锚定比对 + 结构化 JSON 输出"
- Phase 2 步骤 4: "重新打分" → "按锚定比对重新打分（禁止直接对比前后分数）"
- 置信度出口: confidence:low → 2模型交叉验证 → 仍 low → 人工评审
- 新增约束规则 #8: 强制锚定评分 (temperature=0, DeepSeek 禁用 thinking)
- 理论依据: Hashemi et al., ACL 2024，锚定比对偏差 ≤3 分 vs 裸判 8-15 分

**改动位置**:
- 评分规则段: 维度1-7 从"打 1-10 分"改为"锚定比对"
- 新增锚定评分协议段 (评分步骤 + 置信度出口 + 维度8 例外)
- Phase 1 基线评估: 新增步骤 2-5（读锚定库 → 比对 → 结构化输出 → 交叉验证）
- Phase 2 优化循环: 步骤 4 标注"锚定比对"
- 约束规则: 新增 #8

---

## P1: 维度1 Frontmatter 规则化

**问题**: 维度1 (Frontmatter 质量，权重8) 靠 LLM 主观评分——name 格式、
description 长度、version 字段这些是可确定性判断的，不应消耗 LLM tokens
也不应引入随机性。skill-evaluator 的 check_metadata.py 已验证此方案。

**修复**:
- 锚定库中维度1 从"3档锚定示例"改为"确定性检查清单"
- name 格式: 正则 `^[a-z0-9][a-z0-9-]*[a-z0-9]$` + 长度3-64 + 通用名黑名单
- description 质量: "做什么"+"何时用"+"触发词"三要素 + ≤1024字符
- version + license: semver 格式 + 字段存在性
- 每项明确分数档 (3/2/1/0)，LLM 仅兜底（规则无法判断时）

**改动位置**:
- references/anchor-library/dimension-anchors.md: 维度1 重写
- SKILL.md 评分规则: 新增"维度1 例外"标注

---

## P2: TEHC 四组件盲区补齐

**背景**: TEHC 模型 (Zhou et al., arXiv 2605.07358) 将 Skill 解剖为
Trigger/Execution/Heuristics/Completion 四组件。Darwin 8 维覆盖不完整：

| TEHC 组件 | 原覆盖 | 盲区 |
|-----------|--------|------|
| H-Heuristics | 维度3只评"有无异常表" | 不评异常质量（是否具体/可操作） |
| C-Completion | 维度4只评"有无确认点" | 缺失可程序化验证条件 |
| T-Trigger | 维度1只评正向触发 | 缺失负触发（何时不应激活） |

**修复**:
- H 质量: 维度3 高档锚定示例增加反模式警示 + 异常具体性判断标准
- C 自动验证: 维度4 高档锚定示例增加可程序化完成条件 (exit code/lint/文件存在)
- 负触发: 维度1 新增补充检查"何时不应使用此 skill"
- 新增 TEHC 四组件覆盖映射表

**改动位置**:
- references/anchor-library/dimension-anchors.md: 维度1/3/4 重写 + 新增 TEHC 映射表

---

## 新增文件

### references/anchor-library/dimension-anchors.md (300+ 行)

```
## 维度 1: Frontmatter 质量 — 优先规则化检查
  [确定性检查清单: name格式(3分) + description质量(3分) + version+license(2分)]
  [LLM 锚定兜底]
  [负触发条件补充检查]

## 维度 2: 工作流清晰度
  [3档锚定示例: 高档(有序号+输入输出) / 中档(有步骤但模糊) / 低档(无结构)]

## 维度 3: 边界条件覆盖 — 含 H 质量判断
  [高档: 异常表格+反模式警示] / [中档: 笼统处理] / [低档: 全无]

## 维度 4: 检查点设计 — 含 C 自动验证
  [高档: 确认点+自动验证条件] / [中档: 简单确认] / [低档: 全自主]

## 维度 5: 指令具体性
## 维度 6: 资源整合度
## 维度 7: 整体架构
## 维度 8: 实测表现 (不适用锚定)

## 使用方式 (含维度1特殊处理)
## TEHC 四组件覆盖映射
```

---

## 本地 hermes 版同步状态

本地 `~/.hermes/skills/darwin-skill/SKILL.md` 已包含:
- P0 锚定评分协议
- P1 维度1 规则化标注
- P2 TEHC 相关改动

本地额外保留（不在上游 fork 中）:
- 已知限制与社区反馈段
- 大规模批量评估段
- Hermes Agent 路径适配
- DeepSeek reasoning_content 异常处理
- Obsidian 持久化指南
- 与 skill-evaluator 关系说明
- 15 个 references/ 文件 (llm-rubric-anchoring.md 等)

锚定库已同步: `~/.hermes/skills/darwin-skill/references/anchor-library/dimension-anchors.md`
