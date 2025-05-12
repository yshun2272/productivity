"""
Picture Organization Script - Simple Version

This script reads a Markdown file (pictures.md) to rename picture files
that have simple numeric names (like 1.jpg, 2.jpg, etc.) and organize
them into folders based on the "Area" column.

Required columns in Markdown table:
- "Current File Name": The number of the file (with or without .jpg extension)
- "Suggested File Name": New filename
- "Date": Optional date to add as metadata
- "Tags": Optional tags to add as metadata  
- "Area": Folder to move the file into

Author: Claude
Date: May 6, 2025
"""

import os
import subprocess
import shutil
import logging
import re
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('picture_organization.log'),
        logging.StreamHandler()
    ]
)

def check_exiftool():
    """Check if ExifTool is installed and available."""
    try:
        subprocess.run(['exiftool', '-ver'], capture_output=True, check=True)
        logging.info("ExifTool is available")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logging.error("ERROR: ExifTool is not installed or not in PATH")
        print("ERROR: ExifTool is required but not found. Please install ExifTool.")
        return False

def sanitize_filename(filename):
    """Remove invalid characters from filenames."""
    # Replace characters that are invalid in Windows filenames
    for char in '<>:"/\\|?*':
        filename = filename.replace(char, '_')
    return filename.strip()

def create_folder(folder_path):
    """Create a folder if it doesn't exist."""
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            logging.info(f"Created folder: {folder_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to create folder {folder_path}: {str(e)}")
            return False
    return True

def parse_markdown_table(file_path):
    """Parse markdown table into list of dictionaries."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find the table in the markdown content
        table_pattern = r'\|(.+?)\|\s*\n\|[-|]+\|\s*\n((?:\|.+\|\s*\n)+)'
        table_match = re.search(table_pattern, content, re.DOTALL)
        
        if not table_match:
            logging.error("No markdown table found in the file")
            return None
        
        # Extract headers and rows
        headers_str = table_match.group(1)
        rows_str = table_match.group(2)
        
        # Process headers and normalize them (make case-insensitive)
        raw_headers = [h.strip() for h in headers_str.split('|') if h.strip()]
        headers = []
        header_map = {}  # Maps normalized headers to original headers
        
        for h in raw_headers:
            # Normalize header (lowercase, no spaces)
            norm_h = h.lower().replace(' ', '')
            headers.append(norm_h)
            header_map[norm_h] = h
        
        # Check required headers - using normalized format
        required_headers = ["currentfilename", "suggestedfilename", "area"]
        missing_headers = []
        
        for req_h in required_headers:
            if req_h not in headers:
                # Try to find close matches for better error messages
                possible_matches = [h for h in headers if req_h in h]
                if possible_matches:
                    logging.warning(f"Required header '{req_h}' not found exactly, but found similar: {possible_matches}")
                else:
                    missing_headers.append(req_h)
        
        if missing_headers:
            logging.error(f"Required headers not found: {missing_headers}")
            logging.error(f"Available headers: {headers}")
            return None
        
        # Get indices of required headers
        current_file_idx = headers.index("currentfilename")
        suggested_file_idx = headers.index("suggestedfilename")
        area_idx = headers.index("area")
        
        # Try to find date and tags indices (optional)
        date_idx = headers.index("date") if "date" in headers else -1
        tags_idx = headers.index("tags") if "tags" in headers else -1
        
        # Process rows
        rows = []
        for row in rows_str.strip().split('\n'):
            cells = [cell.strip() for cell in row.split('|') if cell]
            if len(cells) >= max(current_file_idx, suggested_file_idx, area_idx) + 1:
                row_dict = {
                    "Current File Name": cells[current_file_idx],
                    "Suggested File Name": cells[suggested_file_idx],
                    "Area": cells[area_idx]
                }
                
                # Add optional fields if they exist
                if date_idx >= 0 and date_idx < len(cells):
                    row_dict["Date"] = cells[date_idx]
                if tags_idx >= 0 and tags_idx < len(cells):
                    row_dict["Tags"] = cells[tags_idx]
                    
                rows.append(row_dict)
            else:
                logging.warning(f"Skipping row with insufficient cells: {row}")
        
        return rows
    
    except Exception as e:
        logging.error(f"Error parsing markdown file: {str(e)}")
        return None

def organize_pictures():
    """Main function to organize pictures based on Markdown data."""
    print("Starting picture organization process...")
    
    # Check if ExifTool is available
    if not check_exiftool():
        return False
    
    # Get current directory (should be Pictures folder)
    pictures_dir = os.getcwd()
    markdown_file = os.path.join(pictures_dir, "pictures.md")
    
    # Check if Markdown file exists
    if not os.path.isfile(markdown_file):
        logging.error(f"Markdown file not found: {markdown_file}")
        print(f"ERROR: Markdown file not found: {markdown_file}")
        return False
    
    try:
        # Read Markdown file
        print("Reading Markdown file...")
        file_data = parse_markdown_table(markdown_file)
        
        if not file_data:
            logging.error("Failed to parse markdown table")
            print("ERROR: Failed to parse markdown table. Make sure it has the correct format.")
            return False
        
        # Process each row in the markdown table
        success_count = 0
        error_count = 0
        error_files = []  # Track files with errors
        
        total_files = len(file_data)
        print(f"Found {total_files} files to process")
        
        for index, row in enumerate(file_data):
            try:
                # Get values from markdown
                current_file = str(row.get("Current File Name", "")).strip()
                suggested_name = str(row.get("Suggested File Name", "")).strip()
                area = str(row.get("Area", "")).strip()
                
                # Skip rows with empty critical values
                if not current_file or not suggested_name or not area:
                    logging.warning(f"Skipping row {index+2} due to missing critical values")
                    error_count += 1
                    continue
                
                # Clean up filenames
                suggested_name = sanitize_filename(suggested_name)
                area = sanitize_filename(area)
                
                # Handle numeric file names with potential leading zeros (01.jpg, 1.jpg, etc.)
                # First strip any extension
                base_file = current_file
                if '.' in base_file:
                    base_file = base_file.split('.')[0]
                
                # Remove leading zeros for processing
                if base_file.isdigit():
                    base_file = str(int(base_file))  # Convert "01" to "1", etc.
                elif base_file.startswith('0') and base_file[1:].isdigit():
                    base_file = str(int(base_file))
                
                # Ensure file has .jpg extension (for pictures)
                if not current_file.lower().endswith('.jpg'):
                    current_file = base_file + ".jpg"
                else:
                    # Keep the extension but normalize the base part
                    current_file = base_file + ".jpg"
                
                # Ensure suggested name has the extension
                if not suggested_name.lower().endswith('.jpg'):
                    suggested_name += ".jpg"
                
                # Construct paths
                current_path = os.path.join(pictures_dir, current_file)
                area_dir = os.path.join(pictures_dir, area)
                new_path = os.path.join(area_dir, suggested_name)
                
                # Print progress
                print(f"Processing file {index+1}/{total_files}: {current_file} -> {suggested_name}")
                
                # Check if source file exists
                if not os.path.isfile(current_path):
                    logging.error(f"Source file not found: {current_path}")
                    print(f"ERROR: Source file not found: {current_path}")
                    error_count += 1
                    error_files.append(f"{current_file} - File not found")
                    continue
                
                # Create area folder if needed
                if not create_folder(area_dir):
                    error_count += 1
                    error_files.append(f"{current_file} - Failed to create folder: {area}")
                    continue
                
                # Check if destination file already exists
                if os.path.exists(new_path):
                    # Add timestamp to make filename unique
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    name_part, ext_part = os.path.splitext(suggested_name)
                    suggested_name = f"{name_part}_{timestamp}{ext_part}"
                    new_path = os.path.join(area_dir, suggested_name)
                    logging.warning(f"Destination file already exists, using unique name: {suggested_name}")
                
                # Apply metadata with ExifTool if available
                metadata_commands = []
                
                # Add date metadata if available
                if "Date" in row and row["Date"].strip():
                    date_str = row["Date"].strip()
                    metadata_commands.append(f"-DateTimeOriginal='{date_str}'")
                
                # Add tags metadata if available
                if "Tags" in row and row["Tags"].strip():
                    tags = row["Tags"].strip()
                    # Convert semicolon-separated tags to comma-separated for ExifTool
                    # ExifTool expects comma-separated keywords
                    if ';' in tags:
                        tags = tags.replace(';', ',')
                    metadata_commands.append(f"-Keywords='{tags}'")
                
                if metadata_commands:
                    # Create ExifTool command
                    exiftool_cmd = ["exiftool"]
                    for cmd in metadata_commands:
                        exiftool_cmd.append(cmd)
                    exiftool_cmd.append(current_path)
                    
                    # Apply metadata
                    try:
                        subprocess.run(exiftool_cmd, capture_output=True, check=True)
                        logging.info(f"Applied metadata to: {current_file}")
                        
                        # ExifTool creates a backup file with _original suffix, remove it
                        backup_file = current_path + "_original"
                        if os.path.exists(backup_file):
                            os.remove(backup_file)
                    except subprocess.SubprocessError as e:
                        logging.error(f"ExifTool error: {str(e)}")
                        print(f"WARNING: Metadata application failed for {current_file}")
                        # We don't count this as a full error, just a warning
                
                # Move and rename the file
                try:
                    shutil.move(current_path, new_path)
                    logging.info(f"Renamed and moved: {current_file} -> {new_path}")
                    print(f"Successfully processed: {current_file} -> {area}/{suggested_name}")
                    success_count += 1
                except Exception as e:
                    logging.error(f"Failed to move file: {str(e)}")
                    print(f"ERROR: Failed to move file: {str(e)}")
                    error_count += 1
                    error_files.append(f"{current_file} - Failed to move file: {str(e)}")
                
            except Exception as e:
                logging.error(f"Error processing row {index+2}: {str(e)}")
                print(f"ERROR processing file: {str(e)}")
                error_count += 1
                error_files.append(f"Row {index+2} - {str(e)}")
        
        # Print summary
        print(f"\nPicture organization complete!")
        print(f"Successfully processed: {success_count} files")
        print(f"Errors: {error_count} files")
        
        # Print error details if any
        if error_count > 0:
            print("\nFiles with errors:")
            for err in error_files:
                print(f"- {err}")
            
            # Also write errors to a file for reference
            with open('picture_errors.txt', 'w') as f:
                f.write(f"Picture organization errors - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for err in error_files:
                    f.write(f"- {err}\n")
                    
            print(f"\nDetailed error list saved to 'picture_errors.txt'")
            
        logging.info(f"Picture organization complete. Success: {success_count}, Errors: {error_count}")
        
        return True
        
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        print(f"ERROR: An unexpected error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    organize_pictures()
    input("\nPress Enter to exit...")
