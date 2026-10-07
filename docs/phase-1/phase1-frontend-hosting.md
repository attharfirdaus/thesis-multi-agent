# Phase 1 — Free frontend hosting for a Next.js App Router app (SSR + auth cookies → external FastAPI on an Oracle VM)

Research date / access date: **2026-10-06** (the brief's access date). Method: primary provider pricing/docs/terms pages only, fetched this session; secondary sources used only as leads and marked. Every row carries the URL it came from. No recommendations are made here for the human to accept — the ranking at the end is a fit ordering with reasons, and the decision stays with Atthar.

Scope: hosting the **frontend only** (Next.js App Router, TypeScript, server components, route handlers/server actions, auth cookies) that talks over HTTPS to a FastAPI backend already hosted on an Oracle Cloud Always Free ARM VM. Backend/Postgres hosting is out of scope (see `phase1-hosting-free-tiers.md`).

Note on the date: the brief fixes today as 2026-10-06 and the repo's other phase-1 docs use that date. A few provider pages fetched this session carry their own self-updated stamps later than that (Netlify legal pages `last_updated: 2026-10-07`); where a page's own stamp matters it is quoted.

---

## 1. Vercel — Hobby

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | Yes — Vercel is the reference host for Next.js; App Router, server components, route handlers and server actions all run natively. No Next.js version range stated on the plan page. | https://vercel.com/docs/plans/hobby (`last_updated: 2026-09-14`) |
| 2 | Free-tier limits | 100 GB Fast Data Transfer, 10 GB Fast Origin Transfer, 1,000,000 CDN requests, 1,000,000 Function Invocations, **4 Active CPU-hrs**, 360 GB-hrs Provisioned Memory, 5,000 image transformations, 300,000 image-cache reads, 100,000 image-cache writes, 50,000 Web Analytics events/mo. 200 projects; 100 deployments/day; 45-min build cap; **1 concurrent build**; build machine 2 vCPU / 8 GB / 32 GB disk; 100 MB CLI source upload. Function memory/CPU: 2 GB / 1 vCPU (max = default); function max duration **300 s default and max** on Hobby. | https://vercel.com/docs/plans/hobby ; https://vercel.com/docs/limits (`last_updated: 2026-09-16`) |
| 3 | Cold start / sleep, logged-in users | Functions are stateless request/response and scale to zero; no persistent process. (Container functions idle 5 min in production scale down — from the existing backend doc's Vercel KB source.) A serverless-only model cannot hold an in-process session — the session must live in a cookie + the FastAPI backend or a DB. | https://vercel.com/docs/plans/hobby ; cross-ref `phase1-hosting-free-tiers.md` §1 |
| 4 | Custom domain + free TLS; previews | Yes — 50 domains/project, automatic TLS. Deployment Protection is available on Hobby (Vercel Authentication for **preview and production** deployments, Deployment Protection Exceptions, Shareable Links), so previews can be gated; by default a preview URL is reachable unless protection is enabled. | https://vercel.com/docs/plans/hobby |
| 5 | Commercial-use clause | **Quote (verbatim):** "Hobby teams are restricted to non-commercial personal use only. All commercial usage of the platform requires either a Pro or Enterprise plan." Definition: "Commercial usage is defined as any Deployment that is used for the purpose of financial gain of **anyone** involved in **any part of the production** of the project, **including a paid employee or consultant writing the code**." Also: "Asking for Donations **does not** fall under commercial usage." | https://vercel.com/docs/limits/fair-use-guidelines (`last_updated: 2026-09-14`) |
| 6 | Secrets / env vars; student text on host | Env vars per environment, max 1,000; total size 64 KB; values available at build and runtime. If a server component fetches submission text server-side, Vercel Functions process it on Vercel infrastructure. | https://vercel.com/docs/limits |
| 7 | Region / log retention | Functions run in a configurable region; CDN is global. Runtime logs: **1 hour** on Hobby (build logs stored indefinitely). | https://vercel.com/docs/plans/hobby ; https://vercel.com/docs/limits |

**Privacy (Vercel):** server-side fetch of student text is **avoidable** — do the fetch client-side (browser calls the FastAPI API, browser holds the session cookie) and the host never sees the text. Otherwise it is processed on Vercel.

---

## 2. Cloudflare — Workers (and Pages) via the OpenNext adapter

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | Yes. `@opennextjs/cloudflare` supports App Router, Route Handlers, dynamic routes, SSR, middleware, ISR, PPR, Pages Router, `'use cache'`, Turbopack. Node Middleware (Next 15.2) **not yet supported**. **Version range:** "All minor and patch versions of Next.js 16 and the latest minors of Next.js 14 and 15 are supported. Next.js 14 support will be dropped Q1 2026." Docs say use the **Node.js runtime**, not Edge (Edge is the older `@cloudflare/next-on-pages` path, and **`next-on-pages` is deprecated** — use OpenNext). | https://opennext.js.org/cloudflare ; https://github.com/cloudflare/next-on-pages/blob/main/README.md |
| 2 | Free-tier limits | Workers Free: **100,000 requests/day** (resets midnight UTC; 30-day… no — daily), **10 ms CPU time per invocation**, 128 MB memory/isolate, 50 subrequests/request, 6 simultaneous connections, 64 env vars × 5 KB, 20,000 static-asset files × 25 MiB, 100 Workers. Worker size: Cloudflare docs table says **64 MiB uncompressed (Free and Paid)**; the OpenNext page still says **3 MiB Free / 10 MiB Paid** (compressed) — **direct conflict, see Gaps**. Workers Builds Free: **3,000 build min/mo**, 1 concurrent build, 20-min build timeout, 2 vCPU / 8 GB. | https://developers.cloudflare.com/workers/platform/limits/ (`Last updated Sep 5, 2026`) ; https://developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing/ (`Last updated May 29, 2026`) ; https://opennext.js.org/cloudflare |
| 3 | Cold start / sleep, logged-in users | No scale-to-zero setting; isolate creation on a new PoP is the "cold start", Worker startup limit 1 s. Duration for HTTP-triggered Workers is **unlimited** while the client stays connected. Still stateless per request — session must live in a cookie + backend. CPU limit note (verbatim): "Heavier workloads that handle authentication, **server-side rendering**, or parse large payloads typically use **10-20 ms**" — i.e. above the 10 ms Free CPU cap; exceeding it returns **Error 1102** (`Worker exceeded resource limits`). | https://developers.cloudflare.com/workers/platform/limits/ |
| 4 | Custom domain + free TLS; previews | Yes — custom domains on Workers with platform TLS, free. Preview/version URLs are public by default. | https://developers.cloudflare.com/workers/platform/limits/ ; https://developers.cloudflare.com/workers/ (custom domains) |
| 5 | Commercial-use clause | **No non-commercial clause on the free plan.** The Self-Serve Subscription Agreement restricts §2.2.1 (no reselling, no circumventing quotas, no reverse-engineering, …) and §2.7 acceptable use (no infringement, no malware, no phishing, no illegal activity) — none bans commercial/academic use. One restriction worth noting: §2.2.1(h) "process or collect personal or business credit card information on any web property that is receiving **Free Services**" — not applicable here (no payments). Free Services are provided "AS IS" with "no liability" (§2.6). | https://www.cloudflare.com/terms/ (`Last Updated September 12, 2025`) |
| 6 | Secrets / env vars; student text on host | 64 env vars × 5 KB (Free). Secrets via `wrangler secret`. If a server component fetches submission text server-side, the Worker processes it on Cloudflare's edge; **avoidable** by client-side fetch. | https://developers.cloudflare.com/workers/platform/limits/ |
| 7 | Region / log retention | Runs on Cloudflare's global network (all PoPs). Workers Logs: Free = **200,000 log events/day, 3-day retention**. (Logpush is Paid-only.) | https://developers.cloudflare.com/workers/platform/pricing/ (`Last updated Oct 2, 2026`) |

**Pages vs Workers:** all Pages Functions are billed as Workers, and the Pages-specific Next.js path (`next-on-pages`, Edge-only) is deprecated in favour of OpenNext on Workers.

---

## 3. Netlify — Free

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | Yes. OpenNext-based adapter; the feature table marks App Router, SSR, ISR, SSG, React Server Components, Server Actions, Response Streaming, Route Handlers, Image Optimization, Middleware, Skew Protection as full support. **Version:** "Next.js 13.5+" (prior versions via a legacy runtime). | https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/ |
| 2 | Free-tier limits | **300 credits/month, hard limit, no auto-recharge** ("You'll never be charged for the Free plan"). Credit costs: production deployment 15 credits; functions/preview/DB compute 10 credits per GB-hour; web bandwidth 20 credits per GB; web requests 2 credits per 10,000. So 300 credits ≈ **15 GB bandwidth** *or* **30 GB-hours compute** *or* 20,000 production deploys (if spent only one way). 500 projects; 1 concurrent build; 1 Live Preview Server; deploy previews, branch deploys and failed deploys are **not** metered. | https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/ ; https://www.netlify.com/pricing/ |
| 3 | Cold start / sleep, logged-in users | Serverless functions — no persistent process; no documented idle-sleep value. Session must live in a cookie + the FastAPI backend. | https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/ ; https://www.netlify.com/pricing/ |
| 4 | Custom domain + free TLS; previews | Yes — custom domains with SSL; "Private by default until you publish"; **unlimited deploy previews**. | https://www.netlify.com/pricing/ |
| 5 | Commercial-use clause | **No non-commercial clause.** The Self-Serve Subscription Agreement does not restrict commercial use; the pricing page labels the Free plan "**Audience: Individual**". The material risk clause is §6: "Netlify's Free Usage Tier is made available ... at Netlify's sole discretion ... we reserve the right to disable or remove any website project on Netlify's Free Usage Tier **without notice** at our sole discretion ... Netlify may shut down Free Usage Tier website projects without notice for any reason or no reason." | https://www.netlify.com/legal/self-serve-subscription-agreement/ (page stamp `last_updated 2026-10-07`) ; https://www.netlify.com/pricing/ |
| 6 | Secrets / env vars; student text on host | Env vars supported. Shared env vars are Pro-only; per-project env vars exist on all plans. Server-side fetch → text processed on Netlify; **avoidable** client-side. | https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/ |
| 7 | Region / log retention | Global CDN. Real user monitoring / web analytics on Free: "Available for current/past day" only. | https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/ |

---

## 4. Render — Free web service

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | Yes — Render runs a real Node process (`next start` or a standalone `server.js`); no framework restriction. | https://render.com/docs/free ; https://render.com/docs/web-services |
| 2 | Free-tier limits | **512 MB RAM, 0.1 CPU** (Free compute plan). 750 Free instance hours/workspace/month (spun-down hours don't count); 5 GB outbound bandwidth/mo (Hobby, then $0.15/GB); 500 build-pipeline min/mo; up to 25 services; 2 custom domains (Hobby); no persistent disk on Free; no scaling beyond one instance; no shell access; no edge caching. | https://render.com/docs/free ; https://render.com/pricing |
| 3 | Cold start / sleep, logged-in users | **Quote:** "Render *spins down* a Free web service that goes **15 minutes** without receiving any inbound traffic ... This process takes about **one minute**." Ephemeral filesystem lost on spin-down/redeploy. A real long-running process while awake, but state in RAM is lost on the 15-min idle kill — session must live in a cookie + backend. | https://render.com/docs/free |
| 4 | Custom domain + free TLS; previews | Yes — custom domains, managed TLS certificates, service previews. | https://render.com/docs/free |
| 5 | Commercial-use clause | **No explicit non-commercial ban**, but two caveats. Docs: "Free instances have important limitations ... **Do not use them for production applications.**" Pricing page describes the Hobby tier as "For individuals building personal projects and prototypes." | https://render.com/docs/free ; https://render.com/pricing |
| 6 | Secrets / env vars; student text on host | Env vars and secret files supported on all plans. Server-side fetch → text processed on Render; **avoidable** client-side. | https://render.com/pricing |
| 7 | Region / log retention | Multiple global regions (Oregon, Ohio, Virginia, Frankfurt, Singapore) + CDN. Log retention: **7 days** (Hobby). | https://render.com/pricing |

---

## 5. Azure Static Web Apps — Free

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | Yes, via **"hybrid" Next.js** (preview): App Router, Pages Router, React Server Components, hybrid rendering, Route Handlers, image optimization, i18n, middleware, authentication. Key line: "**A managed backend is automatically available for every hybrid Next.js deployment in all plans.**" Bring-your-own backend (linked App Service) requires Standard. Not supported in hybrid preview: linked APIs (Azure Functions/App Service/Container Apps/API Management), SWA CLI emulation, navigation fallback, and ISR image caching. Max app size **250 MB** (use `output: 'standalone'`). | https://learn.microsoft.com/en-us/azure/static-web-apps/nextjs (`updated_at 2026-01-23`) ; https://learn.microsoft.com/en-us/azure/static-web-apps/deploy-nextjs-hybrid |
| 2 | Free-tier limits | 100 GB bandwidth/month per subscription; 500 MB total storage, 250 MB per environment; 15,000 file count; 3 preview environments; 2 custom domains/app; free SSL; request size limit 30 MB. Free-plan overage: "If your site exceeds these usage quotas, we will not be able to serve your site." | https://learn.microsoft.com/en-us/azure/static-web-apps/quotas (`updated_at 2026-09-28`) ; https://azure.microsoft.com/en-us/pricing/details/app-service/static/ |
| 3 | Cold start / sleep, logged-in users | Managed backend scales server-side; no documented idle-sleep value on the pages read. Stateless serverless model — session lives in a cookie + backend. | https://learn.microsoft.com/en-us/azure/static-web-apps/nextjs |
| 4 | Custom domain + free TLS; previews | Yes — 2 custom domains/app on Free, free SSL certificate. 3 preview environments (per-deployment URLs). | https://learn.microsoft.com/en-us/azure/static-web-apps/quotas |
| 5 | Commercial-use clause | **No non-commercial ban.** Pricing page frames Free as "For hobbies/personal projects" / "Free tier is intended for hobby/personal usage and does not come with SLA." Nothing prohibits an academic/commercial artefact. | https://azure.microsoft.com/en-us/pricing/details/app-service/static/ |
| 6 | Secrets / env vars; student text on host | App settings / env vars (GitHub Actions secrets + SWA settings). Server-side fetch → text processed on the Azure managed backend; **avoidable** client-side. | https://learn.microsoft.com/en-us/azure/static-web-apps/deploy-nextjs-hybrid |
| 7 | Region / log retention | Globally distributed static host; managed backend region not stated on the pages read. Log retention not documented. **Gaps.** | https://learn.microsoft.com/en-us/azure/static-web-apps/nextjs |

---

## 6. Firebase Hosting — Spark (no-cost)

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | **No on Spark.** Spark does not include Cloud Functions; the pricing table shows Cloud Functions "Not applicable" on Spark and lists "Access to Cloud Functions" as a **Blaze-only** feature. The Firebase Hosting "Integrate Next.js" doc only documents the **Pages Router** (`getStaticProps`/`getStaticPaths`/`getServerSideProps`) and deploys SSR logic to Cloud Functions for Firebase. App Router SSR is the job of **Firebase App Hosting**, which requires Blaze ("create a Firebase project and make sure it has the **Blaze pricing plan** enabled"). So: Spark = static export only. | https://firebase.google.com/docs/hosting/frameworks/nextjs (`Last updated 2026-10-06 UTC`) ; https://firebase.google.com/docs/projects/billing/firebase-pricing-plans ; https://firebase.google.com/docs/app-hosting |
| 2 | Free-tier limits (Spark) | Hosting storage 10 GB; **data transfer 360 MB/day** (≈10.8 GB/mo); custom domain & SSL; multiple sites per project. Cloud Functions (only on Blaze, card required): 2,000,000 invocations/mo, 400,000 GB-s, 200,000 CPU-s, 5 GB egress — all no-cost quotas on Blaze. Cloud Build free 120 min/day; Artifact Registry 500 MB free. | https://firebase.google.com/pricing ; https://firebase.google.com/docs/functions/faq-and-troubleshooting (`Last updated 2026-10-06 UTC`) |
| 3 | Cold start / sleep, logged-in users | Static hosting has no compute; SSR (Blaze) is Cloud Run-backed and scales to zero. No documented idle value. Session lives in a cookie + backend. | https://firebase.google.com/docs/app-hosting |
| 4 | Custom domain + free TLS; previews | Yes — custom domain & SSL on Spark; preview channels exist for Hosting. | https://firebase.google.com/pricing |
| 5 | Commercial-use clause | **Allowed.** Quote (Google support): "You can do whatever you want with Firebase, regardless of payment tier, as long as you adhere to the terms of service." | https://support.google.com/firebase/answer/9628313?hl=en |
| 6 | Secrets / env vars; student text on host | On Spark (static) the host never sees student text — there is no server-side render. On Blaze/App Hosting, Cloud Secret Manager + Cloud Run process it server-side; **avoidable** client-side. | https://firebase.google.com/docs/app-hosting |
| 7 | Region / log retention | Hosting is a global CDN; App Hosting deploys to Cloud Run in a chosen region. Logs via Cloud Logging; retention not stated on the pages read. **Gap.** | https://firebase.google.com/docs/app-hosting |

---

## 7. AWS Amplify Hosting

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | Yes, with caveats. "Amplify Hosting compute fully manages server-side rendering (SSR) for apps built with Next.js versions **12 through 15**" (16 not covered). Supported: SSR, SSG, API routes, dynamic/catch-all routes, ISR, i18n routing, middleware, env vars, image optimization, **Next.js 13 app directory**. **Unsupported:** Edge API routes / edge middleware, on-demand ISR, **Next.js streaming**, middleware on static assets/optimized images, `unstable_after` (Next 15). | https://docs.aws.amazon.com/amplify/latest/userguide/ssr-amplify-support.html |
| 2 | Free-tier limits | **Shape changed and is ambiguous.** Pricing page: build Standard instance no cost up to 1,000 build min/mo; data storage no cost up to 5 GB/mo; data transfer out no cost up to 15 GB/mo; SSR requests no cost up to 500,000/mo; SSR duration no cost up to 100 GB-hours/mo — and "Deploy an app **with AWS Free Tier: Free for 12 months**." A separate "News" block on the same page says new customers (from 2025-07-15) get "up to **$200 in AWS Free Tier credits**" and "a free plan ... available for **6 months** after account creation." Both statements are on the page; the exact current shape is **not reconcilable from this page alone** → Gaps. | https://aws.amazon.com/amplify/pricing/ (`meta-og:updated_time 2026-09-25`) |
| 3 | Cold start / sleep, logged-in users | Amplify Hosting compute (managed SSR) — serverless. No documented idle value. Session lives in a cookie + backend. | https://docs.aws.amazon.com/amplify/latest/userguide/ssr-amplify-support.html |
| 4 | Custom domain + free TLS; previews | Yes — "public SSL certificates at no additional cost"; multiple sites per project; branch-based preview deploys. | https://aws.amazon.com/amplify/pricing/ |
| 5 | Commercial-use clause | No non-commercial clause found. Standard AWS Free Tier conditions apply. | https://aws.amazon.com/amplify/pricing/ |
| 6 | Secrets / env vars; student text on host | Env vars supported in build settings. Server-side fetch → text processed on AWS; **avoidable** client-side. | https://docs.aws.amazon.com/amplify/latest/userguide/ssr-amplify-support.html |
| 7 | Region / log retention | Amplify Hosting serves globally; SSR compute region chosen. Log retention not stated. **Gap.** | https://aws.amazon.com/amplify/pricing/ |

---

## 8. Deno Deploy — Free

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | Yes. Deno Deploy is "Deno's serverless platform ... with first-class support for Deno and Node apps and frameworks like **Next.js**, Astro, and SvelteKit." No Next.js version range stated on the pages read. | https://docs.deno.com/runtime/deploy (`Last updated June 18, 2026`) ; https://deno.com/blog/nextjs-on-deno-deploy |
| 2 | Free-tier limits | 1,000,000 requests/month; 20 GiB egress/month; 5 custom domains; **10 hr active CPU**; 150 GiB-hr memory time; 10 GiB revision storage; 10 apps; 1 concurrent build; 15 builds/hour; KV 1 GiB (1M reads / 500K writes per month). | https://deno.com/deploy/pricing |
| 3 | Cold start / sleep, logged-in users | **Quote:** "Idle apps automatically shut down after **~20-30 seconds**, so you're not billed for memory while scaled to zero." Very short idle → frequent cold starts. Stateless — session lives in a cookie + backend. | https://deno.com/deploy/pricing |
| 4 | Custom domain + free TLS; previews | Yes — 5 custom domains on Free; platform handles TLS. | https://deno.com/deploy/pricing |
| 5 | Commercial-use clause | **Commercial use is acceptable.** Acceptable Use list includes "✅ Server-side rendered websites", "✅ A company website", "✅ An e-commerce site", "✅ A personal blog". Not acceptable: crypto mining, "❌ Highly CPU-intensive load (e.g. machine learning)", media hosting, scrapers, forward proxy, VPN. Free plan label: "For personal use and smaller projects." | https://docs.deno.com/deploy/acceptable_use_policy.md (`last_modified 2025-10-07`) |
| 6 | Secrets / env vars; student text on host | Env vars / secrets supported. Server-side fetch → text processed on Deno Deploy; **avoidable** client-side. | https://deno.com/deploy/pricing |
| 7 | Region / log retention | Global edge. Logs & traces retention: **1 day** on Free (Pro 1 week). App metrics history: 1 month. | https://deno.com/deploy/pricing |

---

## 9. Koyeb — Free instance

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | Yes — the docs give a Next.js guide ("using the app router") with git-driven buildpack deploys or a pre-built container; the example Dockerfile uses `output: 'standalone'` + `node server.js`. | https://www.koyeb.com/docs/deploy/nextjs (`Last updated May 27, 2026`) |
| 2 | Free-tier limits | **512 MB RAM, 0.1 vCPU, 2 GB SSD** (one Free web Service per organization). 100 GB outbound bandwidth/mo free. No Volumes / no persistent storage; no Worker Services; no custom scaling. Free Postgres (separate): 1 GB but only 5 h active. | https://www.koyeb.com/docs/reference/instances ; https://www.koyeb.com/docs/faqs/pricing |
| 3 | Cold start / sleep, logged-in users | "The Koyeb Free Instance automatically **scales down to zero when it doesn't receive any traffic for 1 hour**. Scale-to-zero ... cannot be disabled, and the idle period cannot be customized." Stateless once asleep — session lives in a cookie + backend. | https://www.koyeb.com/docs/run-and-scale/scale-to-zero |
| 4 | Custom domain + free TLS; previews | Custom domains + automatic TLS supported. | https://www.koyeb.com/docs/reference/instances |
| 5 | Commercial-use clause | No non-commercial clause found on the pages read. **A credit card is required even for the free instance** ("We require a credit card to prevent fraud and abuse"; $29 pre-auth hold). | https://www.koyeb.com/docs/faqs/pricing |
| 6 | Secrets / env vars; student text on host | Env vars/secrets supported. Server-side fetch → text processed on Koyeb; **avoidable** client-side. | https://www.koyeb.com/docs/deploy/nextjs |
| 7 | Region / log retention | Free instance regions: Frankfurt or Washington, D.C. only. Build logs stored 30 days; runtime log retention not documented. Partial **gap**. | https://www.koyeb.com/docs/reference/instances |

---

## 10. Fly.io — no free tier

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1–7 | — | **No free tier for new accounts.** Only a free trial: "2 hours of machine runtime or 7 days of access, whichever comes first"; trial machines auto-stop after 5 minutes. After the trial, apps stop until a payment method is added. Smallest always-on `shared-cpu-1x` 256 MB ≈ $2.19/mo, 1 GB ≈ $6.70/mo; outbound $0.02/GB. Container-native (you build the image). | https://fly.io/docs/about/free-trial ; https://fly.io/docs/about/pricing |

Cross-reference: the backend doc (`phase1-hosting-free-tiers.md` §2.4) already covers Fly.io; reproduced here only to close the frontend row.

---

## 11. GitHub Pages — static only (contrast row)

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | **None.** "GitHub Pages is a **static** site hosting service that takes HTML, CSS, and JavaScript files straight from a repository." There is no server runtime, so no server components, no route handlers, no server actions, no SSR. Only `output: 'export'` static export could ever be deployed. | https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages |
| 2 | Limits | Recommended source repo ≤ 1 GB; published site ≤ 1 GB; deployments time out after 10 minutes; soft bandwidth limit 100 GB/month; soft limit 10 builds/hour (not applied if built via a custom GitHub Actions workflow). | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits |
| 3 | Sleep | N/A (static). |
| 4 | Custom domain + TLS | Custom domain supported on `github.io` or your own domain; TLS via GitHub. |
| 5 | Commercial-use clause | **Quote (verbatim):** "GitHub Pages is **not intended for or allowed to be used as a free web-hosting service to run your online business, e-commerce site, or any other website that is primarily directed at either facilitating commercial transactions or providing commercial software as a service (SaaS)**." Also "shouldn't be used for sensitive transactions like sending passwords or credit card numbers." | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits |
| 6–7 | — | No server-side processing (privacy-friendly by construction), but unusable for this app. |

---

## 12. Oracle Cloud Always Free ARM VM — self-host the frontend (no-vendor baseline)

| # | Item | Finding | Source (accessed 2026-10-06) |
|---|---|---|---|
| 1 | App Router SSR support | Yes — full Node.js runtime. Build with `output: 'standalone'` and run `.next/standalone/server.js` (a minimal server that replaces `next start`); copy `public/` and `.next/static` into the standalone folder, or let a reverse proxy serve static assets. Any Next.js version Node supports. | https://nextjs.org/docs/app/api-reference/config/next-config-js/output |
| 2 | Limits | VM-level, not plan-level: the Always Free A1 allowance is **2 OCPU / 12 GB RAM / 200 GB block volume**, always-on; 10 TB/mo outbound free egress (per OCI's free-tier terms). No function-invocation, build-minute or credit caps. | https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm (page last modified 2026-06-12) ; cross-ref `phase1-hosting-free-tiers.md` §2.7 |
| 3 | Cold start / sleep | **None** — always-on VM. One caveat from OCI's own page: idle Always Free compute "may be reclaimed" if, over a **7-day period**, the 95th-percentile CPU, network **and** memory utilisation are all below 20% (A1 shapes). A live frontend plus the FastAPI backend keeps memory/CPU above that. | https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm |
| 4 | Custom domain + free TLS | Yes — a reverse proxy terminates TLS. **Caddy** is the lazy path: it "provisions TLS certificates for all your sites and keeps them renewed", obtaining publicly-trusted certificates from **Let's Encrypt and ZeroSSL** with no config; the Caddy README lists "ZeroSSL and Let's Encrypt for publicly-trusted certificates" and "Automatic HTTPS by default". Alternative: nginx + certbot (ACME/Let's Encrypt). | https://caddyserver.com/docs/automatic-https ; https://github.com/caddyserver/caddy/blob/master/README.md |
| 5 | Commercial-use clause | **None** — it is your VM; OCI's terms govern the account, not content. No academic/commercial restriction. | https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm |
| 6 | Secrets / env vars; student text on host | `.env` / systemd `Environment=` / a root-owned env file, or OCI Vault. **Best privacy option:** put the frontend on the *same VM* as the FastAPI backend and have server components fetch over `localhost` — student text then never leaves hardware you control. | https://nextjs.org/docs/app/api-reference/config/next-config-js/output |
| 7 | Region / log retention | OCI region chosen at signup (pick the nearest to Indonesia, e.g. Singapore). You own logs: systemd journal / Caddy access logs, retention is your choice (logrotate). No provider-side retention. | https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm |

**What the Oracle baseline actually requires (ops burden):**
1. Node.js 20+ LTS installed on the VM (or a container image).
2. `next build` with `output: 'standalone'`; run `node .next/standalone/server.js` (or a Docker container) under **systemd** so it restarts and starts on boot; copy `public/` + `.next/static`.
3. A **reverse proxy**: Caddy (one Caddyfile block → automatic Let's Encrypt/ZeroSSL TLS + HTTP→HTTPS redirect + renewal) or nginx + certbot.
4. **DNS** A/AAAA record for the frontend hostname → the VM's public IP.
5. **OCI firewall**: open 80/443 in the VCN security list *and* the VM's OS firewall (iptables/nftables).
6. **Ongoing ops**: OS security patches, Node/Next.js upgrades, renewal monitoring (Caddy automates it), watching the 7-day idle-reclamation signal, and the 200 GB block-volume ceiling (shared with the backend/DB). This is the price of "no vendor".

---

## Comparison table

Legend: **SSR** = App Router server components / route handlers / server actions actually run on the free tier. **ToS** = the free-tier commercial clause.

| Provider (free tier) | SSR on free tier? (Next.js versions) | Bandwidth / requests | Builds / concurrency | Idle behaviour (exact) | Custom domain + TLS; previews | Commercial-use clause (quote) | Student text on host? | Region / log retention | URL (accessed 2026-10-06) |
|---|---|---|---|---|---|---|---|---|---|
| **Vercel Hobby** | Yes (native; no version cap stated) | 100 GB transfer, 1M invocations, 4 CPU-hrs, 360 GB-hrs memory | 45 min/deploy, 1 concurrent, 100 deploys/day | Functions scale to zero; no persistent process | Yes (50 domains, auto TLS); Deployment Protection available for preview+prod | "Hobby teams are restricted to **non-commercial personal use only**." | Yes if server-fetch; avoidable client-side | Region configurable; **runtime logs 1 hour** | https://vercel.com/docs/plans/hobby ; https://vercel.com/docs/limits/fair-use-guidelines |
| **Cloudflare Workers (OpenNext)** | Yes (Next 16 all minors; latest minors of 14/15; 14 dropped Q1 2026) | 100,000 req/**day**; 10 ms CPU/invoke | 3,000 build min/mo, 1 concurrent | Isolate cold start (startup limit 1 s); no duration cap | Yes; preview URLs public by default | No non-commercial clause (SSA §2.2.1/§2.7) | Yes if server-fetch; avoidable client-side | Global edge; **logs 200k events/day, 3-day retention** | https://developers.cloudflare.com/workers/platform/limits/ ; https://opennext.js.org/cloudflare |
| **Netlify Free** | Yes (13.5+) | **300 credits/mo hard cap** ≈ 15 GB bandwidth *or* 30 GB-h compute *or* 20k deploys; requests 2 cr/10k | 1 concurrent build; previews/branch/failed deploys free | Serverless, no persistent process | Yes; "Private by default until you publish"; unlimited previews | No non-commercial clause; §6 "may shut down ... without notice at our sole discretion" | Yes if server-fetch; avoidable client-side | Global CDN; RUM/analytics current/past day | https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/ ; https://www.netlify.com/legal/self-serve-subscription-agreement/ |
| **Render Free** | Yes (Node runtime, no framework cap) | 5 GB bandwidth/mo; 750 instance-h/mo | 500 build min/mo | **Spins down after 15 min idle; ~1 min spin-up** | Yes; managed TLS; service previews | No ban, but "**Do not use them for production applications**"; Hobby = "personal projects and prototypes" | Yes if server-fetch; avoidable client-side | 6 global regions; **logs 7 days** | https://render.com/docs/free ; https://render.com/pricing |
| **Azure Static Web Apps Free** | Yes, hybrid (preview); managed backend in **all plans** | 100 GB/mo per subscription; 500 MB storage | GitHub Actions; 3 preview envs | Managed serverless; idle value not documented | Yes (2 domains, free SSL) | No ban; "intended for hobby/personal usage" | Yes if server-fetch; avoidable client-side | Global CDN; retention not documented | https://learn.microsoft.com/en-us/azure/static-web-apps/nextjs ; .../quotas |
| **Firebase Hosting Spark** | **No** — Spark has no Cloud Functions; SSR needs Blaze | 10 GB storage; **360 MB/day transfer** | n/a on Spark | Static (no compute) | Yes (custom domain + SSL) | Allowed: "You can do whatever you want with Firebase, regardless of payment tier..." | **No** (static) | Global CDN; retention n/a | https://firebase.google.com/pricing ; https://firebase.google.com/docs/projects/billing/firebase-pricing-plans |
| **AWS Amplify Hosting** | Yes (Next.js **12–15**; no streaming, no edge middleware, no on-demand ISR) | 15 GB/mo transfer; 500k SSR req/mo | 1,000 build min/mo | Serverless; idle value not documented | Yes; free public SSL | No ban found | Yes if server-fetch; avoidable client-side | Global; retention not documented | https://docs.aws.amazon.com/amplify/latest/userguide/ssr-amplify-support.html ; https://aws.amazon.com/amplify/pricing/ |
| **Deno Deploy Free** | Yes ("first-class support ... Next.js") | 1M req/mo; 20 GiB egress/mo; 10 hr active CPU | 1 concurrent, 15 builds/h | **Idle apps shut down after ~20–30 s** | Yes (5 domains) | Allowed: AUP lists "✅ Server-side rendered websites", "✅ A company website" | Yes if server-fetch; avoidable client-side | Global edge; **logs 1 day** | https://deno.com/deploy/pricing ; https://docs.deno.com/deploy/acceptable_use_policy.md |
| **Koyeb Free** | Yes (Node buildpack / standalone Docker) | 100 GB egress/mo | git-driven builds | **Scales to zero after 1 h idle (cannot disable)** | Yes | No ban found; **card required even for free** | Yes if server-fetch; avoidable client-side | Frankfurt or Washington DC only | https://www.koyeb.com/docs/deploy/nextjs ; https://www.koyeb.com/docs/reference/instances |
| **Fly.io** | No free tier (2 h / 7-day trial) | trial only | — | trial machines auto-stop after 5 min | Yes (paid) | n/a at $0 | n/a at $0 | — | https://fly.io/docs/about/free-trial |
| **GitHub Pages** | **No** (static only) | 1 GB site; 100 GB/mo soft | 10 builds/h (soft) | n/a | Yes (custom domain) | "**not intended for or allowed to be used** ... to run your online business, e-commerce site, or any other website ... providing commercial software as a service" | **No** (static) | Global CDN | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits |
| **Oracle Always Free ARM VM (self-host)** | Yes (full Node; `output: 'standalone'`) | VM-level; ~10 TB/mo egress free | your CI | **Always-on, no cold start** | Yes — Caddy auto TLS (Let's Encrypt/ZeroSSL); or nginx+certbot | No restriction (your VM) | **No — can stay on your VM** (fetch over localhost) | Your OCI region; you own logs | https://nextjs.org/docs/app/api-reference/config/next-config-js/output ; https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm ; https://caddyserver.com/docs/automatic-https |

---

## Privacy item — does the frontend host process student text?

The PRD sends pseudonymised submission text to a hosted LLM provider by design; the question here is only whether the **frontend host** also processes it. If a **server component** fetches submission text server-side (or a route handler proxies it), that text is processed on the host's infrastructure.

- **Avoidable, per host:** Vercel, Cloudflare, Netlify, Render, Azure SWA, Amplify, Deno Deploy, Koyeb, Fly — in every case. The alternative is a **client-side fetch**: the browser calls the FastAPI API directly (with CORS + the session cookie), so the SSR host only ever serves the app shell, JS and static assets and never sees student text. Cost: the text is rendered client-side, the session lives in the browser (cookie) and the FastAPI backend, and CORS must be opened from the frontend origin to the API.
- **Avoidable by placement:** Oracle VM — put the frontend on the **same VM** as the FastAPI backend and have server components fetch over `localhost`/the private network. Student text then never leaves hardware Atthar controls; this is the only option where SSR *and* privacy coexist without a client-side workaround.
- **Not applicable:** Firebase Spark and GitHub Pages — no server-side rendering at all on the free tier, so there is no server-side student-text path (they can only host a static shell; the text fetch would be client-side by construction).
- **If server-side fetch is kept:** the host joins the LLM provider as a second third party that touches pseudonymised student text; each host above states it retains operational logs (see the log column) but none of the free-tier pages read claims to train models on customer content. That claim would need its own verification if server-side fetch is chosen.

---

## Verdict: which free tiers permit a published thesis artefact?

"Published thesis artefact" = a public, non-paying, academic demonstration with no payments, no ads, no affiliate links. Against that:

- **Explicitly disallowed / risky:**
  - **Vercel Hobby** — the only hard clause: "non-commercial personal use only." An academic thesis with no revenue is very likely *personal, non-commercial*, and the fair-use page even says donations don't count. **But** the definition reaches "the purpose of financial gain of anyone involved in any part of the production of the project, **including a paid employee or consultant writing the code**." If the thesis is grant-funded, or a paid assistant writes any of the code, the clause is arguably triggered. **Read the clause, then decide — do not assume it is fine.**
  - **GitHub Pages** — disallowed for a "commercial software as a service" site; a research tool that is only demonstrated likely falls outside, but it cannot host SSR anyway, so it is moot.
- **Permitted with a hobby-flavoured intent but no prohibition:** Azure SWA Free, Render Free (with a "do not use for production" warning), Deno Deploy Free (AUP explicitly allows company sites and SSR), Firebase Spark ("do whatever you want ... regardless of payment tier"), Netlify Free (individual audience, no ban, but "shut down without notice" discretion), Cloudflare Workers (no non-commercial clause at all), AWS Amplify (no ban found), Koyeb (no ban found).
- **No restriction at all:** the Oracle VM baseline — it is your machine.

**Bottom line:** every provider except Vercel Hobby's clause and GitHub Pages' clause is *textually* permissive for a no-revenue academic artefact. Vercel Hobby is the single host whose written terms could bite, and only if money enters the project. Deno Deploy and Cloudflare are the cleanest *written* free tiers among the managed hosts (Deno's AUP explicitly blesses SSR and company sites); Oracle is the cleanest overall.

---

## Ranking by fit (reasons, not a decision — the pick is Atthar's)

1. **Oracle Always Free ARM VM (self-host).** Only option with zero ToS risk, zero cold start, no invocation/credit caps, and perfect privacy (frontend + backend on one VM, text over localhost). Cost: real ops burden (§12). Highest fit if the ops burden is acceptable.
2. **Azure Static Web Apps Free.** Best *managed* fit: hybrid Next.js SSR is "automatically available for every hybrid Next.js deployment in **all plans**", 100 GB/mo, 2 custom domains, no commercial clause. Caveats: hybrid support is **preview**, 250 MB app cap, and the free tier is framed as hobby.
3. **Deno Deploy Free.** Permissive AUP that explicitly allows SSR and commercial sites; 1M req/mo. Caveat: **~20–30 s idle shutdown** (frequent cold starts) and 10 hr active CPU.
4. **Cloudflare Workers (OpenNext).** No commercial clause, generous build/free log allowance, modern Next 16 support. **Caveat that dominates:** the Free plan's **10 ms CPU per invocation** vs the docs' own "SSR ... typically use 10–20 ms" — real SSR risk of Error 1102; effectively pushes you toward the paid plan for reliability.
5. **Netlify Free.** Best Next.js feature coverage (streaming, server actions) and it *is* an OpenNext host, but **300 credits/month** is tiny (~15 GB bandwidth) and §6 lets Netlify delete the project without notice.
6. **Render Free.** Simple, real Node process, familiar; but **512 MB / 0.1 CPU**, 15-min spin-down with 1-min wake, 5 GB bandwidth, and a documented "do not use for production."
7. **Vercel Hobby.** Best DX and native Next.js support; **ranked low only because of the non-commercial clause**, which is the one term a thesis artefact must be checked against.
8. **Koyeb Free.** Works, 100 GB egress, but 512 MB / 0.1 vCPU, 1-hour scale-to-zero, and a card is required even for free.
9. **AWS Amplify Hosting.** SSR works (Next 12–15) but the free-tier shape is unclear/time-limited and streaming is unsupported.
10. **Firebase.** Spark cannot do SSR at all; SSR means Blaze (card) or App Hosting.
11. **Fly.io.** No free tier.
12. **GitHub Pages.** Static only.

---

## Not verified / gaps

1. **Vercel Hobby — exact "commercial" boundary for a thesis.** The clause is quoted verbatim, but whether a funded or assistant-assisted thesis is "commercial" is a legal judgement, not a page fact. `[UNVERIFIED — requires Atthar's judgement, or a support ticket to Vercel (/help)]`.
2. **Cloudflare Worker size limit conflict.** Cloudflare's limits page says **64 MiB uncompressed (Free and Paid)** while the OpenNext docs page says **3 MiB Free / 10 MiB Paid** (compressed). Both fetched today. Which governs the OpenNext bundle is unresolved. `[CONFLICT]`
3. **Cloudflare Free 10 ms CPU and SSR.** The docs state SSR "typically use[s] 10-20 ms"; whether a *specific* OpenNext-built app exceeds 10 ms on Free is not stated. `[UNVERIFIED — must be measured on a real deploy]`.
4. **Azure SWA hybrid on the Free plan.** The tutorial lets you pick "Plan type: Free" and states the managed backend is "available ... in all plans", but hybrid is a **preview** feature and the pages do not state a Next.js version range. `[PARTIALLY VERIFIED]`.
5. **AWS Amplify free-tier shape.** The pricing page states both "Free for 12 months" (per-feature allowances) **and** the 2025-07-15 "$200 credits / 6-month free plan" programme. The two are not reconciled on the page. `[CONFLICT — verify in the Amplify console before relying on it]`.
6. **Render commercial terms.** The Acceptable Use page and Terms rendered as JS-only shells this session (only a heading returned); no explicit commercial clause was readable. The "do not use for production" line is from the Free docs, not from a commercial-use clause. `[UNVERIFIED]`.
7. **Firebase App Hosting / Blaze cost at $0.** App Hosting runs on Cloud Run + Cloud Build + Artifact Registry; the pricing table gives no-cost tiers (10 GiB/mo egress, 5 GB storage, 120 Cloud Build min/day), but exceeding them bills a card. Running SSR indefinitely at exactly $0 is not proven. `[UNVERIFIED]`.
8. **Azure SWA, AWS Amplify, Firebase log retention; Azure managed-backend region.** Not documented on the pages read. `[UNVERIFIED]`.
9. **Netlify function idle/sleep behaviour.** No idle-shutdown value is documented; only "serverless functions" is stated. `[UNVERIFIED]`.
10. **Deno Deploy Next.js version range.** No version range stated; only "first-class support ... frameworks like Next.js". `[UNVERIFIED]`.
11. **Cloudflare Pages future.** `next-on-pages` is deprecated in favour of OpenNext on Workers; whether Cloudflare Pages will keep a first-class Next.js path is not stated. `[UNVERIFIED]`.
12. **All prices/limits are provider-declared and change.** Several pages carry self-updated stamps (Vercel 2026-09-14/09-16; Cloudflare limits 2026-09-05, pricing 2026-10-02, builds 2026-05-29; Azure SWA quotas `updated_at` 2026-09-28; Firebase functions FAQ 2026-10-06; Netlify legal 2026-10-07). Re-verify before the defence.
