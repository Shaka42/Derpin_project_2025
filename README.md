# Nutrient Adequacy Dataset (District-Level)

## Dataset Overview
- **File**: `merged_nutrients.csv`  
- **Unit of observation**: District  
- **Key column**: `district`  
- **Total districts**: 122  
- **Total indicators**: 12  

### Example Indicators
- Average Consumption adequacy of nutrients/Calcium  
- Average Consumption adequacy of nutrients/Iron  
- Average Consumption adequacy of nutrients/Proteins  
- Average Consumption adequacy of nutrients/Vitamin A  
- Average Consumption adequacy of nutrients/Vitamin B12  
- Average Consumption adequacy of nutrients/Zinc  

## Methodology
1. Standardize the district key across all inputs.  
2. Detect and coerce numeric indicator columns (preserve units).  
3. Remove duplicates → one record per district per indicator.  
4. Merge indicators via outer join on district (preserve coverage).  
5. Compute descriptive statistics & coverage.  
6. Create a Composite Adequacy Score = mean of available indicators per district.  

## Data Cleaning Rules
- Trim & harmonize district names; treat empty/NA as `Unknown`.  
- Coerce numeric fields (`'1,234' → 1234`).  
- Drop duplicate rows (keep first).  
- Retain indicators with at least one non-missing value.  

# Communicating Composite Vulnerability  

## Composite Vulnerability Index (CVI)  
The CVI combines four factors into one score:  
- Health system vulnerability  
- Nutrition adequacy  
- Per capita food consumption  
- Climate change vulnerability  

**Scale:** 0 = low, 1 = high  

**Insight:** Acholi, Lango, and Busoga are the most vulnerable. Kampala and Elgon are the least.  
➡️ Support should focus first on the high-risk regions.  

---

## Health System Vulnerability  
Shows how much regions are at risk from weak health services.  

**Insight:** Lango is the most vulnerable. Kampala is the least.  
➡️ Improving health systems in Lango and similar regions will reduce risk.  

---

## Nutrition Adequacy vs Food Consumption  
Compares how much food people eat with how nutritious it is.  

- Higher = better nutrition  
- Further right = more food  

**Insight:** Some regions eat more food but still lack good nutrition.  
➡️ Programs should promote balanced diets, not just bigger food supply.  

---

## Vulnerability to Climate Change  
Shows how regions are exposed to risks like droughts and floods.  

**Insight:** Kigezi, Busoga, and Ankole are most at risk. Kampala and Elgon are least.  
➡️ High-risk regions need urgent climate adaptation.
---

## Vulnerability to Climate Change Index by Region  

This chart shows how different regions are exposed to the **risks of climate change**, with values ranging from **0 (low vulnerability) to 1 (high vulnerability).**

- **Most vulnerable:** Kigezi, Busoga, and Ankole → greatest climate risks.  
- **Least vulnerable:** Kampala and Elgon → still require resilience strategies.  


> **Insight:**  
> Regions like Kigezi and Busoga need urgent **climate adaptation measures**, while lower-risk regions should focus on sustaining their resilience.
## Merge Logic
- Outer join on `district`.  
- Descriptive indicator names retained (avoid unit confusion).  
- No imputation — missing values are explicit.  

## Quality Checks
### Coverage by Indicator  
All 12 indicators cover 100% of districts (122/122).  

### Summary sample Statistics 
| Indicator | Mean | Median | Min | Max |
|-----------|------|--------|-----|-----|
| Calcium   | 63.7 | 65.8   | 7.9 | 100 |
| Iron      | 67.6 | 67.2   | 24.9| 100 |
| Proteins  | 87.0 | 88.7   | 55.9| 100 |
| Vitamin A | 87.2 | 88.1   | 17.8| 100 |
| Vitamin C | 97.7 | 100.0  | 9.1 | 100 |

## Analytical Readiness
- Cross-district comparisons per nutrient.  
- Composite adequacy score → quick ranking.  
- Ready for linkage with socio-economic or health indicators via `merged_index.csv`.  

## District Rankings
### Bottom (low adequacy)
| District | Score |
|----------|-------|
| Lamwo    | 42.8  |
| Nwoya    | 56.9  |
| Yumbe    | 57.8  |
| Buvuma   | 62.0  |
| Pader    | 62.4  |

### Top (high adequacy)
| District   | Score |
|------------|-------|
| Ngora      | 100.0 |
| Palisa     | 99.2  |
| Kapchorwa  | 94.0  |
| Kalangala  | 92.6  |
| Kabarole   | 92.2  |

## Policy Action Points
- Maternal & Child Health → Focus on Iron & Folate in low-scoring districts.  
- Child Survival → Expand Vitamin A supplementation.  
- Immunity & Morbidity → Promote Zinc & Vitamin C (legumes, fruits, school feeding).  
- Energy & Productivity → Fortify staples, link with cash transfers.  
- Local Production → Promote nutrient-dense crops (OFSP, beans, groundnuts).  

## Implementation Plan
1. Rank districts → select bottom 10% for intervention.  
2. Identify bottom three nutrient gaps per district.  
3. Co-design district menus (school feeding, facility counseling).  
4. Allocate fortified commodities & supplements.  
5. Monitor using same indicators monthly.  

## Key Performance Indicators (KPIs)
- +10–15% improvement in median adequacy (12 months).  
- >90% coverage for Iron/Folate (pregnancy) & Vitamin A (U5).  
- Higher dietary diversity in school feeding sites.  
- Reduce districts <50% adequacy by half in 1 year.  

## Risks & Mitigation
- Data gaps → Collect more & triangulate with HMIS/LSMS.  
- Seasonality → Time distributions before lean season.  
- Supply chain → Buffer stocks & multi-supplier contracts.  
- Behavioral adoption → Strengthen SBCC & CHW follow-up.  

## Reproducibility of Solution
- The solution is reproducible via a streamlit app in the notebook

## How to Use
1. Open `merged_nutrients.csv` in R, Python, Excel, or PowerBI.  
2. Use composite score to prioritize districts.  
3. Join with `merged_index.csv` for integrated planning.  
4. Target missing data improvements where needed.  

## Glossary
- **Adequacy** → How much observed consumption meets recommended intake.  
- **Composite Adequacy Score** → Mean of all available nutrient indicators.  
- **Coverage** → Share of districts with non-missing values.  
