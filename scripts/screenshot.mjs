#!/usr/bin/env node
/**
 * Darwin Skill - 高清截图脚本
 *
 * 用法: node scripts/screenshot.mjs [html文件路径] [输出png路径]
 *
 * 特性:
 * - 2x deviceScaleFactor，输出高清图
 * - 只截 .card 元素，无多余背景
 * - 等待字体加载完成
 * - 截完自动用 open 命令打开图片
 */

import { createRequire } from 'module';
import { execFileSync } from 'child_process';
const require = createRequire(import.meta.url);

// 动态查找全局安装的 playwright-core
function loadPlaywrightCore() {
  // 1. 尝试 require.resolve 动态查找
  try {
    return require(require.resolve('playwright-core'));
  } catch (_) { /* not in local resolution paths */ }

  // 2. 尝试常见全局路径
  const candidates = [
    '/usr/local/lib/node_modules/playwright-core',
    '/usr/local/lib/node_modules/playwright/node_modules/playwright-core',
  ];

  // 3. 通过 npm root -g 获取全局 node_modules 路径
  try {
    const npmRoot = execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim();
    candidates.push(
      `${npmRoot}/playwright-core`,
      `${npmRoot}/playwright/node_modules/playwright-core`,
    );
  } catch (_) { /* npm not available */ }

  for (const p of candidates) {
    try { return require(p); } catch (_) { /* skip */ }
  }

  console.error(
    '错误: 找不到 playwright-core。\n' +
    '请确认已全局安装: npm install -g playwright\n' +
    '或设置 NODE_PATH 环境变量指向全局 node_modules。'
  );
  process.exit(1);
}

const pw = loadPlaywrightCore();

const htmlPath = process.argv[2] || new URL('../templates/result-card.html', import.meta.url).pathname;
const outputPath = process.argv[3] || new URL('../templates/result-card.png', import.meta.url).pathname;

async function screenshot() {
  const browser = await pw.chromium.launch();

  try {
    const context = await browser.newContext({
      viewport: { width: 920, height: 1600 },
      deviceScaleFactor: 2,
    });

    const page = await context.newPage();

    await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle' });

    // 等待字体加载
    await page.evaluate(() => document.fonts.ready);
    // 额外等待确保渲染完成
    await page.waitForTimeout(2000);

    // 只截 .card 元素
    const card = await page.locator('.card');
    await card.screenshot({
      path: outputPath,
      type: 'png',
    });

    console.log(`截图完成: ${outputPath}`);

    // 获取图片尺寸信息
    const box = await card.boundingBox();
    console.log(`卡片尺寸: ${Math.round(box.width)}x${Math.round(box.height)}px (CSS)`);
    console.log(`输出尺寸: ${Math.round(box.width * 2)}x${Math.round(box.height * 2)}px (2x高清)`);

  } finally {
    await browser.close();
  }

  // 自动打开图片
  execFileSync('open', [outputPath]);
}

screenshot().catch(err => {
  console.error('截图失败:', err.message);
  process.exit(1);
});
