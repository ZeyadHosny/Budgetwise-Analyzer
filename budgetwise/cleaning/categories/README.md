# Category Cleaning
This feature cleans and standardizes transaction category values into a fixed set of approved categories.

## Responsibility

| Item | Details |
|---|---|
| Responsible | Henrieta |
| Domain reviewers | Bahareh (`P1.2`) and Sarah (`P2.2`) |
| PR approval | Zeyad or Patrick |
| Tasks | `P1.2` profiling and `P2.2` implementation |
| Status | Implemented and under review |

## Purpose
The raw dataset contains category values with:

- different capitalization
- spelling mistakes
- abbreviations
- extra spaces
- missing values


These values are converted into approved category names.


FOOD    -> Food
Fod     -> Food
Rentt   -> Rent
Traval  -> Transportation
Helth   -> Healthcare
Misc    -> Other


Missing or blank categories are kept in the dataset and mapped to:

Uncategorized


## Approved Categories

The approved categories:

Food
Rent
Transportation
Entertainment
Utilities
Education
Healthcare
Savings
Other
Freelance
Investment
Bonus
Salary
Uncategorized

## Category Mapping

The raw-to-normalized category mapping is stored in:

config/category_mapping.cs

The mapping is closed, meaning unknown values are not allowed to pass through unchanged.

## Public Function

Other parts of the project can use:


from budgetwise.cleaning.categories import normalize_category


The function returns:

(normalized_category, reason_code)


## Reason Codes

| Reason Code | Meaning |
|---|---|
| `CATEGORY_NORMALIZED` | The category was corrected or standardized |
| `CATEGORY_UNCATEGORIZED` | The category was missing or blank |
| `UNKNOWN_CATEGORY` | The value was not found in the approved mapping |


## Main Files

budgetwise/cleaning/categories/
├── implementation/
│   └── parser.py
├── testing/
│   └── test_parser.py
├── supplementary/
├── __init__.py
└── README.md


## Implementation Update

Whitespace handling was corrected so values with extra spaces are recorded as normalized.


## Testing

The tests cover:

- capitalization differences
- spelling mistakes
- abbreviations
- extra spaces
- missing values
- unknown categories


## Project Connection

The category work is completed in two stages:


P1.2 -> profile and organize raw category values
P2.2 -> implement category normalization

The category variants identified during `P1.2` are used to build the normalization rules for `P2.2`.

