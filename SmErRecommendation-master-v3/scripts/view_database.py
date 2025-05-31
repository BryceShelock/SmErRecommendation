import sqlite3
import sys
import os

def list_tables(cursor):
    """List all tables in the database"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]

def view_table(cursor, table_name):
    """View contents of a specific table"""
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    return columns, rows

def print_table(columns, rows):
    """Print table contents in a formatted way"""
    # Print header
    header = " | ".join(columns)
    print("\n" + "=" * len(header))
    print(header)
    print("=" * len(header))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(cell) for cell in row))
    print("=" * len(header))

def main():
    if len(sys.argv) < 2:
        print("Usage: python view_database.py <database_file> [table_name]")
        print("\nAvailable databases:")
        print("1. script_recommendation.db")
        print("2. murder_script.db")
        print("3. db.sqlite3")
        sys.exit(1)

    db_file = sys.argv[1]
    if not os.path.exists(db_file):
        print(f"Error: Database file '{db_file}' not found!")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # If table name is provided, show that table
        if len(sys.argv) > 2:
            table_name = sys.argv[2]
            columns, rows = view_table(cursor, table_name)
            print(f"\nContents of table '{table_name}':")
            print_table(columns, rows)
        else:
            # Show all tables
            tables = list_tables(cursor)
            print(f"\nTables in {db_file}:")
            for table in tables:
                print(f"\nTable: {table}")
                columns, rows = view_table(cursor, table)
                print_table(columns, rows)

        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 