# Darwin Skill 2.0 模块设计文档

本文档把 `docs/ADD.md` 中的 14 个设计参数转成逻辑模块、接口、数据结构和契约。当前项目主要交付物是 Agent Skill 文档和配套资源，因此这里的“模块”指可独立维护和测试的职责单元，不要求已经存在同名代码文件。

## 1. 模块总览

| ID | 模块 | 对应设计参数 | 责任 |
| --- | --- | --- | --- |
| MDD-MOD-001 | 阶段检查点控制 | ADD-DP-001 | 决定何时暂停、展示什么、用户确认后如何继续。 |
| MDD-MOD-002 | 目标范围解析 | ADD-DP-002 | 从用户请求和运行目录识别待处理 skill。 |
| MDD-MOD-003 | 领域研究记录 | ADD-DP-003 | 选择实际可用研究路径，生成领域研究文件和元数据。 |
| MDD-MOD-004 | 领域评分标准生成 | ADD-DP-004 | 基于研究结果、目标 skill 和用户目标生成领域评分标准。 |
| MDD-MOD-005 | 测试 prompt 管理 | ADD-DP-005 | 生成、复用、校验和展示公共及领域测试 prompt。 |
| MDD-MOD-006 | 领域评分标准质量评估 | ADD-DP-006 | 按 RQ1 到 RQ9 评估领域评分标准本身是否可用。 |
| MDD-MOD-007 | 领域评分确认与冻结 | ADD-DP-007 | 管理用户选择、版本记录、重新评估、冻结和跳过领域评分。 |
| MDD-MOD-008 | 效果验证执行 | ADD-DP-008 | 执行独立评审或干跑验证，并标注验证模式。 |
| MDD-MOD-009 | 公共评分 | ADD-DP-009 | 按公共 rubric 输出维度分、权重分、总分和短板。 |
| MDD-MOD-010 | 领域评分 | ADD-DP-010 | 按冻结的领域评分标准输出领域分、hard gates 和失败说明。 |
| MDD-MOD-011 | runtime 中立性扫描 | ADD-DP-011 | 扫描单 runtime 绑定表达，输出红灯项。 |
| MDD-MOD-012 | 单维度优化控制 | ADD-DP-012 | 选择本轮唯一主要优化方向，并形成可验证改动计划。 |
| MDD-MOD-013 | 综合决策与历史记录 | ADD-DP-013 | 根据公共评分、领域评分、综合评分和 hard gates 决定保留或回滚。 |
| MDD-MOD-014 | 成果报告与公开说明检查 | ADD-DP-014 | 生成结果卡片和报告，并检查公开文档与 skill 行为一致。 |

## 2. 数据结构

| ID | 名称 | 字段 |
| --- | --- | --- |
| MDD-DATA-001 | `SkillTarget` | `name`, `root_path`, `skill_path`, `readme_paths`, `source` |
| MDD-DATA-002 | `CheckpointRequest` | `phase`, `reason`, `artifacts`, `required_decision` |
| MDD-DATA-003 | `CheckpointDecision` | `phase`, `decision`, `notes`, `timestamp` |
| MDD-DATA-004 | `ResearchSource` | `type`, `title`, `location`, `used_for` |
| MDD-DATA-005 | `DomainResearch` | `research_scope`, `skill_goal_summary`, `expected_task_outcome`, `available_evidence`, `research_methods`, `key_findings`, `candidate_evaluation_concerns`, `common_failure_modes`, `high_risk_failure_modes`, `evidence_gaps`, `confidence_level`, `notes` |
| MDD-DATA-006 | `DomainResearchMeta` | `research_version`, `created_at`, `source_skill_path`, `research_methods`, `sources`, `confidence_level`, `evidence_gaps`, `notes` |
| MDD-DATA-007 | `DomainRubricDimension` | `id`, `name`, `weight`, `anchors`, `common_failures`, `evidence_to_check`, `source_refs` |
| MDD-DATA-008 | `DomainRubric` | `rubric_version`, `domain_name`, `skill_goal`, `expected_input`, `expected_output`, `user_intent`, `success_criteria`, `dimensions`, `hard_gates`, `confidence_level`, `questions_for_user` |
| MDD-DATA-009 | `DomainPromptCase` | `id`, `scenario`, `prompt`, `purpose`, `expected_checks`, `target_dimensions`, `target_hard_gates` |
| MDD-DATA-010 | `DomainRubricMeta` | `rubric_version`, `research_version`, `created_at`, `source_skill_path`, `is_frozen`, `common_weight`, `domain_weight`, `rubric_quality_score`, `rubric_quality_decision`, `rubric_quality_evaluation_version`, `research_confidence_level`, `requires_user_confirmation`, `notes` |
| MDD-DATA-011 | `RubricQualityDimensionScore` | `id`, `name`, `weight`, `score`, `reason` |
| MDD-DATA-012 | `DomainRubricEvaluation` | `rubric_version`, `evaluation_version`, `created_at`, `overall_score`, `dimension_scores`, `hard_gate_review`, `decision`, `required_revisions`, `notes` |
| MDD-DATA-013 | `PromptSet` | `target`, `common_cases`, `domain_cases`, `source`, `confirmed` |
| MDD-DATA-014 | `ValidationReport` | `target`, `mode`, `cases`, `judge_count`, `findings`, `risk_notes` |
| MDD-DATA-015 | `DimensionScore` | `dimension_id`, `name`, `weight`, `raw_score`, `weighted_score`, `reason` |
| MDD-DATA-016 | `CommonScoreReport` | `target`, `dimensions`, `common_score`, `weakest_dimensions`, `validation_mode` |
| MDD-DATA-017 | `DomainScoreReport` | `target`, `rubric_version`, `domain_score`, `dimension_scores`, `hard_gate_status`, `failure_notes` |
| MDD-DATA-018 | `RuntimeFinding` | `path`, `line`, `pattern`, `severity`, `suggested_fix` |
| MDD-DATA-019 | `OptimizationPlan` | `target`, `dimension`, `change_summary`, `expected_score_change`, `checks` |
| MDD-DATA-020 | `CompositeDecision` | `target`, `common_score`, `domain_score`, `composite_score`, `hard_gate_status`, `rubric_quality_decision`, `status`, `reason` |
| MDD-DATA-021 | `HistoryRecord` | `timestamp`, `commit`, `skill`, `old_score`, `new_score`, `status`, `dimension`, `note`, `eval_mode`, `common_score`, `domain_score`, `composite_score`, `domain_name`, `rubric_version`, `hard_gate_status`, `hard_gate_reason` |
| MDD-DATA-022 | `ReportPackage` | `target`, `research_summary`, `rubric_quality_summary`, `score_summary`, `decision_summary`, `card_request`, `public_doc_findings` |

## 3. 接口契约

### MDD-API-001 `request_checkpoint`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-001 |
| 输入 | `CheckpointRequest` |
| 输出 | `CheckpointDecision` |
| 前置条件 | `phase` 必须是已定义阶段；`artifacts` 必须包含用户需要判断的最小材料。 |
| 后置条件 | `decision` 明确为 `continue`、`revise`、`skip` 或 `stop`。 |
| 不变量 | 不得在缺少确认的情况下越过 URD 要求的关键阶段。 |
| 副作用 | 可向用户展示 prompt、分数、diff、测试结果、研究文件、领域评分标准或风险说明。 |

### MDD-API-002 `resolve_targets`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-002 |
| 输入 | 用户请求文本、当前目录、可选的显式 skill 名称 |
| 输出 | `SkillTarget[]` |
| 前置条件 | 当前目录可读；用户请求中至少能推断出单个或全部范围。 |
| 后置条件 | 每个目标都有可读的 `SKILL.md` 路径；不能解析时返回明确错误。 |
| 不变量 | 不把范围外文件当作待优化 skill。 |
| 副作用 | 只读取目录和文件，不修改文件。 |

### MDD-API-003 `conduct_domain_research`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-003 |
| 输入 | `SkillTarget`、用户目标、任务说明、已有 prompt、输出样本、失败案例、可用研究能力 |
| 输出 | `DomainResearch`、`DomainResearchMeta` |
| 前置条件 | 目标 skill 内容可读；研究能力清单来自实际可用环境或用户提供信息。 |
| 后置条件 | 生成 `domain-research.md` 和 `domain-research-meta.json`；记录实际研究方法、来源、证据空白和置信度。 |
| 不变量 | 不得伪造联网搜索、内部 skill 调用或外部来源；只用模型已有知识时置信度不得为 `high`。 |
| 副作用 | 可读取用户资料、项目文件或外部资料；可写入领域研究文件。 |

### MDD-API-004 `generate_domain_rubric`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-004 |
| 输入 | `SkillTarget`、用户目标、`DomainResearch`、`DomainResearchMeta`、已有 prompt、输出样本、失败案例 |
| 输出 | `DomainRubric`、初始 `DomainRubricMeta` |
| 前置条件 | `DomainResearch` 已生成；目标 skill 内容可读。 |
| 后置条件 | 生成 `domain-rubric.md`；每个维度有来源引用、权重、1/5/10 分锚点、常见失败和检查证据。 |
| 不变量 | 不得把公共评分维度包装成领域评分维度；研究置信度为 `low` 时领域评分标准也必须标记低置信度。 |
| 副作用 | 可写入 `domain-rubric.md` 和 `domain-rubric-meta.json` 的初始版本。 |

### MDD-API-005 `prepare_prompt_set`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-005 |
| 输入 | `SkillTarget`、已有 `test-prompts.json`、`DomainRubric`、可选用户补充 |
| 输出 | `PromptSet` |
| 前置条件 | 目标 skill 内容可读；若启用领域评分，`DomainRubric` 必须存在。 |
| 后置条件 | 公共 prompt 数量为 2 到 3；领域 prompt 记录测试目的、预期检查点、目标维度和 hard gates。 |
| 不变量 | prompt 必须围绕任务结果质量，不得只检查文件格式。 |
| 副作用 | 可写入或更新 `test-prompts.json` 和 `domain-test-prompts.json`，但正式评分前必须确认。 |

### MDD-API-006 `evaluate_domain_rubric_quality`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-006 |
| 输入 | `DomainRubric`、`DomainResearch`、`DomainRubricMeta`、`PromptSet`、`SkillTarget`、用户目标、质量配置 |
| 输出 | `DomainRubricEvaluation` |
| 前置条件 | `domain-rubric.md`、`domain-research.md` 和领域 prompt 可读。 |
| 后置条件 | 生成 `domain-rubric-evaluation.md` 和 `domain-rubric-evaluation.json`；结论为 `accept`、`revise`、`reject` 或 `needs_user_confirmation`。 |
| 不变量 | 总分低于门槛、关键维度低于最低分、低置信度未确认或模板污染时不得给出自动接受结论。 |
| 副作用 | 写入质量评估文件；不修改已生成的领域评分标准。 |

### MDD-API-007 `confirm_and_freeze_domain_rubric`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-007 |
| 输入 | `DomainRubric`、`DomainResearch`、`DomainRubricEvaluation`、`PromptSet`、用户选择 |
| 输出 | 更新后的 `DomainRubricMeta` |
| 前置条件 | 质量评估已完成；低置信度或低质量状态必须展示给用户。 |
| 后置条件 | 用户选择被记录；冻结后 `is_frozen = true`；用户修改评分标准后必须重新运行质量评估。 |
| 不变量 | 冻结后的 `domain-rubric.md` 和 `domain-rubric-evaluation.md` 不得被优化循环自动改写。 |
| 副作用 | 更新 `domain-rubric-meta.json`；可要求重新研究、重新生成评分标准或跳过领域评分。 |

### MDD-API-008 `run_effect_validation`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-008 |
| 输入 | `SkillTarget`、`PromptSet`、验证策略 |
| 输出 | `ValidationReport` |
| 前置条件 | `PromptSet.confirmed = true`；启用领域评分时领域评分标准已经冻结或已被用户跳过。 |
| 后置条件 | `mode` 必须为 `full_test` 或 `dry_run`；干跑时必须记录原因。 |
| 不变量 | 不得把未执行的效果验证标为 `full_test`。 |
| 副作用 | 可调用独立评审 agent；不可用时只能记录干跑验证。 |

### MDD-API-009 `score_common_rubric`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-009 |
| 输入 | `SkillTarget`、`ValidationReport`、公共 rubric 定义 |
| 输出 | `CommonScoreReport` |
| 前置条件 | skill 文本可读；公共 rubric 权重总和为 100；效果验证已有模式标注。 |
| 后置条件 | 输出 9 个 `DimensionScore` 和 `common_score`；总分保留 1 位小数。 |
| 不变量 | 效果维度不能脱离 `ValidationReport` 单独评分。 |
| 副作用 | 无文件写入。 |

### MDD-API-010 `score_domain_rubric`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-010 |
| 输入 | `SkillTarget`、`ValidationReport`、冻结的 `DomainRubric`、`PromptSet` |
| 输出 | `DomainScoreReport` |
| 前置条件 | `DomainRubricMeta.is_frozen = true`，或用户已跳过领域评分。 |
| 后置条件 | 输出 `domain_score`、领域维度分、hard gate 状态和领域失败说明。 |
| 不变量 | hard gates 只能由输出样本中可观察证据触发。 |
| 副作用 | 无文件写入。 |

### MDD-API-011 `scan_runtime_neutrality`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-011 |
| 输入 | 需要扫描的文档路径列表、红灯模式表 |
| 输出 | `RuntimeFinding[]` |
| 前置条件 | 输入路径可读。 |
| 后置条件 | 每个命中项必须包含文件、行号、模式和建议修复方向。 |
| 不变量 | 明确标注为特定 runtime 的章节不按红灯处理。 |
| 副作用 | 只读文件。 |

### MDD-API-012 `plan_single_dimension_change`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-012 |
| 输入 | `CommonScoreReport`、`DomainScoreReport`、`RuntimeFinding[]`、历史记录 |
| 输出 | `OptimizationPlan` |
| 前置条件 | 公共评分已完成；启用领域评分时领域评分已完成或有跳过记录。 |
| 后置条件 | 只选择一个主要维度，或选择 ADD 中已说明的相关维度组。 |
| 不变量 | runtime 红灯项优先级高于普通评分短板。 |
| 副作用 | 不直接改文件，只生成计划。 |

### MDD-API-013 `decide_and_record`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-013 |
| 输入 | 旧评分、新评分、`DomainRubricEvaluation`、git diff 摘要、验证模式 |
| 输出 | `CompositeDecision`、`HistoryRecord` |
| 前置条件 | 新旧分数来自同一目标 skill；验证模式已标注；领域评分标准质量结论可读。 |
| 后置条件 | 满足公共评分、领域评分、综合评分和 hard gates 规则时才可保留；否则必须回滚或停止，并记录原因。 |
| 不变量 | 禁止把 `git reset --hard` 作为常规回滚动作；低质量领域评分标准不得进入正式优化流程。 |
| 副作用 | 可创建 git commit、git revert commit，并写入新版或旧版兼容结果记录。 |

### MDD-API-014 `build_report_package`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-014 |
| 输入 | `ReportPackage`、公开文档路径列表、成果卡片模板 |
| 输出 | 报告文本、成果卡片路径、一致性检查结果 |
| 前置条件 | 分数、研究摘要、质量评估摘要和决策结果已确定。 |
| 后置条件 | 报告包含 Domain Research 和 Domain Rubric Quality；成果卡片成功生成或记录失败原因；公开文档冲突必须列出。 |
| 不变量 | 报告不得伪造研究来源，不得宣称 `SKILL.md` 没有定义的行为。 |
| 副作用 | 可生成 PNG；可读取 README、发布页、引用资料和 `SKILL.md`。 |

## 4. 模块依赖

| 模块 | 依赖 |
| --- | --- |
| MDD-MOD-001 | 无 |
| MDD-MOD-002 | MDD-MOD-001 |
| MDD-MOD-003 | MDD-MOD-001, MDD-MOD-002 |
| MDD-MOD-004 | MDD-MOD-001 到 MDD-MOD-003 |
| MDD-MOD-005 | MDD-MOD-001 到 MDD-MOD-004 |
| MDD-MOD-006 | MDD-MOD-001 到 MDD-MOD-005 |
| MDD-MOD-007 | MDD-MOD-001 到 MDD-MOD-006 |
| MDD-MOD-008 | MDD-MOD-001, MDD-MOD-002, MDD-MOD-005, MDD-MOD-007 |
| MDD-MOD-009 | MDD-MOD-001, MDD-MOD-002, MDD-MOD-005, MDD-MOD-008 |
| MDD-MOD-010 | MDD-MOD-001 到 MDD-MOD-008 |
| MDD-MOD-011 | MDD-MOD-001, MDD-MOD-002 |
| MDD-MOD-012 | MDD-MOD-001 到 MDD-MOD-011 |
| MDD-MOD-013 | MDD-MOD-001 到 MDD-MOD-012 |
| MDD-MOD-014 | MDD-MOD-001, MDD-MOD-003, MDD-MOD-004, MDD-MOD-006, MDD-MOD-007, MDD-MOD-009, MDD-MOD-010, MDD-MOD-013 |

## 5. 设计约束

| ID | 约束 |
| --- | --- |
| MDD-CON-001 | 默认使用纯数据结构在模块之间传递结果，避免模块直接读取彼此内部状态。 |
| MDD-CON-002 | 能用只读检查完成的模块不得写文件。 |
| MDD-CON-003 | 研究、评分标准生成、质量评估、冻结、评分、决策必须分开记录。 |
| MDD-CON-004 | 涉及文件修改、提交、回滚、成果卡片生成的接口必须说明副作用。 |
| MDD-CON-005 | 研究来源必须来自实际读取、调用或用户提供的材料。 |
| MDD-CON-006 | 当前不定义 wiki 生成模块。 |
