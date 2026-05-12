---
name: extract-risks-constraints
description: >-
  Analyze project documents to build a comprehensive risk register with identified risks,
  probability and impact scoring, mitigation strategies, and ownership assignments. Use when
  the user asks to build, create, or set up a risk register, risk log, or risk management
  document for project initiation.
disable-model-invocation: true
outputs:
  - path: common/input/snippets/risks_constraints.md
    description: Risks & Constraints snippet embedded into the Project Charter
  - path: shared_output/Risk_Register.html
    description: Standalone high-level risk register opened automatically after processing
---

# PMP Risk Register Builder

Creates a risk register document from scratch, suitable for use as the central artifact throughout a project's Initiation Stage.

## Overview

This skill automates the creation of a comprehensive risk register by analyzing project artifacts (SOW, stakeholder lists, purchase orders) and populating a standardized risk register template with project-specific risks, mitigation strategies, and monitoring parameters.

## Prerequisites

Before using this skill, ensure the following files are available:

* Stakeholder list
* Purchase Order
* Risk Register Template (Excel-based)

---

## Workflow

### Step 1: Gather Project Risk Information

Collect and analyze the following project documents:

* [ ] **Stakeholder List** - Identify key stakeholders, their roles, and potential risk exposure
  * Expected filename pattern: `*_Stakeholders*.xlsx` or `*_Stakeholders*.csv`
  * Location: `01_raw_archive/` or `02_working_docs/` in project directory

* [ ] **Purchase Order / Project Charter** - Review budget, timeline, deliverables, and contractual terms
  * Expected filename pattern: `PO_*.docx` or `Project_Charter_*.pdf`
  * Location: `01_raw_archive/` or `02_working_docs/` in project directory

**File Detection Procedure:**

* First check the project working directory (`00_inbox/`, `01_raw_archive/`, `02_working_docs/`)
* If files cannot be located, **STOP** and provide a detailed problem statement with:
  * List of files searched
  * Expected filename patterns
  * Actual location needed from the user

### Step 2: Analyze Project Context

From the collected documents, extract:

1. **Project Scope & Objectives**
   * Technical complexity and novelty
   * Geographic/organizational scope
   * Regulatory and compliance requirements

2. **Stakeholder Risk Exposure**
   * Key decision-makers and their risk tolerance
   * Technical vs. business stakeholder concerns
   * Internal vs. external stakeholder dependencies

3. **Timeline & Budget Constraints**
   * Fixed vs. flexible deadlines
   * Budget constraints and contingency allocation
   * Resource availability and skill gaps

4. **Technical Architecture & Dependencies**
   * Technology stack and integration points
   * Third-party dependencies and vendor risks
   * Data security and compliance requirements

### Step 3: Build the Risk Register

Create the risk register using the following standardized template structure:

#### Risk Register Column Headers

| Column | Description | Format | Example |
|--------|-------------|--------|---------|
| **Risk ID** | Unique identifier | `RISK-###` | `RISK-001` |
| **Category** | Risk classification | Dropdown | Technical, Schedule, Resource, Budget, Vendor, Compliance, Stakeholder, Environmental |
| **Risk Description** | Clear, specific description of the risk | Text | "Delayed third-party API integration impact on development timeline" |
| **Root Cause** | Underlying reason the risk exists | Text | "Vendor experiencing resource constraints" |
| **Potential Impact** | Consequences if risk occurs | Text (link to Impact Scale) | "Project delay of 2-3 weeks, budget overrun of $30K" |
| **Probability** | Likelihood of occurrence | Scale 1-5 | 3 = Medium |
| **Impact Score** | Severity if risk occurs | Scale 1-5 | 4 = High |
| **Risk Score** | Probability × Impact | Calculated (1-25) | 12 (3 × 4) |
| **Priority** | Based on Risk Score | Critical/High/Medium/Low | High |
| **Mitigation Strategy** | Proactive steps to reduce the probability or impact | Text | "Establish backup vendor, weekly status check-ins" |
| **Contingency Plan** | Response if risk occurs | Text | "Allocate additional development resources, extend timeline" |
| **Owner** | Person responsible for monitoring | Name | "Rajesh Kumar (Backend Lead)" |
| **Status** | Current state | Active/Closed/Escalated | Active |
| **Date Identified** | When risk was documented | ISO format (YYYY-MM-DD) | 2025-01-15 |
| **Last Review Date** | Most recent assessment | ISO format (YYYY-MM-DD) | 2025-01-20 |
| **Notes** | Additional context or updates | Text | "Scheduled mitigation meeting for Week 2" |

#### Risk Identification Guidelines

**Categories to assess:**

1. **Technical Risks** - Architecture, integration, technology maturity, skill gaps
2. **Schedule Risks** - Timeline pressure, dependencies, resource availability
3. **Budget Risks** - Cost overruns, scope creep, vendor pricing changes
4. **Resource Risks** - Key person dependencies, team turnover, skill gaps
5. **Vendor/Procurement Risks** - Third-party delays, API limitations, SLA compliance
6. **Compliance & Security Risks** - Regulatory changes, data protection, vulnerability exposure
7. **Stakeholder Risks** - Misalignment, scope disputes, approval delays
8. **Environmental Risks** - External market changes, competitive pressure, infrastructure dependencies

#### Populate with Project-Specific Risks

Extract minimum 8-12 risks from the SOW, stakeholder analysis, and project constraints:

* At least 2 Technical risks
* At least 2 Schedule/Timeline risks
* At least 2 Budget/Resource risks
* At least 1 Vendor/Integration risk
* At least 1 Compliance/Security risk
* At least 1 Stakeholder/Change risk

### Step 4: Validate & Deliver

**Validation Checklist:**

* [ ] All Risk IDs are unique and properly formatted (`RISK-001`, `RISK-002`, etc.)
* [ ] All risks have assigned Probability (1-5) and Impact (1-5) scores
* [ ] Risk Score is calculated correctly (Probability × Impact)
* [ ] Priority assignment matches Risk Score thresholds
* [ ] All risks have identified owners from stakeholder list
* [ ] Mitigation and contingency strategies are specific and actionable
* [ ] Dates are in ISO format (YYYY-MM-DD)
* [ ] No duplicate or near-duplicate risks

**Output Format:**

This skill produces two outputs on every run:

| Output | Path | Purpose |
|--------|------|---------|
| Snippet | `common/input/snippets/risks_constraints.md` | Section 6 embedded into `Project_Charter.html` |
| Risk Register | `shared_output/Risk_Register.html` | Standalone HTML opened automatically in a new browser tab after processing |

The risk register HTML contains:
- A summary bar (total, Critical, High, Medium, Low counts)
- A full risk table with columns: Risk ID · Category · Description · Source · Impact · Probability · Score · Priority · Mitigation
- Rows derived from Section 6a (Constraints), 6b (NFRs), and 6c (Evaluation Criteria)
- Color-coded priority badges (Critical = red, High = orange, Medium = amber, Low = green)

**Deliverable Summary:**

Upon completion, provide:

* Total number of risks documented
* Risk category breakdown (count per category)
* Priority distribution (Critical / High / Medium / Low)
* Top 5 highest-scoring risks
* Recommended risk response approach (Mitigate / Accept / Avoid / Transfer)
* Next review date recommendation

---

## Output Format Standards

### Risk ID Format

* **Pattern:** `RISK-###` (zero-padded)
* **Examples:** `RISK-001`, `RISK-002`, `RISK-010`, `RISK-025`
* **Sequential:** Assigned in order of identification

### Date Format

* **Standard:** ISO 8601 format
* **Format:** `YYYY-MM-DD`
* **Examples:** `2025-01-15`, `2025-06-30`, `2025-12-31`

### Probability Scale (1–5)

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Very Low | < 10% chance of occurrence |
| 2 | Low | 10–30% chance of occurrence |
| 3 | Medium | 30–50% chance of occurrence |
| 4 | High | 50–75% chance of occurrence |
| 5 | Very High | > 75% chance of occurrence |

### Impact Scale (1–5)

| Score | Level | Description | Example |
|-------|-------|-------------|---------|
| 1 | Negligible | Minimal impact on project success | Minor schedule slip (< 1 week) |
| 2 | Low | Small impact, manageable with minor adjustments | Schedule slip (1–2 weeks), minor budget increase ($5K) |
| 3 | Medium | Moderate impact, requires active mitigation | Schedule slip (2–4 weeks), budget increase ($15K–$30K) |
| 4 | High | Significant impact, threatens project objectives | Schedule slip (4–8 weeks), budget overrun ($30K–$60K), scope reduction |
| 5 | Catastrophic | Critical impact, project viability at risk | Project delay (> 2 months), budget overrun (> $100K), major scope cuts, reputational damage |

### Risk Score Calculation

* **Formula:** Risk Score = Probability × Impact
* **Range:** 1–25
* **Interpretation:** Higher scores indicate higher priority for mitigation

### Priority Classification

| Priority | Risk Score | Response | Action Timeline |
|----------|-----------|----------|-----------------|
| **Critical** | 20–25 | Immediate mitigation required | Weeks 1–2 of project |
| **High** | 12–19 | Active mitigation and monitoring | Week 1–4 |
| **Medium** | 6–11 | Planned mitigation strategy | Week 1–8 |
| **Low** | 1–5 | Monitor; contingency plan in place | Ongoing, review monthly |

**Example Calculations:**

* Risk with Probability=5 (Very High) and Impact=5 (Catastrophic): Score=25 → **Critical**
* Risk with Probability=4 (High) and Impact=3 (Medium): Score=12 → **High**
* Risk with Probability=2 (Low) and Impact=3 (Medium): Score=6 → **Medium**
* Risk with Probability=1 (Very Low) and Impact=2 (Low): Score=2 → **Low**

---

## Common Risk Categories & Examples

### Technical Risks

* Third-party API integration delays or unavailability
* Technology stack incompatibility or immaturity
* Performance/scalability issues discovered late
* Security vulnerabilities in dependencies
* Database design inadequacy

### Schedule Risks

* Unrealistic timeline with fixed 24-week deadline
* Complex dependencies between development phases
* Design review delays impacting development start
* Testing phase compression
* App Store approval delays

### Resource & Staffing Risks

* Key person dependency (e.g., Backend Lead, UX Designer)
* Team turnover or key person unavailability
* Skill gaps in iOS/Android native development
* Insufficient QA resources for UAT phase

### Budget Risks

* Scope creep beyond defined requirements
* Infrastructure costs exceeding estimates
* Vendor pricing increases
* Unplanned bug fixes consuming contingency
* Late-stage architectural changes

### Vendor & Procurement Risks

* Third-party service outages (AWS, GCP)
* Payment gateway or SMS provider integration issues
* Wearable device API limitations
* App Store review process delays

### Compliance & Security Risks

* Data privacy regulation changes (PDPL, GDPR)
* Security audit findings requiring rework
* App Store policy violations
* Insufficient encryption or data protection

### Stakeholder Risks

* Scope misalignment between Client and Vendor
* Delayed approval or sign-offs
* Conflicting requirements from multiple stakeholders
* Change requests post-design phase

---

## Tips for Effective Risk Management

1. **Regular Review:** Schedule quarterly risk register reviews (minimum monthly during active development)
2. **Ownership:** Ensure each risk has a single owner accountable for monitoring and mitigation
3. **Actionable Strategies:** Mitigation plans should be specific, measurable, and resource-realistic
4. **Threshold-Based Escalation:** Automatically escalate Critical/High risks to Project Sponsor
5. **Lessons Learned:** Document realized risks and mitigation effectiveness for future projects

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-20 | Initial skill creation with corrected syntax and environment-aware paths |
