# 优化整合指南

本文档说明如何使用 `results.tsv` 中的优化记录进行后续整合和持续优化。

## 数据概览

`results.tsv` 包含 1297 条优化记录，涵盖 15 个 skill 的基线评估和优化过程。

### 评估的 Skills

| Skill | 基线分数 | 主要问题 |
|-------|---------|---------|
| astryx | 62 | dim2_no_workflow, dim4_no_checkpoint |
| auto-learning | 40 | dim1_missing_name, dim3_no_failure_mode |
| autocli-skill | 83 | dim7_too_long |
| autoresearch | 62 | dim3_no_failure_mode, dim4_no_checkpoint |
| cybersecurity-expert | 41 | dim2_no_workflow, dim3_no_failure_mode |
| darwin-skill | 88 | (无主要问题) |
| knowledge-bridge | 26 | dim1_missing_name, dim2_no_workflow |
| openspec | 41 | dim2_no_workflow, dim3_no_failure_mode |
| plan-review-gate | 62 | dim3_no_failure_mode, dim4_no_checkpoint |
| planning-with-files | 74 | dim4_no_checkpoint |
| playwright-connect-existing | 62 | dim3_no_failure_mode, dim4_no_checkpoint |
| project-analysis | 68 | dim1_missing_name, dim4_no_checkpoint |
| siriusec-dev | 48 | dim2_no_workflow, dim3_no_failure_mode |
| viral-content | 65 | dim3_no_failure_mode, dim6_no_resources |
| web-access | 88 | (无主要问题) |

### 常见问题维度

根据基线评估，最常见的问题维度：

1. **dim3 (失败模式编码)** - 13/15 skills 缺少显式失败处理
2. **dim4 (检查点设计)** - 12/15 skills 缺少用户确认检查点
3. **dim6 (资源整合度)** - 10/15 skills 引用路径不可达
4. **dim9 (反例与黑名单)** - 9/15 skills 缺少"不要做什么"的反例

## 后续优化策略

### 优先级排序

基于基线分数，建议按以下顺序优化：

1. **knowledge-bridge (26分)** - 最低分，需要全面重构
2. **auto-learning (40分)** - 缺少核心元数据
3. **cybersecurity-expert (41分)** - 缺少工作流和失败处理
4. **openspec (41分)** - 缺少工作流和失败处理
5. **siriusec-dev (48分)** - 缺少工作流和失败处理

### 通用优化模式

根据 results.tsv 中的优化记录，以下模式在多个 skill 中有效：

#### 模式 1: 添加显式失败处理 (dim3)

```markdown
## 异常处理

| 场景 | 触发条件 | 处理动作 |
|------|---------|---------|
| 配置缺失 | 配置文件不存在 | 使用默认配置并提示用户 |
| API 失败 | 网络请求超时 | 重试 3 次，仍失败则回退到本地缓存 |
| 权限不足 | 访问被拒绝 | 提示用户检查权限，提供修复命令 |
```

#### 模式 2: 添加检查点 (dim4)

```markdown
### 🔴 CHECKPOINT · 🛑 STOP

在执行关键操作前暂停，等待用户确认：
- 展示将要执行的操作
- 列出可能的影响
- 等待用户输入 "确认" 或 "取消"
```

#### 模式 3: 添加反例黑名单 (dim9)

```markdown
## 反例黑名单

| # | 不要做 | 为什么 | 替代做法 |
|---|-------|-------|---------|
| 1 | 不要静默失败 | 用户无法知道发生了什么 | 显式报告错误并提供修复建议 |
| 2 | 不要跳过验证 | 可能导致数据损坏 | 每步操作后验证结果 |
```

## 整合工作流

### 步骤 1: 加载历史数据

```bash
# 读取 results.tsv
cat results.tsv | head -20

# 统计各维度的问题频率
awk -F'\t' 'NR>1 {print $7}' results.tsv | sort | uniq -c | sort -rn
```

### 步骤 2: 选择目标 skill

```bash
# 找到分数最低的 skill
awk -F'\t' '$1 ~ /baseline/ && $4 == "-" {print $3, $5}' results.tsv | sort -k2 -n | head -5
```

### 步骤 3: 应用优化

使用 darwin-skill 的 Phase 2 优化循环：

```
用户: "优化 knowledge-bridge"

→ Phase 0.5: 设计测试 prompt
→ Phase 1: 基线评估（已存在于 results.tsv）
→ Phase 2: 优化循环（最多 3 轮）
→ Phase 3: 汇总报告
```

### 步骤 4: 记录新结果

每次优化后追加到 results.tsv：

```tsv
2026-07-20T10:00	abc1234	knowledge-bridge	26	45	keep	dim3_failure_mode	添加异常处理表	full_test
```

## 持续优化建议

### 短期（1-2 周）

1. 优化分数最低的 5 个 skill（knowledge-bridge, auto-learning, cybersecurity-expert, openspec, siriusec-dev）
2. 重点关注 dim3（失败模式）和 dim4（检查点）
3. 为每个 skill 设计 2-3 个测试 prompt

### 中期（1 个月）

1. 对所有 skill 进行第二轮优化
2. 收集 full_test 数据（减少 dry_run 比例）
3. 分析优化模式，提炼通用模板

### 长期（2-3 个月）

1. 建立 skill 质量基准（目标：所有 skill ≥ 70 分）
2. 自动化优化流程（使用 darwin-skill 的自主优化循环）
3. 定期回顾 results.tsv，识别新的优化模式

## 数据分析示例

### 统计各维度的改进效果

```bash
# 统计 dim3 相关的优化记录
grep "dim3" results.tsv | wc -l

# 统计成功率
awk -F'\t' '$6 == "keep" {keep++} $6 == "revert" {revert++} END {print "Keep:", keep, "Revert:", revert, "Success rate:", keep/(keep+revert)*100 "%"}' results.tsv
```

### 识别最有效的优化策略

```bash
# 找出分数提升最大的优化
awk -F'\t' 'NR>1 && $4 != "-" && $5 != "-" {delta=$5-$4; if(delta>0) print $3, delta, $7}' results.tsv | sort -k2 -rn | head -10
```

## 参考资源

- [SKILL.md](../SKILL.md) - darwin-skill 完整工作流
- [references/skilllens-evidence.md](../references/skilllens-evidence.md) - 学术依据
- [results.tsv](../results.tsv) - 完整优化记录

---

**最后更新**: 2026-07-20  
**数据来源**: 本地 darwin-skill 优化记录（1297 条）
