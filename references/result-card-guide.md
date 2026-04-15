# 成果卡片生成指南

每个 skill 优化完成后（或全量汇总后），可选生成视觉成果卡片，截图保存为 PNG。

## 模板

模板位置：`templates/result-card.html`

3 种风格，每次随机选择一种：

| 风格 | CSS类 | URL hash | 视觉特点 |
|------|--------|----------|---------|
| Warm Swiss | `.theme-swiss` | `#swiss` | 暖白底+赤陶橙，Inter字体，干净网格 |
| Dark Terminal | `.theme-terminal` | `#terminal` | 近黑底+荧光绿，等宽字体，扫描线 |
| Newspaper | `.theme-newspaper` | `#newspaper` | 暖白纸+深红，衬线字体，双栏编辑风 |

## 生成流程

1. 复制 `templates/result-card.html` 到临时工作文件
2. 用编辑工具替换占位数据：
   - `data-field="skill-name"` → 实际 skill 名
   - `data-field="score-before/after/delta"` → 实际分数
   - 8 个维度的 `dim-bar-before/after` width → 实际百分比
   - `data-field="improvement-1/2/3"` → 实际改进摘要
   - `data-field="date"` → 当前日期
3. 随机选择风格：hash 设为 swiss/terminal/newspaper 之一
4. 用 Playwright 截图：
   ```
   npx playwright screenshot "file:///path/to/card.html#[theme]" \
     output.png --viewport-size=960,1280 --wait-for-timeout=2000
   ```
5. 提示用户查看成果卡片 PNG

## 何时生成

- **单 skill 卡片**：每个 skill 优化完成后
- **总览卡片**：全部优化完成后（Phase 3）

## 品牌元素

- 顶部：Darwin.skill 品牌标识 + 日期
- 底部：「Train your Skills like you train your models」+ github.com/alchaincyf/darwin-skill
