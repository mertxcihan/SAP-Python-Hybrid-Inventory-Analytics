import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


class SAPStokAnalizSistemi:
    def __init__(self, root):
        self.root = root
        self.root.title("SAP ERP - Stok Takip ve Analiz Dashboard")
        self.root.geometry("1200x800")
        self.df = None

        self.bg_color = "#f0f2f5"
        self.sidebar_color = "#2c3e50"
        self.root.configure(bg=self.bg_color)

        self.arayuz_olustur()

    def arayuz_olustur(self):

        self.sidebar = tk.Frame(self.root, bg=self.sidebar_color, width=300)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="KONTROL PANELİ", bg=self.sidebar_color, fg="white",
                 font=("Arial", 12, "bold")).pack(pady=20)

        tk.Button(self.sidebar, text="🔌 SAP VERİLERİNİ AKTAR", command=self.sap_verisi_al,
                  bg="#c0392b", fg="white", font=("Arial", 10, "bold"), height=2).pack(fill="x", padx=15, pady=10)

        f_sorgu = tk.LabelFrame(self.sidebar, text=" Sorgulama ", bg=self.sidebar_color, fg="white", padx=10, pady=10)
        f_sorgu.pack(fill="x", padx=15, pady=10)

        tk.Label(f_sorgu, text="Ürün Kodu:", bg=self.sidebar_color, fg="white").pack(anchor="w")
        self.ent_kod = tk.Entry(f_sorgu, font=("Arial", 11))
        self.ent_kod.pack(fill="x", pady=5)
        tk.Button(f_sorgu, text="BİLGİ GETİR", command=self.kod_sorgula, bg="#3498db", fg="white").pack(fill="x",
                                                                                                        pady=5)

        tk.Label(f_sorgu, text="Kategori Adı:", bg=self.sidebar_color, fg="white").pack(anchor="w", pady=(10, 0))
        self.ent_kat = tk.Entry(f_sorgu, font=("Arial", 11))
        self.ent_kat.pack(fill="x", pady=5)
        tk.Button(f_sorgu, text="ANALİZ ET (PASTA)", command=self.kat_sorgula, bg="#9b59b6", fg="white").pack(fill="x",
                                                                                                              pady=5)

        f_analiz = tk.LabelFrame(self.sidebar, text=" Hızlı Analizler ", bg=self.sidebar_color, fg="white", padx=10,
                                 pady=10)
        f_analiz.pack(fill="x", padx=15, pady=10)

        analizler = [("En Yüksek 10 Ürün", "top10", "#27ae60"), ("Kritik 10 Ürün", "bot10", "#e67e22"),
                     ("En Yüksek 3 Kategori", "top3", "#2980b9"), ("Genel Analiz", "genel", "#7f8c8d")]

        for metin, mod, renk in analizler:
            tk.Button(f_analiz, text=metin, command=lambda m=mod: self.analiz_yap(m),
                      bg=renk, fg="white", font=("Arial", 9)).pack(fill="x", pady=3)

        self.main_content = tk.Frame(self.root, bg=self.bg_color)
        self.main_content.pack(side="right", fill="both", expand=True)

        self.info_frame = tk.Frame(self.main_content, bg="white", height=150, relief="flat")
        self.info_frame.pack(fill="x", padx=20, pady=20)
        self.info_frame.pack_propagate(False)

        self.lbl_detay = tk.Label(self.info_frame, text="Sistem Hazır. Lütfen SAP Bağlantısını Başlatın...",
                                  font=("Segoe UI", 12, "bold"), fg="#34495e", bg="white", justify="left")
        self.lbl_detay.pack(expand=True)

        self.graph_frame = tk.Frame(self.main_content, bg="white", bd=1, relief="solid")
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def sap_verisi_al(self):

        dizin = os.path.dirname(os.path.abspath(__file__))
        dosya_yolu = os.path.join(dizin, 'stok_veri.csv')
        try:
            self.df = pd.read_csv(dosya_yolu, sep=';')
            messagebox.showinfo("Başarılı", "SAP Verileri Aktarıldı.")
            self.lbl_detay.config(text=f"✅ SAP SİSTEMİNE BAĞLANILDI\n{len(self.df)} Kalem Ürün Analize Hazır.",
                                  fg="#27ae60")
        except Exception as e:
            messagebox.showerror("Hata", f"stok_veri.csv bulunamadı!\nAranan Yol: {dosya_yolu}")

    def kod_sorgula(self):
        if self.df is None: return
        kod = self.ent_kod.get().strip().upper()
        res = self.df[self.df['URUN_KODU'].astype(str).str.upper() == kod]
        if not res.empty:
            item = res.iloc[0]
            self.lbl_detay.config(
                text=f"📦 {item['URUN_ADI']} | 🔢 Stok: {item['STOK']} | 📂 {item['KATEGORI']} | 🏠 {item['DEPO']}",
                fg="#2980b9")
        else:
            self.lbl_detay.config(text=f"❌ '{kod}' kodlu ürün bulunamadı!", fg="#c0392b")

    def grafik_bas(self, fig):
        for w in self.graph_frame.winfo_children(): w.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def kat_sorgula(self):
        if self.df is None: return
        kat = self.ent_kat.get().strip().upper()

        res = self.df[self.df['KATEGORI'].str.upper() == kat].copy()

        if not res.empty:

            res_grouped = res.groupby('URUN_ADI')['STOK'].sum().reset_index()

            res_grouped = res_grouped.sort_values('STOK')

            boyut = max(5, len(res_grouped) * 0.5)
            fig, ax = plt.subplots(figsize=(8, boyut))

            y_pos = range(len(res_grouped))
            bars = ax.barh(y_pos, res_grouped['STOK'], color='#3498db', height=0.6)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(res_grouped['URUN_ADI'], fontsize=9)

            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + (res_grouped['STOK'].max() * 0.02), i,
                        f'{int(width)}',
                        va='center', fontsize=9, fontweight='bold')

            ax.set_title(f"{kat} Kategorisi - Gruplandırılmış Stok Analizi", pad=20, fontweight='bold')
            ax.set_xlabel("Toplam Stok Adedi")
            ax.set_xlim(0, res_grouped['STOK'].max() * 1.2)

            plt.tight_layout()
            self.grafik_bas(fig)
            self.lbl_detay.config(text=f"✅ {kat} kategorisinde benzer ürünler birleştirildi ({len(res_grouped)} grup).",
                                  fg="#2980b9")
        else:
            messagebox.showwarning("Uyarı", f"'{kat}' kategorisi bulunamadı!")

    def analiz_yap(self, mod):
        if self.df is None: return
        fig, ax = plt.subplots(figsize=(6, 4))
        if mod == "top10":
            data = self.df.nlargest(10, 'STOK')
            ax.bar(data['URUN_ADI'], data['STOK'], color='#2ecc71')
            ax.set_title("En Yüksek Stoklu 10 Ürün")
        elif mod == "bot10":
            data = self.df.nsmallest(10, 'STOK')
            ax.bar(data['URUN_ADI'], data['STOK'], color='#e74c3c')
            ax.set_title("Kritik Stoklu 10 Ürün")
        elif mod == "top3":
            data = self.df.groupby('KATEGORI')['STOK'].sum().nlargest(3)
            ax.bar(data.index, data.values, color='#3498db')
            ax.set_title("En Yüksek 3 Kategori")
        elif mod == "genel":
            data = self.df.groupby('KATEGORI')['STOK'].sum()
            ax.bar(data.index, data.values, color='#95a5a6')
            ax.set_title("Genel Stok Dağılımı")

        plt.xticks(rotation=30, ha='right', fontsize=8)
        plt.tight_layout()
        self.grafik_bas(fig)


if __name__ == "__main__":
    root = tk.Tk()
    app = SAPStokAnalizSistemi(root)
    root.mainloop()
