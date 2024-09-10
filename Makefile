generate:
	alembic revision --m="${NAME}" --autogenerate

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade "${revision}"