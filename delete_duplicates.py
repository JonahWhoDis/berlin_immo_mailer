import os
import logging

#!/usr/bin/env python3

# Configure logging
logging.basicConfig(
    filename='deletion_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def find_duplicates(root_folder):
    files_by_name = {}
    # Walk over the whole folder recursively
    for dirpath, _, filenames in os.walk(root_folder):
        for fname in filenames:
            path = os.path.join(dirpath, fname)
            files_by_name.setdefault(fname, []).append(path)
    return files_by_name

def delete_duplicates(duplicates):
    deletion_counts = {}
    for fname, paths in duplicates.items():
        # If there's more than one file with the same name:
        if len(paths) > 1:
            # Keep the first occurrence, delete the rest.
            to_delete = paths[1:]
            for file_path in to_delete:
                try:
                    os.remove(file_path)
                    deletion_counts[fname] = deletion_counts.get(fname, 0) + 1
                    logging.info(f"Deleted duplicate file: {file_path}")
                except Exception as e:
                    logging.error(f"Error deleting file {file_path}: {e}")
    return deletion_counts

def main():
    output_folder = '/output'
    duplicates = find_duplicates(output_folder)
    deletion_counts = delete_duplicates(duplicates)
    
    if deletion_counts:
        print("Duplicates deleted:")
        for fname, count in deletion_counts.items():
            print(f"{fname}: {count} duplicate(s) removed")
    else:
        print("No duplicates found to delete.")

if __name__ == '__main__':
    main()