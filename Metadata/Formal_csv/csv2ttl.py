import csv
import json
import glob
import os
import re
from collections import defaultdict

# ==============================================================================
# SCRIPT: generate_ttl.py
# PURPOSE: Aggregates all *_formal.csv files into a single Turtle (.ttl) dataset.
# FEATURES: 
#   1. Implements grouped syntax (Subject -> Predicate -> Object list).
#   2. Automatic data typing (xsd:date, xsd:gYear, xsd:integer).
#   3. Automatic language tagging (@zh, @en).
#   4. Robust parsing for complex strings (e.g., SKOS annotations with commas).
# ==============================================================================

def load_namespaces(json_file):
    """
    Load prefixes and URIs from the namespace configuration file.
    Ensures 'xsd' is present for standard data typing.
    """
    namespaces = {"xsd": "http://www.w3.org/2001/XMLSchema#"}
    
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for prefix, uri in data.items():
                # Clean URIs by removing accidental angle brackets
                namespaces[prefix] = uri.strip("<>")
    else:
        print(f"WARNING: {json_file} not found. Utilizing default namespaces.")
        
    return namespaces

def format_object(obj_str):
    """
    Processes the Object column to apply proper RDF formatting rules.
    Identifies URIs, QNames, and Literals (Dates, Integers, and Languages).
    """
    obj_str = obj_str.strip()
    
    # Rule 1: Handle URIs wrapped in angle brackets
    if obj_str.startswith('<') and obj_str.endswith('>'):
        return obj_str
        
    # Rule 2: Handle QNames (e.g., me:entity, schema:name)
    # Ensure it is not a literal string starting with quotes
    if ':' in obj_str and not (obj_str.startswith('"') or obj_str.startswith("'")):
        return obj_str
        
    # Rule 3: Process Literals (initially wrapped in triple or double quotes)
    # Strip all surrounding quote markers to extract the raw value
    val = obj_str.strip('"\'').strip()
    
    # A. Date Pattern (YYYY-MM-DD) -> xsd:date
    if re.match(r'^\d{4}-\d{2}-\d{2}$', val):
        return f'"{val}"^^xsd:date'
        
    # B. Year Pattern (YYYY) -> xsd:gYear
    if re.match(r'^\d{4}$', val):
        return f'"{val}"^^xsd:gYear'
        
    # C. Integer Pattern -> xsd:integer
    if re.match(r'^\d+$', val):
        return f'"{val}"^^xsd:integer'
        
    # D. Language Tagging: Chinese characters detected -> @zh
    if re.search(r'[\u4e00-\u9FFF]', val):
        return f'"{val}"@zh'
        
    # E. Language Tagging: Latin characters detected -> @en
    if re.search(r'[a-zA-Z]', val):
        return f'"{val}"@en'
        
    # Fallback: Default quoted literal
    return f'"{val}"'

def main():
    output_file = "Edward_Yang_Final_Dataset.ttl"
    config_file = "namespace.json"
    
    print("--------------------------------------------------")
    print("INITIALIZING RDF CONVERSION PROCESS...")
    print("--------------------------------------------------")
    
    # 1. Load Namespace Configuration
    prefixes = load_namespaces(config_file)
    
    # 2. Discover all relevant CSV files
    csv_files = glob.glob('*_formal.csv')
    if not csv_files:
        print("ERROR: No files matching '*_formal.csv' were found.")
        return
        
    print(f"Discovered {len(csv_files)} formal CSV files. Proceeding with aggregation.")
    
    # 3. Aggregate data into memory to support grouped syntax
    # Structure: graph[subject][predicate] = set(objects)
    graph = defaultdict(lambda: defaultdict(set))
    triple_count = 0
    
    for file_path in csv_files:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header row
            
            for row in reader:
                # Basic validation: row must contain at least Subject, Predicate, and Object
                if len(row) >= 3:
                    subj = row[0].strip()
                    pred = row[1].strip()
                    
                    # Join row elements from index 2 onwards to handle commas inside quoted strings
                    # This is critical for skos:definition and skos:scopeNote
                    raw_obj = ",".join(row[2:]).strip()
                    
                    formatted_obj = format_object(raw_obj)
                    graph[subj][pred].add(formatted_obj)
                    triple_count += 1
                    
        print(f"Loaded: {file_path}")

    # 4. Generate the Turtle output
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write Prefix Declarations
        f.write("### NAMESPACE DECLARATIONS ###\n")
        for pref, uri in sorted(prefixes.items()):
            f.write(f"@prefix {pref}: <{uri}> .\n")
        f.write("\n")
        
        f.write("### KNOWLEDGE GRAPH DATA ###\n\n")
        
        # Write Triple Groups
        for subj in sorted(graph.keys()):
            f.write(f"{subj}")
            
            predicates = sorted(graph[subj].keys())
            for i, pred in enumerate(predicates):
                # Sort objects for deterministic output
                objs = sorted(list(graph[subj][pred]))
                objs_joined = " , ".join(objs)
                
                if i == 0:
                    f.write(f" {pred} {objs_joined}")
                else:
                    f.write(f" ;\n    {pred} {objs_joined}")
            
            # End the subject block with a period
            f.write(" .\n\n")
            
    print("--------------------------------------------------")
    print(f"CONVERSION COMPLETE: Processed {triple_count} triples.")
    print(f"OUTPUT SAVED AS: {output_file}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()