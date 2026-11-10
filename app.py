"""Chạy: python app.py. Chỉ sử dụng thư viện chuẩn Python."""
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone
from engine import best_move, other, result, winning_line
from storage import Store
from i18n import TEXT

BG, PANEL, INK, MUTED, ACCENT = '#080e1b', '#101c30', '#edf6ff', '#8fa5c0', '#54d9ff'


FONT = 'Segoe UI'
FIELD = '#0b1426'
LINE = '#243550'
PINK = '#ff79bb'


def rounded(canvas, x1, y1, x2, y2, radius=14, **kwargs):
    radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    points = [x1+radius,y1, x2-radius,y1, x2,y1, x2,y1+radius,
              x2,y2-radius, x2,y2, x2-radius,y2, x1+radius,y2,
              x1,y2, x1,y2-radius, x1,y1+radius, x1,y1]
    return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)


def neon_symbol(canvas, symbol, cx, cy, size, color, width=5):
    if not symbol:
        return
    shades = ('#112e48', '#174664', color) if color == ACCENT else ('#321c3d', '#61304f', color)
    for shade, extra in zip(shades, (10, 4, 0)):
        if symbol == 'X':
            canvas.create_line(cx-size, cy-size, cx+size, cy+size,
                               fill=shade, width=width+extra, capstyle='round')
            canvas.create_line(cx-size, cy+size, cx+size, cy-size,
                               fill=shade, width=width+extra, capstyle='round')
        else:
            canvas.create_oval(cx-size, cy-size, cx+size, cy+size,
                               outline=shade, width=width+extra)


class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command, primary=False, width=210, height=46):
        super().__init__(parent, width=width, height=height,
                         bg=parent.cget('bg'), highlightthickness=0,
                         takefocus=True, cursor='hand2')
        self.caption, self.action, self.primary = text, command, primary
        self.hover = False
        self.bind('<Configure>', self.draw)
        self.bind('<Enter>', lambda e: self.highlight(True))
        self.bind('<Leave>', lambda e: self.highlight(False))
        self.bind('<FocusIn>', lambda e: self.highlight(True))
        self.bind('<FocusOut>', lambda e: self.highlight(False))
        self.bind('<ButtonRelease-1>', lambda e: self.invoke())
        self.bind('<Return>', lambda e: self.invoke())
        self.bind('<space>', lambda e: self.invoke())

    def highlight(self, active):
        self.hover = active
        self.draw()

    def draw(self, _event=None):
        self.delete('all')
        w, h = self.winfo_width(), self.winfo_height()
        fill = ('#8ae8ff' if self.hover else ACCENT) if self.primary else ('#19324a' if self.hover else '#14233a')
        border = ACCENT if self.primary or self.hover else LINE
        rounded(self, 2, 2, w-2, h-2, 12, fill=fill, outline=border, width=1)
        self.create_text(w/2, h/2, text=self.caption,
                         fill=BG if self.primary else INK, font=(FONT, 11, 'bold'))

    def invoke(self):
        return self.action()


class NeonCell(tk.Canvas):
    def __init__(self, parent, symbol, command, disabled=False, winner=False):
        super().__init__(parent, bg=BG, highlightthickness=0,
                         takefocus=not disabled, cursor='arrow' if disabled else 'hand2')
        self.symbol, self.action = symbol, command
        self.disabled, self.winner, self.hover = disabled, winner, False
        self.bind('<Configure>', self.draw)
        self.bind('<Enter>', lambda e: self.highlight(True))
        self.bind('<Leave>', lambda e: self.highlight(False))
        self.bind('<FocusIn>', lambda e: self.highlight(True))
        self.bind('<FocusOut>', lambda e: self.highlight(False))
        self.bind('<ButtonRelease-1>', lambda e: self.invoke())
        self.bind('<Return>', lambda e: self.invoke())
        self.bind('<space>', lambda e: self.invoke())

    def highlight(self, active):
        self.hover = active and not self.disabled
        self.draw()

    def draw(self, _event=None):
        self.delete('all')
        w, h = self.winfo_width(), self.winfo_height()
        fill = '#103346' if self.winner else '#13293e' if self.hover else PANEL
        rounded(self, 3, 3, w-3, h-3, 15, fill=fill,
                outline=ACCENT if self.winner or self.hover else LINE,
                width=2 if self.winner else 1)
        neon_symbol(self, self.symbol, w/2, h/2, min(w,h)*0.22,
                    ACCENT if self.symbol == 'X' else PINK, 5)

    def invoke(self):
        if not self.disabled:
            return self.action()


class App(tk.Tk):
    def u(self, vietnamese, english):
        return vietnamese if self.lang == 'vi' else english

    def draw_mode(self, canvas, mode):
        canvas.delete('all')
        w = canvas.winfo_width()
        neon_symbol(canvas, 'X', w/2-40, 40, 21, ACCENT, 4)
        neon_symbol(canvas, 'O', w/2+40, 40, 21, PINK, 4)

    def draw_hero(self, canvas):
        canvas.delete('all')
        w, h = canvas.winfo_width(), canvas.winfo_height()
        size = min(w-30, h-18, 270)
        if size < 20:
            return
        x, y = (w-size)/2, (h-size)/2
        rounded(canvas, x-8, y-8, x+size+8, y+size+8, 24,
                fill='#0b1528', outline='#172d45', width=1)
        step = size/3
        for i in (1, 2):
            for shade, width in [('#102337', 9), ('#204962', 3), ('#3b8ca8', 1)]:
                canvas.create_line(x+i*step, y+12, x+i*step, y+size-12,
                                   fill=shade, width=width, capstyle='round')
                canvas.create_line(x+12, y+i*step, x+size-12, y+i*step,
                                   fill=shade, width=width, capstyle='round')
        for row, col, symbol in [(0, 0, 'X'), (0, 2, 'O'), (1, 1, 'O'), (2, 0, 'X'), (2, 2, 'X')]:
            neon_symbol(canvas, symbol, x+(col+0.5)*step, y+(row+0.5)*step,
                        step*0.22, ACCENT if symbol == 'X' else PINK, 4)


    def __init__(self, db_path=None):
        super().__init__()
        width = min(1160, max(980, self.winfo_screenwidth()-80))
        height = min(820, max(680, self.winfo_screenheight()-90))
        self.geometry(f'{width}x{height}')
        self.minsize(980, 680)
        self.configure(bg=BG)
        folder = Path(os.environ.get('LOCALAPPDATA', Path.home()/'.local/share'))/'Caro3x3Minimax'
        self.store = Store(db_path or folder/'caro.sqlite3')
        self.lang, self.user, self.screen = 'vi', None, 'auth'
        self.human, self.mode, self.turn = 'X', 'ai', 'X'
        self.board, self.finished, self.pending = ['']*9, False, None
        self.scores = {'X': 0, 'O': 0, 'draw': 0}
        self.auth_tab = 'login'
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('Neon.TCombobox', fieldbackground=FIELD,
                             background=PANEL, foreground=INK, arrowcolor=ACCENT,
                             bordercolor=LINE, lightcolor=LINE, darkcolor=LINE, padding=7)
        self.style.map('Neon.TCombobox', fieldbackground=[('readonly', FIELD)],
                       foreground=[('readonly', INK)], selectbackground=[('readonly', FIELD)],
                       selectforeground=[('readonly', INK)])
        self.option_add('*TCombobox*Listbox.background', FIELD)
        self.option_add('*TCombobox*Listbox.foreground', INK)
        self.option_add('*TCombobox*Listbox.selectBackground', '#254960')
        self.style.configure('Treeview', font=(FONT, 11), rowheight=40,
                             background=PANEL, foreground=INK, fieldbackground=PANEL,
                             borderwidth=0)
        self.style.map('Treeview', background=[('selected', '#20516a')],
                       foreground=[('selected', INK)])
        self.style.configure('Treeview.Heading', font=(FONT, 11, 'bold'),
                             background='#192b42', foreground=ACCENT, relief='flat', padding=10)
        self.style.configure('Vertical.TScrollbar', background='#29435d',
                             troughcolor=FIELD, arrowcolor=ACCENT, bordercolor=BG)
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.render()

    def t(self, key, **kwargs):
        if key == 'pvp':
            return self.u('Người với người', 'Player vs Player')
        return TEXT[self.lang][key].format(**kwargs)

    def label(self, parent, text, size=12, color=INK, bold=False, **kwargs):
        return tk.Label(parent, text=text, bg=parent.cget('bg'), fg=color,
                        font=(FONT, size, 'bold' if bold else 'normal'), **kwargs)

    def button(self, parent, text, command, primary=False, **kwargs):
        width = kwargs.pop('width', 22)*8+28
        return NeonButton(parent, text, command, primary, width=width,
                          height=kwargs.pop('height', 46))

    def cancel_ai(self):
        if self.pending is not None:
            self.after_cancel(self.pending)
            self.pending = None

    def render(self):
        self.cancel_ai()
        for child in self.winfo_children():
            child.destroy()
        self.title(self.t('title')+' • Minimax')
        header = tk.Frame(self, bg=BG)
        header.pack(fill='x', padx=32, pady=(20, 10))
        logo = tk.Canvas(header, bg=BG, width=62, height=46, highlightthickness=0)
        logo.pack(side='left', padx=(0, 12))
        neon_symbol(logo, 'X', 17, 22, 10, ACCENT, 3)
        neon_symbol(logo, 'O', 45, 22, 10, PINK, 3)
        brand = tk.Frame(header, bg=BG)
        brand.pack(side='left')
        self.label(brand, self.t('title'), 18, bold=True).pack(anchor='w')
        self.label(brand, self.t('subtitle'), 9, MUTED).pack(anchor='w')
        self.language_var = tk.StringVar(master=self, value='Tiếng Việt' if self.lang == 'vi' else 'English')
        choice = ttk.Combobox(header, textvariable=self.language_var, state='readonly',
                              values=('Tiếng Việt', 'English'), width=13,
                              style='Neon.TCombobox', font=(FONT, 10))
        choice.pack(side='right', pady=6)
        choice.bind('<<ComboboxSelected>>', self.change_language)
        if self.user:
            self.label(header, self.user, 10, MUTED).pack(side='right', padx=22)
        tk.Frame(self, bg=LINE, height=1).pack(fill='x', padx=32)
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill='both', expand=True, padx=32, pady=(18, 12))
        getattr(self, 'show_'+self.screen)()

    def change_language(self, _event=None):
        # Giữ nội dung đang nhập và trạng thái ván khi đổi ngôn ngữ.
        draft = None
        if self.screen == 'auth':
            draft = (self.name_entry.get(), self.pass_entry.get(),
                     self.confirm_entry.get() if self.auth_tab == 'register' else '')
        self.lang = 'vi' if self.language_var.get() == 'Tiếng Việt' else 'en'
        if self.user:
            self.store.language(self.user, self.lang)
        self.render()
        if draft:
            self.name_entry.insert(0,draft[0]); self.pass_entry.insert(0,draft[1])
            if self.auth_tab == 'register':
                self.confirm_entry.insert(0,draft[2])

    def show_auth(self):
        shell = tk.Frame(self.body, bg=BG)
        shell.pack(fill='both', expand=True)
        shell.columnconfigure(0, weight=1, uniform='auth')
        shell.columnconfigure(1, weight=1, uniform='auth')
        shell.rowconfigure(0, weight=1)
        left = tk.Frame(shell, bg=BG)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 34))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(3, weight=1)
        self.label(left, self.u('TƯ DUY CHIẾN THUẬT', 'THINK. PLAY. REPEAT.'),
                   10, ACCENT, bold=True).grid(row=0, column=0, sticky='w', pady=(10, 10))
        self.label(left, self.u('Mỗi nước đi,\nmột chiến lược.', 'Every move.\nA new strategy.'),
                   29, bold=True, justify='left').grid(row=1, column=0, sticky='w')
        self.label(left, self.u('Thử sức cùng AI hoặc thách đấu bạn bè\ntrên bàn cờ neon của riêng bạn.',
                               'Challenge the AI or a friend\non your own neon board.'),
                   11, MUTED, justify='left').grid(row=2, column=0, sticky='w', pady=(12, 0))
        hero = tk.Canvas(left, bg=BG, highlightthickness=0, width=370, height=290)
        hero.grid(row=3, column=0, sticky='nsew', pady=8)
        hero.bind('<Configure>', lambda event: self.draw_hero(hero))
        features = tk.Frame(left, bg=BG)
        features.grid(row=4, column=0, sticky='w', pady=(0, 16))
        for text in ('MINIMAX', self.u('2 CHẾ ĐỘ', '2 MODES'), 'VI / EN'):
            self.label(features, text, 9, MUTED, padx=12, pady=7,
                       highlightbackground=LINE, highlightthickness=1).pack(side='left', padx=(0, 8))
        card = tk.Frame(shell, bg=PANEL, padx=28, pady=22,
                        highlightbackground=LINE, highlightthickness=1)
        card.grid(row=0, column=1, sticky='ew')
        tabs = tk.Frame(card, bg=PANEL)
        tabs.pack(fill='x', pady=(0, 16))
        for col, key in enumerate(('login', 'register')):
            tabs.columnconfigure(col, weight=1, uniform='tabs')
            self.button(tabs, self.t(key), lambda k=key: self.auth_mode(k),
                        self.auth_tab == key, width=16, height=40).grid(row=0, column=col, sticky='ew', padx=(0, 8) if col == 0 else (0, 0))
        title = self.u('Chào mừng trở lại', 'Welcome back') if self.auth_tab == 'login' else self.u('Tạo tài khoản', 'Create your account')
        subtitle = self.u('Đăng nhập để tiếp tục ván chơi của bạn.', 'Sign in and get ready to play.') if self.auth_tab == 'login' else self.u('Bắt đầu hành trình với những nước đi mới.', 'Your next great move starts here.')
        self.label(card, title, 23, bold=True).pack(anchor='w')
        self.label(card, subtitle, 10, MUTED, wraplength=360, justify='left').pack(anchor='w', pady=(4, 8))
        password_entries = []

        def field(key, secret=False):
            self.label(card, self.t(key), 10, MUTED).pack(anchor='w', pady=(8, 5))
            frame = tk.Frame(card, bg=FIELD, padx=12, pady=8,
                             highlightbackground=LINE, highlightthickness=1)
            frame.pack(fill='x')
            entry = tk.Entry(frame, font=(FONT, 12), width=25, relief='flat', bd=0, highlightthickness=0,
                             bg=FIELD, fg=INK, insertbackground=ACCENT,
                             selectbackground='#24516a', selectforeground=INK,
                             show='*' if secret else '')
            entry.pack(fill='x', expand=True)
            entry.bind('<FocusIn>', lambda event: frame.configure(highlightbackground=ACCENT))
            entry.bind('<FocusOut>', lambda event: frame.configure(highlightbackground=LINE))
            entry.bind('<Return>', lambda event: self.submit_auth())
            if secret:
                password_entries.append(entry)
            return entry

        self.name_entry = field('username')
        self.pass_entry = field('password', True)
        self.confirm_entry = field('confirm', True) if self.auth_tab == 'register' else None
        show_password = tk.BooleanVar(master=card, value=False)
        self.show_password = show_password

        def toggle(*_args):
            mask = '' if show_password.get() else '*'
            for entry in password_entries:
                if entry.winfo_exists():
                    entry.configure(show=mask)

        self.password_check = tk.Checkbutton(card, text=self.t('show_password'),
                       variable=show_password, onvalue=True, offvalue=False, command=toggle,
                       bg=PANEL, fg=MUTED, selectcolor=FIELD, activebackground=PANEL,
                       activeforeground=INK, font=(FONT, 10), cursor='hand2', bd=0, highlightthickness=0)
        self.password_check.pack(anchor='w', pady=(8, 0))
        for entry in password_entries:
            entry.bind('<FocusIn>', toggle, add='+')
        toggle()
        self.auth_message = self.label(card, '', 10, ACCENT, wraplength=360,
                                       height=2, anchor='w', justify='left')
        self.auth_message.pack(fill='x', pady=(2, 4))
        self.button(card, self.t(self.auth_tab), self.submit_auth, True).pack(fill='x')
        self.label(card, self.t('local'), 9, MUTED, wraplength=360,
                   justify='center').pack(fill='x', pady=(14, 0))
        self.name_entry.focus_set()

    def auth_mode(self, mode):
        self.auth_tab=mode
        self.render()

    def submit_auth(self):
        name,password=self.name_entry.get(),self.pass_entry.get()
        if self.auth_tab == 'register':
            if password != self.confirm_entry.get():
                error='mismatch'
            else:
                error=self.store.register(name,password)
            if error:
                self.auth_message.configure(text=self.t(error),fg='#ff9f9f')
                return
            self.store.language(name.strip(),self.lang)
            self.auth_tab='login'; self.render()
            self.name_entry.insert(0,name.strip())
            self.auth_message.configure(text=self.t('registered'))
        else:
            account=self.store.login(name,password)
            if not account:
                self.auth_message.configure(text=self.t('bad_login'),fg='#ff9f9f')
                return
            self.user,self.lang=account
            self.screen='menu';self.render()

    def show_menu(self):
        content = tk.Frame(self.body, bg=BG)
        content.pack(fill='both', expand=True, padx=28, pady=20)
        self.label(content, self.t('welcome', name=self.user), 25, bold=True).pack(anchor='w')
        self.label(content, self.t('choose'), 12, MUTED).pack(anchor='w', pady=(6, 26))
        cards = tk.Frame(content, bg=BG)
        cards.pack(fill='x')
        for col, mode in enumerate(('ai', 'pvp')):
            cards.columnconfigure(col, weight=1, uniform='modes')
            card = tk.Frame(cards, bg=PANEL, padx=24, pady=24,
                            highlightbackground=LINE, highlightthickness=1)
            card.grid(row=0, column=col, sticky='nsew', padx=(0, 16) if col == 0 else (0, 0))
            art = tk.Canvas(card, bg=PANEL, height=80, highlightthickness=0)
            art.pack(fill='x', pady=(0, 12))
            art.bind('<Configure>', lambda event, c=art, m=mode: self.draw_mode(c, m))
            self.label(card, self.t(mode), 18, bold=True).pack(anchor='w')
            text = self.u('Thử thách chiến thuật cùng Minimax.', 'Challenge the Minimax AI.') if mode == 'ai' else self.u('Hai người, một bàn cờ, cùng so tài.', 'Two players. One board. Your challenge.')
            self.label(card, text, 10, MUTED, wraplength=350, justify='left').pack(anchor='w', pady=(6, 20))
            self.button(card, self.u('Bắt đầu chơi', 'Start playing'),
                        lambda m=mode: self.start(m), mode == 'ai').pack(fill='x')
        controls = tk.Frame(content, bg=BG)
        controls.pack(fill='x', pady=24)
        for key, action in [('settings', lambda: self.go('settings')),
                            ('history', lambda: self.go('history')), ('logout', self.logout)]:
            self.button(controls, self.t(key), action, width=16).pack(side='left', padx=(0, 12))
        self.label(content, self.t('rule'), 10, MUTED, wraplength=850, justify='left').pack(anchor='w', pady=8)

    def show_settings(self):
        card = tk.Frame(self.body, bg=PANEL, padx=38, pady=30,
                        highlightbackground=LINE, highlightthickness=1)
        card.pack(expand=True)
        self.label(card, self.t('settings'), 25, bold=True).pack(anchor='w', pady=(0, 20))
        self.label(card, self.t('language'), 11, MUTED).pack(anchor='w')
        self.label(card, self.u('Dùng bộ chọn ở góc trên bên phải.', 'Use the selector in the top-right corner.'),
                   11).pack(anchor='w', pady=(6, 24))
        self.label(card, self.t('symbol'), 11, MUTED).pack(anchor='w', pady=(0, 12))
        row = tk.Frame(card, bg=PANEL)
        row.pack(fill='x')
        for symbol in ('X', 'O'):
            self.button(row, symbol, lambda s=symbol: self.set_symbol(s),
                        self.human == symbol, width=12).pack(side='left', padx=(0, 12))
        self.label(card, self.t('saved'), 10, ACCENT).pack(anchor='w', pady=24)
        self.button(card, self.t('back'), lambda: self.go('menu')).pack(fill='x')

    def set_symbol(self, symbol):
        self.human=symbol;self.render()

    def go(self, screen):
        if self.screen=='game' and not self.finished and any(self.board):
            if not messagebox.askyesno(self.t('notice'),self.t('leave'),parent=self):
                return
        self.screen=screen;self.render()

    def logout(self):
        self.user=None;self.screen='auth';self.auth_tab='login'
        self.scores={'X':0,'O':0,'draw':0};self.render()

    def start(self, mode):
        self.mode=mode;self.scores={'X':0,'O':0,'draw':0}
        self.reset()

    def reset(self):
        self.cancel_ai();self.board=['']*9;self.turn='X';self.finished=False
        self.screen='game';self.render()

    def player_name(self, symbol):
        if self.mode=='pvp':return symbol
        return f"{self.t('you') if symbol==self.human else self.t('computer')} ({symbol})"

    def show_game(self):
        outcome = result(self.board)
        ai_turn = self.mode == 'ai' and self.turn != self.human and not outcome
        top = tk.Frame(self.body, bg=BG)
        top.pack(fill='x')
        self.label(top, self.t(self.mode), 20, bold=True).pack(side='left')
        self.label(top, self.u('BÀN CỜ 3 × 3', '3 × 3 BOARD'), 10, MUTED).pack(side='right')
        if outcome == 'draw':
            status = self.t('draw')
        elif outcome:
            status = self.t('win', player=self.player_name(outcome))
        elif ai_turn:
            status = self.t('thinking')
        else:
            status = self.t('turn', player=self.player_name(self.turn))
        self.label(self.body, status, 12, ACCENT, bold=True).pack(pady=(6, 8))
        score_row = tk.Frame(self.body, bg=BG)
        score_row.pack()
        for key, title, color in [('X', 'X', ACCENT), ('draw', self.t('draw_short'), MUTED), ('O', 'O', PINK)]:
            box = tk.Frame(score_row, bg=PANEL, padx=26, pady=5,
                           highlightbackground=LINE, highlightthickness=1)
            box.pack(side='left', padx=5)
            self.label(box, title, 9, color, bold=True).pack()
            self.label(box, str(self.scores[key]), 17, INK, bold=True).pack()
        size = min(396, max(300, self.winfo_height()-365))
        board_frame = tk.Frame(self.body, bg=BG, width=size, height=size)
        board_frame.pack(pady=12)
        board_frame.pack_propagate(False)
        board_frame.grid_propagate(False)
        for r in range(3):
            board_frame.rowconfigure(r, weight=1, uniform='board')
            board_frame.columnconfigure(r, weight=1, uniform='board')
        win = winning_line(self.board)
        self.cells = []
        for i, value in enumerate(self.board):
            cell = NeonCell(board_frame, value, lambda index=i: self.play(index),
                            disabled=bool(value or outcome or ai_turn), winner=i in win)
            cell.grid(row=i//3, column=i%3, sticky='nsew', padx=3, pady=3)
            self.cells.append(cell)
        controls = tk.Frame(self.body, bg=BG)
        controls.pack()
        self.button(controls, self.t('new'), self.new_game, True, width=16).pack(side='left', padx=6)
        self.button(controls, self.t('back'), lambda: self.go('menu'), width=16).pack(side='left', padx=6)
        self.label(self.body, self.t('rule'), 9, MUTED, wraplength=800).pack(pady=(10, 0))
        if ai_turn:
            self.pending = self.after(220, self.ai_move)

    def new_game(self):
        if any(self.board) and not self.finished:
            if not messagebox.askyesno(self.t('notice'),self.t('leave'),parent=self):return
        self.reset()

    def play(self, index):
        if self.finished or self.board[index] or (self.mode=='ai' and self.turn!=self.human):return
        self.apply_move(index)

    def ai_move(self):
        self.pending=None
        if self.screen!='game' or self.finished or self.mode!='ai' or self.turn==self.human:return
        index=best_move(self.board,other(self.human))
        if index is not None:self.apply_move(index)

    def apply_move(self, index):
        self.board[index]=self.turn
        outcome=result(self.board)
        if outcome and not self.finished:
            self.finished=True;self.scores[outcome]+=1
            self.store.record(self.user,self.mode,self.human,outcome)
        self.turn=other(self.turn)
        self.render()

    def show_history(self):
        top = tk.Frame(self.body, bg=BG)
        top.pack(fill='x', pady=(4, 18))
        self.label(top, self.t('history'), 24, bold=True).pack(side='left')
        self.button(top, self.t('back'), lambda: self.go('menu'), width=16).pack(side='right')
        container = tk.Frame(self.body, bg=PANEL, padx=1, pady=1,
                             highlightbackground=LINE, highlightthickness=1)
        container.pack(fill='both', expand=True)
        tree = ttk.Treeview(container, columns=('date', 'mode', 'outcome'), show='headings')
        for key, width in [('date', 210), ('mode', 330), ('outcome', 180)]:
            tree.heading(key, text=self.t(key))
            tree.column(key, width=width, minwidth=120, anchor='w')
        scroll = ttk.Scrollbar(container, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)
        rows = self.store.history(self.user)
        for when, mode, human, outcome in rows:
            local = datetime.strptime(when, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).astimezone().strftime('%d/%m/%Y %H:%M')
            key = 'draw_short' if outcome == 'draw' else ('won' if outcome == human else 'lost') if mode == 'ai' else 'x_win' if outcome == 'X' else 'o_win'
            tree.insert('', 'end', values=(local, self.t(mode), self.t(key)))
        self.label(self.body, self.t('history_note') if rows else self.t('empty'),
                   10, MUTED).pack(pady=14)

    def close(self):
        if self.screen=='game' and not self.finished and any(self.board):
            if not messagebox.askyesno(self.t('notice'),self.t('leave'),parent=self):return
        self.cancel_ai();self.store.close();self.destroy()

if __name__ == '__main__':
    App().mainloop()
