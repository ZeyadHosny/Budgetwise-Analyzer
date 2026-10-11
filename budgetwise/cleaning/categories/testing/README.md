# cleaning/categories/testing

Henrietta · `P2.2` · domain reviewer Sarah

## What is tested

`test_parser.py` checks `normalize_category()` against all 46 nonblank category variants found in the raw dataset, plus missing, whitespace and unknown inputs.

| Group | Inputs | Expected result | Tests |
|---|---|---|---|
| Food | `Food`, `food`, `FOOD`, `Foods`, `Fod`, `Foodd` | `Food` | 6 |
| Rent | `Rent`, `rent`, `RENT`, `Rentt`, `Rnt` | `Rent` | 5 |
| Transportation | `Travel`, `travel`, `TRAVEL`, `Traval`, `Travl` | `Transportation` | 5 |
| Entertainment | `Entertainment`, `entertainment`, `Entertain`, `Entrtnmnt` | `Entertainment` | 4 |
| Utilities | `Utilities`, `utilities`, `Utility`, `Utilties`, `Utlities` | `Utilities` | 5 |
| Education | `Education`, `education`, `Educaton`, `EDU` | `Education` | 4 |
| Healthcare | `Health`, `health`, `HEALTH`, `Helth` | `Healthcare` | 4 |
| Savings | `Savings`, `savings`, `SAVINGS`, `Saving` | `Savings` | 4 |
| Other | `Other`, `Others`, `others`, `OTHERS`, `Misc` | `Other` | 5 |
| Exact only | `Freelance`, `Investment`, `Bonus`, `Salary` | unchanged | 4 |
| Whitespace | `"  Food  "` | `("Food", "CATEGORY_NORMALIZED")` | 1 |
| Missing | `""`, `"   "`, `None` | `("Uncategorized", "CATEGORY_UNCATEGORIZED")` | 3 |
| Unknown | `CarPayment` | `("Uncategorized", "UNKNOWN_CATEGORY")` | 1 |
| **Total** | | | **51** |

Reason codes checked:

- The input is already the approved name, e.g. `"Food"`: reason is `None`.
- Any other recognized variant, including extra spaces: `CATEGORY_NORMALIZED`.
- Missing input: `CATEGORY_UNCATEGORIZED`.
- Not in the mapping: `UNKNOWN_CATEGORY`.



## Run

From the project root:

```bash
python -m unittest budgetwise.cleaning.categories.testing.test_parser -v
```

