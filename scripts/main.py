import os
import docx
from typing import List, Any, Optional, Tuple, Dict
import re
import json
import torch
from table_parser import parse_tables_from_docx
from table_generator import TableGenerator
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline

class ecoSpecsDocumentGenerator:
    """Pre-prototype for ecoSPECS document generation system.
    This class demonstrates an approach to generating detailed URS and functional specifications
    from initial requirement documents."""

    def __init__(self, model_path: str):
        self.model = AutoModelForCausalLM.from_pretrained(model_path,
                                                          device_map="cuda" if torch.cuda.is_available() else "cpu",
                                                          torch_dtype=torch.float16),
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        self.pipe = pipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            task="text-generation",
            device_map="cuda" if torch.cuda.is_available() else "cpu",
            torch_dtype=torch.float16,
            max_length=98304,
                             )
    def extract_document_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Extract the structure and content from a Word document.
        
        Args:
            file_path (str): Path to the Word document
            
        Returns:
            Dict: Structure containing document sections, tables, and text
        """
        document = docx.Document(file_path)
        structure = {
            "title": document.core_properties.title or "Untitled Document",
            "sections": [],
            "tables": []
        }
        
        current_section = {"title": "", "content": "", "level": 0}
        
        # Extract sections, paragraphs, and tables
        for element in document.element.body:
            if element.tag.endswith('tbl'):
                # It's a table
                table_data = []
                tbl = docx.table._Table(element, document)
                
                for row in tbl.rows:
                    row_data = []
                    for cell in row.cells:
                        row_data.append(cell.text)
                    table_data.append(row_data)
                
                structure["tables"].append(table_data)
            elif element.tag.endswith('p'):
                # It's a paragraph
                para = docx.text.paragraph.Paragraph(element, document)
                
                # Check if it's a heading
                if para.style.name.startswith('Heading'):
                    # Save current section if it has content
                    if current_section["content"].strip():
                        structure["sections"].append(current_section)
                    
                    # Extract heading level from style name
                    level = int(para.style.name.replace('Heading ', ''))
                    
                    # Start new section
                    current_section = {
                        "title": para.text,
                        "content": "",
                        "level": level
                    }
                else:
                    # Add to current section content
                    current_section["content"] += para.text + "\n"
        
        # Add the final section
        if current_section["content"].strip():
            structure["sections"].append(current_section)
            
        return structure

    pass