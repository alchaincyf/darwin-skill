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
5. **可回滚** — 所有改动在 git 分支上，用 `git revert` 而非 `reset --hard`
6. **评分独立性** — 效果维度必须用子 agent 或干跑验证，不能同一上下文"改完直接评"
7. **评分闭环一致性** — 同一轮优化中，前后评估必须使用相同的测试 prompt、相同的 rubric 标准、相同的评分尺度。禁止"改完后放宽标准"或"换测试 prompt"来人为制造提升。如果测试 prompt 或 rubric 有调整，必须重跑基线。
8. **尊重花叔风格** — 中文为主、简洁为上

---

## Preflight 检查

优化开始前必须确认：

| 检查项 | 命令/方法 | 失败处理 |
|--------|----------|---------|
| 目标 skill 存在且可读 | `read_file` SKILL.md | 报错退出 |
| 目标 skill 目录可写 | `test -w` | 报错退出 |
| git 可用 | `git --version` | 降级：无版本控制，手动备份 |
| workspace 目录存在 | `mkdir -p workspace/` | 自动创建 |
| 磁盘空间 > 10MB | `df -h .` | 警告但继续 |
| Rubric 可加载 | `skill_view(file_path="references/rubric.md")` | 降级：用速查表评分 |

**降级策略**：如果子 agent 不可用（超时/环境限制），效果维度退化为干跑验证，在 results.tsv 标注 `dry_run`。不要因为跑不了测试就跳过效果维度——模拟推演也比完全不看强。

---

## 评估 Rubric（8维度，总分100）

**加载时机（强制）：**
- Phase 1 基线评估前 → 必须加载完整 Rubric
- Phase 2 每轮重评分前 → 必须重新加载（确保评分标准一致，不依赖上下文缓存）
- 加载方式：`skill_view(name="darwin-skill", file_path="references/rubric.md")`

速查表（完整标准见上方 reference）：

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
2. 执行 Preflight 检查（见上方）
3. 创建 git 分支：`auto-optimize/YYYYMMDD-HHMM`
4. 初始化 `results.tsv`（如不存在），读取历史记录

---

## Phase 0.5: 测试 Prompt 设计

评估前为每个 skill 设计测试 prompt。没有测试 prompt，「实测表现」维度无法打分。

1. 读取 SKILL.md，理解 skill 做什么
2. 设计 2-3 个测试 prompt：最典型场景（happy path）+ 一个稍复杂场景
3. 保存到 `skill目录/test-prompts.json`
4. **展示所有测试 prompt 给用户，确认后再进入评估**

测试 prompt 的质量决定优化方向是否正确。

---

## Phase 1: 基线评估

对每个 skill：

**结构评分（主 agent）：**
1. 加载完整 Rubric → `skill_view(name="darwin-skill", file_path="references/rubric.md")`
2. 读取 SKILL.md 全文，按维度 1-7 逐项打分（附简短理由）

**效果评分（独立子 agent）：**
3. 对每个测试 prompt，spawn 子 agent：
   - with_skill：带着 SKILL.md 执行
   - baseline：不带 skill 执行同一 prompt
4. 对比两组输出，打维度 8 的分

**汇总：**
5. 计算加权总分，记录到 `results.tsv`
6. 展示评分卡（skill名 | 总分 | 结构短板 | 效果短板）

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

## Phase 2: 优化循环

用户确认后，按基线分数从低到高排序，先优化最弱的。

```
for each skill:
  round = 0
  while round < MAX_ROUNDS (默认3):
    round += 1

    1. 诊断：找得分最低的维度
    2. 策略：从策略库选最高优先级修复
    3. 执行：编辑 SKILL.md → git commit
    4. 重评：重新加载 Rubric → 独立评分（同 prompt、同标准）
    5. 决策：新分 > 旧分 → keep；否则 revert + break
    6. 日志：追加 results.tsv

  # 每个 skill 优化完 → 展示 git diff + 分数变化，等用户确认
```

---

## Phase 2.5: 探索性重写（可选）

当 hill-climbing 连续 2 个 skill 在 round 1 就 break 时，提议「探索性重写」：

1. 选瓶颈 skill
2. `git stash` 保存当前最优版
3. 从头重写 SKILL.md（重新组织结构和表达方式）
4. 重新评估
5. 重写版 > stash 版 → 采用；否则 `git stash pop` 恢复

解决 hill-climbing 局部最优问题。**必须征得用户同意。**

---

## Phase 3: 汇总报告

输出：
- 优化 skills 数 / 总实验次数
- 保留改进 X 次（Y%）/ 回滚 Z 次
- 实测验证 A 次 / 干跑 B 次
- 每个 skill：Before → After → Δ
- 主要改进摘要（1-3 条）

---

## results.tsv

位置：`~/.hermes/skills/creative/darwin-skill/workspace/results.tsv`

列：`timestamp | commit | skill | old_score | new_score | status | dimension | note | eval_mode`

- status: `keep` / `revert` / `baseline`
- eval_mode: `full_test`（跑了子 agent 测试）或 `dry_run`（模拟推演）

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
