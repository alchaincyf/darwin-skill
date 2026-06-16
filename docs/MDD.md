# Darwin Skill 2.0 模块设计文档

本文档把 `docs/ADD.md` 中的设计参数转成逻辑模块、接口、数据结构和契约。当前项目主要交付物是 Agent Skill 文档和配套资源，因此这里的“模块”指可独立维护和测试的职责单元，不要求已经存在同名代码文件。

## 1. 模块总览

| ID | 模块 | 对应设计参数 | 责任 |
| --- | --- | --- | --- |
| MDD-MOD-001 | 阶段检查点控制 | ADD-DP-001 | 决定何时暂停、展示什么、用户确认后如何继续。 |
| MDD-MOD-002 | 目标范围解析 | ADD-DP-002 | 从用户请求和运行目录识别待处理 skill。 |
| MDD-MOD-003 | 测试 prompt 管理 | ADD-DP-003 | 生成、复用、校验和展示测试 prompt。 |
| MDD-MOD-004 | 效果验证执行 | ADD-DP-004 | 执行独立评审或干跑验证，并标注验证模式。 |
| MDD-MOD-005 | 9 维评分 | ADD-DP-005 | 按 rubric 输出维度分、权重分、总分和短板。 |
| MDD-MOD-006 | runtime 中立性扫描 | ADD-DP-006 | 扫描单 runtime 绑定表达，输出红灯项。 |
| MDD-MOD-007 | 单维度优化控制 | ADD-DP-007 | 选择本轮唯一主要优化方向，并形成可验证改动计划。 |
| MDD-MOD-008 | git 决策与历史记录 | ADD-DP-008 | 根据分数变化保留或回滚，并写入优化历史。 |
| MDD-MOD-009 | 成果卡片与公开说明检查 | ADD-DP-009 | 生成结果卡片，并检查公开文档与 skill 行为一致。 |

## 2. 数据结构

| ID | 名称 | 字段 |
| --- | --- | --- |
| MDD-DATA-001 | `SkillTarget` | `name`, `root_path`, `skill_path`, `readme_paths`, `source` |
| MDD-DATA-002 | `CheckpointRequest` | `phase`, `reason`, `artifacts`, `required_decision` |
| MDD-DATA-003 | `CheckpointDecision` | `phase`, `decision`, `notes`, `timestamp` |
| MDD-DATA-004 | `PromptCase` | `id`, `scenario`, `prompt`, `expected` |
| MDD-DATA-005 | `PromptSet` | `target`, `cases`, `source`, `confirmed` |
| MDD-DATA-006 | `ValidationReport` | `target`, `mode`, `cases`, `judge_count`, `findings`, `risk_notes` |
| MDD-DATA-007 | `DimensionScore` | `dimension_id`, `name`, `weight`, `raw_score`, `weighted_score`, `reason` |
| MDD-DATA-008 | `ScoreReport` | `target`, `dimensions`, `total_score`, `weakest_dimensions`, `validation_mode` |
| MDD-DATA-009 | `RuntimeFinding` | `path`, `line`, `pattern`, `severity`, `suggested_fix` |
| MDD-DATA-010 | `OptimizationPlan` | `target`, `dimension`, `change_summary`, `expected_score_change`, `checks` |
| MDD-DATA-011 | `HistoryRecord` | `timestamp`, `commit`, `skill`, `old_score`, `new_score`, `status`, `dimension`, `note`, `eval_mode` |
| MDD-DATA-012 | `CardRequest` | `target`, `score_before`, `score_after`, `delta`, `improvements`, `theme`, `output_path` |

## 3. 接口契约

### MDD-API-001 `request_checkpoint`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-001 |
| 输入 | `CheckpointRequest` |
| 输出 | `CheckpointDecision` |
| 前置条件 | `phase` 必须是已定义阶段；`artifacts` 必须包含用户需要判断的最小材料。 |
| 后置条件 | `decision` 明确为 `continue`、`revise` 或 `stop`。 |
| 不变量 | 不得在缺少确认的情况下越过 URD 要求的关键阶段。 |
| 副作用 | 可向用户展示 prompt、分数、diff、测试结果或风险说明。 |

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

### MDD-API-003 `prepare_prompt_set`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-003 |
| 输入 | `SkillTarget`、已有 `test-prompts.json`、可选用户补充 |
| 输出 | `PromptSet` |
| 前置条件 | 目标 skill 内容可读。 |
| 后置条件 | 生成或复用 2 到 3 个 `PromptCase`；进入评分前 `confirmed` 必须为 true。 |
| 不变量 | prompt 必须围绕典型使用场景，不用边缘场景替代主任务。 |
| 副作用 | 可写入或更新目标目录下的 `test-prompts.json`，但必须先确认。 |

### MDD-API-004 `run_effect_validation`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-004 |
| 输入 | `SkillTarget`、`PromptSet`、验证策略 |
| 输出 | `ValidationReport` |
| 前置条件 | `PromptSet.confirmed = true`。 |
| 后置条件 | `mode` 必须为 `full_test` 或 `dry_run`；干跑时必须记录原因。 |
| 不变量 | 不得把未执行的效果验证标为 `full_test`。 |
| 副作用 | 可调用独立评审 agent；不可用时只能记录干跑验证。 |

### MDD-API-005 `score_skill`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-005 |
| 输入 | `SkillTarget`、`ValidationReport`、rubric 定义 |
| 输出 | `ScoreReport` |
| 前置条件 | skill 文本可读；rubric 权重总和为 100；效果验证已有模式标注。 |
| 后置条件 | 输出 9 个 `DimensionScore` 和 1 个总分；总分保留 1 位小数。 |
| 不变量 | 维度 8 不能脱离 `ValidationReport` 单独评分。 |
| 副作用 | 无文件写入。 |

### MDD-API-006 `scan_runtime_neutrality`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-006 |
| 输入 | 需要扫描的文档路径列表、红灯模式表 |
| 输出 | `RuntimeFinding[]` |
| 前置条件 | 输入路径可读。 |
| 后置条件 | 每个命中项必须包含文件、行号、模式和建议修复方向。 |
| 不变量 | 明确标注为特定 runtime 的章节不按红灯处理。 |
| 副作用 | 只读文件。 |

### MDD-API-007 `plan_single_dimension_change`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-007 |
| 输入 | `ScoreReport`、`RuntimeFinding[]`、历史记录 |
| 输出 | `OptimizationPlan` |
| 前置条件 | 已有评分报告；runtime 扫描已执行或明确跳过原因。 |
| 后置条件 | 只选择一个主要维度，或选择 ADD 中已说明的相关维度组。 |
| 不变量 | runtime 红灯项优先级高于普通评分短板。 |
| 副作用 | 不直接改文件，只生成计划。 |

### MDD-API-008 `decide_and_record`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-008 |
| 输入 | 旧 `ScoreReport`、新 `ScoreReport`、git diff 摘要、验证模式 |
| 输出 | `HistoryRecord` |
| 前置条件 | 新旧分数来自同一目标 skill；验证模式已标注。 |
| 后置条件 | 新分严格高于旧分时可保留；否则必须回滚或停止，并记录原因。 |
| 不变量 | 禁止把 `git reset --hard` 作为常规回滚动作。 |
| 副作用 | 可创建 git commit、git revert commit，并写入 `results.tsv`。 |

### MDD-API-009 `create_card_and_check_public_docs`

| 项 | 内容 |
| --- | --- |
| 所属模块 | MDD-MOD-009 |
| 输入 | `CardRequest`、公开文档路径列表 |
| 输出 | 成果卡片路径、一致性检查结果 |
| 前置条件 | 分数变化和改进摘要已确定。 |
| 后置条件 | 成果卡片成功生成，或记录无法生成的原因；公开文档冲突必须列出。 |
| 不变量 | 公开文档不得宣称 `SKILL.md` 没有定义的行为。 |
| 副作用 | 可生成 PNG；可读取 README、发布页、引用资料和 `SKILL.md`。 |

## 4. 模块依赖

| 模块 | 依赖 |
| --- | --- |
| MDD-MOD-001 | 无 |
| MDD-MOD-002 | MDD-MOD-001 |
| MDD-MOD-003 | MDD-MOD-001, MDD-MOD-002 |
| MDD-MOD-004 | MDD-MOD-001, MDD-MOD-002, MDD-MOD-003 |
| MDD-MOD-005 | MDD-MOD-001, MDD-MOD-002, MDD-MOD-003, MDD-MOD-004 |
| MDD-MOD-006 | MDD-MOD-001, MDD-MOD-002 |
| MDD-MOD-007 | MDD-MOD-001 到 MDD-MOD-006 |
| MDD-MOD-008 | MDD-MOD-001, MDD-MOD-002, MDD-MOD-005, MDD-MOD-007 |
| MDD-MOD-009 | MDD-MOD-001, MDD-MOD-005, MDD-MOD-008 |

## 5. 设计约束

| ID | 约束 |
| --- | --- |
| MDD-CON-001 | 默认使用纯数据结构在模块之间传递结果，避免模块直接读取彼此内部状态。 |
| MDD-CON-002 | 能用只读检查完成的模块不得写文件。 |
| MDD-CON-003 | 评分、验证、优化计划、git 决策必须分开记录，便于判断问题来源。 |
| MDD-CON-004 | 涉及文件修改、提交、回滚、成果卡片生成的接口必须说明副作用。 |
| MDD-CON-005 | 当前不定义 wiki 生成模块。 |

