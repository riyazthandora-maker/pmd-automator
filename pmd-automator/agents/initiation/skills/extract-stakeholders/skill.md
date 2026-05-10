# Agent: Start_Extraction

## Overview
Orchestrates data extraction from `/Assets` to automate the final Project Charter PDF creation.

## Workflow Execution
1. **Trigger:** User command: `create the charter`.

2. **Phase 1: Source Validation**
   - Scan `/Assets` for keywords: *RFI, BRD, Business Case, SOW, PO, Service Agreement, MSA, Stakeholder List*.
   - **Condition - Files Missing:** If no files match, terminate and display: "NO RELEVANT SOURCE FILES AVAILABLE IN ASSET FOLDER - once available re-initiate the agent."
   - **Condition - Files Present:** Execute all skills in the `/initiation/` sub-folders.

3. **Phase 2: Data Integration**
   - Collect responses from skills.
   - **If message contains "No... Details Found":** Display the specific error message and stop execution.
   - **If message contains "Details are found":** - Ctrate excel file/Update if already exists `/Shared_Outputs/Snippets/Stakeholders_Register.csv`.
     - Standardize columns: **Name, Organization, Role, Influence, Interest, Email ID, Contact Details**.

4. **Phase 3: Final Charter Generation**
   - **Map:** Populate `/Assets/Project_Charter_Template.docx` with aggregated data.
   - **Naming Convention:** Save as `[Project_Name]_Charter.pdf` (Replace spaces with underscores).
   - **Path:** `/Shared_Outputs/Final_Charter/`.

5. **Phase 4: Closure & Verification**
   - Display: "Charter generation complete. Path: /Shared_Outputs/Final_Charter/[Project_Name]_Charter.pdf"
   - **Confirmation Prompt:** "Has this charter been approved by all stakeholders? (Yes/No)"
   - **If No:** Prompt user to list required revisions.
