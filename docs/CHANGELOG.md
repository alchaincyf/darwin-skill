# 文档变更记录

## 2026-06-16

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
