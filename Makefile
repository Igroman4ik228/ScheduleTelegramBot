project_dir := .
package_dir := src

.PHONY: run
run: ## Run bot
	@uv run python -O $(package_dir)

.PHONY: migrate-new
migrate-new: ## Create a new migration
	@uv run alembic revision --autogenerate \
	$(if $(filter-out $@,$(MAKECMDGOALS)),--message "$(filter-out $@,$(MAKECMDGOALS))")

.PHONY: migrate-all
migrate: ## Apply all migrations
	@uv run alembic upgrade head

.PHONY: migrate-up
migrate-up: ## Apply the next migration only
	@uv run alembic upgrade +1

.PHONY: migrate-down
migrate-down: ## Revert the last migration
	@uv run alembic downgrade -1

.PHONY: migrate-to
migrate-to: ## Upgrade or downgrade to a specific revision: make migrate-to <revision_id>
	@uv run alembic upgrade $(filter-out $@,$(MAKECMDGOALS))

.PHONY: migrate-reset
migrate-reset: ## Reset database: downgrade to base and apply all migrations
	@uv run alembic downgrade base
	@uv run alembic upgrade head

# Allow passing arguments after target (e.g. make migrate-to <revision_id>)
%:
	@: