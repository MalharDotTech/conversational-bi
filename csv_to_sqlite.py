import csv
import sqlite3
from pathlib import Path
import argparse

def csv_to_sqlite(csv_file_path, db_file_path):
    # Read the CSV file
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        columns = next(reader)  # Get column names from the first row
        data = list(reader)  # Read the rest of the data

    # Connect to SQLite database
    conn = sqlite3.connect(db_file_path)
    cur = conn.cursor()

    # Create table dynamically based on CSV columns
    create_table_query = f"CREATE TABLE IF NOT EXISTS data ({', '.join([f'{col} TEXT' for col in columns])})"
    cur.execute(create_table_query)

    # Insert data into the table
    insert_data_query = f"INSERT INTO data VALUES ({', '.join(['?' for _ in columns])})"
    cur.executemany(insert_data_query, data)

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Define argument parser
    parser = argparse.ArgumentParser(description='Convert a CSV file to a SQLite database.')
    parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
    parser.add_argument('db_file', type=str, help='Path to the output SQLite database file')

    # Parse command-line arguments
    args = parser.parse_args()

    # Ensure the database file exists before attempting conversion
    Path(args.db_file).touch()

    # Convert CSV to SQLite using command-line arguments
    csv_to_sqlite(args.csv_file, args.db_file)
