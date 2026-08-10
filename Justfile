run:
  uv run main.py

check:
  ruff check

format:
  ruff format

configure-git:
  git config commit.gpgsign false
  git config tag.gpgsign false
  git config user.name edr-lee
  git config user.email 204632833+edr-lee@users.noreply.github.com
