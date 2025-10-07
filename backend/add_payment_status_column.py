from app.core.database import get_db
from sqlalchemy import text


def column_exists(db, table: str, column: str) -> bool:
    res = db.execute(text(f"PRAGMA table_info({table})"))
    for row in res.fetchall():
        if row[1] == column:
            return True
    return False


def add_payment_status_column():
    db = next(get_db())
    try:
        if not column_exists(db, 'orders', 'payment_status'):
            # Add column as TEXT for SQLite compatibility
            db.execute(text("ALTER TABLE orders ADD COLUMN payment_status TEXT"))
            # Set default value for existing rows
            db.execute(text("UPDATE orders SET payment_status='cod_pending' WHERE payment_status IS NULL"))
            print('SUCCESS: Added payment_status column and initialized existing rows')
        else:
            print('INFO: payment_status column already exists')

        db.commit()
    except Exception as e:
        print(f'ERROR: {e}')
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    add_payment_status_column()





