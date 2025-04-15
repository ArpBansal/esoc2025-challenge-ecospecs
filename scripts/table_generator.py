import os
import docx
from typing import List, Any, Optional, Tuple, Dict
from transformers import pipeline
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from scripts.utils import convert_docx_to_pdf
import json
import ast

class TableGenerator:
    def __init__(self, model_path:str):
        self.model = AutoModelForCausalLM.from_pretrained(model_path,
                                                          device_map="cuda" if torch.cuda.is_available() else "cpu",
                                                          torch_dtype=torch.float16)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        self.pipe = pipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            task="text-generation",
            device_map="cuda" if torch.cuda.is_available() else "cpu",
            torch_dtype=torch.float16,
            # max_length=98304,
                             )
        
        self.SYSTEM_PROMPT = "You are a helpful assistant that generates tables based on the provided prompt. " \
            "You will receive a prompt and you need to generate a table in text format. " \
            "The table should be well-structured and easy to read. " \
            "Please ensure that the table is formatted correctly and includes all necessary information. " \
            "Adhere to the following guidelines: " \
            "Respond with only the table content in a JSON array format, no explanation or markdown."


    def generate_table_content(self, prompt: str, max_new_tokens:int = 98304,
                            row_headers: Optional[List[str]] = None,
                            column_headers: Optional[List[str]] = None,
                            num_rows: int = 5,
                            num_cols: int = 3) -> str:
        
        rows = len(row_headers) if row_headers else num_rows
        cols = len(column_headers) if column_headers else num_cols
        system_prompt = (
            "You are a helpful assistant that generates content for tables based on headers and description. "
            "Respond with only the table content in a JSON array format, no explanation or markdown."
        )
        messages = [
            # {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate content for a table with the following description: {prompt}\n\n" \
             "Adhere to these points strictly:\n" \
                "1. Generate a table with appropriate headers and content.\n" \
                "2. Only generate content for given headers.\n" \
                "3. If no headers are provided, generate a table with appropriate headers.\n" \
                "4. If headers are given, generate content for those headers only.\n"}
        ]

        message = f"Generate content for a table with the following description: {prompt}\n\n"        

        if row_headers and column_headers:
            message += f"Row headers: {row_headers}\nColumn headers: {column_headers}\n"
            message += "Generate a table with these exact row and column headers."
        elif row_headers:
            message += f"Row headers: {row_headers}\n"
            message += f"Generate {cols} columns of appropriate content."
        elif column_headers:
            message += f"Column headers: {column_headers}\n"
            message += f"Generate {rows} rows of appropriate content."
        else:
            message += f"Generate a {rows}x{cols} table with appropriate headers and content."
        
        message += "\nReturn the result as a 2D array in JSON format." \
            "\nMake sure we are only creating rows for given column header nothing outside of it.\n" \

        response = self.pipe(messages, max_new_tokens=max_new_tokens)

        content = response[0]['generated_text'][-1]['content']

        # mannual cleaning cause other one didn't worked
        cleaned_content = content.strip()
        if cleaned_content.startswith('```') and cleaned_content.endswith('```'):
            cleaned_content = cleaned_content[3:-3].strip()
        elif cleaned_content.startswith('`') and cleaned_content.endswith('`'):
            cleaned_content = cleaned_content[1:-1].strip()

        # Didn't worked
        # table_data = ast.literal_eval(content.strip('`').strip())
        # table_data = json.loads(table_data)
        try:
            try:
                table_data = json.loads(cleaned_content)
                return table_data
            except json.JSONDecodeError:
                pass

            try:
                table_data = ast.literal_eval(cleaned_content)
                # If it's a string (might be a JSON string), try parsing it again
                if isinstance(table_data, str):
                    table_data = json.loads(table_data)
                return table_data
            except (ValueError, SyntaxError):
                pass

            if cleaned_content.startswith('[') and cleaned_content.endswith(']'):
                # Replace newlines with spaces in a way that preserves JSON structure
                cleaned_json = cleaned_content.replace('\n', ' ')
                try:
                    table_data = json.loads(cleaned_json)
                    return table_data
                except json.JSONDecodeError:
                    pass

            print("JSON parsing attempts fail. Attempting mannual extraction.")

            if cleaned_content.startswith('[') and cleaned_content.endswith(']'):
                # Split into rows by detecting array patterns
                rows = []
                current_row = []
                in_quotes = False
                row_buffer = ""
                
                for char in cleaned_content[1:-1]:  # Skip the outer brackets
                    if char == '"':
                        in_quotes = not in_quotes
                        row_buffer += char
                    elif char == ',' and not in_quotes:
                        if row_buffer.strip():
                            current_row.append(row_buffer.strip())
                        row_buffer = ""
                    elif char == '[' and not in_quotes and not row_buffer.strip():
                        # New row starting
                        if current_row:
                            rows.append(current_row)
                        current_row = []
                    elif char == ']' and not in_quotes:
                        # Row ending
                        if row_buffer.strip():
                            current_row.append(row_buffer.strip())
                            row_buffer = ""
                    else:
                        row_buffer += char
                        
                if current_row:
                    rows.append(current_row)
                    
                if rows:
                    return rows
            
            # If all else fails, construct a basic table from the text
            lines = cleaned_content.split('\n')
            rows = []
            for line in lines:
                if line.strip():
                    rows.append([line.strip()])
            
            return rows if rows else [["Failed to parse table data"]]
        
        
        except Exception as e:
            print("Failed to parse JSON response, returning text")
            return [["Error parsing table data: " + str(e)]]
        
    def generate_table(self, prompt: str,
                       row_headers:Optional[List[str]]=None,
                       column_headers:Optional[List[str]]=None) -> List[List[str]]:
        """
        Generate a complete table including headers.
        
        Args:
            prompt (str): Description of the table content
            row_headers (List[str], optional): Row headers
            column_headers (List[str], optional): Column headers
            
        Returns:
            List[List[str]]: Complete table with headers
        """

        if not row_headers and not column_headers:
            # Ask the model to generate appropriate headers
            system_prompt = "Generate appropriate row and column headers for the described table."
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate row and column headers for a table about: {prompt}"}
            ]
            
            output = self.pipe(messages, max_new_tokens=int(98304))
            content = output[0]['generated_text'][-1]['content']

            # In production, we need to add better parsing to extract headers from the response
            try:
                import json
                suggested_headers = json.loads(content)
                row_headers = suggested_headers.get("row_headers", [])
                column_headers = suggested_headers.get("column_headers", [])
            except:
                # Fallback
                row_headers = ["Row 1", "Row 2", "Row 3"]
                column_headers = ["Column 1", "Column 2", "Column 3"]
                
        # Then generate the table content
        table_data = self.generate_table_content(prompt, 
                                                row_headers=row_headers, 
                                                column_headers=column_headers)
        
        # Combine headers and content to form complete table
        full_table = []
        
        # Add column headers as first row if available
        if column_headers:
            if row_headers:
                # If we have both headers, add empty cell at top-left
                full_table.append([""] + column_headers)
            else:
                full_table.append(column_headers)
                
        # Add rows with row headers if available
        if row_headers:
            for i, row_data in enumerate(table_data):
                if i < len(row_headers):
                    full_table.append([row_headers[i]] + row_data)
                else:
                    full_table.append([""] + row_data)
        else:
            full_table.extend(table_data)
            
        return full_table
    
    def save_table_to_docx(self, table_data: List[List[str]], output_file: str,
                           intro_text: Optional[str] = None) -> None:
        """
        Save a table to a Word document with optional introduction paragraph.
        
        Args:
            table_data (List[List[str]]): The table data as a list of lists.
            output_file (str): The path to the output Word document.
            intro_text (Optional[str]): Optional introduction paragraph.
        """
        doc = docx.Document()

        if intro_text:
            doc.add_paragraph(intro_text)
            doc.add_paragraph()
        
        rows = len(table_data)
        cols = len(table_data[0]) if rows > 0 else 0

        if rows > 0 and cols > 0:
            table = doc.add_table(rows=rows, cols=cols)
            table.style = 'Table Grid'

            for i, row in enumerate(table_data):
                for j, cell in enumerate(row):
                    if j < cols: # Ensure we don't exceed column count
                        table.cell(i, j).text = str(cell) if cell is not None else ""

        doc.save(output_file)
        print(f"Table saved to {output_file}")

    def save_table_to_file(self, table_data: List[List[str]], output_file: str,
                     intro_text: Optional[str] = None, as_pdf: bool = False) -> None:
        """
        Save a table to a Word document or PDF file with optional introduction paragraph.
        
        Args:
            table_data (List[List[str]]): The table data as a list of lists.
            output_file (str): The path to the output file.
            intro_text (Optional[str]): Optional introduction paragraph.
            as_pdf (bool): If True, save as PDF; if False, save as DOCX.
        """
        doc = docx.Document()

        if intro_text:
            doc.add_paragraph(intro_text)
            doc.add_paragraph()
        
        rows = len(table_data)
        cols = len(table_data[0]) if rows > 0 else 0

        if rows > 0 and cols > 0:
            table = doc.add_table(rows=rows, cols=cols)
            table.style = 'Table Grid'

            for i, row in enumerate(table_data):
                for j, cell in enumerate(row):
                    if j < cols:
                        table.cell(i, j).text = str(cell) if cell is not None else ""

        # Save as DOCX first
        temp_docx = output_file
        if as_pdf:
            # If PDF requested, save to temp DOCX file first
            base_name = os.path.splitext(output_file)[0]
            temp_docx = f"{base_name}_temp.docx"

        doc.save(temp_docx)
        
        if as_pdf:
            try:
                convert_docx_to_pdf(temp_docx, output_file)
                os.remove(temp_docx)
                print(f"Table saved to {output_file}")
            except ImportError:
                print("Warning: docx2pdf package not installed. Saving as DOCX instead.")
                print(f"Table saved to {temp_docx}")
        else:
            print(f"Table saved to {output_file}")