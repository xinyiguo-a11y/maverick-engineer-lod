import pandas as pd
import glob
import os
import re

# 1. Define the mapping from CSV headers to natural language predicates
predicate_mapping = {
    'Source': 'has source',
    'Source (Primary)': 'has primary source',
    'Source (Archival)': 'has archival source',
    'Source (Bibliographic)': 'has bibliographic source',
    'Identifier': 'has identifier',
    'Type': 'has type',
    'Creator': 'has creator',
    'Director': 'has director',
    'Author': 'has author',
    'Maker': 'has maker',
    'Translator': 'has translator',
    'Publisher': 'has publisher',
    'Original Publisher': 'has original publisher',
    'Place of Publication': 'has place of publication',
    'Date': 'has date',
    'Release_Date': 'has release date',
    'Publication_Date': 'has publication date',
    'Year_description': 'has year description',
    'Year_built': 'has year built',
    'Language': 'has language',
    'Format': 'has format',
    'Location': 'has location',
    'Filming_Location': 'has filming location',
    'Campus_location': 'has campus location',
    'Spatial_Coverage': 'has spatial coverage',
    'Subject': 'has subject',
    'Genres': 'has genre',
    'Historical Context': 'has historical context',
    'Production_Companies': 'has production company',
    'Studio': 'has studio',
    'Chinese_translation': 'has chinese translation',
    'Registration_status': 'has registration status',
    'Capital_NTD': 'has capital in NTD',
    'Number_of_level': 'has number of levels',
    'Number_of_room': 'has number of rooms',
    'Gross_square_foot': 'has gross square foot',
    'Departments': 'has department',
    'Origin': 'has origin',
    'Category': 'has category',
    'Material': 'has material',
    'Cataloging Date': 'has cataloging date',
    'Cataloger': 'has cataloger',
    'Festival_Edition': 'has festival edition',
    'Award': 'has award',
    'Duration': 'has duration',
    'Production_Country': 'has production country'
}

# Define columns that might contain multiple values separated by commas or semicolons
multi_value_columns = [
    'Subject', 'Genres', 'Language', 'Departments', 'Creator', 
    'Director', 'Production_Companies', 'Studio', 'Production_Country'
]

def clean_column_name(col_name):
    # Remove pandas duplicate suffixes like '.1', '.2' if headers were duplicated
    return re.sub(r'\.\d+$', '', str(col_name))

# 2. Find all CSV files in the current directory
input_files = glob.glob("*.csv")

print(f"Found {len(input_files)} files. Starting conversion process...\n")

for file in input_files:
    # Skip already generated natural language files to prevent infinite loops
    if "_natural" in file:
        continue
        
    try:
        df = pd.read_csv(file)
        
        # Check if 'Item' column exists (case-sensitive as per your latest adjustment)
        if 'Item' not in df.columns:
            print(f"Skipping file {file}: Could not find 'Item' column.")
            continue
            
        triples = []
        
        # 3. Iterate over each row
        for index, row in df.iterrows():
            subject = str(row['Item']).strip()
            if pd.isna(subject) or subject.lower() == 'nan' or subject == '':
                continue
                
            # Iterate over each column in the row
            for col in df.columns:
                cleaned_col = clean_column_name(col)
                
                # Strictly ignore the 'Description' column and the 'Item' column itself
                if cleaned_col.lower() == 'description' or cleaned_col == 'Item':
                    continue
                    
                object_val = row[col]
                
                # Skip empty cells
                if pd.isna(object_val) or str(object_val).strip() == '':
                    continue
                    
                # Determine the predicate
                predicate = predicate_mapping.get(cleaned_col)
                if not predicate:
                    # Fallback for any unknown headers
                    predicate = f"has {cleaned_col.lower().replace('_', ' ')}"
                
                val_str = str(object_val).strip()
                
                # 4. Split values for columns that contain multiple elements
                if cleaned_col in multi_value_columns:
                    if ';' in val_str:
                        parts = [p.strip() for p in val_str.split(';')]
                    else:
                        parts = [p.strip() for p in val_str.split(',')]
                        
                    for part in parts:
                        if part:
                            triples.append({'Subject': subject, 'Predicate': predicate, 'Object': part})
                else:
                    # Clean up random line breaks in standard text fields
                    clean_val = val_str.replace('\n', ' ').replace('\r', '')
                    triples.append({'Subject': subject, 'Predicate': predicate, 'Object': clean_val})
        
        # 5. Export to a new CSV file
        if triples:
            output_df = pd.DataFrame(triples)
            clean_name = file.split('.xlsx')[0].replace(' ', '_').replace('(', '').replace(')', '').replace("'", "")
            output_filename = f"{clean_name}_natural.csv"
            
            output_df.to_csv(output_filename, index=False)
            print(f"Successfully generated: {output_filename} ({len(triples)} triples)")
            
    except Exception as e:
        print(f"Error processing file {file}: {e}")

print("\nConversion complete. All SPO format files have been generated.")