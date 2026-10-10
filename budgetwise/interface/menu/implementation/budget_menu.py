"""Interactive monthly budget selection and display."""

from datetime import datetime

from budgetwise.analysis.budgets.implementation.monthly_comparison import (
    compare_user_month,
    load_budget_config,
)
from budgetwise.analysis.budgets.implementation.group_comparison import (
    compare_group_month,
)


def prompt_month():
    while True:
        raw = input("Month (YYYY-MM, for example 2024-04): ").strip()

        try:
            selected = datetime.strptime(raw, "%Y-%m")
            return selected.year, selected.month
        except ValueError:
            print("Please enter a valid year and month as YYYY-MM.")


def prompt_budget_category(records, config):
    categories = sorted(
        set(config["limits"])
        | {record["category"] for record in records}
    )
    lookup = {category.lower(): category for category in categories}

    print("Categories:", ", ".join(categories))

    while True:
        raw = input("Category: ").strip().lower()

        if raw in lookup:
            return lookup[raw]

        print("Please choose a category from the displayed list.")


def prompt_users(records, single=False):
    known_users = {record["user_id"] for record in records}

    print("Available users:", ", ".join(sorted(known_users)))

    while True:
        label = (
            "User ID: "
            if single
            else "User IDs separated by commas: "
        )
        raw = input(label).strip()

        users = [value.strip() for value in raw.split(",")]

        if not users or any(not value for value in users):
            print("Please enter non-empty user IDs.")
            continue

        if single and len(users) != 1:
            print("Please enter exactly one user ID.")
            continue

        unknown = set(users) - known_users

        if unknown:
            print("Unknown user IDs:", ", ".join(sorted(unknown)))
            continue

        return users


def display_comparison(result):
    print(f"Recorded spending: {result['recorded_actual']:,.2f}")

    limit = result["limit"]

    if limit is not None:
        print(f"Budget benchmark: {limit:,.2f}")

    status = result["status"]

    if status == "no_data":
        print("No dated records for this selection.")
    elif status == "unbudgeted":
        print("No budget is defined for this selection.")
    elif status == "incomplete_budget":
        print("Some users have no budget; group comparison is unavailable.")
    elif status == "equal":
        print("Recorded spending equals the budget.")
    elif status == "over":
        print(f"Over budget by {result['difference']:,.2f}")
    elif status == "under":
        print(f"Under budget by {result['difference']:,.2f}")


def run_budget_menu(records):
    """Use the complete cleaned record list for budget comparison."""

    records = list(records)

    if not records:
        print("No cleaned records are available. Load a dataset first.")
        return

    config = load_budget_config()

    print("\n=== Monthly Budget Comparison ===")
    print("Limits are proposed project benchmarks for team review.")
    print("Results describe recorded transactions only.")

    year, month = prompt_month()
    category = prompt_budget_category(records, config)

    selected_month = f"{year:04d}-{month:02d}"
    baseline = config.get("baseline", {})

    baseline_start = baseline.get("start")
    baseline_end = baseline.get("end")

    if baseline_start and baseline_end:
        if baseline_start[:7] <= selected_month <= baseline_end[:7]:
            print(
                "Descriptive baseline-period comparison: "
                "this period also contributed to the budget limits."
            )

    print("1. One user")
    print("2. Selected group of users")
    print("3. All users with dated records in this month")

    while True:
        scope = input("Choose 1, 2, or 3: ").strip()

        if scope in ("1", "2", "3"):
            break

        print("Please choose 1, 2, or 3.")

    if scope == "1":
        user_id = prompt_users(records, single=True)[0]

        result = compare_user_month(
            records, config, user_id, year, month, category
        )

        print(f"\nUser: {user_id} | Month: {selected_month}")
        print(f"Category: {category}")
        display_comparison(result)

        if (
            result["has_month_records"]
            and not result["has_category_expense_record"]
        ):
            print(
                "No expense was recorded in this category. "
                "This does not prove actual spending was zero."
            )

        return

    requested_users = (
        prompt_users(records)
        if scope == "2"
        else None
    )

    result = compare_group_month(
        records,
        config,
        year,
        month,
        category,
        requested_users=requested_users,
    )

    print(f"\nMonth: {selected_month} | Category: {category}")
    print(f"Included users: {result['group']['user_count']}")
    display_comparison(result["group"])

    if result["excluded_no_month_records"]:
        print(
            "Excluded users without monthly records:",
            ", ".join(result["excluded_no_month_records"]),
        )

    if result["users_without_category_expenses"]:
        print(
            "Users without recorded expenses in this category:",
            ", ".join(result["users_without_category_expenses"]),
        )
        print("Absence of records does not prove zero actual spending.")

    if result["missing_budget_users"]:
        print(
            "Users without a defined budget:",
            ", ".join(result["missing_budget_users"]),
        )

    print("\nIndividual results:")

    for user_id, details in result["users"].items():
        print(f"\nUser: {user_id}")
        display_comparison(details)
