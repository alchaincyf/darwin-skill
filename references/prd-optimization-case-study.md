# PRD-Writing Skill 优化案例研究

> 日期: 2026-06-01 | 优化者: Darwin Optimizer | 最终评分: 92.3/100

## 背景

用户要求"优化写PRD的skill"。初始评估发现现有 `software-development/writing-plans` skill（58分）本质是**代码实施计划**skill，不是**产品需求文档**skill。两者职责不同，强行改造会破坏原有功能。

## 关键决策：创建新skill vs 改造现有skill

### 决策框架

| 条件 | 改造现有skill | 创建新skill |
|------|-------------|------------|
| 现有skill职责与目标**部分重叠** | ✅ | ❌ |
| 现有skill职责与目标**完全不同** | ❌ | ✅ |
| 改造会**破坏现有功能** | ❌ | ✅ |
| 用户明确说"优化X"但X不存在 | — | ✅ 创建X |

### 本次决策

- `writing-plans` = 代码实施计划（Planning → TDD → Code Review → Debugging）
- 用户要的是 = 产品需求文档（需求分析 → 模块拆解 → PRD撰写 → UI Demo）
- **结论**: 创建新的 `prd-writing` skill，而非改造 `writing-plans`

## 优化过程

### 基线评估

| 维度 | 初始评分 | 主要问题 |
|------|---------|---------|
| dim1 Frontmatter | 9 | — |
| dim2 工作流 | 9 | Phase 3/4边界模糊 |
| dim3 失败模式 | 9 | 子agent失败fallback笼统 |
| dim4 检查点 | 9 | — |
| dim5 可执行性 | 9 | — |
| dim6 资源整合 | 7 | 无实际references/templates |
| dim7 架构 | 9 | — |
| dim8 实测 | 8.5 | Prompt 3匹配度中等 |
| dim9 反例 | 10 | — |
| **总分** | **87.9** | — |

### 优化轮次

| Round | 优化维度 | 改进内容 | Δ |
|-------|---------|---------|---|
| 1 | dim6 | 新增 `references/skill-usage-guide.md` | +0.8 |
| 2 | dim2/dim8 | Phase边界说明 + 不适用场景表 | +1.75 |
| 3 | dim3 | 子agent失败fallback细化 | +0.6 |
| 4 | dim6/dim5 | 新增 `templates/prd-module-template.md` | +1.25 |

### 触顶信号

Round 3 Δ=+0.6, Round 4 Δ=+1.25 → 连续两轮平均<2分 → **HL-4 break**

## 最终文件结构

```
prd-writing/
├── SKILL.md (423行)
├── references/
│   └── skill-usage-guide.md
└── templates/
    └── prd-module-template.md
```

## 经验总结

1. **职责不匹配时创建新skill**: 不要强行把"代码实施计划"改造成"PRD撰写"，两者是不同class
2. **新skill起点可以很高**: 基于实战工作流沉淀的skill，初始评分可达87.9，远高于改造旧skill
3. **dim6是新建skill的常见短板**: 容易忘记创建references/templates，导致资源整合度低
4. **模板文件是P1优化**: `prd-module-template.md` 让子agent输出统一化，显著提升可执行性
