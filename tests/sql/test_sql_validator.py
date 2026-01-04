from app.core.sql.validator import SQLValidator, SQLValidationError


def test_valid_sql_passes():
    sql = """
    SELECT SUM(amount)
    FROM orders
    LIMIT 10
    """
    SQLValidator().validate(sql)


def test_missing_limit_rejected():
    sql = """
    SELECT SUM(amount)
    FROM orders
    """
    try:
        SQLValidator().validate(sql)
        assert False, "Expected rejection"
    except SQLValidationError:
        pass
