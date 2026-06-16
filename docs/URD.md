# Darwin Skill 2.0 用户需求文档

本文档根据当前仓库内容和新增需求反推需求。依据文件包括 `SKILL.md`、`README.md`、`README_EN.md`、`test-prompts.json`、`references/skilllens-evidence.md`、`references/runtime-neutrality.md`、`templates/`、`scripts/`、`docs/index.html`，以及新增需求《个体化领域评分标准生成与评估》和补充需求《领域评分标准的研究依据与质量评估》。

## 1. 项目目标

| ID | 目标 |
| --- | --- |
| URD-GOAL-001 | 提供一个可安装的 Agent Skill，用于评估和改进其他 `SKILL.md` 文件。 |
| URD-GOAL-002 | 通过结构评分、效果验证、独立评审和用户确认，降低 skill 优化中的自评偏差和无效改动。 |
| URD-GOAL-003 | 让 skill 作者能看到每次优化的分数变化、测试依据、保留或回滚结果，并生成可展示的成果卡片。 |
| URD-GOAL-004 | 保持对多种 skills-compatible runtime 的中立描述，避免文档和流程绑定单一 agent 工具。 |
| URD-GOAL-005 | 在保留公共评分标准的同时，为每个被优化 skill 生成个体化领域评分标准，用任务结果质量参与评估和保留决策。 |
| URD-GOAL-006 | 在领域评分标准进入优化前，记录研究依据并评估评分标准本身质量，防止低质量评分标准误导后续优化。 |

## 2. 用户角色

| ID | 角色 | 需要完成的事 |
| --- | --- | --- |
| URD-ROLE-001 | Skill 维护者 | 评估一个或多个 skill 的质量，决定是否进入优化。 |
| URD-ROLE-002 | Skill 作者 | 根据评分报告和测试结果改进某个 `SKILL.md`。 |
| URD-ROLE-003 | Agent 工具用户 | 安装 darwin-skill，在自己的 agent runtime 中触发评估或优化。 |
| URD-ROLE-004 | 项目维护者 | 维护 README、引用资料、测试提示、模板和发布页，使它们与 `SKILL.md` 一致。 |

## 3. 当前范围

### 3.1 范围内

| ID | 范围 |
| --- | --- |
| URD-SCOPE-001 | 评估单个或多个 Agent Skill 的 `SKILL.md`。 |
| URD-SCOPE-002 | 为待评估 skill 设计或复用 2 到 3 个典型测试 prompt。 |
| URD-SCOPE-003 | 使用 9 维 rubric 输出结构分、效果分和总分。 |
| URD-SCOPE-004 | 用独立评审或明确标注的干跑验证评估效果维度。 |
| URD-SCOPE-005 | 检查 runtime 中立性，并把命中项作为优先修复事项。 |
| URD-SCOPE-006 | 每轮只针对一个主要短板提出和执行改动，并用 git 记录保留或回滚。 |
| URD-SCOPE-007 | 在关键阶段暂停，向用户展示 prompt、分数、diff、测试结果和风险。 |
| URD-SCOPE-008 | 记录优化历史到 `results.tsv`，包含时间、commit、skill、分数、状态、维度、说明和验证模式。 |
| URD-SCOPE-009 | 使用模板和截图脚本生成优化成果卡片。 |
| URD-SCOPE-010 | 维护中英文 README、引用资料、测试提示和发布页，使公开说明与 skill 行为一致。 |
| URD-SCOPE-011 | 为被优化 skill 生成 `domain-rubric.md`、`domain-test-prompts.json` 和 `domain-rubric-meta.json`。 |
| URD-SCOPE-012 | 在评估中同时计算 `common_score`、`domain_score` 和 `composite_score`。 |
| URD-SCOPE-013 | 支持用户查看、修改、确认和冻结个体化领域评分标准。 |
| URD-SCOPE-014 | 在保留或回滚决策中检查公共评分、领域评分、综合评分和 hard gates。 |
| URD-SCOPE-015 | 记录每轮优化使用的领域评分版本、权重和 hard gate 触发状态。 |
| URD-SCOPE-016 | 在没有领域评分文件或用户关闭领域评分时，继续支持原有公共评分流程。 |
| URD-SCOPE-017 | 在生成领域评分标准前执行 Phase 0.10 领域调查研究。 |
| URD-SCOPE-018 | 根据当前可用能力选择研究路径，并记录实际使用的研究方法和依据来源。 |
| URD-SCOPE-019 | 生成 `domain-research.md` 和 `domain-research-meta.json`，记录研究范围、发现、证据空白和置信度。 |
| URD-SCOPE-020 | 在领域评分标准冻结前执行 Phase 0.30 质量评估。 |
| URD-SCOPE-021 | 生成 `domain-rubric-evaluation.md` 和 `domain-rubric-evaluation.json`，记录评分标准质量分、维度分、问题和结论。 |
| URD-SCOPE-022 | 低质量或低置信度领域评分标准不得自动进入正式优化流程。 |
| URD-SCOPE-023 | 在优化报告和领域评分元数据中记录研究版本、研究置信度、质量分、质量结论和用户确认状态。 |

### 3.2 范围外

| ID | 范围外事项 |
| --- | --- |
| URD-OOS-001 | 不提供完整的独立 SaaS、Web 后端或数据库服务。 |
| URD-OOS-002 | 不自动发布或分发被优化后的第三方 skill。 |
| URD-OOS-003 | 不承诺 LLM judge 对细粒度质量差异完全可靠。 |
| URD-OOS-004 | 不在没有用户确认的情况下执行高风险 git 操作、远程推送或合并。 |
| URD-OOS-005 | 不把某一个 runtime 的私有能力作为唯一执行路径。 |
| URD-OOS-006 | 不废弃现有公共评分标准。 |
| URD-OOS-007 | 不内置固定领域评分表，也不根据领域名称直接套用评分维度。 |
| URD-OOS-008 | 不引入外部数据库或复杂 UI。 |
| URD-OOS-009 | 不修改 Agent Skill 的基本文件格式。 |
| URD-OOS-010 | 不强制旧项目立即迁移到领域评分流程。 |
| URD-OOS-011 | 不要求把 Phase 0.10 写成完整研究报告或论文。 |
| URD-OOS-012 | 不要求所有运行环境都有联网搜索或 deep research 类型 skill。 |
| URD-OOS-013 | 不把模型已有知识伪装成外部资料或工具研究结果。 |
| URD-OOS-014 | 不允许系统在低置信度或质量不合格时自动冻结领域评分标准。 |

## 4. 功能需求

| ID | 需求 | 来源 |
| --- | --- | --- |
| URD-REQ-001 | 系统必须支持“优化单个 skill”和“评估所有 skills”两类主要入口。 | `SKILL.md` 使用方式、`test-prompts.json` |
| URD-REQ-002 | 系统必须在正式评分前确认或生成测试 prompt，并展示给用户确认。 | `SKILL.md` Phase 0.5 |
| URD-REQ-003 | 系统必须按 9 个维度评分，总分满分 100，并区分结构维度、效果维度和反例黑名单维度。 | `SKILL.md` 评估 Rubric |
| URD-REQ-004 | 效果评分必须基于测试 prompt；不能完整实测时，必须标注 `dry_run`。 | `SKILL.md` 关于实测表现、`references/skilllens-evidence.md` |
| URD-REQ-005 | 系统必须避免同一上下文自评自改；重要评分应由独立评审完成，至少给出独立性说明。 | `SKILL.md`、`references/skilllens-evidence.md` |
| URD-REQ-006 | 系统必须扫描 runtime 中立性红灯项，并在命中时优先修复。 | `references/runtime-neutrality.md` |
| URD-REQ-007 | 优化循环每轮必须只处理一个主要维度或一个明确相关维度簇，避免无法归因。 | `SKILL.md` Phase 2、反例黑名单 |
| URD-REQ-008 | 改进后总分必须严格高于旧分才保留；低于或等于旧分时必须回滚或停止。 | `SKILL.md` 评分规则、Phase 2 |
| URD-REQ-009 | 回滚必须使用可追溯方式，禁止把 `git reset --hard` 当作常规回滚方式。 | `SKILL.md` 反例黑名单 |
| URD-REQ-010 | 系统必须在 Phase 1、Phase 2、Phase 2.5、Phase 3 等关键节点请求用户确认。 | `SKILL.md` 检查点设计 |
| URD-REQ-011 | 系统必须记录优化历史，字段至少包括时间、commit、skill、旧分、新分、状态、维度、说明和验证模式。 | `SKILL.md` results.tsv |
| URD-REQ-012 | 系统必须提供成果卡片生成路径，使用现有 HTML 模板和截图脚本生成 PNG。 | `SKILL.md` 成果卡片生成、`templates/`、`scripts/` |
| URD-REQ-013 | README 和发布页必须能让用户理解安装方式、核心机制、v2.0 变化、学术依据和主要使用方式。 | `README.md`、`README_EN.md`、`docs/index.html` |
| URD-REQ-014 | 项目必须保留 SkillLens、SkillOpt、autoresearch 的来源说明，并区分外部证据与本机验证数据。 | `README.md`、`references/skilllens-evidence.md` |
| URD-REQ-015 | 系统必须保留现有公共评分标准，并新增个体化领域评分标准生成阶段。 | 新增需求《个体化领域评分标准生成与评估》 |
| URD-REQ-016 | 系统必须根据目标 skill 的任务目标、输入、输出、使用场景、失败风险和用户目标生成领域评分标准。 | 新增需求 |
| URD-REQ-017 | 系统必须生成 `domain-rubric.md`，其中包含领域名称、skill 目标、期望输入、期望输出、用户意图、成功标准、评分维度、hard gates、领域测试 prompt 要求和说明。 | 新增需求 |
| URD-REQ-018 | `domain-rubric.md` 中每个领域评分维度必须有稳定 ID、正权重、1 分、5 分、10 分评分说明、常见失败情况和评估证据；所有维度权重之和必须为 100。 | 新增需求 |
| URD-REQ-019 | 系统必须生成 `domain-test-prompts.json`，至少包含 3 个领域测试 prompt；每个 prompt 必须说明测试目的、预期检查点和目标领域维度。 | 新增需求 |
| URD-REQ-020 | 系统必须生成 `domain-rubric-meta.json`，记录领域名称、版本、创建时间、来源 skill、冻结状态、公共评分权重、领域评分权重、生成来源和说明。 | 新增需求 |
| URD-REQ-021 | 系统不得使用内置具体领域模板，不得根据目录名、文件名、领域名称或少量关键词直接生成固定领域评分维度。 | 新增需求 |
| URD-REQ-022 | 领域评分标准必须评价目标任务结果，不得重复包装公共评分维度或主要评价 `SKILL.md` 文件格式。 | 新增需求 |
| URD-REQ-023 | 领域评分标准生成后必须展示给用户确认；用户可接受、修改后接受、重新生成或跳过领域评分。 | 新增需求 |
| URD-REQ-024 | 用户确认后，领域评分标准默认冻结；同一轮优化中不得被优化循环自动改写。 | 新增需求 |
| URD-REQ-025 | 评估结果必须同时报告公共评分、领域评分、综合评分、领域评分版本和 hard gates 状态，不得只报告综合分。 | 新增需求 |
| URD-REQ-026 | 保留或回滚规则必须同时检查公共评分、领域评分、综合评分和 hard gates；公共评分上升但领域评分下降时默认不保留。 | 新增需求 |
| URD-REQ-027 | 新版结果记录必须扩展公共评分、领域评分、综合评分、领域名称、领域评分版本、hard gate 状态和原因字段，同时旧 `results.tsv` 缺少新字段时仍可读取。 | 新增需求 |
| URD-REQ-028 | 当无法判断目标任务时，系统必须生成 `generic_task_rubric` 并提示用户人工确认，不得臆造具体领域评分维度。 | 新增需求 |
| URD-REQ-029 | 领域评分功能必须可通过配置关闭；没有 `domain-rubric.md` 时，原有公共评分流程必须继续可用。 | 新增需求 |
| URD-REQ-030 | 系统必须在生成领域评分标准前新增 Phase 0.10 领域调查研究，用于理解目标 skill 的真实评价方式。 | 补充需求《领域评分标准的研究依据与质量评估》 |
| URD-REQ-031 | 系统必须按优先级选择研究路径：deep research 类型 skill、用户材料或项目文件、联网搜索、模型已有知识、一般推断；实际使用的方法必须记录。 | 补充需求 |
| URD-REQ-032 | 系统不得假装已经搜索或调用研究工具；使用联网资料时必须记录来源，使用内部 skill 或知识库时必须记录调用对象，只使用模型已有知识时必须标记低证据等级。 | 补充需求 |
| URD-REQ-033 | 系统必须生成 `domain-research.md`，包含研究范围、skill 目标摘要、预期任务结果、可用证据、研究方法、关键发现、候选评价关注点、常见失败、高风险失败、证据空白、置信度和说明。 | 补充需求 |
| URD-REQ-034 | 系统必须生成 `domain-research-meta.json`，记录 `research_version`、创建时间、来源 skill 路径、研究方法、依据来源、置信度、证据空白和说明。 | 补充需求 |
| URD-REQ-035 | Phase 0.25 生成 `domain-rubric.md` 时必须同时读取目标 `SKILL.md`、用户目标、`domain-research.md`、`domain-research-meta.json`、测试 prompt、输出样本和失败案例。 | 补充需求 |
| URD-REQ-036 | 每个领域评分维度必须能追溯到任务目标、研究发现、用户资料或失败风险；研究置信度为 low 时，领域评分标准也必须标记为 low confidence。 | 补充需求 |
| URD-REQ-037 | 证据不足时，`domain-rubric.md` 必须列出需要用户确认的问题，不得把无关背景信息或公共评分维度包装成领域评分维度。 | 补充需求 |
| URD-REQ-038 | 系统必须在领域评分标准冻结前新增 Phase 0.30，对 `domain-rubric.md` 本身进行质量评估。 | 补充需求 |
| URD-REQ-039 | 系统必须生成 `domain-rubric-evaluation.md` 和 `domain-rubric-evaluation.json`，记录总分、维度分、hard gate 检查、证据检查、测试 prompt 匹配、发现问题、必要修订和结论。 | 补充需求 |
| URD-REQ-040 | 领域评分标准质量评估必须使用 RQ1 到 RQ9 九个维度，总分 100：目标匹配度 15、研究依据充分性 15、维度完整性 10、维度独立性 10、可观察性与可评分性 15、权重合理性 10、hard gates 合理性 10、测试 prompt 匹配度 10、抗污染能力 5。 | 补充需求 |
| URD-REQ-041 | 质量门槛必须执行：总分不低于 80 才可进入用户确认；65 到 79 必须修订；低于 65 默认拒绝。 | 补充需求 |
| URD-REQ-042 | 当 RQ1 低于 10/15、RQ5 低于 10/15、RQ7 低于 6/10，或发现模板污染且配置要求拒绝时，系统不得接受该领域评分标准。 | 补充需求 |
| URD-REQ-043 | 研究置信度为 low 时，系统必须要求用户确认，不得自动接受或自动冻结领域评分标准。 | 补充需求 |
| URD-REQ-044 | Phase 0.35 必须向用户展示 `domain-rubric.md`、`domain-research.md`、`domain-rubric-evaluation.md` 和 `domain-test-prompts.json`，并支持接受冻结、修改后冻结、重新研究、重新生成评分标准或跳过领域评分。 | 补充需求 |
| URD-REQ-045 | 用户修改领域评分标准后必须重新运行 Phase 0.30；研究依据变化后必须重新运行 Phase 0.25 和 Phase 0.30。 | 补充需求 |
| URD-REQ-046 | `domain-rubric-meta.json` 必须新增研究版本、质量分、质量结论、质量评估版本、研究置信度、是否需要用户确认和是否冻结字段。 | 补充需求 |
| URD-REQ-047 | 优化报告必须新增 Domain Research 和 Domain Rubric Quality 内容，说明研究方法、证据空白、置信度、质量分、结论和必要修订。 | 补充需求 |
| URD-REQ-048 | 没有研究工具或资料不足时，系统仍应基于 `SKILL.md`、用户目标、测试 prompt 和已有样本进行内部推断，并降低置信度、记录证据空白、要求用户确认。 | 补充需求 |
| URD-REQ-049 | 领域评分标准质量不合格时，系统不得进入正式优化循环，必须根据必要修订修改后重新评估；连续修订失败时应提示用户人工介入。 | 补充需求 |

## 5. 验收标准

| ID | 验收标准 | 对应需求 |
| --- | --- | --- |
| URD-AC-001 | 当用户要求优化某个 skill 时，流程能识别目标 skill、检查 git 状态、准备测试 prompt，并在评分前暂停确认。 | URD-REQ-001, URD-REQ-002, URD-REQ-010 |
| URD-AC-002 | 对任一被评估 skill，报告必须包含 9 个维度、权重、分数、总分和主要短板。 | URD-REQ-003 |
| URD-AC-003 | 效果维度报告必须说明使用 `full_test` 还是 `dry_run`，且 `dry_run` 比例过高时给出失效风险。 | URD-REQ-004 |
| URD-AC-004 | runtime 中立性扫描命中时，报告必须列出命中项，并把第一轮优化方向设为 runtime drift 修复。 | URD-REQ-006 |
| URD-AC-005 | 每轮优化报告必须说明本轮改动对应的维度、预期影响、实际分数变化和保留或回滚决定。 | URD-REQ-007, URD-REQ-008 |
| URD-AC-006 | 若新分不高于旧分，系统不得静默保留改动。 | URD-REQ-008, URD-REQ-009 |
| URD-AC-007 | `results.tsv` 新增记录时，字段必须符合当前 `SKILL.md` 中定义的 9 列格式。 | URD-REQ-011 |
| URD-AC-008 | 生成成果卡片时，输出 PNG 必须来自 `templates/result-card*.html` 和 `scripts/screenshot.mjs` 或等价的 Playwright 截图流程。 | URD-REQ-012 |
| URD-AC-009 | README、发布页和 `SKILL.md` 对 v2.0 的核心描述不得互相冲突。 | URD-REQ-013, URD-REQ-014 |
| URD-AC-010 | 对一个任务目标明确的 skill，系统能生成 `domain-rubric.md`、`domain-test-prompts.json` 和 `domain-rubric-meta.json`。 | URD-REQ-015, URD-REQ-016, URD-REQ-017, URD-REQ-019, URD-REQ-020 |
| URD-AC-011 | 生成的领域评分维度权重之和为 100，且每个维度都有 1、5、10 分说明、失败情况和评估证据。 | URD-REQ-018 |
| URD-AC-012 | 对任务目标不清楚的 skill，系统生成 `generic_task_rubric`，提示用户人工确认，并避免编造具体领域评分维度。 | URD-REQ-028 |
| URD-AC-013 | 检查代码和生成结果时，不存在固定具体领域评分维度列表，也不存在按领域名称直接套用固定 rubric 的逻辑。 | URD-REQ-021 |
| URD-AC-014 | 每轮评估报告分别展示 `common_score`、`domain_score`、`composite_score`、领域名称、领域评分版本和 hard gates 状态。 | URD-REQ-025 |
| URD-AC-015 | 构造公共评分上升但领域评分下降的案例时，系统默认不保留修改，并在报告中说明原因。 | URD-REQ-026 |
| URD-AC-016 | 构造综合评分上升但触发 hard gate 的案例时，系统默认不保留修改，并在报告中说明 hard gate 原因。 | URD-REQ-026 |
| URD-AC-017 | 领域评分标准确认并冻结后，优化循环自动改写该评分标准时必须被拒绝，并记录原因。 | URD-REQ-023, URD-REQ-024 |
| URD-AC-018 | 旧项目没有 `domain-rubric.md` 时，公共评分流程不报错、不强制生成领域评分。 | URD-REQ-029 |
| URD-AC-019 | 新版结果记录包含公共评分、领域评分、综合评分、领域名称、领域评分版本、hard gate 状态和原因；读取旧记录时不崩溃。 | URD-REQ-027 |
| URD-AC-020 | 对任一进入领域评分流程的目标 skill，系统先生成 `domain-research.md` 和 `domain-research-meta.json`，再生成 `domain-rubric.md`。 | URD-REQ-030, URD-REQ-033, URD-REQ-034 |
| URD-AC-021 | 构造不同系统能力时，研究路径选择符合 deep research 类型 skill、用户材料或项目文件、联网搜索、模型已有知识、一般推断的优先级。 | URD-REQ-031 |
| URD-AC-022 | 研究元数据包含 `research_methods`、`sources`、`confidence_level` 和 `evidence_gaps`，并且没有伪造外部来源。 | URD-REQ-032, URD-REQ-034 |
| URD-AC-023 | 生成的领域评分维度能追溯到研究发现、任务目标、用户资料或失败风险；低置信度研究会传递到领域评分标准。 | URD-REQ-035, URD-REQ-036, URD-REQ-037 |
| URD-AC-024 | 每次冻结领域评分标准前，系统生成 `domain-rubric-evaluation.md` 和 `domain-rubric-evaluation.json`。 | URD-REQ-038, URD-REQ-039 |
| URD-AC-025 | 质量评估结果包含 RQ1 到 RQ9 的维度分、总分和 `accept`、`revise`、`reject` 或 `needs_user_confirmation` 结论。 | URD-REQ-040 |
| URD-AC-026 | 低于质量门槛、关键维度低于最低分或发现模板污染时，系统给出修订或拒绝结论，并阻止进入正式优化流程。 | URD-REQ-041, URD-REQ-042, URD-REQ-049 |
| URD-AC-027 | 只依赖模型已有知识或一般推断的研究结果不得标记为 high，且必须设置需要用户确认。 | URD-REQ-032, URD-REQ-043, URD-REQ-048 |
| URD-AC-028 | Phase 0.35 展示领域评分、领域研究、质量评估和领域测试 prompt，并记录用户选择。 | URD-REQ-044 |
| URD-AC-029 | 用户修改领域评分标准后重新运行质量评估；研究依据变化后重新生成领域评分标准并重新评估。 | URD-REQ-045 |
| URD-AC-030 | `domain-rubric-meta.json` 包含研究版本、质量分、质量结论、质量评估版本、研究置信度、确认要求和冻结状态。 | URD-REQ-046 |
| URD-AC-031 | 优化报告包含 Domain Research 和 Domain Rubric Quality 内容；强制使用低质量评分标准时报告标记风险。 | URD-REQ-047 |

## 6. 约束

| ID | 约束 |
| --- | --- |
| URD-CON-001 | 项目交付形式是 Agent Skill 文件和配套文档、模板、素材，不是常驻服务。 |
| URD-CON-002 | 核心优化对象是 `SKILL.md`，一次实验应避免同时修改多个无关资产。 |
| URD-CON-003 | 评分结果必须能追溯到 rubric、测试 prompt、验证模式和用户确认点。 |
| URD-CON-004 | 重要决策必须保留人工确认，因为现有证据显示 LLM judge 对细粒度差异仍可能误判。 |
| URD-CON-005 | 高风险动作必须明示禁止或要求确认，包括 `git reset --hard`、强制推送、未确认的远程推送和静默跳过异常。 |
| URD-CON-006 | 文档应保持 runtime 中立，除非明确标注某段只适用于特定 runtime。 |
| URD-CON-007 | 当前项目公开资料有中英文两套 README，需求变更影响公开说明时必须同时检查两者。 |
| URD-CON-008 | 公共评分和领域评分必须同时存在，二者互不替代。 |
| URD-CON-009 | 领域评分生成必须主要依据目标 skill 内容、用户目标、测试 prompt、输出样本或失败案例。 |
| URD-CON-010 | 领域评分标准不得从固定具体领域模板复制。 |
| URD-CON-011 | 领域评分标准必须可由用户编辑，并在确认后冻结。 |
| URD-CON-012 | 默认权重为 `common_weight = 0.4`、`domain_weight = 0.6`，但应允许配置修改。 |
| URD-CON-013 | 默认保留规则应严格检查领域评分提升、综合评分提升和 hard gates。 |
| URD-CON-014 | 新增字段必须有默认处理方式，避免旧结果文件读取失败。 |
| URD-CON-015 | 研究文件和质量评估文件必须可复查，不能只存在于一次性上下文中。 |
| URD-CON-016 | 研究方法字段只能记录实际使用的方法，不得把未使用工具写入结果。 |
| URD-CON-017 | 联网搜索不是必需能力；没有搜索能力时必须降低证据等级并要求用户确认。 |
| URD-CON-018 | `domain-research-meta.json` 中的来源列表不得包含不存在、未读取或未调用的来源。 |
| URD-CON-019 | 默认配置为 `domain_rubric_quality_threshold = 80`、`allow_low_confidence_rubric = false`、`require_user_confirmation_for_low_confidence = true`、`reject_on_template_contamination = true`。 |
| URD-CON-020 | 质量评估结论进入 `accept` 前，必须同时满足总分门槛和关键维度最低分。 |
| URD-CON-021 | 冻结前不得进入正式优化循环，除非用户显式关闭确认要求。 |
| URD-CON-022 | 冻结后的 `domain-rubric.md` 和 `domain-rubric-evaluation.md` 不得被优化循环自动修改。 |
| URD-CON-023 | 用户跳过领域评分时，公共评分流程继续执行，但报告必须说明领域评分未参与决策。 |

## 7. 假设

| ID | 假设 |
| --- | --- |
| URD-ASM-001 | 用户运行环境已经有支持 Agent Skills 的 agent runtime。 |
| URD-ASM-002 | 待优化 skill 以 `SKILL.md` 作为主要可编辑资产。 |
| URD-ASM-003 | 用户接受在关键节点暂停确认，而不是完全无人值守运行。 |
| URD-ASM-004 | git 可用，且项目位于可提交的仓库中；没有 git 时需要按异常表走备份或初始化流程。 |
| URD-ASM-005 | 成果卡片生成环境可运行 Node.js 和 Playwright；不可用时需要记录失败原因。 |
| URD-ASM-006 | 被优化 skill 的目标任务通常能从 `SKILL.md`、用户目标、测试 prompt、输出样本或失败案例中推断。 |
| URD-ASM-007 | 用户愿意在领域评分标准进入正式优化前进行确认，除非显式关闭确认要求。 |
| URD-ASM-008 | 不同 agent runtime 暴露的研究工具不同，因此研究路径需要运行时探测或由用户提供。 |
| URD-ASM-009 | 用户可在低置信度研究或质量评估不合格时提供补充资料。 |
| URD-ASM-010 | 领域评分质量评估仍可能误判，因此关键结论需要记录理由和用户确认状态。 |

## 8. 待确认问题

| ID | 问题 | 影响 |
| --- | --- | --- |
| URD-Q-001 | `results.tsv` 是否应纳入仓库示例，还是只作为用户本地运行产物存在？ | 影响文档、示例和 `.gitignore` 设计。 |
| URD-Q-002 | 成果卡片 PNG 是否应作为每次优化的默认产物，还是只在用户要求展示时生成？ | 影响默认流程耗时和依赖要求。 |
| URD-Q-003 | README 中的手动 zip 安装路径是否需要扩展为多 runtime 路径表？ | 影响 runtime 中立性要求的公开呈现。 |
| URD-Q-004 | `docs/index.html` 是否作为发布页的唯一文档入口，还是需要链接到 `docs/URD.md` 等工程文档？ | 影响 docs 目录的信息架构。 |
| URD-Q-005 | 领域评分文件应放在被优化 skill 目录，还是放在 darwin-skill 的运行产物目录？ | 影响文件路径、版本管理和旧项目兼容。 |
| URD-Q-006 | `rubric_version` 应使用时间戳、内容哈希，还是语义版本？ | 影响冻结、复查和结果记录。 |
| URD-Q-007 | 用户选择跳过领域评分时，报告是否必须显示跳过原因？ | 影响报告格式和审计信息完整性。 |
| URD-Q-008 | `results.tsv` 是否继续作为主记录格式，还是新增 JSONL 结果文件以容纳扩展字段？ | 影响兼容读取和后续测试。 |
| URD-Q-009 | `research_version` 和 `evaluation_version` 应使用内容哈希、时间戳，还是与 `rubric_version` 共享同一版本规则？ | 影响研究、评分标准和质量评估之间的追踪。 |
| URD-Q-010 | 研究来源是否需要按权威资料、用户资料、项目文件、内部 skill 和模型知识分级打分？ | 影响 RQ2 的评分细则。 |
| URD-Q-011 | 低质量领域评分标准连续修订失败几次后提示用户人工介入？ | 影响自动修订次数和用户等待时间。 |
| URD-Q-012 | 领域研究和质量评估产物应存放在被优化 skill 目录，还是存放在 darwin-skill 的运行产物目录？ | 影响文件路径和多 skill 批量评估。 |

