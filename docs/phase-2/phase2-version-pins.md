# Phase 2 — Version Pins, Compatibility Constraints, and Conflicts

Scope: exact versions to pin in a lockfile for the Next.js frontend and the FastAPI/LangGraph
backend on a single Oracle Cloud Always Free ARM64 (aarch64) VM behind Caddy. Local dev on
macOS arm64. No Docker anywhere.

Brief date: 2026-10-06. Every page below was retrieved on **2026-10-07** (the "accessed" column
records the brief's date with the actual retrieval date where they differ); two of the pinned
releases were published on 2026-10-06 UTC, hours before retrieval.

---

## 1. Pinned versions

| Component | Pin | Status / release schedule | Source URL | Accessed |
|---|---|---|---|---|
| Node.js (server + local) | **24.21.0** (LTS "Krypton") | Active LTS now; moves to **Maintenance LTS 2026-10-20**; EOL 2028-04-30. v26.10.0 is *Current*, not LTS (`"lts":false`); v26 becomes LTS 2026-10-28; v22.23.3 is Maintenance LTS (EOL 2027-04-30); v20 EOL 2026-03-24 | https://nodejs.org/dist/index.json · https://nodejs.org/en/about/previous-releases · https://raw.githubusercontent.com/nodejs/Release/main/schedule.json | 2026-10-06 (verified 2026-10-07) |
| Next.js | **16.4.0** (latest stable, published 2026-10-06T18:35Z) | 16.x line stable since 2025-10-22; requires Node ≥20.9.0, TypeScript ≥5.1.0, browsers Chrome/Edge/Firefox 111+, Safari 16.4+. Alternative with more soak time: **16.3.8** (2026-09-30) | https://registry.npmjs.org/next/latest · https://nextjs.org/docs/app/guides/upgrading/version-16 | 2026-10-06 (verified 2026-10-07) |
| React / React DOM | **19.3.0** (both; `react-dom` peer requires `react@^19.3.0`) | Stable since 2026-09-09. Next 16.4.0 peer range is `^18.2.0 \|\| ^19.0.0` → 19.3.0 satisfies | https://registry.npmjs.org/react/latest · https://registry.npmjs.org/react-dom/latest | 2026-10-06 (verified 2026-10-07) |
| @types/react, @types/react-dom | **19.3.0** | Matches React 19.3.0 | https://registry.npmjs.org/@types/react/latest · https://registry.npmjs.org/@types/react-dom/latest | 2026-10-06 (verified 2026-10-07) |
| TypeScript | **7.0.2** (latest stable, published 2026-07-08; `rc` tag is `7.0.1-rc`, no stable 7.0.0/7.0.1 on npm) | Next.js 16.4 documents first-class TS 7 usage (`next build` uses the project-local `tsc` CLI). Safe fallback: **5.9.3** (last 5.x, 2025-09-30) — Next minimum is 5.1.0 | https://registry.npmjs.org/typescript · https://nextjs.org/docs/app/api-reference/config/typescript | 2026-10-06 (verified 2026-10-07) |
| Tailwind CSS | **4.3.3** (published 2026-07-16) | v4 is the default for new projects; v3 branch still maintained as `v3-lts` → 3.4.19. v4 is CSS-first (`@theme`), needs modern browsers | https://registry.npmjs.org/tailwindcss/latest | 2026-10-06 (verified 2026-10-07) |
| @tailwindcss/postcss | **4.3.3** (must match `tailwindcss` exactly — it pins `tailwindcss":"4.3.3"`) | Required PostCSS plugin for Tailwind v4 in Next.js | https://registry.npmjs.org/@tailwindcss/postcss/latest | 2026-10-06 (verified 2026-10-07) |
| shadcn/ui CLI (`shadcn`) | **4.21.3** (published 2026-10-06T06:19Z) | CLI engine requires **Node ≥20.18.1** (stricter than Next). No declared Next.js peer range. Prior patch **4.21.2** (2026-10-05) | https://registry.npmjs.org/shadcn/latest · https://ui.shadcn.com/docs/installation/next | 2026-10-06 (verified 2026-10-07) |
| Python (interpreter to pin) | **3.13.16** (released 2026-09-30) | 3.13 is in **security-only** phase (bugfix ended when 3.14 shipped 2025-10-07); EOL 2029-10. 3.14.8 is the current bugfix (maintenance) release; 3.12.15 security; 3.10 hit **EOL 2026-10-01** | https://devguide.python.org/versions/ · https://www.python.org/api/v2/downloads/release/ | 2026-10-06 (verified 2026-10-07) |
| FastAPI | **0.142.2** (2026-09-30) | `requires-python >=3.10`; classifiers 3.10–3.14; requires `starlette>=0.46.0`, `pydantic>=2.9.0` | https://pypi.org/pypi/fastapi/json | 2026-10-06 (verified 2026-10-07) |
| Uvicorn | **0.54.0** (2026-09-25) | `requires-python >=3.10`; classifiers 3.10–3.14. `uvicorn[standard]` is what `fastapi[standard]` pulls in (uvloop, httptools, watchfiles, websockets) | https://pypi.org/pypi/uvicorn/json | 2026-10-06 (verified 2026-10-07) |
| Pydantic | **2.13.5** (2026-08-28) | `requires-python >=3.9`; classifiers 3.9–3.14; pins `pydantic-core==2.46.5` | https://pypi.org/pypi/pydantic/json | 2026-10-06 (verified 2026-10-07) |
| LangGraph | **1.2.14** (2026-10-06) | `requires-python >=3.10`, **classifiers stop at 3.13 (no 3.14)**. Pins `langchain-core<2,>=1.4.7`, `langgraph-checkpoint<5,>=4.1.0`, `langgraph-prebuilt<1.2,>=1.1.0`, `langgraph-sdk<0.5,>=0.4.6`. Prior patch 1.2.13 (2026-10-05) if you want one more day of soak | https://pypi.org/pypi/langgraph/json | 2026-10-06 (verified 2026-10-07) |
| langgraph-checkpoint-postgres | **3.1.2** (2026-08-07) | `requires-python >=3.10`; depends on `langgraph-checkpoint>=4.1.0,<5`, `psycopg>=3.2.0`, **`psycopg-pool>=3.2.0`**, `orjson>=3.11.5`. Resolves alongside `langgraph-checkpoint` 4.2.0 | https://pypi.org/pypi/langgraph-checkpoint-postgres/json | 2026-10-06 (verified 2026-10-07) |
| psycopg 3 | **3.3.6** (2026-09-18) | `requires-python >=3.10`; classifiers 3.10–3.15. Supported PostgreSQL 10–18. Extras: `binary`, `c`, `pool` | https://pypi.org/pypi/psycopg/json · https://www.psycopg.org/psycopg3/docs/basic/install.html | 2026-10-06 (verified 2026-10-07) |
| PostgreSQL server | **18.6** (major 18 released 2025-09-25) | Latest **stable** major. 19 is still beta (19 Beta 4, 2026-09-24). Supported majors: 18, 17, 16, 15, 14 (14 EOL 2026-11-12); 13 EOL 2025-11-13. Major 18 supported until 2030-11-14 | https://www.postgresql.org/support/versioning/ · https://www.postgresql.org/about/news/postgresql-19-beta-4-released-3386/ | 2026-10-06 (verified 2026-10-07) |
| uv | **0.12.23** (2026-10-03) | Standalone installer: `curl -LsSf https://astral.sh/uv/install.sh \| sh` (pin a version: `curl -LsSf https://astral.sh/uv/0.12.23/install.sh \| sh`). Self-updates via `uv self update` | https://docs.astral.sh/uv/getting-started/installation/ · https://api.github.com/repos/astral-sh/uv/releases/latest · https://pypi.org/pypi/uv/json | 2026-10-06 (verified 2026-10-07) |

---

## 2. Constraints and conflicts

**A. Python minor is capped by LangGraph, not by FastAPI/Pydantic.**
`langgraph` 1.2.14 and `langgraph-prebuilt` 1.1.0 both declare `Programming Language :: Python :: 3.10 … 3.13`
and no 3.14 classifier; their `requires-python` is an open `>=3.10` (no upper bound), so pip will *install*
them on 3.14 without error — nothing in the metadata stops you, but 3.14 is untested/undeclared by the
LangGraph packages. By contrast `langchain-core` 1.6.7 (LangGraph's own dependency) *does* declare 3.14,
and FastAPI 0.142.2, Pydantic 2.13.5 and Uvicorn 0.54.0 all declare 3.14. **The intersection of *declared*
support across the whole backend is 3.10–3.13.** → pin **3.13**, not 3.14, not 3.15.

**B. Python 3.15 must not be considered.** `https://www.python.org/downloads/release/python-3150/` returns
404 and the devguide lists 3.15 as *prerelease* (2026-10-01 is the planned 3.15.0 date, not a shipped one).
Only psycopg (10–3.15) and uv declare 3.15 at all. Also note 3.10 reached **end-of-life on 2026-10-01** —
one day before this brief — so the effective floor is 3.11/3.12, not 3.10, despite what `requires-python`
permits.

**C. Node floor is set by the shadcn CLI, not by Next.js.**
Next 16.4.0 `engines.node` is `>=20.9.0` (same as the upgrade guide's "Node.js 20.9+") and shadcn 4.21.3
`engines.node` is `>=20.18.1`. Node 20 is EOL, so any supported pin (22/24/26) clears both. **No conflict.**

**D. Node 24 LTS is about to leave Active LTS — this is the sharpest timing hazard.**
`nodejs/Release/schedule.json`: v24 Active-LTS → **Maintenance on 2026-10-20**, v26 → **LTS on 2026-10-28**.
Today the only Active LTS is 24; in three weeks it is not. Both remain supported (24 until 2028-04-30,
26 until 2029-04-30), and Next/shadcn accept both, so this is a *policy* decision, not a compatibility one.

**E. Tailwind v4 changes the shadcn setup path — yes.**
Tailwind v4 is CSS-first: no `tailwind.config.js`, theme lives under `@theme` / `@theme inline` in
`globals.css`, configuration goes through the `@tailwindcss/postcss` PostCSS plugin, and
`tw-animate-css` replaces `tailwindcss-animate`. shadcn ships v4-ready components (React 19 types,
`data-slot` attributes, no `forwardRef`, OKLCH colours, `sonner` instead of the deprecated `toast`).
With CLI 4.x this is the default for **new** projects — `npx create-next-app@latest` then
`npx shadcn@latest init` — so the migration steps shown on the Tailwind-v4 page apply only to
pre-existing v3 projects.

**F. `shadcn` CLI + Next version.** The CLI declares **no** `peerDependencies` and publishes no Next.js
version matrix; its docs target the App Router and explicitly instruct `npx create-next-app@latest`
(currently Next 16.4.0). So "which Next.js version does the CLI support" has no official answer —
[UNVERIFIED] no documented range exists; the CLI's only hard constraint is Node ≥20.18.1.
The CLI writes the project's own Next/React versions from `create-next-app`, so pin Next/React first
and let `shadcn init` follow.

**G. PostgreSQL on Ubuntu ARM64 — distro packaging is the gap, not the architecture.**
- Ubuntu 24.04 LTS (noble) main ships **only `postgresql-16`** (`16.15-0ubuntu0.24.04.1`; the
  `postgresql` metapackage depends on `postgresql-16`). `packages.ubuntu.com/noble/postgresql-17`
  and `/noble/postgresql-18` both answer a served "Package not available in this suite" page (the site
  returns HTTP 200 for that error page — status codes alone are misleading here). arm64 build exists
  (`postgresql-16_16.2-1ubuntu4_arm64.deb`).
- Ubuntu 26.04 LTS ("resolute") main ships **`postgresql-18`** (`18.6-0ubuntu0.26.04.1`), including
  arm64 (`postgresql-18_18.6-0ubuntu0.26.04.1_arm64.deb`).
- The **PostgreSQL APT repository** (PGDG) supports `resolute (26.04)`, `noble (24.04)`, `jammy (22.04)`
  and `stonking (26.10)` — and **arm64 only for LTS releases**, which covers both targets. So on 24.04
  you must add PGDG to get 18; on 26.04 the distro already gives 18.6.
- This matters because `psycopg` 3.3.6 declares PostgreSQL support **10–18** — PostgreSQL 19 (beta) is
  not yet in any supported-version matrix, so do not jump to 19.

**H. `psycopg[binary]` is safe on Ubuntu ARM64 — verified at the wheel level, not assumed.**
`psycopg-binary` 3.3.6 publishes `manylinux_2_27_aarch64.manylinux_2_28_aarch64` and
`musllinux_1_2_aarch64` wheels for **cp310, cp311, cp312, cp313, cp314 and cp315**. Ubuntu 24.04/26.04
glibc clears manylinux_2_28, so no compiler and no `libpq-dev` are needed.

**I. `pool` extra is redundant for this stack.** `langgraph-checkpoint-postgres` 3.1.2 depends on
`psycopg-pool>=3.2.0` directly, so the pool is installed transitively. Declare `psycopg[binary]`
(or `psycopg[binary,pool]` if you want the pool as a first-class, version-pinned direct dependency of
your own code).

**J. TypeScript 7 is the native (Go) compiler rewrite.** Next.js 16.4 documents it explicitly and
defaults to invoking the project-local `tsc` CLI; but TS 7 does not expose the JavaScript compiler API,
and `experimental.useTypeScriptCli` is required to fall back to the in-process checker. Anything in
your toolchain that imports the TS compiler API programmatically (some ESLint typed-lint setups,
codegen, `ts-node`-style loaders) may not work yet. `5.9.3` is the last 5.x if you need to retreat.

---

## 3. Answers to the six specific questions

1. **Python support.** LangGraph 1.2.14 and langgraph-prebuilt 1.1.0: `>=3.10`, classifiers 3.10–3.13 —
   **no 3.14**. FastAPI 0.142.2: `>=3.10`, classifiers 3.10–3.14. Pydantic 2.13.5: `>=3.9`,
   classifiers 3.9–3.14. Uvicorn 0.54.0: 3.10–3.14. langchain-core 1.6.7: 3.10–3.14.
   **Python 3.14 is mechanically usable** (open `requires-python`, no upper cap) but is **not declared by
   the LangGraph packages** → pin **3.12 or 3.13**; 3.13 is the recommendation.
2. **shadcn CLI vs Next.js.** No declared Next.js range (no `peerDependencies`, no published matrix)
   → [UNVERIFIED]. Docs target the Next.js App Router and scaffold via `create-next-app@latest` (Next
   16.4.0). CLI requires Node ≥20.18.1. **Tailwind v4 does change the setup path** (CSS-first `@theme`/
   `@theme inline`, `@tailwindcss/postcss`, no `tailwind.config.js`, `tw-animate-css` replacing
   `tailwindcss-animate`) — but it is the default for new projects, so a fresh `shadcn init` needs none of
   the manual migration steps on the Tailwind-v4 page.
3. **Node.js.** Active LTS today = **24 (Krypton)**; it enters Maintenance on **2026-10-20**, and 26
   becomes LTS on **2026-10-28** (26.10.0 is `"lts": false` today). Node 22 is already Maintenance.
   Next.js 16.4.0 requires `node >=20.9.0`; shadcn requires `>=20.18.1`.
4. **PostgreSQL.** Latest stable major = **18** (18.6); 19 is beta. Supported upstream: 18, 17, 16, 15,
   14 (14 goes EOL 2026-11-12). Ubuntu 24.04 LTS packages **16** only; Ubuntu 26.04 LTS packages **18.6**;
   the PGDG repo carries **18 for both, on arm64 (LTS releases only)**.
5. **uv.** `curl -LsSf https://astral.sh/uv/install.sh | sh`; current **0.12.23** (2026-10-03);
   version-pinned form `…/uv/0.12.23/install.sh`.
6. **psycopg 3.** **3.3.6**. Use the **`binary`** extra — aarch64 manylinux wheels exist for every
   Python you would pick (cp310–cp315), so no build toolchain on the VM. The **`pool`** extra is not
   required for this stack: `langgraph-checkpoint-postgres` already depends on `psycopg-pool>=3.2.0`.

---

## 4. Recommendation

**Pin Python 3.13 (3.13.16).**
It is the highest minor for which *every* backend component — LangGraph, langgraph-prebuilt,
langchain-core, FastAPI, Pydantic, Uvicorn, psycopg — declares support. 3.14 would work in practice
for FastAPI/Pydantic/psycopg but is undeclared by LangGraph itself, so it would make the thesis's core
orchestration library the one untested variable. 3.12 is equally safe and one year closer to EOL
(2028-10 vs 2029-10); take 3.13 for the longer runway. Any 3.13 lane also matches psycopg wheel
availability (`cp313` manylinux aarch64 confirmed).

**Pin Node 24 LTS (24.21.0).**
It is the only Active LTS today, it satisfies both Next 16.4.0 (`>=20.9.0`) and the shadcn CLI
(`>=20.18.1`), and it stays in LTS support until 2028-04-30. Node 24 goes to Maintenance on
2026-10-20, so **re-evaluate on/after 2026-10-28**: at that point Node 26 LTS is the newer Active LTS
and equally compatible, and moving to it then (before the Phase 2 skeleton accumulates code) is
cheaper than moving later. Do not pin 22 (Maintenance, EOL 2027-04) or 20 (EOL).

---

## 5. Flagged as too new / not yet safe

| Item | Why flagged | Safer alternative |
|---|---|---|
| **Next.js 16.4.0** | Published 2026-10-06T18:35Z — hours before retrieval | 16.3.8 (2026-09-30) if you want a soak period; 16.4.0 is otherwise a routine minor in a line stable since 2025-10-22 |
| **shadcn CLI 4.21.3** | Published 2026-10-06T06:19Z | 4.21.2 (2026-10-05) |
| **LangGraph 1.2.14** | Published 2026-10-06 | 1.2.13 (2026-10-05). Note the project ships near-daily patch bumps, so this is normal cadence rather than a red flag |
| **TypeScript 7.0.2** | The native-compiler rewrite; only stable 7.x on npm. Non-Next tooling that consumes the TS compiler API may lag | 5.9.3 (last 5.x, 2025-09-30) |
| **Python 3.15** | Not released — `python-3150` 404s, devguide shows *prerelease*; only psycopg/uv declare it | N/A — do not use |
| **PostgreSQL 19** | Beta only (19 Beta 4, 2026-09-24); psycopg 3.3.6 declares support for 10–18 | 18.6 |

---

## 6. Unverified / open

- **[UNVERIFIED]** shadcn CLI's supported Next.js version range — the package has no `peerDependencies`
  and the project publishes no compatibility matrix; only the Node engine (`>=20.18.1`) is declared.
- **[UNVERIFIED]** Whether LangGraph 1.2.14 actually runs on Python 3.14. Its metadata does not forbid it
  and `langchain-core` declares 3.14, but LangGraph drops its classifiers at 3.13, so this is untested by
  the maintainers as far as published metadata shows.
- **Conflict noted:** the psycopg docs site currently serves **3.3.7.dev1** docs while the stable PyPI
  release is **3.3.6**. Support statements (Python 3.10–3.15, PostgreSQL 10–18) were read from that dev
  doc; treat the upper bounds as one-patch-ahead of stable.
- **Conflict noted:** `packages.ubuntu.com` returns HTTP 200 for its "Package not available in this suite"
  page, so status codes alone do not establish package availability. Availability above was confirmed by
  matching page content and `.deb` filenames, not status codes.
