import os
import sqlite3


def clear_products_and_categories(db_path: str):
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # Speed up deletes in SQLite
        cur.execute("PRAGMA foreign_keys = ON;")

        # Delete product-related rows in dependency order
        # product_variant_attributes -> product_variants -> product_images -> order_items -> products
        tables_in_order = [
            "product_variant_attributes",
            "product_variants",
            "product_images",
            "order_items",
        ]
        for t in tables_in_order:
            try:
                cur.execute(f"DELETE FROM {t}")
                print(f"Cleared {t}")
            except sqlite3.OperationalError as e:
                print(f"Skip {t}: {e}")

        cur.execute("DELETE FROM products")
        print("Cleared products")

        # Delete category relation table first, then categories (handles children after parents if FK allows)
        try:
            cur.execute("DELETE FROM category_attributes")
            print("Cleared category_attributes")
        except sqlite3.OperationalError as e:
            print(f"Skip category_attributes: {e}")

        # Remove attributes as well if they are only used for categories/variants
        try:
            cur.execute("DELETE FROM attribute_values")
            print("Cleared attribute_values")
        except sqlite3.OperationalError as e:
            print(f"Skip attribute_values: {e}")
        try:
            cur.execute("DELETE FROM attributes")
            print("Cleared attributes")
        except sqlite3.OperationalError as e:
            print(f"Skip attributes: {e}")

        # Finally, delete categories (children and roots)
        cur.execute("DELETE FROM categories")
        print("Cleared categories")

        conn.commit()
        print("DONE: All products and categories cleared.")
    finally:
        conn.close()


if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), 'marketplace.db')
    clear_products_and_categories(db_path)


