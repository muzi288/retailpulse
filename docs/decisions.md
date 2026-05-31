# Architecture Decision Records

## ADR-001: Repository Structure
**Date:** 2026-05-28
**Status:** Accepted

**Context:**
Starting a new data engineering project (RetailPulse) from scratch. 
Need a folder production grade folder structure

**Decision:**
Separate top-level folders by concern: infra, data-sources, databricks, 
powerbi, docs. CI/CD lives in .github/workflows.

**Consequences:**
- Clear separation between infrastructure code, transformation logic, 
  and source simulators
- Any new contributor can navigate the repo without explanation

---

## ADR-002: CLI-First Infrastructure Provisioning
**Date:** 2026-05-28  
**Status:** Accepted

**Context:**
Azure resources can be provisioned via Portal UI or Azure CLI.

**Decision:**
All provisioning done via Azure CLI. Commands documented in infra/setup.md. 
Portal used only for verification and visual inspection.

**Consequences:**
- Every infrastructure decision is reproducible and version-controlled
- infra/setup.md becomes a runbook anyone can follow
- Demonstrating infrastructure-as-code thinking to employers

## ADR-003: Simplified POS Transaction Schema
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
In a real retail POS system, a single transaction is a basket containing 
multiple line items — one receipt can have rice, cooking oil, and bread 
as separate line items under one transaction_id.

**Decision:**
For the simulator, each transaction contains one product (one line item). 
This simplifies data generation while still demonstrating the full 
Bronze → Silver → Gold pipeline.

**Consequences:**
- Easier to generate and reason about in the simulator
- Does not reflect real POS schema complexity
- In production, schema would require both transaction_id (basket) and 
  line_item_id (individual product), identical pattern to e-commerce orders
- Silver layer deduplication logic would need to operate at line_item level,
  not transaction level

---

## ADR-005: Denormalised POS CSV Structure
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
Real POS systems store transactions and line items in separate normalised 
tables. A transaction has one row in the transactions table and multiple 
rows in the line_items table linked by transaction_id.

**Decision:**
The POS CSV simulator outputs a single denormalised flat file containing 
both transaction-level fields (transaction_id, store_id, customer_id, 
payment_method, transaction_total, transaction_time) and line-item-level 
fields (line_item_id, product_id, quantity, unit_price, discount_applied, 
line_total) in every row.

**Consequences:**
- Simpler to generate and ingest in one ADF copy activity
- transaction_total is repeated across all line items belonging to the 
  same transaction — must never be SUMmed directly in Gold aggregations
- Silver layer is responsible for splitting into two normalised Delta 
  tables: dim_transactions and fact_line_items
- Gold layer daily_revenue must SUM(line_total), never SUM(transaction_total)
- This mirrors real-world Bronze landing patterns where source exports 
  are often flat files regardless of the underlying normalised schema


## ADR-005: Simplified E-commerce Order Schema  
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
Real e-commerce orders contain a basket of items under one order_id,
each with its own line_item_id.

**Decision:**
Simulator generates one product per order for consistency with POS 
simulator and pipeline simplicity.

**Consequences:**
- Same tradeoffs as ADR-003
- In production, aggregations at Gold layer would need to GROUP BY 
  order_id before summing revenue to avoid double-counting

## ADR-006: NULL store_id handling for delivery orders
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
E-commerce orders with fulfillment_type = delivery have no associated 
store_id. Storing NULL causes delivery revenue to appear under a NULL 
group in store-level aggregations.

**Decision:**
Assign store_id = 'ONLINE_DELIVERY' for all delivery orders at the 
producer level — in the FastAPI mock server itself. This means NULL 
never enters the pipeline.

**Consequences:**
- NULL never lands in Bronze — problem eliminated at source
- Silver transformation requires no special NULL handling for store_id
- ONLINE_DELIVERY appears as a named channel in all store aggregations
- In a real system this would be enforced at the source API level,
  not patched in Silver — same principle applies


## ADR-007: Email Hashing at Producer Level
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
Customer emails are personally identifiable information (PII). Bronze 
is a raw landing zone accessible to data engineers. Storing raw emails 
in Bronze exposes PII in the event of a data breach.

**Decision:**
Hash customer emails using SHA-256 at the producer level — in the 
FastAPI mock server before the data enters the pipeline. Raw emails 
never land in Bronze.

**Consequences:**
- PII protected at point of ingestion — privacy by design
- Emails are irreversible — cannot be unhashed back to real emails
- Cross-system customer matching by email is still possible — 
  same email always produces same hash
- In production, a real e-commerce system would hash at the API 
  response level before ADF ingests

## ADR-008: units_ordered vs units_received in Inventory Schema
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
Supplier deliveries do not always match purchase orders. Under-delivery,
over-delivery, and damaged goods are common in retail supply chains.

**Decision:**
Store both units_ordered and units_received as separate fields in the 
inventory schema.

**Consequences:**
- Discrepancies are auditable — business can claim refunds or returns
- Gold layer low_stock_alerts uses units_received for current_stock 
  calculation, not units_ordered
- Silver layer flags records where units_received != units_ordered 
  as exceptions for review
- Mirrors real warehouse management system (WMS) behaviour

## ADR-009: last_restocked_date NULL handling in inventory
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
last_restocked_date should only be NULL for products that have never 
been successfully restocked at a given store. For existing products 
with active purchase orders in_transit or ordered status, a previous 
restock date must exist reflecting real operational history.

**Decision:**
NULL last_restocked_date is only valid for genuinely new product-store 
combinations. All other records carry a historical restock date even 
when current order is pending delivery.

**Consequences:**
- Seed data reflects realistic operational history
- Silver layer can flag truly new product-store combinations separately
- Gold layer stock velocity calculations are meaningful — time between 
  restocks can be calculated

## ADR-010: Local simulation of POS CSV ingestion
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
ADF is a cloud service and cannot directly access files on a local 
machine. Real POS systems push CSV exports to a shared location 
(SFTP, Azure Blob) that ADF can reach.

**Decision:**
Python POS simulator runs locally and uploads CSVs directly to ADLS 
Gen2 Bronze container using Azure CLI. This simulates the POS system 
pushing its daily export to the cloud landing zone.

**Consequences:**
- ADF ingests from ADLS Gen2 Bronze, not from local machine
- In production, a Self-hosted Integration Runtime would bridge 
  on-premise POS systems to ADF
- The ingestion pattern is identical — only the source location differs

## ADR-011: ADF dynamic content for date-partitioned Bronze sink
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
ADF Pipeline 1 needs to write POS CSVs to date-partitioned folders 
in Bronze. Hardcoding the date would break the pipeline daily.

**Decision:**
Use ADF dynamic content expression in the Sink dataset directory field:
pos/@{formatDateTime(utcNow(), 'yyyy-MM-dd')}

This automatically creates the correct date folder on each run.

**Consequences:**
- Pipeline is reusable daily without modification
- Bronze layer is correctly date-partitioned
- Databricks can read partitions efficiently by date

## ADR-012: ForEach pipeline for date-partitioned Bronze ingestion
**Date:** 2026-05-30
**Status:** Accepted

**Context:**
The initial ADF pipeline used a single Copy activity with utcNow() 
for the Bronze sink folder. This meant all files would land in today's 
date folder regardless of the actual transaction date in the filename.
For backfilling historical data, this produces incorrect partitioning.

**Decision:**
Restructured pl_ingest_pos_csv to use three activities:
1. Get Metadata — lists all files in staging/pos/
2. ForEach — iterates over each file
3. Copy — extracts the date from the filename using 
   substring(item().name, 17, 10) and writes to bronze/pos/{date}/

**Why substring(item().name, 17, 10):**
Filename format: pos_transactions_2026-05-29.csv
- Characters 0-16: 'pos_transactions_' (17 characters, 0-indexed)
- Characters 17-26: '2026-05-29' (10 characters)
substring(name, 17, 10) extracts exactly the date portion.

**Consequences:**
- Each file lands in the correct date-partitioned Bronze folder 
  regardless of when the pipeline runs
- Historical backfilling works correctly
- Pipeline is reusable daily — new files in staging get correct dates
- If filename format ever changes, substring indices must be updated
- Non-technical explanation: pipeline reads the date label on each 
  file and files it in the correct date folder automatically

**Alternative considered:**
Single Copy activity with utcNow() — rejected because it breaks 
historical backfilling and produces incorrect date partitioning.

## ADR-013: Delete activity for staging cleanup after ingestion
**Date:** 2026-05-30
**Status:** Accepted

**Context:**
After ADF copies files from staging to Bronze, the files remain in 
staging indefinitely. Without cleanup, staging grows unbounded and 
it becomes impossible to tell which files have been ingested.

**Decision:**
Add a Delete activity inside the ForEach, connected after the Copy 
activity. On each iteration — copy file to Bronze, then delete from 
staging.

**Alternatives considered:**
- Archive to staging/archive/{date}/ — keeps audit trail but adds 
  complexity. Appropriate for production, overkill for portfolio.
- Manual cleanup via CLI — error-prone, not automated.
- Keep files in staging — staging grows indefinitely, no clear 
  ingestion boundary.

**Consequences:**
- Staging is always empty after a successful pipeline run
- Clear boundary between ingested and pending files
- If Copy succeeds but Delete fails, file remains in staging — 
  next pipeline run will attempt to copy again (idempotent)
- No archive trail
- In production, archive pattern would be preferred for audit purposes

## ADR-014: Unity Catalog + Managed Identity for ADLS Gen2 Access
**Date:** 2026-05-31
**Status:** Accepted

**Context:**
Databricks serverless compute does not support spark.conf.set() for 
storage credentials. A secure, production-grade authentication method 
is required for Databricks to access ADLS Gen2.

**Decision:**
Use Azure Managed Identity via Access Connector for Azure Databricks, 
registered as a Storage Credential in Unity Catalog, with External 
Locations pointing to each medallion layer container.

**Setup steps:**
1. Created App Registration (sp-retailpulse-dev) — application identity
2. Created Access Connector (ac-retailpulse-dev) — Databricks managed 
   identity for accessing Azure storage
3. Granted Access Connector 'Storage Blob Data Contributor' role on 
   retailpulsedatalake storage account
4. Registered Storage Credential (cred-retailpulse-adls) in Unity 
   Catalog using the Access Connector resource ID
5. Created External Locations for each container:
   - ext-bronze → abfss://bronze@retailpulsedatalake.dfs.core.windows.net/
   - ext-silver → abfss://silver@retailpulsedatalake.dfs.core.windows.net/
   - ext-gold   → abfss://gold@retailpulsedatalake.dfs.core.windows.net/
6. Created Unity Catalog: retailpulse
7. Created schemas: bronze, silver, gold — each linked to its 
   corresponding external location

**Why Managed Identity over Service Principal:**
Managed Identity credentials are handled by Azure automatically — 
no passwords to rotate, no secrets to manage. More secure and less 
operational overhead than Service Principal.

**Why Unity Catalog:**
Single governance layer for all data, users, and permissions across 
the lakehouse. Required for table-level access control and data lineage.
Enables SQL-based access to Delta tables without knowing storage paths.

**Consequences:**
- No credentials in notebook code — authentication is transparent
- Any notebook in the workspace can access Bronze/Silver/Gold via 
  the abfss:// path without additional configuration
- Unity Catalog tracks all table reads and writes as lineage
- Production-grade setup identical to enterprise Databricks deployments

## ADR-015: Serverless Compute over Classic Clusters
**Date:** 2026-05-31
**Status:** Accepted

**Context:**
New Azure Databricks workspaces created after April 2026 no longer 
expose classic cluster creation in the default UI. Multiple approaches 
to enable classic clusters were attempted and failed.

**Decision:**
Use Databricks Serverless compute for all notebook execution.

**Consequences:**
- Notebooks start instantly — no cluster warmup time
- Pay per second of actual compute used
- Slightly higher per-compute-unit cost than classic clusters
- All PySpark code is identical — serverless vs classic is transparent
- Cannot set spark.conf directly — must use Unity Catalog for auth
- Modern pattern — serverless is the direction Databricks is moving


  ## Engineering Notes: Bugs & Difficulties Encountered

### BUG-001: Premature transaction_total accumulation in POS simulator
**Date:** 2026-05-29
**File:** data-sources/pos-simulator/generate_pos_data.py

**Problem:**
transaction_total was being written to each row inside the basket loop
as items were being added. This meant each line item row had a different
transaction_total — only the last row had the correct basket total.

Example with 3 item basket (correct total = 36.96):
- LI_001 had transaction_total = 25.98 (only item 1 accumulated)
- LI_002 had transaction_total = 34.47 (items 1+2 accumulated)
- LI_003 had transaction_total = 36.96 (all items accumulated — correct)

**Fix:**
Split into two passes:
- Pass 1: iterate basket, calculate all line_totals, accumulate 
  transaction_total fully
- Pass 2: iterate calculated items, write rows with final 
  transaction_total on every row

**Lesson:**
When writing denormalised flat files where a parent-level value depends 
on aggregating child-level values, always complete the aggregation before 
writing any rows. Never write while aggregating.


