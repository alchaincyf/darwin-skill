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
import { spawnSync } from 'child_process';
import { fileURLToPath, pathToFileURL } from 'url';
const require = createRequire(import.meta.url);

function loadPlaywright() {
  const candidates = ['playwright-core', 'playwright'];
  const errors = [];

  for (const packageName of candidates) {
    try {
      return require(packageName);
    } catch (error) {
      errors.push(`${packageName}: ${error.message}`);
    }
  }

  throw new Error(
    [
      'Cannot load Playwright.',
      'Install a project dependency with: npm install -D playwright',
      'Resolution errors:',
      ...errors.map(error => `- ${error}`),
    ].join('\n'),
  );
}

const pw = loadPlaywright();

const htmlPath = process.argv[2] || fileURLToPath(new URL('../templates/result-card.html', import.meta.url));
const outputPath = process.argv[3] || fileURLToPath(new URL('../templates/result-card.png', import.meta.url));

function openOutputImage(path) {
  if (process.env.DARWIN_SCREENSHOT_OPEN === '0') {
    return;
  }

  const commandByPlatform = {
    darwin: { command: 'open', args: [path] },
    win32: { command: 'cmd', args: ['/c', 'start', '', path] },
  };
  const commandSpec = commandByPlatform[process.platform] || { command: 'xdg-open', args: [path] };
  const result = spawnSync(commandSpec.command, commandSpec.args, { stdio: 'ignore' });

  if (result.error) {
    console.warn(`Could not open screenshot automatically: ${result.error.message}`);
  }
}

async function screenshot() {
  const browser = await pw.chromium.launch();

  try {
    const context = await browser.newContext({
      viewport: { width: 920, height: 1600 },
      deviceScaleFactor: 2,
    });

    const page = await context.newPage();

    await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle' });

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

  // 自动打开图片；设置 DARWIN_SCREENSHOT_OPEN=0 可关闭。
  openOutputImage(outputPath);
}

screenshot().catch(err => {
  console.error('截图失败:', err.message);
  process.exit(1);
});
