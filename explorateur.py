import os
import shutil
import subprocess
import platform
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from PIL import Image, ImageTk, ImageOps, ImageDraw


class TacticalSentinelOS:
    def __init__(self, root):
        self.root = root
        self.root.title("EXPLORATEUR")
        self.root.geometry("1500x900")

        # Palette de couleurs avec fond "Gris Ciel" technique
        self.bg_deep = "#334155"  # Fond principal : Gris Ciel / Slate
        self.panel_bg = "#1e293b"  # Panneaux internes
        self.border_color = "#475569"  # Bordures assorties
        self.white_hud = "#ffffff"  # Contours, bordures et textes en blanc pur

        self.color_secure = "#10b981"  # Vert (Sain / Actif)

        self.text_light = "#f8fafc"
        self.text_dim = "#cbd5e1"
        self.icon_white = "#ffffff"

        self.root.configure(bg=self.bg_deep)

        self.current_path = "HOME_HUB"
        self.profile_photo_1 = None
        self.profile_photo_2 = None

        self.create_interface()
        self.bind_shortcuts()
        self.render_organigram_tree()

    def create_interface(self):
        # 1. BARRE DE FONCTION HAUTE (Avec F8 SUPPR)
        f_menu_frame = tk.Frame(self.root, bg="#1e293b", pady=8, padx=10)
        f_menu_frame.pack(fill=tk.X)

        f_keys = [
            ("F1 HOME", lambda: self.go_home()),
            ("F2 DRIVES", lambda: self.show_drives_organigram()),
            ("F3 TASKS", lambda: self.show_processes_organigram()),
            ("F4 RENAME", lambda: self.rename_node()),
            ("F5 NEW DIR", lambda: self.create_folder()),
            ("F7 COPY", lambda: self.copy_node()),
            ("F8 SUPPR", lambda: self.delete_node()),
            ("F9 SEARCH", lambda: self.search_node_dialog()),
            ("F10 EXIT", lambda: self.root.quit())
        ]

        for label, cmd in f_keys:
            btn = tk.Button(f_menu_frame, text=label, command=cmd,
                            bg="#0f172a", fg=self.white_hud, activebackground="#334155", activeforeground="white",
                            relief=tk.SOLID, bd=1, font=("Consolas", 9, "bold"), padx=8, pady=3)
            btn.pack(side=tk.LEFT, padx=3)

        # 2. CAPSULE DE PROFIL
        profile_container = tk.Frame(self.root, bg=self.bg_deep, pady=12)
        profile_container.pack(fill=tk.X)

        self.pill_canvas = tk.Canvas(profile_container, width=315, height=80, bg=self.bg_deep, highlightthickness=0)
        self.pill_canvas.pack(anchor=tk.CENTER)

        self.draw_pill_badge()

        self.avatar_canvas_1 = tk.Canvas(self.pill_canvas, width=64, height=64, bg="#0f172a", highlightthickness=0)
        self.avatar_canvas_1.place(x=8, y=8)
        self.draw_circular_plus_icon()

        self.avatar_canvas_2 = tk.Canvas(self.pill_canvas, width=221, height=64, bg="#0f172a", highlightthickness=0)
        self.avatar_canvas_2.place(x=78, y=8)
        self.draw_default_avatar_2()

        self.avatar_canvas_1.bind("<Button-1>", lambda e: self.load_profile_image(1))
        self.avatar_canvas_2.bind("<Button-1>", lambda e: self.load_profile_image(2))
        self.pill_canvas.bind("<Button-1>", lambda e: self.load_profile_image(1))

        # 3. ZONE CENTRALE
        center_panel = tk.Frame(self.root, bg=self.bg_deep)
        center_panel.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        nav_bar = tk.Frame(center_panel, bg=self.bg_deep, pady=2)
        nav_bar.pack(fill=tk.X, pady=(0, 5))

        btn_up = tk.Button(nav_bar, text="⬆ MEMBRANE PARENTE / RETOUR", command=lambda: self.go_up(),
                           bg="#1e293b", fg=self.white_hud, font=("Consolas", 9, "bold"),
                           relief=tk.SOLID, bd=1, padx=8, pady=4)
        btn_up.pack(side=tk.LEFT)

        header_box = tk.Frame(nav_bar, bg=self.panel_bg, highlightbackground=self.white_hud, highlightthickness=1,
                              padx=15, pady=4)
        header_box.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.path_display_lbl = tk.Label(header_box, text="SENTINEL_HUB // GESTIONNAIRE DE TÂCHES ACTIF",
                                         bg=self.panel_bg, fg=self.text_light, font=("Consolas", 8))
        self.path_display_lbl.pack()

        canvas_container = tk.Frame(center_panel, bg=self.bg_deep)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_container, bg=self.bg_deep, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.on_window_resize(e))

        # 4. LIGNE DE STATUT
        self.log_var = tk.StringVar(
            value=" SYS_STATUS: GESTIONNAIRE DE TÂCHES OPÉRATIONNEL (CLIQUEZ SUR UN PROCESSUS POUR FERMER).")
        log_bar = tk.Label(self.root, textvariable=self.log_var, bg="#1e293b", fg=self.white_hud, anchor=tk.W,
                           font=("Consolas", 9), padx=10, pady=6)
        log_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_shortcuts(self):
        self.root.bind("<F8>", lambda e: self.delete_node())
        self.root.bind("<Delete>", lambda e: self.delete_node())

    def draw_pill_badge(self):
        self.pill_canvas.delete("pill_bg")
        w, h = 315, 80
        r = 40
        self.pill_canvas.create_oval(0, 0, 2 * r, h, fill="#0f172a", outline=self.white_hud, width=1, tag="pill_bg")
        self.pill_canvas.create_oval(w - 2 * r, 0, w, h, fill="#0f172a", outline=self.white_hud, width=1, tag="pill_bg")
        self.pill_canvas.create_rectangle(r, 0, w - r, h, fill="#0f172a", outline="", tag="pill_bg")
        self.pill_canvas.create_line(r, 0, w - r, 0, fill=self.white_hud, width=1, tag="pill_bg")
        self.pill_canvas.create_line(r, h, w - r, h, fill=self.white_hud, width=1, tag="pill_bg")

    def draw_circular_plus_icon(self):
        self.avatar_canvas_1.delete("all")
        self.avatar_canvas_1.create_oval(4, 4, 60, 60, fill="#ffffff", outline="")
        self.avatar_canvas_1.create_line(32, 18, 32, 46, fill="#0f172a", width=4)
        self.avatar_canvas_1.create_line(18, 32, 46, 32, fill="#0f172a", width=4)

    def draw_default_avatar_2(self):
        self.avatar_canvas_2.delete("all")
        self.avatar_canvas_2.create_text(110, 24, text="👤 PROFIL", fill=self.white_hud, font=("Consolas", 10, "bold"))
        self.avatar_canvas_2.create_text(110, 44, text="Changer l'image", fill="#94a3b8", font=("Consolas", 8))

    def load_profile_image(self, profile_num):
        title_str = "Sélectionner l'image pour le cercle 1" if profile_num == 1 else "Sélectionner la photo du profil"
        file_path = filedialog.askopenfilename(title=title_str, filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            try:
                img = Image.open(file_path).convert("RGBA")
                if profile_num == 1:
                    img = ImageOps.fit(img, (56, 56), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                    mask = Image.new("L", (56, 56), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, 56, 56), fill=255)
                    output = Image.new("RGBA", (56, 56), (0, 0, 0, 0))
                    output.paste(img, (0, 0), mask)
                    photo = ImageTk.PhotoImage(output)
                    self.profile_photo_1 = photo
                    self.avatar_canvas_1.delete("all")
                    self.avatar_canvas_1.create_image(32, 32, image=photo)
                else:
                    img = ImageOps.fit(img, (221, 64), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                    photo = ImageTk.PhotoImage(img)
                    self.profile_photo_2 = photo
                    self.avatar_canvas_2.delete("all")
                    self.avatar_canvas_2.create_image(110, 32, image=photo)
                self.log_var.set(f" PROFIL {profile_num} MIS À JOUR : {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger l'image : {e}")

    def on_window_resize(self, event):
        self.render_organigram_tree()

    def go_home(self):
        self.current_path = "HOME_HUB"
        self.render_organigram_tree()

    def navigate_to(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            self.current_path = path
            self.render_organigram_tree()

    def get_node_icon(self, name, is_dir):
        lower = name.lower()
        if "musique" in lower or "music" in lower: return "🎵"
        if "image" in lower or "picture" in lower or "photo" in lower: return "🖼️"
        if "vidéo" in lower or "video" in lower: return "🎬"
        if "document" in lower or "docs" in lower: return "📄"
        if "téléchargement" in lower or "download" in lower: return "⬇️"
        if "bureau" in lower or "desktop" in lower: return "🖥️"
        if "accueil" in lower or "home" in lower: return "🏠"
        if "système" in lower or "system" in lower: return "⚙️"
        if "disque" in lower or "drive" in lower: return "💾"
        if "jeu" in lower or "game" in lower: return "🎮"
        if "application" in lower or "program" in lower: return "📦"
        if "compte" in lower or "user" in lower: return "👤"
        if "code" in lower or "project" in lower or "python" in lower: return "💻"
        if "sécurité" in lower or "security" in lower: return "🔒"
        if "windows" in lower: return "🪟"
        if is_dir: return "📁"

        ext = os.path.splitext(name)[1].lower()
        if ext in ['.py', '.js', '.cpp']:
            return "🐍"
        elif ext in ['.png', '.jpg', '.jpeg']:
            return "🖼️"
        elif ext in ['.pdf']:
            return "📑"
        elif ext in ['.txt', '.doc', '.docx']:
            return "📝"
        elif ext in ['.zip', '.rar', '.7z']:
            return "🗜️"
        elif ext in ['.exe', '.bat']:
            return "⚡"
        elif ext in ['.mp3', '.wav']:
            return "🎵"
        elif ext in ['.mp4', '.avi']:
            return "🎬"
        return "📄"

    def render_organigram_tree(self):
        self.canvas.delete("all")
        try:
            if self.current_path == "HOME_HUB":
                self.path_display_lbl.config(text="ACCÈS RAPIDE & LECTEURS")
                home = os.path.expanduser("~")
                quick_access_items = [
                    ("Accueil", home),
                    ("Bureau", os.path.join(home, "Desktop")),
                    ("Images", os.path.join(home, "Pictures")),
                    ("Vidéos", os.path.join(home, "Videos")),
                    ("Musique", os.path.join(home, "Music")),
                    ("Documents", os.path.join(home, "Documents")),
                    ("Téléchargements", os.path.join(home, "Downloads"))
                ]

                drives = []
                if platform.system() == "Windows":
                    import string
                    drives = [(f"Disque {d}", f"{d}:\\") for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
                else:
                    drives = [("Racine Système", "/")]

                class HubDummy:
                    def __init__(self, name, path):
                        self.name = name
                        self.path = path

                    def is_dir(self): return True

                entries = [HubDummy(name, path) for name, path in quick_access_items if os.path.exists(path)]
                entries += [HubDummy(name, path) for name, path in drives]

                width = max(600, self.canvas.winfo_width())
                height = max(400, self.canvas.winfo_height())
                parent_x = width // 2
                parent_y = 35
                parent_w, parent_h = min(340, width - 40), 40

                self.draw_node_card(parent_x, parent_y, parent_w, parent_h, "CENTRAL_HUB_CORE", "[ACTIF]",
                                    self.color_secure, path=None, is_root=True)

                num_entries = len(entries)
                cols = 4 if num_entries > 8 else (3 if num_entries > 4 else max(1, num_entries))
                rows = (num_entries + cols - 1) // cols
                start_y = 110
                available_height = height - start_y - 20
                row_spacing = max(45, available_height // max(1, rows))
                col_spacing = width // (cols + 1)

                for i, entry in enumerate(entries):
                    r, c = i // cols, i % cols
                    child_x = col_spacing * (c + 1)
                    child_y = start_y + (r * row_spacing)
                    card_w = min(220, col_spacing - 15)
                    card_h = min(40, row_spacing - 8)

                    mid_y = (parent_y + (parent_h // 2) + child_y - (card_h // 2)) // 2
                    self.canvas.create_line(parent_x, parent_y + (parent_h // 2), parent_x, mid_y,
                                            fill=self.color_secure, width=2)
                    self.canvas.create_line(parent_x, mid_y, child_x, mid_y, fill=self.color_secure, width=2)
                    self.canvas.create_line(child_x, mid_y, child_x, child_y - (card_h // 2), fill=self.color_secure,
                                            width=2)

                    self.draw_node_card(child_x, child_y, card_w, card_h, entry.name, "[OK]", self.color_secure,
                                        path=entry.path, is_dir=True)

                self.log_var.set(f" GRILLE CHARGÉE : {num_entries} emplacements.")
                return

            abs_path = os.path.abspath(self.current_path)
            if not os.path.exists(abs_path) or not os.path.isdir(abs_path):
                return

            self.current_path = abs_path
            self.path_display_lbl.config(text=f"PATH: {self.current_path}")

            entries = list(os.scandir(self.current_path))
            entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))

            width = max(600, self.canvas.winfo_width())
            height = max(400, self.canvas.winfo_height())
            parent_x = width // 2
            parent_y = 35
            parent_w, parent_h = min(320, width - 40), 40

            self.draw_node_card(parent_x, parent_y, parent_w, parent_h,
                                os.path.basename(self.current_path) or self.current_path, "[ACTIF]", self.color_secure,
                                path=None, is_root=True)

            if not entries:
                return

            num_entries = len(entries)
            cols = 4 if num_entries > 8 else (3 if num_entries > 4 else max(1, num_entries))
            rows = (num_entries + cols - 1) // cols
            start_y = 110
            available_height = height - start_y - 20
            row_spacing = max(45, available_height // max(1, rows))
            col_spacing = width // (cols + 1)

            for i, entry in enumerate(entries):
                r, c = i // cols, i % cols
                child_x = col_spacing * (c + 1)
                child_y = start_y + (r * row_spacing)
                card_w = min(220, col_spacing - 15)
                card_h = min(40, row_spacing - 8)

                mid_y = (parent_y + (parent_h // 2) + child_y - (card_h // 2)) // 2
                self.canvas.create_line(parent_x, parent_y + (parent_h // 2), parent_x, mid_y, fill=self.color_secure,
                                        width=2)
                self.canvas.create_line(parent_x, mid_y, child_x, mid_y, fill=self.color_secure, width=2)
                self.canvas.create_line(child_x, mid_y, child_x, child_y - (card_h // 2), fill=self.color_secure,
                                        width=2)

                name = entry.name
                is_dir = entry.is_dir()
                target_path = os.path.join(self.current_path, name)
                self.draw_node_card(child_x, child_y, card_w, card_h, name, "[OK]", self.color_secure, path=target_path,
                                    is_dir=is_dir)

            self.log_var.set(f" DOSSIER SYNCHRONISÉ : {num_entries} éléments affichés.")

        except PermissionError:
            self.log_var.set(" INFO : Accès refusé à ce dossier.")
        except Exception as e:
            self.log_var.set(f" ERREUR : {str(e)}")

    def draw_node_card(self, x, y, w, h, title, status_text, status_color, path=None, is_dir=False, is_root=False):
        x1, y1 = x - w // 2, y - h // 2
        x2, y2 = x + w // 2, y + h // 2

        bg_col = self.panel_bg if not is_root else "#283548"
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_col, outline=self.border_color, width=2)

        icon_char = "🛡️" if is_root else self.get_node_icon(title, is_dir)
        self.canvas.create_text(x1 + 16, y - 6, text=icon_char, font=("Segoe UI Emoji", 11), fill=self.icon_white,
                                anchor="center")

        max_chars = max(7, (w - 42) // 9)
        display_title = title[:max_chars] + ("..." if len(title) > max_chars else "")
        t_id = self.canvas.create_text(x + 12, y - 6, text=display_title, fill=self.text_light,
                                       font=("Consolas", 8, "bold"))

        bx1, by1, bx2, by2 = x1 + 30, y + 2, x2 - 6, y + 15
        status_bg = self.canvas.create_rectangle(bx1, by1, bx2, by2, fill=status_color, outline="")
        s_id = self.canvas.create_text((bx1 + bx2) // 2, (by1 + by2) // 2, text=status_text, fill="#030712",
                                       font=("Consolas", 6, "bold"))

        for item in (rect, t_id, status_bg, s_id):
            if path:
                self.canvas.tag_bind(item, "<Button-1>", lambda e, p=path, d=is_dir: self.handle_node_click(p, d))

    def handle_node_click(self, path, is_dir):
        if is_dir and os.path.exists(path):
            self.navigate_to(path)
        elif not is_dir and os.path.exists(path):
            self.open_file_node(path)

    def open_file_node(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
            self.log_var.set(f" OUVERTURE : {path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

    def go_up(self):
        if self.current_path == "HOME_HUB":
            return
        parent_path = os.path.dirname(self.current_path)
        if parent_path == self.current_path or len(parent_path) <= 3:
            self.go_home()
        else:
            self.current_path = parent_path
            self.render_organigram_tree()

    def show_drives_organigram(self):
        self.go_home()

    def show_processes_organigram(self):
        self.canvas.delete("all")
        try:
            procs = []
            if platform.system() == "Windows":
                output = subprocess.check_output(["tasklist"], universal_newlines=True)
                lines = output.splitlines()[3:]
                for line in lines:
                    if line.strip():
                        name = line.split()[0]
                        if name not in procs: procs.append(name)
                procs = procs[:20]
            else:
                output = subprocess.check_output(["ps", "-e", "-o", "comm="], universal_newlines=True)
                procs = [p.strip() for p in output.splitlines() if p.strip()][:20]

            class ProcDummy:
                def __init__(self, name): self.name = name

                def is_dir(self): return False

            entries = [ProcDummy(p) for p in procs]
            self.path_display_lbl.config(
                text="GESTIONNAIRE DE TÂCHES (Cliquez sur un processus pour le fermer - F1 pour le Hub)")

            width = max(600, self.canvas.winfo_width())
            height = max(400, self.canvas.winfo_height())
            parent_x = width // 2
            parent_y = 35
            self.draw_node_card(parent_x, parent_y, 320, 40, "GESTIONNAIRE DE TÂCHES", "[ACTIF]", self.color_secure,
                                path=None, is_root=True)

            num_entries = len(entries)
            cols = 4 if num_entries > 8 else 3
            rows = (num_entries + cols - 1) // cols
            start_y = 110
            row_spacing = max(45, (height - start_y - 20) // max(1, rows))
            col_spacing = width // (cols + 1)

            for i, entry in enumerate(entries):
                r, c = i // cols, i % cols
                child_x, child_y = col_spacing * (c + 1), start_y + (r * row_spacing)
                card_w, card_h = min(220, col_spacing - 15), min(38, row_spacing - 8)

                name = entry.name
                mid_y = (parent_y + 20 + child_y - (card_h // 2)) // 2
                self.canvas.create_line(parent_x, parent_y + 20, parent_x, mid_y, fill=self.color_secure, width=2)
                self.canvas.create_line(parent_x, mid_y, child_x, mid_y, fill=self.color_secure, width=2)
                self.canvas.create_line(child_x, mid_y, child_x, child_y - (card_h // 2), fill=self.color_secure,
                                        width=2)

                x1, y1 = child_x - card_w // 2, child_y - card_h // 2
                x2, y2 = child_x + card_w // 2, child_y + card_h // 2
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.panel_bg, outline=self.border_color,
                                                    width=2)

                self.canvas.create_text(x1 + 16, child_y - 6, text="⚡", font=("Segoe UI Emoji", 11),
                                        fill=self.icon_white, anchor="center")
                t_id = self.canvas.create_text(child_x + 12, child_y - 6, text=name[:14], fill=self.text_light,
                                               font=("Consolas", 8, "bold"))

                status_bg = self.canvas.create_rectangle(x1 + 26, child_y + 2, x2 - 6, child_y + 14,
                                                         fill=self.color_secure, outline="")
                s_id = self.canvas.create_text((x1 + 26 + x2 - 6) // 2, child_y + 8, text="[KILL]", fill="#030712",
                                               font=("Consolas", 6, "bold"))

                for item in (rect, t_id, status_bg, s_id):
                    self.canvas.tag_bind(item, "<Button-1>", lambda e, p=name: self.kill_process(p))

            self.log_var.set(" GESTIONNAIRE DE TÂCHES : Cliquez sur un processus pour l'arrêter.")
        except Exception as e:
            self.log_var.set(f" ERREUR : {str(e)}")

    def kill_process(self, proc_name):
        if messagebox.askyesno("Gestionnaire de Tâches", f"Voulez-vous fermer le processus '{proc_name}' ?"):
            try:
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/f", "/im", proc_name], capture_output=True)
                else:
                    subprocess.run(["killall", proc_name], capture_output=True)
                self.show_processes_organigram()
                self.log_var.set(f" PROCESSUS ARRÊTÉ : {proc_name}")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def rename_node(self):
        if self.current_path == "HOME_HUB": return
        old_name = simpledialog.askstring("Renommer", "Nom exact de l'élément à renommer :", parent=self.root)
        if old_name:
            old_path = os.path.join(self.current_path, old_name)
            if os.path.exists(old_path):
                new_name = simpledialog.askstring("Renommer", f"Nouveau nom pour '{old_name}' :", initialvalue=old_name,
                                                  parent=self.root)
                if new_name and new_name != old_name:
                    try:
                        os.rename(old_path, os.path.join(self.current_path, new_name))
                        self.render_organigram_tree()
                    except Exception as e:
                        messagebox.showerror("Erreur", str(e))

    def create_folder(self):
        if self.current_path == "HOME_HUB": return
        name = simpledialog.askstring("Nouveau dossier", "Nom du nouveau dossier :", parent=self.root)
        if name:
            try:
                os.makedirs(os.path.join(self.current_path, name), exist_ok=False)
                self.render_organigram_tree()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def copy_node(self):
        if self.current_path == "HOME_HUB": return
        src = filedialog.askopenfilename(title="Sélectionner le fichier source")
        if src:
            dest = filedialog.askdirectory(title="Dossier de destination")
            if dest:
                try:
                    shutil.copy2(src, dest)
                    self.render_organigram_tree()
                    self.log_var.set(" FICHIER COPIÉ AVEC SUCCÈS.")
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))

    def delete_node(self):
        if self.current_path == "HOME_HUB": return
        name = simpledialog.askstring("Supprimer", "Nom exact de l'élément à supprimer :", parent=self.root)
        if name:
            target_path = os.path.join(self.current_path, name)
            if os.path.exists(target_path):
                if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer '{name}' ?"):
                    try:
                        if os.path.isdir(target_path):
                            shutil.rmtree(target_path)
                        else:
                            os.remove(target_path)
                        self.render_organigram_tree()
                        self.log_var.set(f" SUPPRIMÉ : {name}")
                    except Exception as e:
                        messagebox.showerror("Erreur", str(e))
            else:
                messagebox.showerror("Erreur", f"L'élément '{name}' est introuvable ici.")

    def search_node_dialog(self):
        search_root = os.path.expanduser("~") if self.current_path == "HOME_HUB" else self.current_path
        query = simpledialog.askstring("Recherche", "Terme à rechercher :", parent=self.root)
        if query:
            matches = [os.path.join(r, f) for r, d, fs in os.walk(search_root) for f in fs + d if
                       query.lower() in f.lower()][:20]
            self.canvas.delete("all")

            class SearchDummy:
                def __init__(self, p): self.name = p

                def is_dir(self): return os.path.isdir(self.name)

            entries = [SearchDummy(m) for m in matches]

            width = max(600, self.canvas.winfo_width())
            height = max(400, self.canvas.winfo_height())
            parent_x = width // 2
            self.draw_node_card(parent_x, 35, 320, 40, f"RECHERCHE: '{query}'", "[RÉSULTATS]", self.color_secure,
                                path=None, is_root=True)

            num_entries = len(entries)
            cols = 4 if num_entries > 8 else 3
            rows = (num_entries + cols - 1) // cols
            start_y = 110
            row_spacing = max(45, (height - start_y - 20) // max(1, rows))
            col_spacing = width // (cols + 1)

            for i, entry in enumerate(entries):
                r, c = i // cols, i % cols
                child_x, child_y = col_spacing * (c + 1), start_y + (r * row_spacing)
                card_w, card_h = min(220, col_spacing - 15), min(38, row_spacing - 8)
                target_path = entry.name

                x1, y1 = child_x - card_w // 2, child_y - card_h // 2
                x2, y2 = child_x + card_w // 2, child_y + card_h // 2
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.panel_bg, outline=self.border_color,
                                                    width=2)

                icon_char = self.get_node_icon(target_path, os.path.isdir(target_path))
                self.canvas.create_text(x1 + 16, child_y - 6, text=icon_char, font=("Segoe UI Emoji", 11),
                                        fill=self.icon_white, anchor="center")

                t_id = self.canvas.create_text(child_x + 12, child_y - 6, text=os.path.basename(target_path)[:14],
                                               fill=self.text_light, font=("Consolas", 8, "bold"))
                status_bg = self.canvas.create_rectangle(x1 + 26, child_y + 2, x2 - 6, child_y + 14,
                                                         fill=self.color_secure, outline="")
                s_id = self.canvas.create_text((x1 + 26 + x2 - 6) // 2, child_y + 8, text="[MATCH]", fill="#030712",
                                               font=("Consolas", 6, "bold"))

                for item in (rect, t_id, status_bg, s_id):
                    self.canvas.tag_bind(item, "<Button-1>", lambda e, p=target_path: self.navigate_to(
                        os.path.dirname(p) if not os.path.isdir(p) else p))


if __name__ == "__main__":
    root = tk.Tk()
    app = TacticalSentinelOS(root)
    root.mainloop()

