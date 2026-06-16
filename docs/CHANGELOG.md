# 文档变更记录

## 2026-06-16

- 更新 `docs/URD.md`，加入领域调查研究、领域评分标准质量评估、用户确认冻结、研究元数据、质量门槛和失败处理要求。
- 更新 `docs/TRACE.md`、`.vibe/trace.json` 和 `scripts/check_project_docs.py`，追踪 `URD-REQ-030` 到 `URD-REQ-049` 的新增需求。
- 更新 `docs/ADD.md`，将领域调查研究、领域评分标准质量评估和用户确认冻结纳入公理设计，形成 14 个 FR/DP 的下三角矩阵。
- 更新 `docs/TRACE.md` 和 `.vibe/coupling_history.json`，记录新增 URD 需求到 ADD 的映射和耦合处理结果。
- 更新 `docs/MDD.md`，按 14 个 ADD-DP 刷新模块、接口、数据结构和契约。
- 更新 `docs/TDD.md`，补充领域研究、领域评分标准质量评估、冻结门槛、报告输出和 14 个 MDD 接口契约测试。
- 更新 `docs/RMD.md`，按领域研究、评分标准生成、质量评估、冻结、评分决策和报告输出顺序刷新执行计划。
- 更新 `docs/TRACE.md`、`.vibe/trace.json`、`.vibe/doc_state.json`、`.vibe/update_log.json` 和 `scripts/check_project_docs.py`，同步 MDD/TDD/RMD 追踪关系。
- 更新 `docs/URD.md`，加入个体化领域评分标准生成、领域测试 prompt、领域评分记录、冻结机制、hard gates、兼容模式和验收标准。
- 更新 `docs/TRACE.md` 和 `.vibe/trace.json`，记录新增 URD 需求来源，并标出后续需要重新推导 ADD、MDD、TDD、RMD。
- 新增 `scripts/check_project_docs.py`，落实 TDD/RMD 中的项目文档检查。
- 修订 `README.md`、`README_EN.md` 和 `SKILL.md` 中的 runtime 路径表达，避免公开安装说明绑定单一 runtime。
- 更新 `docs/TDD.md` 和 `docs/RMD.md`，把检查命令改为 `python scripts\check_project_docs.py`。
- 新增 `docs/MDD.md`，把 ADD 设计参数转成模块、接口、数据结构和契约。
- 新增 `docs/TDD.md`，定义验收测试、接口契约测试、文档一致性检查和暂缓测试。
- 新增 `docs/RMD.md`，定义后续任务顺序、停止条件、回退点和本地检查清单。
- 新增 `.vibe/doc_state.json` 和 `.vibe/update_log.json`，记录文档状态和本次更新；未生成 wiki。
- 更新 `docs/TRACE.md` 和 `.vibe/trace.json`，补充 URD、ADD、MDD、TDD、RMD 之间的追踪关系。
- 新增 `docs/ADD.md`，根据 URD 做公理设计分析，形成下三角设计矩阵。
- 新增 `.vibe/coupling_history.json`，记录公理设计调整过程和耦合处理结果。
- 更新 `docs/TRACE.md`，补充 URD 需求到 ADD-FR/ADD-DP 的追踪关系。
- 新增 `docs/URD.md`，根据当前仓库内容反推 Darwin Skill 2.0 的用户需求、验收标准、约束、假设和待确认问题。
- 新增 `docs/TRACE.md`，记录需求、验收标准和来源文件之间的对应关系。
- 新增 `docs/PARKING_LOT.md`，保存未纳入当前 URD 的后续事项。
- 新增 `.vibe/trace.json`，保存机器可读的追踪摘要。
