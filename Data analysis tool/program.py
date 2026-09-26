import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import plot_tree
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing  import PolynomialFeatures
from matplotlib import colors as mcolors
import seaborn
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
class GraphObject(tk.Frame):
    PAGE_SIZE = 100

    def __init__(self, data: pd.DataFrame, root: tk.Widget):
        super().__init__(root, bg="#00477D")
        self.data = data
        self.rendered_rows = 0
        columns = list(data.columns)

        self.x_scroll = ttk.Scrollbar(self, orient="horizontal")
        self.table = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            xscrollcommand=self.x_scroll.set,
            height=20
        )
        self.x_scroll.configure(command=self.table.xview)

        self.table.pack(side="top", fill="both", expand=True)
        self.x_scroll.pack(side="top", fill="x")

        self.pagination = tk.Frame(self, bg="#00477D")
        self.row_status = tk.Label(self.pagination, bg="#00477D", fg="white")
        self.row_status.pack(side="left", padx=8, pady=4)
        self.more_rows_button = tk.Button(
            self.pagination,
            text=f"Render {self.PAGE_SIZE} more",
            command=self.render_next_page,
        )
        self.more_rows_button.pack(side="right", padx=8, pady=4)
        self.pagination.pack(side="bottom", fill="x")

        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=150, minwidth=100, anchor="center", stretch=False)

        self.render_next_page()

    def render_next_page(self):
        end_row = min(self.rendered_rows + self.PAGE_SIZE, len(self.data))
        rows = self.data.iloc[self.rendered_rows:end_row].itertuples(
            index=False, name=None
        )
        for row in rows:
            self.table.insert("", "end", values=row)
        self.rendered_rows = end_row
        self.row_status.configure(
            text=f"Showing {self.rendered_rows:,} of {len(self.data):,} rows"
        )
        self.more_rows_button.configure(
            state="normal" if self.rendered_rows < len(self.data) else "disabled"
        )


class FileDropFrame(tk.Frame):
    def __init__(self, parent, on_file_selected):
        super().__init__(parent, bg="#00477D", highlightthickness=2,
                         highlightbackground="#001881")
        self.on_file_selected = on_file_selected

        label = tk.Label(
            self,
            text="Drop a CSV file here or choose one",
            bg="#00477D",
            fg="white",
            pady=12,
        )
        label.pack(fill="x")
        button = tk.Button(
            self,
            text="Choose CSV",
            command=self.choose_file,
        )
        button.pack(pady=(0, 12))

        for widget in (self, label, button):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self.handle_drop)

    def choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if file_path:
            self.on_file_selected(file_path)

    def handle_drop(self, event):
        file_paths = self.tk.splitlist(event.data)
        if file_paths:
            self.on_file_selected(file_paths[0])

class GraphParent(tk.Frame):
    def __init__(self, parent: tk.Widget, graphtypes: list, on_graph_selected):
        super().__init__(parent, bg="#14532d", highlightthickness=2,
                         highlightbackground="#0b2e1a")
        self.on_graph_selected = on_graph_selected
        self.graph_value = tk.StringVar(value=graphtypes[0])
        self.dropdown = tk.OptionMenu(self, self.graph_value, *graphtypes,
                                      command=self.onselected)
        self.dropdown.configure(
            bg="#14532d",
            fg="white",
            activebackground="#1f7a46",
            activeforeground="white",
            highlightthickness=0,
            relief="flat",
        )
        self.dropdown["menu"].configure(
            bg="#14532d",
            fg="white",
            activebackground="#1f7a46",
            activeforeground="white",
        )
        self.dropdown.pack(fill="x", padx=8, pady=8)

    def onselected(self, graph_name):
        self.on_graph_selected(graph_name)

    def set_graph(self, graph_name):
        self.graph_value.set(graph_name)

class Config(tk.Frame):
    def __init__(self, parent, on_selected_x, on_selected_y,
                 on_count_limit_changed=None):
        super().__init__(parent, bg="#1a1a1a", highlightthickness=0, bd=0)
        self.on_selected_x = on_selected_x
        self.on_selected_y = on_selected_y
        self.on_count_limit_changed = on_count_limit_changed or (lambda: None)
        self.count_limit = 10
        self.x_f = tk.Frame(self, bg="#1a1a1a", highlightthickness=0, bd=0)
        self.y_f = tk.Frame(self, bg="#1a1a1a", highlightthickness=0, bd=0)
        self.count_f = tk.Frame(self, bg="#1a1a1a", highlightthickness=0, bd=0)
        self.x_value = tk.StringVar(self)
        self.y_value = tk.StringVar(self)
        self.count_value = tk.StringVar(self, value=str(self.count_limit))

        self.x_label = tk.Label(
            self.x_f, text="X axis", bg="#1a1a1a", fg="white", width=7, anchor="w"
        )
        self.y_label = tk.Label(
            self.y_f, text="Y axis", bg="#1a1a1a", fg="white", width=7, anchor="w"
        )
        self.dropdown_x = tk.OptionMenu(self.x_f, self.x_value, "")
        self.dropdown_y = tk.OptionMenu(self.y_f, self.y_value, "")
        self.dropdown_x.configure(
            bg="#14532d",
            fg="white",
            activebackground="#1f7a46",
            activeforeground="white",
            highlightthickness=0,
            relief="flat",
        )
        self.dropdown_x["menu"].configure(
            bg="#14532d",
            fg="white",
            activebackground="#1f7a46",
            activeforeground="white",
        )
        self.dropdown_y.configure(
            bg="#14532d",
            fg="white",
            activebackground="#1f7a46",
            activeforeground="white",
            highlightthickness=0,
            relief="flat",
        )
        self.dropdown_y["menu"].configure(
            bg="#14532d",
            fg="white",
            activebackground="#1f7a46",
            activeforeground="white",
        )
        self.swap_button = tk.Button(
            self.y_f,
            text="Swap X/Y",
            command=self.swap_axes,
            bg="#14532d",
            fg="white",
            activebackground="#1f7a46",
            activeforeground="white",
            relief="flat",
            highlightthickness=0,
        )
        tk.Label(
            self.count_f, text="Categories", bg="#1a1a1a", fg="white"
        ).pack(side="left", padx=(4, 6))
        tk.Button(
            self.count_f,
            text="-",
            width=2,
            command=lambda: self.adjust_count_limit(-1),
        ).pack(side="left")
        self.count_entry = tk.Entry(
            self.count_f, textvariable=self.count_value, width=5, justify="center"
        )
        self.count_entry.pack(side="left", padx=4)
        self.count_entry.bind("<Return>", self.commit_count_limit)
        self.count_entry.bind("<FocusOut>", self.commit_count_limit)
        tk.Button(
            self.count_f,
            text="+",
            width=2,
            command=lambda: self.adjust_count_limit(1),
        ).pack(side="left")
        self.x_label.pack(side="left", padx=(4, 6))
        self.dropdown_x.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.y_label.pack(side="left", padx=(4, 6))
        self.dropdown_y.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.swap_button.pack(side="right", padx=(4, 4))
        self.x_f.pack(fill="x", expand=True, pady=(2, 1))
        self.y_f.pack(fill="x", expand=True, pady=(1, 2))

    def set_columns(self, x_columns, y_columns=(), show_y=True,
                    show_count_limit=False):
        self._set_menu(self.dropdown_x, self.x_value, x_columns, self.on_selected_x)
        self._set_menu(self.dropdown_y, self.y_value, y_columns, self.on_selected_y)
        if show_y:
            self.y_f.pack(fill="x", expand=True, pady=(1, 2))
        else:
            self.y_f.pack_forget()
        if show_count_limit:
            self.count_f.pack(fill="x", expand=True, pady=(1, 2))
        else:
            self.count_f.pack_forget()

    def adjust_count_limit(self, change):
        self.count_limit = max(1, self.count_limit + change)
        self.count_value.set(str(self.count_limit))
        self.on_count_limit_changed()

    def commit_count_limit(self, _event=None):
        try:
            new_limit = max(1, int(self.count_value.get()))
        except ValueError:
            new_limit = self.count_limit
        changed = new_limit != self.count_limit
        self.count_limit = new_limit
        self.count_value.set(str(self.count_limit))
        if changed:
            self.on_count_limit_changed()

    def get_count_limit(self):
        return self.count_limit

    def swap_axes(self):
        x_column = self.x_value.get()
        y_column = self.y_value.get()
        if not x_column or not y_column:
            return
        self.x_value.set(y_column)
        self.y_value.set(x_column)
        self.on_selected_x(y_column)

    @staticmethod
    def _set_menu(dropdown, variable, columns, callback):
        columns = list(columns)
        menu = dropdown["menu"]
        menu.delete(0, "end")
        if not columns:
            variable.set("")
            return

        if variable.get() not in columns:
            variable.set(columns[0])
        for column in columns:
            def select(value=column):
                variable.set(value)
                callback(value)

            menu.add_command(label=column, command=select)


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class Graph(tk.Frame):

    def __init__(self, name, parent):
        super().__init__(parent, bg="#2b2b2b")
        self.title_label = tk.Label(self, text=name)
        self.title_label.pack(fill="x")

    def add_mpl_figure(self, fig):
        graph_view = tk.Frame(self, bg="#2b2b2b")
        graph_view.pack(fill="both", expand=True)

        view_canvas = tk.Canvas(graph_view, bg="#2b2b2b", highlightthickness=0)
        vertical_scrollbar = ttk.Scrollbar(
            graph_view, orient="vertical", command=view_canvas.yview
        )
        horizontal_scrollbar = ttk.Scrollbar(
            graph_view, orient="horizontal", command=view_canvas.xview
        )
        view_canvas.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        graph_area = tk.Frame(view_canvas, bg="#2b2b2b")
        view_canvas.create_window((0, 0), window=graph_area, anchor="nw")
        graph_area.bind(
            "<Configure>",
            lambda event: view_canvas.configure(scrollregion=view_canvas.bbox("all")),
        )

        view_canvas.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        graph_view.rowconfigure(0, weight=1)
        graph_view.columnconfigure(0, weight=1)

        self.mpl_canvas = FigureCanvasTkAgg(fig, graph_area)
        self.mpl_canvas.draw()
        figure_widget = self.mpl_canvas.get_tk_widget()
        figure_widget.configure(
            width=max(1, round(fig.get_figwidth() * fig.dpi)),
            height=max(1, round(fig.get_figheight() * fig.dpi)),
        )
        figure_widget.pack()

        def scroll_graph(event):
            view_canvas.yview_scroll(-int(event.delta / 120), "units")

        for widget in (view_canvas, graph_area, figure_widget):
            widget.bind("<MouseWheel>", scroll_graph)

        self.toolbar = NavigationToolbar2Tk(self.mpl_canvas, self)
        self.toolbar.update()

class ScatterRegressionPlot(Figure):

    def __init__(self, x, y):
        super().__init__(figsize=(5, 5), dpi=100)
        axis = self.add_subplot(111)
        points = pd.DataFrame({"x": x, "y": y}).dropna()
        axis.scatter(points["x"], points["y"], alpha=0.65, label="Data")

        if len(points) >= 2 and points["x"].nunique() > 1:
            slope, intercept = np.polyfit(points["x"], points["y"], 1)
            regression_x = np.linspace(points["x"].min(), points["x"].max(), 100)
            regression_y = slope * regression_x + intercept
            axis.plot(
                regression_x,
                regression_y,
                color="crimson",
                linewidth=2,
                label="Regression",
            )

        axis.set_xlabel(x.name)
        axis.set_ylabel(y.name)
        axis.legend()
        axis.grid(alpha=0.25)


class CountPlot(Figure):

    def __init__(self, x, limit=10):
        super().__init__(figsize=(5, 5), dpi=100)
        axis = self.add_subplot(111)
        counts = x.value_counts().head(max(1, int(limit)))
        axis.bar([str(value) for value in counts.index], counts.values)

        axis.set_xlabel(x.name)
        axis.set_ylabel("count")
        axis.set_title(f"Counts of {x.name}")
        axis.tick_params(axis="x", rotation=35)
        axis.grid(alpha=0.25)
        self.tight_layout()



class Correlations(Figure):

    def __init__(self, data : pd.DataFrame, n=7, plot=True, save_path=None):
        super().__init__(figsize=(7, 5.6), dpi=100)
        numeric_data = data.select_dtypes(include="number").dropna(axis=1, how="all")
        if numeric_data.shape[1] < 2:
            return

        correlations = numeric_data.corr()
        if correlations.shape[0] <= 50:
            ret = correlations.where(
                ~np.eye(correlations.shape[0], dtype=bool)
            ).stack().dropna()
            ret = ret.sort_values(ascending=False).drop_duplicates()
            if len(ret) != 0:
                print("Top " + str(min(n, len(ret))) + " Correlations")
                print("-----")
                print(ret.head(n))
                print()

        if not plot:
            return

        figure_size = max(7, min(16, 1.1 * len(correlations.columns)))
        self.set_size_inches(figure_size, figure_size * 0.8)
        axis = self.add_subplot(111)
        image = axis.imshow(correlations, cmap="coolwarm", vmin=-1, vmax=1)
        axis.set_xticks(range(len(correlations.columns)))
        axis.set_yticks(range(len(correlations.index)))
        axis.set_xticklabels(correlations.columns, rotation=45, ha="right")
        axis.set_yticklabels(correlations.index)
        axis.set_title("Correlation Heatmap")

        if len(correlations.columns) <= 20:
            for row in range(len(correlations.index)):
                for column in range(len(correlations.columns)):
                    axis.text(column, row, f"{correlations.iloc[row, column]:.2f}",
                            ha="center", va="center", fontsize=8)

        self.colorbar(image, ax=axis, label="Correlation")
        self.tight_layout()
        if save_path:
            self.savefig(save_path, dpi=150, bbox_inches="tight")


def __main__():
    root = TkinterDnD.Tk()
    root.geometry("1000x750")
    root.configure(bg='#1a1a1a')

    table = None
    graph_page = None
    current_data = None
    load_generation = 0
    load_status = tk.StringVar(root, value="Ready")
    tk.Label(
        root, textvariable=load_status, bg="#1a1a1a", fg="white", anchor="w"
    ).place(relx=0.82, rely=0.02, relwidth=0.17, relheight=0.12)

    graph_names = ["Heatmap", "Countplot", "Scatter regression"]
    active_graph_name = "Heatmap"

    def render_graph(graph_name):
        nonlocal graph_page, active_graph_name
        active_graph_name = graph_name
        if current_data is None:
            return

        try:
            if graph_name == "Heatmap":
                config_frame.place_forget()
                title = "Correlation Heatmap"
                figure = Correlations(current_data)
            elif graph_name == "Countplot":
                category_columns = current_data.select_dtypes(
                    include=["object", "string", "category"]
                ).columns.tolist()
                x_columns = category_columns or current_data.columns.tolist()
                if not x_columns:
                    raise ValueError("This file does not contain any columns to count.")
                config_frame.set_columns(
                    x_columns, show_y=False, show_count_limit=True
                )
                config_frame.place(
                    relx=0.56, rely=0.02, relwidth=0.25, relheight=0.12
                )
                x_column = config_frame.x_value.get()
                title = f"Countplot: {x_column}"
                figure = CountPlot(
                    current_data[x_column], config_frame.get_count_limit()
                )
            elif graph_name == "Scatter regression":
                numeric_columns = current_data.select_dtypes(
                    include="number"
                ).columns.tolist()
                if len(numeric_columns) < 2:
                    raise ValueError(
                        "Scatter regression requires at least two numeric columns."
                    )
                config_frame.set_columns(
                    numeric_columns,
                    numeric_columns,
                    show_y=True,
                    show_count_limit=False,
                )
                config_frame.place(
                    relx=0.56, rely=0.02, relwidth=0.25, relheight=0.12
                )
                x_column = config_frame.x_value.get()
                y_column = config_frame.y_value.get()
                title = f"{x_column} vs {y_column}"
                figure = ScatterRegressionPlot(
                    current_data[x_column], current_data[y_column]
                )
            else:
                return
        except (IndexError, ValueError, KeyError) as error:
            messagebox.showerror(
                "Could not draw graph",
                str(error),
            )
            return

        if graph_page is not None:
            graph_page.destroy()
        graph_page = Graph(title, root)
        graph_page.add_mpl_figure(figure)
        graph_page.place(relx=0.5, rely=0.16, relwidth=0.48, relheight=0.8)

    graph_selector = GraphParent(root, graph_names, render_graph)
    graph_selector.place(relx=0.3, rely=0.02, relwidth=0.25, relheight=0.12)
    config_frame = Config(
        root,
        lambda _column: render_graph(active_graph_name),
        lambda _column: render_graph(active_graph_name),
        lambda: render_graph(active_graph_name),
    )

    def finish_loading(generation, file_path, new_data, error):
        nonlocal table, current_data
        if generation != load_generation:
            return

        if error is not None:
            load_status.set("Import failed")
            messagebox.showerror("Could not open file", str(error))
            return

        try:
            current_data = new_data

            if table is not None:
                table.destroy()

            table = GraphObject(new_data, root)
            graph_selector.set_graph("Heatmap")
            render_graph("Heatmap")
            table.place(relx=0.02, rely=0.16, relwidth=0.46, relheight=0.8)
            load_status.set(
                f"Loaded {len(new_data):,} rows x {len(new_data.columns):,} columns"
            )
        except (OSError, pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
            load_status.set("Import failed")
            messagebox.showerror("Could not open file", str(error))

    def load_file(file_path):
        nonlocal load_generation
        load_generation += 1
        generation = load_generation
        file_name = file_path.replace("\\", "/").rsplit("/", 1)[-1]
        load_status.set(f"Loading {file_name}...")

        def read_csv_worker():
            try:
                new_data = pd.read_csv(file_path)
            except Exception as error:
                root.after(0, finish_loading, generation, file_path, None, error)
            else:
                root.after(0, finish_loading, generation, file_path, new_data, None)

        threading.Thread(target=read_csv_worker, daemon=True).start()

    FileDropFrame(root, load_file).place(
        relx=0.02, rely=0.02, relwidth=0.25, relheight=0.12
    )
    #load_file("cars.csv")
    root.mainloop()


if __name__ == "__main__":
    __main__()