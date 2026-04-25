const fs = require('fs');
const { chromium } = require('playwright');

async function main() {
  const url = process.argv[2];
  if (!url) {
    throw new Error('Missing URL');
  }

  const pageErrors = [];
  const consoleErrors = [];
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1900 }, deviceScaleFactor: 1 });

  page.on('pageerror', (error) => {
    pageErrors.push(String(error && error.message ? error.message : error));
  });

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  const response = await page.goto(url, { waitUntil: 'networkidle' });
  const status = response ? response.status() : null;

  const result = await page.evaluate(() => {
    const firstParagraph = document.querySelector('p');
    const pageEl = document.querySelector('.page');
    const images = ['qimage-1.png', 'qimage-2.png', 'qimage-3.png'].map((name) => {
      const img = Array.from(document.images).find((node) => node.getAttribute('src') === name);
      return {
        name,
        found: Boolean(img),
        complete: Boolean(img && img.complete),
        naturalWidth: img ? img.naturalWidth : 0,
        naturalHeight: img ? img.naturalHeight : 0
      };
    });

    return {
      title: document.title,
      fontSize: firstParagraph ? getComputedStyle(firstParagraph).fontSize : null,
      pageClientHeight: pageEl ? pageEl.clientHeight : null,
      pageScrollHeight: pageEl ? pageEl.scrollHeight : null,
      docScrollHeight: document.documentElement.scrollHeight,
      images
    };
  });

  const overflow = result.pageClientHeight !== null && result.pageScrollHeight !== null
    ? result.pageScrollHeight > result.pageClientHeight
    : null;

  const summary = {
    status,
    loadedWithoutBlockingIssues: status === 200 && pageErrors.length === 0,
    fontSize: result.fontSize,
    images: result.images,
    overflow,
    pageClientHeight: result.pageClientHeight,
    pageScrollHeight: result.pageScrollHeight,
    docScrollHeight: result.docScrollHeight,
    pageErrors,
    consoleErrors
  };

  console.log(JSON.stringify(summary, null, 2));
  await browser.close();
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
