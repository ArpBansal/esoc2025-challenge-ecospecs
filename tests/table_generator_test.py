import os
from scripts.table_generator import TableGenerator

def test_table_generator():
    # Initialize table generator with model path
    generator = TableGenerator(model_path="Qwen/Qwen2.5-7B-Instruct-AWQ")

    # Test 1: Planet data table
    print("Generating planet data table...")
    row_headers = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn"]
    column_headers = ["Distance from Sun (AU)", "Mass (Earth = 1)", "Diameter (km)", 
                     "Escape Velocity (km/s)", "Day length (Earth hours)"]
    
    table = generator.generate_table_content(
        "Create a table of accurate physical properties for planets in our solar system",
        row_headers=row_headers,
        column_headers=column_headers
    )
    
    print("\nGenerated Planet Table:")
    for row in table:
        print(row)
    
    full_table = [["Planet"] + column_headers]
    
    for i, row in enumerate(row_headers):
        if i < len(table):
            full_table.append([row] + table[i])
    
    generator.save_table_to_docx(
        full_table,
        "planet_data_mannual_headers.docx",
        "Solar System Planets - Physical Properties"
    )
    print("Planet data table saved to 'planet_data.docx'.")

    # Test 2: Programming languages comparison
    print("\nGenerating programming languages table...")
    row_headers = ["Python", "JavaScript", "Java", "C++", "Go", "Rust"]
    column_headers = ["Popularity", "Main Use Cases", "Learning Curve"]
    
    table = generator.generate_table_content(
        "Create a table comparing programming languages",
        row_headers=row_headers,
        column_headers=column_headers
    )
    
    print("\nGenerated Programming Languages Table:")
    for row in table:
        print(row)
    
    # Format the table with headers for saving
    full_table = [["Language"] + column_headers]
    
    for i, row in enumerate(row_headers):
        if i < len(table):
            full_table.append([row] + table[i])
    
    generator.save_table_to_docx(
        full_table,
        "programming_languages_mannual_headers.docx",
        "Comparison of Popular Programming Languages"
    )
    print("Programming languages table saved to 'programming_languages.docx'.")