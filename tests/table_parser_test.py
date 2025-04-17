import docx
import numpy as np
from typing import List, Any
from scripts.table_parser import parse_tables_from_docx, get_table_dimensions

def test_table_parser():
    "tests the table parser functionality"
    
    test_file = "data/A_2.docx"
    try:
        tables = parse_tables_from_docx(test_file)
        print(f"Number of tables parsed: {len(tables)}")

        dimensions = get_table_dimensions(tables)

        print("Dimensions of each table:")
        for i, (rows, cols) in enumerate(dimensions):
            print(f"Table {i}: {rows} rows, {cols} columns")
        
        if tables:
            print("\nExample (first table):")
            for row in tables[0]:
                print(row)

        assert dimensions[0] == (2, 3)
    except Exception as e:
        print(f"Error testing parser: {e}")
        assert False

