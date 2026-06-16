# Darwin Skill 2.0 用户需求文档

本文档根据当前仓库内容反推需求。依据文件包括 `SKILL.md`、`README.md`、`README_EN.md`、`test-prompts.json`、`references/skilllens-evidence.md`、`references/runtime-neutrality.md`、`templates/`、`scripts/` 和 `docs/index.html`。

## 1. 项目目标

| ID | 目标 |
| --- | --- |
| URD-GOAL-001 | 提供一个可安装的 Agent Skill，用于评估和改进其他 `SKILL.md` 文件。 |
| URD-GOAL-002 | 通过结构评分、效果验证、独立评审和用户确认，降低 skill 优化中的自评偏差和无效改动。 |
| URD-GOAL-003 | 让 skill 作者能看到每次优化的分数变化、测试依据、保留或回滚结果，并生成可展示的成果卡片。 |
| URD-GOAL-004 | 保持对多种 skills-compatible runtime 的中立描述，避免文档和流程绑定单一 agent 工具。 |

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

### 3.2 范围外

| ID | 范围外事项 |
| --- | --- |
| URD-OOS-001 | 不提供完整的独立 SaaS、Web 后端或数据库服务。 |
| URD-OOS-002 | 不自动发布或分发被优化后的第三方 skill。 |
| URD-OOS-003 | 不承诺 LLM judge 对细粒度质量差异完全可靠。 |
| URD-OOS-004 | 不在没有用户确认的情况下执行高风险 git 操作、远程推送或合并。 |
| URD-OOS-005 | 不把某一个 runtime 的私有能力作为唯一执行路径。 |

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

## 7. 假设

| ID | 假设 |
| --- | --- |
| URD-ASM-001 | 用户运行环境已经有支持 Agent Skills 的 agent runtime。 |
| URD-ASM-002 | 待优化 skill 以 `SKILL.md` 作为主要可编辑资产。 |
| URD-ASM-003 | 用户接受在关键节点暂停确认，而不是完全无人值守运行。 |
| URD-ASM-004 | git 可用，且项目位于可提交的仓库中；没有 git 时需要按异常表走备份或初始化流程。 |
| URD-ASM-005 | 成果卡片生成环境可运行 Node.js 和 Playwright；不可用时需要记录失败原因。 |

## 8. 待确认问题

| ID | 问题 | 影响 |
| --- | --- | --- |
| URD-Q-001 | `results.tsv` 是否应纳入仓库示例，还是只作为用户本地运行产物存在？ | 影响文档、示例和 `.gitignore` 设计。 |
| URD-Q-002 | 成果卡片 PNG 是否应作为每次优化的默认产物，还是只在用户要求展示时生成？ | 影响默认流程耗时和依赖要求。 |
| URD-Q-003 | README 中的手动 zip 安装路径是否需要扩展为多 runtime 路径表？ | 影响 runtime 中立性要求的公开呈现。 |
| URD-Q-004 | `docs/index.html` 是否作为发布页的唯一文档入口，还是需要链接到 `docs/URD.md` 等工程文档？ | 影响 docs 目录的信息架构。 |

