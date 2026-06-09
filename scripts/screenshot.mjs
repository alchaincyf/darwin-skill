#!/usr/bin/env node
/**
 * Darwin Skill - portable high-resolution screenshot script
 *
 * Usage:
 *   node scripts/screenshot.mjs [html-file-or-url] [output-png] [--selector=.card] [--open|--no-open]
 *
 * Features:
 * - 2x deviceScaleFactor for high-resolution output
 * - Captures a target element only (default: .card; fallback: .container)
 * - Waits for fonts and page rendering
 * - Uses project/local Playwright resolution instead of a hardcoded user path
 * - Falls back to common system Chrome/Edge executables when Playwright browsers are not installed
 */

import { createRequire } from 'node:module';
import { existsSync } from 'node:fs';
import { resolve, isAbsolute } from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const require = createRequire(import.meta.url);

function loadPlaywright() {
  const candidates = ['playwright', 'playwright-core'];
  for (const packageName of candidates) {
    try {
      return require(packageName);
    } catch (error) {
      if (error.code !== 'MODULE_NOT_FOUND') throw error;
    }
  }

  throw new Error(
    'Playwright is not installed. Install it in this repo with `npm install -D playwright` ' +
    'or run the script through an environment that already provides `playwright`/`playwright-core`.'
  );
}

function inputToUrl(input) {
  if (/^https?:\/\//.test(input) || input.startsWith('file://')) return input;

  const absPath = isAbsolute(input) ? input : resolve(process.cwd(), input);
  if (!existsSync(absPath)) {
    throw new Error(`HTML file does not exist: ${absPath}`);
  }
  return pathToFileURL(absPath).href;
}

function parseArgs(argv) {
  const options = {
    positional: [],
    selector: null,
    open: process.platform === 'darwin',
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--open') {
      options.open = true;
    } else if (arg === '--no-open') {
      options.open = false;
    } else if (arg === '--selector') {
      const selector = argv[i + 1];
      if (!selector || selector.startsWith('--')) {
        throw new Error('--selector requires a CSS selector value');
      }
      options.selector = selector;
      i += 1;
    } else if (arg.startsWith('--selector=')) {
      options.selector = arg.slice('--selector='.length);
      if (!options.selector) throw new Error('--selector requires a CSS selector value');
    } else if (arg.startsWith('--')) {
      throw new Error(`Unknown option: ${arg}`);
    } else {
      options.positional.push(arg);
    }
  }

  return options;
}

function findSystemChromium() {
  const candidates = [
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
    process.env.CHROME_EXECUTABLE_PATH,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/microsoft-edge',
  ].filter(Boolean);

  return candidates.find((candidate) => existsSync(candidate)) || null;
}

async function launchChromium(pw) {
  try {
    return await pw.chromium.launch();
  } catch (error) {
    const executablePath = findSystemChromium();
    if (!executablePath) throw error;

    console.warn(
      'Playwright-managed Chromium is unavailable; falling back to system browser: ' + executablePath
    );
    return pw.chromium.launch({ executablePath });
  }
}

async function findTarget(page, explicitSelector) {
  const selectors = explicitSelector ? [explicitSelector] : ['.card', '.container'];
  for (const selector of selectors) {
    const locator = page.locator(selector);
    if ((await locator.count()) > 0) {
      return { selector, locator: locator.first() };
    }
  }

  throw new Error(`Could not find target element. Tried: ${selectors.join(', ')}`);
}

const options = parseArgs(process.argv.slice(2));
const htmlPathOrUrl = options.positional[0] || new URL('../templates/result-card.html', import.meta.url).pathname;
const outputPath = resolve(process.cwd(), options.positional[1] || new URL('../templates/result-card.png', import.meta.url).pathname);
const pageUrl = inputToUrl(htmlPathOrUrl);
const pw = loadPlaywright();

async function screenshot() {
  const browser = await launchChromium(pw);

  try {
    const context = await browser.newContext({
      viewport: { width: 1100, height: 1800 },
      deviceScaleFactor: 2,
    });

    const page = await context.newPage();
    await page.goto(pageUrl, { waitUntil: 'networkidle' });

    await page.evaluate(() => document.fonts?.ready ?? Promise.resolve());
    await page.waitForTimeout(500);

    const { selector, locator } = await findTarget(page, options.selector);

    await locator.screenshot({
      path: outputPath,
      type: 'png',
    });

    const box = await locator.boundingBox();
    console.log(`Screenshot saved: ${outputPath}`);
    console.log(`Captured selector: ${selector}`);
    if (box) {
      console.log(`Element size: ${Math.round(box.width)}x${Math.round(box.height)}px (CSS)`);
      console.log(`Output size: ${Math.round(box.width * 2)}x${Math.round(box.height * 2)}px (2x)`);
    }
  } finally {
    await browser.close();
  }

  if (options.open) {
    try {
      execFileSync('open', [outputPath], { stdio: 'ignore' });
    } catch {
      // Opening is convenience-only; do not fail screenshot generation.
    }
  }
}

screenshot().catch((err) => {
  console.error('Screenshot failed:', err.message);
  process.exit(1);
});
