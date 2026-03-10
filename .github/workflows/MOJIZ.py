import tkinter as tk
from tkinter import messagebox, ttk
import os, json, time, threading, subprocess, webbrowser, re, socket, platform, ctypes, sys
import psutil, requests
import winreg as reg

# Определяем путь к папке, где лежит EXE (или скрипт)
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(APP_DIR, "mojiz_settings.json")
BG, BG_SEC, CARD = "#050508", "#0A0A0F", "#0D0D14"
BORDER = "#1F1F2E"
CYAN, GREEN, RED, PURPLE, ORANGE, YELLOW = "#00F5FF", "#39FF14", "#FF2D55", "#BF5FFF", "#FF6B35", "#FFF000"
TEXT, DIM = "#E0E0FF", "#4F4F6A"
NEONS = [CYAN, GREEN, RED, PURPLE, ORANGE, YELLOW]

def get_win_ver():
    try:
        version = platform.version()
        build = version.split('.')[-1]
        win_info = platform.win32_ver()
        return f"Win {win_info[0]} {win_info[1]} (Build {build})"
    except:
        return "Windows OS"

LOCALES = {
    "RU": {
        "main": "🏠 ГЛАВНАЯ", "tools": "🛠 УТИЛИТЫ", "settings": "⚙ ОПЦИИ",
        "sys": "📊 СТАТИСТИКА", "games": "🎮 БИБЛИОТЕКА", "links": "🔗 ССЫЛКИ",
        "mem": "🧹 ОЧИСТКА RAM", "temp": "🗑 ЧИСТКА TEMP", "scale": "🔍 МАСШТАБ UI",
        "ping_run": "ТЕСТ...", "ping_res": "ПИНГ: ", "ping_btn": "⚡ ТЕСТ ЗАДЕРЖКИ",
        "reset_info": "Reset: CTRL+L (Eng layout)", "lang_title": "🌐 ЯЗЫК",
        "ram_ok": "RAM Оптимизирована", "temp_ok": "Файлов удалено: ",
        "autostart": "🚀 АВТОЗАГРУЗКА"
    },
    "EN": {
        "main": "🏠 MAIN", "tools": "🛠 TOOLS", "settings": "⚙ SET",
        "sys": "📊 STATS", "games": "🎮 LIBRARY", "links": "🔗 LINKS",
        "mem": "🧹 MEM REDUCT", "temp": "🗑 TEMP CLEAN", "scale": "🔍 UI SCALE",
        "ping_run": "TEST...", "ping_res": "PING: ", "ping_btn": "⚡ TEST LATENCY",
        "reset_info": "Reset: CTRL+L (Eng layout)", "lang_title": "🌐 LANGUAGE",
        "ram_ok": "RAM Optimized", "temp_ok": "Files deleted: ",
        "autostart": "🚀 AUTOSTART"
    },
    "UA": {
        "main": "🏠 ГОЛОВНА", "tools": "🛠 УТИЛІТИ", "settings": "⚙ ОПЦІЇ",
        "sys": "📊 СТАТИСТИКА", "games": "🎮 БІБЛІОТЕКА", "links": "🔗 ПОСИЛАННЯ",
        "mem": "🧹 ОЧИЩЕННЯ RAM", "temp": "🗑 ЧИСТКА TEMP", "scale": "🔍 МАСШТАБ UI",
        "ping_run": "ТЕСТ...", "ping_res": "ПІНГ: ", "ping_btn": "⚡ ТЕСТ ЗАТРИМКИ",
        "reset_info": "Reset: CTRL+L (Eng layout)", "lang_title": "🌐 МОВА",
        "ram_ok": "RAM Оптимізовано", "temp_ok": "Файлів видалено: ",
        "autostart": "🚀 АВТОЗАВАНТАЖЕННЯ"
    },
    "ES": {
        "main": "🏠 INICIO", "tools": "🛠 HERRAM.", "settings": "⚙ AJUSTES",
        "sys": "📊 ESTADO", "games": "🎮 BIBLIOTECA", "links": "🔗 ENLACES",
        "mem": "🧹 LIMPIAR RAM", "temp": "🗑 LIMPIAR TEMP", "scale": "🔍 ESCALA UI",
        "ping_run": "TEST...", "ping_res": "PING: ", "ping_btn": "⚡ PROBAR LATENCIA",
        "reset_info": "Reset: CTRL+L (Eng layout)", "lang_title": "🌐 IDIOMA",
        "ram_ok": "RAM Optimizada", "temp_ok": "Archivos borrados: ",
        "autostart": "🚀 INICIO AUTO"
    },
    "DE": {
        "main": "🏠 HOME", "tools": "🛠 TOOLS", "settings": "⚙ SETTINGS",
        "sys": "📊 STATS", "games": "🎮 BIBLIOTHEK", "links": "🔗 LINKS",
        "mem": "🧹 RAM REINIGEN", "temp": "🗑 TEMP LEEREN", "scale": "🔍 UI SKALIERUNG",
        "ping_run": "TEST...", "ping_res": "PING: ", "ping_btn": "⚡ LATENZ TEST",
        "reset_info": "Reset: CTRL+L (Eng layout)", "lang_title": "🌐 SPRACHE",
        "ram_ok": "RAM Optimiert", "temp_ok": "Dateien gelöscht: ",
        "autostart": "🚀 AUTOSTART"
    }
}

class MojizV1(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = self.load_settings()
        self.lang = self.data.get("lang", "EN")
        self.games = self.data.get("games", [])
        self.links = self.data.get("links", [])
        self.win_res = self.data.get("res", "750x950")
        self.win_scale = self.data.get("scale", 1.5)
        self.stats_colors = self.data.get("stats_colors", {"CPU": [GREEN, CYAN], "RAM": [GREEN, CYAN], "GPU": [GREEN, CYAN], "DISK": [GREEN, CYAN]})
        self.collapsed = self.data.get("collapsed", {"games": False, "links": False})
        
        self.cur_tab = "MAIN"
        self.canvas = None
        self.list_frames = {}
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        self.apply_ui_settings()
        self.init_ui()
        self.start_threads()
        
        self.bind_all("<Control-l>", self.hard_reset)
        self.bind_all("<Control-L>", self.hard_reset)
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding='utf-8') as f: return json.load(f)
            except: return {}
        return {}

    def save_settings(self):
        self.data = {"lang": self.lang, "games": self.games, "links": self.links, "res": self.geometry(), "scale": self.win_scale, "stats_colors": self.stats_colors, "collapsed": self.collapsed}
        with open(CONFIG_FILE, "w", encoding='utf-8') as f: json.dump(self.data, f, indent=4, ensure_ascii=False)

    def on_close(self): self.save_settings(); self.destroy()

    def hard_reset(self, event=None):
        self.win_scale = 1.5; self.lang = "EN"; self.save_settings(); self.apply_ui_settings(); self.init_ui()

    def toggle_autostart(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "MojizApp"
        exe_path = f'"{sys.executable}"' if getattr(sys, 'frozen', False) else f'"{os.path.abspath(__file__)}"'
        
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
            try:
                reg.QueryValueEx(key, app_name)
                reg.DeleteValue(key, app_name)
                messagebox.showinfo("Mojiz", "Autostart: OFF")
            except FileNotFoundError:
                reg.SetValueEx(key, app_name, 0, reg.REG_SZ, exe_path)
                messagebox.showinfo("Mojiz", "Autostart: ON")
            reg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def apply_ui_settings(self):
        self.geometry(self.win_res)
        try: self.tk.call('tk', 'scaling', self.win_scale)
        except: pass
        self.configure(bg=BG); self.title("MOJIZ V1")

    def init_ui(self):
        for w in self.winfo_children(): w.destroy()
        L, s = LOCALES[self.lang], self.win_scale

        hdr = tk.Frame(self, bg=BG); hdr.pack(fill="x", padx=15, pady=int(10*s))
        tk.Label(hdr, text="⬢ MOJIZ", font=("Consolas", int(16*s), "bold"), fg=GREEN, bg=BG).pack(side="left")
        
        nav = tk.Frame(self, bg=BG); nav.pack(fill="x", padx=15)
        for t_id, t_key, t_clr in [("MAIN", "main", GREEN), ("TOOLS", "tools", CYAN), ("SET", "settings", RED)]:
            clr = t_clr if self.cur_tab == t_id else DIM
            tk.Button(nav, text=L[t_key], font=("Segoe UI", int(10*s), "bold"), bg=BG, fg=clr, relief="flat", bd=0, command=lambda x=t_id: self.switch_tab(x)).pack(side="left", padx=int(10*s))
            
        self.main_container = tk.Frame(self, bg=BG)
        self.main_container.pack(fill="both", expand=True, padx=12, pady=5)
        self.render_tab()
        
        footer = tk.Frame(self, bg=BG_SEC, height=int(30*s)); footer.pack(fill="x", side="bottom")
        self.lbl_net = tk.Label(footer, text="   ● CHECKING...", fg=YELLOW, bg=BG_SEC, font=("Segoe UI", int(7*s)))
        self.lbl_net.pack(side="left", padx=5)
        sys_info = f"{get_win_ver()} | V1.0"
        tk.Label(footer, text=sys_info, fg=DIM, bg=BG_SEC, font=("Segoe UI", int(7*s))).pack(side="right", padx=15)

    def switch_tab(self, tab):
        self.cur_tab = tab
        self.init_ui()

    def _on_mousewheel(self, event):
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def render_tab(self):
        L, s = LOCALES[self.lang], self.win_scale
        if self.cur_tab == "MAIN":
            self.canvas = tk.Canvas(self.main_container, bg=BG, highlightthickness=0)
            self.scrollable_frame = tk.Frame(self.canvas, bg=BG)
            self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
            self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width))
            self.canvas.pack(side="left", fill="both", expand=True)
            
            st_card = self.card(self.scrollable_frame, L["sys"], GREEN)
            self.stats_ui = {}
            for n in ["CPU", "RAM", "GPU", "DISK"]:
                f = tk.Frame(st_card, bg=CARD); f.pack(fill="x", padx=15, pady=int(4*s))
                clrs = self.stats_colors.get(n, [GREEN, CYAN])
                lbl_n = tk.Label(f, text=n, font=("Consolas", int(8*s), "bold"), fg=clrs[0], bg=CARD, width=6, cursor="hand2")
                lbl_n.pack(side="left")
                lbl_n.bind("<Button-1>", lambda e, x=n: self.cycle_stat_part(x, 0))
                st_name = f"{n}.Horizontal.TProgressbar"
                self.style.configure(st_name, background=clrs[1], troughcolor=BG_SEC, borderwidth=0, thickness=6)
                pb = ttk.Progressbar(f, style=st_name); pb.pack(side="left", padx=10, fill="x", expand=True)
                lbl_v = tk.Label(f, text="0%", font=("Consolas", int(9*s), "bold"), fg=clrs[1], bg=CARD, cursor="hand2", width=5)
                lbl_v.pack(side="right")
                lbl_v.bind("<Button-1>", lambda e, x=n: self.cycle_stat_part(x, 1))
                self.stats_ui[n] = (pb, lbl_v)

            self.list_frames = {}
            for key, data, clr, mode in [("games", self.games, ORANGE, "steam"), ("links", self.links, PURPLE, "web")]:
                card_frame = self.card(self.scrollable_frame, L[key], clr, collapsible=True, section=key)
                content_f = tk.Frame(card_frame, bg=CARD)
                self.list_frames[key] = content_f
                if not self.collapsed.get(key):
                    content_f.pack(fill="x")
                    self.update_list_ui(key, data, mode)
            
            add_bar = tk.Frame(self, bg=BG_SEC, pady=8); add_bar.pack(fill="x", side="bottom")
            self.ent_name = self.draw_entry(add_bar, "NAME", 12)
            self.ent_val = self.draw_entry(add_bar, "ID / URL", 20)
            self.tool_btn(add_bar, "+G", ORANGE, self.add_game).pack(side="left", padx=5)
            self.tool_btn(add_bar, "+L", PURPLE, self.add_link).pack(side="left", padx=5)

        elif self.cur_tab == "TOOLS":
            t_card = self.card(self.main_container, L["tools"], YELLOW)
            for k, c, cmd in [(L["mem"], GREEN, self.mem_reduct), (L["temp"], ORANGE, self.clean_temp)]:
                self.tool_btn(t_card, k, c, cmd).pack(fill="x", padx=30, pady=10)
            p_f = tk.Frame(t_card, bg=BG_SEC, pady=20); p_f.pack(fill="x")
            self.lbl_ping = tk.Label(p_f, text="PING: ---", fg=CYAN, bg=BG_SEC, font=("Consolas", int(12*s), "bold"))
            self.lbl_ping.pack()
            self.tool_btn(p_f, L["ping_btn"], CYAN, self.ping_anim).pack(pady=5)

        elif self.cur_tab == "SET":
            s_card = self.card(self.main_container, L["settings"], RED)
            # Кнопка автозагрузки
            self.tool_btn(s_card, L["autostart"], CYAN, self.toggle_autostart).pack(fill="x", padx=30, pady=10)
            
            tk.Label(s_card, text=L["reset_info"], fg=ORANGE, bg=CARD, font=("Consolas", int(8*s), "bold")).pack(pady=10)
            tk.Label(s_card, text=L["lang_title"], fg=RED, bg=CARD, font=("Segoe UI", int(9*s), "bold")).pack(pady=5)
            l_f = tk.Frame(s_card, bg=CARD); l_f.pack(pady=5)
            for ln in ["RU", "EN", "UA", "ES", "DE"]:
                self.tool_btn(l_f, ln, YELLOW if self.lang==ln else DIM, lambda x=ln: self.set_lang(x)).pack(side="left", padx=3)
            
            tk.Label(s_card, text=L["scale"], fg=CYAN, bg=CARD, font=("Segoe UI", int(9*s), "bold")).pack(pady=10)
            sc_f = tk.Frame(s_card, bg=CARD); sc_f.pack()
            for sc in [1.0, 1.25, 1.5, 2.0, 2.5]: 
                self.tool_btn(sc_f, str(sc), GREEN if self.win_scale==sc else DIM, lambda x=sc: self.change_ui(scale=x)).pack(side="left", padx=3)

    def card(self, parent, title, color, collapsible=False, section=None):
        f = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER); f.pack(fill="x", pady=6)
        h = tk.Frame(f, bg=BG_SEC, cursor="hand2" if collapsible else ""); h.pack(fill="x")
        lbl_arr = tk.Label(h, text=" △" if not self.collapsed.get(section) else " ▽", fg=color, bg=BG_SEC, font=("Arial", int(10*self.win_scale)))
        lbl_arr.pack(side="right", padx=10)
        lbl_txt = tk.Label(h, text=title, font=("Segoe UI", int(10*self.win_scale), "bold"), fg=color, bg=BG_SEC, padx=10, pady=7)
        lbl_txt.pack(side="left")
        if collapsible:
            for el in [h, lbl_txt, lbl_arr]: el.bind("<Button-1>", lambda e, s=section, l=lbl_arr: self.toggle_section(s, l))
        tk.Frame(h, bg=color, width=4).pack(side="left", fill="y")
        return f

    def update_list_ui(self, key, data_list, mode):
        parent = self.list_frames.get(key)
        if not parent: return
        for w in parent.winfo_children(): w.destroy()
        for i, item in enumerate(data_list):
            row = tk.Frame(parent, bg=CARD); row.pack(fill="x", pady=1)
            mv = tk.Frame(row, bg=CARD); mv.pack(side="left", padx=2)
            tk.Button(mv, text="▲", font=("Arial", 6), bg=BG, fg=DIM, bd=0, command=lambda x=i, l=data_list, k=key, m=mode: self.move_item(l, x, -1, k, m)).pack()
            tk.Button(mv, text="▼", font=("Arial", 6), bg=BG, fg=DIM, bd=0, command=lambda x=i, l=data_list, k=key, m=mode: self.move_item(l, x, 1, k, m)).pack()
            tk.Button(row, text="●", bg=CARD, fg=item.get("color", CYAN), font=("Arial", 10), relief="flat", bd=0, command=lambda l=data_list, idx=i, k=key, m=mode: self.cycle_item_color(l, idx, k, m)).pack(side="left", padx=5)
            btn = tk.Button(row, text=item['name'], anchor="w", bg=CARD, fg=item.get("color", CYAN), font=("Segoe UI", int(9*self.win_scale), "bold"), relief="flat", command=lambda x=item: self.launch(x, mode))
            btn.pack(side="left", fill="x", expand=True)
            tk.Button(row, text="✕", bg=CARD, fg=RED, relief="flat", font=("Arial", 8), command=lambda x=i, l=data_list, k=key, m=mode: self.del_item(l, x, k, m)).pack(side="right", padx=8)

    def toggle_section(self, section, label):
        self.collapsed[section] = not self.collapsed[section]
        label.config(text=" ▽" if self.collapsed[section] else " △")
        frame = self.list_frames.get(section)
        if self.collapsed[section]: frame.pack_forget()
        else:
            frame.pack(fill="x")
            m, d = ("steam", self.games) if section == "games" else ("web", self.links)
            self.update_list_ui(section, d, m)
        self.save_settings()

    def move_item(self, l, i, d, key, mode):
        ni = i + d
        if 0 <= ni < len(l): l[i], l[ni] = l[ni], l[i]; self.save_settings(); self.update_list_ui(key, l, mode)

    def cycle_item_color(self, l, idx, key, mode):
        cur = l[idx].get("color", CYAN)
        l[idx]["color"] = NEONS[(NEONS.index(cur) + 1) % len(NEONS)]
        self.save_settings(); self.update_list_ui(key, l, mode)

    def del_item(self, l, i, key, mode): l.pop(i); self.save_settings(); self.update_list_ui(key, l, mode)

    def add_game(self):
        aid = self.ent_val.get().strip()
        if aid.isdigit():
            def fetch():
                try:
                    r = requests.get(f"https://store.steampowered.com/api/appdetails?appids={aid}", timeout=5).json()
                    if r[aid]['success']:
                        self.games.append({"name": r[aid]['data']['name'], "id": aid, "color": CYAN})
                        self.after(0, lambda: [self.save_settings(), self.update_list_ui("games", self.games, "steam")])
                except: pass
            threading.Thread(target=fetch, daemon=True).start()

    def add_link(self):
        u, n = self.ent_val.get().strip(), self.ent_name.get().strip()
        if u and n and n != "NAME":
            if not u.startswith("http"): u = "https://" + u
            self.links.append({"name": n, "url": u, "color": CYAN})
            self.save_settings(); self.update_list_ui("links", self.links, "web")

    def set_lang(self, l): self.lang = l; self.save_settings(); self.init_ui()
    def change_ui(self, scale=None): self.win_scale = scale; self.save_settings(); self.init_ui()
    def cycle_stat_part(self, name, p_idx):
        clrs = self.stats_colors.get(name, [GREEN, CYAN])
        clrs[p_idx] = NEONS[(NEONS.index(clrs[p_idx]) + 1) % len(NEONS)]
        self.stats_colors[name] = clrs; self.save_settings(); self.init_ui()

    def ping_anim(self):
        def run():
            self.after(0, lambda: self.lbl_ping.config(text=LOCALES[self.lang]["ping_run"], fg=YELLOW))
            try:
                res = subprocess.run("ping 8.8.8.8 -n 1", capture_output=True, text=True, shell=True)
                ms = re.search(r"(\d+)ms", res.stdout).group(1)
                self.after(0, lambda: self.lbl_ping.config(text=f"{LOCALES[self.lang]['ping_res']} {ms}ms", fg=GREEN))
            except: self.after(0, lambda: self.lbl_ping.config(text="ERROR", fg=RED))
        threading.Thread(target=run, daemon=True).start()

    def mem_reduct(self):
        ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
        messagebox.showinfo("Mojiz", LOCALES[self.lang]["ram_ok"])

    def clean_temp(self):
        c = 0
        for p in [os.environ.get('TEMP'), 'C:\\Windows\\Temp']:
            if not p: continue
            for root, dirs, files in os.walk(p):
                for f in files:
                    try: os.remove(os.path.join(root, f)); c += 1
                    except: pass
        messagebox.showinfo("Mojiz", f"{LOCALES[self.lang]['temp_ok']} {c}")

    def tool_btn(self, p, t, c, cmd):
        return tk.Button(p, text=t, bg=BG_SEC, fg=c, font=("Consolas", int(9*self.win_scale), "bold"), relief="flat", bd=1, highlightbackground=BORDER, command=cmd)

    def draw_entry(self, p, ph, w):
        e = tk.Entry(p, bg=BG, fg=TEXT, insertbackground=TEXT, bd=0, font=("Consolas", int(10*self.win_scale)), width=w)
        e.pack(side="left", padx=5); e.insert(0, ph)
        e.bind("<FocusIn>", lambda a: e.delete(0, tk.END) if e.get()==ph else None)
        return e

    def launch(self, item, mode): webbrowser.open(item['url'] if mode=="web" else f"steam://rungameid/{item['id']}")

    def start_threads(self):
        def loop():
            while True:
                try:
                    cpu, ram = psutil.cpu_percent(), psutil.virtual_memory().percent
                    disk = psutil.disk_usage('C:').percent
                    if self.cur_tab == "MAIN" and hasattr(self, 'stats_ui'):
                        for n, v in [("CPU", cpu), ("RAM", ram), ("DISK", disk)]:
                            self.after(0, lambda x=n, y=v: self.upd_pb(x, y))
                    try:
                        requests.get("http://google.com", timeout=2)
                        self.after(0, lambda: self.lbl_net.config(text="   ● MOJIZ ONLINE", fg=GREEN))
                    except: self.after(0, lambda: self.lbl_net.config(text="   ● MOJIZ OFFLINE", fg=RED))
                except: pass
                time.sleep(3)
        threading.Thread(target=loop, daemon=True).start()

    def upd_pb(self, n, v):
        if hasattr(self, 'stats_ui') and n in self.stats_ui:
            self.stats_ui[n][0]['value'] = v
            self.stats_ui[n][1].config(text=f"{int(v)}%")

if __name__ == "__main__":
    MojizV1().mainloop()