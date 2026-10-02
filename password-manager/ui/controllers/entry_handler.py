from tkinter import messagebox
import crypto
import database
from ui.dialogs.edit_dialog import EditEntryDialog

class EntryHandler:
    def __init__(self, app):
        self.app = app

    def generate_and_set_password(self):
        """Generiert ein sicheres Zufallspasswort und trägt es in das Eingabefeld ein."""
        v = self.app.current_view
        if not hasattr(v, 'entry_pass'):
            return

        new_pw = crypto.generate_secure_password(length=16)
        
        v.entry_pass.delete(0, "end")
        v.entry_pass.insert(0, new_pw)
        
        self.app.clipboard_mgr.set_clipboard(new_pw, "GENERATED_PASSWORD")

    def load_entries(self):
        v = self.app.current_view
        if not hasattr(v, 'tree'):
            return

        for item in v.tree.get_children():
            v.tree.delete(item)

        search_term = v.entry_search.get().strip().lower() if hasattr(v, 'entry_search') else ""
        selected_cat = v.filter_category.get() if hasattr(v, 'filter_category') else "ALL"
        fav_only = v.fav_only_var.get() if hasattr(v, 'fav_only_var') else False

        entries = database.get_all_entries()

        for row in entries:
            entry_id = row[0]
            link = row[1] if len(row) > 1 else ""
            user = row[2] if len(row) > 2 else ""
            enc_pw = row[3] if len(row) > 3 else ""
            enc_totp = row[4] if len(row) > 4 else ""
            category = row[5] if len(row) > 5 else "Other"
            is_fav = row[6] if len(row) > 6 else 0

            if fav_only and not is_fav:
                continue

            if selected_cat != "ALL" and category != selected_cat:
                continue

            if search_term and (search_term not in link.lower() and search_term not in user.lower()):
                continue

            try:
                plain_pw = crypto.decrypt_text(self.app.fernet, enc_pw) if enc_pw else ""
            except Exception:
                plain_pw = "[DECRYPT_ERROR]"

            display_pw = "••••••••" if getattr(self.app, 'hide_passwords', True) else plain_pw
            totp_code = self.app.generate_totp(enc_totp) if (enc_totp and hasattr(self.app, 'generate_totp')) else "---"
            fav_icon = "★" if is_fav else "☆"

            v.tree.insert(
                "", "end", 
                iid=entry_id,
                values=(
                    entry_id,
                    fav_icon,
                    category,
                    link,
                    user,
                    display_pw,
                    totp_code
                )
            )

    def save_entry(self, entry_data=None):
        """
        Speichert einen neuen Eintrag oder aktualisiert einen bestehenden.
        Kann entweder mit einm 'entry_data' Dict (aus dem EditDialog) 
        oder ohne Parameter (aus der Hauptansicht) aufgerufen werden.
        """
        v = self.app.current_view

        if entry_data:
            # Daten kommen aus dem Bearbeiten-Dialog (EditEntryDialog)
            entry_id = entry_data.get("id")
            link = entry_data.get("link", "").strip()
            user = entry_data.get("user", "").strip()
            plain_pw = entry_data.get("pw", "").strip()
            cat = entry_data.get("category", "Other")
            totp_secret = entry_data.get("totp", "").strip()
            is_fav = entry_data.get("is_fav", 0)
        else:
            # Daten kommen direkt aus den Eingabefeldern der MainView
            if not hasattr(v, 'entry_link'):
                return

            entry_id = getattr(self.app, 'editing_id', None)
            link = v.entry_link.get().strip()
            user = v.entry_user.get().strip()
            plain_pw = v.entry_pass.get().strip()
            cat = v.opt_category.get()
            totp_secret = v.entry_totp.get().strip() if hasattr(v, 'entry_totp') else ""
            is_fav = 1 if (hasattr(v, 'chk_favorite') and v.chk_favorite.get()) else 0

        # Validierung
        if not link or not plain_pw:
            from tkinter import messagebox
            messagebox.showwarning("VALIDATION_ERROR", "Target URI and Password are required!")
            return

        # Verschlüsselung
        enc_pw = crypto.encrypt_text(self.app.fernet, plain_pw)
        enc_totp = crypto.encrypt_text(self.app.fernet, totp_secret) if totp_secret else ""

        # Datenbank-Operation durchführen
        if entry_id:
            database.update_entry(entry_id, link, user, enc_pw, enc_totp, cat, is_fav)
            if hasattr(self.app, 'editing_id'):
                self.app.editing_id = None
            if hasattr(v, 'btn_save'):
                v.btn_save.configure(text="Save Entry")
        else:
            database.add_entry(link, user, enc_pw, enc_totp, cat, is_fav)

        # Formular zurücksetzen und Treeview neu laden
        self.clear_form()
        self.load_entries()

    def edit_selected_entry(self, event=None):
        v = self.app.current_view
        if not hasattr(v, 'tree'):
            return

        item_id = None
        if event:
            item_id = v.tree.identify_row(event.y)
        
        if not item_id:
            selection = v.tree.selection()
            if selection:
                item_id = selection[0]

        if not item_id:
            return

        # Rohdaten direkt aus der Datenbank abfragen, um Klartext-Passwort & Secret zu laden
        db_entry = database.get_entry_by_id(item_id) if hasattr(database, 'get_entry_by_id') else None

        if db_entry:
            # db_entry erwartet: (id, link, user, enc_pw, enc_totp, category, is_fav)
            enc_pw = db_entry[3] if len(db_entry) > 3 else ""
            enc_totp = db_entry[4] if len(db_entry) > 4 else ""

            try:
                plain_pw = crypto.decrypt_text(self.app.fernet, enc_pw) if enc_pw else ""
            except Exception:
                plain_pw = ""

            try:
                plain_totp = crypto.decrypt_text(self.app.fernet, enc_totp) if enc_totp else ""
            except Exception:
                plain_totp = ""

            entry_data = {
                "id": db_entry[0],
                "link": db_entry[1] if len(db_entry) > 1 else "",
                "user": db_entry[2] if len(db_entry) > 2 else "",
                "pw": plain_pw,
                "totp": plain_totp,
                "category": db_entry[5] if len(db_entry) > 5 else "Other",
                "is_fav": db_entry[6] if len(db_entry) > 6 else 0
            }
        else:
            # Fallback über Werte aus der Treeview
            values = v.tree.item(item_id, "values")
            entry_data = {
                "id": values[0],
                "is_fav": 1 if values[1] == "★" else 0,
                "category": values[2],
                "link": values[3],
                "user": values[4],
                "pw": "",
                "totp": ""
            }

        try:
            dialog = EditEntryDialog(
                parent=v.winfo_toplevel(),
                entry_data=entry_data, 
                on_save_callback=self._update_entry_in_db,
                on_delete_callback=self.delete_entry  # <--- HIER: Verbindet den Löschen-Button
            )
            dialog.focus()
        except Exception as e:
            print(f"FEHLER beim Öffnen des Dialogs: {e}")

    def _update_entry_in_db(self, updated_data):
        enc_pw = crypto.encrypt_text(self.app.fernet, updated_data["pw"])
        enc_totp = crypto.encrypt_text(self.app.fernet, updated_data["totp"]) if updated_data.get("totp") else ""

        database.update_entry(
            updated_data["id"],
            updated_data["link"],
            updated_data["user"],
            enc_pw,
            enc_totp,
            updated_data["category"],
            updated_data["is_fav"]
        )
        self.load_entries()

    def delete_entry(self, entry_id=None):
        """Löscht einen Eintrag aus der Datenbank und aktualisiert die Ansicht."""
        # Falls keine ID aus dem Dialog mitgegeben wurde, versuchen aus der Treeview-Selektion zu lesen
        if entry_id is None:
            v = self.app.current_view
            if hasattr(v, 'tree'):
                selected_item = v.tree.selection()
                if not selected_item:
                    messagebox.showwarning("WARNING", "Please select an entry to delete.")
                    return
                # Die ID steht in der ersten Spalte (values[0])
                entry_id = v.tree.item(selected_item[0])['values'][0]

        if not entry_id:
            print("Löschen abgebrochen: Keine validierte ID gefunden.")
            return

        # Sicherheitsabfrage
        confirm = messagebox.askyesno(
            "CONFIRM_DELETE", 
            f"Are you sure you want to delete entry ID {entry_id}?\nThis action cannot be undone."
        )

        if confirm:
            try:
                # WICHTIG: String in Integer umwandeln für die Datenbank-Query
                clean_id = int(entry_id)
                
                # Datenbank-Löschung ausführen
                database.delete_entry(clean_id)
                
                # UI-Tabelle neu laden
                self.load_entries()
                
                messagebox.showinfo("SUCCESS", f"Entry ID {clean_id} deleted successfully.")
            except ValueError:
                messagebox.showerror("ERROR", f"Invalid Entry ID: {entry_id}")
            except Exception as e:
                messagebox.showerror("ERROR", f"Failed to delete entry: {str(e)}")

    def clear_form(self):
        v = self.app.current_view
        if hasattr(v, 'entry_link'):
            v.entry_link.delete(0, "end")
            v.entry_user.delete(0, "end")
            v.entry_pass.delete(0, "end")
            v.entry_totp.delete(0, "end")
            v.opt_category.set("Other")
            v.chk_favorite.deselect()