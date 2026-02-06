import os
import shutil
from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError
from datetime import datetime
import uuid

class KeePassDatabaseManager:
    def __init__(self, db_path=None, password=None, keyfile=None):
        import sys
        if db_path is None:
            if getattr(sys, 'frozen', False):
                # If running as EXE, keep DB next to the executable
                base_dir = os.path.dirname(sys.executable)
            else:
                # Default to ../../vault.kdbx relative to this file (src/mmpasswd/core/keepass_db.py)
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            self.db_path = os.path.join(base_dir, "vault.kdbx")
        else:
            self.db_path = db_path

        self._kp = None
        self._password = password
        
        # Initialize or Load
        if password:
            self.load_database(password)

    def is_setup(self):
        return os.path.exists(self.db_path)

    def create_database(self, password):
        """Creates a new KDBX database."""
        from pykeepass import create_database
        self._kp = create_database(self.db_path, password=password)
        self._kp.save()
        self._password = password

    def load_database(self, password):
        """Loads an existing KDBX database."""
        try:
            self._kp = PyKeePass(self.db_path, password=password)
            self._password = password
            return True
        except CredentialsError:
            return False
        except FileNotFoundError:
            return False

    def save(self):
        if self._kp:
            self._kp.save()

    # --- Configuration Persistence ---
    def set_config(self, key, value):
        if not self._kp: return
        # Store in a special entry named 'MMPasswd_Config' in 'Meta' group
        meta_group = self._kp.find_groups(name="Meta", first=True)
        if not meta_group:
            meta_group = self._kp.add_group(self._kp.root_group, "Meta")
            
        config_entry = self._kp.find_entries(title="MMPasswd_Config", group=meta_group, first=True)
        if not config_entry:
            config_entry = self._kp.add_entry(meta_group, "MMPasswd_Config", "", "")
            
        # We use custom properties (string fields)
        # Fix: Use set_custom_property method
        config_entry.set_custom_property(key, str(value))
        
        self.save()
        
    def get_config(self, key, default=None):
        if not self._kp: return default
        meta_group = self._kp.find_groups(name="Meta", first=True)
        if not meta_group: return default
        
        config_entry = self._kp.find_entries(title="MMPasswd_Config", group=meta_group, first=True)
        if not config_entry: return default
        
        val = config_entry.get_custom_property(key)
        return val if val is not None else default

    # --- Entry Management ---
    
    def _entry_to_dict(self, entry):
        if not entry: return None
        return {
            "id": str(entry.uuid),
            "username": entry.username or "",
            "password": entry.password or "", # KeePass handles encryption
            "website": entry.url or "",
            "notes": entry.notes or "",
            "is_favorite": 1 if entry.tags and 'favorite' in entry.tags else 0,
            "created_date": getattr(entry, 'ctime', datetime.now()).isoformat()
        }

    def add_entry(self, data: dict):
        group = self._kp.root_group
        # Use website or username as title
        title = data.get('website', '') or data.get('username', 'No Title')
        entry = self._kp.add_entry(
            destination_group=group,
            title=title,
            username=data.get('username', ''),
            password=data.get('password', '')
        )
        entry.url = data.get('website', '')
        entry.notes = data.get('notes', '')
        
        if data.get('is_favorite') == 1:
            entry.tags = ['favorite']
            
        self.save()
        return self._entry_to_dict(entry)

    def get_entries(self, filter_type='all', query=None):
        if not self._kp: return []
        
        entries = []
        
        # Helper to check tags
        def has_tag(e, tag): return e.tags and tag in e.tags
        
        all_entries = self._kp.entries
        
        for e in all_entries:
            # Check Recycle Bin by Name
            parent = e.group
            is_deleted = False
            while parent:
                if parent.name == "Recycle Bin":
                    is_deleted = True
                    break
                parent = parent.parentgroup
            
            if e.title == "MMPasswd_Config":
                continue
                
            if filter_type != 'deleted' and is_deleted:
                continue
            elif filter_type == 'deleted' and not is_deleted:
                continue
            if filter_type == 'favorites':
                if not has_tag(e, 'favorite'): continue
                
            elif filter_type == 'all':
                pass # Show everything except deleted
            
            # Query Filter
            if query:
                q = query.lower()
                if q not in (e.url or "").lower() and q not in (e.username or "").lower():
                    continue
                    
            entries.append(self._entry_to_dict(e))
            
        # Sort by website/username
        entries.sort(key=lambda x: (x['website'] or x['username']).lower())
        return entries

    def get_entry(self, entry_id):
        if not self._kp: return None
        try:
            uuid_obj = uuid.UUID(entry_id)
            entry = self._kp.find_entries(uuid=uuid_obj, first=True)
            return self._entry_to_dict(entry)
        except:
            return None

    def update_entry(self, entry_id, data: dict):
        if not self._kp: return
        uuid_obj = uuid.UUID(entry_id)
        entry = self._kp.find_entries(uuid=uuid_obj, first=True)
        if not entry: return

        if 'website' in data: 
            entry.url = data['website']
            # Re-sync title to website
            entry.title = data['website'] or data.get('username', entry.title)
        
        if 'username' in data: 
            entry.username = data['username']
            if not entry.url: # If no URL, use username as title
                entry.title = data['username']
        if 'password' in data: entry.password = data['password']
        if 'website' in data: entry.url = data['website']
        if 'notes' in data: entry.notes = data['notes']
        
        # Tags
        current_tags = list(entry.tags) if entry.tags else []
        
        if 'is_favorite' in data:
            if data['is_favorite'] == 1 and 'favorite' not in current_tags:
                current_tags.append('favorite')
            elif data['is_favorite'] == 0 and 'favorite' in current_tags:
                current_tags.remove('favorite')
                
        entry.tags = current_tags
        self.save()

    def delete_entry(self, entry_id, soft=True):
        if not self._kp: return
        uuid_obj = uuid.UUID(entry_id)
        entry = self._kp.find_entries(uuid=uuid_obj, first=True)
        if not entry: return
        
        if soft:
            # Move to Recycle Bin
            rb_group = self._kp.find_groups(name="Recycle Bin", first=True)
            if not rb_group:
                 rb_group = self._kp.add_group(self._kp.root_group, "Recycle Bin")
            self._kp.move_entry(entry, rb_group)
        else:
            self._kp.delete_entry(entry)
            
        self.save()

    def restore_entry(self, entry_id):
        if not self._kp: return
        uuid_obj = uuid.UUID(entry_id)
        entry = self._kp.find_entries(uuid=uuid_obj, first=True)
        if not entry: return
        
        # Move back to Root Group
        # Ideally, we should restore to original group if we tracked it, but Root is safe default.
        self._kp.move_entry(entry, self._kp.root_group)
        self.save()

    def get_search_results(self, filter_type, query):
        return self.get_entries(filter_type, query)
