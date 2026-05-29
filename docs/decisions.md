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


