import os


def get_database_url() -> str:
    """
    Returns database URL for read-only analytics access (MySQL).
    """
    return os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://analytics_read:mypassword123@localhost:3306/analytics"
    )
