"""Hidding desktop prototype. No network or game-memory access."""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from analysis import summarize, validate
from copy import deepcopy

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
BG = '#090b13'
PANEL = '#131726'
RAISED = '#1c2135'
EDGE = '#282d44'
FG = '#f1f0fa'
MUTED = '#9198b2'
ACCENT = '#aa87ff'
GREEN = '#57d7b0'
RED = '#ee899e'


def build_demo_lobby(base):
    """Synthetic profiles only; no real identity or inferred consent."""
    identities = [('Oreo#DEMO','Sage','Diamant 2'), ('Nova#DEMO','Jett','Diamant 1'),
                  ('Echo#DEMO','Sova','Platine 3'), ('Lumen#DEMO','Omen','Diamant 2'),
                  ('Profil privé','Raze','—')]
    profiles=[]
    for i,(name,agent,rank) in enumerate(identities):
        history=deepcopy(base['matches'][:10])
        for j,m in enumerate(history):
            m['agent']=agent
            if i==1:
                m.update(kills=32+j%4,deaths=11+j%3,score=m['rounds']*(325+j%4*8),
                         damage=m['rounds']*(205+j%4*5),headshots=32,bodyshots=42,legshots=4,result='win' if j<8 else 'loss')
            elif i==2:
                m.update(kills=15+j%4,deaths=18+j%3,score=m['rounds']*(205+j%3*10),damage=m['rounds']*137)
            elif i==3:
                m.update(score=m['rounds']*(310 if j<5 else 205),kills=27 if j<5 else 17,deaths=16)
        if i==2:history=history[:6]  # Demonstrate incomplete data.
        profiles.append(dict(player=name,agent=agent,rank=rank,matches=history,
                             consent=i in (1,2,3),self=i==0))
    return profiles


def lobby_summary(profile):
    """Never expose stats in the simulated UI without simulated consent."""
    return summarize(profile) if profile.get('consent') else None


def observation_label(summary):
    if summary is None:return 'Partage non autorisé'
    if summary['count']<10:return f"Historique incomplet · {summary['count']}/10"
    if any(x.startswith('Domination régulière') for x in summary['signals']):return 'Domination régulière'
    if any(x.startswith('Hausse d’ACS') for x in summary['signals']):return 'Hausse de performances'
    return 'Aucun seuil atteint'


def rounded(canvas, x1, y1, x2, y2, r=16, **kwargs):
    return canvas.create_polygon(
        x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,x2,y2,
        x2-r,y2,x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1,
        smooth=True, splinesteps=24, **kwargs)


class Surface(tk.Canvas):
    def __init__(self, parent, height=160, **kwargs):
        super().__init__(parent, bg=BG, highlightthickness=0, height=height, **kwargs)
        self.inner = tk.Frame(self, bg=PANEL)
        self.window = self.create_window(16, 12, window=self.inner, anchor='nw')
        self.bind('<Configure>', self.resize)

    def resize(self, event):
        self.delete('surface')
        rounded(self, 1, 1, event.width-1, event.height-1, fill=PANEL, outline=EDGE, tags='surface')
        self.tag_lower('surface')
        self.itemconfigure(self.window, width=max(1,event.width-32), height=max(1,event.height-24))


class StatCard(tk.Canvas):
    def __init__(self, parent, title, value, subtitle, color, **kwargs):
        super().__init__(parent, height=124, bg=BG, highlightthickness=0, **kwargs)
        self.info = title, value, subtitle, color
        self.bind('<Configure>', self.render)

    def render(self, event):
        self.delete('all')
        title,value,subtitle,color = self.info
        w,h = event.width,event.height
        rounded(self,1,1,w-1,h-1,fill=PANEL,outline=EDGE)
        self.create_rectangle(18,20,21,38,fill=color,outline='')
        self.create_text(32,29,text=title,fill=MUTED,font=('Segoe UI',10),anchor='w')
        self.create_text(20,69,text=value,fill=FG,font=('Segoe UI',28,'bold'),anchor='w')
        self.create_text(20,104,text=subtitle,fill=MUTED,font=('Segoe UI',9),anchor='w')


class Hidding:
    def __init__(self):
        if os.name == 'nt':
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Hidding.Tracker.Desktop')
        self.root = tk.Tk()
        self.root.title('Hidding — Match insights')
        self.root.geometry('1260x860')
        self.root.minsize(1100,800)
        self.root.configure(bg=BG)
        self.root.option_add('*Font', ('Segoe UI',10))
        self.logo = tk.PhotoImage(file=str(ROOT/'assets/hidding.png')).subsample(4,4)
        self.root.iconphoto(True,self.logo)
        self.overlay = None
        self.overlay_position = '+50+100'
        self.registered = False
        if os.name == 'nt':
            self.root.iconbitmap(str(ROOT/'assets/hidding.ico'))
            self.registered = bool(ctypes.windll.user32.RegisterHotKey(None,1,0x4001,0x57))
            self.root.after(80,self.poll_hotkey)
        self.load_demo()
        self.lobby=build_demo_lobby(self.data)
        self.view='lobby'
        self.simulated_connected=False
        self.setup_table_style()
        self.draw()
        self.root.protocol('WM_DELETE_WINDOW',self.quit)

    def label(self,parent,text,size=11,color=FG,bold=False,**kwargs):
        return tk.Label(parent,text=text,font=('Segoe UI',size,'bold' if bold else 'normal'),
                        bg=parent.cget('bg'),fg=color,**kwargs)

    def button(self,parent,text,command,primary=False):
        base = ACCENT if primary else RAISED
        b = tk.Button(parent,text=text,command=command,bg=base,fg=BG if primary else FG,
                      activebackground='#bea5ff' if primary else '#2a3049',
                      activeforeground=BG if primary else FG,relief='flat',borderwidth=0,
                      padx=16,pady=10,cursor='hand2',font=('Segoe UI',10,'bold'))
        b.bind('<Enter>',lambda e:b.configure(bg='#bea5ff' if primary else '#2a3049'))
        b.bind('<Leave>',lambda e:b.configure(bg=base))
        return b

    def setup_table_style(self):
        style=ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('H.Treeview',background=PANEL,fieldbackground=PANEL,foreground=FG,
                        rowheight=35,borderwidth=0,font=('Segoe UI',10))
        style.configure('H.Treeview.Heading',background=PANEL,foreground=MUTED,
                        relief='flat',font=('Segoe UI',9,'bold'),padding=(10,8))
        style.map('H.Treeview',background=[('selected','#34294f')],foreground=[('selected',FG)])
        style.map('H.Treeview.Heading',background=[('active',RAISED)])
        style.configure('H.Vertical.TScrollbar',background=EDGE,troughcolor=PANEL,
                        bordercolor=PANEL,arrowcolor=MUTED,lightcolor=EDGE,darkcolor=EDGE)

    def load_demo(self):
        self.data=json.loads((ROOT/'demo.json').read_text(encoding='utf-8'))
        self.source='DÉMO · DONNÉES FICTIVES'

    def shell(self):
        for child in self.root.winfo_children():
            if child is not self.overlay:child.destroy()
        self.root.grid_columnconfigure(1,weight=1)
        self.root.grid_rowconfigure(0,weight=1)
        sidebar=tk.Frame(self.root,bg='#0e111d',width=186)
        sidebar.grid(row=0,column=0,sticky='nsew');sidebar.grid_propagate(False)
        self.label(sidebar,'',image=self.logo).pack(pady=(27,8))
        self.label(sidebar,'HIDDING',18,FG,True).pack()
        self.label(sidebar,'VALORANT COMPANION',8,MUTED).pack(pady=(4,25))
        for key,title in [('lobby','Lobby démo'),('overview','Statistiques'),('account','Connexion démo')]:
            self.button(sidebar,title,lambda v=key:self.navigate(v),self.view==key).pack(fill='x',padx=14,pady=4)
        self.label(sidebar,'HISTORIQUE LOCAL',8,MUTED).pack(pady=(22,6))
        self.button(sidebar,'Importer un JSON',self.import_data).pack(fill='x',padx=14,pady=5)
        self.button(sidebar,'Mode démonstration',self.demo).pack(fill='x',padx=14,pady=5)
        foot=tk.Frame(sidebar,bg='#0e111d');foot.pack(side='bottom',fill='x',padx=16,pady=22)
        self.label(foot,'PROTOTYPE  /  0.3',9,ACCENT).pack(anchor='w')
        self.label(foot,'Riot non connecté',9,MUTED).pack(anchor='w',pady=6)
        self.label(foot,'Projet indépendant',9,MUTED).pack(anchor='w')
        main=tk.Frame(self.root,bg=BG)
        main.grid(row=0,column=1,sticky='nsew',padx=26,pady=22)
        return main

    def navigate(self,view):
        self.close_overlay();self.view=view;self.draw()

    def draw(self):
        if self.view=='lobby':return self.draw_lobby()
        if self.view=='account':return self.draw_account()
        main=self.shell()
        s=summarize(self.data)
        main.grid_columnconfigure(0,weight=1);main.grid_rowconfigure(4,weight=1)
        top=tk.Frame(main,bg=BG);top.grid(row=0,column=0,sticky='ew',pady=(0,20))
        left=tk.Frame(top,bg=BG);left.pack(side='left')
        self.label(left,'Vue d’ensemble',24,FG,True).pack(anchor='w')
        self.label(left,'Ton historique, en un regard.',11,MUTED).pack(anchor='w',pady=(4,0))
        self.button(top,'Ouvrir l’overlay    Alt + W',self.toggle_overlay,True).pack(side='right')

        identity=tk.Frame(main,bg=BG);identity.grid(row=1,column=0,sticky='ew',pady=(0,15))
        self.label(identity,str(self.data.get('player','Joueur'))[:42],16,FG,True).pack(side='left')
        self.label(identity,self.source,9,ACCENT,padx=12,pady=6).pack(side='right')

        cards=tk.Frame(main,bg=BG);cards.grid(row=2,column=0,sticky='ew',pady=(0,18))
        hs=f"{s['hs']:.1f}%" if s['hs'] is not None else '—'
        stats=[('K / D',f"{s['kd']:.2f}",'Ratio éliminations / morts',ACCENT),
               ('SCORE DE COMBAT',f"{s['acs']:.0f}",'ACS moyen par round','#72b9ff'),
               ('DÉGÂTS / ROUND',f"{s['adr']:.0f}",'Dégâts moyens infligés',GREEN),
               ('HEADSHOTS',hs,'Part des impacts à la tête','#f3b875')]
        for i,values in enumerate(stats):
            cards.grid_columnconfigure(i,weight=1,uniform='stats')
            StatCard(cards,*values).grid(row=0,column=i,sticky='ew',padx=(0,10) if i<3 else 0)

        insights=tk.Frame(main,bg=BG);insights.grid(row=3,column=0,sticky='ew',pady=(0,18))
        insights.grid_columnconfigure(0,weight=3);insights.grid_columnconfigure(1,weight=2)
        graph=Surface(insights,height=220);graph.grid(row=0,column=0,sticky='ew',padx=(0,14))
        self.label(graph.inner,'Dynamique des matchs',12,FG,True).pack(anchor='w')
        self.label(graph.inner,'ACS · du plus ancien au plus récent',9,MUTED).pack(anchor='w',pady=(3,5))
        plot=tk.Canvas(graph.inner,bg=PANEL,highlightthickness=0)
        plot.pack(fill='both',expand=True)
        plot.bind('<Configure>',lambda e:self.draw_chart(plot))
        observation=Surface(insights,height=220);observation.grid(row=0,column=1,sticky='ew')
        self.label(observation.inner,'Lecture des performances',12,FG,True).pack(anchor='w')
        self.label(observation.inner,f"{s['count']}/10 matchs analysés",9,ACCENT).pack(anchor='w',pady=(5,8))
        meaningful=[x for x in s['signals'] if not x.startswith('Ces observations')]
        note=self.label(observation.inner,'\n\n'.join(meaningful),10,MUTED,justify='left',anchor='nw')
        note.pack(fill='both',expand=True)
        observation.inner.bind('<Configure>',lambda e:note.configure(wraplength=max(100,e.width)))

        history=Surface(main,height=300);history.grid(row=4,column=0,sticky='nsew')
        header=tk.Frame(history.inner,bg=PANEL);header.pack(fill='x',pady=(0,8))
        self.label(header,'Historique récent',12,FG,True).pack(side='left')
        self.label(header,f"{s['wins']} victoires / {s['count']} matchs",9,GREEN).pack(side='right')
        tableframe=tk.Frame(history.inner,bg=PANEL);tableframe.pack(fill='both',expand=True)
        columns=('order','map','agent','kda','acs','result')
        table=ttk.Treeview(tableframe,columns=columns,show='headings',style='H.Treeview',selectmode='browse')
        for name,title,width,anchor in [('order','#',40,'center'),('map','CARTE',135,'w'),('agent','AGENT',110,'w'),('kda','K / D / A',120,'center'),('acs','ACS',85,'center'),('result','RÉSULTAT',110,'center')]:
            table.heading(name,text=title,anchor=anchor)
            table.column(name,width=width,minwidth=width,anchor=anchor,stretch=name!='order')
        table.tag_configure('win',foreground=GREEN)
        table.tag_configure('loss',foreground=RED)
        table.tag_configure('even',background='#171c2c')
        for i,m in enumerate(self.data['matches'][:10],1):
            result=m.get('result')
            tags=['even'] if i%2==0 else []
            if result in ('win','loss'):tags.append(result)
            table.insert('', 'end',values=(f'{i:02}',str(m.get('map','—'))[:24],str(m.get('agent','—'))[:24],
                         f"{m['kills']:g} / {m['deaths']:g} / {m['assists']:g}",f"{m['score']/m['rounds']:.0f}",
                         'VICTOIRE' if result=='win' else 'DÉFAITE' if result=='loss' else '—'),tags=tags)
        scrollbar=ttk.Scrollbar(tableframe,orient='vertical',command=table.yview,style='H.Vertical.TScrollbar')
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right',fill='y');table.pack(side='left',fill='both',expand=True)
        bottom=tk.Frame(main,bg=BG);bottom.grid(row=5,column=0,sticky='ew',pady=(12,0))
        self.label(bottom,'Indicateurs expérimentaux · aucun verdict de smurf ou de triche.',9,MUTED).pack(side='left')
        self.label(bottom,'● Alt + W actif' if self.registered else 'Raccourci indisponible · bouton disponible',9,
                   GREEN if self.registered else MUTED).pack(side='right')

    def draw_lobby(self):
        main=self.shell()
        main.grid_columnconfigure(0,weight=1)
        main.grid_rowconfigure(3,weight=1)
        top=tk.Frame(main,bg=BG);top.grid(row=0,column=0,sticky='ew',pady=(0,16))
        title=tk.Frame(top,bg=BG);title.pack(side='left')
        self.label(title,'Sélection des agents',24,FG,True).pack(anchor='w')
        self.label(title,'Ascent · Compétitif · équipe fictive',11,MUTED).pack(anchor='w',pady=4)
        self.button(top,'Overlay équipe    Alt + W',self.toggle_overlay,True).pack(side='right')
        banner=self.label(main,'DÉMONSTRATION — lobby, identités, rangs et consentements simulés. Aucun accès au jeu.',
                          10,ACCENT,padx=12,pady=12,anchor='w')
        banner.grid(row=1,column=0,sticky='ew',pady=(0,14))
        strip=tk.Frame(main,bg=BG);strip.grid(row=2,column=0,sticky='ew',pady=(0,14))
        visible=sum(p['consent'] for p in self.lobby)
        for title,value,color in [('JOUEURS', '5 / 5',FG),('PROFILS PARTAGÉS',f'{visible} / 5',GREEN),
                                  ('FENÊTRE D’ANALYSE','10 matchs',ACCENT)]:
            box=tk.Frame(strip,bg=PANEL,padx=20,pady=12);box.pack(side='left',fill='x',expand=True,padx=(0,8))
            self.label(box,title,9,MUTED).pack(anchor='w');self.label(box,value,20,color,True).pack(anchor='w')
        surface=Surface(main,height=340);surface.grid(row=3,column=0,sticky='nsew',pady=(0,14))
        f=surface.inner
        self.label(f,'Ton équipe · profils de démonstration',12,FG,True).pack(anchor='w',pady=(0,12))
        style=ttk.Style(self.root);style.configure('Lobby.Treeview',rowheight=48,background=PANEL,
            fieldbackground=PANEL,foreground=FG,borderwidth=0,font=('Segoe UI',10))
        style.configure('Lobby.Treeview.Heading',background=PANEL,foreground=MUTED,font=('Segoe UI',9,'bold'),padding=(3,10))
        style.map('Lobby.Treeview',background=[('selected','#34294f')],foreground=[('selected',FG)])
        columns=('player','agent','rank','kd','acs','sample','note')
        table=ttk.Treeview(f,columns=columns,show='headings',style='Lobby.Treeview',height=5,selectmode='browse')
        for key,label,width in [('player','JOUEUR',148),('agent','AGENT',65),('rank','RANG',100),('kd','K/D',50),
                                ('acs','ACS',50),('sample','MATCHS',62),('note','OBSERVATION',216)]:
            table.heading(key,text=label,anchor='w');table.column(key,width=width,minwidth=width,stretch=key in ('player','note'))
        table.tag_configure('private',foreground=MUTED)
        table.tag_configure('signal',foreground='#f3b875')
        for i,p in enumerate(self.lobby):
            s=lobby_summary(p)
            note=observation_label(s)
            tags=('private',) if s is None else ('signal',) if note in ('Domination régulière','Hausse de performances') else ()
            name=p['player']+(' (toi)' if p['self'] else '')
            table.insert('','end',iid=str(i),values=(name,p['agent'],p['rank'] if s else '—',
                          f"{s['kd']:.2f}" if s else '—',f"{s['acs']:.0f}" if s else '—',
                          f"{s['count']}/10" if s else '—',note),tags=tags)
        table.pack(fill='both',expand=True)
        self.label(f,'Sélectionne un joueur pour lire les observations. Double-clic : historique autorisé.',9,MUTED).pack(anchor='w',pady=(8,0))
        details=Surface(main,height=160);details.grid(row=4,column=0,sticky='ew')
        self.label(details.inner,'Pourquoi cet indicateur ?',12,FG,True).pack(anchor='w')
        detail=self.label(details.inner,'',10,MUTED,justify='left',anchor='nw')
        detail.pack(fill='both',expand=True,pady=(8,0))
        details.inner.bind('<Configure>',lambda e:detail.configure(wraplength=max(100,e.width)))
        def select(event=None):
            chosen=table.selection()
            if not chosen:return
            p=self.lobby[int(chosen[0])];s=lobby_summary(p)
            text='Aucune statistique affichée : ce profil n’a pas autorisé le partage dans la simulation.' if s is None else '\n'.join(s['signals'])
            detail.configure(text=text)
        table.bind('<<TreeviewSelect>>',select)
        table.bind('<Double-1>',lambda e:self.open_profile(int(table.selection()[0])) if table.selection() else None)
        table.selection_set('1');select()
        self.label(main,'Aucun adversaire affiché avant le match · aucun verdict de triche · Riot non connecté.',9,MUTED).grid(row=5,column=0,sticky='w',pady=(12,0))

    def open_profile(self,index):
        p=self.lobby[index]
        if lobby_summary(p) is None:
            messagebox.showinfo('Profil indisponible','Partage non autorisé dans la simulation. Aucune statistique disponible.');return
        self.data=deepcopy(p);self.source='DÉMO · PROFIL FICTIF';self.navigate('overview')

    def draw_account(self):
        main=self.shell()
        self.label(main,'Connexion & consentement',24,FG,True).pack(anchor='w')
        self.label(main,'Maquette du parcours prévu avec Riot Sign On',11,MUTED).pack(anchor='w',pady=(6,20))
        self.label(main,'SIMULATION UNIQUEMENT · aucune connexion Riot, aucun mot de passe demandé.',10,ACCENT).pack(anchor='w',pady=(0,15))
        step1=Surface(main,height=158);step1.pack(fill='x',pady=(0,14))
        f=step1.inner
        self.label(f,'01  ·  Relier son compte',14,FG,True).pack(anchor='w')
        self.label(f,'En production, la connexion se fera sur la page officielle Riot, après validation des accès.',10,MUTED,
                   wraplength=780,justify='left').pack(anchor='w',pady=8)
        self.button(f,'Simuler la connexion Riot' if not self.simulated_connected else 'Identité simulée : Oreo#DEMO',
                    self.simulate_connect,True).pack(anchor='w')
        step2=Surface(main,height=245);step2.pack(fill='x',pady=(0,14))
        f=step2.inner
        self.label(f,'02  ·  Choisir le partage',14,FG,True).pack(anchor='w')
        self.label(f,'Le partage donne aux autres utilisateurs de Hidding accès aux statistiques de ton profil.\n'
                      'La démonstration utilise uniquement des données fictives et ne conserve pas ce choix après fermeture.',
                   10,MUTED,wraplength=780,justify='left').pack(anchor='w',pady=(8,12))
        consent=tk.BooleanVar(value=self.lobby[0]['consent'])
        check=tk.Checkbutton(f,text='J’autorise le partage de mes statistiques dans Hidding (simulation)',variable=consent,
                            bg=PANEL,fg=FG,selectcolor=RAISED,activebackground=PANEL,activeforeground=FG,
                            disabledforeground=MUTED,anchor='w',wraplength=760)
        check.pack(anchor='w')
        apply=self.button(f,'Valider le choix simulé',lambda:self.apply_consent(consent.get()),True)
        apply.pack(anchor='w',pady=12)
        if not self.simulated_connected:check.configure(state='disabled');apply.configure(state='disabled')
        step3=Surface(main,height=160);step3.pack(fill='x')
        f=step3.inner
        self.label(f,'03  ·  Contrôler ses données',14,FG,True).pack(anchor='w')
        state='Partage simulé actif : ton profil apparaît dans le lobby.' if self.lobby[0]['consent'] else 'Partage désactivé : ton profil reste sans statistiques dans le lobby.'
        self.label(f,state,10,GREEN if self.lobby[0]['consent'] else MUTED,wraplength=780).pack(anchor='w',pady=8)
        row=tk.Frame(f,bg=PANEL);row.pack(anchor='w')
        self.button(row,'Révoquer et déconnecter',self.revoke_consent).pack(side='left',padx=(0,10))
        self.button(row,'Voir le lobby démo',lambda:self.navigate('lobby')).pack(side='left')

    def simulate_connect(self):
        self.simulated_connected=True
        self.navigate('account')

    def apply_consent(self,allowed):
        if not self.simulated_connected:return
        self.lobby[0]['consent']=bool(allowed)
        if not allowed and self.data.get('self'):
            self.load_demo()
        self.navigate('account')

    def revoke_consent(self):
        self.simulated_connected=False
        self.lobby[0]['consent']=False
        if self.data.get('self'):self.load_demo()
        self.navigate('account')

    def lobby_overlay(self):
        w=tk.Toplevel(self.root);self.overlay=w;w.title('Hidding — équipe démo');w.configure(bg=BG)
        w.overrideredirect(True);w.attributes('-topmost',True);w.attributes('-alpha',0.97)
        w.geometry('680x470'+self.overlay_position)
        surface=Surface(w,height=470);surface.pack(fill='both',expand=True);f=surface.inner
        header=tk.Frame(f,bg=PANEL);header.pack(fill='x')
        title=self.label(header,'HIDDING  /  TON ÉQUIPE',14,ACCENT,True);title.pack(side='left')
        self.button(header,'×',self.close_overlay).pack(side='right')
        for widget in (header,title):
            widget.bind('<Button-1>',lambda e:setattr(self,'drag',(e.x_root-w.winfo_x(),e.y_root-w.winfo_y())))
            widget.bind('<B1-Motion>',lambda e:w.geometry(f'+{e.x_root-self.drag[0]}+{e.y_root-self.drag[1]}'))
        self.label(f,'LOBBY FICTIF · consentements simulés · Ascent',9,MUTED).pack(anchor='w',pady=(4,14))
        rows=tk.Frame(f,bg=PANEL);rows.pack(fill='x')
        widths=[19,8,8,7,27]
        for j,(text,width) in enumerate(zip(['JOUEUR','K/D','ACS','MATCHS','OBSERVATION'],widths)):
            self.label(rows,text,9,MUTED,width=width,anchor='w').grid(row=0,column=j,sticky='w',pady=(0,10))
        for i,p in enumerate(self.lobby,1):
            s=lobby_summary(p);note=observation_label(s)
            values=[p['player'],f"{s['kd']:.2f}" if s else '—',f"{s['acs']:.0f}" if s else '—',f"{s['count']}/10" if s else '—',note]
            for j,(text,width) in enumerate(zip(values,widths)):
                self.label(rows,text,9,MUTED if s is None else FG,width=width,anchor='w').grid(row=i,column=j,sticky='w',pady=10)
        self.label(f,'Indicateurs exploratoires · aucune accusation de triche ou de smurf.',9,MUTED).pack(side='bottom',pady=8)
        self.label(f,'ALT + W : masquer · glisser le titre : déplacer',9,ACCENT).pack(side='bottom',pady=6)
        w.bind('<Escape>',lambda e:self.close_overlay())

    def draw_chart(self,canvas):
        canvas.delete('all')
        matches=list(reversed(self.data['matches'][:10]))
        w,h=canvas.winfo_width(),canvas.winfo_height()
        if w<80 or h<60:return
        if not matches:
            canvas.create_text(w/2,h/2,text='Aucun match importé',fill=MUTED,font=('Segoe UI',10));return
        values=[m['score']/m['rounds'] for m in matches]
        upper=max(400,max(values)*1.15)
        x1,x2,y1,y2=38,w-12,8,h-24
        for fraction in (0,.5,1):
            y=y2-(y2-y1)*fraction
            canvas.create_line(x1,y,x2,y,fill=EDGE)
            canvas.create_text(x1-8,y,text=f'{upper*fraction:.0f}',anchor='e',fill=MUTED,font=('Segoe UI',8))
        coords=[]
        for i,value in enumerate(values):
            x=(x1+x2)/2 if len(values)==1 else x1+(x2-x1)*i/(len(values)-1)
            y=y2-(y2-y1)*value/upper
            coords.extend((x,y))
        if len(values)>1:
            canvas.create_polygon(x1,y2,*coords,x2,y2,fill='#262139',outline='')
            canvas.create_line(*coords,fill=ACCENT,width=2)
        for i,m in enumerate(matches):
            x,y=coords[2*i:2*i+2]
            color=GREEN if m.get('result')=='win' else RED if m.get('result')=='loss' else ACCENT
            canvas.create_oval(x-4,y-4,x+4,y+4,fill=color,outline=PANEL,width=2)
            canvas.create_text(x,y2+14,text=str(i+1),fill=MUTED,font=('Segoe UI',8))

    def demo(self):
        self.load_demo();self.view='overview';self.refresh()

    def import_data(self):
        path=filedialog.askopenfilename(filetypes=[('Historique JSON','*.json')])
        if not path:return
        try:
            if Path(path).stat().st_size>2_000_000:raise ValueError('Fichier trop volumineux (2 Mo maximum).')
            data=validate(json.loads(Path(path).read_text(encoding='utf-8')))
        except (ValueError,OSError) as exc:
            messagebox.showerror('Import impossible',str(exc));return
        self.data=data;self.source='IMPORT LOCAL · SOURCE NON VÉRIFIÉE';self.view='overview';self.refresh()

    def refresh(self):
        self.close_overlay();self.draw()

    def close_overlay(self):
        if self.overlay:
            self.overlay_position=f'+{self.overlay.winfo_x()}+{self.overlay.winfo_y()}'
            self.overlay.destroy();self.overlay=None

    def toggle_overlay(self):
        if self.overlay:self.close_overlay();return
        if self.view=='lobby':return self.lobby_overlay()
        if self.view=='account':
            messagebox.showinfo('Overlay','Ouvre le lobby démo ou les statistiques pour afficher leur overlay.');return
        s=summarize(self.data)
        w=tk.Toplevel(self.root);self.overlay=w;w.title('Hidding Overlay');w.configure(bg=BG)
        w.overrideredirect(True);w.attributes('-topmost',True);w.attributes('-alpha',0.97)
        w.geometry('430x370'+self.overlay_position)
        card=Surface(w,height=370);card.pack(fill='both',expand=True)
        f=card.inner
        header=tk.Frame(f,bg=PANEL);header.pack(fill='x',pady=(2,6))
        title=self.label(header,'HIDDING',15,ACCENT,True);title.pack(side='left')
        self.button(header,'×',self.close_overlay).pack(side='right')
        for widget in (header,title):
            widget.bind('<Button-1>',lambda e:setattr(self,'drag',(e.x_root-w.winfo_x(),e.y_root-w.winfo_y())))
            widget.bind('<B1-Motion>',lambda e:w.geometry(f'+{e.x_root-self.drag[0]}+{e.y_root-self.drag[1]}'))
        self.label(f,self.source,9,MUTED).pack(anchor='w')
        self.label(f,str(self.data.get('player','Joueur'))[:32],13,FG,True).pack(anchor='w',pady=(12,8))
        numbers=tk.Frame(f,bg=PANEL);numbers.pack(fill='x',pady=(0,14))
        for title,value,color in [('K/D',f"{s['kd']:.2f}",ACCENT),('ACS',f"{s['acs']:.0f}",GREEN),('ADR',f"{s['adr']:.0f}",'#72b9ff')]:
            column=tk.Frame(numbers,bg=PANEL);column.pack(side='left',expand=True,fill='x')
            self.label(column,title,9,MUTED).pack();self.label(column,value,23,color,True).pack()
        text=next((x for x in s['signals'] if not x.startswith('Ces observations')),'Aucune observation.')
        self.label(f,text,10,MUTED,wraplength=390,justify='left').pack(anchor='w',pady=5)
        self.label(f,'Indicateurs expérimentaux · aucun verdict de triche.',9,MUTED,wraplength=390).pack(side='bottom',pady=8)
        self.label(f,'ALT + W pour masquer · glisser le titre pour déplacer',9,ACCENT).pack(side='bottom',pady=4)
        w.bind('<Escape>',lambda e:self.close_overlay())

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
