project_dir := .
package_dir := src

# Command: which uv
UV := ~/.local/bin/uv

.PHONY: run
run: ## Run bot
	@$(UV) run python -O $(package_dir)

.PHONY: migrate-new
migrate-new: ## Create a new migration
	@$(UV) run alembic revision --autogenerate \
	$(if $(filter-out $@,$(MAKECMDGOALS)),--message "$(filter-out $@,$(MAKECMDGOALS))")

.PHONY: migrate-all
migrate-all: ## Apply all migrations
	@$(UV) run alembic upgrade head

.PHONY: migrate-up
migrate-up: ## Apply the next migration only
	@$(UV) run alembic upgrade +1

.PHONY: migrate-down
migrate-down: ## Revert the last migration
	@$(UV) run alembic downgrade -1

.PHONY: migrate-to
migrate-to: ## Upgrade or downgrade to a specific revision: make migrate-to <revision_id>
	@$(UV) run alembic upgrade $(filter-out $@,$(MAKECMDGOALS))

.PHONY: migrate-reset
migrate-reset: ## Reset database: downgrade to base and apply all migrations
	@$(UV) run alembic downgrade base
	@$(UV) run alembic upgrade head

# Allow passing arguments after target (e.g. make migrate-to <revision_id>)
%:
	@: