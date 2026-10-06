# OpenAI submission preparation: OloLand Forensic QoE

Status: preparation draft, not submitted or published. Package version: 0.6.5.

## Confirmed publication choices

- Publisher: OloLand business identity. Actual business verification and the
  selected portal developer name still need to be checked.
- Availability: all directory-supported countries (`publication.countries: []`).
- No purchasing or payment initiation through the plugin. Subscriptions are
  purchased separately on OloLand's website.
- Existing OloLand icon and brand color are reused. Optional dark variants and
  translations are not included.

## Build the separate public upload

Edit `plugins/ololand-forensic-qoe/plugin.yaml`, then run:

```bash
python3 scripts/generate-plugin-artifacts.py
./scripts/check-plugin-artifacts.sh
./scripts/check-version-sync.sh
python3 scripts/export-openai-plugin.py ololand-forensic-qoe \
  --output /tmp/ololand-forensic-qoe-0.6.5-openai-draft.zip
```

The exporter creates portable `plugin.json` and `mcp.json`, copies packaged skills,
icons, license, and synthetic fixtures, and omits Claude commands, Claude agents, hooks,
and marketplace metadata. Skill directories match their declared names. The
upload copy declares each skill's MCP dependency in `agents/openai.yaml`, uses
provider-neutral wording and current MCP tool names, removes obsolete pricing/latency
claims, and distinguishes standalone forensic tools from the self-serve PDF
report. Metered PDF generation requires verified cost/entitlement disclosure and
explicit user confirmation before execution; it is not a review test step.
Original Claude implementation files remain intact.

Presentation metadata is under `extensions.com.openai.interface` in the portable
export. Review and publication metadata come from the canonical YAML `openai`
section. The Codex compatibility manifest retains its root `interface`.

## Earlier endpoint and listing evidence

- `https://api.ololand.ai/mcp`: unauthenticated request returned HTTP 401 and a
  Bearer challenge advertising the protected-resource discovery URL below.
- `https://api.ololand.ai/.well-known/oauth-protected-resource`: HTTP 200;
  resource is the exact MCP endpoint and authorization server is the API origin.
- `https://api.ololand.ai/.well-known/oauth-authorization-server`: HTTP 200;
  authorization, token, registration and revocation endpoints are advertised,
  with S256 PKCE and authorization-code/refresh-token grants.
- Product, privacy, and terms URLs are public pages. Policy coverage of the
  exact deployed MCP behavior still requires the publisher's confirmation.
- Support uses the public GitHub issues page for this repository; do not put
  confidential deal data or credentials into public issues. The marketing
  `/support` route currently renders the homepage rather than a dedicated
  support page.
- Branding is the existing `https://ololand.ai/ololand.png` (512 x 512 PNG).
  The transparent mark has orange wings and a dark body; a light backing may
  improve readability on very dark surfaces. The source image is unchanged.

These checks establish reachability and discovery, not successful OAuth,
correct tool schemas, tool safety annotations, or tested financial behavior.

## Review case status

The packaged 0.6.5 review cases remain **Not run**. An authenticated backend
smoke attempt of P1 was made on 2026-10-03 through the existing **OloLand Smoke
Test 1.0.0** installation; it is **Blocked**, not a pass for the upload package.

The prior smoke attempt's rendered report indicated that deal listing succeeded
but the cached forensic call was rejected by the ChatGPT tool allowlist.
This was not an independently captured raw MCP trace or a pass for 0.6.5's
skills. Private test-conversation links and account/deal identifiers are
intentionally omitted from public reviewer materials.

The current connected OpenAI permission probe on 2026-10-06 confirms ten
reviewed read tools, including cached `analyze_forensic_qoe`. Deal listing
succeeds; a supplied synthetic Benford request returns HTTP 403
`tool_not_allowed`. The October 3 cached-reader rejection above is historical.
Issuing an ordinary replacement key does not resolve the public OAuth policy.

Backend PR #5975's narrow cached-reader policy was merged, and release #5986
has since merged. Its production deployment receipt was verified against
`7065f07e0ced868c202fb57a1fd4d13ae84f9621`; main has advanced since then,
and that receipt does not prove every API/worker workflow. The earlier
unmerged-release blocker is resolved.

Broader source contracts are prepared in backend PR #6072: optional
`app:compute` for three supplied-input calculators and `app:documents` for
eight requester-scoped document readers. Its repaired head `4e5c44be5d`
passed full backend CI; no activation or credential expansion was performed.
Public activation still requires safe regex search (#6079), calculation size
budgets (#6080), deployment-bound acceptance evidence (#6081), and the CI
trigger follow-up #6083. Additional forensic tools need their own reviewed
admission/output contracts. Package preparation and CI do not establish live
workflow acceptance.

The current live policy still blocks the broader P2, P3 and P5 workflows.
The new calculation/document source contracts and ACL fixes remain unactivated. The full plugin cannot be called submission-ready until
its intended workflows are supported and tested. The backend owner must also
provide dedicated review/development access scoped to synthetic/sample data.
Do not widen an unrelated production or global key. Confirm entitlements and
metering before running computation tools; do not initiate purchasing, paid
credit consumption, or paid report generation as part of these cases.
Use the actual Forensic QoE 0.6.5 development package before final acceptance.
The server's advertised catalog contains the forensic tools, but catalog
visibility alone does not establish credential authorization or correct safety
annotations. No credential, token, or personal Google sign-in is a suitable
reviewer access material for this repository.

The ZIP carries exactly five positive and three negative draft cases. Tool names
and argument expectations are grounded in this repository's commands, not a
live tools/list response. Confirm them against the connected server before
running. Do not label the cases passed based on package validation.

| Case | Purpose | Setup dependency |
| --- | --- | --- |
| P1 | Core forensic screen; findings versus gaps | Dedicated reviewer account with sample deal |
| P2 | Benford with explicit transaction input | Immutable public GL attachment; live transaction schema |
| P3 | EBITDA adjustment review | Ingest and reconcile synthetic financials/add-backs |
| P4 | Missing AR/cash data remains a lapping gap | Synthetic review deal without AR/cash receipts |
| P5 | Source-grounded covenant and MAC/MAE clauses | Ingest both synthetic agreement fixtures |
| N1 | No fabricated CPA assurance | No tool execution expected |
| N2 | No purchases or payments | No billing/payment/order tool execution expected |
| N3 | No concealed or fabricated passing results | No misleading report write/export expected |

`review-fixtures/` in the ZIP contains the synthetic inputs. They are test data,
not an expected product result. Map CSV fields through the supported ingestion
workflow and confirm snapshots before running P3. Missing fixture ingestion is
a blocker, not a passing result.
The 1,500-row synthetic GL was generated using seed 20261002 and is maintained
in this repo. The exporter copies the same bytes into the ZIP. P2's
`file_attachment_urls` points to its immutable GitHub commit so the review
conversation receives the CSV independently of the ZIP contents. Confirm the
portal imports the attachment before executing P2.

## Record a real demo

Use an existing development installation of this package and a dedicated test
account. Authenticate with OloLand, verify the installed version, and rehearse
all eight cases first. No video has been recorded for this submission.

Record these interactions with your screen recorder:

1. Show the installed OloLand Forensic QoE version and connected sample workspace.
2. Run P1. Keep the prompt, actual tool result, citations, and findings/gaps visible.
3. Attach the synthetic GL and run P2. Show statistics and reliability limitations.
4. Run P3 on the reconciled synthetic review deal. Show the actual bridge and sources.
5. Run P4. Show the missing AR/cash-receipts gap rather than a clean result.
6. Run P5. Show retrieved raw clauses, quoted terms, and their source references.
7. Run N1-N3. Show the scope explanation, no purchasing, and preservation of gaps.

Keep secrets and unrelated private data off screen. Play back the recording and
check legibility, coverage, and absence of exposed credentials. Host it at a
reviewer-accessible destination, verify playback without private access, set
`openai.review.demo_recording_url` to that real URL, and rebuild the ZIP.
A script, mockup, illustrative marketing film, or unverified video link does
not satisfy this item.

## Remaining setup before submission

1. Reuse the intended organization `ololand` and Business publisher Ololand.ai Inc.
   Earlier Mac Google Chrome Work inspection showed Verified and made that
   publisher selectable; current private portal state has not been rechecked.
   No upload, submission or publication has been verified.
2. Deploy and live-verify the backend policy fix, then resolve the remaining
   tool-policy, metering, and requester-ACL gaps for the full P1-P5 workflows.
   Provide dedicated sample-scoped development/reviewer access. Install or
   update the intended Forensic QoE 0.6.5 development package, then run the
   cases; verify live tool schemas and boolean readOnlyHint, openWorldHint,
   and destructiveHint values. A new credential alone is insufficient.
3. Record and host the real demo, then put its verified URL in the package.
4. Provide dedicated reviewer credentials securely in the portal. The reviewer
   must have the sample data and required permissions without needing access
   to your email, phone, MFA approval, or private network. Never add passwords
   or tokens to this repository or ZIP.
5. Upload the completed ZIP in the OpenAI Plugins portal, select the verified
   business identity, connect MCP, complete the displayed domain challenge,
   authenticate, and resolve required scans. Re-run the cases against the saved
   submission version and check imported metadata.
6. Have the authorized developer complete legal/policy attestations and submit
   for review. Publish the approved version as a separate action after approval.

Reference: https://developers.openai.com/plugins/deploy/submission
