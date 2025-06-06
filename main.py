import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
from datetime import datetime, timedelta


class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("800x600")

        # Configurações padrão
        self.work_time = 25
        self.break_time = 5
        self.timer_running = False
        self.start_time = None
        self.elapsed_time = 0
        self.current_task_id = None
        self.tasks = []
        self.task_counter = 0
        self.today = datetime.today().date()
        self.session_time = 0

        # Criar abas
        self.notebook = ttk.Notebook(root)
        self.tasks_tab = ttk.Frame(self.notebook)
        self.timer_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.tasks_tab, text="Tarefas")
        self.notebook.add(self.timer_tab, text="Temporizador")
        self.notebook.add(self.stats_tab, text="Estatísticas")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configurar abas
        self.setup_tasks_tab()
        self.setup_timer_tab()
        self.setup_stats_tab()

        # Atualizar relógio
        self.update_clock()

    def setup_tasks_tab(self):
        # Frame de entrada de tarefas
        input_frame = ttk.Frame(self.tasks_tab)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(input_frame, text="Nova Tarefa:").pack(side=tk.LEFT, padx=(0, 5))
        self.task_entry = ttk.Entry(input_frame, width=30)
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Label(input_frame, text="Tags/Projeto:").pack(side=tk.LEFT, padx=(10, 5))
        self.tag_entry = ttk.Entry(input_frame, width=15)
        self.tag_entry.pack(side=tk.LEFT, padx=5)

        add_btn = ttk.Button(input_frame, text="Adicionar", command=self.add_task)
        add_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Lista de tarefas
        columns = ("#1", "#2", "#3", "#4")
        self.task_tree = ttk.Treeview(
            self.tasks_tab, columns=columns, show="headings", selectmode="browse"
        )

        self.task_tree.heading("#1", text="ID")
        self.task_tree.heading("#2", text="Tarefa")
        self.task_tree.heading("#3", text="Tags")
        self.task_tree.heading("#4", text="Tempo")

        self.task_tree.column("#1", width=40, anchor="center")
        self.task_tree.column("#2", width=200, anchor="w")
        self.task_tree.column("#3", width=100, anchor="w")
        self.task_tree.column("#4", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(
            self.tasks_tab, orient="vertical", command=self.task_tree.yview
        )
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        self.task_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botões de ação
        btn_frame = ttk.Frame(self.tasks_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="Remover", command=self.remove_task).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Editar", command=self.edit_task).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Concluir", command=self.complete_task).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Trabalhar", command=self.set_active_task).pack(
            side=tk.RIGHT, padx=5
        )

    def setup_timer_tab(self):
        # Configurações de tempo
        config_frame = ttk.LabelFrame(self.timer_tab, text="Configurações de Tempo")
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(config_frame, text="Trabalho (min):").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.work_spin = ttk.Spinbox(config_frame, from_=1, to=60, width=5)
        self.work_spin.grid(row=0, column=1, padx=5, pady=5)
        self.work_spin.set(self.work_time)

        ttk.Label(config_frame, text="Descanso (min):").grid(
            row=0, column=2, padx=5, pady=5
        )
        self.break_spin = ttk.Spinbox(config_frame, from_=1, to=30, width=5)
        self.break_spin.grid(row=0, column=3, padx=5, pady=5)
        self.break_spin.set(self.break_time)

        ttk.Button(config_frame, text="Aplicar", command=self.apply_times).grid(
            row=0, column=4, padx=10, pady=5
        )

        # Display do temporizador
        timer_frame = ttk.Frame(self.timer_tab)
        timer_frame.pack(pady=20)

        self.timer_label = ttk.Label(
            timer_frame, text="25:00", font=("Helvetica", 48, "bold"), foreground="#333"
        )
        self.timer_label.pack(pady=10)

        self.task_label = ttk.Label(
            timer_frame,
            text="Nenhuma tarefa selecionada",
            font=("Helvetica", 12),
            foreground="#666",
        )
        self.task_label.pack(pady=5)

        # Botões de controle
        btn_frame = ttk.Frame(self.timer_tab)
        btn_frame.pack(pady=20)

        self.start_btn = ttk.Button(
            btn_frame, text="Iniciar", command=self.toggle_timer
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        ttk.Button(btn_frame, text="Resetar", command=self.reset_timer).pack(
            side=tk.LEFT, padx=10
        )

    def setup_stats_tab(self):
        # Estatísticas do dia
        today_frame = ttk.LabelFrame(
            self.stats_tab,
            text=f"Estatísticas do Dia ({self.today.strftime('%d/%m/%Y')})",
        )
        today_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(today_frame, text="Tarefas Concluídas:").pack(
            anchor="w", padx=10, pady=5
        )
        self.completed_label = ttk.Label(today_frame, text="0", font=("Helvetica", 14))
        self.completed_label.pack(anchor="w", padx=20, pady=(0, 10))

        ttk.Label(today_frame, text="Tempo Total Trabalhado:").pack(
            anchor="w", padx=10, pady=5
        )
        self.session_label = ttk.Label(
            today_frame, text="0 minutos", font=("Helvetica", 14)
        )
        self.session_label.pack(anchor="w", padx=20, pady=(0, 10))

        # Lista de tarefas concluídas
        columns = ("#1", "#2", "#3", "#4")
        self.completed_tree = ttk.Treeview(
            today_frame, columns=columns, show="headings"
        )

        self.completed_tree.heading("#1", text="Tarefa")
        self.completed_tree.heading("#2", text="Tags")
        self.completed_tree.heading("#3", text="Tempo (min)")
        self.completed_tree.heading("#4", text="Conclusão")

        self.completed_tree.column("#1", width=200, anchor="w")
        self.completed_tree.column("#2", width=100, anchor="w")
        self.completed_tree.column("#3", width=80, anchor="center")
        self.completed_tree.column("#4", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(
            today_frame, orient="vertical", command=self.completed_tree.yview
        )
        self.completed_tree.configure(yscrollcommand=scrollbar.set)

        self.completed_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Atualizar estatísticas
        self.update_stats()

    def add_task(self):
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("Campo Vazio", "Por favor, digite uma tarefa.")
            return

        tags = self.tag_entry.get().strip()
        self.task_counter += 1

        task = {
            "id": self.task_counter,
            "text": task_text,
            "tags": tags,
            "completed": False,
            "time_spent": 0,
            "created": datetime.now(),
            "completed_at": None,
        }

        self.tasks.append(task)
        self.task_tree.insert(
            "",
            "end",
            values=(
                task["id"],
                task["text"],
                task["tags"],
                f"{task['time_spent']//60}:{task['time_spent']%60:02d}",
            ),
        )

        self.task_entry.delete(0, tk.END)
        self.tag_entry.delete(0, tk.END)

    def remove_task(self):
        selected = self.task_tree.selection()
        if not selected:
            return

        item = self.task_tree.item(selected[0])
        task_id = item["values"][0]

        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self.task_tree.delete(selected[0])

        if self.current_task_id == task_id:
            self.current_task_id = None
            self.task_label.config(text="Nenhuma tarefa selecionada")

    def edit_task(self):
        selected = self.task_tree.selection()
        if not selected:
            return

        item = self.task_tree.item(selected[0])
        task_id = item["values"][0]
        task = next(t for t in self.tasks if t["id"] == task_id)

        new_text = simpledialog.askstring(
            "Editar Tarefa", "Editar descrição da tarefa:", initialvalue=task["text"]
        )

        if new_text and new_text.strip():
            task["text"] = new_text.strip()
            self.task_tree.item(
                selected[0],
                values=(
                    task["id"],
                    task["text"],
                    task["tags"],
                    f"{task['time_spent']//60}:{task['time_spent']%60:02d}",
                ),
            )

    def complete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            return

        item = self.task_tree.item(selected[0])
        task_id = item["values"][0]
        task = next(t for t in self.tasks if t["id"] == task_id)

        task["completed"] = True
        task["completed_at"] = datetime.now()

        self.task_tree.delete(selected[0])
        self.update_stats()

        if self.current_task_id == task_id:
            self.current_task_id = None
            self.task_label.config(text="Nenhuma tarefa selecionada")

    def set_active_task(self):
        selected = self.task_tree.selection()
        if not selected:
            return

        item = self.task_tree.item(selected[0])
        task_id = item["values"][0]
        self.current_task_id = task_id

        task = next(t for t in self.tasks if t["id"] == task_id)
        self.task_label.config(text=task["text"])

    def apply_times(self):
        try:
            self.work_time = int(self.work_spin.get())
            self.break_time = int(self.break_spin.get())
            self.reset_timer()
        except ValueError:
            messagebox.showerror("Valor Inválido", "Por favor, insira números válidos.")

    def toggle_timer(self):
        if not self.timer_running:
            if self.current_task_id is None:
                messagebox.showwarning("Sem Tarefa", "Selecione uma tarefa primeiro!")
                return

            self.timer_running = True
            self.start_btn.config(text="Pausar")
            self.start_time = time.time() - self.elapsed_time
            self.run_timer()
        else:
            self.timer_running = False
            self.start_btn.config(text="Continuar")

    def run_timer(self):
        if not self.timer_running:
            return

        current_time = time.time()
        self.elapsed_time = current_time - self.start_time
        remaining = max(self.work_time * 60 - self.elapsed_time, 0)

        mins, secs = divmod(int(remaining), 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

        # Atualizar tempo da tarefa a cada 10 segundos
        if int(self.elapsed_time) % 10 == 0:
            self.update_task_time()

        if remaining <= 0:
            self.timer_complete()
            return

        self.root.after(1000, self.run_timer)

    def update_task_time(self):
        if not self.current_task_id:
            return

        task = next(t for t in self.tasks if t["id"] == self.current_task_id)
        task["time_spent"] = int(self.elapsed_time)

        # Atualizar exibição na lista de tarefas
        for item in self.task_tree.get_children():
            values = self.task_tree.item(item)["values"]
            if values[0] == self.current_task_id:
                self.task_tree.item(
                    item,
                    values=(
                        values[0],
                        values[1],
                        values[2],
                        f"{task['time_spent']//60}:{task['time_spent']%60:02d}",
                    ),
                )
                break

    def timer_complete(self):
        self.timer_running = False
        self.update_task_time()

        # Registrar conclusão da sessão
        self.session_time += self.work_time

        # Atualizar estatísticas
        self.update_stats()

        # Tocar alarme
        self.root.bell()

        # Mostrar mensagem
        messagebox.showinfo(
            "Tempo Concluído",
            f"Tempo de trabalho terminado!\n\nHora de uma pausa de {self.break_time} minutos.",
        )

        self.reset_timer()

    def reset_timer(self):
        self.timer_running = False
        self.elapsed_time = 0
        self.start_btn.config(text="Iniciar")
        self.timer_label.config(text=f"{self.work_time:02d}:00")

    def update_stats(self):
        # Calcular tarefas concluídas hoje
        completed_today = [
            t
            for t in self.tasks
            if t["completed"] and t["completed_at"].date() == self.today
        ]

        # Calcular tempo total da sessão
        session_minutes = self.session_time + sum(
            t["time_spent"] // 60 for t in completed_today
        )

        # Atualizar labels
        self.completed_label.config(text=str(len(completed_today)))
        self.session_label.config(text=f"{session_minutes} minutos")

        # Atualizar lista de tarefas concluídas
        for item in self.completed_tree.get_children():
            self.completed_tree.delete(item)

        for task in completed_today:
            time_spent_min = task["time_spent"] // 60
            completion_time = task["completed_at"].strftime("%H:%M")
            self.completed_tree.insert(
                "",
                "end",
                values=(task["text"], task["tags"], time_spent_min, completion_time),
            )

    def update_clock(self):
        now = datetime.now()
        # Verificar se mudou o dia
        if now.date() != self.today:
            self.today = now.date()
            self.session_time = 0
            self.setup_stats_tab()

        self.root.after(60000, self.update_clock)  # Verificar a cada minuto


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
