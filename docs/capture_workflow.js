/* CraftProof workflow screenshot capture — v2 (card-scoped, two pieces).
 *
 * Walks the real app in headless Chrome through the complete product journey:
 *   maker login -> register piece -> QR tag -> transfer to gallery
 *   -> gallery login -> sell to external buyer -> publish checkpoint
 *   -> public certificate page -> how-it-works -> tamper demo
 *
 * Usage:  node capture_workflow.js
 * Output: ./screenshots/*.png   (and ./capture_meta.json)
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const BASE = 'http://localhost:5174';
const API = 'http://localhost:8002';
const OUT = path.join(__dirname, 'screenshots');

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function clickByText(page, selector, text) {
  const ok = await page.evaluate((sel, txt) => {
    const els = [...document.querySelectorAll(sel)];
    const el = els.find(e => e.innerText.trim().toLowerCase().includes(txt.toLowerCase()));
    if (el) { el.click(); return true; }
    return false;
  }, selector, text);
  if (!ok) throw new Error(`clickByText: no ${selector} containing "${text}"`);
}

// Click a button with an exact (trimmed, lowercased) label inside the card whose <h3> matches.
async function clickInCard(page, cardTitle, buttonText) {
  const ok = await page.evaluate((t, b) => {
    const cards = [...document.querySelectorAll('.card')];
    const card = cards.find(c => c.querySelector('h3') && c.querySelector('h3').innerText.includes(t));
    if (!card) return 'no card: ' + t;
    const btn = [...card.querySelectorAll('button')].find(x => x.innerText.trim().toLowerCase() === b.toLowerCase());
    if (!btn) return 'no button: ' + b;
    btn.click();
    return true;
  }, cardTitle, buttonText);
  if (ok !== true) throw new Error('clickInCard: ' + ok);
}

async function typeInto(page, selector, value) {
  await page.waitForSelector(selector, { timeout: 10000 });
  await page.evaluate(sel => { document.querySelector(sel).value = ''; }, selector);
  await page.click(selector);
  await page.type(selector, value, { delay: 10 });
}

async function selectOption(page, optionText) {
  await page.evaluate((txt) => {
    const sel = document.querySelector('select.select');
    const opt = [...sel.options].find(o => o.text.toLowerCase().includes(txt.toLowerCase()));
    if (!opt) throw new Error('option not found: ' + txt);
    const setter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
    setter.call(sel, opt.value);
    sel.dispatchEvent(new Event('change', { bubbles: true }));
  }, optionText);
}

async function shot(page, name) {
  await sleep(350);
  await page.screenshot({ path: path.join(OUT, name) });
  console.log('  ✓', name);
}

async function cardScreenshot(page, titleText, name) {
  const handles = await page.$$('.card');
  for (const h of handles) {
    const t = await h.evaluate(el => el.innerText);
    if (t.toLowerCase().includes(titleText.toLowerCase())) {
      await h.screenshot({ path: path.join(OUT, name) });
      console.log('  ✓', name, '(card)');
      return;
    }
  }
  throw new Error('card not found: ' + titleText);
}

async function login(page, email) {
  await page.goto(BASE + '/login', { waitUntil: 'networkidle0' });
  await typeInto(page, 'input[type=email]', email);
  await typeInto(page, 'input[type=password]', 'craftproof123');
  await clickByText(page, 'button', 'Sign In');
  await page.waitForFunction(() => location.pathname === '/dashboard', { timeout: 15000 });
  await sleep(900);
}

async function logout(page) {
  await clickByText(page, 'button', 'Logout');
  await sleep(500);
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=2'],
    defaultViewport: { width: 1440, height: 900, deviceScaleFactor: 2 },
  });
  const page = await browser.newPage();
  page.setDefaultTimeout(20000);

  const meta = { code: null, pieceId: null };

  // ---------- 1. Public landing page ----------
  console.log('STEP 1: landing page');
  await page.goto(BASE + '/', { waitUntil: 'networkidle0' });
  await shot(page, '01-landing.png');

  // ---------- 2. Maker logs in ----------
  console.log('STEP 2: maker login');
  await page.goto(BASE + '/login', { waitUntil: 'networkidle0' });
  await typeInto(page, 'input[type=email]', 'meera@example.com');
  await typeInto(page, 'input[type=password]', 'craftproof123');
  await shot(page, '02-login-filled.png');
  await clickByText(page, 'button', 'Sign In');
  await page.waitForFunction(() => location.pathname === '/dashboard');
  await sleep(900);
  await shot(page, '03-maker-dashboard.png');

  // ---------- 3. Register a new piece ----------
  console.log('STEP 3: register piece');
  const TITLE = 'Enamel-and-silver brooch';
  await clickByText(page, 'button', 'Register New Piece');
  await sleep(300);
  await typeInto(page, 'input[placeholder*="Hand-thrown"]', TITLE);
  await typeInto(page, 'input[placeholder*="Stoneware"]', 'Sterling silver, vitreous enamel');
  await typeInto(page, 'textarea', 'Enamelled in three firings; the copper underside is left bare so the maker\u2019s mark shows.');
  await shot(page, '04-register-piece-form.png');
  await clickByText(page, 'button', 'Create Digital Certificate');
  await page.waitForSelector('svg[id^="qr-"]', { timeout: 15000 });
  await sleep(500);
  meta.code = await page.evaluate(() => document.querySelector('svg[id^="qr-"]').id.replace('qr-', ''));
  await shot(page, '05-maker-dashboard-with-certificate.png');
  await cardScreenshot(page, TITLE, '06-piece-card-qr-tag.png');

  // ---------- 4. Maker transfers THE BROOCH to the gallery ----------
  console.log('STEP 4: transfer brooch to gallery');
  await clickInCard(page, TITLE, 'Transfer');
  await sleep(300);
  await selectOption(page, 'Kalakriti Gallery');
  await typeInto(page, 'input[placeholder*="craft fair"]', 'Delivered ahead of the autumn show');
  await shot(page, '07-transfer-form-filled.png');
  await clickInCard(page, TITLE, 'Confirm & Sign Transfer');
  await sleep(1000);
  await shot(page, '08-maker-dashboard-after-transfer.png');

  // ---------- 5. Gallery logs in ----------
  console.log('STEP 5: seller login');
  await logout(page);
  await login(page, 'priya@example.com');
  await shot(page, '09-gallery-dashboard.png');

  // ---------- 6. Gallery sells THE BROOCH to a buyer with no account ----------
  console.log('STEP 6: sell to buyer (no account)');
  await clickInCard(page, TITLE, 'Transfer');
  await sleep(300);
  // default option is "-- External Buyer (no account) --" so the Buyer's Name input shows
  await typeInto(page, 'input[placeholder*="John Doe"]', 'Jonathan Price');
  await typeInto(page, 'input[placeholder*="craft fair"]', 'Sold in store after the opening night');
  await shot(page, '10-sell-to-buyer-form.png');
  await clickInCard(page, TITLE, 'Confirm & Sign Transfer');
  await sleep(1000);
  await shot(page, '11-gallery-after-sale.png');

  // ---------- 7. Publish ledger checkpoint ----------
  console.log('STEP 7: publish checkpoint');
  await page.goto(BASE + '/ledger', { waitUntil: 'networkidle0' });
  await sleep(600);
  const pubBtn = await page.evaluateHandle(() => {
    const b = [...document.querySelectorAll('button')].find(x => x.innerText.toLowerCase().includes('publish a checkpoint'));
    return b || null;
  });
  if (pubBtn && pubBtn.asElement()) {
    await pubBtn.asElement().click();
    await sleep(1400);
  }
  await shot(page, '12-ledger-checkpoints.png');

  // ---------- 8. Public certificate page (the buyer's view) ----------
  console.log('STEP 8: public certificate page');
  await page.goto(`${BASE}/c/${meta.code}`, { waitUntil: 'networkidle0' });
  await sleep(700);
  await shot(page, '13-certificate-verified.png');
  // expand the plain-language explanation
  await clickByText(page, 'summary, .detail-toggle, span', 'How is this verified?');
  await sleep(400);
  await shot(page, '14-certificate-how-verified-expanded.png');

  // ---------- 9. How it works page ----------
  console.log('STEP 9: how it works');
  await page.goto(BASE + '/how-it-works', { waitUntil: 'networkidle0' });
  await sleep(500);
  await shot(page, '15-how-it-works.png');

  // ---------- 10. Tamper demo on the brooch's maker->gallery record ----------
  console.log('STEP 10: tamper demo');
  const cert = await (await fetch(`${API}/c/${meta.code}`)).json();
  meta.pieceId = cert.piece.id;
  const tamperNote = 'FORGED: bought at a discount store';
  const res = await fetch(`${API}/admin/tamper/${meta.pieceId}/1?new_note=${encodeURIComponent(tamperNote)}`, { method: 'POST' });
  console.log('  tamper response:', await res.json());
  await page.goto(`${BASE}/c/${meta.code}`, { waitUntil: 'networkidle0' });
  await sleep(700);
  await shot(page, '16-certificate-tampered.png');

  await browser.close();
  fs.writeFileSync(path.join(__dirname, 'capture_meta.json'), JSON.stringify(meta, null, 2));
  console.log('\nDONE. certificate code:', meta.code, 'piece id:', meta.pieceId);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
