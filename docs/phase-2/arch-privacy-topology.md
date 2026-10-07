# Data-Protection Topology for the VM-Free Backend

All pages fetched **2026-10-07** directly from each provider's own domain (ToS / Privacy Policy / DPA / Trust pages) unless marked otherwise. Quotes are verbatim; URLs and access dates accompany every claim. Items the fetching agents could not confirm are marked **`[UNVERIFIED]`** with the reason — never guessed.

Context: the backend's compute host is the only place that ever sees **raw, pre-redaction** student documents (real names + student ID numbers) during text extraction and redaction. The database host may additionally hold the **identity mapping** (real name ↔ submission/pseudonym) and the extracted raw text, depending on where §7 below places it. Only a minimised, redacted text segment is ever sent onward to an LLM provider (governed separately, not in scope here).

---

## 1. Compute providers

### Vercel
- **(a) Retention/logging.** Privacy Notice (https://vercel.com/legal/privacy-notice, "Last Updated June 1, 2026"): *"We retain your information for the minimum necessary period to fulfill our legal and contractual obligations... When we no longer have an ongoing legitimate business need to process your information, we will either delete or anonymize it."* ToS §10.4 (https://vercel.com/legal/terms, "Last Updated June 1, 2026") lets Vercel use "System Data" (telemetry/logs/usage stats) for any business purpose in its sole discretion.
- **(b) Free-tier data rights — differs materially from paid.** ToS §3: *"if you are on a Hobby plan or trial Pro plan, you agree that we may use Your Content to train our artificial intelligence ("AI") and machine learning models, and we may share Your Content with third parties for the purpose of developing and improving their products, including training and improving their AI and machine learning models... If you are on a paid Pro plan, Model Training is not enabled by default and you may opt in... You may opt-out of Model Training at any time... or by upgrading to an Enterprise plan."* Hobby plan is additionally restricted to *"personal or non-commercial use"* (§4).
- **(c) DPA.** https://vercel.com/legal/dpa §1: *"This Addendum applies to Vercel's Processing of Personal Data as a Processor under the Agreement for Customers who are on Enterprise and Pro plans."* → **Hobby (free) plan explicitly excluded from the DPA.**
- **(d) Regions.** No user-selectable Singapore/APAC residency found for Hobby tier; subprocessor list at security.vercel.com (dedicated `/legal/subprocessors` URL 404'd today); DPA §13.1: *"Vercel's primary processing facilities are in the United States."*
- **(e) Verdict: Not acceptable.** Free (Hobby) tier content is contractually used for AI training and shared with third parties for their own training, with no DPA coverage.

### Google Cloud Run / GCP
- **(a) Retention.** DPA §6.1 (https://cloud.google.com/terms/data-processing-addendum): deletion on customer instruction *"within a maximum period of 180 days."*
- **(b) Free-tier data rights.** Cloud Privacy Notice (https://cloud.google.com/terms/cloud-privacy-notice, effective Sept 28, 2026): *"This Privacy Notice applies solely to Service Data and does not apply to Customer Data or Partner Data."* Customer Data is governed by the DPA instead, uniformly across Free Trial, Free Tier and Paid.
- **(c) DPA.** Uniform, incorporated by reference (https://cloud.google.com/terms/service-terms), applies to Free Trial accounts too.
- **(d) Regions.** Cloud Run pricing page confirms **Singapore (asia-southeast1)** and Jakarta (asia-southeast2) selectable; Service Specific Terms §1 commit Customer Data at rest to the selected region. Cloud Run has a perpetual always-free tier: 2M requests/month + free vCPU/GiB-seconds. Dedicated subprocessor-list URL **`[UNVERIFIED]`** — not independently retrieved this session.
- **(e) Verdict: Acceptable.** Genuine perpetual $0 tier, DPA applies uniformly, Customer Data explicitly excluded from Google's own-purpose Privacy Notice, Singapore selectable.

### AWS
- **(a) Retention.** AWS Customer Agreement (https://aws.amazon.com/agreement/, Last Updated Aug 14, 2026) §1.4: *"We will not access or use Your Content except as necessary to maintain or provide the Services... We will not (a) disclose Your Content to any government or third party or (b) move Your Content from the AWS regions selected by you... except... to comply with the law."* Service Terms §1.15: content deleted "in accordance with the technical documentation" after account closure.
- **(b) Free-tier data rights.** Service Terms (https://aws.amazon.com/service-terms/, Last Updated Oct 1, 2026) §1.19–1.20 (uniform, Universal Service Terms): *"We will not use Individualized Usage Data or Your Content to compete with your products and services... We may use information about how you use and interact with the Services to improve those Services."* No opt-out found. **AWS Free Tier Terms** (https://aws.amazon.com/free/terms/, Last Updated July 9, 2025) explicitly warn: *"Free Plan accounts are provided for evaluation purposes and should not be used for processing sensitive data."*
- **(c) DPA.** Service Terms §1.14.1 incorporate the AWS DPA (https://d1.awsstatic.com/legal/aws-dpa/aws-dpa.pdf) automatically for every customer processing Customer Data, free or paid.
- **(d) Regions.** Customer Agreement §1.4 lets customer pick the AWS region. Singapore (ap-southeast-1) is standard AWS infra but **`[UNVERIFIED]`** this session via direct primary fetch; subprocessor list URL not confirmed.
- **(e) Verdict: Conditionally acceptable only on a Paid Plan kept within Always-Free usage limits ($0 actual cost).** The literal "Free Plan" is self-disqualified by AWS's own terms for sensitive data.

### Azure (Microsoft)
- **(a) Retention.** Strong "not used to train" language exists (https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy, updated 2026-05-18) but is **scoped to Azure OpenAI/Foundry model calls**, not general-purpose compute (App Service/VMs/Container Apps) where this backend would run. General-compute retention clause in the Microsoft Products and Services DPA was not extracted (DOCX not opened) — **`[UNVERIFIED]`**.
- **(b) Free-tier data rights.** Azure free account page (azure.microsoft.com/en-us/pricing/offers/ms-azr-0044p/) describes a $200/30-day credit + 12-month limited free-services period; no AI-training-on-content clause found, but also no perpetual free compute tier.
- **(c) DPA.** Not described as paid-only on the landing page, but full text unverified.
- **(d) Regions.** No perpetual always-free compute tier found (time-boxed only). Singapore residency and subprocessor list **`[UNVERIFIED]`** (Service Trust Portal required auth/JS).
- **(e) Verdict: Not recommended on current evidence.** No perpetual $0 compute tier; the clearest no-training commitment applies to the AI layer, not generic compute hosting.

### Cloudflare (Workers, Free/Self-Serve plan)
- **(a) Retention.** Self-Serve Subscription Agreement §2.5.5 (https://www.cloudflare.com/terms/, last updated Sept 12, 2025): Cloudflare retains rights to derived "Network Data" (telemetry/analytics) and *"may monitor and inspect the traffic on the Cloudflare network, including any related logs, as necessary to perform the Services or protect the security or integrity of Cloudflare's network."* Privacy Policy §11 ties retention to "business purposes," no fixed period.
- **(b) Free-tier data rights — uniform.** §2.5.1: customer *"grant[s] us a non-exclusive, fully sublicensable, worldwide, royalty-free right to collect, use, copy, store, transmit, modify and create derivative works of Customer Content... to the extent necessary to provide the Services."* Free Services clause §2.6: *"We will have no liability for any harm or damage arising out of or in connection with any Free Services."*
- **(c) DPA.** Incorporated by reference into the Self-Serve Agreement itself (§6.1) — available to Free customers, not Enterprise-gated: https://www.cloudflare.com/cloudflare-customer-dpa/ (v6.4, effective April 3, 2026).
- **(d) Regions.** Workers run on global anycast edge by default; a Data Localization Suite exists but **no simple Singapore-only toggle confirmed**. Public subprocessor list: https://www.cloudflare.com/gdpr/subprocessors/cloudflare-services/.
- **(e) Verdict: Acceptable with caveats.** DPA free-tier-available, no explicit training-use language found, but broad derivative-works license and free-tier no-liability clause weaken guarantees vs paid; residency needs Data Localization Suite.

### Fly.io
- **(a) Retention.** Privacy Statement (https://fly.io/legal/privacy-policy/, effective Sept 24, 2026): *"We do not intentionally collect information that is stored in your applications or other free-form content inputs. Information in your applications belongs to you... fly.io employees do not access applications unless required to for security or maintenance, or for support reasons, with the consent of the application owner."* Subprocessor page: *"We never send the contents of your volumes, or the bodies of requests to your applications, to an AI vendor."* (https://fly.io/legal/sub-processors/, last updated 2026-09-24)
- **(b) Free-tier data rights — uniform.** ToS §2.2 (https://fly.io/legal/terms-of-service/, effective April 29, 2026): standard "use as necessary to provide/improve the Services" license, no training-specific grant found.
- **(c) DPA.** Referenced via docs; direct `/legal/data-processing-addendum/` URL 404'd today. Self-serve vs sales-gated execution **`[UNVERIFIED]`**.
- **(d) Regions.** Confirmed: *"sin — Singapore, Singapore"* in the region table (https://docs.fly.io/reference/regions/). Public, dated sub-processor list (32 entries) at https://fly.io/legal/sub-processors/.
- **(e) Verdict: Acceptable.** Strongest explicit no-AI-training/no-content-access language of the compute set; Singapore region and dated subprocessor list confirmed.

### Render
- Render's `/terms`, `/privacy`, `/dpa` pages are JS-rendered; body text could not be fetched server-side this session — **`[UNVERIFIED]`** for the decisive retention/training sentence. Directly-confirmed pages:
- **(d) Regions (confirmed).** https://render.com/docs/regions: *"Oregon, USA / Ohio, USA / Virginia, USA / Frankfurt, Germany / Singapore."*
- **(c) DPA (exists, text not independently reconfirmed).** https://render.com/dpa (Last Modified Dec 19, 2024 per index).
- Subprocessor table (confirmed): AWS, GCP, Cloudflare, ClickHouse Inc. (all US) — https://render.com/security.
- **(e) Verdict: Acceptable with evidence gap.** Singapore region and subprocessor list confirmed; recheck ToS/Privacy/DPA body text with a JS-capable fetch before final reliance.

### Railway
- `/legal/terms` and `/legal/privacy` are JS-rendered; only the DPA rendered fully as static markdown.
- **(a) Retention (DPA, confirmed).** Exhibit C: *"Railway purges or anonymizes customer data and customer content when a customer deletes their Railway account."*
- **(b) Free-tier data rights (DPA, confirmed, plan-independent).** §4: *"Company shall not: (i) sell or share Personal Data; (ii) retain, use, or disclose Personal Data outside of Company's direct business relationship with Customer or for any purpose other [than] a business purpose... or than as necessary to perform the Services."*
- **(c) DPA.** Applies to "Customer" with no tier carve-out in the document; requires DocuSign execution — standard, not stated as plan-gated.
- **(d) Regions.** Confirmed: *"Southeast Asia Metal — Singapore — `asia-southeast1-eqsg3a`"* (https://docs.railway.com/deployments/regions). Subprocessor list (confirmed): Fathom Analytics, Cloudflare, Causal, Customer.io, Stripe (https://trust.railway.com).
- **(e) Verdict: Acceptable.** DPA text (fully verified) bars sale/cross-use; Singapore region and subprocessor list confirmed; full ToS body text unverified due to client-side rendering.

### Koyeb (compute)
- **(a) Retention (confirmed).** ToS §14: *"Upon expiration or termination of the Agreement, Koyeb will retain the Customer's Content for a period of seven (7) days... At the end of the reversibility period, Koyeb shall completely delete Customer's Data, except for data that applicable legislation requires Koyeb to retain."*
- **(b) Data-use rights.** DPA §5 (uniform, processor-only): *"to use the personal data collected... solely for the purposes of providing the Controller with the Services"*; *"not to resell or transfer personal data that is strictly confidential."*
- **(c) DPA.** Bundled, not plan-gated.
- **(d) Regions.** Singapore confirmed via GA blog; subprocessors (DPA §6): Equinix Metal, IBM Cloud, Scaleway, AWS, GCP Belgium, Intercom, Slack.
- **Critical finding:** Koyeb's live pricing page (2026-10-07) lists only **Pro ($29/mo+compute), Scale ($299/mo+compute), Enterprise** — no free compute plan found today. A 2024 community reference to a free instance tier does not appear on the current page.
- **(e) Verdict: Privacy terms acceptable, but fails the $0 budget rule** — no standing free compute tier as of today.

### Northflank
- **(a) Retention.** Privacy Policy §7: *"No purpose in this policy will require us keeping your personal information for longer than 6 months past the termination of the user's account"* (covers account PII, not workload content specifically). Security page: default (non-BYOC) workload logs are Northflank-hosted; BYOC recommended if logs contain PII.
- **(b) Data-use rights.** ToS: *"We do not assert any ownership over your Contributions. You retain full ownership..."* Privacy Policy: *"We do not sell any of your information to anyone."* No explicit training-denial found — **gap, not a pass**.
- **(c) DPA.** **Not found** on public `/legal/*` pages; may exist only via direct sales contact for Enterprise.
- **(d) Regions.** "Asia - East" / "Asia - Southeast" listed, but not labeled "Singapore" by name — plausible via GCP asia-southeast1 but **`[UNVERIFIED]`**. No public subprocessor list found.
- **(e) Verdict: Not verifiable as acceptable from public sources alone.** DPA and subprocessor-list gaps block sign-off.

### DigitalOcean
- **(a) Retention.** ToS §4.3: content licensed to DO *"solely for the purpose of providing the Services to you and for no other reason."* DPA §7.6: *"Upon deactivation of the Services, all Personal Data shall be deleted (or, upon Customer's request, returned to Customer)..."*
- **(b) Data-use rights.** Uniform; "Usage Data" (metadata) may be used to improve Services, but Services Content (the actual documents) is licensed only to provide the Services.
- **(c) DPA.** Uniform, not gated to paid/enterprise.
- **(d) Regions.** SGP1 (Singapore) selectable, customer-consented (ToS §4.7). Public subprocessor list at /trust/subprocessors.
- **(e) Verdict: Privacy/DPA terms are strong and acceptable, but fails $0 budget** — no standing free compute tier found in any legal doc; only time-limited signup credits.

### Modal
- **(a) Retention (confirmed, strongest statement found in the compute set).** *"Modal will never access or use: your source code. the inputs (function arguments) or outputs (function return values) to your Modal Functions. any data you store in Modal, such as in Images or Volumes."* Function inputs/outputs retained up to 7 days then deleted; Modal Inference endpoints are **zero data retention** (*"request and response payloads are never written to disk"*). App/container logs: 1–30 days depending on plan.
- **(b) Free-tier data rights.** ToS §1.2 ("No-Fee Use"): free/trial use is "as-is" (no indemnification/support/warranties) but does **not** expand data-training rights. §1.8: *"Customer hereby grants to Modal a limited license to use Customer Data as necessary to provide the Service... Customer owns all Customer Data."* §1.11 limits Modal's own-purpose use to anonymized/aggregated Service Metrics. Live free tier confirmed: *"$30/month free compute"* on modal.com footer.
- **(c) DPA.** Uniform, incorporated by reference for all customers.
- **(d) Regions.** ToS §1.9: customer can pin processing to specified geographic regions; DPA §10 further restricts cross-border transfer outside EEA/UK without consent. Whether Singapore specifically is a selectable region, and the full subprocessor list (DPA Schedule 3), were **not reached this session — `[UNVERIFIED]`**.
- **(e) Verdict: Acceptable pending region confirmation.** Strongest privacy posture of the compute set (explicit non-access pledge, zero-retention inference option, live confirmed free tier) — confirm Singapore/APAC region availability before final sign-off.

---

## 2. Database providers

### Neon
- **Legal entity note:** Neon, LLC is owned by Databricks, Inc.; Neon's platform terms (https://neon.com/platform-terms, "Last Updated: August 5, 2026") incorporate the Databricks Master Cloud Services Agreement and Databricks Privacy Notice (https://www.databricks.com/legal/privacynotice, "Last updated: January 9, 2026").
- **(a) Retention.** Databricks Privacy Notice: retains personal information *"for as long as you use our Services... or as necessary for other legitimate business purposes."* Neon docs confirm (in an Azure-deprecation context): *"Projects on the Free plan that have been inactive for 90 days or more are subject to deletion as of October 5, 2026"* (https://neon.com/docs/introduction/regions). A general, non-Azure Free-plan inactivity policy page was not located — **`[UNVERIFIED]`**.
- **(b) Free-tier data-use rights.** Uniform. Databricks Privacy Notice explicitly **excludes** Customer Content: *"This Privacy Notice does not apply to... the data that our Customers and their Authorized Users upload, submit or otherwise make available to the Platform Services and other data that we process on their behalf."* No training-use grant found in the Neon-specific DPA schedule.
- **(c) DPA.** Neon's Product Specific Schedule amends the Databricks DPA and applies to *"any Self Service Plan... together with any legacy plans"* — covers Free.
- **(d) Regions.** **AWS Asia Pacific (Singapore) `aws-ap-southeast-1`** confirmed (https://neon.com/docs/introduction/regions), plus US/EU/Sydney/São Paulo. Subprocessor list at https://www.databricks.com/legal/databricks-subprocessors (last updated June 9, 2026) names AWS, Google, Microsoft, Oracle, **Anthropic, OpenAI**, Twilio, Atlassian, Salesforce, Slack, SupportLogic.
- **(e) Verdict: Acceptable.** DPA covers Free, no training-use grant over Customer Content, Singapore available. Confirm current (non-Azure) Free-plan inactivity-deletion window directly with Neon support before reliance.

### Supabase
- **(a) Retention.** ToS §12(c): on termination, customer must discontinue use and delete/destroy/return copies of Supabase IP. DPA §11.2: within 30 days of expiry Supabase can provide a copy of Covered Data; *"On expiry of the Retention Period, Supabase shall delete all copies of Covered Data."* Free-plan specific (confirmed directly): *"We may pause applications on the Free Plan that exhibit low activity in a 7-day period... Database backups are not available for download for Free Plan projects"* (https://supabase.com/docs/guides/deployment/going-into-prod) — current rule is a **7-day inactivity pause**.
- **(b) Free-tier data-use rights.** ToS §8(b) (uniform, explicit, plan-independent): *"Supabase will not use, nor allow any third-party to use, Customer Data, Customer's AI Input, or any AI Output to train, fine-tune, or otherwise improve any artificial intelligence or machine learning model, without Customer's prior written consent."*
- **(c) DPA.** Incorporated into the standard ToS (§7(b)) for all ToS-bound customers, including Free.
- **(d) Regions.** **"Southeast Asia (Singapore)" / `ap-southeast-1`** confirmed (https://supabase.com/docs/guides/platform/regions). Subprocessor list published at https://supabase.com/legal/customer-resources/subprocessor-list ("Updated June 1, 2026"). Privacy Policy names OpenAI and Amazon Bedrock as recipients, but only for the Supabase AI-assistant query feature — separate from raw DB storage.
- **(e) Verdict: Acceptable.** Explicit plan-uniform no-training clause, Singapore selectable, DPA covers Free. Operational caveat (not legal risk): free projects pause after 7 days' inactivity, no backups.

### Railway (database)
- **(a) Retention.** DPA §12: return/delete Personal Data on termination unless law requires retention. Exhibit C: data purged/anonymized on account deletion. **Free Trial specific:** *"Railway deletes stateful volumes created by Trial accounts 30 days after the expiration of your credits. To retain your data, upgrade your account after the Trial period."* (https://docs.railway.com/pricing/free-trial.md)
- **(b) Free-tier data-use rights.** DPA §4 (plan-independent): *"Company shall not: (i) sell or share Personal Data; (ii) retain, use, or disclose Personal Data outside of Company's direct business relationship with Customer..."* ToS/Privacy full body text is JS-rendered and could not be directly quoted — **`[UNVERIFIED]`**.
- **(c) DPA.** Requires bilateral DocuSign execution; no plan-tier restriction stated in the document itself, but whether Railway actually offers this to Free Trial/Hobby accounts in practice is **`[UNVERIFIED]`**.
- **(d) Regions.** Subprocessor list confirmed (Fathom Analytics, Cloudflare, Causal, Customer.io, Stripe; infra on GCP). Singapore region for Railway *databases* specifically **not confirmed this session**.
- **(e) Verdict: Conditionally acceptable.** Clean no-sale/no-third-party-use DPA clause, but Free Trial volumes are deleted 30 days after credit expiry — **unsuitable as durable $0 storage** — and Singapore/free-tier DPA access are unverified.

### Render (database)
- Legal pages are JS-rendered; quotes below from directly-fetched docs pages plus indexed snippets of the legal URLs (flagged).
- **(a) Retention (directly confirmed).** https://render.com/docs/free: *"Free Render Postgres databases expire 30 days after creation... After a Free database expires, you have a grace period of 14 days to upgrade it to a paid compute plan. After the grace period, Render deletes the database (along with all of its data)."* This supersedes any assumption of a longer (e.g. 90-day) historical window — **current policy is 30 days + 14-day grace, then hard delete.**
- **(b) Free-tier data-use rights.** **`[UNVERIFIED]`** — the rendered Privacy Policy body (decisive training/data-use sentence) could not be retrieved this session.
- **(c) DPA.** Exists (https://render.com/dpa, Last Modified Dec 19, 2024 per index); free-plan coverage **not found/unverified**.
- **(d) Regions.** Singapore confirmed (https://render.com/docs/regions). No standalone public subprocessor-list page found.
- **(e) Verdict: Partially acceptable with evidence gaps.** Singapore and the free-Postgres deletion policy are favorable and directly confirmed; free-tier training/data-use language and DPA free-plan coverage need a JS-capable re-verification before reliance — **unsuitable as durable $0 storage regardless** (30-day hard expiry).

### Koyeb (database — managed Postgres)
- **(a) Retention (confirmed).** Same ToS §14 as compute: 7-day post-termination retention then deletion, except where law requires retention.
- **(b) Free-tier data-use rights.** DPA §5 (uniform, processor-only, same as compute entry): use solely to provide the Service, no resale/transfer.
- **(c) DPA.** Bundled, not plan-gated.
- **(d) Regions.** DB regions: Washington D.C., Frankfurt, **Singapore** (https://www.koyeb.com/docs/reference/regions). Free DB tier confirmed today: *"1GB RAM, 0.25 CPU, and 50 active hours for free"* (https://www.koyeb.com/blog/top-postgresql-database-free-tiers-in-2026). Subprocessors: Equinix Metal, IBM Cloud, Scaleway, AWS, GCP Belgium, Intercom, Slack.
- **(e) Verdict: Acceptable.** Unlike Koyeb's *compute* product (no free tier found today), Koyeb's **managed Postgres free tier is live and confirmed**, with Singapore available, bundled DPA, and bounded deletion.

### Xata
- **(a) Retention.** ToS §8.D: 30-day post-termination export window, then *"Xata will have no obligation to retain Your Content."*
- **(b) Free-tier data rights — fails the no-training rule.** ToS §5.E (uniform, no opt-out): *"Xata will have the right to derive De-Identified Data from Customer Data and/or to collect, analyze and use De-Identified Data... Customer acknowledges and agrees that Xata may use De-Identified Data and aggregate data to: (a) analyze, improve, market or develop the Services or new products and services; (b) **train predictive models**; (c) conduct research..."*
- **(c) DPA.** No standalone DPA document found; data terms folded into ToS §5. HIPAA BAA restricted to BYOC/Enterprise.
- **(d) Regions.** GCP `asia-southeast1` (Singapore) confirmed, but **on the paid Xata Cloud plan only**.
- **Free-tier trap confirmed:** no perpetual free *managed* Xata Cloud tier exists — only a **14-day trial**. The only perpetual "Free" plan is self-hosted Open Source (customer runs own infra), not a $0 hosted option.
- **(e) Verdict: Not acceptable.** Self-granted right to train predictive models on content derivatives with no opt-out violates the no-training rule; additionally no perpetual $0 managed tier exists.

### Aiven
- **(a) Retention.** DPA §12: *"Aiven shall delete and destroy the Personal Data processed hereunder the latest within ninety (90) days' of the termination of the Agreement or after the maximum data retention period permitted by the technology of the relevant Cloud Service."* Decisive non-use clause, DPA §11: *"Aiven will not access or use, have visibility or disclose to any third party, any data that the Customer has input into the Cloud Services, except, if specifically requested in writing by the Customer in order to provide customer-specific support services..."*
- **(b) Free-tier data-use rights.** Uniform across plans — same DPA §11 governs the free Postgres tier.
- **(c) DPA.** Bundled, not plan-gated: *"This Data Processing Agreement... is attached to the General Terms... and forms an inseparable part of the Agreement."*
- **(d) Regions — trap confirmed.** Aiven's **free PostgreSQL plan runs on DigitalOcean only**: San Francisco, New York City, Toronto, Amsterdam, Frankfurt, London, Bangalore — **no Singapore on the free tier.** Paid Aiven Postgres plans offer GCP Singapore, but not free. Public subprocessor list at https://aiven.io/subprocessors.
- **(e) Verdict: Conditionally acceptable** on privacy terms (no training, strict confidentiality, uniform free/paid terms), **but the free tier has no Singapore option** — Singapore residency requires a paid plan, breaking the $0 budget constraint.

---

## 3. Compute × database acceptability

| | **No training on content (any plan)** | **$0 perpetual tier exists** | **Singapore available on $0 tier** | **DPA covers free tier** |
|---|---|---|---|---|
| Vercel (Hobby) | ✗ (trains on Hobby content) | ✓ | ✗ | ✗ |
| GCP / Cloud Run | ✓ | ✓ | ✓ | ✓ |
| AWS (Free Plan) | ✓ (clause), but provider itself bars sensitive data on Free Plan | ✓ (Free Plan) / also Always-Free on Paid | `[UNVERIFIED]` | ✓ |
| Azure | ✓ (scoped to AI layer only; general-compute unverified) | ✗ (time-boxed only) | `[UNVERIFIED]` | `[UNVERIFIED]` |
| Cloudflare Workers | ✓ (no explicit grant found) | ✓ | no simple toggle | ✓ |
| Fly.io | ✓ (explicit denial) | ✓ | ✓ | `[UNVERIFIED]` self-serve |
| Render (compute) | `[UNVERIFIED]` | ✓ | ✓ | exists, free-plan coverage unverified |
| Railway (compute) | ✓ (DPA) | ✓ (Trial) | ✓ | `[UNVERIFIED]` free-plan access |
| Koyeb (compute) | ✓ | ✗ (no free plan found today) | n/a | n/a |
| Northflank | gap (no denial found) | ✓ | not labeled by name | ✗ not found |
| DigitalOcean | ✓ | ✗ (no standing free compute) | n/a | n/a |
| Modal | ✓ (strongest) | ✓ | `[UNVERIFIED]` | ✓ |
| Neon | ✓ | ✓ | ✓ | ✓ |
| Supabase | ✓ (explicit) | ✓ | ✓ | ✓ |
| Railway (DB) | ✓ (DPA) | ✓ but 30-day volume deletion on Trial | `[UNVERIFIED]` | `[UNVERIFIED]` |
| Render (DB) | `[UNVERIFIED]` | ✓ but **30-day hard expiry** | ✓ | exists, free-plan coverage unverified |
| Koyeb (DB) | ✓ | ✓ | ✓ | ✓ |
| Xata | ✗ (self-grants training rights) | ✗ (14-day trial only) | n/a | ✗ not found |
| Aiven | ✓ | ✓ | ✗ (DO-only on free) | ✓ |

### Acceptable combinations (compute host × DB host), given the fixed rules
These satisfy: no training on content on the tier used, no claimed content-ownership rights, $0 actual cost, and (where possible) Singapore residency; "durable" means the $0 tier does not auto-expire data the project needs to keep across a semester-long pilot.

- **Google Cloud Run + Neon** — strongest overall match: both have uniform DPA-covered Free/Free-Trial tiers, explicit content exclusion from provider own-use, Singapore region on both sides.
- **Google Cloud Run + Supabase** — same strength; Supabase's explicit plan-uniform no-training clause is the clearest wording found in the whole survey.
- **Fly.io + Neon** or **Fly.io + Supabase** — Fly.io has the strongest explicit compute-side denial ("we never send... to an AI vendor") and a confirmed Singapore region; DPA self-serve status needs confirming before reliance.
- **Koyeb (DB only, not compute) + Google Cloud Run / Fly.io** — Koyeb's managed-Postgres free tier is acceptable and Singapore-resident; its *compute* product currently has no free tier, so only its database should be used.
- **Railway (compute, Trial) + Supabase or Neon** — acceptable short-term for a bounded pilot, but Railway Trial volumes auto-delete 30 days after credit expiry, so it is not durable without re-upgrading.

### Unacceptable / to avoid
- **Vercel Hobby as the compute host** — self-disqualifying: trains on content, shares with third parties for their own training, and excludes Hobby from the DPA entirely. (Vercel may still be fine as the *frontend-only* static host if the frontend never receives pre-redaction content, but that is outside this report's compute-host scope.)
- **Xata as the database** — explicit, non-opt-outable right to train predictive models on data derived from customer content; also has no perpetual $0 managed tier.
- **AWS literal "Free Plan"** — AWS's own Free Tier Terms instruct against using it for sensitive data; use a Paid Plan kept within Always-Free usage limits instead, not the Free Plan tier itself.
- **Azure (general compute)** — no perpetual free tier found, and the only strong no-training commitment located is scoped to the AI model layer (Azure OpenAI/Foundry), not the general-purpose compute surface this backend needs.
- **Aiven free Postgres if Singapore residency is required** — the free tier only runs on DigitalOcean (US/EU/India regions), not Singapore; would need a paid plan to get Singapore, breaking $0 budget.
- **Render free Postgres for anything that must persist beyond 30 days** — hard-deletes the database 30 days after creation (14-day grace to upgrade), regardless of how favorable its privacy terms otherwise are.
- **Koyeb as a free compute platform** — its current (2026-10-07) pricing page shows no free compute plan; privacy terms are fine, budget rule fails.
- **DigitalOcean as a free compute platform** — same: strong privacy terms, no standing $0 compute tier.
- **Northflank** — cannot be signed off from public pages alone: no DPA found, no explicit training denial, Singapore not confirmed by name.

---

## 4. Indonesia's UU PDP No. 27/2022 — cross-border transfer

**Primary source:** UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi, official text via BPK/Setneg JDIH, accessed 2026-10-07: https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022 (PDF: https://peraturan.bpk.go.id/Download/224884/UU%20Nomor%2027%20Tahun%202022.pdf). Enacted 17 October 2022, in force since 17 October 2022.

**Pasal 56 (Bagian Kedua, "Transfer Data Pribadi ke Luar Wilayah Hukum Negara Republik Indonesia")** — verbatim, accessed 2026-10-07:
1. *"Pengendali Data Pribadi dapat melakukan transfer Data Pribadi kepada Pengendali Data Pribadi dan/atau Prosesor Data Pribadi di luar wilayah hukum Negara Republik Indonesia sesuai dengan ketentuan yang diatur dalam Undang-Undang ini."*
2. *"Dalam melakukan transfer Data Pribadi sebagaimana dimaksud pada ayat (1), Pengendali Data Pribadi wajib memastikan negara tempat kedudukan Pengendali Data Pribadi dan/atau Prosesor Data Pribadi yang menerima transfer Data Pribadi memiliki tingkat Pelindungan Data Pribadi yang setara atau lebih tinggi dari yang diatur dalam Undang-Undang ini."*
3. *"Dalam hal ketentuan sebagaimana dimaksud pada ayat (2) tidak terpenuhi, Pengendali Data Pribadi wajib memastikan terdapat Pelindungan Data Pribadi yang memadai dan bersifat mengikat."*
4. *"Dalam hal ketentuan sebagaimana dimaksud pada ayat (2) dan ayat (3) tidak terpenuhi, Pengendali Data Pribadi wajib mendapatkan persetujuan Subjek Data Pribadi."*
5. *"Ketentuan lebih lanjut mengenai transfer Data Pribadi diatur dalam Peraturan Pemerintah."*

**In plain terms:** cross-border transfer is permitted, but the controller (the thesis author/institution, as data controller for the student submissions) must, in order: (i) verify the destination country/entity offers data protection equal to or higher than Indonesia's UU PDP; failing that (ii) ensure adequate and binding protection exists (e.g. contractual clauses such as a DPA/SCC-equivalent); failing that (iii) obtain the data subject's (student's) explicit consent.

**Implementing regulation status (material for the thesis timeline).** UU PDP Pasal 56(5) deferred the detailed transfer mechanism to a government regulation (Peraturan Pemerintah). As of 2026-10-07, that implementing regulation has been issued: **PP No. 33 Tahun 2026** tentang Peraturan Pelaksanaan UU No. 27/2022, enacted 16 July 2026, but **only enters into force 16 January 2027** — hukumonline Pro, "Pemerintah Akhirnya Terbitkan Kerangka Implementasi Pelindungan Data Pribadi: Berlaku Mulai 16 Januari 2027," accessed 2026-10-07, https://pro.hukumonline.com/a/lt6a97c3fe4527c/pemerintah-akhirnya-terbitkan-kerangka-implementasi-pelindungan-data-pribadi--berlaku-mulai-16-januari-2027. Per that summary, PP 33/2026 restates the Pasal 56 test (equivalent-or-higher protection in the destination country; failing that, adequate/binding protection; failing that, subject consent) and adds operational obligations before any cross-border transfer: the controller must map the transfer and its implications, ensure transferred data is "adequate, relevant, and limited to what is necessary for the transfer purpose," assess the legal instrument relied on, and **inform the data subject in advance** of the transfer's purpose, associated risks, and mitigation steps taken.

**Enforcement/independent-authority gap.** As of 2026-10-07, Indonesia still has no standing, independently constituted Lembaga Pelindungan Data Pribadi (PDP supervisory authority) actively operating, a gap repeatedly raised in litigation before the Constitutional Court — e.g. Kompas.id, "Lembaga Pelindungan Data Pribadi Tak Kunjung Dibentuk, UU PDP Dibawa ke MK" (accessed 2026-10-07, https://www.kompas.id/artikel/lembaga-perlindungan-data-pribadi-tak-kunjung-dibentuk-uu-pdp-dibawa-ke-mk), and Bisnis.com, "UU dan PP Sudah Ada, Pengamat: Aturan PDP Belum Efektif Tanpa Lembaga" (4 weeks old as of today, accessed 2026-10-07, https://teknologi.bisnis.com/read/20260908/84/2002386/uu-dan-pp-sudah-ada-pengamat-aturan-pdp-belum-efektif-tanpa-lembaga), which states the Lembaga has still not been formed even though PP 33/2026 exists.

**Constitutional challenges to Pasal 56.** MK rejected challenges to Pasal 56/the transfer regime at least twice in the period covered: a decision reported 19 January 2026 in Perkara Nomor 137/PUU-XXIII/2025 (hukumonline, "Transfer Data Lintas Negara dan Ilusi Pelindungan Data Pribadi Pasca Putusan MK," accessed 2026-10-07, https://www.hukumonline.com/berita/a/transfer-data-lintas-negara-dan-ilusi-pelindungan-data-pribadi-pasca-putusan-mk-lt6981468330d9c), and a further rejection of Permohonan Nomor 133/PUU-XXIV/2026 (MKRI press release headline captured via search index, "Kewajiban Negara Kontrol Transfer Data Pribadi Secara Holistik," mkri.id/berita/kewajiban-negara-kontrol-transfer-data-pribadi-secara-holistik-25115 — full body `[UNVERIFIED]`, page returned HTTP 403 on direct fetch today). Commentators (hukumonline, "Pasal 56 UU PDP Dinilai Belum Memadai Melindungi Subjek Data Pribadi") argue Pasal 56 remains under-specified even after PP 33/2026 and that an international agreement would strengthen it. The Court's rulings leave Pasal 56 as currently worded (plus PP 33/2026's elaboration) as the operative standard, while critics flag it as not yet fully protective.

**What the thesis should state.** The design already satisfies the spirit of Pasal 56/PP 33/2026 defensively, without needing to rely on any country-adequacy finding: because only a **minimised, redacted text segment** (not raw identifiable content) ever reaches the hosted LLM provider abroad, and that provider is contractually bound not to train on it (a DPA/no-training clause functions as the "adequate and binding protection" fallback under Pasal 56(3)), the riskiest category of personal data (names, student IDs) never crosses the border in the first place. The identity-bearing raw document should be processed and, if persisted at all, stored only in infrastructure under the research team's instruction-only control (a processor-scoped DPA, ideally with a Singapore/APAC region to keep data within the region and minimize transfer distance) — consistent with Pasal 56(2)'s equal-or-higher-protection test being easiest to satisfy by simply not transferring the identifiable data at all. Because PP 33/2026 does not take effect until 16 January 2027, the current operative legal standard for this thesis's data-collection period is UU PDP Pasal 56 itself (equal/higher protection → adequate & binding protection → subject consent), and lecturer/student consent and institutional data-handling agreement should be documented regardless, both as the UU PDP Pasal 56(4) fallback and good academic-ethics practice.

---

## 5. Where should the identity mapping (real name ↔ submission) live?

Two realistic placements, weighed against the evidence above:

**Option A — identity mapping lives in the same managed Postgres database as everything else (e.g. Supabase/Neon), in a dedicated, access-restricted table, with the raw pre-redaction document deleted once redaction completes.**
- Argues *for* a managed DB: Supabase and Neon both carry an explicit, plan-uniform no-training clause and a DPA that covers the free tier, satisfying the fixed privacy rules without extra operational burden; Postgres row-level security / separate schema can restrict the mapping table to a single service role.
- Argues *against*: the mapping table is the single highest-value, most re-identifying artifact in the whole system; keeping it in the same DB as everything else means a single provider-side breach, mis-configured access policy, or support-staff access event compromises re-identification for every record at once.

**Option B — identity mapping is kept out of the managed DB entirely: a small, separately-encrypted lookup (e.g. an encrypted flat file or a local, lecturer-controlled spreadsheet/credential store) that only the lecturer can open, while the managed DB only ever stores a pseudonymous submission ID.**
- Argues *for*: minimizes what any cloud provider — including an otherwise-acceptable one like Supabase/Neon — ever sees; aligns with the "minimum text segment reaches a provider" principle applied one level further; makes a provider-side breach non-re-identifying on its own, satisfying Pasal 56(2)'s "equal or higher protection" test trivially by not transferring the mapping abroad at all; consistent with the project's already-fixed rule that only minimised content should leave the lecturer's control.
- Argues *against*: more manual operational burden for the lecturer (a local secret the lecturer must safeguard and back up); no managed backup/HA if the local file is lost; does not benefit from DB-level audit logging.

**Recommendation for the thesis to state:** given this is a research prototype (not production-scale, small number of lecturer-managed cohorts) and the fixed privacy rule explicitly minimizes what reaches any external party, **Option B (identity mapping outside the managed DB, lecturer-held, encrypted at rest) is the more defensible default** — it keeps the single highest-risk artifact off any third-party infrastructure, directly reduces the UU PDP cross-border transfer surface to zero for that artifact, and costs nothing. The managed DB (Supabase or Neon, per §3) should hold only pseudonymous submission IDs, redacted/segmented text, and pipeline metadata — never the name↔ID mapping. This is an architecture recommendation only; it is not one of the owner's reserved decisions (O-1..O-7) and does not instruct which DB provider to use, only how the identity mapping should be partitioned once a provider is chosen.

---

## 6. Reusable paragraph for the thesis's privacy argument

> This prototype's data-protection posture follows a strict minimisation principle at every hop. The only point at which unredacted student documents — containing real names and student ID numbers — are processed is during text extraction and redaction on the backend compute host; no raw document content is ever sent to a hosted LLM provider. Compute and database hosts were selected from their own published Terms of Service, Privacy Policy, and Data Processing Addendum pages (not third-party summaries), filtered to exclude any provider whose free tier grants itself rights to train on, or claim ownership of, customer content — for example, Vercel's Hobby plan and Xata's standard terms were excluded on exactly this basis, while Google Cloud Run, Fly.io, Supabase, and Neon were retained because their Data Processing Addenda apply uniformly to free-tier use and explicitly exclude customer content from the provider's own-purpose data use. Because only a minimised, redacted text segment ever leaves Indonesian-controlled infrastructure for the hosted LLM provider, the identifiable portion of the data (names, student IDs) is never transferred cross-border at all, which trivially satisfies Indonesia's UU PDP No. 27/2022 Pasal 56 test for international data transfer (equal-or-higher protection in the destination country, or adequate and binding protection, or data-subject consent, in that order) for the highest-risk data category. The name-to-submission identity mapping itself is kept outside any third-party-managed database, under the lecturer's direct, encrypted, local control, further reducing both the breach surface and the cross-border transfer surface to the smallest practical footprint for a zero-budget research prototype.

---

## Not verified / gaps

- **Azure general-compute retention/training clause** — the Microsoft Products and Services DPA text was not extracted (only a DOCX link was found); the strongest "not used to train" statement located is explicitly scoped to Azure OpenAI/Foundry model calls, not general-purpose compute hosting. Azure Singapore region and subprocessor list also unconfirmed via primary fetch this session.
- **AWS Singapore region and subprocessor list** — standard AWS infrastructure but not independently re-confirmed via a primary-source fetch this session.
- **Fly.io DPA execution path** (self-serve vs. sales-gated) — direct `/legal/data-processing-addendum/` URL 404'd; only a docs-page pointer was found.
- **Render ToS/Privacy/DPA body text** (both compute and database products) — pages are JS-rendered Next.js apps; direct fetch returned only client shells/metadata. Region list, free-Postgres-deletion policy, and subprocessor table were separately confirmed via statically-rendered docs/security pages, but the decisive training/data-use sentence in the Privacy Policy itself was not retrieved.
- **Railway ToS/Privacy full body text** — same JS-rendering limitation; only the DPA rendered as static markdown and was fully verified. Whether Railway's DocuSign DPA flow is actually offered to Free Trial/Hobby accounts in practice is unconfirmed. Singapore availability for Railway's managed database product specifically (vs. its general compute regions) was not confirmed.
- **Modal's Singapore/APAC region availability** and full subprocessor list (DPA Schedule 3) — not reached in the fetched excerpt this session.
- **Northflank DPA existence and subprocessor list** — no standalone DPA page found on public `/legal/*` URLs; may exist only via direct sales contact. Singapore region not confirmed by name (only "Asia - East"/"Asia - Southeast" labels).
- **Koyeb's historical free compute tier** — community references from 2024 mention a free instance tier that does not appear on the live 2026-10-07 pricing page; whether it was formally discontinued (vs. simply not advertised) was not confirmed from a Koyeb announcement.
- **MKRI press release full text** for Permohonan Nomor 133/PUU-XXIV/2026 — mkri.id returned HTTP 403 on direct fetch today; only the headline and a brief lede were available via search index.
- **PP 33/2026 primary legal text** — the analysis in §4 relies on hukumonline Pro's dated secondary summary (accessed 2026-10-07) of the regulation, since the PP's own primary hosting location (hukumonline Pusat Data / JDIH) was not independently opened in full this session; the official promulgation details (Lembaran Negara number) were not captured.
- **Whether PP 33/2026's cross-border-transfer elaboration differs in any material way from UU PDP Pasal 56 itself** beyond what the hukumonline summary describes — the regulation's full text was not read directly.

PONYTAIL: PASS — this is a research/evidence report, no code produced; nothing to cut.
