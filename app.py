import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading, queue, json, shutil, webbrowser
from pathlib import Path
from viralclips.pipeline import process
from viralclips.config import OUTPUT, ROOT

BG="#10131b"; PANEL="#191f2b"; PANEL2="#222b3a"; TEXT="#f4f6fb"; MUTED="#aab4c5"; ACCENT="#7c5cff"; GREEN="#35d39a"
class App:
    def __init__(self, root):
        self.root=root; self.root.title("ViralClipsAI 1.0"); self.root.geometry("1120x760"); self.root.minsize(900,650); self.root.configure(bg=BG)
        self.q=queue.Queue(); self.project=None
        self.style=ttk.Style(); self.style.theme_use("clam")
        self.style.configure("TProgressbar", troughcolor=PANEL2, background=ACCENT, bordercolor=PANEL2, lightcolor=ACCENT, darkcolor=ACCENT)
        self.build(); self.poll()
    def label(self,parent,text,size=11,color=TEXT,bold=False):
        return tk.Label(parent,text=text,bg=parent.cget("bg"),fg=color,font=("Segoe UI",size,"bold" if bold else "normal"))
    def build(self):
        top=tk.Frame(self.root,bg=BG); top.pack(fill="x",padx=28,pady=(22,12))
        self.label(top,"ViralClipsAI",25,TEXT,True).pack(side="left")
        self.label(top,"CREADOR AUTOMÁTICO DE CLIPS",9,MUTED,True).pack(side="left",padx=18,pady=(10,0))
        self.label(top,"v1.0  •  Windows 64-bit",9,MUTED).pack(side="right",pady=12)
        body=tk.Frame(self.root,bg=BG); body.pack(fill="both",expand=True,padx=28,pady=10)
        left=tk.Frame(body,bg=PANEL,width=330); left.pack(side="left",fill="y",padx=(0,16)); left.pack_propagate(False)
        self.label(left,"Nuevo proyecto",16,TEXT,True).pack(anchor="w",padx=20,pady=(22,16))
        self.label(left,"ENLACE DEL VIDEO",9,MUTED,True).pack(anchor="w",padx=20)
        self.url=tk.Text(left,height=4,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",wrap="word",font=("Segoe UI",10)); self.url.pack(fill="x",padx=20,pady=(8,14))
        self.label(left,"NOMBRE DEL PROYECTO",9,MUTED,True).pack(anchor="w",padx=20)
        self.name=tk.Entry(left,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",font=("Segoe UI",11)); self.name.insert(0,"Mi proyecto"); self.name.pack(fill="x",padx=20,pady=(8,18),ipady=9)
        self.btn(left,"ANALIZAR Y CREAR 10 CLIPS",self.start,ACCENT).pack(fill="x",padx=20,pady=4)
        self.progress=ttk.Progressbar(left,maximum=100); self.progress.pack(fill="x",padx=20,pady=(22,8))
        self.status=self.label(left,"Listo para comenzar",9,MUTED); self.status.pack(anchor="w",padx=20)
        self.label(left,"FORMATOS",9,MUTED,True).pack(anchor="w",padx=20,pady=(30,8))
        self.label(left,"MP4  •  1080 × 1920  •  9:16\nSubtítulos en español\nCaption y hashtags por clip",10,TEXT).pack(anchor="w",padx=20)
        self.btn(left,"ABRIR CARPETA DE CLIPS",self.open_output,PANEL2).pack(fill="x",padx=20,pady=(30,8))
        right=tk.Frame(body,bg=PANEL); right.pack(side="left",fill="both",expand=True)
        head=tk.Frame(right,bg=PANEL); head.pack(fill="x",padx=22,pady=20)
        self.label(head,"Tus clips",18,TEXT,True).pack(side="left")
        self.label(head,"Los resultados aparecerán aquí",9,MUTED).pack(side="right",pady=8)
        self.list=tk.Listbox(right,bg=PANEL2,fg=TEXT,selectbackground=ACCENT,relief="flat",font=("Segoe UI",11),activestyle="none")
        self.list.pack(fill="both",expand=True,padx=22,pady=(0,10)); self.list.bind("<<ListboxSelect>>",self.show_clip)
        self.preview=tk.Text(right,height=7,bg="#131925",fg=TEXT,relief="flat",wrap="word",font=("Segoe UI",10)); self.preview.pack(fill="x",padx=22,pady=(0,10))
        actions=tk.Frame(right,bg=PANEL); actions.pack(fill="x",padx=22,pady=(0,20))
        self.btn(actions,"ABRIR VIDEO",self.open_clip,PANEL2).pack(side="left")
        self.btn(actions,"COPIAR CAPTION",self.copy_caption,PANEL2).pack(side="left",padx=8)
        self.btn(actions,"DESCARGAR TODOS",self.download_all,GREEN,fg="#07140f").pack(side="right")
        foot=tk.Frame(self.root,bg=BG); foot.pack(fill="x",padx=28,pady=(0,14))
        self.label(foot,"Procesa únicamente contenido público o que tengas autorización para utilizar.",9,MUTED).pack(side="left")
    def btn(self,parent,text,command,color,fg="white"):
        return tk.Button(parent,text=text,command=command,bg=color,fg=fg,activebackground=color,activeforeground=fg,relief="flat",bd=0,cursor="hand2",font=("Segoe UI",9,"bold"),padx=14,pady=12)
    def start(self):
        url=self.url.get("1.0","end").strip(); name=self.name.get().strip() or "Proyecto"
        if not url.startswith(("http://","https://")):
            messagebox.showwarning("Falta el enlace","Pega un enlace público de YouTube, Twitch o Kick."); return
        self.btn_state="busy"; self.progress["value"]=0; self.status.config(text="Iniciando...")
        self.list.delete(0,"end"); self.preview.delete("1.0","end"); self.project=None
        threading.Thread(target=self.worker,args=(url,name),daemon=True).start()
    def worker(self,url,name):
        try:
            data=process(url,name,lambda pct,msg:self.q.put(("progress",pct,msg)))
            self.q.put(("done",data))
        except Exception as e: self.q.put(("error",str(e)))
    def poll(self):
        try:
            while True:
                item=self.q.get_nowait()
                if item[0]=="progress":
                    self.progress["value"]=item[1]; self.status.config(text=item[2])
                elif item[0]=="done":
                    self.project=item[1]
                    for i,c in enumerate(self.project["clips"],1): self.list.insert("end",f"CLIP {i:02d}   •   {int(c['end']-c['start'])} segundos")
                    self.status.config(text=f"{len(self.project['clips'])} clips listos"); messagebox.showinfo("Finalizado","Tus clips se han creado correctamente.")
                elif item[0]=="error":
                    self.status.config(text="El proceso encontró un error"); messagebox.showerror("No se pudo completar",item[1])
        except queue.Empty: pass
        self.root.after(250,self.poll)
    def selected(self):
        if not self.project or not self.list.curselection(): return None
        return self.project["clips"][self.list.curselection()[0]]
    def show_clip(self,event=None):
        c=self.selected()
        if c:
            self.preview.delete("1.0","end"); self.preview.insert("end",c["caption"])
    def open_clip(self):
        c=self.selected()
        if c and Path(c["file"]).exists(): webbrowser.open(Path(c["file"]).as_uri())
        elif c: messagebox.showerror("Archivo no encontrado","No se encontró el MP4.")
    def copy_caption(self):
        c=self.selected()
        if c:
            self.root.clipboard_clear(); self.root.clipboard_append(c["caption"]); self.status.config(text="Caption copiado")
    def download_all(self):
        if not self.project: return
        dest=filedialog.askdirectory(title="Selecciona dónde guardar tus 10 clips")
        if not dest: return
        for c in self.project["clips"]:
            shutil.copy2(c["file"],dest); shutil.copy2(str(Path(c["file"]).with_name(Path(c["file"]).stem+"_caption.txt")),dest)
        messagebox.showinfo("Descarga completada",f"Clips y captions copiados a:\n{dest}")
    def open_output(self):
        OUTPUT.mkdir(parents=True,exist_ok=True); webbrowser.open(OUTPUT.as_uri())
if __name__=="__main__":
    root=tk.Tk(); App(root); root.mainloop()
