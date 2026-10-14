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
