# Darwin Skill 2.0 测试计划文档

本文档定义如何验证 `docs/URD.md`、`docs/ADD.md` 和 `docs/MDD.md` 中的要求。当前阶段以文档一致性、接口契约和现有资源检查为主，不要求已经存在完整实现代码。

## 1. 测试范围

| ID | 范围 |
| --- | --- |
| TDD-SCOPE-001 | 检查 URD、ADD、MDD、TDD、RMD 和 `.vibe` 追踪文件是否一致。 |
| TDD-SCOPE-002 | 检查 `SKILL.md` 中定义的 rubric、流程、异常处理和反例黑名单是否能映射到文档需求。 |
| TDD-SCOPE-003 | 检查公共测试 prompt 和领域测试 prompt 的结构、数量、目的和维度匹配。 |
| TDD-SCOPE-004 | 检查领域研究文件、研究元数据、领域评分标准、质量评估文件和冻结元数据。 |
| TDD-SCOPE-005 | 检查 runtime 中立性扫描命令能发现红灯模式。 |
| TDD-SCOPE-006 | 检查成果卡片模板、截图脚本、报告内容和公开文档一致性。 |

## 2. 验收标准映射

| 测试 ID | 对应验收标准 | 验证方式 | 判定标准 |
| --- | --- | --- | --- |
| TDD-TEST-001 | URD-AC-001 | 文档检查 | `SKILL.md` 和 MDD 中存在目标识别、git 状态、prompt 准备、评分前确认的流程或接口。 |
| TDD-TEST-002 | URD-AC-002 | 文档检查 | 公共 rubric 明确 9 个维度、权重、总分算法和短板输出。 |
| TDD-TEST-003 | URD-AC-003 | 数据检查 | 效果验证输出必须包含 `full_test` 或 `dry_run`；干跑风险有说明。 |
| TDD-TEST-004 | URD-AC-004 | 命令检查 | runtime 红灯扫描命令存在，并能对给定文本返回文件和行号。 |
| TDD-TEST-005 | URD-AC-005 | 文档检查 | 优化计划必须包含目标维度、改动摘要、预期影响、实际分数变化和保留或回滚决定。 |
| TDD-TEST-006 | URD-AC-006 | 契约检查 | `decide_and_record` 明确新分不高于旧分时不能保留。 |
| TDD-TEST-007 | URD-AC-007 | 数据检查 | `results.tsv` 字段顺序与兼容的 `HistoryRecord` 一致。 |
| TDD-TEST-008 | URD-AC-008 | 文件检查 | `templates/result-card*.html` 和 `scripts/screenshot.mjs` 存在。 |
| TDD-TEST-009 | URD-AC-009 | 文档一致性检查 | README、发布页、引用资料和 `SKILL.md` 对 v2.0 的核心说明不冲突。 |
| TDD-TEST-010 | URD-AC-010 | 契约检查 | 任务目标明确时能生成 `domain-rubric.md`、`domain-test-prompts.json` 和 `domain-rubric-meta.json`。 |
| TDD-TEST-011 | URD-AC-011 | 数据检查 | 领域维度权重合计 100，每个维度有 1、5、10 分锚点、失败情况和检查证据。 |
| TDD-TEST-012 | URD-AC-012 | 负向检查 | 目标任务不清楚时生成 `generic_task_rubric`，并要求用户确认。 |
| TDD-TEST-013 | URD-AC-013 | 负向检查 | 不存在固定具体领域维度列表，也不存在按领域名称直接套用固定 rubric 的逻辑。 |
| TDD-TEST-014 | URD-AC-014 | 报告检查 | 每轮评估报告分别展示公共评分、领域评分、综合评分、领域名称、领域评分版本和 hard gates 状态。 |
| TDD-TEST-015 | URD-AC-015 | 决策检查 | 公共评分上升但领域评分下降时默认不保留修改，并说明原因。 |
| TDD-TEST-016 | URD-AC-016 | 决策检查 | 综合评分上升但触发 hard gate 时默认不保留修改，并说明 hard gate 原因。 |
| TDD-TEST-017 | URD-AC-017 | 状态检查 | 领域评分标准冻结后，优化循环自动改写该文件时被拒绝并记录原因。 |
| TDD-TEST-018 | URD-AC-018 | 兼容检查 | 旧项目没有 `domain-rubric.md` 时，公共评分流程不报错、不强制生成领域评分。 |
| TDD-TEST-019 | URD-AC-019 | 数据检查 | 新版结果记录包含公共评分、领域评分、综合评分、领域名称、领域评分版本、hard gate 状态和原因；旧记录可读取。 |
| TDD-TEST-020 | URD-AC-020 | 顺序检查 | 进入领域评分流程时，先生成领域研究文件和研究元数据，再生成领域评分标准。 |
| TDD-TEST-021 | URD-AC-021 | 路径选择检查 | 不同系统能力下，研究路径选择符合 URD 中定义的优先级。 |
| TDD-TEST-022 | URD-AC-022 | 元数据检查 | 研究元数据包含方法、来源、置信度和证据空白，且没有伪造外部来源。 |
| TDD-TEST-023 | URD-AC-023 | 追踪检查 | 领域评分维度能追溯到研究发现、任务目标、用户资料或失败风险；低置信度会传递。 |
| TDD-TEST-024 | URD-AC-024 | 文件检查 | 每次冻结领域评分标准前生成质量评估 Markdown 和 JSON 文件。 |
| TDD-TEST-025 | URD-AC-025 | 质量评分检查 | 质量评估包含 RQ1 到 RQ9 的维度分、总分和允许结论。 |
| TDD-TEST-026 | URD-AC-026 | 阻断检查 | 低于质量门槛、关键维度低于最低分或发现模板污染时阻止进入正式优化流程。 |
| TDD-TEST-027 | URD-AC-027 | 低置信度检查 | 只依赖模型已有知识或一般推断时置信度不得为 high，且必须要求用户确认。 |
| TDD-TEST-028 | URD-AC-028 | 展示检查 | Phase 0.35 展示领域评分、领域研究、质量评估和领域测试 prompt，并记录用户选择。 |
| TDD-TEST-029 | URD-AC-029 | 变更触发检查 | 用户修改领域评分标准后重新运行质量评估；研究依据变化后重新生成并重新评估。 |
| TDD-TEST-030 | URD-AC-030 | 元数据检查 | `domain-rubric-meta.json` 包含研究版本、质量分、质量结论、质量评估版本、研究置信度、确认要求和冻结状态。 |
| TDD-TEST-031 | URD-AC-031 | 报告检查 | 优化报告包含 Domain Research 和 Domain Rubric Quality；强制使用低质量评分标准时标记风险。 |

## 3. 接口契约测试

| 测试 ID | 接口 | 输入 | 预期结果 |
| --- | --- | --- | --- |
| TDD-TEST-032 | MDD-API-001 `request_checkpoint` | 缺少 `artifacts` 的检查点请求 | 返回错误，不允许继续。 |
| TDD-TEST-033 | MDD-API-002 `resolve_targets` | 指定不存在的 skill 名称 | 返回明确错误，不创建目标。 |
| TDD-TEST-034 | MDD-API-003 `conduct_domain_research` | 无研究工具、无外部资料 | 生成低或中置信度研究结果，方法为内部知识或一般推断，不伪造来源。 |
| TDD-TEST-035 | MDD-API-004 `generate_domain_rubric` | 研究置信度为 low | 领域评分标准标记低置信度，并列出待用户确认问题。 |
| TDD-TEST-036 | MDD-API-005 `prepare_prompt_set` | 领域 prompt 未关联维度 | 返回不合格状态，要求补充目标维度或 hard gate。 |
| TDD-TEST-037 | MDD-API-006 `evaluate_domain_rubric_quality` | 维度抽象、无锚点、无依据的领域评分标准 | 输出低于门槛的总分，结论为 `revise` 或 `reject`。 |
| TDD-TEST-038 | MDD-API-007 `confirm_and_freeze_domain_rubric` | 用户修改了领域评分标准但未重新评估 | 拒绝冻结，并要求重新运行质量评估。 |
| TDD-TEST-039 | MDD-API-008 `run_effect_validation` | 未确认的 `PromptSet` | 拒绝执行验证。 |
| TDD-TEST-040 | MDD-API-009 `score_common_rubric` | 8 个维度或 10 个维度的公共 rubric | 返回错误，要求 9 个维度。 |
| TDD-TEST-041 | MDD-API-010 `score_domain_rubric` | 未冻结的领域评分标准 | 拒绝正式领域评分，除非用户已跳过领域评分。 |
| TDD-TEST-042 | MDD-API-011 `scan_runtime_neutrality` | 包含“Claude Code skill”的测试文本 | 返回 1 条红灯命中，包含行号和建议修复方向。 |
| TDD-TEST-043 | MDD-API-012 `plan_single_dimension_change` | 同时要求修改多个无关维度 | 返回错误或要求重写计划。 |
| TDD-TEST-044 | MDD-API-013 `decide_and_record` | 综合分上升但 hard gate 触发 | 输出 `stop` 或 `revert`，不得输出 `keep`。 |
| TDD-TEST-045 | MDD-API-014 `build_report_package` | 缺少成果卡片模板文件 | 记录失败原因，不生成伪造输出路径。 |

## 4. 文档一致性测试

| 测试 ID | 检查项 | 判定标准 |
| --- | --- | --- |
| TDD-TEST-046 | 必需文件 | `SKILL.md`、README、docs、模板、脚本和 `.vibe` 状态文件存在。 |
| TDD-TEST-047 | URD 到 ADD | 每个 `URD-REQ` 至少映射到一个 `ADD-FR` 或明确说明原因。 |
| TDD-TEST-048 | ADD 到 MDD | 每个 `ADD-DP` 至少映射到一个 `MDD-MOD` 和 `MDD-API`。 |
| TDD-TEST-049 | MDD 到 TDD | 每个 `MDD-API` 至少有一个契约测试。 |
| TDD-TEST-050 | `.vibe/trace.json` | JSON 可解析，且列出 URD、ADD、MDD、TDD、RMD 文档路径。 |
| TDD-TEST-051 | `.vibe/coupling_history.json` | JSON 可解析，且最终状态为 `decoupled_lower_triangular`。 |
| TDD-TEST-052 | 文档标记检查 | 新增文档不得包含未处理的占位标记。 |
| TDD-TEST-053 | 项目用词检查 | 新增文档不得包含项目指令中禁止的空泛表达。 |
| TDD-TEST-054 | wiki 缺失检查 | 本轮不生成 wiki 文件。 |
| TDD-TEST-055 | ADD 矩阵检查 | ADD 设计矩阵右上区域不得出现直接依赖。 |

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
| TDD-DEFER-004 | 联网研究资料质量的真实外部复查 | 当前环境不要求联网执行，只规定有联网能力时的记录和验证方式。 |
