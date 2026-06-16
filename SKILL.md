---
name: darwin-skill
description: "Darwin Skill 2.0 (达尔文.skill 2.0): autonomous skill optimizer, integrating SkillLens 9-dim rubric, SkillOpt validation gates, evidence-backed domain rubrics, domain rubric quality evaluation, git checkpoints, independent judges, test prompts, and visual result cards. Use when user mentions \"优化skill\", \"skill评分\", \"自动优化\", \"auto optimize\", \"skill质量检查\", \"达尔文\", \"darwin\", \"帮我改改skill\", \"skill怎么样\", \"提升skill质量\", \"skill review\", \"skill打分\"."
---

# Darwin Skill 2.0

> **v2.0 · 2026-05-28** — 吸收 Microsoft Research SkillLens（arXiv 2605.23899）的 9 维评分药方 + SkillOpt（arXiv 2605.23904）的 validation-gated 验证机制 + human in the loop 三层守关；当前版本新增领域研究、个体化领域评分标准和领域评分标准质量评估。
>
> 借鉴 Karpathy autoresearch 的自主实验循环，对 skills 进行持续优化。
> 核心理念：**评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚 → 生成成果卡片**
> GitHub: https://github.com/alchaincyf/darwin-skill

---

## 设计哲学

autoresearch 的精髓：
1. **单一可编辑资产** — 每次只改一个 SKILL.md
2. **双重评估** — 结构评分（静态分析）+ 效果验证（跑测试看输出）
3. **棘轮机制** — 只保留改进，自动回滚退步
4. **独立评分** — 评分用子agent，避免「自己改自己评」的偏差
5. **人在回路** — 每个skill优化完后暂停，用户确认再继续
6. **领域依据可查** — 领域评分标准必须来自目标任务、用户资料、项目文件、研究结果或失败风险；不能凭文件名和少量关键词套用固定评分表

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

## 个体化领域评分标准

公共 9 维 rubric 只评价 skill 文件质量和通用执行质量。为了判断目标 skill 是否真的完成自己的任务，Darwin 在正式评分前可以生成并冻结一份领域评分标准。

### 领域评分产物

| 文件 | 作用 |
|---|---|
| `domain-research.md` | 记录领域调查研究结果：研究范围、目标任务、证据、发现、失败模式、证据空白和置信度 |
| `domain-research-meta.json` | 记录研究版本、创建时间、研究方法、来源、置信度和证据空白 |
| `domain-rubric.md` | 记录领域评分标准：任务目标、输入输出、评分维度、权重、1/5/10 分锚点、hard gates 和待确认问题 |
| `domain-test-prompts.json` | 记录领域测试 prompt，每条包含目的、预期检查点、目标维度和目标 hard gate |
| `domain-rubric-evaluation.md` | 记录领域评分标准本身的质量评估说明 |
| `domain-rubric-evaluation.json` | 记录质量总分、RQ1-RQ9 维度分、hard gate 检查、结论和必要修订 |
| `domain-rubric-meta.json` | 记录 rubric 版本、研究版本、质量分、质量结论、确认要求和冻结状态 |

### 领域研究路径

生成 `domain-rubric.md` 前，必须先执行领域调查研究。研究路径按以下顺序选择，记录实际使用的方法：

1. 当前系统有 deep research 类型 skill：优先调用该 skill 做简要研究。
2. 用户提供领域资料、项目文档或参考文件：优先读取这些材料。
3. 当前系统具备联网搜索能力：查找权威资料、官方文档、标准、专业指南或高质量来源。
4. 没有搜索能力：根据 `SKILL.md`、用户目标、测试 prompt、输出样本和失败案例做内部推断。
5. 仍无法可靠判断任务标准：生成低置信度研究结果，并要求用户确认。

硬性规则：

- 不得假装已经搜索、读取资料或调用研究工具。
- 不得把模型已有知识写成外部资料。
- 使用联网资料时，必须记录来源。
- 使用内部 skill 或知识库时，必须记录调用对象。
- 只使用模型已有知识或一般推断时，`confidence_level` 不得为 `high`。
- 资料不足时，必须记录 `evidence_gaps` 并要求用户确认。

### 领域评分标准质量评估

领域评分标准冻结前，必须先评估该评分标准本身是否值得使用。总分 100，维度如下：

| ID | 维度 | 权重 |
|---|---|---:|
| RQ1 | 目标匹配度 | 15 |
| RQ2 | 研究依据充分性 | 15 |
| RQ3 | 维度完整性 | 10 |
| RQ4 | 维度独立性 | 10 |
| RQ5 | 可观察性与可评分性 | 15 |
| RQ6 | 权重合理性 | 10 |
| RQ7 | hard gates 合理性 | 10 |
| RQ8 | 测试 prompt 匹配度 | 10 |
| RQ9 | 抗模板污染能力 | 5 |

质量门槛：

- `overall_score >= 80`：可进入用户确认阶段。
- `65 <= overall_score < 80`：必须修订后再确认。
- `overall_score < 65`：默认拒绝，不进入正式优化流程。
- RQ1 低于 10/15、RQ5 低于 10/15、RQ7 低于 6/10：不得接受。
- 研究置信度为 `low`：必须进入用户确认，不得自动冻结。
- 发现模板污染且 `reject_on_template_contamination = true`：必须修订。

默认配置：

```json
{
  "domain_rubric_quality_threshold": 80,
  "allow_low_confidence_rubric": false,
  "require_user_confirmation_for_low_confidence": true,
  "reject_on_template_contamination": true
}
```

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
   - 全部skills → 扫描当前 runtime 配置的 skills 目录下所有 `SKILL.md`
   - 指定skills → 用户指定列表
2. 创建 git 分支：auto-optimize/YYYYMMDD-HHMM
3. 初始化 results.tsv（如不存在）
4. 读取现有 results.tsv 了解历史优化记录
```

### Phase 0.10: 领域调查研究

在生成领域评分标准前，先为每个目标 skill 形成最小可复查研究记录。

```
for each skill:
  1. 读取 SKILL.md、用户目标、任务说明、已有 test-prompts.json、输出样本和失败案例
  2. 探测可用研究能力：
     - deep research 类型 skill
     - 用户提供资料或项目文件
     - 联网搜索能力
     - 仅内部知识或一般推断
  3. 按优先级选择实际研究路径
  4. 生成 domain-research.md：
     - Research Scope
     - Skill Goal Summary
     - Expected Task Outcome
     - Available Evidence
     - Research Method
     - Key Findings
     - Candidate Evaluation Concerns
     - Common Failure Modes
     - High-Risk Failure Modes
     - Evidence Gaps
     - Confidence Level
     - Notes
  5. 生成 domain-research-meta.json：
     {
       "research_version": "...",
       "created_at": "YYYY-MM-DDTHH:mm:ssZ",
       "source_skill_path": "SKILL.md",
       "research_methods": ["user_provided_materials"],
       "sources": [],
       "confidence_level": "medium",
       "evidence_gaps": [],
       "notes": ""
     }
```

如果没有研究工具，不停止流程；改用内部推断，`research_methods` 写 `internal_knowledge` 或 `generic_inference`，置信度只能为 `low` 或 `medium`，并要求用户确认。

### Phase 0.25: 生成个体化领域评分标准

领域评分标准必须读取 Phase 0.10 的研究结果，不能只看文件名或目录名。

```
for each skill:
  1. 读取 SKILL.md、用户目标、domain-research.md、domain-research-meta.json、测试 prompt、输出样本和失败案例
  2. 生成 domain-rubric.md：
     - domain_name
     - skill_goal
     - expected_input
     - expected_output
     - user_intent
     - success_criteria
     - dimensions（每项含 id、weight、1/5/10 anchors、common_failures、evidence_to_check、source_refs）
     - hard_gates
     - confidence_level
     - questions_for_user
  3. 生成初始 domain-rubric-meta.json：
     - rubric_version
     - research_version
     - source_skill_path
     - common_weight
     - domain_weight
     - research_confidence_level
     - requires_user_confirmation
     - is_frozen = false
```

规则：

- 每个领域评分维度必须能追溯到任务目标、研究发现、用户资料或失败风险。
- 不得把无关背景信息改写成评分维度。
- 不得把公共 9 维 rubric 重新命名后当作领域评分维度。
- 研究置信度为 `low` 时，领域评分标准也必须标记低置信度。
- 证据不足时，必须在 `questions_for_user` 中列出待确认问题。

### Phase 0.30: 领域评分标准质量评估

领域评分标准不得直接进入优化流程，必须先评估其自身质量。

```
for each skill:
  1. 读取 domain-rubric.md、domain-research.md、domain-rubric-meta.json、domain-test-prompts.json、SKILL.md 和用户目标
  2. 按 RQ1-RQ9 打分，总分 100
  3. 生成 domain-rubric-evaluation.md
  4. 生成 domain-rubric-evaluation.json：
     {
       "rubric_version": "...",
       "evaluation_version": "...",
       "created_at": "YYYY-MM-DDTHH:mm:ssZ",
       "overall_score": 0,
       "dimension_scores": [],
       "hard_gate_review": {"passed": true, "issues": []},
       "decision": "accept",
       "required_revisions": [],
       "notes": ""
     }
  5. 把质量分、质量结论和 evaluation_version 写回 domain-rubric-meta.json
```

允许的 `decision`：

- `accept`
- `revise`
- `reject`
- `needs_user_confirmation`

如果质量不合格，不能进入正式优化循环。先根据 `required_revisions` 修订 `domain-rubric.md`，再重新运行 Phase 0.30。连续修订仍失败时，停止并要求用户介入。

### Phase 0.35: 用户确认并冻结领域评分标准

质量评估完成后，展示以下材料给用户：

1. `domain-rubric.md`
2. `domain-research.md`
3. `domain-rubric-evaluation.md`
4. `domain-test-prompts.json`

用户可选择：

1. 接受并冻结
2. 修改后冻结
3. 要求重新研究
4. 要求重新生成评分标准
5. 跳过领域评分

冻结规则：

- 冻结后，当前优化轮不得自动修改 `domain-rubric.md`。
- 冻结后，当前优化轮不得自动修改 `domain-rubric-evaluation.md`。
- 用户修改领域评分标准后，必须重新运行 Phase 0.30。
- 研究依据变化后，必须重新运行 Phase 0.25 和 Phase 0.30。

### Phase 0.5: 测试Prompt设计

在评估之前，为每个skill设计测试prompt。这步很关键——没有测试prompt，「实测表现」维度就打不了分。

```
for each skill:
  1. 读取 SKILL.md，理解它做什么
  2. 设计2-3个公共测试prompt，覆盖：
     - 最典型的使用场景（happy path）
     - 一个稍复杂或有歧义的场景
  3. 保存到 skill目录/test-prompts.json：
     [
       {"id": 1, "prompt": "用户会说的话", "expected": "期望输出的简短描述"},
       {"id": 2, "prompt": "...", "expected": "..."}
     ]
  4. 如果启用领域评分，读取 domain-rubric.md，生成至少3个 domain-test-prompts.json 条目：
     [
       {
         "id": "domain-1",
         "prompt": "...",
         "purpose": "检查什么任务质量",
         "expected_checks": ["..."],
         "target_dimensions": ["D1"],
         "target_hard_gates": []
       }
     ]
```

展示所有公共测试 prompt 和领域测试 prompt 给用户，**确认后再进入评估**。测试 prompt 的质量决定了优化方向是否正确。

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
  5. 计算 common_score
  6. 如果领域评分已启用并冻结：
     - 按 domain-rubric.md 计算 domain_score
     - 检查 hard gates
     - 计算 composite_score = common_score * common_weight + domain_score * domain_weight
  7. 如果领域评分被跳过：
     - composite_score = common_score
     - 报告中标注 domain scoring skipped
  8. 记录到 results.tsv 或兼容的新结果记录
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

基线报告必须同时列出：

- `common_score`
- `domain_score`（如启用）
- `composite_score`
- `domain_name`
- `rubric_version`
- `rubric_quality_score`
- `rubric_quality_decision`
- `hard_gate_status`

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
    if hard_gate 触发:
      status = "revert"
      git revert HEAD
      记录 hard_gate_reason
      break
    else if common_score 下降:
      status = "revert"
      git revert HEAD
      break
    else if domain_score 下降且领域评分未被用户跳过:
      status = "revert"
      git revert HEAD
      break
    else if composite_score > 旧 composite_score:
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
    - 公共评分、领域评分、综合评分变化
    - hard gates 状态
    - 领域评分标准质量结论
    - 测试prompt输出对比（如果跑过的话）
  等用户确认 OK 再继续下一个skill。
  如果用户说"不好"，回滚到该skill的优化前版本。
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

### Domain Research
- Research Version:
- Research Methods:
- Confidence Level:
- Evidence Gaps:

### Domain Rubric Quality
- Rubric Version:
- Quality Score:
- Decision:
- Required Revisions:
- Forced Low-Quality Use Risk:
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
文件位置：当前 darwin-skill 目录下的 `results.tsv`

兼容扩展字段：

```tsv
common_score	domain_score	composite_score	domain_name	rubric_version	hard_gate_status	hard_gate_reason	rubric_quality_score	rubric_quality_decision	research_confidence_level
```

旧 `results.tsv` 缺少这些字段时必须能读取。新增记录时，优先写入扩展字段；如果用户要求保持旧格式，则报告中必须说明领域评分结果未写入旧文件。

---

## 实战 high-leverage 操作（精髓速查）

4 条经实战验证（huashu-gpt-image +10.85 / huashu-weread-advisor +14.9 / claude-design +16.5）。详细案例数据见 [references/skilllens-evidence.md](references/skilllens-evidence.md) 的「HL 实战案例」节。

- **HL-1（dim4）显性视觉标记是杠杆**：加 🔴 CHECKPOINT / 🛑 STOP，靠「必须」措辞不行——LLM 解析时扫描视觉标记。4 行改动撬动 dim4 +3 分
- **HL-2（dim3）if-then 三段式 fallback 表**：把「症状/解法」两列升级为「触发条件 / 一线修复 / 仍失败兜底」三段式。SkillLens failure-mechanism encoding 维度的落地
- **HL-3（Phase 2 诊断）维度相关簇警告**：dim2/3/4 是相关簇——修 dim3 时 dim2 常跟着涨。「找最低维度」时同时看相关簇短板再决定是否同步改
- **HL-4（Phase 2 退出）触顶自动 break**：连续 2 轮 Δ < 2 分 → break 进 Phase 3。+0.15 是停手信号不是继续信号；硬凑 MAX_ROUNDS=3 引入 over-engineering

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

### P2: 具体性问题
- 步骤模糊（"处理图片"）→ 改为具体操作和参数
- 缺少输入/输出规格 → 补充格式、路径、示例
- 缺少异常处理 → 补充 "如果X失败，则Y"

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
| 无研究工具 | 无 deep research、无用户资料、无联网搜索 | 用内部推断生成 `domain-research.md`，置信度标记 `low` 或 `medium`，要求用户确认 |
| 研究资料不足 | 证据空白影响评分维度判断 | 生成初步领域评分标准，列出 `evidence_gaps` 和待确认问题，降低置信度 |
| 质量评估不合格 | `domain-rubric-evaluation.json` 结论为 `revise` 或 `reject` | 不进入正式优化循环，按 `required_revisions` 修订后重新评估 |
| 低置信度未确认 | `research_confidence_level=low` 且用户未确认 | 不冻结领域评分标准，不执行正式领域评分 |
| 冻结后被自动改写 | 优化循环试图修改 `domain-rubric.md` 或质量评估文件 | 拒绝改写，记录原因，要求用户显式重新研究或重新生成 |

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
| 9 | **伪造领域研究来源** | 没有搜索、读取或调用却写成外部依据，会误导评分标准 | 只记录实际使用的资料；内部推断必须标为低证据等级 |
| 10 | **低质量领域评分标准直接优化** | 错误评分标准会引导 skill 改向错误目标 | 先修订并重新运行 Phase 0.30；不达标不得进入正式优化循环 |

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

### 学术依据 & Credits

- **SkillLens**（arXiv [2605.23899](https://arxiv.org/abs/2605.23899)）：9 维 rubric 的实证来源（LLM 自评 46.4% → 加 meta-skill 三维度后 73.8%）。
- **SkillOpt**（arXiv [2605.23904](https://arxiv.org/abs/2605.23904)）：validation-gated edits 形式化框架。代码 [github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)（`pip install skillopt`）、项目页 [microsoft.github.io/SkillOpt](https://microsoft.github.io/SkillOpt/)。🤝 2026-06-03 微软官方仓库已把 darwin-skill 列入集成名单。
- **autoresearch**：[github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch)，本 skill 1.0 的原始灵感。

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
   node <darwin-skill-dir>/scripts/screenshot.mjs \
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
