# darwin-skill 自指优化案例

> Session: 2026-06-03
> 优化对象：darwin-skill 自身
> 基线分数：76.9 → 最终分数：82.2（+5.3）
> 实验轮次：5 轮，保留 5 轮，回滚 0 次

## 背景

用户指令："用darwin技能优化自己"

解读：用 darwin-skill 的流程对 darwin-skill 自身进行自指优化（self-referential optimization）。

## 执行过程

### Phase 0: 初始化

- 发现 darwin-skill 目录已是 git 仓库（master 分支）
- 创建分支 `auto-optimize/20250603-darwin-self`
- 发现 `results.tsv` 已存在（来自 google-ads-strategist 优化记录）→ 直接追加

### Phase 0.5: 测试 Prompt 设计

为 darwin-skill 设计 3 个测试 prompt：

1. **全量优化**："优化所有skills" → 验证完整 Phase 0-3 流程
2. **单个评估**："帮我看看 huashu-slides 这个skill写得怎么样" → 验证 Phase 0.5-1 评估流程
3. **仅评估**："评估所有skills的质量，先不改" → 验证仅评估模式

### Phase 1: 基线评估

| 维度 | 分数 | 权重 | 得分 | 短板 |
|------|------|------|------|------|
| dim1 Frontmatter | 7 | 7 | 4.9 | description 信息过载（776字符，arXiv编号堆砌） |
| dim2 工作流清晰度 | 8 | 12 | 9.6 | 良好 |
| dim3 失败模式编码 | 8 | 12 | 9.6 | 良好 |
| dim4 检查点设计 | 7 | 6 | 4.2 | Phase 0.5 后无 CHECKPOINT |
| dim5 可执行具体性 | 8 | 17 | 13.6 | 测试 prompt 设计步骤模糊 |
| dim6 资源整合度 | 7 | 4 | 2.8 | references 内容指针不全 |
| dim7 整体架构 | 7 | 12 | 8.4 | 535行文档无导航 |
| dim8 实测表现 | 8 | 23 | 18.4 | 干跑验证 |
| dim9 反例黑名单 | 9 | 6 | 5.4 | 优秀 |

**结构分：58.5 / 效果分：18.4 / 总分：76.9**

### Phase 2: 优化循环

#### Round 1 · dim1 · e824060
- **改动**：压缩 frontmatter description（776→380字符），移除 arXiv 编号堆砌
- **新分**：78.3（+1.4）→ keep

#### Round 2 · dim6 · e081fbd
- **改动**：补全 references 内容指针（runtime-neutrality + prd-case-study）
- **新分**：78.7（+0.4）→ keep

#### Round 3 · dim7 · bb0c068
- **改动**：新增目录速查表，14 章节 + 「何时查看」标注
- **新分**：79.9（+1.2）→ keep

#### Round 4 · dim4 · 6aa07f8
- **改动**：Phase 0.5 后新增显性 CHECKPOINT
- **新分**：80.5（+0.6）→ keep

#### Round 5 · dim5 · 3170d5d
- **改动**：测试 prompt 设计步骤具体化（提取方法 + expected 格式 + 边界场景）
- **新分**：82.2（+1.7）→ keep

#### 触顶判断
- Round 4 Δ=+0.6，Round 5 Δ=+1.7
- 连续两轮 Δ < 2 分 → **触顶信号**，停止 hill-climbing

### Phase 3: 汇总

生成成果卡片 HTML（`/workspace/darwin-skill-result-card.html`），因环境无 Playwright/chromium，降级为纯 HTML 交付。

## 关键发现

### 1. 自指优化的可行性

同一 skill 指导自身优化是可行的，但需注意：
- dim8（实测表现）只能用干跑验证，无法 spawn 独立子 agent 做「带 skill vs 不带 skill」对比（因为 skill 本身就在指导执行）
- 评分偏差风险：主 agent 对自指优化有天然乐观倾向，需更严格地应用 ratchet 机制

### 2. 环境依赖陷阱

本次 session 踩中 3 个环境依赖：

| 问题 | 表现 | 解决 |
|------|------|------|
| git identity 未配置 | `git commit` 失败 | 现场配置 `user.email` + `user.name` |
| Playwright 未安装 | 截图失败 | 降级为纯 HTML 成果卡片 |
| results.tsv 已存在 | 文件非空，需追加而非新建 | 读取现有内容，追加新行 |

### 3. 触顶信号验证

HL-4「连续 2 轮 Δ < 2 分 → break」在本 session 得到验证：
- Round 4 后结构维度最低已升至 8 分
- Round 5 虽仍有 +1.7 收益，但边际递减明显
- 若继续 Round 6，可能进入 over-engineering（如过度拆分章节、增加冗余说明）

## 可复用模式

### 测试 Prompt 设计模板（darwin-skill 专用）

```json
[
  {"id": 1, "prompt": "优化所有skills", "expected": "完整 Phase 0-3 流程"},
  {"id": 2, "prompt": "帮我看看 XX 这个skill写得怎么样", "expected": "Phase 0.5-1 评估流程"},
  {"id": 3, "prompt": "评估所有skills的质量，先不改", "expected": "仅评估模式"}
]
```

### 自指优化 checklist

- [ ] 确认 git 仓库状态（`git status`）
- [ ] 配置 git identity（如未配置）
- [ ] 检查 results.tsv 是否存在（追加 vs 新建）
- [ ] dim8 强制标注 `dry_run`（自指无法 full_test）
- [ ] 触顶信号严格应用（连续 2 轮 Δ < 2 分即停）
- [ ] 成果卡片截图失败时降级 HTML

## 关联文件

- 优化分支：`auto-optimize/20250603-darwin-self`
- 测试 prompt：`../test-prompts.json`
- 成果卡片：`/workspace/darwin-skill-result-card.html`
