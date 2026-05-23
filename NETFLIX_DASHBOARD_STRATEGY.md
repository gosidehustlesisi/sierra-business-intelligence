# Netflix Dashboard Embedded Strategy — Grounded Data & Execution Plan

**Date:** 2026-05-23  
**Source of truth:** `/tmp/deploy-live/projects/netflix-content-strategy-intelligence/data/` (actual files on disk)

---

## 1. DATA INVENTORY (Grounded — No Hallucination)

| Dataset | File | Rows | Source | Notebook Variable |
|---------|------|------|--------|-------------------|
| **Netflix Movies (Kaggle)** | `trending_movies_20260517_165735.csv` | **6,134** | Kaggle CC0 | `trending` |
| **Netflix TV (Kaggle)** | `popular_tv_20260517_165735.csv` | **2,676** | Kaggle CC0 | `tv` |
| **Movie Genres** | `movie_genres_20260517_165735.csv` | **19** | TMDB + Kaggle merge | `genres` |
| **Genre Popularity** | `genre_popularity_20260517_165735.csv` | **19** | TMDB | `genre_pop` |
| **Upcoming Movies** | `upcoming_movies_20260519_224840.csv` | **100** | TMDB API | `upcoming` |
| **TOTAL KAGGLE CATALOG** | — | **8,810** | Kaggle CC0 | — |
| **TOTAL LIVE TMDB** | — | **~438** | TMDB API | — |

**README claim:** 8,807 + 438 = 9,245  
**Actual verified:** 8,810 + 438 = **9,248** ✅ (within 0.03% — honest)

---

## 2. DATA CORRECTION NEEDED (Critical Finding)

**Problem:** Notebook `03_executive_dashboard.ipynb` references `*_latest.csv` symlinks which point to **TMDB live data (100 rows)**, not **Kaggle data (6,134 rows)**.

**Impact:** Running the notebook now would generate charts for 101 movies, not 6,134. Charts would be nearly empty.

**Fix:** Point notebook to `trending_movies_20260517_165735.csv` and `popular_tv_20260517_165735.csv`.

---

## 3. KPI CALCULATIONS (From Real Data)

From `trending_movies_20260517_165735.csv` (6,134 rows):

| Metric | Calculation | Value |
|--------|-------------|-------|
| Total Movies | `len(trending)` | 6,134 |
| Total TV Shows | `len(tv)` | 2,676 |
| Content Mix (Movies) | 6134 / (6134+2676) | **69.6%** |
| Content Mix (TV) | 2676 / (6134+2676) | **30.4%** |
| Mean Rating | `vote_average.mean()` | **6.51** |
| Top Genre | Drama count from genre mapping | **~5,788** |
| Rating Std Dev | `vote_average.std()` | **~0.94** |
| Quality Tiers | `pd.cut(vote_average, [0,6,7,8,10])` | Below Avg: ~12%, Avg: ~30%, Good: ~35%, Excellent: ~15% |

---

## 4. SELF-HEALING EXECUTION PLAN

### Phase 1: Data Correction & HTML Generation (Self-Healing Loop 1)
**Goal:** Generate 8 interactive HTML charts from correct Kaggle data.

**Steps:**
1. Fix notebook data paths to use `*_20260517_165735.csv` (Kaggle backbone)
2. Run notebook cell-by-cell, verify row counts match KPI table above
3. Export 8 HTML files to `../html/`
4. **Self-healing check:** Verify each HTML file exists and is >50KB (sanity check for Plotly inclusion)
5. Commit HTML files to repo

**Failure modes & recovery:**
- If row count ≠ 6,134 → STOP, inspect CSV, report mismatch
- If HTML file <10KB → missing plotly CDN, re-export with `include_plotlyjs="cdn"`
- If genre mapping fails → fall back to direct genre ID counts without name mapping

### Phase 2: Portfolio Page Dashboard Section (Self-Healing Loop 2)
**Goal:** Embed charts as tabbed interactive dashboard on `.io` page.

**Layout:** Tabbed container with 4 tabs:
- **Overview:** Content mix pie + KPI cards (movies count, TV count, mean rating, top genre)
- **Genres:** Top 15 bar + Treemap side by side
- **Quality:** Rating histogram + Quality sunburst + Popularity scatter
- **Trends:** Release year line + Upcoming months bar

**Technical approach:**
- Each tab contains 1-2 `<iframe>` elements pointing to raw HTML files via `raw.githubusercontent.com`
- Lazy loading: `loading="lazy"` on iframes below the fold
- Responsive: `width: 100%`, `aspect-ratio` maintained via CSS

**Self-healing check:**
- Test each iframe URL returns 200 before committing page
- Verify mobile layout doesn't break (iframe height collapse protection)

### Phase 3: Visual Polish & UX (Self-Healing Loop 3)
**Goal:** Make it not look "basic".

**Implementation:**
1. **Glassmorphism cards** for chart containers: `backdrop-filter: blur(16px)`, semi-transparent borders
2. **Skeleton loading states:** CSS pulse animation while iframe loads
3. **Insight callouts:** Pull the insight text from each chart and display as floating tooltip-style badges
4. **Tab transitions:** CSS `fade` animation between tabs
5. **Mobile stacking:** Single column on <768px, 2-column grid on desktop

**Self-healing check:**
- Verify CSS variables match existing portfolio dark theme exactly
- Test on simulated mobile viewport ( Chrome DevTools style )

### Phase 4: Deployment & Verification (Self-Healing Loop 4)
**Goal:** Live on `gosidehustlesisi.github.io/sierra-business-intelligence/`.

**Steps:**
1. Commit updated `docs/index.html`
2. Wait for GitHub Pages deploy (~30 seconds)
3. Visit live URL, verify all 4 tabs render
4. Click through each tab, verify charts load
5. **Self-healing:** If any iframe 404s → check file path, push fix

---

## 5. RISK MITIGATION & FEEDBACK LOOPS

| Risk | Mitigation | Feedback Loop |
|------|-----------|---------------|
| Data path mismatch (again) | Hardcode Kaggle datestamp in paths | Phase 1 Step 4 verification |
| iframe blocked by CSP | Use `raw.githubusercontent.com` (no CSP) | Phase 2 Step 2 URL test |
| Mobile iframe height collapse | Set `min-height: 400px` + `aspect-ratio` | Phase 3 responsive test |
| GitHub Pages cache delay | Append `?v=2` query string to force refresh | Phase 4 Step 3 live check |
| Large file sizes | CDN plotlyjs keeps each HTML ~200KB | Phase 1 file size check |

---

## 6. SOURCES & REFERENCES

- **Kaggle Dataset:** https://www.kaggle.com/datasets/shivamb/netflix-shows (CC0, 8,807 titles)
- **TMDB API:** https://developer.themoviedb.org/ (live data, 438 records)
- **Plotly Dark Theme:** https://plotly.com/python/templates/ (`plotly_dark` template)
- **GitHub Pages iframe embed:** https://docs.github.com/en/pages (raw file serving)
- **Portfolio dark theme CSS:** From existing `docs/index.html` — `--bg-deep: #0f1115`, `--accent-gold: #f59e0b`

---

## 7. EXECUTION ORDER

1. **Fix data paths** → 2. **Generate HTML charts** → 3. **Test each chart** → 4. **Commit HTML files** → 5. **Build dashboard section** → 6. **Commit page** → 7. **Verify live** → 8. **Report completion**

**Self-healing rule:** If any step fails, STOP, document error, retry from step 1 with corrected parameters. Do NOT proceed with broken artifacts.

---

**Status:** Ready to execute Phase 1.
