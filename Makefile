UV ?= uv
ALEMBIC := $(UV) run alembic

.DEFAULT_GOAL := help

.PHONY: help run migrate migrate-new migrate-upgrade migrate-up migrate-down migrate-to \
	migrate-current migrate-history migrate-check migrate-heads migrate-stamp

help: ## Show available commands
	@$(MAKE) -s --no-print-directory help-internal

.PHONY: help-internal
help-internal:
	@$(MAKE) -qp | awk -F':.*?## ' '/^[a-zA-Z0-9][^$$#\/\t=]*:.*?## / { printf "  %-20s %s\\n", $$1, $$2 }' | sort

run: ## Run the bot
	@$(UV) run scheduletelegrambot

migrate: migrate-upgrade ## Alias for migrate-upgrade

migrate-new: ## Create a migration: make migrate-new MESSAGE="add user timezone"
	@test -n "$(MESSAGE)" || (echo 'Usage: make migrate-new MESSAGE="description"' >&2; exit 2)
	@$(ALEMBIC) revision --autogenerate -m "$(MESSAGE)"

migrate-upgrade: ## Apply all pending migrations
	@$(ALEMBIC) upgrade head

migrate-up: ## Apply the next migration only
	@$(ALEMBIC) upgrade +1

migrate-down: ## Revert the most recently applied migration
	@$(ALEMBIC) downgrade -1

migrate-to: ## Upgrade to revision: make migrate-to REVISION=<revision|head>
	@test -n "$(REVISION)" || (echo 'Usage: make migrate-to REVISION=<revision|head>' >&2; exit 2)
	@$(ALEMBIC) upgrade $(REVISION)

migrate-current: ## Display the database's current revision
	@$(ALEMBIC) current

migrate-history: ## Display migration history
	@$(ALEMBIC) history --verbose

migrate-heads: ## Display repository migration head(s)
	@$(ALEMBIC) heads

migrate-check: ## Check that models have no ungenerated migration changes
	@$(ALEMBIC) check

migrate-stamp: ## Mark existing schema without changing it: make migrate-stamp REVISION=head
	@test -n "$(REVISION)" || (echo 'Usage: make migrate-stamp REVISION=<revision|head>' >&2; exit 2)
	@$(ALEMBIC) stamp $(REVISION)
