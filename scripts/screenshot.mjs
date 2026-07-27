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
import { execSync } from 'child_process';
import { existsSync } from 'fs';
import path from 'path';
const require = createRequire(import.meta.url);

// 健壮解析 playwright / playwright-core：跨机器、跨平台，不硬编码任何用户路径
function loadPlaywright() {
  // 1) 标准解析（脚本目录或 NODE_PATH 里有的话）
  for (const m of ['playwright', 'playwright-core']) {
    try { return require(m); } catch {}
  }
  // 2) 动态定位全局 node_modules 并尝试候选路径
  const candidates = [];
  try {
    const groot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    candidates.push(path.join(groot, 'playwright-core'));
    candidates.push(path.join(groot, 'playwright'));
    // openclaw 等把 playwright-core 作为嵌套依赖的情况
    candidates.push(path.join(groot, 'openclaw', 'node_modules', 'playwright-core'));
  } catch {}
  for (const c of candidates) {
    if (existsSync(c)) { try { return require(c); } catch {} }
  }
  throw new Error(
    'playwright/playwright-core 未找到。请先安装：npm install -g playwright-core 且 npx playwright install chromium'
  );
}
const pw = loadPlaywright();

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

    await page.goto(`file://${htmlPath.replace(/\\/g,'/')}`, { waitUntil: 'networkidle' });

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

  // 自动打开图片（跨平台）
  try {
    if (process.platform === 'win32') {
      execSync(`start "" "${outputPath}"`);
    } else if (process.platform === 'darwin') {
      execSync(`open "${outputPath}"`);
    } else {
      execSync(`xdg-open "${outputPath}"`);
    }
  } catch {
    // 打不开也无妨，路径已打印
    console.log(`图片已保存: ${outputPath}`);
  }
}

screenshot().catch(err => {
  console.error('截图失败:', err.message);
  process.exit(1);
});
