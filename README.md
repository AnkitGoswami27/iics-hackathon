# IMS Hackathon — Sales ETL Data Engineering (IICS)

**Event:** Campus Visit – IMS Ghaziabad  
**Date:** 23-Mar-2026  

---

## Project Overview

A complete **Informatica IICS ETL pipeline** that reads raw sales CSV files, cleans dirty data, enriches it via lookups, computes KPIs, and generates analytical output reports.

---

## Theory & Approach

### What is ETL?
ETL stands for **Extract, Transform, Load** — the backbone of any data engineering pipeline.

| Phase | What We Did |
|---|---|
| **Extract** | Read 4 CSV source files (dirty transactions, clean transactions, product master, store master) into IICS as flat file sources |
| **Transform** | Cleansed dirty data, standardised formats, applied lookups to enrich records, computed business KPIs |
| **Load** | Wrote final validated, enriched records into output CSV target files for reporting |

---

### Why Two Separate Source Files?
Real-world data arrives in two states:
- **Clean data** (`sales_transactions.csv`) — already validated, ready to use directly
- **Dirty data** (`sales_transactions_dirty.csv`) — contains errors that must be fixed before use

Both must be **merged into one unified dataset** for reporting. This is a standard pattern in data warehousing called **data consolidation**.

---

### Data Quality — Why It Matters
Before any analysis, data must be trusted. Bad data produces wrong KPIs and misleading reports. We applied **8 cleansing rules**:

| Problem | Why It's a Problem | Fix Applied |
|---|---|---|
| Negative QUANTITY | A sale cannot have negative units sold | Convert to positive using ABS() |
| Zero QUANTITY | No transaction happened — meaningless row | Reject the record |
| Negative DISCOUNT | Discount cannot be negative | Convert to positive using ABS() |
| DISCOUNT > 100% | Physically impossible — can't discount more than full price | Reject |
| NULL STORE_ID | Cannot link to a store — data is incomplete | Reject |
| NULL PRODUCT_ID | Cannot identify what was sold | Reject |
| Invalid date | Inconsistent date formats break aggregations and sorting | Standardise to MM/DD/YYYY |
| Duplicate records | Double-counting inflates revenue figures | Mark as DUPLICATE |

Rejected records are **not discarded** — they are stored in `TGT_REJECTED_SALES.csv` for audit and reprocessing. This is called a **data quality audit trail**.

---

### Lookup Enrichment — Why We Join Masters
The transaction file only contains IDs (`STORE_ID`, `PRODUCT_ID`). IDs alone are not useful for reporting. We need human-readable names and pricing:

- **LKP_PRODUCT** → adds `PRODUCT_NAME`, `CATEGORY`, `BRAND`, `UNIT_PRICE`
- **LKP_STORE** → adds `STORE_NAME`, `CITY`, `STATE`

This is called **dimension enrichment** — joining a fact (transaction) with its dimension tables (product, store) to create a meaningful, analysis-ready dataset. It mirrors the **Star Schema** concept used in data warehouses.

> If a STORE_ID or PRODUCT_ID in a transaction has **no match** in the master table, the record is rejected — because we cannot compute accurate revenue without a valid price.

---

### KPI Computation — Business Metrics
Three key financial metrics are computed per transaction line:

$$GROSS\_AMOUNT = UNIT\_PRICE \times QUANTITY$$

$$DISCOUNT\_VALUE = GROSS\_AMOUNT \times \frac{DISCOUNT\_PERCENT}{100}$$

$$NET\_REVENUE = GROSS\_AMOUNT - DISCOUNT\_VALUE$$

These are computed **after** the lookup so that `UNIT_PRICE` is available from the product master (the authoritative source for pricing — not the transaction file).

---

### Union — Merging Two Clean Streams
After cleaning dirty data and normalising both sources to the same 6-column structure, a **Union transformation** combines them into one stream. This avoids duplication of lookup and KPI logic — both branches feed into a single pipeline after the union.

---

### Aggregation & Ranking (Tasks 7 & 8)
For analytical reports, raw transaction data is aggregated:

- **Task 7 (Store Leaderboard):** Groups all transactions by `STORE_ID` → sums revenue, counts transactions → sorts descending → assigns rank. Identifies top-performing stores.
- **Task 8 (High Value Transactions):** Computes average `NET_AMOUNT` per month using an Aggregator → joins back to each transaction → filters rows where individual NET_AMOUNT exceeds the monthly average. Surfaces premium purchases.

---

### Why IICS (Informatica Intelligent Cloud Services)?
IICS provides a **no-code/low-code** visual ETL designer where each transformation is a canvas object:

| IICS Object | Purpose |
|---|---|
| Source | Read CSV files |
| Expression | Compute new fields, rename fields, apply formulas |
| Router | Split data into valid/rejected streams based on conditions |
| Lookup | Join with reference/master data |
| Union | Merge multiple input streams into one |
| Aggregator | Group and aggregate (SUM, COUNT, AVG) |
| Sorter | Order rows (needed before rank assignment) |
| Filter | Keep only rows meeting a condition |
| Joiner | Join two streams (like SQL JOIN) |
| Target | Write output to CSV or database |

Each mapping runs as a **Mapping Task** and can be orchestrated in a **Taskflow** for end-to-end pipeline execution.

---

## Source Files

| File | Records | Description |
|---|---|---|
| `Source/sales_transactions.csv` | 16,070 | Clean sales transactions |
| `Source/sales_transactions_dirty.csv` | 1,014 | Dirty transactions needing cleansing |
| `Source/product_master.csv` | 50 | Product lookup (name, category, brand, price) |
| `Source/store_master.csv` | 8 | Store lookup (name, city, state) |

---

## Output Files

| File | Description |
|---|---|
| `Output/cleaned.csv` | Cleaned dirty transactions (valid + rejected flags) |
| `Output/rejected.csv` | All rejected records with reasons |
| `Output/TGT_CLEAN_SALES.csv` | Task 1 — Merged clean dataset (dirty valid + clean transactions) with lookup enrichment + KPIs |
| `Output/TGT_REJECTED_SALES.csv` | Task 2 — Rejected records with rejection reason |
| `Output/TGT_STORE_SALES_LEADERBOARD.csv` | Task 7 — Store-wise sales ranking by revenue |
| `Output/TGT_HIGH_VALUE_TRANSACTIONS.csv` | Task 8 — Transactions above monthly average NET_AMOUNT |

---

## Cleansing Rules Applied (Dirty File)

| Issue | Rule |
|---|---|
| Negative QUANTITY | Convert to positive (ABS) |
| Zero QUANTITY | Reject |
| Negative DISCOUNT_PERCENT | Convert to positive (ABS) |
| DISCOUNT_PERCENT > 100 | Reject |
| NULL STORE_ID or PRODUCT_ID | Reject |
| Invalid date format | Standardise to MM/DD/YYYY |

---

## KPI Formulas

| KPI | Formula |
|---|---|
| `GROSS_AMOUNT` | `UNIT_PRICE × QUANTITY` |
| `DISCOUNT_VALUE` | `GROSS_AMOUNT × (DISCOUNT_PERCENT / 100)` |
| `NET_REVENUE` | `GROSS_AMOUNT − DISCOUNT_VALUE` |

---

## IICS Mappings

| Mapping | Task | Description |
|---|---|---|
| `M_CLEAN_DIRTY_SALES` | Pre-Task | Clean dirty file → cleaned.csv + rejected.csv |
| `M_TASK1_TGT_CLEAN_SALES` | Task 1 | Union dirty valid + clean → Lookup → KPIs → TGT_CLEAN_SALES.csv |
| `M_TASK2_TGT_REJECTED_SALES` | Task 2 | rejected.csv → TGT_REJECTED_SALES.csv |
| `M_TASK7_STORE_SALES_LEADERBOARD` | Task 7 | Aggregate by store → rank by revenue |
| `M_TASK8_HIGH_VALUE_TRANSACTIONS` | Task 8 | Filter transactions > monthly average NET_AMOUNT |

---

## Pipeline Flow (Task 1)

```
sales_transactions_dirty.csv  →  EXP_DIRTY  ──→
                                               UNION → LKP_PRODUCT → LKP_STORE → EXP_CALC → TGT_CLEAN_SALES.csv
sales_transactions.csv        →  EXP_CLEAN  ──→
```
