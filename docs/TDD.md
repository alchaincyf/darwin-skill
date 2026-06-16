# Darwin Skill 2.0 测试计划文档

本文档定义如何验证 `docs/URD.md`、`docs/ADD.md` 和 `docs/MDD.md` 中的要求。当前阶段以文档一致性、接口契约和现有资源检查为主，不要求已经存在完整实现代码。

## 1. 测试范围

| ID | 范围 |
| --- | --- |
| TDD-SCOPE-001 | 检查 URD、ADD、MDD、TDD、RMD 和 `.vibe` 追踪文件是否一致。 |
| TDD-SCOPE-002 | 检查 `SKILL.md` 中定义的 rubric、流程、异常处理和反例黑名单是否能映射到文档需求。 |
| TDD-SCOPE-003 | 检查 `test-prompts.json` 的结构和数量是否满足效果验证前提。 |
| TDD-SCOPE-004 | 检查 runtime 中立性扫描命令能发现红灯模式。 |
| TDD-SCOPE-005 | 检查成果卡片模板和截图脚本的输入输出约束。 |

## 2. 验收标准映射

| 测试 ID | 对应验收标准 | 验证方式 | 判定标准 |
| --- | --- | --- | --- |
| TDD-TEST-001 | URD-AC-001 | 文档检查 | `SKILL.md` 和 MDD 中存在目标识别、git 状态、prompt 准备、评分前确认的流程或接口。 |
| TDD-TEST-002 | URD-AC-002 | 文档检查 | rubric 明确 9 个维度、权重、总分算法和短板输出。 |
| TDD-TEST-003 | URD-AC-003 | 数据检查 | 效果验证输出必须包含 `full_test` 或 `dry_run`；干跑风险有说明。 |
| TDD-TEST-004 | URD-AC-004 | 命令检查 | runtime 红灯扫描命令存在，并能对给定文本返回文件和行号。 |
| TDD-TEST-005 | URD-AC-005 | 文档检查 | 优化计划必须包含目标维度、改动摘要、预期影响、实际分数变化和保留或回滚决定。 |
| TDD-TEST-006 | URD-AC-006 | 契约检查 | `decide_and_record` 明确新分不高于旧分时不能保留。 |
| TDD-TEST-007 | URD-AC-007 | 数据检查 | `results.tsv` 字段顺序与 MDD 中 `HistoryRecord` 一致。 |
| TDD-TEST-008 | URD-AC-008 | 文件检查 | `templates/result-card*.html` 和 `scripts/screenshot.mjs` 存在。 |
| TDD-TEST-009 | URD-AC-009 | 文档一致性检查 | README、发布页、引用资料和 `SKILL.md` 对 v2.0 的核心说明不冲突。 |

## 3. 接口契约测试

| 测试 ID | 接口 | 输入 | 预期结果 |
| --- | --- | --- | --- |
| TDD-TEST-010 | MDD-API-001 `request_checkpoint` | 缺少 `artifacts` 的检查点请求 | 返回错误，不允许继续。 |
| TDD-TEST-011 | MDD-API-002 `resolve_targets` | 指定不存在的 skill 名称 | 返回明确错误，不创建目标。 |
| TDD-TEST-012 | MDD-API-003 `prepare_prompt_set` | 只有 1 个 prompt 的集合 | 返回不合格状态，要求补足到 2 到 3 个。 |
| TDD-TEST-013 | MDD-API-004 `run_effect_validation` | 未确认的 `PromptSet` | 拒绝执行验证。 |
| TDD-TEST-014 | MDD-API-005 `score_skill` | 8 个维度或 10 个维度的 rubric | 返回错误，要求 9 个维度。 |
| TDD-TEST-015 | MDD-API-006 `scan_runtime_neutrality` | 包含“Claude Code skill”的测试文本 | 返回 1 条红灯命中，包含行号和建议修复方向。 |
| TDD-TEST-016 | MDD-API-007 `plan_single_dimension_change` | 同时要求修改多个无关维度 | 返回错误或要求重写计划。 |
| TDD-TEST-017 | MDD-API-008 `decide_and_record` | 新分等于旧分 | 输出 `stop` 或 `revert`，不得输出 `keep`。 |
| TDD-TEST-018 | MDD-API-009 `create_card_and_check_public_docs` | 缺少模板文件 | 记录失败原因，不生成伪造输出路径。 |

## 4. 文档一致性测试

| 测试 ID | 检查项 | 判定标准 |
| --- | --- | --- |
| TDD-TEST-019 | URD 到 ADD | 每个 `URD-REQ` 至少映射到一个 `ADD-FR` 或明确暂缓。 |
| TDD-TEST-020 | ADD 到 MDD | 每个 `ADD-DP` 至少映射到一个 `MDD-MOD`。 |
| TDD-TEST-021 | MDD 到 TDD | 每个 `MDD-API` 至少有一个契约测试。 |
| TDD-TEST-022 | `.vibe/trace.json` | JSON 可解析，且列出 URD、ADD、MDD、TDD、RMD 文档路径。 |
| TDD-TEST-023 | `.vibe/coupling_history.json` | JSON 可解析，且最终状态为 `decoupled_lower_triangular`。 |
| TDD-TEST-024 | 未完成标记检查 | 新增文档不得包含未处理的占位标记。 |
| TDD-TEST-025 | 项目用词检查 | 新增文档不得包含项目指令中禁止的空泛表达。 |

## 5. 建议命令

使用以下命令运行项目文档检查：

```powershell
python scripts\check_project_docs.py
```

该脚本覆盖 JSON 解析、追踪关系、测试 prompt、runtime 中立性、成果卡片资源、文档用词和 wiki 缺失检查。

## 6. 暂不执行的测试

| ID | 测试 | 暂不执行原因 |
| --- | --- | --- |
| TDD-DEFER-001 | 独立评审 agent 的真实效果对比测试 | 当前任务是完善文档，没有启动子 agent 做真实优化。 |
| TDD-DEFER-002 | 成果卡片真实截图测试 | 当前任务不要求生成新卡片；截图依赖 Node.js 和 Playwright 环境。 |
| TDD-DEFER-003 | git commit、git revert 的真实操作测试 | 当前只写文档，不进行优化实验。 |
