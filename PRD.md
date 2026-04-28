# Product Requirements Document
## AI Lead Generation & Outreach Agent
**Project:** `node_4_crewai-project`  
**Version:** 1.0  
**Date:** 2026-04-28  
**Stack:** CrewAI · GPT-4o-mini · Google Sheets API · Gmail API

---

## 1. Overview

An autonomous, 4-agent CrewAI pipeline that takes simple search criteria as input and delivers a **populated Google Sheet of scored leads + personalised Gmail outreach drafts** — with no manual research required.

---

## 2. Problem Statement

Sales and business-development teams spend hours manually researching companies, finding executive contacts, validating data quality, and drafting cold outreach emails. This agent automates the entire workflow end-to-end.

---

## 3. Inputs

| Field | Type | Description |
|---|---|---|
| `location` | string | Target geography (e.g. `"Dubai, UAE"`) |
| `industry` | string | Target sector (e.g. `"SaaS"`, `"Fintech"`) |
| `company_size` | string | Size filter (e.g. `"11-50 employees"`) |
| `limit` | integer | Max companies to discover (e.g. `10`) |

---

## 4. Pipeline — 4 Sequential Nodes

```
[Input] → Node 1 → Node 2 → Node 3 → Node 4 → [Google Sheets + Gmail]
```

### Node 1 — Company Discovery Specialist
**Goal:** Find `{limit}` real, verified companies matching all criteria.  
**Tools:** `SerperDevTool`, `FirecrawlScrapeWebsiteTool`, `LinkedInBooleanGeneratorTool`, `AdvancedWebBooleanBuilderTool`, `SmartSearchQueryOptimizer`  
**Output:** JSON list of companies with `name`, `website_url`, `description`, `industry`, `location`, `company_size`, `website_accessible`.

### Node 2 — Contact Discovery Specialist
**Goal:** For each company, find CEO / Founder / C-level contacts with LinkedIn URL, email, and phone number.  
**Tools:** `SerperDevTool`, `LinkedInBooleanGeneratorTool`, `AdvancedWebBooleanBuilderTool`, `PhoneEnrichmentTool`  
**Output:** Enriched JSON — all Node 1 data + `contacts[]` per company (name, title, linkedin_url, email_address, phone_number, confidence, verification_status).

### Node 3 — Lead Quality Analyst
**Goal:** Validate every contact and assign a priority grade (A/B/C/D) to each lead.  
**Tools:** `MultiSourcePhoneValidatorTool`, `SerperDevTool`  
**Scoring Dimensions:**
- Phone validation score (0–100)
- Email validation score (0–100)
- LinkedIn validation score (0–100)
- Company fit score (0–100)
- Data completeness score (0–100)

**Output:** Scored JSON + `lead_priority` (A/B/C/D), `outreach_readiness`, `recommended_contact_method`, `quality_flags`.

### Node 4 — Output Coordinator
**Goal:** Persist leads to Google Sheets and trigger Gmail outreach for top-priority leads.  
**Apps:** `google_sheets/create_spreadsheet`, `google_sheets/append_values`, `google_sheets/update_values`, `google_gmail/create_draft`, `google_gmail/send_email`  
**Actions:**
1. Create dated Google Sheet: *"Lead Database — YYYY-MM-DD"*
2. Populate all leads (14-column schema, sorted A→D)
3. Create personalised Gmail drafts for **A-priority** leads
4. Queue Gmail drafts for **B-priority** leads
5. Update sheet with outreach status

---

## 5. Custom Tools

| Tool | Purpose |
|---|---|
| `LinkedInBooleanGeneratorTool` | Builds precision LinkedIn boolean search strings |
| `AdvancedWebBooleanBuilderTool` | Generates multi-source web boolean queries for email discovery |
| `SmartSearchQueryOptimizer` | Optimises and rewrites search queries for best recall |
| `PhoneEnrichmentTool` | Finds direct / mobile phone numbers for executives |
| `MultiSourcePhoneValidatorTool` | Cross-validates phone numbers across multiple sources |

---

## 6. Outputs

| Deliverable | Description |
|---|---|
| **Google Sheet** | All leads with scores, priorities, and outreach status |
| **Gmail Drafts** | Personalised cold-email drafts for A & B priority leads |
| **JSON Report** | Machine-readable summary of the full campaign run |

---

## 7. Success Metrics

| Metric | Target |
|---|---|
| Company discovery accuracy | ≥ 90% real, verified companies |
| Contact find rate | ≥ 1 verified contact per company |
| A/B priority leads | ≥ 50% of total leads found |
| End-to-end runtime | < 10 min for 10 companies |
| Sheet population success | 100% of scored leads written |
| Email draft creation | 100% of A-priority leads |

---

## 8. Tech Stack & Dependencies

- **Runtime:** Python ≥ 3.10  
- **Framework:** CrewAI (sequential process)  
- **LLM:** `openai/gpt-4o-mini` (all agents)  
- **Search:** Serper API  
- **Scraping:** Firecrawl  
- **Integrations:** Google Sheets API, Gmail API (via CrewAI `apps`)  
- **Package manager:** `uv`

---

## 9. Out of Scope (v1.0)

- CRM integration (Salesforce, HubSpot)
- Email reply tracking / inbox monitoring
- Multi-language outreach
- Human-in-the-loop approval step before sending emails
