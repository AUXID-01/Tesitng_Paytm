# Cognee Knowledge Graph Evaluation: Running Notes

## Phase 0 & 1: Bare Ingestion (Setup & Unstructured)
*(To be completed based on earlier unstructured tests)*

## Phase 2: Structured Ingestion & Determinism
*(To be completed based on Phase 2 JSON seeding tests)*

## Phase 3: Write-Then-Read Discipline & Entity Resolution
- **Write/Read Latency:** 
  - Structured writes (`cognee.add` + `cognee.cognify`) take roughly **5-8 seconds** on average per event, with some outlier spikes (up to 30-40s) depending on cloud load.
  - Read queries via `cognee.search()` generally take between **5-15 seconds** to process the natural language query, traverse the graph, and synthesize the result.
- **Debt Aggregation:** Cognee correctly aggregates amounts across sequential events. When querying for Suresh's total debt after multiple separate transactions of 100, 150, and 100 INR, the synthesized response accurately calculated the combined sum (350 INR).
- **Entity Resolution Behavior:** 
  - **Result:** Cognee created **two distinct customer nodes** rather than unifying them.
  - **Context:** We wrote a transaction for `"Suresh"` (`c_suresh_01` with a phone number) and later wrote one for `"suresh"` (`c_suresh_02_unknown` with no phone number). 
  - **Takeaway:** Cognee prioritizes the explicit schema identifiers (like `customer_id`) and structural differences over aggressive fuzzy-name matching. This is highly beneficial for VyaparSetu as it prevents accidental merging of two different customers who happen to share the common name "Suresh".

## Phase 4: Core Queries
*(Pending)*

## Phase 5: Isolation Test
*(Pending)*

## Phase 6: Latency Test
*(Pending)*
