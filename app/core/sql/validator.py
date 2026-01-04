from sqlglot import parse_one
from sqlglot.expressions import (
    Select,
    Insert,
    Update,
    Delete,
    Drop,
    Alter,
    Create,
    Subquery,
    Join,
)


class SQLValidationError(Exception):
    pass


class SQLValidator:
    """
    AST-level SQL validator.
    Rejects unsafe, ambiguous, or non-analytic queries.
    """

    def validate(self, sql: str) -> None:
        try:
            ast = parse_one(sql)
        except Exception as e:
            raise SQLValidationError(f"Invalid SQL syntax: {e}")

        self._ensure_select_only(ast)
        self._block_destructive_ops(ast)
        self._block_subqueries(ast)
        self._block_cross_joins(ast)
        self._ensure_limit(ast)

    def _ensure_select_only(self, ast) -> None:
        if not ast.find(Select):
            raise SQLValidationError("Only SELECT queries are allowed")

    def _block_destructive_ops(self, ast) -> None:
        forbidden = (Insert, Update, Delete, Drop, Alter, Create)
        for node in ast.walk():
            if isinstance(node, forbidden):
                raise SQLValidationError(
                    f"Destructive operation not allowed: {type(node).__name__}"
                )

    def _block_subqueries(self, ast) -> None:
        for node in ast.walk():
            if isinstance(node, Subquery):
                raise SQLValidationError("Subqueries are not allowed")

    def _block_cross_joins(self, ast) -> None:
        for node in ast.walk():
            if isinstance(node, Join):
                if node.args.get("kind") == "cross":
                    raise SQLValidationError("CROSS JOIN is not allowed")

    def _ensure_limit(self, ast) -> None:
        if ast.args.get("limit") is None:
            raise SQLValidationError("LIMIT clause is required")
