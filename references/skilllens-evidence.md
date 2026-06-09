# SkillLens 实证基线 + darwin-skill 本机验证数据

> SKILL.md 在「评估 Rubric」章节会引用本文件。论文证据可外部核验；本机 controlled study / HL 案例是作者内部实验摘要，原始 judge logs 与 results.tsv 未随仓库发布时，不应被表述为可独立复现实验。

---

## SkillLens 论文实证（外部证据）

**论文**：From Raw Experience to Skill Consumption: A Systematic Study of Model-Generated Agent Skills
**作者**：Microsoft Research + 复旦大学 + 上海交大（16 作者）
**arXiv**：2605.23899（2026-05-22，与 SkillOpt 同期发布）
**实验规模**：5 domains（ALFWorld / SpreadsheetBench / SWE-bench-Verified / SEAL-0 / BFCL-v4）× 6 targets × 5 extractors

### 关键发现

1. **75% 案例 skill 有正收益，25% 出现 negative transfer**——即「加 skill 比不加还差」
2. **强 agent 不一定是好 extractor**（Gemini-3.1-FL 在 skill 提取效率上反超 GPT-5.4）
3. **LLM-as-judge 准确率仅 46.4%**——给 LLM judge 两份 skill，让它选哪份更好，**比扔硬币（50%）还差**
4. **meta-skill rubric 把准确率提升到 73.8%**——加入三个维度：
   - **Failure-mechanism encoding**（必须显式编码失败模式）
   - **Actionable specificity**（禁止"考虑/可能"软化措辞）
   - **Risk-action blacklist**（必须有反例清单）
5. 所有 domain 一致 +1.55pp 提升（meta-rubric 不是某个 domain 的特例）

### 对 darwin-skill 的意义

旧 8 维 rubric 全部由 LLM judge 打分 → 系统性乐观偏差 → 本机 results.tsv 早期 40 次 0 revert / 67% dry_run 印证。

v2 9 维 rubric 强化 dim3/dim5 + 新增 dim9 是 SkillLens 验证过的方向。**但即使 73.8%，每 4 次决策仍错 1 次——重要决策必须人审确认。**

---

## 本机 controlled study（2026-05-27，作者内部实验摘要）

### 实验设计

- **目标 skill**：huashu-research（170 行，独立度高）
- **V1**：当前 GitHub 仓库最新版（被 darwin-skill 优化过 +33 分的版本）
- **V2 (degraded)**：在 V1 基础上应用 4 类明确质量劣化：
  - **D1 模糊化具体指令**：「必须/立即」→「建议/可以根据情况」
  - **D2 删除关键检查点**：删掉 2 个 🔴 检查点
  - **D3 删掉异常处理表**：整段「## 异常处理」章节删除
  - **D4 插入 AI 腔废话**：在 Step 2、Step 3 插入花叔禁用词 9 个套话
- **5 个独立 judge agent**（general-purpose subagent，无 context 共享）盲测打分
- 一半 judge 先读 V1 后读 V2，另一半反序（去除位置偏差）

### 结果

| Judge | 顺序 | V1 总分 | V2 总分 | Δ | Verdict | Confidence |
|---|---|---|---|---|---|---|
| 1 | V1 → V2 | 89.5 | 41.7 | **+47.8** | V1>V2 | high |
| 2 | V2 → V1 | 90.2 | 46.7 | **+43.5** | V1>V2 | high |
| 3 | V1 → V2 | 89.5 | 37.6 | **+51.9** | V1>V2 | high |
| 4 | V2 → V1 | 89.5 | 48.4 | **+41.1** | V1>V2 | high |
| 5 | V1 → V2 | 89.5 | 41.4 | **+48.1** | V1>V2 | high |
| **均值** | — | **89.6** | **43.2** | **+46.5** | **5/5 V1>V2** | **5/5 high** |

### 维度级共识

| 维度 | V1 均值 | V2 均值 | Δ | 一致性 |
|---|---|---|---|---|
| 1. Frontmatter | 9.0 | 5.6 | -3.4 | 全部识别 |
| 2. 工作流清晰度 | 9.0 | 5.0 | -4.0 | 全部识别 |
| 3. 边界条件覆盖 | 9.2 | 3.4 | -5.8 | **最明显劣化** |
| 4. 检查点设计 | 9.0 | 2.6 | -6.4 | **最明显劣化** |
| 5. 指令具体性 | 9.0 | 3.6 | -5.4 | 全部识别 |
| 6. 资源整合度 | 8.0 | 6.8 | -1.2 | 弱 |
| 7. 整体架构 | 9.0 | 4.6 | -4.4 | 全部识别 |
| 8. 实测表现 | 9.0 | 3.6 | -5.4 | 全部识别 |

### 结论

**rubric 能识别 gross degradation（5/5 high confidence）**，但**这不能证明 fine-grained quality difference 也能识别**——SkillLens 的 46.4% 来自细粒度对比，darwin-skill 在细粒度判别上仍有失效风险。**重要决策仍需人审。**

**复现边界**：本节仅记录实验摘要。若仓库没有同时提供原始 prompt、judge 输出、打分表和 commit 对照，本节数字只能作为作者内部验证线索，不能作为第三方可复现实证。

---

## HL 实战 high-leverage 案例（作者内部 results.tsv 摘要）

### HL-1：显性视觉标记是 dim4 的杠杆

**huashu-gpt-image Round 1**：红线 4 标题前加 🔴 CHECKPOINT + 「禁止交付」→「🛑 STOP」
- 改动：4 行
- dim4 变化：6.0 → 9.5（+3.5）
- 单维度 ROI：每行改动 +0.875 分

**huashu-slide-codex r4**：路径优先级章节插入 🔴🔴🔴 默认路径锁定铁律
- dim 总分 85 → 持平但避免了「Codex 自我合理化切 Path3 失败」实测翻车
- 视觉锚是 LLM 解析的关键信号

### HL-2：if-then 三段式 fallback 表

**huashu-gpt-image Round 1**：新增「🛟 失败模式与 fallback 树」章节
- 改动：3 张表 23 条三段式（触发条件 / 一线修复 / 仍失败兜底）
  - 单图失败 9 条
  - 批量生成 9 条
  - 生成执行层 5 条
- dim3 变化：6.5 → 10（满分）

**huashu-weread-advisor edit-r2**：SKILL 加 11 行全局异常表 + 4 行数据展示规范 + 4 工作流各加 5-6 行 workflow 特有异常表
- 共 ~33 个异常场景覆盖
- dim 总分 81.3 → 87.6（+6.3）

### HL-3：维度相关性（dim2/3/4 是相关簇）

**huashu-gpt-image 实测**：
- Round 1 攻 dim3（最低 6.5）→ 改成 10
- 同期 dim2 自动从 7.5 → 9（未单独优化）
- Round 2 试图单独攻 dim2 → 发现已触顶 9，多此一举
- **教训**：找最低维度时同时看相关簇短板

### HL-4：触顶后边际收益递减

**huashu-gpt-image Round 2**：+0.15 marginal
- Round 1: +10.7 分（基线 80.8 → 91.5）
- Round 2: +0.15 分（91.5 → 91.65）
- **触顶信号**：连续 2 轮 Δ < 2 → break，避免过度优化

**对比 darwin-skill 早期**：40 次记录 0 revert，部分是因为没有触顶规则，硬凑 MAX_ROUNDS=3 都 keep 了边际改动。

---

## 历史 results.tsv 优化记录摘要（截至 2026-05-27，未随仓库发布原始表）

完整记录未随当前仓库发布；下表仅为作者内部记录摘要。

| skill | 起分 | 终分 | Δ | 模式 |
|---|---|---|---|---|
| huashu-research | 40.0 | 73.2 | +33.2 | dry_run |
| huashu-video-check | 72.1 | 80.5 | +8.4 | dry_run |
| harness-optimizer | 78.4 | 86.0 | +7.6 | dry_run |
| freud-skill | 72.5 | 86.0 | +13.5 | dry_run |
| **claude-design** | **74.5** | **91.0** | **+16.5** | **full_test ✅** |
| huashu-design | 62.3 | 86.7 | +24.4 | dry_run |
| huashu-weread-advisor | 76.5 | 91.4 | +14.9 | full_test_informed ✅ |
| huashu-slide-codex | 82.6 | 85+ | +2~ | mixed |
| **huashu-gpt-image** | **80.8** | **91.65** | **+10.85** | **full_test ✅（v2 实战）** |
| **darwin-skill (self-fix)** | **86.05** | **92.05** | **+6.0** | **full_test ✅（自指闭环）** |

**统计**：
- 平均提升：~+13.5 分
- 全部 keep（v1 时代 0 revert 印证 rubric 偏松；v2 引入触顶 break 规则）
- full_test 比例：作者内部记录称从 33% 提升到 100%（最近 2 次都是 full_test）；因原始记录未随仓库发布，第三方审查时应降级采信。
