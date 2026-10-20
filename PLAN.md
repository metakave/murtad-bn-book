# Native Mobile Reading Experience (PWA) Architecture & Tech Stack Plan

## 1. High-Level Requirements Overview
- **Target Experience:** Native iOS / Android reading feel (PWA with app shell, smooth scroll or swipe transitions, bottom safe-area padding, haptics, offline support).
- **Core Navigation:** Persistent bottom app bar with:
  1. **Home** (Book overview, book cover, stats, blurb, quick jump)
  2. **Continue Reading** (Auto-resumes exact scroll/chapter offset where user last left off)
  3. **Table of Contents (TOC)** (Chapter index, search within headings, estimated read time)
  4. **Profile** (User account/registration details, reading streaks/stats, font & theme customizations)
- **Reader Engine Features:**
  - Font size controls (A- / A+)
  - Line height & margin adjustments
  - Color themes: Clean Light, Sepia/Warm (great for reading), OLED Dark, Midnight Blue
  - Reading progress percentage bar & chapter indicator
  - Bengali typography optimization (Kalpurush / SolaimanLipi / Noto Serif Bengali via modern variable webfonts)
- **Content Pipeline:** PDF Source -> Python extraction & cleanup script -> Structured Chapter JSONs (Title, Chapter ID, Sections, Paragraphs) -> Bundled or preloaded.
- **User Registration & Storage:**
  - Free sign-up modal / lock gate before reading or on initial launch.
  - Option A: Cloudflare D1 (Serverless SQLite) + Cloudflare Workers via Pages Functions for 100% free Cloudflare stack.
  - Option B: Supabase (Auth + Postgres) or Firebase Auth with client-side localStorage fallback.
- **Hosting Target:** Cloudflare Pages (Fast global CDN, edge-rendered or static + Pages Functions).

---

## 2. Recommended Tech Stack

| Layer | Technology | Why It Fits |
|---|---|---|
| **Framework** | **Vite + React (or Preact / Vanilla/Alpine)** | Blazing fast build, zero-overhead client rendering, instant page transitions without browser page reloads. |
| **Styling** | **Tailwind CSS or Vanilla CSS Variables** | Native mobile touch gestures, smooth hardware-accelerated animations (`transform`, `opacity`), safe-area-insets (`env(safe-area-inset-bottom)`), zero jank. |
| **PWA Engine** | **Vite PWA (`vite-plugin-pwa`)** | Full offline support, service workers, web app manifest (`display: standalone`, iOS `apple-mobile-web-app-capable`). Looks & feels 100% like a native app when installed or opened. |
| **Typography** | **Google Fonts / Self-hosted Noto Serif Bengali or Hind Siliguri** | Clear rendering of conjuncts (যুক্তবর্ণ), optimal font weights for mobile screens. |
| **Data & State** | **Zustand / Nano Stores + LocalStorage / IndexedDB** | Instant sync for last reading position (scroll/chapter offset), theme preferences, offline caching. |
| **Backend & Auth (Cloudflare-Native)** | **Cloudflare Pages Functions + Cloudflare D1 or Supabase Auth** | Free tier is generous. No cold starts, runs on Cloudflare's edge alongside the static frontend. |
| **PDF Extraction** | **Python (`pypdf` / `pdfplumber` / `fitz`)** | Preserves Bengali Unicode characters, fixes decomposed Unicode / vowel marks (কার), formats into JSON chapters. |

---

## 3. Reader Experience & UI Blueprint

1. **Native App Shell:**
   - Fullscreen viewport (`viewport-fit=cover`, disabling double-tap zoom with `touch-action: manipulation`).
   - Header with discreet progress indicator + quick font/theme settings sheet.
   - Bottom Bar: Floating or fixed translucent blur bar (`backdrop-filter: blur(16px)`), designed around iOS home indicator and Android navigation gestures.

2. **Bengali Text Readability:**
   - Default serif font for prose with generous line-height (`leading-relaxed` / 1.7 - 1.9).
   - Justified / left-aligned text with hyphenation safeguards.
   - Preserved formatting for dialogue, verses, poetry, or footnote callouts.

3. **Gating / Registration Flow:**
   - Simple, frictionless registration (Name, Email / WhatsApp number, optional password or magic link / direct token).
   - Stores user token in local device storage so returning users never get re-prompted.

---

## 4. Implementation Phases

1. **Step 1: Ingest & Extract PDF**
   - Provide or upload the PDF into the project.
   - Run extraction script to verify Bengali Unicode fidelity and split chapters into `chapters.json`.
2. **Step 2: Initialize Web App**
   - Setup lightweight Vite + React/Vanilla PWA project.
   - Configure manifest, mobile meta tags, touch feedback, and fonts.
3. **Step 3: Core Reading & Navigation Engine**
   - Build Bottom Navigation (Home, Read, TOC, Profile).
   - Build Reader View (scroll sync, chapter switcher, font & theme controls, scroll-to-resume).
4. **Step 4: User Registration Flow**
   - Implement Registration modal/page with Edge API backend on Cloudflare Pages Functions.
5. **Step 5: Cloudflare Pages Deployment Setup**
   - Build optimization, headers configuration, and deployment ready commands (`wrangler` / GitHub action).
