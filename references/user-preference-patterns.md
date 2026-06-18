# User Preference Adaptation Patterns for Darwin Skill

> 本文件记录 darwin-skill 在优化过程中遇到的用户偏好信号及适配模式。
> 当 darwin-skill 检测到以下信号时，自动应用对应适配，无需用户重复表达。

---

## 信号 1：直接执行偏好

**触发短语**：
- "不用再询问我"
- "直接执行"
- "不用逐步确认"
- "直接产出"
- "不要问我，直接做"

**适配行为**：
1. 跳过 Phase 1 基线评估后的 🔴 CHECKPOINT
2. Phase 2 每轮优化后展示 diff + 分数变化，不阻塞等待确认
3. Phase 3 汇总后直接输出最终报告
4. **保留的确认点**：仅 Phase 2.5 探索性重写前（stash/重写高风险操作）

**记忆键**：`user_pref_direct_execution = true`

---

## 信号 2：中文交流偏好

**触发短语**：
- "请用中文与我交流"
- "用中文"
- "中文回复"

**适配行为**：
1. 所有评估报告、评分卡、沟通语言切换为中文
2. 测试 prompt 设计使用中文场景
3. results.tsv 注释使用中文
4. SKILL.md 本身保持原文语言（不强制翻译）

**记忆键**：`user_pref_chinese = true`

---

## 信号 3：简洁列表格式

**触发短语**：
- "一行一个"
- "clean list"
- "不要 bullet points"
- "one per line"

**适配行为**：
1. 输出列表时采用纯文本 one-item-per-line
2. 不添加编号、bullet points 或额外评论
3. 评分卡表格保留（因表格是结构化数据），但文字说明部分遵循简洁格式

**记忆键**：`user_pref_clean_list = true`

---

## 信号 4：厌恶管理 overhead

**触发短语**：
- "厌恶管理 overhead"
- "不要流程"
- "低 overhead"
- "高效执行"

**适配行为**：
1. 减少检查点数量（仅在关键决策点保留）
2. 简化报告格式，去掉冗余的元数据展示
3. 优先执行 over 规划

**记忆键**：`user_pref_low_overhead = true`

---

## 组合信号处理

当多个信号同时触发时，按优先级应用：

1. **直接执行**（最高优先级）— 改变流程控制模式
2. **中文交流** — 改变输出语言
3. **简洁列表** — 改变格式风格
4. **低 overhead** — 减少检查点密度

这些偏好应在首次检测到后记录到 memory，后续 session 自动应用。
