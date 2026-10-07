# Oracle Cloud Always Free ARM VM — runbook (OCI Ampere A1, arm64)

Scope: stand up one Always Free ARM VM for the thesis stack, from "no account" to an SSH prompt.
Every claim below was fetched from the URL cited, access date **2026-10-07 (UTC)** except where a page's own
"last modified" date is quoted. Sources are listed at the end as `[S1]`…`[S25]`.
Nothing here is a recommendation about the application; only infrastructure facts.

Access-date note: the task asked for citations dated 2026-10-06. The fetches ran at 2026-10-07 08:20 UTC
(session clock). Dates are reported as fetched, not rewritten.

---

## 0. What the tenancy actually gets (facts, not memory)

| Item | Current Always Free value | Source |
| --- | --- | --- |
| ARM shape name | `VM.Standard.A1.Flex` (OCI Ampere A1 Compute, Arm processor), labelled "Always Free-eligible" in the Console | [S1] |
| ARM allowance | "the first **1,500 OCPU hours and 9,000 GB hours per month** for free … **For Always Free tenancies, this is equivalent to 2 OCPUs and 12 GB of memory.**" | [S1] |
| Console/so-what | OCPU-hour arithmetic: 1,500 ÷ 744 h = 2.0 OCPU; 9,000 ÷ 744 h = 12.1 GB. An always-on 2 OCPU/12 GB instance consumes ~1,488 of the 1,500 OCPU-h and ~8,928 of the 9,000 GB-h in a 744-hour month. | derived from [S1] |
| Instance count | "you can create one or two OCI Ampere A1 Compute instances, **2 OCPUs total**" | [S1] |
| Shape limits (paid-flexible) | `VM.Standard.A1.Flex`: 1 OCPU minimum, 76 OCPU maximum; memory "1 GB or a value matching the number of OCPUs, whichever is greater", up to 64 GB/OCPU, 472 GB total | [S19] |
| Block volume | "a total of **200 GB** of Block Volume storage … **These amounts apply to both boot volumes and block volumes combined.**" Plus five volume backups. Home region only. | [S1] |
| Outbound data | 10 TB/month | [S1] |
| VCNs | Free Tier tenancies: up to 2 VCNs; one Always Free flexible Load Balancer at 10 Mbps | [S1] |
| Regions | Trial/free-tier/Pay-As-You-Go tenancies "are limited to one subscribed region" | [S17] |
| A1 regional exclusion | "You can create OCI Ampere A1 Compute instances in any availability domain, **except South Korea North (Chuncheon)**" | [S1] |

**Change alert (this is why any older note saying 4 OCPU/24 GB is wrong).** The Always Free A1 allowance is
**half of what it was**: the 2026-10-07 pages state 1,500 OCPU-h / 9,000 GB-h = **2 OCPU / 12 GB**. `oracle.com/cloud/free`
also states: "Arm-based Ampere A1 cores and **12 GB of memory** usable as 1 VM or 2 VMs. Always Free **1,500 OCPU hours
and 9,000 GB hours per month**." [S24]. The Free Tier doc adds the enforcement rule: if you hold more A1 than an Always
Free tenancy allows, "all existing OCI Ampere A1 Compute instances are **disabled and then deleted after 30 days**,
unless you upgrade to a paid account. To continue using your existing Arm-based instances as an Always Free user,
before your trial ends, ensure that you have **no more than 2 OCPUs and 12 GB of memory in total**." [S2]
Third-party reporting dates the cut to 2026-06-15 (InfoQ) and Oracle Community posts quote notices from
2026-07/08 — those are **not** primary and are not relied on here. [S1] itself (last modified 2026-06-12)
already carries the 2 OCPU/12 GB text.

### Idle reclamation — exact rule

Quote ([S1]):

> **Reclamation of Idle Compute Instances**
> Idle Always Free compute instances may be reclaimed by Oracle. Oracle will deem virtual machine and bare metal
> compute instances as idle if, during a 7-day period, the following are true:
> - CPU utilization for the 95th percentile is less than 20%
> - Network utilization is less than 20%
> - Memory utilization is less than 20% *(applies to A1 shapes only)*

In practice: the trigger is **all three simultaneously** across a **rolling 7-day window**, with 95th-percentile CPU
(so a single busy hour does not save a mostly-idle week on its own, though it moves the percentile). The docs say
"**may be** reclaimed", not "will be". A1 additionally carries the memory condition, which the AMD micro shape does not.
The thresholds are on the ***instance*** (95th percentile utilisation), so a light-but-steady workload is the
documented way to stay visible. Oracle documents **no** grace period and **no** appeal. The only documented lever
besides staying busy is upgrading: "Oracle doesn't charge for Always Free resources after you upgrade, and will only
charge you for resource usage above the Always Free limits." [S1]. Any claim that you can appeal a reclamation by
support ticket is **not in Oracle's documentation** — see Gaps.

Console check of your own consumption: **Governance & Administration → Tenancy Management → Limits, Quotas and Usage** [S1].

---

## 1. Console-only (account) — cannot be scripted

Everything in this section needs a browser, an email mailbox, a phone and a payment card. There is no API path.

1. Go to <https://signup.oraclecloud.com> [S15].
2. Country, name, valid email; solve the CAPTCHA ("I am human"), **Verify my email**, then open the mail
   "Confirm your Oracle cloud account" and click **Click Here**. The link is **valid for 30 minutes** [S15].
3. Password: min 8 chars, 1 lower, 1 upper, 1 numeric, 1 special; max 40; must not contain your name, email, spaces,
   or `` ~ < > \ ``. Then choose a **cloud account name** [S15].
4. **Choose the Home Region.** This is the irreversible step:

   > "Your home region is the geographic location where your account and identity resources will be created.
   > **You can't change this after signing up.**" [S15]
   > "Your home region contains your account information and identity resources. **It is not changeable after your
   > tenancy is provisioned.**" [S25]

   Always Free compute **must** be created in the home region: "You must create the Always Free compute instances in
   your home region." [S1] See §1a for the Indonesia choice.
5. Address and phone number [S15].
6. **Add payment verification method → Credit Card.** "You might see a small, temporary charge on your payment method.
   This is a verification hold that will be removed automatically. Note that your credit card won't be charged unless
   you elect to upgrade your cloud account." Debit cards bearing a major card logo and no PIN are accepted [S15].
   Free Tier overview adds: "For security purposes, **most users need a mobile phone number and a credit card** to
   create an account." [S2]
7. Accept terms → **Start my free trial**. The $300 / 30-day Free Trial is included; the Always Free resources are
   separate and "never expire" [S2]. You land in the Console at <https://cloud.oracle.com> [S6][S25].

### 1a. Region for a user in Indonesia (console choice)

Both candidate regions are Live in the OCI commercial realm [S17][S18]:

| Region name | Identifier | Location | Region key | ADs |
| --- | --- | --- | --- | --- |
| **Indonesia North (Batam)** | `ap-batam-1` | Batam, Indonesia | HSG | 1 |
| Singapore (Singapore) | `ap-singapore-1` | Singapore | SIN | 1 |
| Singapore West (Singapore) | `ap-singapore-2` | Singapore | XSP | 1 |

Nearest on network geography to Indonesia is **Indonesia North (Batam), `ap-batam-1`** — it is in-country; the
regions doc lists it as a commercial-realm region, location "Batam, Indonesia" [S17], and the public-region page
lists "Indonesia North (Batam) … Live" [S18]. **Singapore `ap-singapore-1`** is the next-nearest and the safer
second choice if Batam reports `Out of Host Capacity`.
Caveats that make this a real risk, not a formality: A1 capacity is documented as constrained ("Capacity might be
limited for A1 shapes" [S19]; "If you receive an 'out of host capacity' error … this indicates a temporary lack of
Always Free shapes in your home region. Try creating the instance in a different availability domain, or wait a
while" [S1]), and the documented remedies are "Change the shape / change the fault domain / change the availability
domain / don't specify a fault domain" [S20]. Batam has only one AD, so "change the AD" is not available there.
Because the home region is permanent ("Oracle assigns your home region and you can't change it" [S16]) and
free-tier tenancies get exactly one subscribed region [S17], a wrong pick
is not fixable by re-subscribing — only by creating a new tenancy. Note also that a *new* tenancy's A1 allowance is
2 OCPU/12 GB (§0), so do not plan on 4 OCPU/24 GB anywhere.

---

## 2. Console-only (network): VCN and subnet

Console: **Networking → Virtual cloud networks → Start VCN Wizard → "Create VCN with Internet Connectivity"**.
The wizard "Creates a VCN. Adds an **Internet Gateway** … Creates and configures public and private subnets for the
VCN. Sets up route tables and security lists for the subnets." Accept the defaults for the VCN IPv4 CIDR, DNS
resolution, and both subnets [S6]. Free-tier tenancy limit: 2 VCNs [S1].

Result you will use later: a **public subnet** with the **default security list** attached (the wizard does not
create an NSG), plus an internet gateway and a route rule to it.

---

## 3. Firewall layer 1 of 2 — Console: security list ingress for 80 and 443

**This is mandatory.** The default security list ships without any HTTP/HTTPS rule. Its documented contents are [S8]:

- stateful ingress: TCP dst port **22** from authorized sources;
- stateful ingress: ICMP type 3 code 4; stateful ingress: ICMP type 3 from the VCN CIDR;
- stateful egress: allow all.

To add the rules — Console: **Networking → Virtual cloud networks → your VCN → Resources → Security Lists → your
subnet's security list → Add Ingress Rules** [S3, WinRM procedure, same console path]. Add one rule per port:

| Field | Value |
| --- | --- |
| Stateless | **unchecked** (leave stateful; default) [S3] |
| Source Type | CIDR [S8] |
| Source CIDR | `0.0.0.0/0` [S8] |
| IP Protocol | TCP [S8] |
| Source Port Range | All [S8] |
| Destination Port Range | `80` (repeat the whole step for `443`) |
| Description | optional for security lists (NSG rules only) [S7] |

NSG alternative (Oracle's stated preference — "We recommend using NSGs instead of security lists" [S7]): create an
NSG, add the instance's primary VNIC to it at instance-create time or by updating the VNIC, and add the same two
rules via **Add Rules** (NSG rules accept a Description). Limit: 120 rules total per NSG; a security list allows 200
ingress + 200 egress rules [S7][S21]. If both are used, the effective rule set is the **union** [S7].

Hardening/sanity notes from the same docs:
- Oracle recommends narrowing the default SSH rule: "We recommend changing these rules to only allow inbound traffic
  from authorized subnets" [S8]. Practical effect: set the port-22 rule's Source CIDR to your own ISP address, not
  `0.0.0.0/0`.
- Security rules are **not** enforced for the `169.254.0.0/16` block (iSCSI/metadata) [S7].
- If you use stateful rules under load, watch connection tracking (shape-dependent table) — VNIC metrics
  `INGRESS/EGRESS PACKETS DROPPED BY FULL CONNECTION TRACKING TABLE` [S14].

---

## 4. Shell (on your Mac): generate the ed25519 key

Supported key types for platform images are explicitly "RSA, DSA, DSS, ECDSA, and **Ed25519**" [S11].

```
ssh-keygen -t ed25519 -C "oci-arm-$(date +%Y%m%d)" -f ~/.ssh/oci-arm-a1
chmod 600 ~/.ssh/oci-arm-a1
cat ~/.ssh/oci-arm-a1.pub          # this is what you paste in the Console
```

Notes drawn from [S11]: the private key is not stored by Oracle ("Without the private key, the only remedy to
connect to an instance is to create a new instance using a new private key"); a passphrase makes every later SSH
prompt (their example generates `-N ""` for convenience); Oracle's own suggested template uses RSA-2048, but
Ed25519 is on the supported list.

---

## 5. Console-only: create the instance

Console: **Compute → Instances → Create Instance** [S6]. Values:

1. **Name / Compartment** — any name; compartment defaults to your root compartment [S6].
2. **Placement** — take the defaults, but "For Free Tier, use the **Always Free Eligible** option for availability
   domain." [S6]. Availability-domain names are tenancy-prefixed and randomised per tenancy [S17].
3. **Image and shape** → click **Edit**:
   - Image: **Ubuntu 24.04 LTS**, the non-Minimal, aarch64 build (see §5a).
   - Click **Change shape** → **Virtual Machine** → shape series **Ampere** → **`VM.Standard.A1.Flex`**, the
     "Always Free" shape. **OCPU: 2** (the Always Free maximum), memory auto-paired (12 GB) [S1][S6].
     The tutorial's own example uses 1 OCPU / 6 GB to stay inside the allowance; 2 OCPU / 12 GB is the current
     full allowance [S6][S1].
4. **Networking** — pick the VCN/subnet from §2; keep **Assign a public IPv4 address: Yes**; **Use network security
   groups to control traffic: No** unless you built an NSG in §3 [S6].
5. **Add SSH keys** — either paste the `.pub` from §4 ("Paste public key"), or let the wizard generate one. Oracle
   warns: "You can't retrieve keys again after the compute instance has been created." [S6]. The public key is
   written to `/home/ubuntu/.ssh/authorized_keys` for Ubuntu images [S3].
6. **Boot volume** — see §6.
7. **Block volume** — none needed now; attach later if you want the rest of the 200 GB [S6][S1].
8. **Create**. Provisioning takes several minutes; "Do not refresh the page." [S6]
9. Note the **public IP address** from the instance's details page.

If creation fails with `Out of host capacity`: apply the documented remedies (other fault domain, don't specify a
fault domain, wait, or another AD) [S20][S1]. If the region has no capacity at all, the only in-tenancy fix is a
different region — which does not exist for a free-tier tenancy (one subscribed region [S17]).

### 5a. Image choice (arm64)

- Both **Ubuntu 24.04 LTS** and **Ubuntu 22.04 LTS** are listed as platform images supporting **Arm-based shapes**
  [S3]. Never use the Minimal build on Arm: "For Arm-based shapes, use the Ubuntu image, not Minimal Ubuntu." [S3]
- Latest Ubuntu 24.04 builds as of the fetch, from the image-notes index (release dates in parentheses) [S4][S5]:
  - `Canonical-Ubuntu-24.04-aarch64-2026.09.18-0` (September 21, 2026) ← the arm64 build to pick
  - `Canonical-Ubuntu-24.04-2026.09.18-0` (x86, same date)
  - `Canonical-Ubuntu-24.04-Minimal-aarch64-2026.09.18-0` (Minimal — do not use on Arm)
  - Previous arm64 builds: `...-2026.07.17-0`, `...-2026.06.29-0`, `...-2026.04.30-1`, `...-2026.02.28-0`, `...-2026.01.29-0`.
- Latest listed in the **Ubuntu 22.04** family is `Canonical-Ubuntu-22.04-Minimal-2026.09.18-0` (the index lists the
  Minimal variant as the family's latest) [S5]; the non-Minimal aarch64 build exists in the family listing but its
  exact 2026.09.18 build string was not captured — see Gaps.
- Image OCIDs for the two candidate regions, `Canonical-Ubuntu-24.04-aarch64-2026.09.18-0` [S4]:
  - `ap-singapore-1`: `ocid1.image.oc1.ap-singapore-1.aaaaaaaaw75ef2chh5goomskvdznqz36cadczqelqvndbqcozc5icyig57za`
  - `ap-batam-1`: `ocid1.image.oc1.ap-batam-1.aaaaaaaaoim33bqupt5df6uiudy34rx75v5sfbsxu3ootl522bpik5q7h6tq`
- Post-launch OS maintenance is your job: "After you launch an instance using the Ubuntu image, you are responsible
  for applying the required OS security updates using the `sudo apt-get upgrade` command." [S3]
- IPv6-only subnets are supported by Ubuntu 24.04/22.04 images released on/after March 31, 2026; irrelevant here
  (public IPv4 subnet) [S3].

---

## 6. Console-only: boot volume sizing inside the 200 GB allowance

Facts, all from Oracle docs, with the conflict stated rather than papered over:

- "All tenancies receive a total of **200 GB** of Block Volume storage … These amounts apply to both boot volumes
  and block volumes combined." [S1]
- "When you provision a compute instance, the instance automatically receives a **50 GB** boot volume for storage." [S1]
- "When you create a compute instance, the **default boot volume size** for the instance is **50 GB** … You can
  customize the instance's boot volume size **up to 200 GB**; however, this will use up your full allotment." [S1]
- "The **minimum boot volume size** for each instance is **47 GB**, regardless of shape." [S1]
- "…because the **minimum boot volume size allowed for compute instances is 50 GB**, launching four instances will
  use all your Always Free Block Volume resources." [S1]  ← **conflict: 47 GB vs 50 GB in the same page.**
- Independent statement: "For Linux and Windows images, the custom boot volume size must be **larger than the image's
  default boot volume size or 50 GB, whichever is higher**." [S12]
- If you set a size larger than the image default, "you need to [extend the partition] to take advantage of the
  larger size" — `oci`/`growpart`/`resize2fs` procedure in [S12].
- Always Free block volumes must be created in the **home region**; volumes elsewhere bill normally [S1].
- Max five volume backups (boot + block combined); creating a sixth fails until you delete one [S1].

Practical reading: 200 GB total. A 50 GB boot volume + one 150 GB block volume, or a 50 GB boot + a second instance's
50 GB boot (2 × 50 = 100 GB), etc. Any boot volume above 50 GB consumes the remainder of the allotment immediately.

---

## 7. Shell (on your Mac): SSH in and prove it is ARM

```
ssh -i ~/.ssh/oci-arm-a1 ubuntu@<PUBLIC_IP>
```

- Default username for Ubuntu images is **`ubuntu`** (Oracle Linux/RHEL-compatible images use `opc`);
  "Note that `root` login is disabled." [S3][S6][S10]
- First connection asks you to accept the host key fingerprint — type `yes` [S6].
- Verify inside the shell:

```
uname -m                      # expect: aarch64
lsb_release -a                # expect: Ubuntu 24.04 LTS
nproc; free -g                # expect: 2 CPUs, ~12 GB total
sudo whoami                   # expect: root (ubuntu has sudo) [S3]
```

Two documented traps for this step:
- Private key permissions must be owner-only (`chmod 600`) or SSH refuses the key [S6].
- macOS Ventura / OpenSSH 9.0 can fail to negotiate with images offering `ssh-rsa` host keys
  (`Unable to negotiate with <ip> port 22: no matching host key type found`); workaround is adding
  `PubkeyAcceptedKeyTypes +ssh-rsa` / `HostkeyAlgorithms +ssh-rsa` to `~/.ssh/config` [S9]. Only relevant if you
  hit it; with a modern Ubuntu 24.04 image it usually does not apply.
- Do not disable NetworkManager or stop the DHCP client: "the instance can't renew its DHCP lease and becomes
  inaccessible when the lease expires (typically within 24 hours)" [S10].

---

## 8. Firewall layer 2 of 2 — Shell (on the VM): the image blocks 80/443

**Yes — Oracle's Ubuntu images ship with host firewall rules that allow only SSH.** Two Oracle statements:

> "**Firewall Rules**
> Instances created using platform images have a default set of firewall rules that **allow only SSH access**.
> Instance owners can modify those rules as needed, but must not restrict link local traffic to address 169.254.0.2 …" [S3]

> "By default VM instances are **limited by their host firewalls to accepting SSH traffic only**." [S22 —
> Oracle Developers blog, "Enabling Network Traffic to Ubuntu Images in Oracle Cloud Infrastructure", Martin Bach,
> published July 4, 2022; read via Wayback snapshot 2026-06-29 because the live URL returns HTTP 403]

The Ubuntu images have **UFW disabled** and use raw iptables, ending in a REJECT:
"The last rule rejects any further connection attempts not allowed before." [S22]
Oracle forbids the obvious shortcut:

> "**Do not use Uncomplicated Firewall (UFW) to edit firewall rules on an Ubuntu image.** Using UFW to edit rules
> might cause an instance not to boot." [S3][S10]

and the corresponding known-issue entry gives the documented fix:

> "To modify or add new firewall rules, update the `/etc/iptables/rules.v4` file instead. Modifications to firewall
> rules here will take effect after a reboot. To have the rules take effect immediately, run the following:
> `sudo su -` / `# iptables-restore < /etc/iptables/rules.v4`" [S9]

Documented procedure, run on the VM:

```
# 1. back up, then edit
sudo cp /etc/iptables/rules.v4 /etc/iptables/rules.v4.bak
sudo nano /etc/iptables/rules.v4
```

Insert two lines **immediately after the existing SSH ACCEPT line** — order matters, because the file ends with a
catch-all REJECT:

```
-A INPUT -p tcp -m state --state NEW -m tcp --dport 80  -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
```

```
# 2. the SSH line must survive, or you lock yourself out
-A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT

# 3. apply now (and it persists across reboot)
sudo iptables-restore < /etc/iptables/rules.v4

# 4. verify
sudo iptables -S INPUT
```

The blog's exact warning, verbatim: "It is important *not* to add the new iptables rule at the end of the file or
else it will be ignored due to the earlier REJECT rule's higher precedence. The error message returned to the caller
('no route to host') can be misleading." [S22] Its `iptables -L INPUT` output for a stock Ubuntu image is:

```
ACCEPT     all  --  anywhere             anywhere             state RELATED,ESTABLISHED
ACCEPT     icmp --  anywhere             anywhere
ACCEPT     all  --  anywhere             anywhere
ACCEPT     udp  --  anywhere             anywhere             udp spt:ntp
ACCEPT     tcp  --  anywhere             anywhere             state NEW tcp dpt:ssh
REJECT     all  --  anywhere             anywhere             reject-with icmp-host-prohibited
```

Also edit `/etc/iptables/rules.v6` if you enable IPv6 on the subnet [S22].
**nftables:** no Oracle source found in this survey prescribes nftables for Ubuntu platform images; the documented
mechanism is the iptables + `rules.v4` + `iptables-restore` path above [S9][S22]. Oracle's own docs route the
*Oracle Linux* images (8/7, Autonomous Linux, Cloud Developer) through `firewalld` instead, not through
`rules.v4` [S7][S14].
Keep the iSCSI rules intact: host firewall rules must let only root reach `169.254.0.2:3260` and
`169.254.2.0/24:3260`; removing them "allows non-root users … to access the instance's boot disk volume" [S3][S10].
(Oracle Linux images differ: there you drive iptables through `firewalld` with
`sudo firewall-cmd --zone=public --permanent --add-port=…/tcp && sudo firewall-cmd --reload` — not applicable to
Ubuntu.) [S7][S14]

### Firewall layers, explicitly

| # | Layer | Where you change it | Where it is documented | Symptom when only this layer is closed |
| --- | --- | --- | --- | --- |
| 1 | Security list / NSG on the subnet / VNIC | OCI Console (or API) | [S7][S8] | Connection **times out**; VNIC metrics show packets dropped by security rules |
| 2 | Host iptables inside Ubuntu | `/etc/iptables/rules.v4`, then `iptables-restore` | [S3][S9][S22] | `no route to host` / connection refused (the REJECT rule) |
| 3 | The service not listening yet | app/systemd | — | Connection refused even with 1 and 2 open |

Both 1 **and** 2 must be open. Quote: "When troubleshooting access to an instance, ensure that all the following
items are set correctly: the rules in the network security groups that the instance is in; the rules in the
security lists associated with the instance's subnet; **the instance's OS firewall rules**." [S7][S14]

Verification that does not depend on the app: from your Mac, `nc -vz <PUBLIC_IP> 80` and `nc -vz <PUBLIC_IP> 443`
(expect "succeeded" once something listens) or `curl -I http://<PUBLIC_IP>`; on the VM,
`sudo iptables -S INPUT` must show the two ACCEPT lines before the REJECT.

---

## 9. DNS: point a free DuckDNS subdomain at the VM's public IP

DuckDNS is a free dynamic-DNS provider; the record is an A record for `<sub>.duckdns.org` pointing at your IP. [S23]

1. Console/browser (their side): sign in at <https://www.duckdns.org> (Google/GitHub/Twitter/Reddit/Persona) and
   create a subdomain; copy the account **token** [S23].
2. Shell — set/refresh the record (A record, IPv4):

```
curl -s "https://www.duckdns.org/update?domains=<SUBDOMAIN>&token=<TOKEN>&ip=<PUBLIC_IP>&verbose=true"
# good response: OK <ip> UPDATED   |   bad response: KO
```

   The `domains` value "does not need to include the .duckdns.org part"; omit `ip` to let DuckDNS auto-detect your
   own IPv4; `ip` also accepts IPv6; `clear=true` clears both records [S23]. Parameter-free form for dumb clients:
   `https://duckdns.org/update/<DOMAIN>/<TOKEN>/<IP>` [S23].
3. Shell — verify the record resolves to the instance, from your Mac:
   `dig +short <SUBDOMAIN>.duckdns.org` → should print the VM's public IP. (Also `dig <SUBDOMAIN>.duckdns.org TXT`
   if you later use the TXT API, which the spec says can be used "to prove your ownership with letsencrypt.org" for
   DNS-01 challenges.) [S23]
4. One update is enough while the instance keeps its public address; re-run step 2 if you terminate/recreate the
   instance or otherwise change its public IP.

Why 80/443 must actually be open at both layers: an HTTP-01/TLS-ALPN ACME issuance **and** the renewal loop need
inbound 80 and/or 443 from the public internet. If either layer blocks them, DNS resolves but certificate issuance
fails — the two failures look different (timeout vs `no route to host`) per the table in §8.

---

## 10. Post-launch console items that matter to this tenancy

1. **Outbound port 25 is blocked by default.** "Tenancies are by default not allowed to send e-mail through outbound
   TCP port 25 to the internet. If you require the ability to send email from your tenancy, open a service limits
   request to obtain an exemption." Tenancies created **after June 23, 2021** are affected; earlier ones are not. [S1][S14][S13]
   Inbound 25 is a separate matter and is not needed here; outbound SMTP from the app will fail until an exemption is
   granted via **Help → Support → Request service limit increase** [S14][S17].
2. **Idle reclamation** — see §0. No console setting prevents it; monitoring is your own responsibility.
3. **Always Free flags.** Always Free-eligible resources "display the **Always Free-eligible** label in the Console" [S1].
   Known cosmetic bug: "Oracle Autonomous Linux is not supported for Always Free compute instances, but in the Console,
   Oracle Autonomous Linux appears in the list of supported images for Always Free shapes." [S9]
4. **Trial expiry behaviour** (if you started from the $300 trial): the account stays active and Always Free resources
   are uninterrupted; but A1 over-allocation → disabled, then deleted after 30 days; paid resources bought with trial
   credits are reclaimed unless you upgrade [S2].

---

## 11. Not verified / gaps

- **Access date.** All fetches executed 2026-10-07 08:20 UTC; the task asked for 2026-10-06. Nothing was re-fetched
  on 2026-10-06 and no 2026-10-06 access date is claimed.
- **A1 allowance change has no primary release note found.** The current docs [S1][S2][S24] state 2 OCPU/12 GB and
  [S2] states the >2 OCPU/12 GB enforcement. A dated Oracle release note or blog announcing the halving was **not
  found**; the 2026-06-15 date comes from third-party press (InfoQ) and a 2026-07-21 Oracle Community post, which were
  not treated as primary. `[UNVERIFIED — announcement date/channel]`
- **Boot volume 47 GB vs 50 GB.** [S1] says both, on the same page. [S12] implies "50 GB whichever is higher" for
  custom sizes. Which number the Console actually enforces in 2026 was not observed. `[UNVERIFIED — console default/min]`
- **Image default boot volume size for `Canonical-Ubuntu-24.04-aarch64-*`.** Not stated in [S4]; [S12] defers to "the
  image's default boot volume size". `[UNVERIFIED]`
- **Ubuntu 22.04 non-Minimal aarch64 build string.** The family index shows the Minimal variant as latest [S5]; the
  non-Minimal aarch64 name was not captured. Use 24.04 (verified) if it matters. `[UNVERIFIED]`
- **Batam capacity for Always Free A1.** Region existence is verified [S17][S18]; whether `ap-batam-1` holds Always
  Free A1 capacity today cannot be checked without a tenancy, and the docs only promise that capacity "might be
  limited for A1 shapes" [S19]. Batam has a single AD, so the documented "change the availability domain" remedy
  [S20] is unavailable there. `[UNVERIFIED — capacity]`
- **Reclamation appeal.** Oracle's docs describe the trigger and the upgrade path only; no appeal/notification
  process is documented. Treat "you can appeal" as community folklore. `[UNVERIFIED — no documented appeal]`
- **Live Oracle Developers blog unavailable.** `https://blogs.oracle.com/developers/enabling-network-traffic-to-ubuntu-images-in-oracle-cloud-infrastructure`
  returns HTTP 403 to automated fetches on 2026-10-07 (live URL = 403; the 403 is confirmed at fetch time).
  Content was read from the Wayback snapshot dated 2026-06-29. The page metadata reports publish date 2022-07-04,
  which is the blog's own date, not our access date. `[PARTIALLY VERIFIED via archive]`
- **UFW rules content.** The command lines that stock Ubuntu images place in `/etc/iptables/rules.v4` come from the
  blog ([S22]); docs.oracle.com states only "allow only SSH access" [S3] plus the UFW prohibition [S9][S10].
- **Exact NSG console wording.** The "Add Rules" field list comes from the WinRM procedure in [S3] and the rule
  anatomy in [S7]; the 80/443 values are composed from those, not copied from an HTTP-specific Oracle procedure
  (no such procedure was found in docs.oracle.com).
- **Console default for "Use in-transit encryption"** on the boot volume: the tutorial selects it in a step [S6];
  whether it is selected by default today was not observed. `[UNVERIFIED]`
- **OCI CLI flow.** Not covered: the steps above are Console+shell by design. An equivalent CLI flow needs an API key
  created in the Console first, which is still a console-only step.
- **DuckDNS terms/rate limits.** The spec [S23] documents the API but no rate limits or SLA; DuckDNS is a third party
  with no relationship to the OCI tenancy.

---

## Sources (all fetched 2026-10-07 UTC unless noted)

- [S1] Always Free Resources — https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm (page last modified 2026-06-12)
- [S2] Oracle Cloud Infrastructure Free Tier — https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm (2026-06-29)
- [S3] Platform Images — https://docs.oracle.com/en-us/iaas/Content/Compute/References/images.htm (2026-08-12)
- [S4] Image notes: Canonical-Ubuntu-24.04-aarch64-2026.09.18-0 — https://docs.oracle.com/en-us/iaas/images/ubuntu-2404/canonical-ubuntu-24-04-aarch64-2026-09-18-0.htm (2026-09-24)
- [S5] All Image Families — https://docs.oracle.com/en-us/iaas/images/ (2026-09-30)
- [S6] Tutorial: Launching Your First Linux Instance — https://docs.oracle.com/en-us/iaas/Content/Compute/tutorials/first-linux-instance/overview.htm
- [S7] Security Rules — https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securityrules.htm
- [S8] Security Lists — https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securitylists.htm
- [S9] Known Issues for Compute — https://docs.oracle.com/en-us/iaas/Content/Compute/known-issues.htm (2026-03-25)
- [S10] Best Practices for Your Compute Instances — https://docs.oracle.com/en-us/iaas/Content/Compute/References/bestpracticescompute.htm (2026-02-26)
- [S11] Managing Key Pairs on Linux Instances — https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/managingkeypairs.htm
- [S12] Working with Boot Volumes — https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/bootvolumes.htm (2026-09-03)
- [S13] Release note: Outbound SMTP is blocked — https://docs.oracle.com/en-us/iaas/releasenotes/changes/f7e95770-9844-43db-916c-6ccbaf2cfe24
- [S14] VCN Troubleshooting — https://docs.oracle.com/en-us/iaas/Content/Network/Troubleshoot/vcn_troubleshooting.htm
- [S15] Sign Up for the Free Oracle Cloud Promotion — https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/signingup_topic-Sign_Up_for_Free_Oracle_Cloud_Promotion.htm
- [S16] Managing Regions — https://docs.oracle.com/en-us/iaas/Content/Identity/regions/managingregions.htm
- [S17] Regions and Availability Domains — https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm (2026-06-22)
- [S18] Public Cloud Regions and Data Centers — https://www.oracle.com/cloud/public-cloud-regions/ (page updated 2026-04-14)
- [S19] Compute Shapes — https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm
- [S20] Resolving Out of Host Capacity error — https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/troubleshooting-out-of-host-capacity.htm (2025-04-25)
- [S21] Limits by Service — https://docs.oracle.com/en-us/iaas/Content/General/service-limits/default.htm
- [S22] Oracle Developers blog, "Enabling Network Traffic to Ubuntu Images in Oracle Cloud Infrastructure" (Martin Bach, published 2022-07-04) — live URL https://blogs.oracle.com/developers/enabling-network-traffic-to-ubuntu-images-in-oracle-cloud-infrastructure returns HTTP 403 on 2026-10-07; read via https://web.archive.org/web/20260629131131/https://blogs.oracle.com/developers/enabling-network-traffic-to-ubuntu-images-in-oracle-cloud-infrastructure
- [S23] DuckDNS HTTP API specification — https://www.duckdns.org/spec.jsp
- [S24] Oracle Cloud Free Tier pricing page — https://www.oracle.com/cloud/free (arm "12 GB of memory … 1,500 OCPU hours and 9,000 GB hours per month")
- [S25] Getting Started FAQ (home region not changeable; console URL) — https://docs.oracle.com/en-us/iaas/Content/GSG/Reference/faq.htm
