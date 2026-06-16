# 项目追踪表

本文档追踪本次从现有仓库反推得到的需求、设计、模块、测试和执行计划。当前阶段不生成 wiki。

| 需求 | 验收标准 | 主要来源文件 |
| --- | --- | --- |
| URD-REQ-001 | URD-AC-001 | `SKILL.md`, `test-prompts.json` |
| URD-REQ-002 | URD-AC-001 | `SKILL.md` |
| URD-REQ-003 | URD-AC-002 | `SKILL.md` |
| URD-REQ-004 | URD-AC-003 | `SKILL.md`, `references/skilllens-evidence.md` |
| URD-REQ-005 | URD-AC-003, URD-AC-005 | `SKILL.md`, `references/skilllens-evidence.md` |
| URD-REQ-006 | URD-AC-004 | `references/runtime-neutrality.md` |
| URD-REQ-007 | URD-AC-005 | `SKILL.md` |
| URD-REQ-008 | URD-AC-005, URD-AC-006 | `SKILL.md` |
| URD-REQ-009 | URD-AC-006 | `SKILL.md` |
| URD-REQ-010 | URD-AC-001, URD-AC-005 | `SKILL.md` |
| URD-REQ-011 | URD-AC-007 | `SKILL.md` |
| URD-REQ-012 | URD-AC-008 | `SKILL.md`, `templates/`, `scripts/screenshot.mjs` |
| URD-REQ-013 | URD-AC-009 | `README.md`, `README_EN.md`, `docs/index.html` |
| URD-REQ-014 | URD-AC-009 | `README.md`, `references/skilllens-evidence.md`, `references/runtime-neutrality.md` |

## URD 到 ADD

| URD 需求 | ADD 功能需求 | ADD 设计参数 |
| --- | --- | --- |
| URD-REQ-001 | ADD-FR-002 | ADD-DP-002 |
| URD-REQ-002 | ADD-FR-001, ADD-FR-003 | ADD-DP-001, ADD-DP-003 |
| URD-REQ-003 | ADD-FR-005 | ADD-DP-005 |
| URD-REQ-004 | ADD-FR-004, ADD-FR-005 | ADD-DP-004, ADD-DP-005 |
| URD-REQ-005 | ADD-FR-004, ADD-FR-005 | ADD-DP-004, ADD-DP-005 |
| URD-REQ-006 | ADD-FR-006 | ADD-DP-006 |
| URD-REQ-007 | ADD-FR-007 | ADD-DP-007 |
| URD-REQ-008 | ADD-FR-008 | ADD-DP-008 |
| URD-REQ-009 | ADD-FR-008 | ADD-DP-008 |
| URD-REQ-010 | ADD-FR-001 | ADD-DP-001 |
| URD-REQ-011 | ADD-FR-008 | ADD-DP-008 |
| URD-REQ-012 | ADD-FR-009 | ADD-DP-009 |
| URD-REQ-013 | ADD-FR-009 | ADD-DP-009 |
| URD-REQ-014 | ADD-FR-009 | ADD-DP-009 |

## ADD 到 MDD

| ADD 设计参数 | MDD 模块 | MDD 接口 |
| --- | --- | --- |
| ADD-DP-001 | MDD-MOD-001 | MDD-API-001 |
| ADD-DP-002 | MDD-MOD-002 | MDD-API-002 |
| ADD-DP-003 | MDD-MOD-003 | MDD-API-003 |
| ADD-DP-004 | MDD-MOD-004 | MDD-API-004 |
| ADD-DP-005 | MDD-MOD-005 | MDD-API-005 |
| ADD-DP-006 | MDD-MOD-006 | MDD-API-006 |
| ADD-DP-007 | MDD-MOD-007 | MDD-API-007 |
| ADD-DP-008 | MDD-MOD-008 | MDD-API-008 |
| ADD-DP-009 | MDD-MOD-009 | MDD-API-009 |

## MDD 到 TDD

| MDD 接口 | TDD 测试 |
| --- | --- |
| MDD-API-001 | TDD-TEST-010 |
| MDD-API-002 | TDD-TEST-011 |
| MDD-API-003 | TDD-TEST-012 |
| MDD-API-004 | TDD-TEST-013 |
| MDD-API-005 | TDD-TEST-014 |
| MDD-API-006 | TDD-TEST-015 |
| MDD-API-007 | TDD-TEST-016 |
| MDD-API-008 | TDD-TEST-017 |
| MDD-API-009 | TDD-TEST-018 |

## TDD 到 RMD

| 测试范围 | RMD 任务 |
| --- | --- |
| TDD-TEST-001 到 TDD-TEST-009 | RMD-TASK-004 |
| TDD-TEST-010 到 TDD-TEST-018 | RMD-TASK-002 |
| TDD-TEST-019 到 TDD-TEST-025 | RMD-TASK-001, RMD-TASK-003 |
| TDD-DEFER-001 | RMD-TASK-002 |
| TDD-DEFER-002 | RMD-TASK-005 |
| TDD-DEFER-003 | RMD-TASK-002, RMD-TASK-003 |

## 文档状态

| 文件 | 状态 | 说明 |
| --- | --- | --- |
| `docs/URD.md` | 已创建 | 当前项目的用户需求文档。 |
| `docs/TRACE.md` | 已创建 | 追踪 URD 需求、验收标准和来源文件。 |
| `docs/CHANGELOG.md` | 已创建 | 记录 docs 变更。 |
| `docs/PARKING_LOT.md` | 已创建 | 记录暂不进入当前 URD 的事项。 |
| `.vibe/trace.json` | 已创建 | 机器可读追踪摘要。 |
| `docs/ADD.md` | 已创建 | 公理设计拆分，包含 FR、DP、设计矩阵和耦合调整记录。 |
| `.vibe/coupling_history.json` | 已创建 | 机器可读耦合调整记录。 |
| `docs/MDD.md` | 已创建 | 模块、接口、数据和契约设计。 |
| `docs/TDD.md` | 已创建 | 验收测试、接口契约测试和文档一致性检查。 |
| `docs/RMD.md` | 已创建 | 后续执行顺序、停止条件、回退点和检查清单。 |
| `.vibe/doc_state.json` | 已创建 | 文档状态记录，标注未生成 wiki。 |
| `.vibe/update_log.json` | 已创建 | 文档更新记录。 |

## 后续追踪

后续新增需求时，继续按以下关系追加：

```text
URD-REQ-NNN
  -> ADD-FR-NNN
  -> ADD-DP-NNN
  -> MDD-MOD-NNN
  -> MDD-API-NNN
  -> TDD-TEST-NNN
  -> RMD-TASK-NNN
```
