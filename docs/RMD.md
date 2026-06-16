# Darwin Skill 2.0 执行计划文档

本文档给出后续实现或维护文档时的安全顺序。当前用户要求是不生成 wiki，因此所有任务都只更新 `docs/`、`.vibe/`、根目录说明文件、脚本和现有资源。

## 1. 执行原则

| ID | 原则 |
| --- | --- |
| RMD-RULE-001 | 每个任务只修改一个清楚的职责范围。 |
| RMD-RULE-002 | 先补接口和测试计划，再改 `SKILL.md` 或脚本。 |
| RMD-RULE-003 | 先实现只读检查和数据结构，再实现会写文件或执行 git 的动作。 |
| RMD-RULE-004 | 每个任务结束前检查 JSON、文档标记、禁用词和 git 状态。 |
| RMD-RULE-005 | 涉及提交、回滚、推送或合并时必须明确检查点。 |
| RMD-RULE-006 | 本轮不创建 wiki 文件。 |

## 2. 任务顺序

| ID | 任务 | 输入 | 输出 | 检查命令 | Git 检查点 |
| --- | --- | --- | --- | --- | --- |
| RMD-TASK-001 | 建立文档追踪状态 | URD、ADD、MDD、TDD、RMD | `.vibe/trace.json`, `.vibe/doc_state.json`, `.vibe/update_log.json` | `python scripts\check_project_docs.py` | `RMD-GIT-001` 本地提交，PR 状态按远程情况决定 |
| RMD-TASK-002 | 实现领域研究记录能力 | MDD-API-003, TDD-TEST-034 | `domain-research.md`, `domain-research-meta.json` 生成规则 | `python scripts\check_project_docs.py` | `RMD-GIT-002` 单独提交 |
| RMD-TASK-003 | 实现研究驱动的领域评分标准和领域 prompt | MDD-API-004, MDD-API-005, TDD-TEST-035, TDD-TEST-036 | `domain-rubric.md`, `domain-rubric-meta.json`, `domain-test-prompts.json` 规则 | `python scripts\check_project_docs.py` | `RMD-GIT-003` 单独提交 |
| RMD-TASK-004 | 实现领域评分标准质量评估和冻结门槛 | MDD-API-006, MDD-API-007, TDD-TEST-037, TDD-TEST-038 | `domain-rubric-evaluation.md`, `domain-rubric-evaluation.json`, 冻结规则 | `python scripts\check_project_docs.py` | `RMD-GIT-004` 单独提交 |
| RMD-TASK-005 | 实现公共评分、领域评分和综合决策扩展 | MDD-API-008 到 MDD-API-013, TDD-TEST-039 到 TDD-TEST-044 | `common_score`, `domain_score`, `composite_score`, hard gate 决策和兼容记录 | `python scripts\check_project_docs.py` | `RMD-GIT-005` 单独提交 |
| RMD-TASK-006 | 实现报告、成果卡片和公开说明检查扩展 | MDD-API-014, TDD-TEST-045 | 包含 Domain Research 和 Domain Rubric Quality 的报告 | `python scripts\check_project_docs.py` | `RMD-GIT-006` 单独提交 |
| RMD-TASK-007 | 扩展项目文档检查脚本 | TDD-TEST-046 到 TDD-TEST-055 | `scripts/check_project_docs.py` 覆盖 14 个 ADD-DP、14 个 MDD-API 和新增追踪 | `python scripts\check_project_docs.py` | `RMD-GIT-007` 单独提交 |
| RMD-TASK-008 | 检查并修订 `SKILL.md` 与 README 的一致性 | `SKILL.md`, README, docs | 公开说明与新增领域研究、质量评估流程一致 | `python scripts\check_project_docs.py` | `RMD-GIT-008` 单独提交 |
| RMD-TASK-009 | 验证成果卡片生成流程 | templates, `scripts/screenshot.mjs` | 成功截图或失败原因记录 | Node/Playwright 命令，按环境补充 | `RMD-GIT-009` 单独提交 |

## 3. 当前文档完善任务

| ID | 状态 | 说明 |
| --- | --- | --- |
| RMD-TASK-DOC-001 | 已完成 | 根据当前项目内容创建 URD。 |
| RMD-TASK-DOC-002 | 已完成 | 根据 URD 创建 ADD，并形成下三角矩阵。 |
| RMD-TASK-DOC-003 | 已完成 | 根据 ADD 创建 MDD，定义模块、接口、数据和契约。 |
| RMD-TASK-DOC-004 | 已完成 | 根据 URD/ADD/MDD 创建 TDD，定义验收测试和契约测试。 |
| RMD-TASK-DOC-005 | 已完成 | 创建本 RMD，给出后续维护顺序和检查点。 |
| RMD-TASK-DOC-006 | 已完成 | 根据领域研究与评分标准质量评估新增需求，刷新 MDD、TDD、RMD 和追踪关系。 |
| RMD-TASK-IMPL-001 | 已完成 | 新增 `scripts/check_project_docs.py`，落实 TDD 文档检查。 |
| RMD-TASK-IMPL-002 | 已完成 | 修订 README、README_EN 和 `SKILL.md` 中的 runtime 路径表达。 |

## 4. 停止条件

| ID | 条件 | 处理 |
| --- | --- | --- |
| RMD-STOP-001 | URD 中的待确认问题影响当前任务判断。 | 记录到 `docs/PARKING_LOT.md` 或对应文档，不编造答案。 |
| RMD-STOP-002 | ADD 矩阵出现新的右上区域依赖。 | 暂停实现，先更新 `docs/ADD.md` 和 `.vibe/coupling_history.json`。 |
| RMD-STOP-003 | MDD 接口缺少输入、输出、前置条件、后置条件、不变量或副作用说明。 | 先补 MDD，再写测试或代码。 |
| RMD-STOP-004 | TDD 缺少可判定结果。 | 先补测试判定标准。 |
| RMD-STOP-005 | 研究来源无法确认真实性。 | 降低置信度，记录证据空白，并要求用户确认。 |
| RMD-STOP-006 | 领域评分标准质量评估结论为 `reject`，或关键维度低于最低分。 | 不进入正式优化流程，先修订并重新评估。 |
| RMD-STOP-007 | 用户修改领域评分标准但未重新运行质量评估。 | 拒绝冻结或评分，重新执行质量评估。 |
| RMD-STOP-008 | 需要执行高风险 git 操作或远程操作。 | 明确向用户说明并等待确认。 |

## 5. 回退点

| ID | 位置 | 回退方式 |
| --- | --- | --- |
| RMD-ROLLBACK-001 | 文档文件写入后 | 用 git diff 审查，必要时用反向补丁恢复相关文档。 |
| RMD-ROLLBACK-002 | 脚本实现后 | 保留上一版本，通过普通 commit 或 revert commit 记录恢复。 |
| RMD-ROLLBACK-003 | 领域研究或领域评分标准生成后 | 保留旧版本文件，不覆盖冻结版本；必要时生成新版本号。 |
| RMD-ROLLBACK-004 | 质量评估后 | 不修改已评估的评分标准；用新评估版本记录重新评估结果。 |
| RMD-ROLLBACK-005 | 成果卡片生成后 | 删除本次生成产物前先确认产物路径，避免误删用户文件。 |

## 6. 本地检查清单

| ID | 检查 |
| --- | --- |
| RMD-CHECK-001 | `python scripts\check_project_docs.py` 通过。 |
| RMD-CHECK-002 | `.vibe/trace.json`、`.vibe/coupling_history.json`、`.vibe/doc_state.json` 和 `.vibe/update_log.json` 能解析。 |
| RMD-CHECK-003 | TRACE 中存在 URD → ADD → MDD → TDD → RMD 的追踪关系。 |
| RMD-CHECK-004 | 未创建 wiki 文件。 |
| RMD-CHECK-005 | ADD 矩阵右上区域没有直接依赖。 |
| RMD-CHECK-006 | MDD 中 14 个模块、14 个接口和 14 个 ADD-DP 一一对应。 |
| RMD-CHECK-007 | TDD 中 14 个 MDD-API 都有契约测试。 |
| RMD-CHECK-008 | `git status --short` 只显示预期文档、脚本和说明文件变更。 |
