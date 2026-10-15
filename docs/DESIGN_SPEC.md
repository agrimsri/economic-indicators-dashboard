# Figma Design Specification (Extracted from Frame `1:2`)

## 1. Frame Geometry
- **Figma Canvas Dimensions:** 1248px × 2193px
- **Target Evaluation Viewport:** 1214px × 2159px
- **Layout Model:** Single-page fixed/responsive container, 2 columns × 3 rows grid
- **Column Gap:** 24px
- **Row Gap:** 24px
- **Page Background:** `#0B0F17` (Deep dark blue / near-black)
- **Header:** Height ~110px with candlestick chart overlay texture (`docs/reference/assets/image_Frame_2087327377_1_63.png`) and centered white title "ECONOMIC INDICATOR".

## 2. Market Ticker
- **Height:** ~48px
- **Background:** Semi-transparent dark navy with subtle border `#1F2937`
- **LIVE Badge:** Rounded pill with solid red background (`#D62C2A`), white text "LIVE", and pulsing red dot indicator.
- **Indices:** NIFTY 50, NIFTY BANK, NIFTY IT, SENSEX (BSE).
- **Format:** `SYMBOL  LAST_PRICE  (+PERCENT%)` (Green: `#69F6B8`, Red: `#FF716A`).
- **Interaction:** Continuous CSS marquee loop, pause on hover/focus, static list for `prefers-reduced-motion`.

## 3. Card Specifications (6 Cards)
- **Dimensions:** Width ~584px, Height ~540px
- **Card Background:** Glassmorphism navy gradient:
  `linear-gradient(180deg, rgba(7, 18, 42, 0.95) 0%, rgba(31, 51, 91, 0.85) 50%, rgba(0, 28, 92, 0.95) 100%)`
- **Border / Glow:** 1px solid `rgba(25, 181, 230, 0.35)` with subtle inner glow.
- **Top-left Fold:** Distinctive cut/folded white corner accent (`Vector 1624/1625`).
- **Header:** White bold title (`18.7px Segoe UI`, weight 600) with cyan qualifier in parentheses e.g. `(Y0Y%)` in `#0FCAF0`.

## 4. Typography
- **Primary Font Family:** `Segoe UI, -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif`
- **Heading Bold:** `Segoe UI`, 700 / 600, 36px (Page Header), 18.7px (Card Titles)
- **KPI Values:** `Segoe UI`, 600, 32px
- **KPI Labels:** `Segoe UI`, 600, 16px
- **Axis & Legends:** `Segoe UI` / `Roboto`, 400 / 500, 14px–15px
- **Delta Chips:** `Segoe UI`, 600, 14px

## 5. Color Palette & Tokens
- `--bg-page`: `#070C18`
- `--bg-card`: `linear-gradient(180deg, #07122A 0%, #101E3D 50%, #061533 100%)`
- `--border-card`: `rgba(15, 202, 240, 0.25)`
- `--text-primary`: `#FFFFFF`
- `--text-secondary`: `#A0AEC0`
- `--text-cyan`: `#0FCAF0`
- `--accent-india-blue`: `#0FB8E6`
- `--accent-world-orange`: `#FFA73F`
- `--accent-green-positive`: `#69F6B8`
- `--accent-red-negative`: `#FF716A`
- `--badge-live-red`: `#D62C2A`
- `--chart-yellow`: `#F4E15C`
- `--chart-grid`: `rgba(255, 255, 255, 0.08)`

## 6. Extracted Assets Index
All 3D card illustrations and flags exported to `docs/reference/assets/`:
- `image_image_945_1_77.png`: India Flag
- `image_image_944_1_307.png`: US Flag
- `image_image_951_1_91.png`: World Globe 3D Icon
- `image_image_954_1_218.png` & `image_955_1_227.png`: Exports / Imports 3D Art
- `image_image_959_1_251.png` & `image_957_1_261.png`: Inflation Basket / RBI Target 3D Art
- `image_image_960_1_423.png` & `image_958_1_429.png`: GST Coin Stack / Calendar 3D Art
- `image_image_952_1_452.png` & `image_953_1_458.png`: Revenue / Capital Expenditure 3D Art
- `image_Frame_2087327377_1_63.png`: Candlestick Header Background Art
