import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from analysis import summarize, validate

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
BG, PANEL, FG, MUTED, ACCENT = '#0b0d16', '#171b2b', '#f4f2ff', '#a5acc7', '#ad82ff'

class Hidding:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Hidding — VALORANT companion')
        self.root.geometry('1080x750')
        self.root.minsize(850, 650)
        self.root.configure(bg=BG)
        self.overlay = None
        self.registered = False
        if os.name == 'nt':
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Hidding.Tracker.Desktop')
            self.root.iconbitmap(str(ROOT / 'assets/hidding.ico'))
            self.registered = bool(ctypes.windll.user32.RegisterHotKey(None, 1, 0x4001, 0x57))
            self.root.after(80, self.poll_hotkey)
        self.data = json.loads((ROOT / 'demo.json').read_text(encoding='utf-8'))
        self.source = 'DÉMONSTRATION · données fictives'
        self.draw()
        self.root.protocol('WM_DELETE_WINDOW', self.quit)

    def label(self, parent, text, size=12, color=FG, **kw):
        widget = tk.Label(parent, text=text, font=('Segoe UI', size), bg=parent.cget('bg'), fg=color, **kw)
        return widget

    def button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, bg=PANEL, fg=FG, activebackground=ACCENT,
                         activeforeground=BG, relief='flat', padx=16, pady=10, cursor='hand2')

    def draw(self):
        for w in self.root.winfo_children(): w.destroy()
        top = tk.Frame(self.root, bg=BG); top.pack(fill='x', padx=30, pady=(24,10))
        self.label(top, 'H / HIDDING', 26, ACCENT).pack(side='left')
        self.button(top, 'Overlay · Alt + W', self.toggle_overlay).pack(side='right')
        self.label(self.root, 'Comprendre les performances. Suivre la progression.', 14, MUTED).pack(anchor='w', padx=30)
        self.label(self.root, self.source, 11, ACCENT).pack(anchor='w', padx=30, pady=(16,6))
        self.label(self.root, str(self.data.get('player','Joueur'))[:80], 22).pack(anchor='w', padx=30)
        s = summarize(self.data)
        cards = tk.Frame(self.root, bg=BG); cards.pack(fill='x', padx=30, pady=18)
        for title, value in [('K/D',f"{s['kd']:.2f}"),('ACS',f"{s['acs']:.0f}"),('DÉGÂTS / ROUND',f"{s['adr']:.0f}"),('HEADSHOTS',f"{s['hs']:.1f}%" if s['hs'] is not None else '—')]:
            card=tk.Frame(cards,bg=PANEL);card.pack(side='left',expand=True,fill='both',padx=4)
            self.label(card,title,10,MUTED).pack(pady=(12,4));self.label(card,value,25).pack(pady=(0,12))
        self.label(self.root, 'OBSERVATIONS · 10 DERNIÈRES PARTIES', 12, ACCENT).pack(anchor='w',padx=30)
        for signal in s['signals']:
            self.label(self.root, '• '+signal, 11, MUTED, wraplength=980, justify='left').pack(anchor='w',padx=30,pady=3)
        table=tk.Frame(self.root,bg=PANEL);table.pack(fill='both',expand=True,padx=30,pady=15)
        self.label(table,'CARTE / AGENT                         K / D / A                 ACS             RÉSULTAT',10,MUTED).pack(anchor='w',padx=15,pady=8)
        canvas=tk.Canvas(table,bg=PANEL,highlightthickness=0);scroll=tk.Scrollbar(table,command=canvas.yview)
        scroll.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True);canvas.configure(yscrollcommand=scroll.set)
        rows=tk.Frame(canvas,bg=PANEL);canvas.create_window((0,0),window=rows,anchor='nw')
        for m in self.data['matches'][:10]:
            text=f"{str(m.get('map','—'))[:20]} / {str(m.get('agent','—'))[:20]}     ·     {m['kills']:g}/{m['deaths']:g}/{m['assists']:g}     ·     ACS {m['score']/m['rounds']:.0f}     ·     {'Victoire' if m.get('result')=='win' else 'Défaite' if m.get('result')=='loss' else '—'}"
            self.label(rows,text,11).pack(anchor='w',padx=15,pady=5)
        rows.update_idletasks();canvas.configure(scrollregion=canvas.bbox('all'))
        bottom=tk.Frame(self.root,bg=BG);bottom.pack(fill='x',padx=30,pady=(0,20))
        self.button(bottom,'Importer un historique JSON',self.import_data).pack(side='left')
        self.button(bottom,'Revenir à la démo',self.demo).pack(side='left',padx=8)
        status='Alt + W actif' if self.registered else 'Utilise le bouton overlay (raccourci indisponible)'
        self.label(bottom,status,10,MUTED).pack(side='right')

    def demo(self):
        self.data=json.loads((ROOT/'demo.json').read_text(encoding='utf-8'));self.source='DÉMONSTRATION · données fictives';self.refresh()

    def import_data(self):
        path=filedialog.askopenfilename(filetypes=[('Historique JSON','*.json')])
        if not path:return
        try:
            if Path(path).stat().st_size>2_000_000:raise ValueError('Fichier trop volumineux (2 Mo maximum).')
            data=validate(json.loads(Path(path).read_text(encoding='utf-8')))
        except (ValueError,OSError) as exc:
            messagebox.showerror('Import impossible',str(exc));return
        self.data=data;self.source='IMPORT LOCAL · source non vérifiée';self.refresh()

    def refresh(self):
        if self.overlay:self.overlay.destroy();self.overlay=None
        self.draw()

    def toggle_overlay(self):
        if self.overlay:self.overlay.destroy();self.overlay=None;return
        w=tk.Toplevel(self.root);self.overlay=w;w.title('Hidding Overlay');w.configure(bg=BG)
        w.overrideredirect(True);w.attributes('-topmost',True);w.attributes('-alpha',0.95)
        w.geometry('460x350+40+100')
        if os.name=='nt':w.iconbitmap(str(ROOT/'assets/hidding.ico'))
        header=self.label(w,'HIDDING    ·    glisser pour déplacer',15,ACCENT);header.pack(fill='x',padx=18,pady=12)
        header.bind('<Button-1>',lambda e:setattr(self,'drag',(e.x_root-w.winfo_x(),e.y_root-w.winfo_y())))
        header.bind('<B1-Motion>',lambda e:w.geometry(f'+{e.x_root-self.drag[0]}+{e.y_root-self.drag[1]}'))
        self.label(w,self.source,10,ACCENT).pack(anchor='w',padx=18)
        s=summarize(self.data)
        self.label(w,f"K/D {s['kd']:.2f}    ACS {s['acs']:.0f}    ADR {s['adr']:.0f}",17).pack(pady=12)
        for signal in s['signals']:self.label(w,signal,10,MUTED,wraplength=420,justify='left').pack(anchor='w',padx=18,pady=4)
        self.button(w,'Fermer · Alt + W',self.toggle_overlay).pack(side='bottom',pady=12)
        w.bind('<Escape>',lambda e:self.toggle_overlay())

    def poll_hotkey(self):
        msg=wintypes.MSG()
        while ctypes.windll.user32.PeekMessageW(ctypes.byref(msg),None,0x0312,0x0312,1):
            if msg.wParam==1:self.toggle_overlay()
        self.root.after(80,self.poll_hotkey)

    def quit(self):
        if self.registered:ctypes.windll.user32.UnregisterHotKey(None,1)
        self.root.destroy()

if __name__=='__main__':
    Hidding().root.mainloop()
