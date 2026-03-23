# IMS Hackathon — Sales ETL Data Engineering (IICS)

**Event:** Campus Visit – IMS Ghaziabad  
**Date:** 23-Mar-2026  

---

## Project Overview

A complete **Informatica IICS ETL pipeline** that reads raw sales CSV files, cleans dirty data, enriches it via lookups, computes KPIs, and generates analytical output reports.

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
