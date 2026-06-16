# Darwin Skill 2.0 执行计划文档

本文档给出后续实现或维护文档时的安全顺序。当前用户要求是不生成 wiki，因此所有任务都只更新 `docs/`、`.vibe/`、根目录说明文件和现有资源。

## 1. 执行原则

| ID | 原则 |
| --- | --- |
| RMD-RULE-001 | 每个任务只修改一个清楚的职责范围。 |
| RMD-RULE-002 | 先补接口和测试计划，再改 `SKILL.md` 或脚本。 |
| RMD-RULE-003 | 每个任务结束前检查 JSON、占位词、禁用词和 git 状态。 |
| RMD-RULE-004 | 涉及提交、回滚、推送或合并时必须明确检查点。 |
| RMD-RULE-005 | 本轮不创建 wiki 文件。 |

## 2. 任务顺序

| ID | 任务 | 输入 | 输出 | 检查命令 | Git 检查点 |
| --- | --- | --- | --- | --- | --- |
| RMD-TASK-001 | 建立文档追踪状态 | URD、ADD、MDD、TDD、RMD | `.vibe/trace.json`, `.vibe/doc_state.json`, `.vibe/update_log.json` | `Get-Content .vibe\trace.json \| ConvertFrom-Json \| Out-Null` | `RMD-GIT-001` 本地提交，PR 状态按远程情况决定 |
| RMD-TASK-002 | 将 MDD 契约转成实现骨架或脚本检查项 | `docs/MDD.md`, `docs/TDD.md` | `scripts/check_project_docs.py` | `python scripts\check_project_docs.py` | `RMD-GIT-002` 单独提交 |
| RMD-TASK-003 | 实现文档一致性检查 | `docs/TDD.md` | `scripts/check_project_docs.py` | `python scripts\check_project_docs.py` | `RMD-GIT-003` 单独提交 |
| RMD-TASK-004 | 检查并修订 `SKILL.md` 与 README 的一致性 | `SKILL.md`, README, docs | 已移除公开安装说明中的单 runtime 路径 | `python scripts\check_project_docs.py` | `RMD-GIT-004` 单独提交 |
| RMD-TASK-005 | 验证成果卡片生成流程 | templates, `scripts/screenshot.mjs` | 成功截图或失败原因记录 | Node/Playwright 命令，按环境补充 | `RMD-GIT-005` 单独提交 |

## 3. 当前文档完善任务

| ID | 状态 | 说明 |
| --- | --- | --- |
| RMD-TASK-DOC-001 | 已完成 | 根据当前项目内容创建 URD。 |
| RMD-TASK-DOC-002 | 已完成 | 根据 URD 创建 ADD，并形成下三角矩阵。 |
| RMD-TASK-DOC-003 | 已完成 | 根据 ADD 创建 MDD，定义模块、接口、数据和契约。 |
| RMD-TASK-DOC-004 | 已完成 | 根据 URD/ADD/MDD 创建 TDD，定义验收测试和契约测试。 |
| RMD-TASK-DOC-005 | 已完成 | 创建本 RMD，给出后续维护顺序和检查点。 |
| RMD-TASK-IMPL-001 | 已完成 | 新增 `scripts/check_project_docs.py`，落实 TDD 文档检查。 |
| RMD-TASK-IMPL-002 | 已完成 | 修订 README、README_EN 和 `SKILL.md` 中的 runtime 路径表达。 |

## 4. 停止条件

| ID | 条件 | 处理 |
| --- | --- | --- |
| RMD-STOP-001 | URD 中的待确认问题影响当前任务判断。 | 记录到 `docs/PARKING_LOT.md` 或对应文档，不编造答案。 |
| RMD-STOP-002 | ADD 矩阵出现新的右上区域依赖。 | 暂停实现，先更新 `docs/ADD.md` 和 `.vibe/coupling_history.json`。 |
| RMD-STOP-003 | MDD 接口缺少输入、输出或副作用说明。 | 先补 MDD，再写测试或代码。 |
| RMD-STOP-004 | TDD 缺少可判定结果。 | 先补测试判定标准。 |
| RMD-STOP-005 | 需要执行高风险 git 操作或远程操作。 | 明确向用户说明并等待确认。 |

## 5. 回退点

| ID | 位置 | 回退方式 |
| --- | --- | --- |
| RMD-ROLLBACK-001 | 文档文件写入后 | 用 git diff 审查，必要时用反向补丁恢复相关文档。 |
| RMD-ROLLBACK-002 | 脚本实现后 | 保留上一版本，通过普通 commit 或 revert commit 记录恢复。 |
| RMD-ROLLBACK-003 | 成果卡片生成后 | 删除本次生成产物前先确认产物路径，避免误删用户文件。 |

## 6. 本地检查清单

| ID | 检查 |
| --- | --- |
| RMD-CHECK-001 | `python scripts\check_project_docs.py` 通过。 |
| RMD-CHECK-002 | `.vibe/trace.json`、`.vibe/coupling_history.json`、`.vibe/doc_state.json` 和 `.vibe/update_log.json` 能解析。 |
| RMD-CHECK-003 | TRACE 中存在 URD → ADD → MDD → TDD → RMD 的追踪关系。 |
| RMD-CHECK-004 | 未创建 wiki 文件。 |
| RMD-CHECK-005 | `git status --short` 只显示预期文档、脚本和说明文件变更。 |
