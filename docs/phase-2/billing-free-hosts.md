# Hosting a free FastAPI/LangGraph API on a card-free account — provider report

**Section owner:** `RenderBillingReality` (Render only)
**Date:** 2026-10-14 (UTC+7). Every claim below was fetched today unless a capture date is stated.
**Other sections:** append below this one rather than overwriting (co-edited file).

---

# RENDER — can a brand-new account deploy a free web service with no card and no billing details?

## Direct answer

**Yes for the documented free path, and no for the flow this project actually tried.**

- A brand-new account can, per Render's own documentation, deploy a **free web service** (Docker included) with **no payment method, no card, and no billing details**. Render's signup form (observed live today) has **no card or billing-address field at all** — it asks for GitHub/GitLab/Bitbucket/Google, or email + password, plus hCaptcha.
- But **a Blueprint is a different story, and the difference is documented**: in a `render.yaml`, if you omit the `plan` field, Render provisions a **paid** `0.5c-512mb` instance. Render's public API returns **HTTP 402 "You must enter payment information to perform this request."** for that create. That is almost certainly what your owner hit: "Blueprint creation demanded billing information" is the expected product behaviour for a Blueprint that does not explicitly say `plan: free` on every service.
- **The honest framing:** the marketing/docs say "no card" and are correct about *free instances*; the product asks for a card the moment anything in the request is **paid** — and a Blueprint silently defaults to paid. This is not marketing lying; it is a default that is invisible unless you read the Blueprint spec's "If you omit this field" list.

---

## 1. Does creating a Blueprint (New → Blueprint) require a payment method or billing details?

**No payment or billing step is documented anywhere in Render's Blueprint flow.** The complete documented setup, verbatim from [render.com/docs/infrastructure-as-code](https://render.com/docs/infrastructure-as-code) (accessed 2026-10-14):

> 1. Create an empty YAML file in your repository where you'll define your Blueprint's resources.
> 2. Populate your Blueprint file with the details of the resources you want to create and manage.
> 3. Commit and push your changes to your Git provider.
> 4. Open the Render Dashboard and click *New > Blueprint*:
> 5. In the list that appears, click the *Connect* button for whichever repo contains your Blueprint.
> 6. In the form that appears, specify a name for your Blueprint and which branch of your repo to link.
> 7. If needed, specify a custom file path to your Blueprint's YAML file in the *Blueprint Path* field.
> 8. Review the list of the changes that Render will apply based on the linked Blueprint:
> 9. If everything looks correct, click *Deploy Blueprint*.

Nine steps, zero mention of a payment method, card, or billing information. **However**, this doc says nothing about *what plans* a Blueprint requests. That is where the requirement actually comes from:

[render.com/docs/blueprint-spec](https://render.com/docs/blueprint-spec), field `plan` (accessed 2026-10-14), verbatim:

> *If you omit this field:*
>
> - Render uses `0.5c-512mb` for a new web service, private service, background worker, or cron job.
> - Render uses `256mb` for a new Key Value instance.
> - Render retains the current compute plan for an existing service.

`0.5c-512mb` is the **$7/month paid** plan ([render.com/pricing](https://render.com/pricing), Compute table, accessed 2026-10-14: "Less than 1 CPU | $7/month | 512 MB RAM | `0.5c-512mb`"). `256mb` is the **$10/month** Key Value plan. So a Blueprint that omits `plan` (or `plan: free`) asks Render to create **paid resources**, which is exactly the request that triggers the payment gate.

**Verbatim user report that matches this exactly** — [GitHub, Chameleon-company/Planting-Optimisation-Tool issue #442](https://github.com/Chameleon-company/Planting-Optimisation-Tool/issues/442), opened **2026-04-17**, by `leecopland`:

> "The project Render account cannot use the render.yaml blueprint for deployment, a limitation of the free-tier on render. Docker-based web services (pot-backend) require a paid plan on Render - free tier only supports native runtimes (Node, Python, etc.). **Blueprint deployment also requires a card on file.**"

> "At present, services are created and managed only manually through the Render dashboard. render.yaml currently serves as documentation only."

Caveat on this source (see §5): it also contains a factually wrong claim (Docker web services *do* support the free compute plan per [render.com/docs/free](https://render.com/docs/free), which lists "Web services (web apps in Node.js, Python, Rails, etc.)" and notes "Other service types don't support Free instances" — Docker is a runtime, not a service type). So treat the card sentence as **evidence, not authority**: it is a first-hand 2026 report, and it happens to match the documented `plan` default.

## 2. Does creating a Web Service by hand (New → Web Service) require the same? Is there a documented difference?

**Documented difference: yes — the plan source, and therefore the card.**

- **Manual flow:** you pick the compute plan in the wizard. [render.com/docs/your-first-deploy](https://render.com/docs/your-first-deploy) (accessed 2026-10-14), verbatim: "*This tutorial uses free Render resources. No payment is required.* All you need is a repository connected to a supported Git provider with the web app you want to deploy." Under "Compute": "Choose the *Free* compute plan to deploy for free".
- [render.com/docs/free](https://render.com/docs/free) step 4: "During the service creation flow, you choose a *compute plan* for your service (unless it's a static site). Choose *Free*".
- **Blueprint flow:** you do not pick a plan in the UI. The plan comes from `render.yaml`, and its default is paid (`0.5c-512mb`, quoted above). Omit the field → paid request → payment-required.

Nothing in Render's docs states that the Blueprint *UI* differs from the manual *UI* in payment handling. The observable difference is the **resource plan being requested**, not the flow's payment step. Both flows hit the same server-side gate: Render's public OpenAPI declares a shared `402PaymentRequired` response on service creation and modification, and on other paid operations (see §3).

**Second, undocumented-but-plausible difference:** a Blueprint can create several resources in one click (e.g. a Postgres database and a Key Value instance alongside the web service). Each of those has its own plan default, so a mixed Blueprint can request paid datastores even when the web service is `free` — again producing a card prompt that the manual single-service flow would not produce.

## 3. What does Render mean by "billing information"? Is there a name/address-without-card step? When does a card become required?

**"Billing information" in Render's product = a payment method on file (a credit/debit card, stored and processed by Stripe). There is no documented name-and-address-only mode.**

- [render.com/pricing](https://render.com/pricing) FAQ, accessed 2026-10-14, verbatim: "**Which payment methods do you accept?** We accept all major credit and debit cards. Your payment info is stored and processed securely by [Stripe](https://stripe.com/) and never touches our servers."
- There is **no** Render docs page for billing or payment methods: `https://render.com/docs/billing` → HTTP 404; `https://render.com/docs/payment-methods` → HTTP 404 (both checked 2026-10-14). Billing is documented only as a Dashboard section — [render.com/docs/render-dashboard](https://render.com/docs/render-dashboard): "View and update your plan / **Update your payment method** / View accrued usage charges for the current billing month / View invoices for past months". No field list is published, so a non-card "billing details" step cannot be confirmed from Render's docs either way.
- **Where the card is required, by contract:** [render.com/terms](https://render.com/terms), "Payment Method Requirements", verbatim: "You must maintain a current, valid payment method on file with Render **at all times during your use of any paid aspects of the Service**." The phrase "any paid aspects" is the whole rule: unpaid/free aspects are excluded.
- **The pre-authorisation hold, verbatim** ([render.com/terms](https://render.com/terms), "Card Verification"): "Render or its payment processor may place a temporary authorization hold of up to one U.S. dollar ($1.00) on your payment method, which hold shall be released or cancelled and shall not result in an actual charge. In addition, **as an abuse prevention measure**, Render may periodically initiate a test authorization on your payment method in an amount up to your estimated usage charges for the applicable billing period." Matching FAQ entry: "**Why was I charged $1 after adding a credit card?** A $1 USD transaction is performed as a credit security check to ensure your card details are correct and authorized. The charge is refunded after the transaction completes."

**Answer in timeline form:**

| Point in lifecycle | Card required? | Evidence |
| --- | --- | --- |
| Signup | **No.** Signup page has no card field | `https://dashboard.render.com/register` observed live 2026-10-14: fields are GitHub / GitLab / Bitbucket / Google, or "Email", "Password", plus hCaptcha ("This site is protected by hCaptcha") |
| First workspace | **No.** Created automatically on the free plan | [render.com/docs/team-members](https://render.com/docs/team-members): "When you sign up for Render, we automatically create your first workspace on the free *Hobby* plan." |
| Deploying a **free** instance (web service / static site / free Postgres / free Key Value) | **No.** | [render.com/docs/your-first-deploy](https://render.com/docs/your-first-deploy): "No payment is required." |
| Deploying a **paid** instance (any non-`free` plan, incl. a Blueprint default) | **Yes.** HTTP 402 | `https://api-docs.render.com/openapi/render-public-api-1.json` (fetched 2026-10-14): `"402PaymentRequired":{"description":"You must enter payment information to perform this request."…}` |
| Creating an **additional** workspace on a paid plan | **Yes** | [render.com/docs/team-members](https://render.com/docs/team-members): "Complete the workspace creation flow, including specifying a plan type and payment method. Then click *Create Workspace*." (Render plans give Hobby accounts exactly 1 workspace per [render.com/pricing](https://render.com/pricing), so an additional workspace is inherently paid) |
| Adding a persistent disk, dedicated IP, registry credential, custom domain beyond the 2 included | **Yes** (same 402 response) | OpenAPI `402` declared on `POST /dedicated-ips`, `POST /registrycredentials`, `PATCH /registrycredentials/{registryCredentialId}`, `POST /services/{serviceId}/custom-domains` |
| Upgrading a free service to paid | **Yes** | same 402 on `PATCH /services/{serviceId}` |

**Exact 402 surface, verified by parsing today's spec (not from memory):** `POST /services`, `PATCH /services/{serviceId}`, `POST /services/{serviceId}/custom-domains`, `POST /dedicated-ips`, `POST /registrycredentials`, `PATCH /registrycredentials/{registryCredentialId}`. **No `402` is declared on `POST /postgres`, `POST /key-value`, or on any `/blueprints*` path** — the only Blueprint endpoints in the public API are `GET /blueprints`, `POST /blueprints/validate`, and `GET/PATCH/DELETE /blueprints/{blueprintId}` + `/syncs`; there is no public "create Blueprint" endpoint, so the Blueprint create gate is only reachable through the dashboard and is not specified in the API contract. Treat "does a Blueprint *always* demand a card" as **[UNVERIFIED]** (see gaps).

The spec also exposes an account-level **spend-authorization** concept tied to paid plans, with verbatim enum descriptions: "The plan needs a spend authorization and no payment method is on file." / "The plan needs a spend authorization the requester has not accepted." / "The owner's card declined the spend authorization." (error codes `preauth_no_payment_method`, `preauth_consent_required`, `preauth_declined`). This is consistent with "card required for *plans*", not for free instances.

**What happens *without* a card if you exceed free allowances** — [render.com/docs/faq](https://render.com/docs/faq), verbatim: "**All of my services run on free instances. Can I still be billed?** *Yes, if you've added a payment method.* … If you haven't added a payment method and you would incur charges, Render instead disables your services for the duration of the current billing period." Same rule in [render.com/docs/free](https://render.com/docs/free): "If you haven't added a payment method, Render instead suspends all of your Free services for the remainder of the month." **So a cardless account can never be surprised with a charge — it gets suspended instead.** This is the safest possible failure mode for a zero-budget thesis deployment, but it means a bandwidth/pipeline overage takes the API offline until month end.

## 4. Anti-fraud / account verification / acceptable use / region-specific rules

- **The only automated verification observed at signup is hCaptcha** (live check of `https://dashboard.render.com/register`, 2026-10-14: "This site is protected by hCaptcha. Its Privacy Policy and Terms of Service apply."). No phone number, ID document, or address step is requested.
- **Render's AUP contains no card, identity-verification, or KYC requirement** ([render.com/acceptable-use](https://render.com/acceptable-use), rendered text, 2026-10-14). Its relevant clauses: "Bypass Access or Usage Restrictions: Attempt to bypass, circumvent, or defeat any access or usage restrictions, authentication, or security measures…"; "Abuse Network Resources or Service Capacity: … especially for the purpose of evading payment or financial obligations"; and "We reserve the right to investigate any suspected violation of this Acceptable Use Policy … You agree to cooperate fully with us in any investigation or enforcement action … including providing information and taking any remedial actions we reasonably request." Abuse contact: `abuse@render.com`.
- **The Terms' abuse-prevention instrument is the card test authorisation**, not identity verification: "as an abuse prevention measure, Render may periodically initiate a test authorization on your payment method…" (quoted in §3). Note the circularity: this lever only exists *if a card is already on file*.
- **Eligibility / region restrictions are contractual, not procedural** ([render.com/terms](https://render.com/terms)): "Any use or access to the Service by anyone under 16 is strictly prohibited"; "The Service is not available to any Users prev[iously terminated]…"; and an "Export Control" clause ("You represent and warrant that by using the Service, you are authorized to receive the Service, and you are not (and are not part of or a citizen or resident of or located in) (i) a person or entity or group or region that is [sanctioned]…").
- **Available regions** ([render.com/docs/regions](https://render.com/docs/regions), 2026-10-14): "Oregon, USA / Ohio, USA / Virginia, USA / Frankfurt, Germany / **Singapore**". Singapore is available → a Render API in Singapore next to the Neon Singapore database is a supported configuration. No region-specific verification or card requirement is documented for any region.
- **Nothing in the changelog introduces a card requirement**: `render.com/changelog.md` (generated 2026-10-14, last 25 entries) contains **no** entry matching `payment|card|billing|fraud|verif`.

## 5. 2026 reports of being asked for a card, with source authority

| Source | Date | Claim (verbatim) | Authority |
| --- | --- | --- | --- |
| [GitHub issue #442](https://github.com/Chameleon-company/Planting-Optimisation-Tool/issues/442) | 2026-04-17 | "Blueprint deployment also requires a card on file." + manual dashboard creation worked instead | **User anecdote**, first-hand, but the same issue misstates Docker/free-tier support → medium confidence |
| [bex `workspace-plan-change.md`](https://github.com/bex-co/bex/blob/main/docs/render-artifacts/workspace-plan-change.md) | captured 2026-07-12 from a live authenticated session | Dashboard banner: "**This workspace plan requires a card for paid services and compute.**" — "Present regardless of which plan is selected (even Hobby, since compute/bandwidth overage still bills the card)" | **Third-party capture** (internal research of a Render *competitor*); wording of the banner is quoted from the UI, but it was on a workspace already on Pro (Legacy) with a card — not a fresh cardless account |
| [feedback.render.com — "Credit card required for free plan?"](https://feedback.render.com/features/p/credit-card-required-for-free-plan) | 2023-05-23 | "When I'm making a web service and I deploy tells me *'Please enter your payment information to select an instance type with higher limits.'*" | **User anecdote**; note the wording names a *higher-limit instance type*, i.e. a paid plan |
| [feedback.render.com — "Credit card information is required while your public offer says it's not"](https://feedback.render.com/features/p/credit-card-information-is-required-while-your-public-offer-says-its-not) | 2021-06-20 | "Render forces me to enter credit card when I try to create new static website, even on trial account period. Howether your documentation says it's not required." A commenter replies "they told me that was fixed" and links a community thread | **User anecdote**; 2021, and reported fixed |
| [toolfreebie.com](https://toolfreebie.com/render-hosting-review) | updated 2026-10-11 | "Credit card: **Not required**"; "Start free at render.com — no credit card required." | Third-party review; author states "We do not have a Render account, so nothing on this page is a deployment of ours" → **not first-hand** |
| [justinmckelvey.com](https://justinmckelvey.com/blog/is-render-free) | 2026-09-03 | "Yes — genuinely, permanently, **no card** … Verified September 2026 against render.com/docs/free and render.com/pricing" | Third-party review, doc-verified not tested |
| [freetier.co](https://freetier.co/directory/products/render) | verified 2026-08-29 | Field says "Credit card **Not stated**", but the prose says "**a credit card is required to sign up**, which adds some friction" | Third-party aggregator, **internally contradictory** |
| Reddit r/webdev "Render.com (don't give your credit card)"; r/developersIndia "Render.com automatically charged me…" | 2025–2026 | not retrievable | **Blocked by Reddit bot challenge** from this environment → [UNVERIFIED] |

### Conflicting claims, side by side

| Claim | Who says it | Primary or secondary |
| --- | --- | --- |
| "No payment is required" to deploy free resources | Render docs, twice | **Primary** (render.com/docs/your-first-deploy, render.com/docs/free) |
| "**No credit card is required.** You can deploy with Docker, Node.js / Bun, Python, Ruby, Go, Rust, and Elixir" | Render's own editorial article "Platforms with a real free tier for developers in 2026", 2026-04-23 | **Primary** (render.com/articles/…) |
| "Signup page has no card field" | Observed live today on dashboard.render.com/register | **Primary observation** |
| "You must enter payment information to perform this request." (HTTP 402) on `POST /services` | Render's own public OpenAPI + API reference | **Primary** |
| "Blueprint deployment also requires a card on file." | GitHub user, 2026-04-17 | Secondary, first-hand |
| "a credit card is required to sign up" | freetier.co, verified 2026-08-29 | Secondary; contradicts the live signup page and its own data field |

### Which is likely correct, and why

**Render's primary sources win, with one sharp qualifier — and the qualifier is the answer to your owner's problem.**

1. The card gate is **per-resource-plan**, not per-account or per-flow. The Terms say a payment method is required "during your use of any **paid aspects** of the Service"; the 402 is declared on *create/modify service* and other paid operations; the spend-authorization error codes all say "*the plan* needs a spend authorization". Nothing in Render's contract conditions free instances on a card.
2. Therefore "Blueprint demands billing details while manual creation did not" is not a contradiction of the docs — it is the documented default biting: `render.yaml` without `plan: free` provisions `0.5c-512mb` (paid) for **each** service, and `256mb` (paid) for a Key Value instance. The manual wizard makes you *choose* Free; the Blueprint makes you *state* Free.
3. freetier.co's "card required to sign up" is the least credible claim in the table: it contradicts a page I loaded live today (no card field, hCaptcha only) and contradicts its own "Not stated" field.
4. The 2021 feedback post is the one genuine "marketing says no card but the product asked" case — for an always-free **static site** — and a Render-adjacent reply states it was fixed. That is the failure mode you're afraid of, and it is 4+ years stale.

**So: the honest answer is *not* "the marketing page says no card but the product asks for one" for a free web service. It is: "the docs say no card for free instances and that holds — but a Blueprint without explicit `plan: free` on every service silently requests paid compute, and paid compute is where the card prompt comes from."** For your project: put `plan: free` on every service in `render.yaml`, and if you still get a card prompt at "Deploy Blueprint", fall back to creating the three resources by hand (New → Web Service → Free, plus Neon for the DB so Render's 30-day free-Postgres expiry never applies).

## Not verified / gaps

1. **No account was created and no flow was clicked through by this agent.** Every "no card in the flow" statement above is from Render's docs, its API contract, or the public signup page — not from a completed cardless deploy.
2. **Whether a Blueprint whose `render.yaml` explicitly sets `plan: free` everywhere still triggers a payment prompt in the dashboard is UNKNOWN.** Render publishes no doc for the Blueprint create payment gate (no 402 is declared on any `/blueprints*` endpoint, and no `/docs` page mentions payment in the Blueprint flow). GitHub #442 is the only 2026 report and its Blueprint also requested paid defaults (and a disk/paid DB), so it is not a clean single-variable test.
3. **`community.render.com` was unreachable from this environment** — `community.render.com/t/creating-static-site-during-free-trail-fails/1649` redirects to `render.discourse.group`, which failed DNS (`getaddrinfo ENOTFOUND render.discourse.group`). No Render-staff statement could be retrieved today. The pricing FAQ does point users there: "talk to us in our [user community](https://community.render.com/)".
4. **Reddit threads blocked** by a bot challenge ("Prove your humanity"), so `r/webdev` "Render.com (don't give your credit card)" and `r/developersIndia` "automatically charged me" are unreported above.
5. **No published billing/payment-methods docs page exists** (`/docs/billing` and `/docs/payment-methods` both 404), so the exact fields in Render's "Add payment method" form — and whether a name/address step exists *without* a card — could not be confirmed from the provider. The `$1` hold and card-only method list come from the pricing FAQ; the Stripe dependency from the Terms.
6. **Whether Render runs any undocumented anti-fraud/risk check at first deploy** (beyond hCaptcha + the card test authorisations) is unknown; AUP and Terms are silent. `[UNVERIFIED]`
7. **antilak.com's "Render Free Tier 2026" guide (2026-03-04)** appeared in search results with a headline about credit cards, but its body could not be retrieved (page serves a canonical root document) → excluded. `[UNVERIFIED]`
8. **The bex-authored artifacts are a competitor's internal research**, captured from a live authenticated dashboard on 2026-07-12 / 2026-07-31 and a **Pro (Legacy)** workspace with a card already on file. They are quoted above only where they reproduce UI wording; they cannot show a cardless first deploy.

## Sources (all accessed 2026-10-14)

Primary (Render):
- https://render.com/docs/free
- https://render.com/docs/faq
- https://render.com/docs/your-first-deploy
- https://render.com/docs/infrastructure-as-code
- https://render.com/docs/blueprint-spec
- https://render.com/docs/compute-plans
- https://render.com/docs/render-dashboard
- https://render.com/docs/team-members
- https://render.com/docs/regions
- https://render.com/pricing (+ FAQ)
- https://render.com/terms (client-rendered; text read via headless Chromium)
- https://render.com/acceptable-use (client-rendered; text read via headless Chromium)
- https://render.com/articles/platforms-with-a-real-free-tier-for-developers-in-2026 (dated 2026-04-23)
- https://api-docs.render.com/openapi/render-public-api-1.json (downloaded and parsed; 376,412 bytes)
- https://api-docs.render.com/reference/create-service
- https://dashboard.render.com/register (public signup form observed; no account created)
- https://render.com/changelog.md (generated 2026-10-14)

Community / secondary:
- https://feedback.render.com/features/p/credit-card-required-for-free-plan (user, 2023-05-23)
- https://feedback.render.com/features/p/credit-card-information-is-required-while-your-public-offer-says-its-not (user, 2021-06-20)
- https://github.com/Chameleon-company/Planting-Optimisation-Tool/issues/442 (user, 2026-04-17)
- https://github.com/bex-co/bex/blob/main/docs/render-artifacts/workspace-plan-change.md (competitor capture, 2026-07-12)
- https://github.com/bex-co/bex/blob/main/docs/render-artifacts/paid-create-without-card.md (competitor research, 2026-07-31)
- https://toolfreebie.com/render-hosting-review (updated 2026-10-11; "no credit card")
- https://justinmckelvey.com/blog/is-render-free (2026-09-03; "no card")
- https://freetier.co/directory/products/render (verified 2026-08-29; "card required", contradicts its own field)

---

**Section owner:** `DurableFreePythonHosts` (all hosts except Render — see the Render section above).

# DURABLE CARD-FREE HOSTS for a FastAPI + LangGraph container that calls Neon over TCP 5432

Scope of this section: Modal (Starter), Leapcell (Hobby), Koyeb, Railway, Wispbyte, Replit, Back4App Containers, Hugging Face Spaces, plus Zeabur, Vercel Hobby, and the usual card-walled "free forever" hosts (Oracle, Fly.io, alwaysdata, Pella) as explicit rejects. All pages fetched **2026-10-14 (UTC+7)** unless a capture date is stated. Quotes are the provider's own wording; where the marketing page and the docs disagree, that is called out in the row.

## Summary table — signup requirement first

| Host (free tier name) | 1. Signup / deploy requirement (provider's own words) | 2. FastAPI/ASGI + outbound TCP 5432 to Neon | 3. Durability of the free tier | 4. Limits that would bite this project | 5. HTTPS + custom domain on free |
| --- | --- | --- | --- | --- | --- |
| **Wispbyte** (free client-panel server) | "**Free forever, no credit card**" / "**Free hosting, no card required.**" / "Free hosting forever! No renewals, no credits needed." | Docker image picked in panel; KB: "Start your web app and bind it to all interfaces so we can reach it." 5432 outbound **[UNVERIFIED]** | "Free servers are never deleted" + "Log in every 2 weeks to keep a free server running" | 512 MB RAM / 1 GB disk / 35 % CPU (100 % ~90 s at startup); biweekly login; no SLA, small operator | Free subdomains (beta) per KB; public HTTPS URL for a free web app **[UNVERIFIED]** |
| **Leapcell** (Hobby $0) | **No provider statement found about a card at signup** — the only card wording is for paid: "We accept all major credit and debit cards" + "$1 USD transaction … credit security check" for adding a card. → **card requirement [UNVERIFIED]** | Documented FastAPI path (`uvicorn app:app --host 0.0.0.0 --port 8080`); official repo `leapcell/leapcell-neon-example` connects to Neon (5432, `sslmode=require`) | $0 Hobby is an ongoing plan (Free column vs Pro), **but serverless only** — "Persistent Servers" is a Plus feature | Request 15 min max ("The maximum execution time for a single request is 15 minutes"); "it cannot run any background tasks when there are no incoming requests"; **3 GB-hours/month** compute; 100 k invocations; 60 build min (3rd-party) | HTTPS `*.leapcell.dev`; custom domains on free, "We use Let's Encrypt to provide free SSL certificates for your custom domains" |
| **Back4App Containers** (Free) | "(**no credit card required**)" twice on the pricing page | "a **Dockerfile is mandatory**"; Python listed; 5432 outbound **[UNVERIFIED]** | Free plan is a permanent plan on the pricing page; **third-party tester claims the free container is destroyed 60 min after deploy starts [not confirmed by Back4App]** | **0.25 vCPU / 256 MB RAM / 100 GB transfer** → below this project's 250–400 MB RSS | Free `*.b4a.run` HTTPS; **custom domain left the free plan** (Back4App docs: "The menu path moved, and the feature left the free plan") |
| **Hugging Face Spaces** (cpu-basic) | Pricing table lists **CPU Basic … FREE**; no provider statement found about cards → **card requirement [UNVERIFIED]** (account only) | Docker SDK Spaces run uvicorn/FastAPI — **but "you can make requests through the standard HTTP and HTTPS ports (80 and 443) along with port 8080. Any requests going to other ports will be blocked." → TCP 5432 blocked** | Free hardware is permanent but not always-on: "Your Space will automatically be paused after 48h of inactivity"; "A paused Space stops executing until **manually restarted by its owner**" | 2 vCPU / 16 GB free; 48 h auto-pause; documented page quota for cpu-basic hours **[UNVERIFIED]** | HTTPS `*.hf.space`; custom domain "is part of **PRO or Team & Enterprise plans**" → no |
| **Zeabur** (Free / "Serverless") | "**No credit card required — just sign up and start deploying.**" | Product supports GitHub/Dockerfile/Docker images; free "Serverless" plan's support for a Dockerfile/persistent container **[UNVERIFIED]**; 5432 outbound **[UNVERIFIED]** | Ongoing $0 plan, but auto-sleep and usage policing: "Serverless plans are **restricted to non-commercial use only**"; "if we've detected that your usage is not fair, we will **terminate your services immediately**" | "Services on the Free Plan automatically sleep after a period of inactivity"; free compute quota not published on the pricing page **[UNVERIFIED]** | `*.zeabur.app`; custom domain on free **[UNVERIFIED]** |
| **Vercel** (Hobby) | "The Hobby plan is **free** and aimed at developers with personal projects, and small-scale applications" (no card step documented) | **No Dockerfile/container** — FastAPI must be rewritten as a Python serverless function; no long-lived process for a 10–60 min batch | Free plan is ongoing but usage-metered; overage pauses the account | "**Maximum duration … Hobby: 300s default and maximum**" → a >5 min batch request is impossible; 60 GB-hrs/month included | `*.vercel.app` + custom domains free |
| **Modal** (Starter) | Pricing sells "$30 / month free credits"; **docs contradict it**: "Note that you must have a **payment method on file in order to use Modal**." → **card required, marketing/docs disagree** | ASGI/FastAPI app supported (`@modal.asgi_app`), Docker images; 5432 outbound not restricted in docs **[UNVERIFIED]** | Starter is an ongoing plan with recurring credits, but unusable under the owner's absolute "no card" rule | Function timeout "between 1 second and 24 hours" (good for batch); Starter has "**Scheduled and Web Functions (limited)**", 100 containers | HTTPS `*.modal.run`; "Custom domains" appear in the **Team** plan feature list, not Starter |
| **Koyeb** (free instance) | FAQ: "**We require a credit card to prevent fraud and abuse.** We verify the card you enter by placing a **$29 pre-authorization hold** and immediately canceling it." Blog says the opposite: "we believe keeping a **free tier available without a credit card** is key", signup "will prompt you for a credit card only if we find no automatic way to prove that you're a human." → **direct marketing/docs conflict; card risk** | Docker/buildpack deploys, FastAPI fine; 5432 outbound **[UNVERIFIED]** | FAQ: "Is there a free tier? … One `free` web Service in Frankfurt or Washington, D.C."; "You will never be charged when using the `free` web Service." Blog reaffirms commitment to a free tier | Free instance is tiny: "1 Service running on a tiny instance (2GB Disk, **512 MB RAM, and 0.1 vCPU**)" (blog wording) | HTTPS `*.koyeb.app`; custom domains documented for **Pro** ("100 custom domains for free in the Pro plan and up") → free-plan custom domain **[UNVERIFIED]** |
| **Railway** (Free) | "**Can I try Railway without a credit card? Yes.** As a new Railway user, you can sign up for a free Trial." Also: "I prefer to prepay. Is that possible? Not anymore as of March 30th, Railway requires the use of a post-paid card." | Dockerfile/Nixpacks deploys, full outbound | **Not durable compute**: Trial = 30 days + one-time $5, then "the free trial reverts to the Free plan, which provides **$1 of free credit per month**. The credit does not roll over." | Free = "Up to 1 vCPU / 0.5 GB per service, 1 replica, and 3-day log history"; $1/month cannot hold 0.5 GB up all month ($10/GB/month) → "if your credit balance reaches zero … we will **stop all of your workloads**" | HTTPS `*.up.railway.app`; custom domains (1 on Trial per pricing table) |
| **Replit** (Starter) | Free Starter plan exists (no card wording found); publish of 1 app included | Backend not included on free: "**converting to an artifact with backend functionality requires an upgrade**" | **Fails**: "This published link will **automatically go down after 30 days**" | 1 published app, 30-day link lifetime, Autoscale/Reserved VM are paid | `*.replit.app` on the free published app; custom domains paid |

## Per-host detail

### Wispbyte — free, card-free, persistent container (with a biweekly chore)
1. **Signup/deploy:** [wispbyte.com/client/register](https://wispbyte.com/client/register) and [/client/login](https://wispbyte.com/client/login), fetched 2026-10-14, verbatim: "Free forever, no credit card", "Free hosting, no card required.", "Log in every 2 weeks to keep a free server running, and we never delete it for inactivity." Homepage/markdown metadata, same day: "Free hosting forever! No renewals, no credits needed. Deploy websites, Discord bots, and applications with our reliable 24/7 hosting platform." KB article descriptions: "[Create a free Wispbyte server: register, **pick a Docker image**, configure startup and environment variables…](https://wispbyte.com/kb/getting-started)", "[Start your web app and bind it to all interfaces so we can reach it](https://wispbyte.com/kb/static-web-server)", and a [Subdomains (Beta)](https://wispbyte.com/kb/subdomains) article.
2. **Python/ASGI:** Docker-image based panel → the existing Dockerfile can be used as-is. **Outbound TCP 5432 is not documented anywhere I could fetch — [UNVERIFIED].**
3. **Durability:** "Free servers are never deleted" (login page) + "Free hosting forever! No renewals, no credits needed." The catch is the biweekly login: miss it and the server is stopped (not deleted).
4. **Limits:** 512 MB RAM, 1 GB storage, 35 % CPU with a ~90 s 100 % startup boost (provider's own blog table at [wispbyte.com/blog/free-hosting-comparison](https://wispbyte.com/blog/free-hosting-comparison)); no documented request-duration cap (it is a persistent process, so a 10–60 min batch job is fine); no SLA.
5. **HTTPS/domain:** KB implies a linkable subdomain (example `https://starlight.wispbyte.org`); whether the free plan exposes a public HTTPS URL for an arbitrary web app, and whether a custom domain works without premium, is **[UNVERIFIED]** (KB bodies are client-rendered; only frontmatter was retrievable).

### Leapcell — Hobby $0, best technical fit, card statement missing
1. **Signup/deploy:** No provider sentence about cards on the Hobby plan. [leapcell.io/pricing](https://leapcell.io/pricing) FAQ only covers paid: "We accept all major credit and debit cards." and "Why was I charged $1 after adding a credit card? A $1 USD transaction is performed as a credit security check…". Their fair-use page polices free abuse ("If you determine you're using multiple accounts to get around the free limit, we reserve the right to terminate service"), and the docs list a permanent "Free" column. → **No card cannot be confirmed from Leapcell's own words: [UNVERIFIED].** Third-party freetier.co (2026) says "Credit card Not required".
2. **Python/ASGI:** [docs.leapcell.io/examples/python/fastapi](https://docs.leapcell.io/examples/python/fastapi): Build `pip install -r requirements.txt`, Start `uvicorn app:app --host 0.0.0.0 --port 8080`, Port `8080`. Neon over TCP 5432 is evidenced by Leapcell's own repo [github.com/leapcell/leapcell-neon-example](https://github.com/leapcell/leapcell-neon-example): "You can use this connection string with popular ORMs or directly in your code" (Python example uses `psycopg2-binary`, `sslmode=require`). Dockerfile builds: not documented in the pages I read → **[UNVERIFIED]** (their limits page does list image retention and max build duration, implying image builds).
3. **Durability:** Hobby is a standing $0 plan, not a trial; "Serverless Duration … 3 GB-hours / month included. After that, pricing starts at $0.18 per GB-hour" implies metered, not expiring.
4. **Limits:** Request Timeout free = **15 min**; "**HTTP Short-Lived Requests Only** … it cannot run any background tasks when there are no incoming requests"; 100,000 Serverless Invocations/month; 3 GB-hours/month (with 0.5–4 GB allocation, that is only ~45 min to ~6 h of wall-clock compute per month — the binding constraint for a 10–60 min batch); 20 projects; up to 3 vCPU / 4 GB per project; 7-day log retention.
5. **HTTPS/domain:** `foo-bar.leapcell.dev` after deploy; "We use Let's Encrypt to provide free SSL certificates for your custom domains"; limits page: free = 10 custom domains.

### Back4App Containers — card-free but 256 MB and a lifetime question
1. **Signup/deploy:** [back4app.com/pricing/container-as-a-service](https://www.back4app.com/pricing/container-as-a-service) (fetched today) — "With Back4app Web Deployment Free limit, you can spin up your Dockerized software project at no charge (**no credit card required**)" and "Back4app Web Deployment has a Free tier (**no credit card required**)". Table cell, verbatim: "Free | 0.25 | 256 MB | 100 GB | $0/mo".
2. **Python/ASGI:** [docs-containers](https://www.back4app.com/docs-containers): "a **Dockerfile is mandatory** to run your project on the platform"; Python (Django/Flask) listed among runnable stacks → FastAPI fine. 5432 outbound **[UNVERIFIED]**.
3. **Durability:** the Free plan is a standing plan, not a trial — but a third-party tester writes "on the free plan the URL is temporary and the container is destroyed **60 minutes after the deploy starts** — we saw 60 heartbeats, then silence" (snapdeploy.dev, fetched via search today). **That sentence could not be found on any Back4App-owned page: [UNVERIFIED], and it is decisive if true.**
4. **Limits:** 256 MB RAM / 0.25 shared vCPU — below the project's 250–400 MB RSS. No request-duration or hourly-quota statement found on Back4App's own pages.
5. **HTTPS/domain:** "Every site or web service hosted on Back4app Containers automatically receives a free `b4a.run` address." Custom domain: provider docs page states the feature "left the free plan".

### Hugging Face Spaces — 16 GB free, but 5432 is blocked and it pauses
1. **Signup/deploy:** [huggingface.co/pricing](https://huggingface.co/pricing): "CPU Basic | 2 vCPU | 16 GB | - | - | **FREE**". No provider sentence about a card was found → **[UNVERIFIED]** (an HF account appears sufficient; ZeroGPU free access also requires only "verified email, account older than 30 days").
2. **Python/ASGI:** Docker SDK Spaces with a FastAPI/uvicorn container work — but the network policy kills the Neon TCP path: [spaces-overview](https://huggingface.co/docs/hub/spaces-overview): "If your Space needs to make any network requests, you can make requests through the standard HTTP and HTTPS ports (80 and 443) along with port 8080. **Any requests going to other ports will be blocked.**" → 5432 is out; only a code change to Neon's HTTPS SQL-over-HTTP driver (443) would work.
3. **Durability:** free hardware is not time-limited, but not continuously online: "On free hardware, your Space will 'go to sleep' and stop executing after a period of time if unused"; huggingface_hub docs: "if you are using a 'cpu-basic' hardware, you cannot configure a custom sleep time. Your Space will **automatically be paused after 48h of inactivity**"; spaces-overview: "A paused Space stops executing **until manually restarted by its owner**."
4. **Limits:** 2 vCPU / 16 GB (ample); no published monthly hour quota for cpu-basic that I could find **[UNVERIFIED]**; the 48 h pause + no scheduler is the operational problem; Spaces are positioned as "ML demo apps".
5. **HTTPS/domain:** `*.hf.space` HTTPS yes; [spaces-custom-domain](https://huggingface.co/docs/hub/spaces-custom-domain): "This feature is part of **PRO or Team & Enterprise plans**." → no custom domain on free.

### Zeabur — no card, but auto-sleep and a non-commercial clause
1. **Signup/deploy:** [zeabur.com/docs/pricing/free-plan](https://zeabur.com/docs/en-US/pricing/free-plan): "No credit card required — just sign up and start deploying."
2. **Python/ASGI:** Zeabur supports GitHub integration, Dockerfile and Docker images generally; the free plan is the **Serverless** plan ([changelog](https://zeabur.com/changelogs/say-hello-to-the-serverless-plan): "The Serverless Plan focuses on the future, emphasizing Serverless services from GitHub"; "If you ever feel the need for more traditional containerized services … our Developer Plan is always there") → whether a Dockerfile/persistent container is allowed on free is **[UNVERIFIED]**. 5432 outbound **[UNVERIFIED]**.
3. **Durability:** $0 plan is standing, but conditional: fair-use guidelines: "**Serverless plans are restricted to non-commercial use only**" (a thesis prototype qualifies) and "if we've detected that your usage is not fair, we will terminate your services immediately". "No SLA".
4. **Limits:** "Services on the Free Plan automatically sleep after a period of inactivity. They wake up on the next incoming request, which may cause a few seconds of cold-start latency." A free-tier compute quota (vCPU/GB-hours) is **not published** on the pricing page I read → **[UNVERIFIED]** (third-party aggregators claim $5 credit / 1 vCPU / 2 GB, unconfirmed).
5. **HTTPS/domain:** `*.zeabur.app`; custom domain on free **[UNVERIFIED]**.

### Modal (Starter) — the docs say a card is mandatory
1. **Signup/deploy:** [modal.com/pricing](https://modal.com/pricing): "Starter … $0 + compute / month · $30 / month free credits · 3 workspace seats included · 100 containers + 10 GPU concurrency · Scheduled and Web Functions (limited) · 1 TiB / month free network egress". Its own [billing docs](https://modal.com/docs/guide/billing), fetched today, contradict that framing: "**Note that you must have a payment method on file in order to use Modal.**" and "This will take you to a Stripe-hosted page where you can update your payment method and/or billing email." → **card required; marketing page vs docs disagreement.**
2. **Python/ASGI:** strong fit technically — [webhooks](https://modal.com/docs/guide/webhooks) documents serving ASGI apps (FastAPI) and non-ASGI servers; images are Dockerfile/registry-based; no documented outbound port restriction, so 5432 to Neon is presumably fine **[UNVERIFIED]**.
3. **Durability:** Starter is a recurring plan, not a trial, so durability is fine — but it fails the owner's absolute rule.
4. **Limits:** [timeouts doc](https://modal.com/docs/guide/timeouts): "All Modal Function executions have a default execution timeout of 300 seconds (5 minutes), but users may specify timeout durations between 1 second and 24 hours." Web Functions are "limited" on Starter; custom domains are in the Team column.
5. **HTTPS/domain:** `*.modal.run` HTTPS. Custom domains listed only for **Team** on the pricing comparison → free-plan custom domain presumably unavailable **[INFERENCE from the pricing table]**.

### Koyeb — marketing says "no card", the FAQ says "$29 pre-authorisation hold"
1. **Signup/deploy:** [koyeb.com/docs/faqs/pricing](https://www.koyeb.com/docs/faqs/pricing) (fetched today): "**We require a credit card to prevent fraud and abuse.** We verify the card you enter by placing a **$29 pre-authorization hold** and immediately canceling it." and "Right after we place the $29 pre-authorization hold to verify your card, we also charge you the pro-rated amount for the plan you select." Against that, Koyeb's own blog [Sustaining free compute in a hostile environment](https://www.koyeb.com/blog/sustaining-free-compute-in-a-hostile-environment): "we believe keeping a **free tier available without a credit card** is key for a frictionless onboarding" and "we now offer a signup that will prompt you for a credit card **only if we find no automatic way to prove that you're a human**". → **Direct contradiction between the provider's blog and its pricing FAQ. Do not rely on the blog.**
2. **Python/ASGI:** Docker/buildpack deployments; 5432 outbound **[UNVERIFIED]** (no Koyeb doc fetched today states egress restrictions).
3. **Durability:** FAQ: "Is there a free tier? … One `free` web Service in Frankfurt or Washington, D.C." and "You will never be charged when using the `free` web Service." Blog: "In the long run, we think we can keep a free tier with 1 Service running on a tiny instance (2GB Disk, **512 MB RAM, and 0.1vCPU**)."
4. **Limits:** 0.1 vCPU / 512 MB free instance (blog wording above); the FAQ page I fetched still describes a "$29 Pro plan" and a free Postgres "limited to 5 hours of active time", so parts of that FAQ read as stale — flag before trusting numbers.
5. **HTTPS/domain:** `*.koyeb.app`; custom domains are documented as a **Pro** feature ("We let you use 100 custom domains for free in the Pro plan and up to 500 in the Scale plan") → free-plan custom domain **[UNVERIFIED]**.

### Railway — card-free trial, but the free tier cannot stay online
1. **Signup/deploy:** "**Can I try Railway without a credit card? Yes.** As a new Railway user, you can sign up for a free Trial." ([railway.com/pricing](https://railway.com/pricing) FAQ). But: "I prefer to prepay. Is that possible? **Not anymore as of March 30th, Railway requires the use of a post-paid card.**"
2. **Python/ASGI:** Dockerfile/Nixpacks; outbound unrestricted.
3. **Durability:** **fails** — [docs.railway.com/pricing/free-trial](https://docs.railway.com/pricing/free-trial): "The trial gives access to basic features for **up to 30 days** and includes a one-time grant of **$5**"; "After 30 days passes or $5 is spent, the free trial reverts to the **Free** plan, which provides **$1 of free credit per month**. The credit does not roll over month to month." [Plans doc](https://docs.railway.com/pricing/plans): "**Free** — For running small apps with **$1 of free credit per month**".
4. **Limits:** Free = "Up to **1 vCPU / 0.5 GB** per service, 1 replica, and **3-day log history**"; RAM billed "$10 / GB / month", so $1/month covers well under a month of a 0.5 GB service; when credits run out, "we will **stop all of your workloads**".
5. **HTTPS/domain:** `*.up.railway.app`; custom domains exist (Trial table: 1).

### Replit — the free published link expires in 30 days
1. **Signup/deploy:** free Starter plan; [docs.replit.com/billing/plans/starter-plan](https://docs.replit.com/billing/plans/starter-plan): "Get **1 free published app**".
2. **Python/ASGI:** not for a backend on free: "Starter plan builders can create designs and publish them, but **converting to an artifact with backend functionality requires an upgrade**."
3. **Durability:** **fails** — same doc: "This published link will **automatically go down after 30 days**."
4. **Limits:** Autoscale ("You pay while requests are being served") and Reserved VM ("Fixed monthly cost") are paid deployment types; the free published app also carries a "Made with Replit" badge.
5. **HTTPS/domain:** `*.replit.app` HTTPS; custom domains are a paid publishing feature.

### Vercel Hobby — free and card-free, but the wrong shape
1. **Signup/deploy:** [vercel.com/docs/plans/hobby](https://vercel.com/docs/plans/hobby): "The Hobby plan is **free** and aimed at developers with personal projects, and small-scale applications." (Hobby is personal/non-commercial; no card step is documented.)
2. **Python/ASGI:** no Dockerfile execution — the FastAPI app would have to be restructured into a Python serverless function, with no long-lived process for the batch runner.
3. **Durability:** the Hobby plan is standing, but metered (Hobby includes 60 GB-hrs and 1,000,000 invocations per the plan page).
4. **Limits:** [vercel.com/docs/functions/limitations](https://vercel.com/docs/functions/limitations): "**Maximum duration … Hobby: 300s default and maximum**" → a 10–60 min batch request cannot run in one invocation.
5. **HTTPS/domain:** `*.vercel.app` + custom domains free (already used for the frontend).

## Explicit rejects (card-walled "free forever" hosts)

| Host | Provider wording | Why rejected |
| --- | --- | --- |
| **Oracle Cloud Always Free** | "Why do I need to provide credit or debit card information when I sign up for Oracle Cloud Free Tier? We use your contact information and **credit/debit card information for account setup and identity verification** … your credit card is authorized for **$1 USD** (or its equivalent in your country) at the time of sign-up." | Card + authorisation hold at signup, even for "Always Free" |
| **Fly.io** | "**All organizations (except for Linked Organizations) require a credit card on file.**" (docs, quoted in today's search results) | Card required |
| **Pella (pella.app)** | Free Flask/FastAPI pages: "Our Python-optimized platform offers a quick, hassle-free setup—**no credit card required**." | No published free-tier specs (RAM/hours/durability) → cannot be ranked; **[UNVERIFIED]** |
| **alwaysdata** (free plan) | Free plan "**cannot be used for profit purposes** and the creation of websites on this plan is **limited to the alwaysdata.net account's address**" (docs wording surfaced via search; the plan page itself was not fetched today) | 100 MB disk class plan, no custom domain, sources second-hand → **[UNVERIFIED]** |

## Ranking for this specific use case

Constraint order used: (a) no card at any step, verified from provider wording, (b) can run this Docker/FastAPI container and reach Neon on 5432, (c) still deployable and demonstrable months from now, (d) can survive a 10–60 min batch over 30–100 submissions, (e) free HTTPS.

1. **Wispbyte — first choice on the hard constraint.** It is the only candidate whose own pages state both halves of what this project needs: "**Free forever, no credit card**" and a persistent, never-deleted server that can run a Docker image around the clock ("Free servers are never deleted"), which is exactly what a 10–60 min batch job wants. Cost: 512 MB RAM, a biweekly panel login, and an unverified answer on outbound 5432 / public HTTPS for a web app. Prove those two things on day one (deploy the container, `psql`/`asyncpg` to Neon, curl the public URL) before trusting it.
2. **Leapcell Hobby — best technical fit, one missing sentence.** Documented FastAPI deploy config, an official Neon integration example, free custom domain + Let's Encrypt SSL, and a 15-minute per-request ceiling that suits chunked batch work. Against it: **no Leapcell wording confirms a card-free signup**, the Hobby tier is serverless-only (no always-on process, no work without traffic), and **3 GB-hours/month of compute** is small — with a 0.5–1 GB allocation that is roughly 3–6 wall-clock hours per month, so the batch must be chunked per submission (idempotent, resumable via the Neon DB) and the month's budget watched.
3. **Back4App Containers Free — card-free by the provider's own words, but under-specified.** "no credit card required" twice, Dockerfile mandatory (works), free `b4a.run` HTTPS. Two disqualifiers must be cleared first: **256 MB RAM vs this project's 250–400 MB RSS**, and the third-party claim that the free container dies 60 minutes after each deploy (no Back4App-owned page confirms that, and if true it is fatal).
4. **Hugging Face Spaces — demo-only fallback.** No card, 16 GB RAM, Docker SDK — but 5432 to Neon is blocked by policy (only 80/443/8080 allowed), free Spaces auto-pause after 48 h of inactivity pending a manual restart, no custom domain, and the product is positioned for ML demos. Only worth it if you switch the DB access to Neon's HTTPS driver and accept manual restarts.
5. **Zeabur Free — last resort.** Card-free and standing, but auto-sleep, non-commercial-only terms with unilateral termination for "not fair" usage, no published free compute quota, and unclear support for a Dockerfile/persistent container on the free plan.
6. **Vercel Hobby** — free and card-free, but a 300 s request cap and no container: keep it for the frontend only.
7. **Render** — see the section above: the documented free path is card-free; the card prompt comes from a Blueprint that omits `plan: free`. Best-ranked option *if* the Blueprint with explicit `plan: free` deploys without a card prompt — that is unproven (peer's gap #2).

**Rejected outright:** Modal (payment method mandatory in its own billing docs), Koyeb (FAQ: card + $29 pre-authorisation hold), Railway (30-day trial → $1/month credit, cannot stay online), Replit (30-day published link; backend requires upgrade), Oracle Cloud and Fly.io (card at signup).

**For the batch job specifically:** none of the card-free survivors is designed for a 10–60 minute synchronous call. The safe design is the same on all of them — split the batch into per-submission units of ≤15 minutes, persist progress in the Neon table, make each unit idempotent and retryable, and drive it from the API rather than expecting a background worker (Leapcell: "it cannot run any background tasks when there are no incoming requests"). Wispbyte is the only survivor where a real 60-minute process can simply run.

## Not verified / gaps (flagged because a marketing page already failed this project once)

1. **Leapcell: whether signup/deploy requires a card — [UNVERIFIED].** No Leapcell-owned page states either way; only payment-card wording for *paid* plans was found. This is the single most important unverified item in this section.
2. **Leapcell: Dockerfile/image build support on the free plan — [UNVERIFIED].** Docs show language build configs; the limits page's image-retention/build-duration rows imply image builds but do not say Dockerfile.
3. **Wispbyte: outbound TCP 5432 — [UNVERIFIED].** No network/egress documentation exists; KB bodies are client-rendered React and were not retrievable (only frontmatter + search snippets).
4. **Wispbyte: public HTTPS URL and custom domain on the free plan — [UNVERIFIED].** Only "Subdomains (Beta)" and a "link a subdomain" KB description were found.
5. **Wispbyte: the 512 MB / 1 GB / 35 % CPU specs** come from the provider's own blog metadata and third-party comparisons; the client panel's plan page was not reachable without an account.
6. **Back4App: free container lifetime — [UNVERIFIED and critical].** A third-party tester says the free URL/container lives 60 minutes per deploy; Back4App's own pricing page and docs pages do not mention it.
7. **Back4App: outbound TCP 5432 — [UNVERIFIED].**
8. **Hugging Face: no provider statement about card-freeness, and no published cpu-basic monthly hour quota — [UNVERIFIED].**
9. **Hugging Face: whether an auto-slept (as opposed to manually paused) Space restarts automatically on the next request — [UNVERIFIED].** The docs say free Spaces are "paused" after 48 h and that "A paused Space stops executing until manually restarted by its owner"; wake behaviour on request is not stated in the pages I fetched.
10. **Zeabur: Dockerfile/persistent-container support and the compute quota on the free Serverless plan — [UNVERIFIED].** The pricing page lists features, not free-tier compute; the changelog says free = "Serverless services from GitHub".
11. **Koyeb: which flow actually requires the card (blog vs FAQ contradiction), and whether the free instance still exists in 2026 — [UNVERIFIED].** The FAQ I fetched still contains stale $29-Pro wording. A third-party news item (corpdev, 2026-02-17) claims Koyeb was acquired by Mistral AI — third-party, not confirmed on koyeb.com today.
12. **Modal: custom domains on Starter — [INFERENCE] only**, from "Custom domains" appearing in the Team column of the pricing comparison; no dedicated doc page was reachable (`/docs/guide/custom-domains` → 404).
13. **No account was created and no signup form was submitted on any of these hosts.** Every card statement above is a provider-page quote, not an observed flow — except where a peer's section reports a live observation for Render.
14. **alwaysdata and Pella were not fetched from their own plan/pricing pages today**, so their rows stay second-hand.

## Sources (all accessed 2026-10-14)

Provider-primary:
- https://modal.com/pricing · https://modal.com/docs/guide/billing · https://modal.com/docs/guide/timeouts · https://modal.com/docs/guide/webhooks
- https://leapcell.io/pricing · https://leapcell.io/signup · https://docs.leapcell.io/limit/ · https://docs.leapcell.io/serverless-vs-persistent · https://docs.leapcell.io/fair-use · https://docs.leapcell.io/service/domain · https://docs.leapcell.io/examples/python/fastapi · https://docs.leapcell.io/sitemap.xml · https://github.com/leapcell/leapcell-neon-example
- https://www.koyeb.com/docs/faqs/pricing · https://www.koyeb.com/blog/sustaining-free-compute-in-a-hostile-environment · https://community.koyeb.com/t/free-tier-issue-redirecting-to-pro-plan/4571 (login-walled)
- https://railway.com/pricing · https://docs.railway.com/pricing/free-trial · https://docs.railway.com/pricing/plans.md
- https://wispbyte.com/ · https://wispbyte.com/client/login · https://wispbyte.com/client/register · https://wispbyte.com/terms · https://wispbyte.com/kb · https://wispbyte.com/kb/getting-started · https://wispbyte.com/kb/startup-settings · https://wispbyte.com/kb/static-web-server · https://wispbyte.com/kb/subdomains · https://wispbyte.com/blog/free-hosting-comparison
- https://docs.replit.com/billing/plans/starter-plan · https://docs.replit.com/features/publishing/deployment-types
- https://www.back4app.com/pricing/container-as-a-service · https://www.back4app.com/docs-containers · https://www.back4app.com/docs-containers/release-notes
- https://huggingface.co/pricing · https://huggingface.co/docs/hub/spaces-overview · https://huggingface.co/docs/hub/spaces-custom-domain · https://huggingface.co/docs/hub/spaces-gpus · https://huggingface.co/docs/hub/spaces-zerogpu · https://huggingface.co/docs/huggingface_hub/guides/manage-spaces
- https://zeabur.com/docs/en-US/pricing/free-plan · https://zeabur.com/changelogs/say-hello-to-the-serverless-plan · https://zeabur.com/pricing · https://zeabur.com/docs/en-US/compliance/fair-use-guidelines · https://zeabur.com/docs/en-US/deploy/methods/dockerfile
- https://vercel.com/docs/plans/hobby · https://vercel.com/docs/functions/limitations
- Oracle Cloud Free Tier FAQ pages (always-free + card verification) via today's search
- Fly.io docs (credit-card-on-file statement) via today's search

Third-party / secondary (used only where labelled):
- https://freetier.co/directory/products/leapcell ("Credit card Not required", 2026)
- snapdeploy.dev free-hosting comparisons (Back4App "60 minutes" claim, 2026)
- https://www.acciyo.com/wispbyte-com-faq (third-party FAQ aggregation)
- corpdev.org 2026-02-17 (Koyeb/Mistral acquisition claim)
