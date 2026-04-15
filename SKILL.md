---
name: darwin-skill
description: "Darwin Skill (达尔文.skill): autonomous skill optimizer inspired by Karpathy's autoresearch. Evaluates SKILL.md files using an 8-dimension rubric (structure + effectiveness), runs hill-climbing with git version control, validates improvements through test prompts, and generates visual result cards. Use when user mentions \"优化skill\", \"skill评分\", \"自动优化\", \"auto optimize\", \"skill质量检查\", \"达尔文\", \"darwin\", \"帮我改改skill\", \"skill怎么样\", \"提升skill质量\", \"skill review\", \"skill打分\"."
---

# Darwin Skill

> 借鉴 Karpathy autoresearch 的自主实验循环，对 skills 进行持续优化。
> 核心理念：**评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚**
> GitHub: https://github.com/alchaincyf/darwin-skill

---

## 核心原则

单一资产·双重评估（结构+实测）·棘轮回滚·独立评分·人在回路

---

## 约束规则

1. **不改变核心功能和用途** — 只优化"怎么写"和"怎么执行"，不改"做什么"
2. **不引入新依赖** — 不添加 skill 原本没有的 scripts 或 references
3. **每轮只改一个维度** — 避免多变更导致无法归因
4. **文件大小 ≤ 原始 150%** — 优化后 SKILL.md 不超过原始大小的 150%
4a. **轻量 skill 保护** — 原始 < 2KB 的 skill，优化后应控制在 1.8-2.5KB 绝对区间内。"得分高了但 skill 不再轻巧"是失败，不是成功
5. **可回滚** — 所有改动在 git 分支上，用 `git revert` 而非 `reset --hard`
6. **评分独立性** — 效果维度必须用子 agent 或干跑验证，不能同一上下文"改完直接评"
7. **评分闭环一致性** — 同一轮优化中，前后评估必须使用相同的测试 prompt、相同的 rubric 标准、相同的评分尺度。禁止"改完后放宽标准"或"换测试 prompt"来人为制造提升。如果测试 prompt 或 rubric 有调整，必须重跑基线。
8. **尊重花叔风格** — 中文为主、简洁为上

---

## Preflight 检查

优化开始前逐项确认。**逐 skill 执行**：单个 skill preflight 失败 → 记录 `status=skip`，跳过该 skill 继续其他 skill，不阻塞整体流程。

| # | 检查项 | 失败处理 |
|---|--------|---------|
| 1 | 目标 skill 的 SKILL.md 文件存在且可读 | 跳过该 skill（status=skip） |
| 2 | 目标 skill 目录可写 | 跳过该 skill（status=skip） |
| 3 | git 可用 | 降级：跳过版本控制，手动备份原始文件 |
| 4 | workspace 目录存在，不存在则创建 | 自动创建 |
| 5 | 完整 Rubric 可加载（`references/rubric.md`） | 降级：使用本文档内嵌速查表继续，results.tsv 标注 `rubric_mode=fallback` |
| 6 | 磁盘剩余 > 10MB | 警告但继续 |
| 7 | 子 agent 可用 | 降级：效果维度退化为干跑验证，results.tsv 标注 `eval_mode=dry_run` |

**降级原则**：任何降级都必须在 results.tsv 中如实标注，不要因为环境受限就跳过维度——模拟推演也比不评强。

---

## 评估 Rubric（8维度，总分100）

**加载规则：**
- 优先加载完整 Rubric：`skill_view(name="darwin-skill", file_path="references/rubric.md")`
- 若引用失败，使用下方速查表 + 评分规则继续，标注 `rubric_mode=fallback`
- **Phase 1 基线评估前** → 必须加载一次
- **Phase 2 每轮重评分前** → 必须重新加载（不依赖上下文缓存，确保标准一致）

速查表（fallback 时使用）：

| # | 维度 | 权重 | 一句话 |
|---|------|------|--------|
| 1 | Frontmatter质量 | 8 | name/description/触发词完整 |
| 2 | 工作流清晰度 | 15 | 有序号步骤，有输入/输出定义 |
| 3 | 边界条件覆盖 | 10 | 异常处理和 fallback 路径 |
| 4 | 检查点设计 | 7 | 关键决策前用户确认 |
| 5 | 指令具体性 | 15 | 参数/格式/示例可直接执行 |
| 6 | 资源整合度 | 5 | 引用文件路径可达 |
| 7 | 整体架构 | 15 | 结构清晰不冗余 |
| 8 | 实测表现 | 25 | 跑测试 prompt 验证输出质量 |

总分 = Σ(维度分 × 权重) / 10，满分100。

---

## Phase 0: 初始化

1. 确认优化范围：全部 skills（扫描 `~/.hermes/skills/*/SKILL.md`）或用户指定列表
2. 执行 Preflight 检查（见上方），记录降级项
3. 若 git 可用 → 创建分支 `auto-optimize/YYYYMMDD-HHMM`；否则手动备份原始文件
4. 初始化 `results.tsv`（如不存在），读取历史记录

---

## Phase 0.5: 测试 Prompt 设计

评估前为每个 skill 设计测试 prompt。没有测试 prompt，「实测表现」维度无法打分。

**设计流程：**
1. 读取 SKILL.md，理解 skill 做什么
2. 设计 2-3 个测试 prompt
3. 保存到 `skill目录/test-prompts.json`
4. 展示所有测试 prompt 给用户，**确认后再进入评估**

**硬规则：**
- 数量：最少 2 个，最多 3 个
- 覆盖：必须包含该 skill 最核心的主场景，禁止全用边缘 case
- 锁定：baseline 和 with_skill 必须使用完全同一组 prompt，评估期间不得替换。如需调整，必须重跑全部基线

测试 prompt 的质量决定优化方向是否正确。

---

## Phase 1: 基线评估

对每个 skill：

**结构评分（主 agent）：**
1. 加载完整 Rubric（或 fallback 到速查表）
2. 读取 SKILL.md 全文，按维度 1-7 逐项打分（附简短理由）

**效果评分（独立子 agent，或降级为干跑验证）：**
3. 对每个测试 prompt，spawn 子 agent：
   - with_skill：带着 SKILL.md 执行
   - baseline：不带 skill 执行同一 prompt
4. 对比两组输出，打维度 8 的分

**汇总：**
5. 计算加权总分，记录到 `results.tsv`
6. 将测试 prompt 集写入 `skill目录/test-prompts.json` 并锁定（后续所有评估只允许读取该文件，不允许重新生成或修改）
7. 展示评分卡（skill名 | 总分 | 结构短板 | 效果短板）

**暂停等用户确认，再进入优化循环。**

---

## 优化策略库

Phase 2 每轮从策略库选最高优先级的一个执行：

### P0: 效果问题（实测发现）
- 测试输出偏离用户意图 → 检查 skill 是否有误导性指令
- 带 skill 比不带还差 → 可能过度约束，考虑精简
- 输出格式不符合预期 → 补充明确输出模板

### P1: 结构性问题
- Frontmatter 缺触发词 → 补充中英文触发词
- 缺 Phase/Step 结构 → 重组为线性流程
- 缺用户确认检查点 → 在关键决策处插入

### P2: 具体性问题
- 步骤模糊 → 改为具体操作和参数
- 缺输入/输出规格 → 补充格式、路径、示例
- 缺异常处理 → 补充 "如果 X 失败，则 Y"

### P3: 可读性问题
- 段落过长 → 拆分+表格
- 重复描述 → 合并去重
- 缺速查 → 添加 TL;DR 或决策树

---

## 维度并列选择规则（Tie-Break）

当多个维度得分相同且为最低分时，不直接按顺序选择，按以下优先级决策：

### Step 1: 排除低价值维度
以下维度在极简 skill 中优先级降低：
- 资源整合度（如无外部依赖）
- Frontmatter（非核心执行路径）

### Step 2: 判断"结构杠杆"
优先选择能改变执行方式的维度：

优先级：
1. 工作流清晰度（是否有 Step / Phase / 执行顺序）
2. 检查点设计（是否有关键确认机制）
3. 边界条件覆盖（异常处理）
4. 指令具体性（参数/格式）

### Step 3: 参考最近一轮收益
- 若某维度上一轮 Δ = 0 → 降级（避免重复无效优化）
- 若某维度 Δ > 0 → 可继续（若仍未达标）

### Step 4: 判断主矛盾
识别当前 skill 的核心问题：
- 工具堆叠但无流程 → 选 工作流
- 有流程但容易误操作 → 选 检查点
- 正常路径 OK 但容易失败 → 选 边界条件
- 输出模糊 → 选 指令具体性

### 决策原则
选择"最可能带来结构性变化 + 实测表现提升"的维度，而非仅最低分。

**禁止：**
- 连续两轮选择同一维度但 Δ=0
- 为"补分"而优化低价值维度

---

## Phase 2: 优化循环

用户确认后，按基线分数从低到高排序，先优化最弱的。**并列时按 Tie-Break 规则选择。**

**round 来源**：每个 skill 的当前 round 必须从 results.tsv 中该 skill 的历史记录读取（最新一行的 round + 1），不得自行推断或从内存计数。若 results.tsv 无该 skill 记录，round 从 1 开始。

对每个 skill，执行以下循环协议：

1. **选择** 当前待优化 skill
2. **检查** round 计数器，若 ≥ 3，跳到步骤 10
3. **诊断** 找当前得分最低的维度
4. **选策略** 从优化策略库选对应最高优先级策略
5. **执行** 编辑 SKILL.md 并提交（git commit 或记录变更）
6. **重加载** 重新加载 Rubric（不依赖缓存）
7. **重评分** 使用与基线完全相同的测试 prompt 和评分标准进行评分。若评分理由发生变化（非结果变化，而是标准/角度变化），必须在 results.tsv 的 note 字段标注「评分标准漂移：[具体变化]」
8. **决策** 若新总分 > 旧总分 → keep，更新旧总分，round++，回到步骤 3；若新总分 ≤ 旧总分 → revert，跳到步骤 10
9. **记录** 追加 results.tsv，回到步骤 2
10. **人类检查点** 展示该 skill 的 git diff + 分数变化，等用户确认后再处理下一个 skill

---

## Phase 2.5: 探索性重写（可选）

当 hill-climbing 连续 2 个 skill 在 round 1 就 break，**且这些 skill 的 eval_mode=full_test、评分可信**时，提议「探索性重写」。若 eval_mode=dry_run，不得触发探索性重写（评分不可靠时重写没有依据）。

1. 选瓶颈 skill
2. `git stash` 保存当前最优版（或手动备份）
3. 从头重写 SKILL.md（重新组织结构和表达方式）
4. 重新评估
5. 重写版 > stash 版 → 采用；否则恢复

解决 hill-climbing 局部最优问题。**必须征得用户同意。**

---

## Phase 3: 汇总报告

**成功标准建议**（展示给用户确认）：
- 总分提升 ≥ 8 分（轻量 skill 可放宽至 ≥ 5）
- 最弱维度显著提升（至少 +3 分）
- 核心工作流维度同步提升
- 文件大小不失控（见约束 4a）

**统计摘要：**
- 优化 skills 数 / 总实验次数
- 保留改进 X 次（Y%）/ 回滚 Z 次
- 实测验证 A 次 / 干跑 B 次
- 每个 skill：Before → After → Δ

**结论分层（每个 skill 归入一类）：**

| 分类 | 判断标准 | 建议动作 |
|------|---------|---------|
| 继续自动优化 | 分数稳步提升且未到瓶颈 | 下次 Darwin 运行时继续 |
| 已到局部最优 | 连续 revert 或分数停滞 ≥ 2 轮 | 建议人工审查，考虑 Phase 2.5 探索性重写 |
| 建议人工重写 | 核心结构有问题，hill-climbing 无法解决 | 标记为需重构，不浪费自动优化轮次 |
| 评分不可信 | eval_mode=dry_run 且结构评分也不确定 | 补充测试 prompt 后重跑基线 |

---

## results.tsv

位置：`~/.hermes/skills/creative/darwin-skill/workspace/results.tsv`

列：`timestamp | commit | skill | round | old_score | new_score | status | dimension | note | eval_mode | rubric_mode`

- status: `keep` / `revert` / `baseline` / `skip`
- eval_mode: `full_test` / `dry_run`
- rubric_mode: `full` / `fallback`
- round: 该 skill 的第几轮优化（baseline 记为 0）

---

## 使用方式

| 触发 | 执行范围 |
|------|---------|
| "优化所有skills" / "全量优化" | Phase 0-3，建议先评估再选最低 5-10 个重点 |
| "优化 [skill名]" | Phase 0.5-2，仅指定 skill |
| "评估skills质量" / "给skill打分" | Phase 0.5-1，不进入优化循环 |
| "优化历史" / "看看改了什么" | 读取 results.tsv 展示 |

---

## 成果卡片（可选）

优化完成后可生成视觉成果卡片（3种主题，Playwright 截图）。

详见：`skill_view(name="darwin-skill", file_path="references/result-card-guide.md")`
