# Synthetic dirty dataset: category variant mapping

This file lists every category value in `budgetwise_synthetic_dirty.csv` that the original mapping did not cover, and what it now maps to.

- **Raw rows** count all 15,836 input rows.
- **Retained rows** count the rows kept after duplicates and skipped rows are removed.

The 1,634 affected rows reported earlier are raw rows. 1,540 of them are retained.

## Mapping rule

A variant is mapped when it differs from one approved name by a single letter (missing, extra, swapped or wrong) and from every other name by at least three. Case and extra spaces are ignored.

All 192 variants meet this rule. 191 are mapped: 166 in `config/category_mapping.csv` (8 of them added by Bahareh in PR #44) and 25 `Other Income` variants in `parser.py`.

`ent` is left unmapped. It is one letter from `Rent`, but it is also the start of `Entertainment`, which the mapping already accepts as `Entertain`. Its notes and amounts do not show which was meant, so it stays `Uncategorized` and is logged as `unknown_category`.

`Other Income` and its misspellings are handled in `parser.py` rather than the CSV, so they can depend on the transaction type: on an income row they map to `Other`, and on an expense row they stay `Uncategorized`. All 787 raw rows in this dataset are income.

## Summary

| Maps to | Variants | Raw rows | Retained rows |
|---|---:|---:|---:|
| Food | 6 | 160 | 154 |
| Rent | 8 | 159 | 148 |
| Transportation | 16 | 110 | 106 |
| Utilities | 22 | 87 | 85 |
| Entertainment | 31 | 76 | 73 |
| Education | 13 | 23 | 22 |
| Healthcare | 7 | 13 | 12 |
| Savings | 18 | 51 | 49 |
| Other (expense: Others variants) | 16 | 46 | 43 |
| Other (income: Other Income variants) | 25 | 787 | 736 |
| Salary | 16 | 52 | 48 |
| Bonus | 13 | 51 | 46 |
| Uncategorized (ambiguous) | 1 | 19 | 18 |
| **Total** | **192** | **1,634** | **1,540** |

Blank categories (158 raw rows, 154 retained) are missing values, not variants, and stay `Uncategorized` with the reason `category_uncategorized`.

## Every variant

### Food

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Foood` | 48 | 45 |
| `FFood` | 31 | 29 |
| `Fodo` | 23 | 23 |
| `Foo` | 23 | 22 |
| `oFod` | 19 | 19 |
| `ood` | 16 | 16 |

### Rent

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Ret` | 26 | 22 |
| `eRnt` | 24 | 23 |
| `Reent` | 21 | 20 |
| `Retn` | 20 | 19 |
| `Ren` | 19 | 19 |
| `Rnet` | 18 | 15 |
| `Rennt` | 17 | 16 |
| `RRent` | 14 | 14 |

### Transportation

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Tavel` | 13 | 12 |
| `Trave` | 9 | 9 |
| `Trvael` | 9 | 8 |
| `Tarvel` | 8 | 8 |
| `Travle` | 8 | 7 |
| `ravel` | 8 | 8 |
| `Travell` | 7 | 7 |
| `Trvel` | 7 | 7 |
| `rTavel` | 7 | 7 |
| `TTravel` | 5 | 5 |
| `Traavel` | 5 | 5 |
| `Traevl` | 5 | 5 |
| `Traveel` | 5 | 5 |
| `Travvel` | 5 | 5 |
| `Trravel` | 5 | 5 |
| `Trael` | 4 | 3 |

### Utilities

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Utilitiees` | 9 | 9 |
| `Utiilities` | 6 | 6 |
| `Utilitie` | 6 | 6 |
| `Utilitise` | 6 | 6 |
| `Utiliies` | 5 | 5 |
| `Utilitiess` | 5 | 5 |
| `Utillities` | 5 | 5 |
| `Utiltiies` | 5 | 5 |
| `Utliities` | 5 | 5 |
| `tilities` | 5 | 5 |
| `Utiilties` | 4 | 4 |
| `Utiliities` | 4 | 3 |
| `Utiliteis` | 4 | 4 |
| `Utilites` | 3 | 3 |
| `Utilitis` | 3 | 3 |
| `Uitlities` | 2 | 2 |
| `Utiities` | 2 | 2 |
| `Utilitiies` | 2 | 2 |
| `Uttilities` | 2 | 1 |
| `tUilities` | 2 | 2 |
| `UUtilities` | 1 | 1 |
| `Uilities` | 1 | 1 |

### Entertainment

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Entertainmetn` | 6 | 5 |
| `Entertanment` | 5 | 4 |
| `Etertainment` | 5 | 5 |
| `nEtertainment` | 5 | 5 |
| `Enteertainment` | 4 | 4 |
| `Enteratinment` | 4 | 3 |
| `Entertaniment` | 4 | 4 |
| `EEntertainment` | 3 | 3 |
| `Enntertainment` | 3 | 3 |
| `Entertainemnt` | 3 | 3 |
| `Entertainmnt` | 3 | 3 |
| `Entretainment` | 3 | 3 |
| `Enterrtainment` | 2 | 2 |
| `Entertaimnent` | 2 | 2 |
| `Entertainent` | 2 | 2 |
| `Entertainmentt` | 2 | 2 |
| `Entertainnment` | 2 | 2 |
| `Entertianment` | 2 | 2 |
| `Entertinment` | 2 | 2 |
| `Entetainment` | 2 | 2 |
| `Enttertainment` | 2 | 2 |
| `Enertainment` | 1 | 1 |
| `Entertaainment` | 1 | 1 |
| `Entertaiinment` | 1 | 1 |
| `Entertainmennt` | 1 | 1 |
| `Entertainmet` | 1 | 1 |
| `Entertainmnet` | 1 | 1 |
| `Enterttainment` | 1 | 1 |
| `Entetrainment` | 1 | 1 |
| `Entrtainment` | 1 | 1 |
| `Etnertainment` | 1 | 1 |

### Education

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Educatino` | 4 | 4 |
| `Educcation` | 3 | 3 |
| `Edcation` | 2 | 2 |
| `Eduation` | 2 | 1 |
| `Educationn` | 2 | 2 |
| `Eucation` | 2 | 2 |
| `Eudcation` | 2 | 2 |
| `EEducation` | 1 | 1 |
| `Edducation` | 1 | 1 |
| `Educatiion` | 1 | 1 |
| `Educatio` | 1 | 1 |
| `Educatioon` | 1 | 1 |
| `Eduucation` | 1 | 1 |

### Healthcare

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Heealth` | 4 | 3 |
| `Heaalth` | 3 | 3 |
| `Helath` | 2 | 2 |
| `Healh` | 1 | 1 |
| `Healt` | 1 | 1 |
| `Heath` | 1 | 1 |
| `ealth` | 1 | 1 |

### Savings

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Savinngs` | 7 | 6 |
| `aSvings` | 7 | 6 |
| `Saings` | 4 | 4 |
| `Saivngs` | 4 | 4 |
| `Saviings` | 4 | 4 |
| `Savigs` | 3 | 3 |
| `Savingss` | 3 | 3 |
| `Svings` | 3 | 3 |
| `Saavings` | 2 | 2 |
| `Savinggs` | 2 | 2 |
| `Savins` | 2 | 2 |
| `Savnigs` | 2 | 2 |
| `Savvings` | 2 | 2 |
| `avings` | 2 | 2 |
| `SSavings` | 1 | 1 |
| `Savigns` | 1 | 1 |
| `Savinsg` | 1 | 1 |
| `Savngs` | 1 | 1 |

### Other (expense: Others variants)

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Otherrs` | 6 | 5 |
| `thers` | 6 | 5 |
| `Othhers` | 5 | 5 |
| `Othres` | 4 | 4 |
| `Ohters` | 3 | 3 |
| `Otehrs` | 3 | 3 |
| `Othes` | 3 | 3 |
| `Otthers` | 3 | 3 |
| `OOthers` | 2 | 2 |
| `Ohers` | 2 | 1 |
| `Oters` | 2 | 2 |
| `Othesr` | 2 | 2 |
| `Othrs` | 2 | 2 |
| `Otheers` | 1 | 1 |
| `Otherss` | 1 | 1 |
| `tOhers` | 1 | 1 |

### Other (income: Other Income variants)

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Other Income` | 749 | 700 |
| `Oter Income` | 3 | 3 |
| `Othr Income` | 3 | 3 |
| `Othre Income` | 3 | 2 |
| `tOher Income` | 3 | 3 |
| `Othe Income` | 2 | 2 |
| `Other  Income` | 2 | 1 |
| `Other Icnome` | 2 | 2 |
| `Other Incoem` | 2 | 2 |
| `Other Incoome` | 2 | 2 |
| `Other Inncome` | 2 | 2 |
| `OOther Income` | 1 | 1 |
| `Oher Income` | 1 | 1 |
| `Ohter Income` | 1 | 1 |
| `Otehr Income` | 1 | 1 |
| `Othe rIncome` | 1 | 1 |
| `Otheer Income` | 1 | 1 |
| `Other IIncome` | 1 | 1 |
| `Other Icome` | 1 | 1 |
| `Other Incmoe` | 1 | 1 |
| `Other Incoe` | 1 | 1 |
| `Other Incom` | 1 | 1 |
| `Other Inome` | 1 | 1 |
| `Other nIcome` | 1 | 1 |
| `OtherIncome` | 1 | 1 |

### Salary

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Salaryy` | 7 | 6 |
| `Saary` | 6 | 6 |
| `Salry` | 6 | 5 |
| `alary` | 6 | 5 |
| `aSlary` | 4 | 4 |
| `Salaary` | 3 | 3 |
| `Sallary` | 3 | 3 |
| `SSalary` | 2 | 2 |
| `Saalary` | 2 | 2 |
| `Saalry` | 2 | 2 |
| `Salay` | 2 | 2 |
| `Salayr` | 2 | 1 |
| `Salray` | 2 | 2 |
| `Slaary` | 2 | 2 |
| `Slary` | 2 | 2 |
| `Salarry` | 1 | 1 |

### Bonus

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `Bnous` | 6 | 4 |
| `Bonu` | 6 | 5 |
| `Bonnus` | 5 | 5 |
| `Bouns` | 5 | 4 |
| `BBonus` | 4 | 4 |
| `Bonuus` | 4 | 4 |
| `oBnus` | 4 | 4 |
| `onus` | 4 | 3 |
| `Bons` | 3 | 3 |
| `Boonus` | 3 | 3 |
| `Bous` | 3 | 3 |
| `Bnus` | 2 | 2 |
| `Bonsu` | 2 | 2 |

### Uncategorized (ambiguous)

| Raw value | Raw rows | Retained rows |
|---|---:|---:|
| `ent` | 19 | 18 |
