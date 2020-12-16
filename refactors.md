# Refactors

* Switched formatter to use black instead of autopep.
* Refactored code to follow style guide (variable naming, spacing, etc).
* Added expiry timestamp to generated JWT, not have any tokens that are valid forever.
* Refactored routes to use a default error handler and added correct error attributes for frontend to display errors (iteration 3).
* Refactored db.py to include constants as class attributes.
* Refactored routes to parse params in the same place instead of across multiple functions.
* Removed unnecessary function calls from tests and used helpers to reduce dulpicate code.