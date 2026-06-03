---
name: darwin-skill
description: "Darwin Skill 2.0: autonomous skill optimizer. Evaluates SKILL.md files with a 9-dimension rubric (structure + effectiveness + meta-skill blacklists), runs hill-climbing with git version control, spawns independent judge agents for blind evaluation, validates improvements through test prompts with auto-break on diminishing returns, and generates visual result cards. Use when user mentions 优化skill, skill评分, 自动优化, auto optimize, skill质量检查, 达尔文, darwin, 帮我改改skill, skill怎么样, 提升skill质量, skill review, skill打分."
---

# Darwin Skill 2.0

> **v2.0 · 2026-05-28** — 吸收 Microsoft Research SkillLens（arXiv 2605.23899）的 9 维评分药方 + SkillOpt（arXiv 2605.23904）的 validation-gated 验证机制 + human in the loop 三层守关。
>
> 借鉴 Karpathy autoresearch 的自主实验循环，对 skills 进行持续优化。
> 核心理念：**评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚 → 生成成果卡片**
> GitHub: https://github.com/alchaincyf/darwin-skill

---

## 目录速查

| 章节 | 内容 | 何时查看 |
|------|------|---------|
| [设计哲学](#设计哲学) | 5条核心原则 | 首次使用 |
| [评估 Rubric](#评估-rubric9维度总分100) | 9维度评分标准 + 权重 | 评分时对照 |
| [Runtime 适配性审查](#runtime-适配性审查gate-项独立于-9-维度评分) | 红灯扫描 + 中立性规则 | 新建/改造 skill 时 |
| [自主优化循环](#自主优化循环) | Phase 0→3 完整流程 | 执行优化时跟随 |
| [results.tsv 格式](#resultstsv-格式) | 日志格式规范 | 记录结果时 |
| [high-leverage 操作](#实战-high-leverage-操作精髓速查) | 4条经实战验证的杠杆点 | 快速提分 |
| [优化策略库](#优化策略库) | P0-P3 优先级策略 | 诊断短板时 |
| [异常与边界条件](#异常与边界条件) | 10条 fallback 规则 | 遇到异常时 |
| [反例黑名单](#darwin-操作反例黑名单dim9-应用darwin-自己优化时不要做的事) | 9条反模式 | 每轮改动前对照 |
| [使用方式](#使用方式) | 5种使用模式 | 不确定怎么启动时 |
| [成果卡片](#成果卡片生成result-card) | 视觉报告生成 | Phase 3 汇总时 |

---

## 设计哲学

autoresearch 的精髓：
1. **单一可编辑资产** — 每次只改一个 SKILL.md
2. **双重评估** — 结构评分（静态分析）+ 效果验证（跑测试看输出）
3. **棘轮机制** — 只保留改进，自动回滚退步
4. **独立评分** — 评分用子agent，避免「自己改自己评」的偏差
5. **人在回路** — 每个skill优化完后暂停，用户确认再继续

与纯结构审查的区别：不只看 SKILL.md 写得规不规范，更看改完后**实际跑出来的效果是否更好**。

---

## 评估 Rubric（9维度，总分100）

> **设计依据**：基于 SkillLens 论文（arXiv 2605.23899）实证发现——LLM-as-judge 评估 skill 质量准确率仅 46.4%（接近随机），加入 meta-skill 三维度后提升到 73.8%。本 rubric 强化 dim3 / dim5 评分标准，新增 dim9「反例与黑名单」，权重平衡到 100。**目的：让评分对真实质量更敏感，减少 LLM judge 的乐观偏差。**

### 结构维度（59分）— 静态分析

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 1 | **Frontmatter质量** | 7 | name规范、description包含做什么+何时用+触发词、≤1024字符、**禁结尾加"灵活应用/根据情况判断"等空话尾巴** |
| 2 | **工作流清晰度** | 12 | 步骤明确可执行、有序号、每步有明确输入/输出 |
| 3 | **失败模式编码** | 12 | **必须显式编码失败模式**（写出"如果 X 失败 → Y"的明确分支）；有fallback路径、错误恢复；**只写正向流程而不写失败分支扣 ≥3 分**（SkillLens meta-skill 维度） |
| 4 | **检查点设计** | 6 | 关键决策前有用户确认、防止自主失控；**检查点必须显性标记（🔴/STOP/CHECKPOINT），仅靠"如果...建议..."措辞不算** |
| 5 | **可执行具体性** | 17 | 不模糊、有具体参数/格式/示例、可直接执行；**禁止"建议/可以考虑/根据情况/灵活把握/视情况而定"等软化措辞**——出现 ≥3 处扣 ≥3 分（SkillLens actionable specificity 维度） |
| 6 | **资源整合度** | 4 | references/scripts/assets引用正确、路径可达 |

### 效果维度（35分）— 需要实测

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 7 | **整体架构** | 12 | 结构层次清晰、不冗余不遗漏、与花叔生态一致；**冗余/AI腔废话段落（说白了/换句话说/首先其次综上等花叔禁用词）出现一处扣 1 分** |
| 8 | **实测表现** | 23 | 用测试prompt跑一遍，输出质量是否符合skill宣称的能力 |

### Meta-skill 维度（6分）— 反例与黑名单

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 9 | **反例与黑名单** | 6 | **skill 必须有"不要做什么"的反例清单**；只写"应该做 X"没有"不要做 Y"扣 ≥3 分；红灯/危险动作/反模式应单独章节列出（SkillLens risk-action blacklist 维度） |

### 评分规则
- 维度1-7、9：每个维度打 1-10 分，乘以权重得到该维度得分
- 维度8（实测表现）：跑2-3个测试prompt，按输出质量打1-10分
- **总分 = Σ(维度分 × 权重) / 10**，满分100
- 改进后总分必须 **严格高于** 改进前才保留

### Rubric 的实证基础

rubric 设计依据来自 **SkillLens 论文（arXiv 2605.23899）** + **本机 controlled study**：

- SkillLens 发现 LLM-as-judge 准确率仅 46.4%（接近随机），加入 meta-skill 三维度后升到 73.8%
- 本机对 huashu-research 做 4 类 degradation → 5 个独立 judge 盲测一致 V1>V2，Δ 均值 +46.5（5/5 high confidence）

**结论**：rubric 能识别 gross degradation，但 fine-grained quality difference 仍不可信，**重要决策必须人审**。

→ 详细论文证据 + 5 judges 完整数据 + HL 实战案例数字见 [references/skilllens-evidence.md](references/skilllens-evidence.md)
→ 用户偏好适配模式（直接执行/中文/简洁格式等）见 [references/user-preference-patterns.md](references/user-preference-patterns.md)
→ Runtime 中立性红灯/绿灯规则 + 例外清单见 [references/runtime-neutrality.md](references/runtime-neutrality.md)
→ 新建 skill 从零到优化的完整案例见 [references/prd-optimization-case-study.md](references/prd-optimization-case-study.md)

### 关于「实测表现」维度

这是与纯结构评分最大的区别。评分方式：

1. 为每个skill设计2-3个**典型用户prompt**（不是边缘case，是最常见的使用场景）
2. 用子agent执行：一个带skill跑，一个不带skill跑（baseline）
3. 对比输出质量，从以下角度打分：
   - 输出是否完成了用户意图？
   - 相比不带skill的baseline，质量提升明显吗？
   - 有没有skill引入的负面影响（过度冗余、跑偏、格式奇怪）？

若子 agent 不可用（超时/资源限制），退化为「干跑验证」：读完 skill 后模拟一个典型 prompt 的执行思路，判断流程是否合理；必须在 results.tsv 标注 `dry_run`。**dry_run 比例 > 30% → 评估失效警告**（来自本机 controlled study：dim8 实测维度权重 23%，无 full_test 验证时分数不可信）。

---

## Runtime 适配性审查（gate 项，独立于 9 维度评分）

skill 应当能在 Claude Code / Codex / Cursor / OpenClaw / Hermes / Gemini CLI / OpenCode 等 50+ skills-compatible runtime 通用——否则其他 agent 解析时会被「在 Claude Code 里」「Claude Code skill」等措辞误判为「不是给我用的」直接拒装（实例：nuwa-skill 因此被 Marvis agent 拒绝）。

### Phase 1 基线评估时强制跑一次红灯扫描

```bash
grep -nE "(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)" SKILL.md README.md 2>/dev/null
```

输出非空 = 红灯命中 → 强制把 Phase 2 第一轮定为 P0「runtime drift 修复」（写入 results.tsv 的 note 列 `runtime_warn=N`）。

### 例外（允许的「Claude Code 痕迹」）

frontmatter 触发词、花叔生态内部 skill 名引用、明确标注 runtime-specific 章节、commit message——这些正当出现，不算红灯。

→ 红灯/绿灯完整对照表 + 例外清单详细规则 + Phase 1/2/3 各阶段审查时机见 [references/runtime-neutrality.md](references/runtime-neutrality.md)

---

## 自主优化循环

### Phase 0: 初始化

```
1. 确认优化范围：
   - 全部skills → 扫描 .claude/skills/*/SKILL.md
   - 指定skills → 用户指定列表
2. 创建 git 分支：auto-optimize/YYYYMMDD-HHMM
3. 初始化 results.tsv（如不存在）
4. 读取现有 results.tsv 了解历史优化记录
```

### Phase 0.5: 测试Prompt设计

在评估之前，为每个skill设计测试prompt。这步很关键——没有测试prompt，「实测表现」维度就打不了分。

```
for each skill:
  1. 读取 SKILL.md，提取核心功能：
     - 从 description 和「使用方式」章节找出该 skill 的 3-5 个典型调用场景
     - 从触发词反推用户最可能说的原话
  2. 设计2-3个测试prompt，覆盖：
     - 最典型的使用场景（happy path）：用户用最简洁的方式触发核心功能
     - 一个稍复杂或有歧义的场景：用户意图模糊或需要多步决策
     - （可选）一个边界场景：用户要求与 skill 设计意图不完全匹配
  3. 每个 prompt 写 expected：用1-2句话描述「带 skill 执行」vs「不带 skill 执行」应有的质量差异
  4. 保存到 skill目录/test-prompts.json：
     [
       {"id": 1, "prompt": "用户原话", "expected": "带skill时应... 不带skill时可能..."},
       {"id": 2, "prompt": "...", "expected": "..."}
     ]
```

展示所有测试prompt给用户，**确认后再进入评估**。测试prompt的质量决定了优化方向是否正确。

**🔴 CHECKPOINT · 🛑 STOP：展示 test-prompts.json 内容，等用户确认或修改后再进入 Phase 1。**

> **例外**：如果用户此前已明确表达"直接执行"偏好，跳过本 CHECKPOINT，直接展示 test-prompts 内容并进入 Phase 1。

### Phase 1: 基线评估（Baseline）

```
for each skill in 优化范围:

  # 结构评分（主agent可以做）
  1. 读取 SKILL.md 全文
  2. 按维度1-7逐项打分（附简短理由）

  # 效果评分（用子agent做，独立于主agent）
  3. 对每个测试prompt，spawn子agent：
     - with_skill: 带着SKILL.md执行测试prompt
     - baseline: 不带skill执行同一prompt
  4. 对比两组输出，打维度8的分

  # 汇总
  5. 计算加权总分
  6. 记录到 results.tsv
```

**如果子agent不可用**（超时、环境限制），维度8用干跑验证打分，标注 `dry_run`。不要因为跑不了测试就跳过这个维度——哪怕是模拟推演也比完全不看效果好。

基线评估完成后，展示评分卡：

```
┌──────────────────────────┬───────┬──────────────┬──────────────┐
│ Skill                    │ Score │ 结构短板      │ 效果短板      │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ huashu-proofreading      │ 78    │ 边界条件      │ 测试prompt2  │
│ huashu-slides            │ 72    │ 指令具体性    │ baseline持平  │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ 平均                     │ 75    │              │              │
└──────────────────────────┴───────┴──────────────┴──────────────┘
```

**🔴 CHECKPOINT · 🛑 STOP：暂停等用户确认，再进入优化循环。**

> **例外**：如果用户此前已明确表达"直接执行"偏好（见异常表「用户说"不用再询问我"」条目），跳过本 CHECKPOINT，直接进入 Phase 2。

### Phase 2: 优化循环

用户确认后，按基线分数从低到高排序，先优化最弱的。

```
for each skill:
  round = 0
  while round < MAX_ROUNDS (默认3):
    round += 1

    # Step 1: 诊断
    找出得分最低的维度（结构或效果都算）
    # HL-3 警告：dim2/dim3/dim4 是相关簇，修一个时另两个常跟着涨
    # → 不要因为 dim3 最低就单独修，要看整簇短板再决定是否同步改

    # Step 2: 提出改进方案
    针对最低维度，生成1个具体改进方案：
      - 改什么（具体段落/行）
      - 为什么改（对应rubric哪条）
      - 预期提升多少分

    # Step 3: 执行改进
    编辑 SKILL.md
    git add + commit（message: "optimize {skill}: {改进摘要}"）

    # Step 4: 重新评估
    - 结构维度：主agent重新打分
    - 效果维度：spawn独立子agent重跑测试prompt（关键！不能自己评自己）

    # Step 5: 决策
    if 新总分 > 旧总分:
      status = "keep"，更新旧总分
      # HL-4 见好就收：连续2轮 Δ < 2 分 → break 进 Phase 3
      if last_delta < 2.0 and this_delta < 2.0:
        print("触顶信号：连续2轮边际收益 < 2 分，停止优化避免过度调整")
        break
    else:
      status = "revert"
      git revert HEAD（创建新commit回滚，不用reset --hard）
      记录失败尝试到 results.tsv
      break  # 该skill到瓶颈，跳到下一个

    # Step 6: 日志
    results.tsv 追加行

  # === 🔴 CHECKPOINT · 每个 skill 优化完后强制人审 ===
  展示该skill的改动摘要：
    - git diff（改前 vs 改后）
    - 分数变化（哪些维度提升/下降）
    - 测试prompt输出对比（如果跑过的话）
  等用户确认 OK 再继续下一个skill。
  如果用户说"不好"，回滚到该skill的优化前版本。

  > **例外**：如果用户此前已明确表达"直接执行"偏好，本 CHECKPOINT 改为**异步展示**：输出改动摘要后继续下一个skill，不阻塞等待确认。用户可在任何时候说"回滚 XX"来撤销。
```

### Phase 2.5: 探索性重写（按需触发）

当 hill-climbing 连续2个skill都在 round 1 就 break（涨不动）时，提议一次「探索性重写」：

```
1. 选一个瓶颈skill
2. git stash 保存当前最优版本
3. 从头重写SKILL.md（不是微调，是重新组织结构和表达方式）
4. 重新评估
5. if 重写版 > stash版: 采用重写版
   else: git stash pop 恢复
```

这解决了 hill-climbing 的局部最优问题——有时候需要「先拆后建」才能突破瓶颈。
**🔴 CHECKPOINT · 🛑 STOP：必须征得用户同意后才执行。**

### Phase 3: 汇总报告

```
## 优化报告

### 总览
- 优化skills数：N
- 总实验次数：M
- 保留改进：X（Y%）
- 回滚次数：Z
- 实测验证：A次完整测试 / B次干跑

### 分数变化
┌──────────────────────────┬────────┬────────┬────────┐
│ Skill                    │ Before │ After  │ Δ      │
├──────────────────────────┼────────┼────────┼────────┤
│ huashu-proofreading      │ 78     │ 87     │ +9     │
│ huashu-slides            │ 72     │ 83     │ +11    │
├──────────────────────────┼────────┼────────┼────────┤
│ 平均                     │ 75     │ 85     │ +10    │
└──────────────────────────┴────────┴────────┴────────┘

### 主要改进
1. [skill-A] 补充了边界条件处理，测试输出质量提升明显
2. [skill-B] 重组了workflow结构，baseline对比优势增大
```

---

## results.tsv 格式

```tsv
timestamp	commit	skill	old_score	new_score	status	dimension	note	eval_mode
2026-03-31T10:00	baseline	huashu-proofreading	-	78	baseline	-	初始评估	full_test
2026-03-31T10:05	a1b2c3d	huashu-proofreading	78	84	keep	边界条件	补充fallback	full_test
2026-03-31T10:10	b2c3d4e	huashu-proofreading	84	82	revert	指令具体性	过度细化	dry_run
```

新增 `eval_mode` 列：`full_test`（跑了子agent测试）或 `dry_run`（模拟推演）。
文件位置：`.claude/skills/darwin-skill/results.tsv`

---

## 实战 high-leverage 操作（精髓速查）

4 条经实战验证（huashu-gpt-image +10.85 / huashu-weread-advisor +14.9 / claude-design +16.5）。详细案例数据见 [references/skilllens-evidence.md](references/skilllens-evidence.md) 的「HL 实战案例」节。

- **HL-1（dim4）显性视觉标记是杠杆**：加 🔴 CHECKPOINT / 🛑 STOP，靠「必须」措辞不行——LLM 解析时扫描视觉标记。4 行改动撬动 dim4 +3 分
- **HL-2（dim3）if-then 三段式 fallback 表**：把「症状/解法」两列升级为「触发条件 / 一线修复 / 仍失败兜底」三段式。SkillLens failure-mechanism encoding 维度的落地
- **HL-3（Phase 2 诊断）维度相关簇警告**：dim2/3/4 是相关簇——修 dim3 时 dim2 常跟着涨。「找最低维度」时同时看相关簇短板再决定是否同步改
- **HL-4（Phase 2 退出）触顶自动 break**：连续 2 轮 Δ < 2 分 → break 进 Phase 3。+0.15 是停手信号不是继续信号；硬凑 MAX_ROUNDS=3 引入 over-engineering
- **HL-5（用户偏好适配）直接执行模式**：用户说"不用再询问我"或"直接执行"时，立即切换自主模式——跳过基线后 CHECKPOINT，每轮展示 diff 不阻塞，仅在 Phase 2.5 探索性重写前保留确认（高风险操作）。已在异常表中编码为正式 fallback

---

## 优化策略库

按优先级排序，每轮只做最高优先级的一个：

### P0: Runtime 适配性问题（gate 项命中 → 必须先修）
- README/SKILL.md 出现红灯措辞（如「在 Claude Code 里」「Claude Code skill」）→ 替换为 runtime-neutral 措辞
- Badge 钉死单一 runtime → 改为 `Agent Skills Standard` + `skills.sh` + `Multi-Runtime` 三个中立 badge
- 安装章节只给一种 runtime 的路径 → 改为「一行命令（auto-detect）+ 手动路径表 + 作为参考资料」三层结构
- 工作流硬编码 runtime-specific 工具且无 fallback → 给出通用替代方案或标注「仅在某 runtime 可用」
- 例外：skill 名明确标注单 runtime（如 `xxx-codex`）的，可跳过本项

### P0: 效果问题（实测发现的）
- 测试输出偏离用户意图 → 检查skill是否有误导性指令
- 带skill比不带还差 → skill可能过度约束，考虑精简
- 输出格式不符合预期 → 补充明确的输出模板

### P1: 结构性问题
- Frontmatter缺少触发词 → 补充中英文触发词
- 缺少Phase/Step结构 → 重组为线性流程
- 缺少用户确认检查点 → 在关键决策处插入
- **新建skill时忘记创建references/templates** → dim6资源整合度易低，Phase 0时检查是否需要support files

### P2: 具体性问题
- 步骤模糊（"处理图片"）→ 改为具体操作和参数
- 缺少输入/输出规格 → 补充格式、路径、示例
- 缺少异常处理 → 补充 "如果X失败，则Y"
- **子agent输出格式不统一** → 提供标准模板文件（templates/*.md）

### P3: 可读性问题
- 段落过长 → 拆分+用表格
- 重复描述 → 合并去重
- 缺少速查 → 添加TL;DR或决策树

---

## 异常与边界条件

流程假设环境理想，但实操常遇异常。以下预定义 fallback，保证优化过程不会「一跑就卡住」。

| 场景 | 触发条件 | 处理动作 |
|---|---|---|
| 不在 git 仓库 | `git rev-parse` 失败 | 询问用户：执行 `git init` 或回退到文件备份；用户选后者则 `cp SKILL.md SKILL.md.bak.YYYYMMDD-HHMM` 代替 revert |
| results.tsv 缺失 | 文件不存在 | 新建并写表头行（9列：含 eval_mode） |
| results.tsv 损坏 | 列数不匹配 / 非TSV | 备份为 `.bak.YYYYMMDD-HHMM` 后重建，告知用户 |
| 分支已存在 | `git checkout -b` 失败 | 分支名末尾加 `-2` / `-3`；第3次失败则切回现有分支并询问继续还是新起 |
| `git revert` 失败 | 冲突 / 工作树脏 | 先 `git stash`，重试；仍失败则从上一个 commit 的 SKILL.md 读出覆盖当前文件手动恢复 |
| MAX_ROUNDS 触顶（默认3） | 已跑3轮仍有短板 | 不强制 break，展示当前最弱维度问用户「继续加1轮 / 进入Phase 2.5 / 收工」 |
| 优化后超 150% 体积 | 新文件 > 原 × 1.5 | 拒绝提交，回到改进步骤精简（删冗余/合并重复），再评 |
| test-prompts.json 已存在 | 文件已在 skill 目录 | 默认复用并展示，问用户「复用 / 重写 / 追加」三选一 |
| SKILL.md 找不到 | 目录存在但无 SKILL.md | 该 skill 终止，results.tsv 记 `status=error`，继续下一个 |
| 分数计算规则 | 浮点精度漂移 | 总分保留 1 位小数，改进需严格 > 旧分（不靠四舍五入） |
| **git identity 未配置** | `git commit` 失败，提示 "Please tell me who you are" | 在 skill 目录执行 `git config user.email "darwin@hermes.local" && git config user.name "Darwin Optimizer"` 后再 commit |
| **Playwright/chromium 未安装** | 成果卡片截图失败（`ModuleNotFoundError: No module named 'playwright'` 或 `NO_CHROME`） | 跳过截图，提示用户「成果卡片 HTML 已生成，可在浏览器中打开查看」；不阻塞 Phase 3 完成 |
| **bc 等基础命令缺失** | `bc: command not found`，导致文件大小比例计算失败 | 用 Python 替代：`python3 -c "print(f'{current/original*100:.1f}')"` |
| **用户说"不用再询问我"或"直接执行"** | 用户明确授权自主执行，厌恶逐步确认 | **立即切换为自主模式**：跳过 Phase 1 基线评估后的 CHECKPOINT，直接进入 Phase 2 优化循环；每轮改动后展示 diff 和分数变化，不再停下来等确认；Phase 3 汇总后直接输出最终报告。仅在探索性重写（Phase 2.5）前保留一次确认（因涉及 stash/重写高风险操作）。记录用户偏好到 memory："用户偏好直接执行 over 逐步确认" |
| **用户要求"用中文交流"** | 用户明确中文偏好 | 所有输出、评分卡、测试prompt、results.tsv 注释均使用中文；skill 优化后的 SKILL.md 保持原文语言（不强制翻译），但评估报告和沟通语言切换为中文。记录到 memory |
| **用户偏好简洁列表格式** | 用户说"一行一个"或类似 | 输出列表时采用 clean one-item-per-line 格式，不添加 bullet points、编号或额外评论。记录到 memory |

**原则**：异常先告知用户，再按规则处理；绝不静默跳过或静默失败。

---

## darwin 操作反例黑名单（dim9 应用：darwin 自己优化时不要做的事）

来自本机 results.tsv 早期 40 次 0 revert 的教训 + Judge G/H 自指评估暴露的反模式。每条都是**真实踩过的坑**。

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|---|---|---|
| 1 | **同 context 自评自改** | 改完后立刻在同一 Claude session 打分，会有「我刚改的肯定更好」乐观偏差（SkillLens 实证 LLM-as-judge 准确率仅 46.4%）| 必须 spawn **独立子 agent** 评分，且至少 2 个 judge 共识才信 |
| 2 | **`git reset --hard` 当回滚** | 会丢工作树未提交改动；CI 历史断裂 | 用 `git revert HEAD` 创建反向 commit，保留可追溯链 |
| 3 | **为凑分增冗余** | 触顶后继续硬改往往是「加废话/加段落让 LLM 觉得更详细」，实际质量不变 | 触顶信号（连续 2 轮 Δ<2 分）→ break 进 Phase 3，**见好就收** |
| 4 | **跳过 test-prompts 直接评分** | 没有 test-prompts 的 dim8 是凭空打分，权重 23% 等于编造 | Phase 0.5 强制设计 2-3 prompts；若用户不给，默认编 3 个并展示确认 |
| 5 | **轮内改多个维度** | 多变量同时变，分数升降无法归因到具体改动 | 每轮 1 个维度；相关簇（dim2/3/4）改其一时观察另两个是否跟涨 |
| 6 | **dry_run 比例 > 30%** | dim8 实测维度形同虚设，分数虚高（早期 40 次记录 67% dry_run，0 revert） | 强制至少 1 个真实 full_test；dry_run 多的优化在 results.tsv 显式打 ⚠️ |
| 7 | **静默跳过异常** | 遇到 git/tsv 异常时静默继续，破坏 ratchet 完整性 | 异常表 10 条 fallback 必须先告知用户再处理 |
| 8 | **忽视维度相关性单独优化** | dim2/3/4 是相关簇，单独优化 dim2 时常发现已被前轮 dim3 修复推到顶 | 找最低维度时同时看相关簇短板，决定是否同步改 |
| 9 | **`replace_all=true` 在 patch 时误用** | 当前 session 实例：用 `replace_all=true` 修复双 `---` 分隔符，old_string 中「每轮 Phase 3...」在文件 15 处匹配，整文件被连环改写导致结构崩溃（标题、段落、表格被随机拼接）。根本原因：`replace_all` 不检查匹配位置的上下文一致性，只要 old_string 子串出现就替换 | ① NEVER 使用 `replace_all=true`，除非 old_string 已被验证为**全文件唯一**（如某行开头的完整 UUID 或极长特定短语） ② 若需批量替换已知模式（如统一单词），先 `grep -c` 确认命中数后再决定 ③ 出事后立即 `git checkout -- SKILL.md` 恢复文件，重新用更精准的唯一锚点 patch ④ 宁可多写几个单独的精准 patch，也不要用 `replace_all` 扫射 |
| 10 | **假设环境有 bc/playwright/chromium** | 文件大小比例计算依赖 `bc`，截图依赖 Playwright/chromium——这些在精简容器环境中常缺失，导致流程中断 | ① 数值计算一律用 Python（`python3 -c`）替代 shell 工具 ② 截图失败时优雅降级为「HTML 已生成，请浏览器查看」③ 在 Phase 0 初始化时检测关键工具可用性，提前告知用户 |

**触发场景**：每轮 Phase 2 改动前对照本表一次。任一反模式命中 → 改方案重写。

---

## 约束规则

1. **不改变skill的核心功能和用途** — 只优化"怎么写"和"怎么执行"，不改"做什么"
2. **不引入新依赖** — 不添加skill原本没有的scripts或references文件
3. **每轮只改一个维度** — 避免多个变更导致无法归因
4. **保持文件大小合理** — 优化后SKILL.md不应超过原始大小的150%
5. **尊重花叔风格** — 中文为主、简洁为上
6. **可回滚** — 所有改动在git分支上，用git revert而非reset --hard
7. **评分独立性** — 效果维度必须用子agent或至少干跑验证，不能在同一上下文里「改完直接评」
8. **Runtime 中立性** — skill 必须能在 Claude Code、Codex、Cursor、OpenClaw、Hermes 等任何 skills-compatible runtime 中正常运行。除非 skill 名明确绑定单一 runtime（如 `xxx-codex`、`huashu-slides-codex`），任何「在 Claude Code 里」「Claude Code skill」「单一 badge 钉死」「安装命令只给 `.claude/skills/` 一种路径」都视为 gate 不通过，须在 P0 优先修复（详见「Runtime 适配性审查」章节）

---

## 使用方式

### 全量优化（推荐首次使用）
```
用户："优化所有skills"
→ Phase 0-3 完整流程
→ 默认：先基线评估，按分数升序优先优化最低 5-10 个
```

### 单个优化
```
用户："优化 huashu-slides 这个skill"
→ 只对指定skill执行 Phase 0.5-2
```

### 新建skill优化
```
用户："创建一个XX skill" 或 "优化写PRD的skill"（但目标skill不存在时）
→ 先评估现有skill是否可改造（职责重叠？改造会破坏现有功能？）
→ 决策：改造现有skill 或 创建新skill
→ 创建新skill → 直接编写SKILL.md → Phase 1基线评估 → Phase 2优化
→ 参考案例: references/prd-optimization-case-study.md
```

### 仅评估不改
```
用户："评估所有skills的质量"
→ 只执行 Phase 0.5-1（设计测试prompt + 基线评估），不进入优化循环
```

### 查看历史
```
用户："看看skill优化历史"
→ 读取并展示 results.tsv
```

---

## 设计灵感

> "You write the goals and constraints in program.md; let an agent generate and test code deltas indefinitely; keep only what measurably improves the objective."
> — Karpathy, autoresearch

本skill的对应关系：
- **program.md** → 本文件（评估rubric和约束规则）
- **train.py** → 每个SKILL.md
- **val_bpb** → 9维加权总分（含实测表现 + meta-skill 反例黑名单）
- **git ratchet** → 只保留有改进的commit
- **test set** → 每个skill的test-prompts.json

区别：增加了人在回路（autoresearch是全自主的，skill优化需要人的判断力），以及双重评估机制（结构+效果），因为skill的「好坏」比loss数值更微妙。

---

## 成果卡片生成（Result Card）

每个skill优化完成后（或全量汇总后），自动生成视觉成果卡片，截图保存为PNG。

### 卡片模板

模板位置：`templates/result-card.html`

3种风格，每次随机选择一种：

| 风格 | CSS类 | URL hash | 视觉特点 |
|------|--------|----------|---------|
| Warm Swiss | `.theme-swiss` | `#swiss` | 暖白底+赤陶橙，Inter字体，干净网格 |
| Dark Terminal | `.theme-terminal` | `#terminal` | 近黑底+荧光绿，等宽字体，扫描线 |
| Newspaper | `.theme-newspaper` | `#newspaper` | 暖白纸+深红，衬线字体，双栏编辑风 |

### 生成流程

```
1. 复制 templates/result-card.html 到临时工作文件
2. 用 sed/编辑工具 替换占位数据：
   - data-field="skill-name" → 实际skill名
   - data-field="score-before/after/delta" → 实际分数
   - 9个维度的 dim-bar-before/after width → 实际百分比（若模板仍是旧 8 维布局，加一行 dim9 反例黑名单条目）
   - data-field="improvement-1/2/3" → 实际改进摘要
   - data-field="date" → 当前日期
3. 随机选择风格：hash 设为 swiss/terminal/newspaper 之一
4. 用 scripts/screenshot.mjs 截图（2x 高清，只截 .card 元素，自动 open 图片）：
   node .claude/skills/darwin-skill/scripts/screenshot.mjs \
     /abs/path/to/card.html /abs/path/to/output.png
   # 回退方案（脚本失败时）：
   npx playwright screenshot "file:///path/to/card.html#[theme]" \
     output.png --viewport-size=960,1280 --wait-for-timeout=2000
5. 提示用户查看成果卡片 PNG

### 资源文件速查

| 路径 | 用途 |
|---|---|
| `templates/result-card.html` | 3风格主模板（swiss/terminal/newspaper，hash切换） |
| `templates/result-card-dark.html` / `-white.html` | 单一风格替代模板（需要锁定风格时用） |
| `scripts/screenshot.mjs` | 2x 高清截图，只截 .card，自动 open |
| `results.tsv` | 历次优化日志（9列含 eval_mode） |
| `{skill目录}/test-prompts.json` | 每个 skill 的测试 prompt 集（用于维度8实测） |

### 何时生成

- **单skill卡片**：每个skill优化完成后，展示该skill的分数变化
- **总览卡片**：全部优化完成后（Phase 3），展示全局战绩

### 品牌元素

- 顶部：Darwin.skill 品牌标识 + 日期
- 底部：「Train your Skills like you train your models」+ github.com/alchaincyf/darwin-skill
