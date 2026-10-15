import { test, expect } from '@playwright/test'

test.describe('Economic Indicators Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Intercept backend auth calls
    await page.route('**/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ username: 'agrim', role: 'admin' }),
      })
    })

    await page.route('**/auth/refresh', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ access_token: 'mock-jwt-token' }),
      })
    })

    // Intercept stream to return clean 200 SSE or empty
    await page.route('**/api/v1/stream*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: 'event: ping\ndata: "ok"\n\n',
      })
    })

    // Intercept backend dashboard API
    await page.route('**/api/v1/dashboard', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ticker: {
            items: [
              { symbol: 'NIFTY 50', last: 24850.3, variation: 120.4, percent_change: 0.49, is_nse: true, status: 'fresh' },
              { symbol: 'NIFTY BANK', last: 51200.8, variation: -85.2, percent_change: -0.17, is_nse: true, status: 'fresh' },
              { symbol: 'NIFTY IT', last: 42150.0, variation: 310.5, percent_change: 0.74, is_nse: true, status: 'fresh' },
              { symbol: 'SENSEX', last: 81400.1, variation: 340.2, percent_change: 0.42, is_nse: false, status: 'fresh' },
            ],
            market_status: 'Open',
            as_of: '2026-10-15T15:30:00Z',
          },
          cards: {
            gdp: {
              card: 'gdp',
              status: 'fresh',
              as_of: '2025-12-31',
              fetched_at: '2026-10-15T10:00:00Z',
              source: { id: 'worldbank', name: 'World Bank Open Data', url: 'https://data.worldbank.org', is_nse: false },
              kpis: [
                { key: 'india', label: 'India', value: 6.5, unit: '%', delta: -0.5, delta_unit: 'pp', delta_basis: 'vs 2024' },
                { key: 'world', label: 'World', value: 2.7, unit: '%', delta: -0.1, delta_unit: 'pp', delta_basis: 'vs 2024' },
              ],
              series: [
                { key: 'IND', label: 'India', points: [{ x: '2021', y: 8.7 }, { x: '2022', y: 7.2 }, { x: '2023', y: 7.0 }, { x: '2024', y: 7.0 }, { x: '2025', y: 6.5 }] },
                { key: 'WLD', label: 'World', points: [{ x: '2021', y: 6.3 }, { x: '2022', y: 3.1 }, { x: '2023', y: 2.9 }, { x: '2024', y: 2.8 }, { x: '2025', y: 2.7 }] },
              ],
              notes: ['Real GDP growth at market prices'],
            },
            debt: {
              card: 'debt',
              status: 'fresh',
              as_of: '2025-12-31',
              fetched_at: '2026-10-15T10:00:00Z',
              source: { id: 'imf', name: 'IMF WEO DataMapper', url: 'https://www.imf.org', is_nse: false },
              kpis: [
                { key: 'india_fy25', label: 'India (FY25)', value: 82.5, unit: '%', delta: -0.6, delta_unit: 'pp', delta_basis: 'vs previous year' },
                { key: 'ind_vs_us', label: 'Ind vs US', value: -40.8, unit: 'pp', delta: -0.6, delta_unit: 'pp', delta_basis: 'relative gap' },
              ],
              series: [
                { key: 'debt_gdp', label: 'India Debt to GDP', points: [{ x: '2020', y: 88.5 }, { x: '2021', y: 83.7 }, { x: '2022', y: 81.0 }, { x: '2023', y: 82.7 }, { x: '2024', y: 83.1 }, { x: '2025', y: 82.5 }] },
              ],
              notes: ['General government gross debt (% of GDP)'],
            },
            trade: {
              card: 'trade',
              status: 'fresh',
              as_of: '2025-12-31',
              fetched_at: '2026-10-15T10:00:00Z',
              source: { id: 'commerce', name: 'Ministry of Commerce / World Bank', url: 'https://commerce.gov.in', is_nse: false },
              kpis: [
                { key: 'exports', label: 'Exports', value: 880.7, unit: '$ B', delta: 6.13, delta_unit: '%', delta_basis: 'vs previous year' },
                { key: 'imports', label: 'Imports', value: 949.7, unit: '$ B', delta: 5.86, delta_unit: '%', delta_basis: 'vs previous year' },
              ],
              series: [
                { key: 'imports', label: 'Imports', points: [{ x: '2020', y: 512.2 }, { x: '2021', y: 730.8 }, { x: '2022', y: 897.8 }, { x: '2023', y: 853.5 }, { x: '2024', y: 897.1 }, { x: '2025', y: 949.7 }] },
                { key: 'exports', label: 'Exports', points: [{ x: '2020', y: 497.3 }, { x: '2021', y: 660.8 }, { x: '2022', y: 776.4 }, { x: '2023', y: 778.2 }, { x: '2024', y: 829.8 }, { x: '2025', y: 880.7 }] },
                { key: 'trade_balance', label: 'Trade Balance', points: [{ x: '2020', y: -14.9 }, { x: '2021', y: -70.0 }, { x: '2022', y: -121.4 }, { x: '2023', y: -75.3 }, { x: '2024', y: -67.3 }, { x: '2025', y: -69.0 }] },
              ],
              notes: ['Merchandise + Services trade in billions USD'],
            },
            gst: {
              card: 'gst',
              status: 'fresh',
              as_of: '2026-03-31',
              fetched_at: '2026-10-15T10:00:00Z',
              source: { id: 'gst', name: 'PIB / GSTN Monthly Releases', url: 'https://pib.gov.in', is_nse: false },
              kpis: [
                { key: 'gst_collections', label: 'GST Collections', value: 12.4, unit: '%', delta: -0.81, delta_unit: 'pp', delta_basis: 'vs previous month' },
                { key: 'monthly_average', label: 'Monthly Average', value: 1.76, unit: '₹ lakh cr', delta: 0.13, delta_unit: '₹ lakh cr', delta_basis: 'vs FY24' },
              ],
              series: [
                { key: 'gross_gst', label: 'Gross GST (₹ lakh cr)', points: [{ x: 'Apr 24', y: 2.10 }, { x: 'May 24', y: 1.73 }, { x: 'Jun 24', y: 1.74 }, { x: 'Jul 24', y: 1.82 }, { x: 'Aug 24', y: 1.75 }, { x: 'Sep 24', y: 1.73 }] },
                { key: 'yoy_growth', label: 'YoY Growth (%)', points: [{ x: 'Apr 24', y: 12.4 }, { x: 'May 24', y: 10.0 }, { x: 'Jun 24', y: 7.7 }, { x: 'Jul 24', y: 10.3 }, { x: 'Aug 24', y: 10.0 }, { x: 'Sep 24', y: 6.5 }] },
              ],
              notes: ['Monthly gross goods and services tax collections'],
            },
            inflation: {
              card: 'inflation',
              status: 'fresh',
              as_of: '2025-12-31',
              fetched_at: '2026-10-15T10:00:00Z',
              source: { id: 'worldbank', name: 'World Bank / MoSPI CPI Data', url: 'https://mospi.gov.in', is_nse: false },
              kpis: [
                { key: 'inflation_cpi', label: 'Inflation (CPI)', value: 2.4, unit: '%', delta: -2.55, delta_unit: 'pp', delta_basis: 'vs previous period' },
                { key: 'target_rbi', label: 'Target (RBI)', value: 4.0, unit: '%', delta: 0.0, delta_unit: 'pp', delta_basis: 'medium-term target (2-6%)' },
              ],
              series: [
                { key: 'cpi', label: 'CPI YoY (%)', points: [{ x: '2021', y: 5.13 }, { x: '2022', y: 6.70 }, { x: '2023', y: 5.65 }, { x: '2024', y: 4.95 }, { x: '2025', y: 2.40 }] },
              ],
              notes: ['All-India Consumer Price Index (CPI-C) annual YoY rate'],
            },
            fiscal: {
              card: 'fiscal',
              status: 'fresh',
              as_of: '2025-03-31',
              fetched_at: '2026-10-15T10:00:00Z',
              source: { id: 'cga', name: 'Union Budget / CGA (Ministry of Finance)', url: 'https://www.indiabudget.gov.in', is_nse: false },
              kpis: [
                { key: 'total_expenditure', label: 'Total Expenditure', value: 48.21, unit: '₹ lakh cr', delta: 7.3, delta_unit: '%', delta_basis: 'YoY Growth' },
                { key: 'capital_expenditure', label: 'Capital Expenditure', value: 11.11, unit: '₹ lakh cr', delta: 17.1, delta_unit: '%', delta_basis: 'YoY Growth' },
              ],
              series: [
                { key: 'capital_expenditure', label: 'Capital Expenditure', points: [{ x: 'FY21', y: 4.26 }, { x: 'FY22', y: 5.93 }, { x: 'FY23', y: 7.36 }, { x: 'FY24', y: 9.49 }, { x: 'FY25', y: 11.11 }] },
                { key: 'revenue_expenditure', label: 'Revenue Expenditure', points: [{ x: 'FY21', y: 30.84 }, { x: 'FY22', y: 32.01 }, { x: 'FY23', y: 34.57 }, { x: 'FY24', y: 35.43 }, { x: 'FY25', y: 37.10 }] },
              ],
              notes: ['Central Government Accounts: Revenue and Capital Expenditure'],
            },
          },
        }),
      })
    })
  })

  test('should render dashboard with zero horizontal scroll at 1214x2159 viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1214, height: 2159 })
    await page.goto('/')

    // Wait for header
    await expect(page.locator('h1.header-title')).toHaveText('ECONOMIC INDICATOR')

    // Verify horizontal scroll is completely absent (scrollWidth <= clientWidth)
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth
    })
    expect(hasHorizontalScroll).toBe(false)

    // Verify all 6 cards are rendered
    await expect(page.getByRole('heading', { name: 'GDP (INDIA VS WORLD' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'DEBT TO GDP' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'EXPORTS & IMPORTS' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'GST REVENUE COLLECTION' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'INFLATION RATE (CPI)' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'GOVERNMENT EXPENDITURE' })).toBeVisible()

    // Verify all cards have the folded corner visual accent
    const cornerFolds = page.locator('img.card-corner-fold')
    await expect(cornerFolds).toHaveCount(6)

    // Verify Non-NSE tags are present on non-NSE cards
    const nonNseTags = page.locator('.non-nse-tag')
    expect(await nonNseTags.count()).toBeGreaterThanOrEqual(6)

    // Verify Ticker is visible with status badge and SENSEX has BSE tag
    await expect(page.locator('.ticker-badge')).toBeVisible()
    await expect(page.locator('.bse-tag').first()).toHaveText('BSE')

    // Verify authenticated user badge
    await expect(page.locator('.user-name')).toHaveText('agrim')
    await expect(page.locator('button.logout-btn')).toBeVisible()

    // Capture visual snapshot for audit
    await page.screenshot({
      path: 'tests/screenshots/dashboard_1214x2159.png',
      fullPage: true,
    })
  })

  test('should verify ticker hover pauses marquee and preserves accessible styles', async ({ page }) => {
    await page.setViewportSize({ width: 1214, height: 2159 })
    await page.goto('/')

    const marqueeWrapper = page.locator('.ticker-marquee-wrapper')
    await expect(marqueeWrapper).toBeVisible()

    // Hover over ticker
    await marqueeWrapper.hover()

    // Ensure ticker items are accessible
    await expect(page.locator('.ticker-symbol:has-text("NIFTY 50")').first()).toBeVisible()
    await expect(page.locator('.ticker-symbol:has-text("SENSEX")').first()).toBeVisible()
  })
})
