# interface/menu/testing

Sarah · domain reviewer Bahareh

## Required cases

- [ ] Each of options 1 to 5 triggers the right action
- [ ] `9`, `banana`, and empty input each reprompt without crashing
- [ ] `2023-13-45` is rejected at the date prompt
- [ ] End date before start date is rejected
- [ ] A date range matching nothing reports zero, not an error
- [ ] An unknown category reports and reprompts
- [ ] Option 5 exits the loop
- [ ] Option 4 reads the error log and shows something useful when it is empty

## Testing something that reads input()

Patch `input` so the test supplies a scripted sequence of answers:

```python
from unittest.mock import patch

with patch("builtins.input", side_effect=["2", "2023-01-01", "2023-12-31", "5"]):
    run_menu()
```

`unittest.mock` is standard library. Keep the menu loop separate from the
prompts — a loop that only dispatches is far easier to test than one that also
validates dates.

## Run

```bash
python -m unittest discover
```

Check how many tests ran, not just that it said `OK`.
