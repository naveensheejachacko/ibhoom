import os
import sqlite3


def fix_db(db_path: str):
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}")
        return
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # check if column exists
        cur.execute("PRAGMA table_info(orders)")
        cols = [row[1] for row in cur.fetchall()]
        if 'payment_status' not in cols:
            cur.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT")
            cur.execute("UPDATE orders SET payment_status='cod_pending' WHERE payment_status IS NULL")
            conn.commit()
            print("SUCCESS: Added payment_status to orders in backend DB")
        else:
            print("INFO: payment_status already exists in backend DB")
    finally:
        conn.close()


if __name__ == '__main__':
    # This script expects to run from repository root
    db_path = os.path.join(os.path.dirname(__file__), 'marketplace.db')
    fix_db(db_path)





