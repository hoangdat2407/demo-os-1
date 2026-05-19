"""
Demo Page Replacement Algorithms
--------------------------------
Giao dien Tkinter:
  - Nhap chuoi tham chieu trang + so frame
  - Chon thuat toan: FIFO / Optimal / LRU / MRU / LFU / MFU / Second Chance
  - Bang mo phong tung buoc (highlight Hit/Fault)
  - Bieu do duong: Page Faults theo so Frame -> rat tien show Belady cua FIFO

Chay:
    python app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)

import algorithms as algo


# Chuoi mau gay Belady cho FIFO khi tang frame tu 3 -> 4
BELADY_SAMPLE = "1 2 3 4 1 2 5 1 2 3 4 5"
# 1 2 3 4 1 2 5 1 2 3 4 5
"""
=== Cac chuoi co san ===
{
'1 2 3 4 1 2 5 1 2 3 4 5'
  faults theo frame 1..7 = [12, 12, 9, 10, 5, 5, 5]
  Belady: [(3, 4, 9, 10)]

'3 2 1 0 3 2 4 3 2 1 0 4'
  faults theo frame 1..7 = [12, 12, 9, 10, 5, 5, 5]
  Belady: [(3, 4, 9, 10)]

'4 3 2 1 4 3 5 4 3 2 1 5'
  faults theo frame 1..7 = [12, 12, 9, 10, 5, 5, 5]
  Belady: [(3, 4, 9, 10)]

'1 2 3 4 5 6 1 2 3 4 5 6'
  faults theo frame 1..7 = [12, 12, 12, 12, 12, 6, 6]
  Belady: []

'0 1 2 3 0 1 4 0 1 2 3 4'
  faults theo frame 1..7 = [12, 12, 9, 10, 5, 5, 5]
  Belady: [(3, 4, 9, 10)]

'5 4 3 2 1 5 4 6 5 4 3 2 1 6'
  faults theo frame 1..7 = [14, 14, 12, 11, 12, 6, 6]
  Belady: [(4, 5, 11, 12)]

'2 3 4 5 2 3 6 2 3 4 5 6'
  faults theo frame 1..7 = [12, 12, 9, 10, 5, 5, 5]
  Belady: [(3, 4, 9, 10)]

'1 2 3 4 1 2 5 1 2 3 4 5 6 1 2 3 4 5 6'
  faults theo frame 1..7 = [19, 19, 16, 17, 12, 6, 6]
  Belady: [(3, 4, 16, 17)]
}
"""


# ---------------------------------------------------------------------------
class PageReplacementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Demo - Các thuật toán thay thế trang")
        self.geometry("1180x780")
        self.minsize(1000, 700)

        self._build_top_panel()
        self._build_main_panel()
        self._build_status()

        # chay san mot lan voi du lieu mau
        # self.entry_pages.insert(0, BELADY_SAMPLE)
        # self.entry_capacity.insert(0, "3")
        # self.combo_algo.set("FIFO")
        self.run_simulation()

    # ----------------------------------------------------------- top panel
    def _build_top_panel(self):
        frm = ttk.LabelFrame(self, text="Tham số đầu vào", padding=10)
        frm.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(frm, text="Chuỗi tham chiếu:").grid(row=0, column=0, sticky="w")
        self.entry_pages = ttk.Entry(frm, width=70)
        self.entry_pages.grid(row=0, column=1, padx=5, sticky="we")

        ttk.Label(frm, text="Số frame:").grid(row=0, column=2, padx=(15, 0))
        self.entry_capacity = ttk.Entry(frm, width=6)
        self.entry_capacity.grid(row=0, column=3, padx=5)

        ttk.Label(frm, text="Thuật toán:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.combo_algo = ttk.Combobox(
            frm,
            values=list(algo.ALGORITHMS.keys()),
            state="readonly",
            width=20,
        )
        self.combo_algo.grid(row=1, column=1, sticky="w", pady=(8, 0))

        btns = ttk.Frame(frm)
        btns.grid(row=1, column=2, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(btns, text="Chạy mô phỏng", command=self.run_simulation).pack(
            side="left", padx=4
        )
        # ttk.Button(btns, text="Bieu do (Belady)", command=self.draw_chart).pack(
        #     side="left", padx=4
        # )
        # ttk.Button(btns, text="Vi du Belady", command=self.fill_belady).pack(
        #     side="left", padx=4
        # )

        frm.columnconfigure(1, weight=1)

    # ----------------------------------------------------------- main panel
    def _build_main_panel(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=5)

        # Tab 1: bang mo phong
        self.tab_table = ttk.Frame(nb)
        nb.add(self.tab_table, text="Mô phỏng từng bước")
        self._build_table_tab(self.tab_table)

        # Tab 2: bieu do
        self.tab_chart = ttk.Frame(nb)
        nb.add(self.tab_chart, text="Biểu đồ Page Fault / Frame")
        self._build_chart_tab(self.tab_chart)

    def _build_table_tab(self, parent):
        # khung tom tat
        self.lbl_summary = ttk.Label(
            parent,
            text="",
            font=("Segoe UI", 11, "bold"),
            foreground="#1a4f8a",
        )
        self.lbl_summary.pack(anchor="w", padx=10, pady=(8, 4))

        # Treeview - bang mo phong
        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(wrap, show="headings")
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # mau hang
        self.tree.tag_configure("fault", background="#ffe1e1")  # do nhat
        self.tree.tag_configure("_", background="#e1ffe6")    # xanh nhat

    def _build_chart_tab(self, parent):
        # tuy chon ve bieu do
        opt = ttk.Frame(parent)
        opt.pack(fill="x", padx=10, pady=8)

        ttk.Label(opt, text="Số frame: từ").pack(side="left")
        self.entry_fmin = ttk.Entry(opt, width=4)
        self.entry_fmin.insert(0, "1")
        self.entry_fmin.pack(side="left", padx=4)

        ttk.Label(opt, text="đến").pack(side="left")
        self.entry_fmax = ttk.Entry(opt, width=4)
        self.entry_fmax.insert(0, "7")
        self.entry_fmax.pack(side="left", padx=4)

        ttk.Label(opt, text="    Hiển thị:").pack(side="left", padx=(15, 4))
        self.algo_vars = {}
        for name in algo.ALGORITHMS.keys():
            v = tk.BooleanVar(value=(name in ("FIFO", "Optimal", "LRU")))
            cb = ttk.Checkbutton(opt, text=name, variable=v)
            cb.pack(side="left", padx=2)
            self.algo_vars[name] = v

        ttk.Button(opt, text="Vẽ biểu đồ", command=self.draw_chart).pack(
            side="left", padx=10
        )

        # khung chua matplotlib
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.fig = Figure(figsize=(8, 4.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Số Page Fault theo số Frame")
        self.ax.set_xlabel("Số frame")
        self.ax.set_ylabel("Số page fault")
        self.ax.grid(True, linestyle="--", alpha=0.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, chart_frame)
        toolbar.update()

    # ----------------------------------------------------------- status bar
    def _build_status(self):
        self.status = ttk.Label(
            self,
            text="Sẵn sàng.",
            anchor="w",
            relief="sunken",
            padding=(8, 3),
        )
        self.status.pack(fill="x", side="bottom")

    # ----------------------------------------------------------- helpers
    def _parse_pages(self):
        text = self.entry_pages.get().strip()
        if not text:
            raise ValueError("Vui lòng nhập chuỗi tham chiếu.")
        # cho phep dau cach hoac dau phay
        raw = text.replace(",", " ").split()
        try:
            pages = [int(x) for x in raw]
        except ValueError:
            raise ValueError("Chuỗi tham chiếu phải gồm các số nguyên.")
        if not pages:
            raise ValueError("Chuoi tham chiếu rỗng.")
        return pages

    def _parse_capacity(self):
        try:
            cap = int(self.entry_capacity.get())
        except ValueError:
            raise ValueError("Số frame phải là số nguyên.")
        if cap <= 0:
            raise ValueError("Số frame phải > 0.")
        return cap

    # def fill_belady(self):
    #     self.entry_pages.delete(0, tk.END)
    #     self.entry_pages.insert(0, BELADY_SAMPLE)
    #     self.entry_capacity.delete(0, tk.END)
    #     self.entry_capacity.insert(0, "3")
    #     self.combo_algo.set("FIFO")
    #     self.status.configure(
    #         text="Da nap vi du Belady. Bam 'Bieu do (Belady)' de thay nghich ly."
    #     )

    # ----------------------------------------------------------- run sim
    def run_simulation(self):
        try:
            pages = self._parse_pages()
            capacity = self._parse_capacity()
        except ValueError as e:
            messagebox.showerror("Lỗi nhập", str(e))
            return

        name = self.combo_algo.get() or "FIFO"
        result = algo.run(name, pages, capacity)

        # cau hinh cot
        cols = ["step", "page"] + ["F{}".format(i + 1) for i in range(capacity)]
        cols += ["status", "victim", "note"]

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = cols

        widths = {
            "step": 50, "page": 60, "status": 80, "victim": 70, "note": 380,
        }
        headings = {
            "step": "Bước", "page": "Trang", "status": "Trạng thái",
            "victim": "Bị thay", "note": "Ghi chú",
        }
        for c in cols:
            if c.startswith("F"):
                self.tree.heading(c, text=c)
                self.tree.column(c, width=60, anchor="center")
            else:
                self.tree.heading(c, text=headings[c])
                self.tree.column(c, width=widths[c], anchor="center")

        # do du lieu
        for i, st in enumerate(result["steps"], start=1):
            row = [i, st["page"]]
            for f in st["frames"]:
                row.append("-" if f is None else f)
            row.append("FAULT" if st["fault"] else "_")
            row.append(st["victim"] if st["victim"] is not None else "-")
            row.append(st["note"])
            tag = "fault" if st["fault"] else "_"
            self.tree.insert("", "end", values=row, tags=(tag,))

        total = result["faults"] + result["hits"]
        rate = (result["faults"] / total * 100) if total else 0
        self.lbl_summary.configure(
            text="Thuật toán: {}   |   Số frame: {}   |   "
                 "Page Fault: {}   |   Tỉ lệ fault: {:.1f}%".format(
                name, capacity, result["faults"], result["hits"], rate
            )
        )
        self.status.configure(
            text="Đã chạy {} với {} bướcc.".format(name, len(result["steps"]))
        )

    # ----------------------------------------------------------- chart
    def draw_chart(self):
        try:
            pages = self._parse_pages()
            fmin = int(self.entry_fmin.get())
            fmax = int(self.entry_fmax.get())
        except ValueError as e:
            messagebox.showerror("Lỗi nhập", "Tham số biểu đồ không hợp lệ.\n" + str(e))
            return
        if fmin < 1 or fmax < fmin:
            messagebox.showerror("Lỗi nhập", "Khoảng frame không hợp lệ.")
            return

        selected = [n for n, v in self.algo_vars.items() if v.get()]
        if not selected:
            messagebox.showinfo("Biểu đồ", "Hãy chọn ít nhất 1 thuật toán.")
            return

        xs = list(range(fmin, fmax + 1))

        self.ax.clear()
        self.ax.set_title("Số Page Fault theo số Frame")
        self.ax.set_xlabel("Số frame")
        self.ax.set_ylabel("Số page fault")
        self.ax.grid(True, linestyle="--", alpha=0.5)

        markers = ["o", "s", "^", "D", "v", "P", "X"]
        for i, name in enumerate(selected):
            ys = [algo.run(name, pages, c)["faults"] for c in xs]
            line, = self.ax.plot(
                xs, ys,
                marker=markers[i % len(markers)],
                linewidth=2,
                label=name,
            )
            # them nhan so cho moi diem
            for x, y in zip(xs, ys):
                self.ax.annotate(
                    str(y),
                    xy=(x, y),
                    xytext=(0, 6),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                    color=line.get_color(),
                )

            # phat hien Belady: f -> f+1 ma faults TANG
            for j in range(len(xs) - 1):
                if ys[j + 1] > ys[j]:
                    self.ax.annotate(
                        "Belady!",
                        xy=(xs[j + 1], ys[j + 1]),
                        xytext=(10, 14),
                        textcoords="offset points",
                        fontsize=9,
                        color="red",
                        fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color="red"),
                    )

        self.ax.set_xticks(xs)
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()
        self.status.configure(
            text="Đã vẽ biểu đồ cho: " + ", ".join(selected)
        )


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = PageReplacementApp()
    app.mainloop()
