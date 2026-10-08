                       
import csv, json, math, platform, re, socket, subprocess, threading, time, ssl, urllib.parse, urllib.request
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import ipaddress
import shutil
import webbrowser
from datetime import datetime
from pathlib import Path
import psutil

APP = "NETGUARD PRO // CYBER EDITION"
LOG = Path("netguard_cyber.log")

class App:
    BG="#060a10"; PANEL="#0c141e"; PANEL2="#101d29"
    TEXT="#d8f7ff"; MUTED="#6d8795"; CYAN="#00e5ff"; GREEN="#35ff91"
    RED="#ff5577"; PURPLE="#a486ff"

    def __init__(self, root):
        self.root=root; self.root.title(APP); self.root.geometry("1360x860")
        self.root.configure(bg=self.BG); self.running=True
        try:
            icon=Path(__file__).with_name("assets")/"netguard_pro_icon.png"
            if icon.exists(): self.root.iconphoto(True,tk.PhotoImage(file=str(icon)))
        except Exception: pass
        self.rx=[]; self.tx=[]; self.last=None; self.last_rx=0; self.last_tx=0
        self.wifi=[]; self.alerts=0
        self.baseline=self.snapshot()
        self.style(); self.ui(); self.refresh(); self.root.after(500, self.refresh_device_map); self.root.after(2000,self.loop)
        self.root.protocol("WM_DELETE_WINDOW",self.close)

    def style(self):
        s=ttk.Style()
        try:s.theme_use("clam")
        except:pass
        s.configure(".",background=self.PANEL,foreground=self.TEXT,fieldbackground=self.PANEL2,font=("Segoe UI",10))
        s.layout("Hidden.TNotebook", [])
        s.configure("Treeview",background="#07131d",foreground=self.TEXT,fieldbackground="#07131d",rowheight=30,borderwidth=0,font=("Segoe UI",9))
        s.configure("Treeview.Heading",background="#102536",foreground=self.CYAN,font=("Consolas",9,"bold"),relief="flat")
        s.map("Treeview",background=[("selected","#123b4f")],foreground=[("selected","#ffffff")])
        s.configure("TButton",background="#0d2b3d",foreground=self.TEXT,padding=8)
        s.configure("Vertical.TScrollbar",background="#0c2737",troughcolor="#061018",arrowcolor=self.CYAN,borderwidth=0,relief="flat")

    def panel(self,parent,title=""):
        f=tk.Frame(parent,bg=self.PANEL,highlightbackground="#173347",
                   highlightthickness=1)
        if title:
            tk.Label(f,text="  "+title+"  ",bg=self.PANEL,fg=self.CYAN,
                     font=("Consolas",10,"bold")).pack(anchor="nw",padx=10,pady=8)
        return f

    def ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        header=tk.Frame(self.root,bg="#07111a",height=82,highlightbackground="#123246",highlightthickness=1)
        header.grid(row=0,column=0,columnspan=2,sticky="ew",padx=10,pady=(10,6))
        header.grid_propagate(False)
        brand=tk.Frame(header,bg="#07111a")
        brand.pack(side="left",fill="y",padx=12)
        try:
            self.header_icon=tk.PhotoImage(file=str(Path(__file__).with_name("assets")/"netguard_pro_icon.png"))
            self.header_icon=self.header_icon.subsample(max(1,self.header_icon.width()//64),max(1,self.header_icon.height()//64))
            tk.Label(brand,image=self.header_icon,bg="#07111a",bd=0).pack(side="left",padx=(0,10),pady=7)
        except Exception:
            tk.Label(brand,text="N",bg="#07111a",fg=self.CYAN,font=("Segoe UI",26,"bold")).pack(side="left",padx=12)
        brand_text=tk.Frame(brand,bg="#07111a")
        brand_text.pack(side="left",fill="y",pady=13)
        tk.Label(brand_text,text="NetGuard Pro",bg="#07111a",fg="#eefaff",font=("Segoe UI",20,"bold")).pack(anchor="w")
        tk.Label(brand_text,text="Network & Security Toolkit",bg="#07111a",fg=self.CYAN,font=("Segoe UI",8,"bold")).pack(anchor="w")
        self.clock=tk.StringVar()
        tk.Label(header,text="⌖  Your Location  35.6892° N  51.3890° E",bg="#07111a",fg="#b9d5df",font=("Segoe UI",9,"bold")).pack(side="right",padx=14)
        tk.Label(header,textvariable=self.clock,bg="#07111a",fg="#8aa4b3",font=("Consolas",10)).pack(side="right",padx=12)
        self.status=tk.StringVar(value="● ONLINE")
        tk.Label(header,textvariable=self.status,bg="#07111a",fg=self.GREEN,font=("Consolas",10,"bold")).pack(side="right",padx=8)
        github=tk.Button(header,text="  GitHub  ",command=lambda:webbrowser.open("https://github.com/kasrarasa-coder"),bg="#102536",fg="#d8f7ff",activebackground="#16445e",activeforeground="#00e5ff",relief="flat",bd=1,font=("Segoe UI",9,"bold"),padx=10,pady=5,cursor="hand2")
        github.pack(side="right",padx=(6,10))

        sidebar=tk.Frame(self.root,bg="#08131d",width=255,highlightbackground="#123246",highlightthickness=1)
        sidebar.grid(row=1,column=0,sticky="nsew",padx=(10,6),pady=(0,10))
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(0,weight=1); sidebar.grid_columnconfigure(0,weight=1)
        side_canvas=tk.Canvas(sidebar,bg="#08131d",highlightthickness=0,bd=0)
        side_bar=ttk.Scrollbar(sidebar,orient="vertical",command=side_canvas.yview)
        side_canvas.configure(yscrollcommand=side_bar.set)
        side_canvas.grid(row=0,column=0,sticky="nsew"); side_bar.grid(row=0,column=1,sticky="ns")
        side_inner=tk.Frame(side_canvas,bg="#08131d")
        side_window=side_canvas.create_window((0,0),window=side_inner,anchor="nw",width=240)
        side_inner.bind("<Configure>",lambda e: side_canvas.configure(scrollregion=side_canvas.bbox("all")))
        side_canvas.bind("<Configure>",lambda e: side_canvas.itemconfigure(side_window,width=max(e.width,1)))
        def side_wheel(event):
            side_canvas.yview_scroll(-3 if event.delta>0 else 3,"units")
            return "break"
        side_canvas.bind("<MouseWheel>",side_wheel); side_inner.bind("<MouseWheel>",side_wheel)
        self._sidebar_canvas=side_canvas
        tk.Label(side_inner,text="NAVIGATION",bg="#08131d",fg="#557181",font=("Consolas",8,"bold")).pack(anchor="w",padx=18,pady=(16,7))
        groups=[
            ([("⌂","Dashboard",0),("⌁","Wi-Fi Radar",1),("⌖","Device Map",2),("♜","Cell Towers & Satellites",3)]),
            ([("◉","Authorized Targets",4),("⌁","Security Kit",7),("⚙","Security Lab",8),("⌬","Network Analysis",9),("◎","Web Security",11)]),
            ([("♢","Bluetooth Radar",5),("◌","Camera Security",6),("◈","Signal Audio",10),("▦","Network",12),("↔","Tests",13),("⇄","Connections",14)]),
            ([("▤","Reports",15),("≡","Logs",16)])]
        self._side_buttons=[]
        for gi,items in enumerate(groups):
            for icon,label,index in items:
                btn=tk.Button(side_inner,text=f"  {icon}  {label}",anchor="w",command=lambda i=index:self._select_tab(self._menu_notebook,i),
                               bg="#08131d",fg="#9bb4c0",activebackground="#0d2b3d",activeforeground="#00e5ff",
                               relief="flat",bd=0,font=("Segoe UI",9,"bold"),padx=12,pady=9,cursor="hand2")
                btn.pack(fill="x",padx=10,pady=1)
                self._side_buttons.append((index,btn))
            if gi<len(groups)-1:
                tk.Frame(side_inner,bg="#122433",height=1).pack(fill="x",padx=18,pady=7)
        secure=tk.Frame(side_inner,bg="#0a1f1c",highlightbackground="#174e40",highlightthickness=1)
        secure.pack(fill="x",padx=12,pady=14)
        tk.Label(secure,text="◉",bg="#0a1f1c",fg=self.GREEN,font=("Segoe UI",20,"bold")).pack(side="left",padx=10,pady=10)
        sf=tk.Frame(secure,bg="#0a1f1c"); sf.pack(side="left",pady=8)
        tk.Label(sf,text="System Secure",bg="#0a1f1c",fg="#aaffd0",font=("Segoe UI",10,"bold")).pack(anchor="w")
        tk.Label(sf,text="Monitoring active",bg="#0a1f1c",fg="#5b9c87",font=("Segoe UI",8)).pack(anchor="w")
        tk.Label(side_inner,text="NetGuard Pro  •  Cyber Edition",bg="#08131d",fg="#466170",font=("Consolas",7)).pack(pady=(4,16))

        content=tk.Frame(self.root,bg=self.BG)
        content.grid(row=1,column=1,sticky="nsew",padx=(0,10),pady=(0,10))
        content.grid_rowconfigure(1,weight=1); content.grid_columnconfigure(0,weight=1)

        nav=tk.Frame(content,bg="#071522",height=40,highlightbackground="#123246",highlightthickness=1)
        nav.grid(row=0,column=0,sticky="ew",pady=(0,6))
        nav.grid_propagate(False)
        self._top_nav_buttons=[]
        nav_names=["Dashboard","Wi-Fi","Device","Cell / Satellite","Authorized","Bluetooth","Camera","Security","Network AI","Web","Signal","Tools"]
        nav_indices=[0,1,2,3,4,5,6,7,9,11,10,12]
        for label,index in zip(nav_names,nav_indices):
            b=tk.Button(nav,text=label,command=lambda i=index:self._select_tab(self._menu_notebook,i),bg="#0a1b2a",fg="#b7cfda",activebackground="#0e4160",activeforeground="#ffffff",relief="flat",bd=0,font=("Segoe UI",9,"bold"),padx=11,pady=5,cursor="hand2")
            b.pack(side="left",padx=1,pady=3)
            self._top_nav_buttons.append((index,b))
        tk.Button(nav,text="⟳ Refresh",command=self._menu_refresh,bg="#0d3044",fg=self.CYAN,activebackground="#14506b",activeforeground="#ffffff",relief="flat",font=("Segoe UI",9,"bold"),padx=11,pady=5,cursor="hand2").pack(side="right",padx=5,pady=3)

        scroll_host=tk.Frame(content,bg=self.BG)
        scroll_host.grid(row=1,column=0,sticky="nsew")
        scroll_host.grid_rowconfigure(0,weight=1); scroll_host.grid_columnconfigure(0,weight=1)
        scroll_canvas=tk.Canvas(scroll_host,bg=self.BG,highlightthickness=0,bd=0)
        scroll_bar=ttk.Scrollbar(scroll_host,orient="vertical",command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scroll_bar.set)
        scroll_canvas.grid(row=0,column=0,sticky="nsew")
        scroll_bar.grid(row=0,column=1,sticky="ns")
        nb=ttk.Notebook(scroll_canvas,style="Hidden.TNotebook",height=900)
        nb_window=scroll_canvas.create_window((0,0),window=nb,anchor="nw",width=1,height=900)
        def resize_notebook(event):
            scroll_canvas.itemconfigure(nb_window,width=max(event.width,1),height=max(event.height,900))
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        scroll_canvas.bind("<Configure>",resize_notebook)
        nb.bind("<Configure>",lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        def wheel(event):
            scroll_canvas.yview_scroll(-3 if event.delta>0 else 3,"units")
            return "break"
        scroll_canvas.bind("<MouseWheel>",wheel)
        nb.bind("<MouseWheel>",wheel)
        self._scroll_canvas=scroll_canvas
        self._scroll_bar=scroll_bar
        self.tabs=[]
        names=["DASHBOARD","WI-FI RADAR","DEVICE MAP","CELL / SATELLITE","AUTHORIZED TARGETS","BLUETOOTH","CAMERA SECURITY","SECURITY KIT","SECURITY LAB","NETWORK ANALYSIS","SIGNAL AUDIO","WEB SECURITY","NETWORK","TESTS","CONNECTIONS","REPORTS","LOGS"]
        for name in names:
            f=tk.Frame(nb,bg=self.BG); nb.add(f,text=name); self.tabs.append(f)
        self._menu_notebook=nb
        (self.dashboard,self.wifi_tab,self.device_map,self.cell_sat,self.targets,self.bluetooth,self.camera,self.sec,
         self.security_lab,self.network_analysis,self.signal_audio,self.web_security,self.net,self.tests,self.conn,self.rep,self.logs)=self.tabs
        self.dashboard_ui(); self.wifi_ui(); self.device_map_ui(); self.cell_sat_ui(); self.targets_ui(); self.bluetooth_ui(); self.camera_ui(); self.security_ui()
        self.security_lab_ui(); self.network_analysis_ui(); self.signal_audio_ui(); self.web_security_tools_ui(); self.network_ui()
        self.tests_ui(); self.connections_ui(); self.reports_ui(); self.logs_ui()
        self._select_tab(nb,0)

    def _make_tabs_scrollable(self, notebook):
                                                                        
        try:
            notebook.configure(takefocus=1)
        except Exception:
            pass

        def wheel(event):
            try:
                                                             
                direction = -1 if event.delta > 0 else 1
                notebook.xview_scroll(direction, "units")
            except Exception:
                pass
            return "break"

        notebook.bind("<MouseWheel>", wheel)
        notebook.bind("<Shift-MouseWheel>", wheel)


    def _build_app_menu(self, notebook):
        menubar = tk.Frame(self.root, bg="#061018", height=38)
        menubar.pack(fill="x", padx=10, pady=(0, 4))
        menubar.pack_propagate(False)

        tk.Label(menubar, text="MENU", bg="#061018", fg=self.CYAN,
                 font=("Consolas", 10, "bold")).pack(side="left", padx=(10, 8))

        groups = [
            ("MONITOR", [("Dashboard", 0), ("Wi-Fi Radar", 1), ("Device Map", 2),
                         ("Cell / Satellite", 3), ("Bluetooth", 5), ("Camera Security", 6)]),
            ("SECURITY", [("Security Kit", 7), ("Security Lab", 8),
                          ("Network Analysis", 9), ("Web Security", 11), ("Authorized Targets", 4)]),
            ("TOOLS", [("Signal Audio", 10), ("Network", 12), ("Tests", 13),
                       ("Connections", 14)]),
            ("REPORTS", [("Reports", 15), ("Logs", 16)]),
        ]

        for title, items in groups:
            btn = tk.Menubutton(menubar, text=title, bg="#0d1b26",
                                fg="#b8d3df", activebackground="#123047",
                                activeforeground=self.CYAN, relief="flat",
                                font=("Consolas", 9, "bold"), padx=10, pady=5)
            m = tk.Menu(btn, tearoff=0, bg="#0b1721", fg="#d8edf7",
                        activebackground="#123047", activeforeground=self.CYAN,
                        font=("Segoe UI", 9))
            for label, index in items:
                m.add_command(label=label,
                              command=lambda i=index: self._select_tab(notebook, i))
            btn.configure(menu=m)
            btn.pack(side="left", padx=3)

                                     
        tk.Button(menubar, text="⟳ REFRESH", command=self._menu_refresh,
                  bg="#123047", fg=self.CYAN, activebackground="#17465a",
                  relief="flat", font=("Consolas", 8, "bold"),
                  padx=10).pack(side="right", padx=5)

    def _select_tab(self, notebook, index):
        try:
            nb = notebook or getattr(self, "_menu_notebook", None)
            if nb is not None:
                nb.select(index)
            if index == 3 and hasattr(self, "tower_tree") and not getattr(self, "space_scan_started", False):
                self.space_scan_started = True
                self.scan_towers()
                self.track_satellites()
            if hasattr(self, "_scroll_canvas"):
                self._scroll_canvas.yview_moveto(0)
            for i,btn in getattr(self,"_side_buttons",[]):
                active = i == index
                btn.configure(bg="#0d2b3d" if active else "#08131d", fg=self.CYAN if active else "#9bb4c0")
            for i,btn in getattr(self,"_top_nav_buttons",[]):
                active = i == index
                btn.configure(bg="#0879b5" if active else "#0a1b2a", fg="#ffffff" if active else "#b7cfda")
        except Exception:
            pass

    def _menu_refresh(self):
        try:
            if hasattr(self, "update_dashboard"):
                self.update_dashboard()
            if hasattr(self, "scan_wifi"):
                self.scan_wifi()
            self.log("Menu refresh requested.")
        except Exception:
            pass

    def dashboard_ui(self):
        outer=tk.Frame(self.dashboard,bg=self.BG)
        outer.pack(fill="both",expand=True,padx=2,pady=2)
        top=tk.Frame(outer,bg=self.BG)
        top.pack(fill="x",pady=(2,8))
        tk.Label(top,text="Dashboard",bg=self.BG,fg="#eefaff",font=("Segoe UI",22,"bold")).pack(side="left")
        tk.Label(top,text="  Monitor  •  Analyze  •  Protect",bg=self.BG,fg="#5d7d8c",font=("Segoe UI",10)).pack(side="left",pady=(10,0))
        tk.Button(top,text="↻  Refresh",command=self._menu_refresh,bg="#0d2b3d",fg=self.CYAN,activebackground="#17465a",relief="flat",font=("Segoe UI",9,"bold"),padx=14,pady=7).pack(side="right")

        metrics=tk.Frame(outer,bg=self.BG); metrics.pack(fill="x",pady=(0,8))
        self.m={}
        metric_defs=[("WIFI","Connected",self.CYAN),("DEVICES","Online",self.CYAN),("CELL TOWERS","Nearby",self.CYAN),("SATELLITES","Visible",self.PURPLE),("SECURITY","Safe",self.GREEN)]
        for name,sub,accent in metric_defs:
            f=tk.Frame(metrics,bg="#0b1722",highlightbackground="#153246",highlightthickness=1); f.pack(side="left",fill="x",expand=True,padx=3)
            left=tk.Frame(f,bg="#0b1722"); left.pack(fill="both",expand=True,padx=12,pady=10)
            tk.Label(left,text=name,bg="#0b1722",fg="#7893a1",font=("Consolas",8,"bold")).pack(anchor="w")
            v=tk.StringVar(value="--"); self.m[name]=v
            tk.Label(left,textvariable=v,bg="#0b1722",fg=accent,font=("Segoe UI",17,"bold")).pack(anchor="w",pady=(2,0))
            tk.Label(left,text=sub,bg="#0b1722",fg="#506a78",font=("Segoe UI",8)).pack(anchor="w")

        body=tk.Frame(outer,bg=self.BG); body.pack(fill="both",expand=True)
        left=tk.Frame(body,bg=self.BG); left.pack(side="left",fill="both",expand=True,padx=(0,5))
        right=tk.Frame(body,bg=self.BG,width=370); right.pack(side="right",fill="both",padx=(5,0)); right.pack_propagate(False)

        nearby=self.panel(left,"NEARBY CELL TOWERS  •  LIVE RELATIVE VIEW")
        nearby.pack(fill="both",expand=True,pady=(0,6))
        self.dashboard_map=tk.Canvas(nearby,bg="#071019",highlightthickness=0,bd=0,height=390)
        self.dashboard_map.pack(fill="both",expand=True,padx=8,pady=8)
        self.dashboard_map.bind("<Configure>",lambda e:self.draw_dashboard_space_map())

        lower=tk.Frame(left,bg=self.BG); lower.pack(fill="both",expand=True)
        activity=self.panel(lower,"NETWORK ACTIVITY")
        activity.pack(side="left",fill="both",expand=True,padx=(0,3))
        self.graph=tk.Canvas(activity,bg="#061019",highlightthickness=0); self.graph.pack(fill="both",expand=True,padx=8,pady=8)
        self.graph.bind("<Configure>",lambda e:self.draw_graph())

        quick=self.panel(lower,"QUICK TOOLS")
        quick.pack(side="right",fill="both",expand=True,padx=(3,0))
        tools=[("↯","Ping",13),("⇢","Traceroute",9),("◎","DNS Lookup",9),("▣","Port Scan",8)]
        grid=tk.Frame(quick,bg=self.PANEL); grid.pack(fill="both",expand=True,padx=8,pady=4)
        for i,(ic,label,idx) in enumerate(tools):
            b=tk.Button(grid,text=f"{ic}\n{label}",command=lambda i=idx:self._select_tab(self._menu_notebook,i),bg="#0a1b28",fg="#b8d7e3",activebackground="#12394d",activeforeground=self.CYAN,relief="flat",font=("Segoe UI",8,"bold"),width=10,height=3)
            b.grid(row=0,column=i,padx=4,pady=4,sticky="nsew")
            grid.grid_columnconfigure(i,weight=1)

        tower_panel=self.panel(right,"NEARBY CELL TOWERS")
        tower_panel.pack(fill="both",expand=True,pady=(0,6))
        tw=tk.Frame(tower_panel,bg=self.PANEL); tw.pack(fill="both",expand=True,padx=8,pady=6)
        cols=("name","type","distance")
        self.dashboard_tower_tree=ttk.Treeview(tw,columns=cols,show="headings",height=6)
        for c,w in zip(cols,[150,80,85]): self.dashboard_tower_tree.heading(c,text=c.upper()); self.dashboard_tower_tree.column(c,width=w,anchor="center")
        ts=ttk.Scrollbar(tw,orient="vertical",command=self.dashboard_tower_tree.yview); self.dashboard_tower_tree.configure(yscrollcommand=ts.set)
        self.dashboard_tower_tree.grid(row=0,column=0,sticky="nsew"); ts.grid(row=0,column=1,sticky="ns"); tw.grid_rowconfigure(0,weight=1); tw.grid_columnconfigure(0,weight=1)

        sat_panel=self.panel(right,"VISIBLE SATELLITES")
        sat_panel.pack(fill="both",expand=True,pady=(0,6))
        sw=tk.Frame(sat_panel,bg=self.PANEL); sw.pack(fill="both",expand=True,padx=8,pady=6)
        cols=("name","distance","el")
        self.dashboard_sat_tree=ttk.Treeview(sw,columns=cols,show="headings",height=7)
        for c,w in zip(cols,[155,80,70]): self.dashboard_sat_tree.heading(c,text=("DISTANCE" if c=="distance" else c.upper())); self.dashboard_sat_tree.column(c,width=w,anchor="center")
        ss=ttk.Scrollbar(sw,orient="vertical",command=self.dashboard_sat_tree.yview); self.dashboard_sat_tree.configure(yscrollcommand=ss.set)
        self.dashboard_sat_tree.grid(row=0,column=0,sticky="nsew"); ss.grid(row=0,column=1,sticky="ns"); sw.grid_rowconfigure(0,weight=1); sw.grid_columnconfigure(0,weight=1)

        sec=self.panel(right,"SECURITY OVERVIEW")
        sec.pack(fill="both",expand=True)
        self.security_overview=tk.Text(sec,bg="#061019",fg="#a7c5d1",relief="flat",font=("Segoe UI",9),bd=0)
        self.security_overview.pack(fill="both",expand=True,padx=8,pady=8)

        self.space_summary=tk.Text(self.dashboard,bg=self.BG,fg=self.TEXT,height=1,width=1)
        self.space_summary.place(x=-1000,y=-1000)
        self.activity=tk.Text(self.dashboard,bg=self.BG,fg=self.TEXT,height=1,width=1)
        self.activity.place(x=-1000,y=-1000)
        self.sys=tk.Text(self.dashboard,bg=self.BG,fg=self.TEXT,height=1,width=1)
        self.sys.place(x=-1000,y=-1000)
        self._dashboard_activity=[]

    def draw_dashboard_space_map(self):
        if not hasattr(self,"dashboard_map"): return
        c=self.dashboard_map; c.delete("all")
        w=max(c.winfo_width(),620); h=max(c.winfo_height(),360)
        for x in range(0,w,55): c.create_line(x,0,x,h,fill="#0d2531")
        for y in range(0,h,45): c.create_line(0,y,w,y,fill="#0d2531")
        for pts in [[(0,h*.72),(w*.18,h*.52),(w*.35,h*.62),(w*.54,h*.40),(w*.72,h*.50),(w,h*.32)],[(w*.05,h*.20),(w*.28,h*.36),(w*.46,h*.25),(w*.68,h*.34),(w*.95,h*.12)]]:
            c.create_line(*[v for p in pts for v in p],fill="#183847",width=2,smooth=True)
        cx,cy=w*.47,h*.53; r=min(w,h)*.34
        for q in [1,.66,.33]:
            rr=r*q; c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline="#1a4658",dash=(3,5))
        c.create_oval(cx-7,cy-7,cx+7,cy+7,fill="#00e5ff",outline="#8af6ff",width=1)
        c.create_text(cx+12,cy-12,text="YOU",anchor="w",fill="#d8f7ff",font=("Consolas",8,"bold"))
        try: lat=float(self.obs_lat.get()); lon=float(self.obs_lon.get()); radius=max(float(self.obs_radius.get()),1)
        except Exception: lat,lon,radius=35.6892,51.3890,10
        for t in getattr(self,"towers",[])[:60]:
            br=self.bearing(lat,lon,t["lat"],t["lon"]); rr=r*min(max(t["distance"]/radius,.04),1); a=math.radians(br-90); px=cx+rr*math.cos(a); py=cy+rr*math.sin(a)
            c.create_line(cx,cy,px,py,fill="#214c5f")
            c.create_oval(px-5,py-5,px+5,py+5,fill="#ff5577",outline="")
            c.create_text(px+8,py,text="⌁",fill="#ff5577",font=("Segoe UI",10,"bold"))
        for sat in [x for x in getattr(self,"satellites",[]) if x.get("el",-90)>0][:35]:
            rr=r*(1-min(sat.get("el",0)/90,1)*.55); a=math.radians(sat.get("az",0)-90); px=cx+rr*math.cos(a); py=cy+rr*math.sin(a)
            c.create_oval(px-4,py-4,px+4,py+4,fill="#a486ff",outline="")
        c.create_text(12,12,anchor="nw",text="You (Device)    ◆ Cell Tower    ◆ Satellite",fill="#b7cfda",font=("Segoe UI",8,"bold"))
        c.create_text(12,h-10,anchor="sw",text=f"Range: {radius:g} km     Towers: {len(getattr(self,'towers',[]))}     Visible satellites: {sum(1 for x in getattr(self,'satellites',[]) if x.get('el',-90)>0)}",fill="#6d8795",font=("Consolas",8))
    def wifi_ui(self):
        top=tk.Frame(self.wifi_tab,bg=self.BG); top.pack(fill="x",pady=5)
        tk.Label(top,text="◉ WI-FI SIGNAL RADAR",bg=self.BG,fg=self.CYAN,font=("Consolas",15,"bold")).pack(side="left")
        tk.Button(top,text="SCAN NOW",command=self.scan_wifi,bg="#123047",fg=self.CYAN,
                  activebackground="#1b4c68",relief="flat",padx=18,pady=7).pack(side="right")
        body=tk.Frame(self.wifi_tab,bg=self.BG); body.pack(fill="both",expand=True)
        a=self.panel(body,"SIGNAL MAP"); a.pack(side="left",fill="both",expand=True,padx=(0,5))
        self.radar=tk.Canvas(a,bg="#050a10",highlightthickness=0); self.radar.pack(fill="both",expand=True,padx=8,pady=8)
        self.radar.bind("<Configure>",lambda e:self.draw_radar())
        b=self.panel(body,"VISIBLE NETWORKS"); b.pack(side="right",fill="both",expand=True,padx=(5,0))
        cols=("ssid","signal","channel","security"); self.wtree=ttk.Treeview(b,columns=cols,show="headings")
        for c,w in zip(cols,[230,90,90,150]): self.wtree.heading(c,text=c.upper()); self.wtree.column(c,width=w)
        self.wtree.pack(fill="both",expand=True,padx=8,pady=8)

    def scan_wifi(self):
        self.status.set("● SCANNING WI-FI...")
        threading.Thread(target=self._scan_wifi,daemon=True).start()

    def _scan_wifi(self):
        if platform.system().lower()!="windows":
            self.root.after(0,lambda:self.status.set("● WI-FI SCAN: WINDOWS ONLY"))
            return
        try:
            r=subprocess.run(["netsh","wlan","show","networks","mode=bssid"],
                             capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=15)
            data=[]; cur=None
            for x in r.stdout.splitlines():
                s=x.strip()
                m=re.match(r"SSID\s+\d+\s*:\s*(.*)",s)
                if m:
                    cur={"ssid":m.group(1).strip() or "<hidden>","signal":0,"channel":"-","security":"Unknown"}
                    data.append(cur)
                elif cur:
                    m=re.match(r"Signal\s*:\s*(\d+)%",s)
                    if m: cur["signal"]=int(m.group(1))
                    m=re.match(r"Channel\s*:\s*(\d+)",s)
                    if m: cur["channel"]=m.group(1)
                    m=re.match(r"Authentication\s*:\s*(.*)",s)
                    if m: cur["security"]=m.group(1).strip()
            self.root.after(0,lambda:self.apply_wifi(data))
        except Exception as e:
            self.root.after(0,lambda err=str(e):self.alert("WARN","WI-FI",err))

    def apply_wifi(self,data):
        self.wifi=data
        for i in self.wtree.get_children(): self.wtree.delete(i)
        for n in data:self.wtree.insert("", "end",values=(n["ssid"],str(n["signal"])+"%",n["channel"],n["security"]))
        self.status.set(f"● ONLINE // {len(data)} WI-FI NETWORKS"); self.draw_radar()
        self.log(f"Wi-Fi scan: {len(data)} visible networks")

    def draw_radar(self):
        if not hasattr(self,"radar"): return
        c=self.radar;c.delete("all");w=max(c.winfo_width(),350);h=max(c.winfo_height(),350);cx=w/2;cy=h/2;r=min(w,h)*.37
        for q in [1,.75,.5,.25]:
            rr=r*q;c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline="#153343")
        for a in range(0,360,30):
            z=math.radians(a);c.create_line(cx,cy,cx+r*math.cos(z),cy+r*math.sin(z),fill="#102633")
        z=math.radians((time.time()*45)%360);c.create_line(cx,cy,cx+r*math.cos(z),cy+r*math.sin(z),fill=self.CYAN,width=2)
        c.create_oval(cx-4,cy-4,cx+4,cy+4,fill=self.GREEN,outline="")
        for i,n in enumerate(self.wifi[:35]):
            sig=n["signal"] or 1; z=math.radians((i*137.5+sig*2)%360); d=r*(1-sig/130)
            x=cx+d*math.cos(z);y=cy+d*math.sin(z);q=3+sig/25
            c.create_oval(x-q,y-q,x+q,y+q,fill=self.CYAN,outline="")
            c.create_text(x+8,y,text=n["ssid"][:15],anchor="w",fill=self.TEXT,font=("Consolas",8))


                                                               
                                           
                                                               
    def device_map_ui(self):
        top = tk.Frame(self.device_map, bg=self.BG)
        top.pack(fill="x", pady=6)
        tk.Label(
            top, text="◎ 3D-STYLE LAN DEVICE MAP",
            bg=self.BG, fg=self.CYAN,
            font=("Consolas", 15, "bold")
        ).pack(side="left")
        tk.Label(
            top,
            text="Shows devices already present in the local ARP cache; no active probing.",
            bg=self.BG, fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(side="left", padx=15)
        tk.Button(
            top, text="REFRESH",
            command=self.refresh_device_map,
            bg="#123047", fg=self.CYAN, relief="flat",
            padx=16, pady=7
        ).pack(side="right")

        body = tk.Frame(self.device_map, bg=self.BG)
        body.pack(fill="both", expand=True)

        left = self.panel(body, "NETWORK TOPOLOGY")
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.map_canvas = tk.Canvas(
            left, bg="#050a10", highlightthickness=0
        )
        self.map_canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.map_canvas.bind("<Configure>", lambda e: self.draw_device_map())

        right = self.panel(body, "LOCAL ARP DEVICES")
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))
        cols = ("ip", "mac", "type", "state")
        self.device_tree = ttk.Treeview(
            right, columns=cols, show="headings"
        )
        for c, w in zip(cols, [180, 190, 130, 100]):
            self.device_tree.heading(c, text=c.upper())
            self.device_tree.column(c, width=w)
        self.device_tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.devices = []

    def refresh_device_map(self):
        self.devices = []
        if platform.system().lower() == "windows":
            try:
                r = subprocess.run(
                    ["arp", "-a"],
                    capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=8
                )
                          
                                                         
                rx = re.compile(
                    r"^\s*(\d+\.\d+\.\d+\.\d+)\s+"
                    r"([0-9a-fA-F:-]{11,17})\s+(\w+)"
                )
                for line in r.stdout.splitlines():
                    m = rx.match(line)
                    if m:
                        ip, mac, state = m.groups()
                        self.devices.append({
                            "ip": ip,
                            "mac": mac,
                            "type": self.guess_device_type(mac),
                            "state": state.upper()
                        })
            except Exception as e:
                self.alert("WARN", "DEVICE MAP", str(e))
        else:
            try:
                r = subprocess.run(
                    ["arp", "-n"],
                    capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=8
                )
                rx = re.compile(
                    r"^\s*(\d+\.\d+\.\d+\.\d+)\s+"
                    r"([0-9a-fA-F:]{17})\s+\S+\s+\S+\s+(\S+)"
                )
                for line in r.stdout.splitlines():
                    m = rx.match(line)
                    if m:
                        ip, mac, state = m.groups()
                        self.devices.append({
                            "ip": ip,
                            "mac": mac,
                            "type": self.guess_device_type(mac),
                            "state": state.upper()
                        })
            except Exception as e:
                self.alert("WARN", "DEVICE MAP", str(e))

        if hasattr(self, "device_tree"):
            for item in self.device_tree.get_children():
                self.device_tree.delete(item)
            for d in self.devices:
                self.device_tree.insert(
                    "", "end",
                    values=(d["ip"], d["mac"], d["type"], d["state"])
                )
        self.draw_device_map()
        self.log(f"LAN map refreshed: {len(self.devices)} cached devices.")

    @staticmethod
    def guess_device_type(mac):
                                                                
        return "LAN device"

    def draw_device_map(self):
        if not hasattr(self, "map_canvas"):
            return
        c = self.map_canvas
        c.delete("all")
        w = max(c.winfo_width(), 500)
        h = max(c.winfo_height(), 350)
        cx, cy = w / 2, h / 2

                             
        for y in range(int(h * .60), h, 25):
            c.create_line(0, y, w, y, fill="#0c202d")
        for x in range(-w, w * 2, 55):
            c.create_line(
                cx + (x - cx) * .35, h * .60,
                x, h,
                fill="#0c202d"
            )

                      
        c.create_oval(cx-42, cy-42, cx+42, cy+42,
                      fill="#102b3c", outline=self.CYAN, width=2)
        c.create_text(cx, cy, text="ROUTER",
                      fill=self.CYAN, font=("Consolas", 10, "bold"))

        count = max(len(self.devices), 1)
        for i, d in enumerate(self.devices[:24]):
            angle = (i / count) * 2 * math.pi
            ring = 130 + (i % 3) * 55
            x = cx + math.cos(angle) * ring
            y = cy + math.sin(angle) * ring * .55

            c.create_line(cx, cy, x, y, fill="#174153")
            c.create_oval(
                x-14, y-14, x+14, y+14,
                fill="#0b2635", outline=self.GREEN
            )
            c.create_text(
                x, y,
                text=str(i + 1),
                fill=self.GREEN,
                font=("Consolas", 9, "bold")
            )
            c.create_text(
                x, y+24,
                text=d["ip"],
                fill=self.TEXT,
                font=("Consolas", 8)
            )

        if not self.devices:
            c.create_text(
                cx, cy+85,
                text="No cached LAN devices.\nPress REFRESH.",
                fill=self.MUTED,
                font=("Consolas", 10),
                justify="center"
            )

                                                               
                        
                                                               
    def cell_sat_ui(self):
        top=tk.Frame(self.cell_sat,bg=self.BG); top.pack(fill="x",pady=6)
        tk.Label(top,text="◈ NEARBY TOWERS & SATELLITES",bg=self.BG,fg=self.CYAN,font=("Consolas",15,"bold")).pack(side="left")
        tk.Label(top,text="Nearby telecom towers + satellites currently above the horizon",bg=self.BG,fg=self.MUTED,font=("Segoe UI",9)).pack(side="left",padx=14)
        controls=self.panel(self.cell_sat,"OBSERVER LOCATION")
        controls.pack(fill="x",pady=5)
        row=tk.Frame(controls,bg=self.PANEL);row.pack(fill="x",padx=10,pady=10)
        tk.Label(row,text="LAT",bg=self.PANEL,fg=self.MUTED).pack(side="left")
        self.obs_lat=tk.Entry(row,bg="#07111a",fg=self.TEXT,insertbackground=self.CYAN,relief="flat",width=14);self.obs_lat.insert(0,"35.6892");self.obs_lat.pack(side="left",padx=6)
        tk.Label(row,text="LON",bg=self.PANEL,fg=self.MUTED).pack(side="left",padx=(10,0))
        self.obs_lon=tk.Entry(row,bg="#07111a",fg=self.TEXT,insertbackground=self.CYAN,relief="flat",width=14);self.obs_lon.insert(0,"51.3890");self.obs_lon.pack(side="left",padx=6)
        tk.Label(row,text="RADIUS KM",bg=self.PANEL,fg=self.MUTED).pack(side="left",padx=(10,0))
        self.obs_radius=tk.Entry(row,bg="#07111a",fg=self.TEXT,insertbackground=self.CYAN,relief="flat",width=8);self.obs_radius.insert(0,"10");self.obs_radius.pack(side="left",padx=6)
        tk.Button(row,text="SCAN TOWERS",command=self.scan_towers,bg="#123047",fg=self.CYAN,relief="flat",padx=12,pady=6).pack(side="left",padx=6)
        tk.Button(row,text="SHOW SATELLITES",command=self.track_satellites,bg="#123047",fg=self.GREEN,relief="flat",padx=12,pady=6).pack(side="left",padx=4)
        tk.Button(row,text="CLEAR",command=self.clear_space_data,bg="#2b1822",fg=self.RED,relief="flat",padx=12,pady=6).pack(side="right")

        map_panel=self.panel(self.cell_sat,"NEARBY VIEW")
        map_panel.pack(fill="x",pady=5)
        self.space_map=tk.Canvas(map_panel,bg="#050a10",height=260,highlightthickness=0,bd=0)
        self.space_map.pack(fill="x",padx=8,pady=(0,8))
        self.space_map.bind("<Configure>",lambda e:self.draw_space_map())
        self.space_map_status=tk.StringVar(value="Enter observer coordinates, then scan for nearby towers and visible satellites.")
        tk.Label(map_panel,textvariable=self.space_map_status,bg=self.PANEL,fg=self.MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=10,pady=(0,8))

        body=tk.Frame(self.cell_sat,bg=self.BG);body.pack(fill="both",expand=True)
        left=self.panel(body,"CELL TOWERS / RADIO MASTS");left.pack(side="left",fill="both",expand=True,padx=(0,5))
        tower_wrap=tk.Frame(left,bg=self.PANEL);tower_wrap.pack(fill="both",expand=True,padx=8,pady=8)
        cols=("name","type","distance","lat","lon");self.tower_tree=ttk.Treeview(tower_wrap,columns=cols,show="headings")
        for c,w in zip(cols,[220,140,100,120,120]):self.tower_tree.heading(c,text=c.upper());self.tower_tree.column(c,width=w)
        tower_scroll=ttk.Scrollbar(tower_wrap,orient="vertical",command=self.tower_tree.yview);self.tower_tree.configure(yscrollcommand=tower_scroll.set)
        self.tower_tree.grid(row=0,column=0,sticky="nsew");tower_scroll.grid(row=0,column=1,sticky="ns")
        tower_wrap.grid_rowconfigure(0,weight=1);tower_wrap.grid_columnconfigure(0,weight=1)

        right=self.panel(body,"SATELLITES ABOVE HORIZON");right.pack(side="right",fill="both",expand=True,padx=(5,0))
        sat_wrap=tk.Frame(right,bg=self.PANEL);sat_wrap.pack(fill="both",expand=True,padx=8,pady=8)
        cols=("name","distance","az","el","status");self.sat_tree=ttk.Treeview(sat_wrap,columns=cols,show="headings")
        for c,w in zip(cols,[220,100,90,90,150]):self.sat_tree.heading(c,text=("DISTANCE KM" if c=="distance" else c.upper()));self.sat_tree.column(c,width=w)
        sat_scroll=ttk.Scrollbar(sat_wrap,orient="vertical",command=self.sat_tree.yview);self.sat_tree.configure(yscrollcommand=sat_scroll.set)
        self.sat_tree.grid(row=0,column=0,sticky="nsew");sat_scroll.grid(row=0,column=1,sticky="ns")
        sat_wrap.grid_rowconfigure(0,weight=1);sat_wrap.grid_columnconfigure(0,weight=1)
        tk.Label(right,text="Only satellites currently above the local horizon are shown. Tower results come from public OpenStreetMap data; this is not live RF detection.",bg=self.PANEL,fg=self.MUTED,font=("Segoe UI",9),wraplength=520,justify="left").pack(anchor="w",padx=10,pady=(0,8))
        self.towers=[];self.satellites=[];self.space_scan_started=False

    def bearing(self,lat1,lon1,lat2,lon2):
        a=math.radians(lon2-lon1);p1=math.radians(lat1);p2=math.radians(lat2)
        y=math.sin(a)*math.cos(p2);x=math.cos(p1)*math.sin(p2)-math.sin(p1)*math.cos(p2)*math.cos(a)
        return (math.degrees(math.atan2(y,x))+360)%360

    def draw_space_map(self):
        if not hasattr(self,"space_map"):return
        c=self.space_map;c.delete("all");w=max(c.winfo_width(),600);h=max(c.winfo_height(),260);cx=w/2;cy=h/2;r=min(w,h)*0.34
        for q,label in [(1,"10 km"),(.66,""),(.33,"")]:
            rr=r*q;c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline="#153343")
            if label:c.create_text(cx+rr+8,cy,anchor="w",text=label,fill="#506a78",font=("Consolas",8))
        for deg,name in [(0,"N"),(90,"E"),(180,"S"),(270,"W")]:
            z=math.radians(deg-90);x=cx+(r+18)*math.cos(z);y=cy+(r+18)*math.sin(z);c.create_text(x,y,text=name,fill=self.MUTED,font=("Consolas",8,"bold"))
        c.create_oval(cx-5,cy-5,cx+5,cy+5,fill=self.GREEN,outline="")
        c.create_text(cx+9,cy-10,anchor="w",text="OBSERVER",fill=self.TEXT,font=("Consolas",8,"bold"))
        try:lat=float(self.obs_lat.get());lon=float(self.obs_lon.get());radius=float(self.obs_radius.get())
        except Exception:return
        for x in self.towers[:100]:
            br=self.bearing(lat,lon,x["lat"],x["lon"]);d=min(x["distance"]/max(radius,1),1);rr=r*max(d,.05);z=math.radians(br-90);px=cx+rr*math.cos(z);py=cy+rr*math.sin(z)
            c.create_line(cx,cy,px,py,fill="#153b4d")
            c.create_oval(px-4,py-4,px+4,py+4,fill=self.CYAN,outline="")
        for x in [s for s in self.satellites if s.get("el",-90)>0][:80]:
            rr=r*(1-min(x.get("el",0)/90,1)*.55);z=math.radians(x.get("az",0)-90);px=cx+rr*math.cos(z);py=cy+rr*math.sin(z)
            c.create_oval(px-3,py-3,px+3,py+3,fill=self.PURPLE,outline="")
        c.create_text(12,12,anchor="nw",text=f"TOWERS: {len(self.towers)}   VISIBLE SATELLITES: {sum(1 for x in self.satellites if x.get('el',-90)>0)}",fill=self.TEXT,font=("Consolas",9,"bold"))
        c.create_text(12,h-12,anchor="sw",text="CYAN = nearby telecom towers   PURPLE = visible satellites   Relative view only",fill="#6d8795",font=("Segoe UI",8))

    def _observer(self):
        try:
            lat=float(self.obs_lat.get());lon=float(self.obs_lon.get());radius=float(self.obs_radius.get())
            if not -90<=lat<=90 or not -180<=lon<=180 or not 1<=radius<=100: raise ValueError
            return lat,lon,radius
        except Exception:
            messagebox.showwarning("Observer location","Enter valid latitude, longitude and a radius from 1 to 100 km.")
            return None

    def scan_towers(self):
        obs=self._observer()
        if not obs:return
        lat,lon,radius=obs
        def work():
            try:
                q=f"""[out:json][timeout:20];(node[\"tower:type\"=\"communication\"](around:{radius*1000},{lat},{lon});way[\"tower:type\"=\"communication\"](around:{radius*1000},{lat},{lon});node[\"communication:mobile_phone\"=\"yes\"](around:{radius*1000},{lat},{lon});way[\"communication:mobile_phone\"=\"yes\"](around:{radius*1000},{lat},{lon});node[\"communication:radio\"=\"yes\"](around:{radius*1000},{lat},{lon});way[\"communication:radio\"=\"yes\"](around:{radius*1000},{lat},{lon}););out center tags;"""
                req=urllib.request.Request("https://overpass-api.de/api/interpreter",data=q.encode(),headers={"User-Agent":"NetGuard-Pro/12.0"})
                with urllib.request.urlopen(req,timeout=25) as r:data=json.loads(r.read().decode("utf-8"))
                rows=[]
                for e in data.get("elements",[]):
                    p=e.get("center",e);la=p.get("lat");lo=p.get("lon")
                    if la is None or lo is None:continue
                    d=self.haversine(lat,lon,la,lo);tags=e.get("tags",{})
                    rows.append({"name":tags.get("name",tags.get("operator","Radio mast")),"type":tags.get("tower:type",tags.get("man_made","mast")),"distance":d,"lat":la,"lon":lo})
                rows.sort(key=lambda x:x["distance"]);self.root.after(0,lambda:self.apply_towers(rows))
            except Exception as e:self.root.after(0,lambda err=str(e):self.alert("WARN","CELL TOWERS",err))
        threading.Thread(target=work,daemon=True).start()

    @staticmethod
    def haversine(lat1,lon1,lat2,lon2):
        r=6371.0088;a=math.radians(lat2-lat1);b=math.radians(lon2-lon1);x=math.sin(a/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(b/2)**2
        return r*2*math.asin(math.sqrt(x))

    def apply_towers(self,rows):
        self.towers=rows
        self.tower_tree.delete(*self.tower_tree.get_children())
        for x in rows[:500]:self.tower_tree.insert("","end",values=(x["name"],x["type"],f'{x["distance"]:.2f} km',f'{x["lat"]:.5f}',f'{x["lon"]:.5f}'))
        if hasattr(self,"dashboard_tower_tree"):
            self.dashboard_tower_tree.delete(*self.dashboard_tower_tree.get_children())
            for x in rows[:20]: self.dashboard_tower_tree.insert("","end",values=(x["name"],x["type"],f'{x["distance"]:.1f} km'))
        self.space_map_status.set(f"Nearby telecom towers: {len(rows)} within {self.obs_radius.get()} km.")
        self.draw_space_map()
        self.draw_dashboard_space_map()
        self.log(f"Public mast map: {len(rows)} objects")

    def track_satellites(self):
        obs=self._observer()
        if not obs:return
        lat,lon,_=obs
        def work():
            try:
                try:
                    from skyfield.api import load, EarthSatellite, wgs84
                except ImportError:
                    raise RuntimeError("Skyfield is not installed. Run: pip install skyfield")
                urls=["https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle","https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"]
                lines=[]
                for url in urls:
                    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"NetGuard-Pro/12.0"}),timeout=20) as r:lines.extend(r.read().decode("utf-8",errors="ignore").splitlines())
                ts=load.timescale();t=ts.now();obspos=wgs84.latlon(lat,lon)
                rows=[]
                i=0
                while i+2<len(lines):
                    name=lines[i].strip();l1=lines[i+1].strip();l2=lines[i+2].strip()
                    if l1.startswith("1 ") and l2.startswith("2 "):
                        try:
                            sat=EarthSatellite(l1,l2,name,ts);difference=sat-obspos;alt,az,distance=difference.at(t).altaz()
                            rows.append({"name":name,"alt_km":distance.km,"az":az.degrees,"el":alt.degrees,"status":"VISIBLE" if alt.degrees>0 else "BELOW HORIZON"})
                        except Exception:pass
                        i+=3
                    else:i+=1
                rows.sort(key=lambda x:(x["status"]!="VISIBLE",-x["el"]));self.root.after(0,lambda:self.apply_satellites(rows))
            except Exception as e:self.root.after(0,lambda err=str(e):self.alert("WARN","SATELLITES",err))
        threading.Thread(target=work,daemon=True).start()

    def apply_satellites(self,rows):
        self.satellites=rows;self.sat_tree.delete(*self.sat_tree.get_children())
        visible_rows=[x for x in rows if x.get("el",-90)>0]
        for x in visible_rows[:500]:self.sat_tree.insert("","end",values=(x["name"],f'{x["alt_km"]:.0f}',f'{x["az"]:.1f}°',f'{x["el"]:.1f}°',"VISIBLE"))
        if hasattr(self,"dashboard_sat_tree"):
            self.dashboard_sat_tree.delete(*self.dashboard_sat_tree.get_children())
            for x in visible_rows[:20]: self.dashboard_sat_tree.insert("","end",values=(x["name"],f'{x["alt_km"]:.0f} km',f'{x["el"]:.0f}°'))
        visible=len(visible_rows)
        self.space_map_status.set(f"Nearby telecom towers: {len(self.towers)} | Visible satellites above horizon: {visible}.")
        self.draw_space_map()
        self.draw_dashboard_space_map()
        self.log(f"Satellite catalog: {len(rows)} public orbital objects; {visible} visible")

    def clear_space_data(self):
        self.towers=[];self.satellites=[];self.tower_tree.delete(*self.tower_tree.get_children());self.sat_tree.delete(*self.sat_tree.get_children())
        if hasattr(self,"dashboard_tower_tree"): self.dashboard_tower_tree.delete(*self.dashboard_tower_tree.get_children())
        if hasattr(self,"dashboard_sat_tree"): self.dashboard_sat_tree.delete(*self.dashboard_sat_tree.get_children())
        self.space_map_status.set("Cleared. Press SCAN TOWERS and SHOW SATELLITES to refresh nearby results.");self.draw_space_map();self.draw_dashboard_space_map()

    def network_analysis_ui(self):
        top=tk.Frame(self.network_analysis,bg=self.BG);top.pack(fill="x",pady=6)
        tk.Label(top,text="◈ NETWORK ANALYSIS",bg=self.BG,fg=self.CYAN,font=("Consolas",15,"bold")).pack(side="left")
        tk.Label(top,text="Diagnostics for networks and hosts you own or are authorized to test",bg=self.BG,fg=self.MUTED,font=("Segoe UI",9)).pack(side="left",padx=14)
        body=tk.Frame(self.network_analysis,bg=self.BG);body.pack(fill="both",expand=True)
        self.na_host=tk.Entry(body,bg="#07111a",fg=self.TEXT,insertbackground=self.CYAN,relief="flat",width=28);self.na_host.insert(0,"example.com")
        self.na_cidr=tk.Entry(body,bg="#07111a",fg=self.TEXT,insertbackground=self.CYAN,relief="flat",width=24);self.na_cidr.insert(0,"192.168.1.0/24")
        p1=self.panel(body,"DNS / ROUTE / TLS");p1.pack(side="left",fill="both",expand=True,padx=(5,3),pady=5)
        row=tk.Frame(p1,bg=self.PANEL);row.pack(fill="x",padx=10,pady=10);self.na_host.pack(in_=row,side="left",padx=4)
        for text,fn in [("DNS",self.na_dns),("TRACEROUTE",self.na_trace),("TLS",self.na_tls)]:tk.Button(row,text=text,command=fn,bg="#123047",fg=self.CYAN,relief="flat",padx=10,pady=6).pack(side="left",padx=4)
        p2=self.panel(body,"SUBNET CALCULATOR");p2.pack(side="left",fill="both",expand=True,padx=(3,5),pady=5)
        row2=tk.Frame(p2,bg=self.PANEL);row2.pack(fill="x",padx=10,pady=10);self.na_cidr.pack(in_=row2,side="left",padx=4);tk.Button(row2,text="CALCULATE",command=self.na_subnet,bg="#123047",fg=self.GREEN,relief="flat",padx=10,pady=6).pack(side="left",padx=4)
        out=self.panel(self.network_analysis,"ANALYSIS OUTPUT");out.pack(fill="both",expand=True,padx=5,pady=5);self.na_out=tk.Text(out,bg="#050a10",fg=self.TEXT,relief="flat",font=("Consolas",10));self.na_out.pack(fill="both",expand=True,padx=8,pady=8)

    def na_write(self,text):self.na_out.delete("1.0","end");self.na_out.insert("1.0",text)

    def na_dns(self):
        host=self.na_host.get().strip()
        def work():
            try:
                infos=socket.getaddrinfo(host,None);ips=sorted({x[4][0] for x in infos});self.root.after(0,lambda:self.na_write("DNS RESULTS\n\n"+"\n".join(ips)))
            except Exception as e:self.root.after(0,lambda:self.na_write(f"DNS ERROR\n\n{e}"))
        threading.Thread(target=work,daemon=True).start()

    def na_trace(self):
        host=self.na_host.get().strip()
        def work():
            cmd=["tracert","-d",host] if platform.system().lower()=="windows" else ["traceroute","-n",host]
            try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=45);out=r.stdout or r.stderr
            except Exception as e:out=str(e)
            self.root.after(0,lambda:self.na_write(out))
        threading.Thread(target=work,daemon=True).start()

    def na_tls(self):
        host=self.na_host.get().strip()
        def work():
            try:
                ctx=ssl.create_default_context();t0=time.perf_counter()
                with socket.create_connection((host,443),timeout=8) as raw:
                    with ctx.wrap_socket(raw,server_hostname=host) as sck:
                        cert=sck.getpeercert();elapsed=(time.perf_counter()-t0)*1000;subject=dict(x[0] for x in cert.get("subject",()))
                        issuer=dict(x[0] for x in cert.get("issuer",()))
                        out=f"TLS VERSION: {sck.version()}\nCIPHER: {sck.cipher()[0]}\nLATENCY: {elapsed:.1f} ms\nSUBJECT: {subject.get('commonName','-')}\nISSUER: {issuer.get('commonName','-')}\nEXPIRES: {cert.get('notAfter','-')}"
            except Exception as e:out=f"TLS ERROR\n\n{e}"
            self.root.after(0,lambda:self.na_write(out))
        threading.Thread(target=work,daemon=True).start()

    def na_subnet(self):
        try:
            n=ipaddress.ip_network(self.na_cidr.get().strip(),strict=False);hosts=list(n.hosts())
            out=f"NETWORK: {n}\nVERSION: IPv{n.version}\nNETMASK: {n.netmask}\nWILDCARD: {n.hostmask}\nNETWORK: {n.network_address}\nBROADCAST: {getattr(n,'broadcast_address','-')}\nPREFIX: /{n.prefixlen}\nUSABLE HOSTS: {max(len(hosts),0)}"
            if hosts:out+=f"\nFIRST HOST: {hosts[0]}\nLAST HOST: {hosts[-1]}"
        except Exception as e:out=f"SUBNET ERROR\n\n{e}"
        self.na_write(out)

    def targets_ui(self):
        top = tk.Frame(self.targets, bg=self.BG)
        top.pack(fill="x", pady=6)
        tk.Label(
            top, text="◎ AUTHORIZED TARGETS",
            bg=self.BG, fg=self.CYAN,
            font=("Consolas", 15, "bold")
        ).pack(side="left")
        tk.Label(
            top,
            text="Only targets explicitly entered here are tested.",
            bg=self.BG, fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(side="left", padx=15)

        box = self.panel(self.targets, "TARGET ALLOWLIST")
        box.pack(fill="x", pady=5)

        row = tk.Frame(box, bg=self.PANEL)
        row.pack(fill="x", padx=10, pady=10)

        tk.Label(row, text="HOST/IP", bg=self.PANEL, fg=self.MUTED).pack(side="left")
        self.target_host = tk.Entry(
            row, bg="#07111a", fg=self.TEXT,
            insertbackground=self.CYAN, relief="flat", width=28
        )
        self.target_host.pack(side="left", padx=7)

        tk.Label(row, text="PORT", bg=self.PANEL, fg=self.MUTED).pack(side="left", padx=(15, 3))
        self.target_port = tk.Entry(
            row, bg="#07111a", fg=self.TEXT,
            insertbackground=self.CYAN, relief="flat", width=8
        )
        self.target_port.insert(0, "443")
        self.target_port.pack(side="left")

        tk.Button(
            row, text="ADD TARGET",
            command=self.add_target,
            bg="#123047", fg=self.GREEN,
            relief="flat", padx=12, pady=6
        ).pack(side="left", padx=7)

        tk.Button(
            row, text="REMOVE SELECTED",
            command=self.remove_target,
            bg="#2b1822", fg=self.RED,
            relief="flat", padx=12, pady=6
        ).pack(side="left", padx=3)

        tk.Button(
            row, text="TEST SELECTED",
            command=self.test_selected_target,
            bg="#123047", fg=self.CYAN,
            relief="flat", padx=12, pady=6
        ).pack(side="left", padx=3)

        info = self.panel(self.targets, "ALLOWLIST")
        info.pack(fill="both", expand=True, pady=5)

        cols = ("host", "port", "status")
        self.target_tree = ttk.Treeview(
            info, columns=cols, show="headings"
        )
        for c, w in zip(cols, [360, 120, 180]):
            self.target_tree.heading(c, text=c.upper())
            self.target_tree.column(c, width=w)
        self.target_tree.pack(fill="both", expand=True, padx=8, pady=8)

        self.authorized_targets = []

    def add_target(self):
        host = self.target_host.get().strip()
        try:
            port = int(self.target_port.get())
            if not host or not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid target",
                "Enter a hostname/IP and a port from 1 to 65535."
            )
            return

        item = (host, port, "NOT TESTED")
        if (host, port) not in [(x[0], x[1]) for x in self.authorized_targets]:
            self.authorized_targets.append(item)
            self.target_tree.insert("", "end", values=item)
            self.log(f"Authorized target added: {host}:{port}")

    def remove_target(self):
        sel = self.target_tree.selection()
        if not sel:
            return
        for item_id in sel:
            vals = self.target_tree.item(item_id, "values")
            self.authorized_targets = [
                x for x in self.authorized_targets
                if not (str(x[0]) == str(vals[0]) and int(x[1]) == int(vals[1]))
            ]
            self.target_tree.delete(item_id)

    def test_selected_target(self):
        sel = self.target_tree.selection()
        if not sel:
            messagebox.showinfo("Target", "Select an authorized target first.")
            return

        vals = self.target_tree.item(sel[0], "values")
        host, port = vals[0], int(vals[1])

        def work():
            started = time.perf_counter()
            try:
                with socket.create_connection((host, port), timeout=5):
                    elapsed = (time.perf_counter() - started) * 1000
                    status = f"OPEN / REACHABLE ({elapsed:.1f} ms)"
            except Exception as e:
                status = f"UNREACHABLE / CLOSED: {e}"

            self.root.after(
                0,
                lambda: self.update_target_status(sel[0], status)
            )

        threading.Thread(target=work, daemon=True).start()

    def update_target_status(self, item_id, status):
        vals = self.target_tree.item(item_id, "values")
        self.target_tree.item(
            item_id,
            values=(vals[0], vals[1], status)
        )
        self.log(f"Authorized target test: {vals[0]}:{vals[1]} -> {status}")

                                                               
                     
                                                               
    def bluetooth_ui(self):
        top = tk.Frame(self.bluetooth, bg=self.BG)
        top.pack(fill="x", pady=6)
        tk.Label(
            top, text="◉ BLUETOOTH RADAR",
            bg=self.BG, fg=self.CYAN,
            font=("Consolas", 15, "bold")
        ).pack(side="left")
        tk.Button(
            top, text="SCAN",
            command=self.scan_bluetooth,
            bg="#123047", fg=self.CYAN, relief="flat",
            padx=16, pady=7
        ).pack(side="right")

        box = self.panel(
            self.bluetooth,
            "VISIBLE / PAIRED BLUETOOTH DEVICES"
        )
        box.pack(fill="both", expand=True, pady=5)

        cols = ("name", "status", "address")
        self.bt_tree = ttk.Treeview(
            box, columns=cols, show="headings"
        )
        for c, w in zip(cols, [320, 160, 260]):
            self.bt_tree.heading(c, text=c.upper())
            self.bt_tree.column(c, width=w)
        self.bt_tree.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(
            box,
            text="Windows may restrict nearby-device discovery depending on Bluetooth permissions and adapter support.",
            bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=10, pady=(0, 8))

    def scan_bluetooth(self):
        threading.Thread(
            target=self._bluetooth_worker,
            daemon=True
        ).start()

    def _bluetooth_worker(self):
        if platform.system().lower() != "windows":
            self.root.after(
                0, lambda: self.alert(
                    "INFO", "BLUETOOTH",
                    "This built-in scanner is implemented for Windows."
                )
            )
            return

                                                                 
                                                                 
        ps = (
            "Get-PnpDevice -Class Bluetooth -PresentOnly | "
            "Select-Object FriendlyName,Status,InstanceId | "
            "ConvertTo-Json -Compress"
        )
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=15
            )
            raw = r.stdout.strip()
            if not raw:
                data = []
            else:
                parsed = json.loads(raw)
                data = parsed if isinstance(parsed, list) else [parsed]

            rows = []
            for x in data:
                rows.append({
                    "name": x.get("FriendlyName", "Unknown"),
                    "status": x.get("Status", "Unknown"),
                    "address": x.get("InstanceId", "")
                })

            self.root.after(0, lambda: self.apply_bluetooth(rows))
        except Exception as e:
            self.root.after(
                0, lambda: self.alert(
                    "WARN", "BLUETOOTH", str(e)
                )
            )

    def apply_bluetooth(self, rows):
        for i in self.bt_tree.get_children():
            self.bt_tree.delete(i)
        for x in rows:
            self.bt_tree.insert(
                "", "end",
                values=(x["name"], x["status"], x["address"])
            )
        self.log(f"Bluetooth enumeration: {len(rows)} local/visible entries.")

                                                               
                     
                                                               
    def camera_ui(self):
        top = tk.Frame(self.camera, bg=self.BG)
        top.pack(fill="x", pady=6)
        tk.Label(
            top, text="◉ CAMERA SECURITY MONITOR",
            bg=self.BG, fg=self.CYAN,
            font=("Consolas", 15, "bold")
        ).pack(side="left")
        tk.Button(
            top, text="CHECK LOCAL CAMERAS",
            command=self.camera_check,
            bg="#123047", fg=self.GREEN, relief="flat",
            padx=16, pady=7
        ).pack(side="right")

        body = self.panel(
            self.camera,
            "AUTHORIZED / LOCAL CAMERA CHECK"
        )
        body.pack(fill="both", expand=True, pady=5)

        self.camera_text = tk.Text(
            body, bg="#050a10", fg=self.TEXT,
            relief="flat", font=("Consolas", 10)
        )
        self.camera_text.pack(fill="both", expand=True, padx=10, pady=10)

        self.camera_text.insert(
            "1.0",
            "This module checks only camera hardware exposed to this computer.\n"
            "It does not search the Internet/LAN for other people's cameras.\n\n"
            "Press CHECK LOCAL CAMERAS to inspect the Windows camera devices."
        )
        self.camera_text.config(state="disabled")

    def camera_check(self):
        def work():
            lines = []
            if platform.system().lower() == "windows":
                ps = (
                    "Get-PnpDevice -Class Camera -PresentOnly | "
                    "Select-Object FriendlyName,Status,InstanceId | "
                    "ConvertTo-Json -Compress"
                )
                try:
                    r = subprocess.run(
                        ["powershell", "-NoProfile", "-Command", ps],
                        capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=15
                    )
                    raw = r.stdout.strip()
                    if raw:
                        parsed = json.loads(raw)
                        parsed = parsed if isinstance(parsed, list) else [parsed]
                        for x in parsed:
                            lines.append(
                                f'{x.get("FriendlyName","Unknown")} | '
                                f'{x.get("Status","Unknown")}'
                            )
                    else:
                        lines.append("No present camera devices reported.")
                except Exception as e:
                    lines.append(f"Camera query failed: {e}")
            else:
                lines.append(
                    "Local camera enumeration is currently implemented "
                    "for Windows in this build."
                )

            text = "\n".join(lines)
            self.root.after(
                0,
                lambda: self.camera_result(text)
            )

        threading.Thread(target=work, daemon=True).start()

    def camera_result(self, text):
        self.camera_text.config(state="normal")
        self.camera_text.delete("1.0", "end")
        self.camera_text.insert("1.0", text)
        self.camera_text.config(state="disabled")
        self.log("Local camera security check completed.")

    def security_ui(self):
        tk.Label(self.sec,text="🛡 DEFENSIVE SECURITY TOOLKIT",bg=self.BG,fg=self.CYAN,font=("Consolas",15,"bold")).pack(anchor="w",pady=7)
        tk.Label(self.sec,text="Local diagnostics only — no exploitation, credential theft or offensive automation.",
                 bg=self.BG,fg=self.MUTED,font=("Segoe UI",9)).pack(anchor="w")
        grid=tk.Frame(self.sec,bg=self.BG);grid.pack(fill="both",expand=True,pady=10)
        tools=[("FIREWALL","Windows Firewall status",self.firewall),("DNS CHECK","Resolve example.com",self.dns),
               ("LOCAL SECURITY","CPU/RAM/system snapshot",self.local_security),("ADAPTERS","Interface state",self.adapters),
               ("PUBLIC IP","Show public address",self.public_ip),("BASELINE","Run safe checks",self.baseline_check)]
        for i,(name,desc,fn) in enumerate(tools):
            r,col=divmod(i,3);f=self.panel(grid);f.grid(row=r,column=col,sticky="nsew",padx=5,pady=5)
            tk.Label(f,text=name,bg=self.PANEL,fg=self.CYAN,font=("Consolas",12,"bold")).pack(anchor="w",padx=12,pady=(12,3))
            tk.Label(f,text=desc,bg=self.PANEL,fg=self.MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=12)
            tk.Button(f,text="RUN",command=fn,bg="#102b3e",fg=self.GREEN,relief="flat",padx=14,pady=6).pack(anchor="e",padx=12,pady=12)
        for r in range(2):grid.rowconfigure(r,weight=1)
        for c in range(3):grid.columnconfigure(c,weight=1)

    def result(self,title,text):
        w=tk.Toplevel(self.root);w.title(title);w.geometry("700x450");w.configure(bg=self.BG)
        tk.Label(w,text="// "+title,bg=self.BG,fg=self.CYAN,font=("Consolas",14,"bold")).pack(anchor="w",padx=14,pady=12)
        t=tk.Text(w,bg="#050a10",fg=self.TEXT,relief="flat",font=("Consolas",10));t.pack(fill="both",expand=True,padx=14,pady=(0,14));t.insert("1.0",text);t.config(state="disabled")

    def firewall(self):
        if platform.system().lower()!="windows": return self.alert("INFO","FIREWALL","Windows Firewall check is supported on Windows.")
        def work():
            try:
                r=subprocess.run(["netsh","advfirewall","show","allprofiles"],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=10)
                self.root.after(0,lambda:self.result("FIREWALL STATUS",r.stdout or r.stderr))
            except Exception as e:self.root.after(0,lambda err=str(e):self.alert("WARN","FIREWALL",err))
        threading.Thread(target=work,daemon=True).start()

    def dns(self):
        try:
            t=time.perf_counter();ip=socket.gethostbyname("example.com");ms=(time.perf_counter()-t)*1000
            self.result("DNS CHECK",f"example.com -> {ip}\nResolution: {ms:.1f} ms");self.alert("OK","DNS",f"Resolved {ip}")
        except Exception as e:self.alert("WARN","DNS",str(e))

    def local_security(self):
        self.result("LOCAL SECURITY",f"OS: {platform.platform()}\nHost: {socket.gethostname()}\nPython: {platform.python_version()}\nCPU: {psutil.cpu_percent(.2):.1f}%\nRAM: {psutil.virtual_memory().percent:.1f}%\nInterfaces: {len(psutil.net_if_addrs())}")

    def adapters(self):
        s=psutil.net_if_stats();self.result("ADAPTERS","\n".join(f"{n}: {'UP' if x.isup else 'DOWN'} | {x.speed} Mbps | MTU {x.mtu}" for n,x in s.items()))

    def public_ip(self):
        def work():
            try:
                from urllib.request import urlopen
                with urlopen("https://api.ipify.org",timeout=5) as r: ip=r.read().decode().strip()
                self.root.after(0,lambda:self.result("PUBLIC IP",ip))
            except Exception as e:self.root.after(0,lambda err=str(e):self.alert("INFO","PUBLIC IP",err))
        threading.Thread(target=work,daemon=True).start()

    def baseline_check(self):
        self.firewall();self.dns();self.local_security();self.adapters()


                                                               
                                         
                                                               
    def security_lab_ui(self):
        top=tk.Frame(self.security_lab,bg=self.BG); top.pack(fill="x",pady=6)
        tk.Label(top,text="⚙ ETHICAL SECURITY LAB",bg=self.BG,fg=self.CYAN,
                 font=("Consolas",15,"bold")).pack(side="left")
        tk.Label(top,text="Private/authorized targets only",bg=self.BG,fg=self.MUTED,
                 font=("Segoe UI",9)).pack(side="left",padx=15)

        row=tk.Frame(self.security_lab,bg=self.BG); row.pack(fill="x",pady=5)
        box=self.panel(row,"TARGET")
        box.pack(fill="x",expand=True)
        tk.Label(box,text="PRIVATE IP",bg=self.PANEL,fg=self.MUTED).pack(side="left",padx=10,pady=10)
        self.lab_ip=tk.Entry(box,bg="#07111a",fg=self.TEXT,insertbackground=self.CYAN,
                             relief="flat",width=20)
        self.lab_ip.insert(0,"192.168.1.1"); self.lab_ip.pack(side="left",padx=6,pady=10)
        tk.Button(box,text="PORT CHECK",command=self.security_lab_ports,bg="#123047",
                  fg=self.CYAN,relief="flat").pack(side="left",padx=5)
        tk.Button(box,text="DNS CHECK",command=self.security_lab_dns,bg="#123047",
                  fg=self.CYAN,relief="flat").pack(side="left",padx=5)

        out=self.panel(self.security_lab,"RESULTS"); out.pack(fill="both",expand=True,pady=5)
        cols=("check","result","detail")
        self.lab_tree=ttk.Treeview(out,columns=cols,show="headings")
        for c,w in zip(cols,[180,180,520]):
            self.lab_tree.heading(c,text=c.upper()); self.lab_tree.column(c,width=w)
        self.lab_tree.pack(fill="both",expand=True,padx=8,pady=8)

        note=tk.Label(self.security_lab,
                      text="Checks are connectivity/configuration diagnostics; no password attacks or exploitation.",
                      bg=self.BG,fg=self.MUTED,font=("Segoe UI",9))
        note.pack(anchor="w",pady=4)

    def _private_target(self):
        try:
            a=ipaddress.ip_address(self.lab_ip.get().strip())
            if not a.is_private: raise ValueError
            return str(a)
        except Exception:
            messagebox.showwarning("Target","Enter a valid private IP address.")
            return None

    def security_lab_ports(self):
        ip=self._private_target()
        if not ip: return
        for i in self.lab_tree.get_children(): self.lab_tree.delete(i)
        common=[(22,"SSH"),(53,"DNS"),(80,"HTTP"),(443,"HTTPS"),(445,"SMB"),(3389,"RDP")]
        def work():
            rows=[]
            for p,name in common:
                state="CLOSED / FILTERED"
                try:
                    with socket.create_connection((ip,p),timeout=1.2):
                        state="OPEN"
                except: pass
                rows.append(("TCP "+str(p),state,name))
            self.root.after(0,lambda:[self.lab_tree.insert("", "end",values=r) for r in rows])
        threading.Thread(target=work,daemon=True).start()

    def security_lab_dns(self):
        host=self.host.get().strip() if hasattr(self,"host") else "example.com"
        for i in self.lab_tree.get_children(): self.lab_tree.delete(i)
        try:
            infos=socket.getaddrinfo(host,None)
            ips=sorted(set(x[4][0] for x in infos))
            self.lab_tree.insert("", "end",values=("DNS", "RESOLVED", ", ".join(ips)))
        except Exception as e:
            self.lab_tree.insert("", "end",values=("DNS", "FAILED", str(e)))


                                                               
                                           
                                                               
    def web_security_tools_ui(self):
        top=tk.Frame(self.web_security,bg=self.BG); top.pack(fill="x",pady=6)
        tk.Label(top,text="WEB SECURITY TOOLS",bg=self.BG,fg=self.CYAN,
                 font=("Consolas",15,"bold")).pack(side="left")
        tk.Label(top,text="Use on systems/services you are authorized to test",
                 bg=self.BG,fg=self.MUTED).pack(side="left",padx=15)

        bar=tk.Frame(self.web_security,bg=self.BG); bar.pack(fill="x",pady=5)
        tk.Label(bar,text="HOST",bg=self.BG,fg=self.MUTED).pack(side="left")
        self.web_host=tk.Entry(bar,bg="#07111a",fg=self.TEXT,insertbackground=self.CYAN,
                               relief="flat",width=34)
        self.web_host.insert(0,"example.com"); self.web_host.pack(side="left",padx=7)
        tk.Button(bar,text="TLS CHECK",command=self.tls_check,bg="#123047",
                  fg=self.CYAN,relief="flat").pack(side="left",padx=4)
        tk.Button(bar,text="SECURITY HEADERS",command=self.header_audit,bg="#123047",
                  fg=self.CYAN,relief="flat").pack(side="left",padx=4)

        self.web_tree=ttk.Treeview(self.web_security,
                                   columns=("check","status","detail"),show="headings")
        for c,w in [("check",220),("status",180),("detail",600)]:
            self.web_tree.heading(c,text=c.upper()); self.web_tree.column(c,width=w)
        self.web_tree.pack(fill="both",expand=True,padx=4,pady=8)

    def _web_host(self):
        h=self.web_host.get().strip()
        h=re.sub(r"^https?://","",h).split("/")[0]
        return h

    def tls_check(self):
        host=self._web_host()
        for i in self.web_tree.get_children(): self.web_tree.delete(i)
        def work():
            rows=[]
            try:
                ctx=ssl.create_default_context()
                with socket.create_connection((host,443),timeout=5) as raw:
                    with ctx.wrap_socket(raw,server_hostname=host) as s:
                        cert=s.getpeercert()
                        cipher=s.cipher()
                        rows.append(("TLS","CONNECTED",f"Version: {s.version()}"))
                        rows.append(("Cipher","OK",str(cipher[0]) if cipher else "unknown"))
                        rows.append(("Subject","INFO",str(cert.get("subject","unknown"))))
                        rows.append(("Issuer","INFO",str(cert.get("issuer","unknown"))))
                        rows.append(("Expiry","INFO",str(cert.get("notAfter","unknown"))))
            except Exception as e:
                rows.append(("TLS","FAILED",str(e)))
            self.root.after(0,lambda:[self.web_tree.insert("", "end",values=r) for r in rows])
        threading.Thread(target=work,daemon=True).start()

    def header_audit(self):
        import urllib.request
        host=self._web_host()
        if not host: return
        for i in self.web_tree.get_children(): self.web_tree.delete(i)
        def work():
            rows=[]
            try:
                req=urllib.request.Request("https://"+host,method="GET",
                                           headers={"User-Agent":"NetGuard-Pro/8"})
                with urllib.request.urlopen(req,timeout=7) as r:
                    headers={k.lower():v for k,v in r.headers.items()}
                checks=[
                    ("Strict-Transport-Security","hsts"),
                    ("Content-Security-Policy","csp"),
                    ("X-Content-Type-Options","x-content-type-options"),
                    ("X-Frame-Options","x-frame-options"),
                    ("Referrer-Policy","referrer-policy"),
                ]
                for label,key in checks:
                    if key in headers:
                        rows.append((label,"PRESENT",headers[key][:180]))
                    else:
                        rows.append((label,"NOT FOUND","Consider reviewing this header"))
            except Exception as e:
                rows.append(("HTTP","FAILED",str(e)))
            self.root.after(0,lambda:[self.web_tree.insert("", "end",values=r) for r in rows])
        threading.Thread(target=work,daemon=True).start()

                                                               
                                            
                                                               
    def signal_audio_ui(self):
        top=tk.Frame(self.signal_audio,bg=self.BG); top.pack(fill="x",pady=6)
        tk.Label(top,text="◉ SIGNAL AUDIO VISUALIZER",bg=self.BG,fg=self.CYAN,
                 font=("Consolas",15,"bold")).pack(side="left")
        tk.Label(top,text="Synthetic audio from Wi-Fi RSSI metadata",bg=self.BG,fg=self.MUTED,
                 font=("Segoe UI",9)).pack(side="left",padx=15)

        controls=tk.Frame(self.signal_audio,bg=self.BG); controls.pack(fill="x",pady=5)
        tk.Button(controls,text="SCAN",command=self.scan_wifi,bg="#123047",fg=self.CYAN,
                  relief="flat",padx=14,pady=7).pack(side="left",padx=3)
        tk.Button(controls,text="START AUDIO",command=self.start_signal_audio,bg="#123047",
                  fg=self.GREEN,relief="flat",padx=14,pady=7).pack(side="left",padx=3)
        tk.Button(controls,text="STOP",command=self.stop_signal_audio,bg="#123047",
                  fg="#ff8da5",relief="flat",padx=14,pady=7).pack(side="left",padx=3)

        body=tk.Frame(self.signal_audio,bg=self.BG); body.pack(fill="both",expand=True)
        left=self.panel(body,"SIGNAL HISTORY"); left.pack(side="left",fill="both",expand=True,padx=(0,5))
        self.signal_canvas=tk.Canvas(left,bg="#050a10",highlightthickness=0)
        self.signal_canvas.pack(fill="both",expand=True,padx=8,pady=8)
        self.signal_canvas.bind("<Configure>",lambda e:self.draw_signal_audio_graph())

        right=self.panel(body,"SIGNAL → AUDIO"); right.pack(side="right",fill="both",expand=True,padx=(5,0))
        cols=("ssid","signal","tone")
        self.signal_tree=ttk.Treeview(right,columns=cols,show="headings")
        for c,w in zip(cols,[210,100,170]):
            self.signal_tree.heading(c,text=c.upper()); self.signal_tree.column(c,width=w)
        self.signal_tree.pack(fill="both",expand=True,padx=8,pady=8)
        self.audio_status=tk.StringVar(value="● AUDIO STOPPED")
        tk.Label(right,textvariable=self.audio_status,bg=self.PANEL,fg=self.CYAN,
                 font=("Consolas",10,"bold")).pack(anchor="w",padx=10,pady=8)
        self.signal_history=[]; self.audio_running=False; self.audio_thread=None

    def start_signal_audio(self):
        if self.audio_running: return
        self.audio_running=True
        self.audio_status.set("● AUDIO RUNNING")
        self.audio_thread=threading.Thread(target=self._signal_audio_worker,daemon=True)
        self.audio_thread.start()

    def stop_signal_audio(self):
        self.audio_running=False
        self.audio_status.set("● AUDIO STOPPED")

    def _signal_audio_worker(self):
        while self.audio_running:
            try:
                values=[n.get("signal",0) for n in self.wifi if isinstance(n.get("signal",0),(int,float))]
                avg=sum(values)/len(values) if values else 0
                hz=int(220+(max(0,min(100,avg))/100)*660)
                self.root.after(0,lambda a=avg,h=hz:self.update_signal_audio(a,h))
                if platform.system().lower()=="windows":
                    try:
                        import winsound
                        winsound.Beep(hz,180)
                    except Exception:
                        pass
                time.sleep(0.35)
            except Exception:
                time.sleep(0.5)

    def update_signal_audio(self,avg,hz):
        self.signal_history.append(avg)
        self.signal_history=self.signal_history[-80:]
        self.audio_status.set(f"● AUDIO RUNNING  |  AVG RSSI {avg:.0f}%  |  TONE {hz} Hz")
        self.draw_signal_audio_graph()
        self.signal_tree.delete(*self.signal_tree.get_children())
        for n in self.wifi[:30]:
            sig=n.get("signal",0)
            tone=int(220+(max(0,min(100,sig))/100)*660)
            self.signal_tree.insert("", "end",values=(n.get("ssid","<hidden>"),f"{sig}%",f"{tone} Hz"))

    def draw_signal_audio_graph(self):
        if not hasattr(self,"signal_canvas"): return
        c=self.signal_canvas; c.delete("all")
        w=max(c.winfo_width(),420); h=max(c.winfo_height(),300)
        for i in range(1,6):
            y=20+(h-40)*i/6
            c.create_line(20,y,w-15,y,fill="#102532")
        vals=self.signal_history
        if len(vals)<2: return
        pts=[]
        for i,v in enumerate(vals):
            x=25+(w-45)*i/max(1,len(vals)-1)
            y=h-20-(max(0,min(100,v))/100)*(h-40)
            pts.extend([x,y])
        c.create_line(*pts,fill=self.CYAN,width=2,smooth=True)

    def network_ui(self):
        f=self.panel(self.net,"INTERFACES / IP");f.pack(fill="both",expand=True,pady=5)
        cols=("interface","address","mask","family");self.itree=ttk.Treeview(f,columns=cols,show="headings")
        for c,w in zip(cols,[230,320,270,100]):self.itree.heading(c,text=c.upper());self.itree.column(c,width=w)
        self.itree.pack(fill="both",expand=True,padx=8,pady=8)

    def tests_ui(self):
        f=self.panel(self.tests,"CONNECTIVITY TESTS");f.pack(fill="x",pady=5)
        row=tk.Frame(f,bg=self.PANEL);row.pack(fill="x",padx=10,pady=10)
        tk.Label(row,text="HOST/IP",bg=self.PANEL,fg=self.MUTED).pack(side="left")
        self.host=tk.Entry(row,bg="#07111a",fg=self.TEXT,insertbackground=self.CYAN,relief="flat",width=28);self.host.insert(0,"example.com");self.host.pack(side="left",padx=7)
        tk.Button(row,text="PING",command=self.ping,bg="#123047",fg=self.CYAN,relief="flat").pack(side="left",padx=4)
        tk.Label(row,text="PORT",bg=self.PANEL,fg=self.MUTED).pack(side="left",padx=(20,3))
        self.port=tk.Entry(row,bg="#07111a",fg=self.TEXT,relief="flat",width=8);self.port.insert(0,"443");self.port.pack(side="left")
        tk.Button(row,text="TCP TEST",command=self.tcp,bg="#123047",fg=self.GREEN,relief="flat").pack(side="left",padx=5)
        o=self.panel(self.tests,"OUTPUT");o.pack(fill="both",expand=True)
        self.out=tk.Text(o,bg="#050a10",fg=self.TEXT,relief="flat",font=("Consolas",10));self.out.pack(fill="both",expand=True,padx=8,pady=8)

    def ping(self):
        h=self.host.get().strip()
        def work():
            cmd=["ping","-n","4",h] if platform.system().lower()=="windows" else ["ping","-c","4",h]
            try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=15);s=r.stdout or r.stderr
            except Exception as e:s=str(e)
            self.root.after(0,lambda:self.write(s))
        threading.Thread(target=work,daemon=True).start()

    def tcp(self):
        h=self.host.get().strip()
        try:p=int(self.port.get());assert 1<=p<=65535
        except: return messagebox.showwarning("Port","Port must be 1-65535.")
        def work():
            try:
                t=time.perf_counter()
                with socket.create_connection((h,p),timeout=5):pass
                s=f"Connection successful: {h}:{p}\nLatency: {(time.perf_counter()-t)*1000:.1f} ms"
            except Exception as e:s=f"Connection failed: {h}:{p}\n{e}"
            self.root.after(0,lambda:self.write(s))
        threading.Thread(target=work,daemon=True).start()

    def write(self,s):self.out.insert("end","\n"+s+"\n");self.out.see("end")

    def connections_ui(self):
        f=self.panel(self.conn,"ACTIVE CONNECTIONS");f.pack(fill="both",expand=True,pady=5)
        cols=("local","remote","status","pid");self.ctree=ttk.Treeview(f,columns=cols,show="headings")
        for c,w in zip(cols,[270,320,150,100]):self.ctree.heading(c,text=c.upper());self.ctree.column(c,width=w)
        self.ctree.pack(fill="both",expand=True,padx=8,pady=8)

    def refresh_connections(self):
        for i in self.ctree.get_children():self.ctree.delete(i)
        try:cs=psutil.net_connections("inet")
        except (psutil.AccessDenied,PermissionError):return
        for c in cs:self.ctree.insert("", "end",values=(self.addr(c.laddr),self.addr(c.raddr),c.status,c.pid or "-"))

    def addr(self,a):
        if not a:return "-"
        try:return f"{a.ip}:{a.port}"
        except:return str(a)

    def reports_ui(self):
        f=self.panel(self.rep,"REPORTS");f.pack(fill="both",expand=True,pady=5)
        tk.Button(f,text="EXPORT JSON",command=self.export_json,bg="#123047",fg=self.CYAN,relief="flat",padx=18,pady=9).pack(anchor="w",padx=14,pady=14)
        tk.Button(f,text="EXPORT CSV",command=self.export_csv,bg="#123047",fg=self.GREEN,relief="flat",padx=18,pady=9).pack(anchor="w",padx=14)

    def report(self):
        return {"created":datetime.now().isoformat(),"app":APP,"system":{"host":socket.gethostname(),"platform":platform.platform(),"python":platform.python_version(),"cpu":psutil.cpu_percent(),"ram":psutil.virtual_memory().percent},"wifi":self.wifi}

    def export_json(self):
        p=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
        if p:
            with open(p,"w",encoding="utf-8") as f:json.dump(self.report(),f,ensure_ascii=False,indent=2)
            messagebox.showinfo("Done","JSON report saved.")

    def export_csv(self):
        p=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if p:
            with open(p,"w",newline="",encoding="utf-8-sig") as f:
                w=csv.DictWriter(f,fieldnames=["ssid","signal","channel","security"]);w.writeheader();w.writerows(self.wifi)
            messagebox.showinfo("Done","CSV report saved.")

    def logs_ui(self):
        self.logbox=tk.Text(self.logs,bg="#050a10",fg=self.TEXT,relief="flat",font=("Consolas",10));self.logbox.pack(fill="both",expand=True,padx=8,pady=8)

    def log(self,s):
        line=f"[{datetime.now():%H:%M:%S}] {s}"
        try:LOG.open("a",encoding="utf-8").write(line+"\n")
        except:pass
        if hasattr(self,"logbox"):self.logbox.insert("end",line+"\n");self.logbox.see("end")

    def alert(self,sev,cat,msg):
        self.alerts+=1;self.log(f"[{sev}] {cat}: {msg}")

    def snapshot(self):
        return {n:sorted((str(a.address),str(a.netmask)) for a in ads if a.family in (socket.AF_INET,socket.AF_INET6)) for n,ads in psutil.net_if_addrs().items()}

    def refresh(self):
        try:
            cpu=psutil.cpu_percent();ram=psutil.virtual_memory().percent
            self.m["WIFI"].set("Connected" if self.wifi else "Ready")
            self.m["DEVICES"].set(str(len(getattr(self,"devices",[]))))
            self.m["CELL TOWERS"].set(str(len(getattr(self,"towers",[]))))
            visible=sum(1 for x in getattr(self,"satellites",[]) if x.get("el",-90)>0)
            self.m["SATELLITES"].set(str(visible))
            self.m["SECURITY"].set("Safe" if self.alerts==0 else f"{self.alerts} Alert")
            net=psutil.net_io_counters();now=time.time()
            if self.last:
                dt=max(now-self.last,0.001);rx=max(0,(net.bytes_recv-self.last_rx)/dt/1024);tx=max(0,(net.bytes_sent-self.last_tx)/dt/1024)
                self.rx.append(rx);self.tx.append(tx);self.rx=self.rx[-60:];self.tx=self.tx[-60:]
            self.last=now;self.last_rx=net.bytes_recv;self.last_tx=net.bytes_sent
            self.clock.set(datetime.now().strftime("%H:%M:%S"))
            if hasattr(self,"sys"):
                self.sys.delete("1.0","end")
                for name,addrs in list(psutil.net_if_addrs().items())[:8]:
                    ipv4=next((a.address for a in addrs if getattr(a,"family",None)==socket.AF_INET),"-")
                    state="UP" if any(getattr(x,"isup",False) for x in psutil.net_if_stats().values()) else "-"
                    self.sys.insert("end",f"{name:<14} {ipv4:<16} {state}\n")
            if hasattr(self,"security_overview"):
                self.security_overview.delete("1.0","end")
                self.security_overview.insert("end","✓  Firewall / local checks\n", "ok")
                self.security_overview.insert("end","✓  Network interfaces readable\n", "ok")
                self.security_overview.insert("end","✓  Monitoring service active\n", "ok")
                self.security_overview.insert("end",f"•  Active alerts: {self.alerts}\n")
            if hasattr(self,"space_summary"):
                self.space_summary.delete("1.0","end")
                visible=sum(1 for x in getattr(self,"satellites",[]) if x.get("el",-90)>0)
                self.space_summary.insert("end",f"Nearby telecom towers:  {len(getattr(self,"towers",[]))}\n\nVisible satellites:  {visible}\n\nOpen Cell / Satellite to view nearby tower and visible-satellite results.")
            self.draw_graph()
        except Exception as e:
            self.status.set("● MONITORING ERROR")
            self.log(f"Refresh error: {e}")

    def draw_graph(self):
        c=self.graph;c.delete("all");w=max(c.winfo_width(),500);h=max(c.winfo_height(),250)
        for i in range(1,6):c.create_line(30,h*i/6,w-15,h*i/6,fill="#102532")
        mx=max(self.rx+self.tx,default=10);mx=max(mx,10)
        def pts(a):
            return sum(([30+(w-45)*i/max(len(a)-1,1),h-25-(v/mx)*(h-55)] for i,v in enumerate(a)),[])
        a,b=pts(self.rx),pts(self.tx)
        if len(a)>3:c.create_line(*a,fill=self.CYAN,width=2,smooth=True)
        if len(b)>3:c.create_line(*b,fill=self.GREEN,width=2,smooth=True)

    def loop(self):
        if self.running:self.refresh();self.draw_radar();self.root.after(2000,self.loop)

    def close(self):
        self.running=False
        if hasattr(self,'audio_running'): self.audio_running=False
        self.log("Stopped.");self.root.destroy()

if __name__=="__main__":
    root=tk.Tk();App(root);root.mainloop()
