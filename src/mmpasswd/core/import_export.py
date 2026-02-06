import csv

class ImportExportManager:
    # EXPORT REMOVED FOR SECURITY
    
    @staticmethod
    def import_csv(kdbx_manager, filepath):
        count = 0
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Basic validation
                if 'password' not in row:
                    continue
                    
                kdbx_manager.add_entry({
                    'username': row.get('username', ''),
                    'password': row.get('password', ''),
                    'website': row.get('website', ''),
                    'notes': row.get('notes', ''),
                    'is_favorite': int(row.get('is_favorite', 0))
                })
                count += 1
        return count
