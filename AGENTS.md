# Project instructions

- Do not add comments or explanatory comments to code unless explicitly requested by the user.
- Keep public exports centralized in package `__init__.py` files; do not add module-level `__all__` declarations in implementation modules.
- Service method prefixes: `get_` for guaranteed single results, `find_` for nullable single results, `list_` for collections, `create_`, `update_`, `delete_` for ORM mutations.
