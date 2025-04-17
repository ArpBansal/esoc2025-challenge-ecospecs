import os
from scripts.table_generator_adv import AdvancedTableGenerator

def test_advanced_table_generator():
    # Initialize table generator with model path
    generator = AdvancedTableGenerator(model_path="Qwen/Qwen2.5-7B-Instruct-AWQ")
    
    # Test 1: Generate complete table from scratch
    print("\n=== Test 1: Generate complete table from scratch ===")
    prompt = "Comparing the environmental impact of different transportation methods"
    generator.create_and_save_complete_table(
        prompt=prompt,
        output_file="transportation_impact.docx",
        table_title="Environmental Impact of Transportation Methods"
    )
    
    # Test 2: Generate XKCD-inspired table
    print("\n=== Test 2: Generate XKCD-inspired table ===")
    # Based on XKCD #1497 - New Products
    prompt = "Weird new product ideas and their ridiculous features"
    row_headers = ["Self-driving car for dogs", "Wireless water", 
                  "Blockchain-powered toaster", "AI sunglasses", 
                  "Quantum dishwasher"]
    column_headers = ["Ridiculous feature", "Unexpected side effect", "Price"]
    
    table_content = generator.generate_table_content(
        prompt=prompt,
        row_headers=row_headers,
        column_headers=column_headers
    )
    
    # Print generated content
    print("\nGenerated XKCD-inspired table content:")
    for i, row in enumerate(table_content):
        print(f"{row_headers[i]}: {row}")
    
    # Format table for saving with headers
    formatted_table = [["Product"] + column_headers]
    for i, header in enumerate(row_headers):
        formatted_table.append([header] + table_content[i])
    
    # Generate intro paragraph
    intro = generator.generate_intro_paragraph(prompt, {
        "row_headers": row_headers,
        "column_headers": column_headers
    })
    
    # Save to document with intro
    generator.save_table_to_docx(
        formatted_table,
        "xkcd_products.docx",
        intro_text=intro,
        table_title="Absurd Product Ideas (XKCD-inspired)"
    )
    print("\nXKCD-inspired table saved to 'xkcd_products.docx'")

    # Test 3: Generate table from scratch with PDF output
    print("\n=== Test 3: Generate table with PDF output ===")
    prompt = "Popular programming languages and their characteristics in 2025"
    try:
        generator.create_and_save_complete_table(
            prompt=prompt,
            output_file="programming_languages_2025.pdf",
            as_pdf=True
        )
        print("Table saved as PDF successfully")
    except Exception as e:
        print(f"Error saving as PDF: {e}")
        generator.create_and_save_complete_table(
            prompt=prompt,
            output_file="programming_languages_2025.docx",
            as_pdf=False
        )