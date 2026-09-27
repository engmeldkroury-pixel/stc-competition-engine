# R8 history capture run log

- 36343955073: failed in local GitHub runner test collection because the shared conftest imports Pydantic. No SSH or database access occurred. Corrected workflow to install requirements.txt, keeping all tests. Existing 3 local reader tests passed; remote acceptance is pending.
- The ordinary authenticated inbox capture 36343734257 succeeded but only returned old September 21 data. Never use its seven incomplete/no-entry observations as evidence for the latest trades.
