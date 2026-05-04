import random
import json
import os
from tkinter import *
from tkinter import ttk, messagebox

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Предопределённые задачи с типами
        self.tasks_db = {
            "Учёба": [
                "Прочитать статью по Python",
                "Решить 5 математических задач",
                "Посмотреть лекцию по истории",
                "Написать конспект по физике",
                "Выучить 10 новых английских слов"
            ],
            "Спорт": [
                "Сделать зарядку (15 мин)",
                "Пробежка 3 км",
                "Отжимания 20 раз",
                "Планка 2 минуты",
                "Растяжка 10 минут"
            ],
            "Работа": [
                "Сделать отчёт по проекту",
                "Ответить на важные письма",
                "Провести код-ревью",
                "Написать документацию",
                "Спланировать задачи на неделю"
            ]
        }

        # История сгенерированных задач (каждый элемент: {"task": "...", "type": "..."})
        self.history_file = "task_history.json"
        self.history = self.load_history()

        # Переменные для фильтрации
        self.filter_type = StringVar(value="Все")

        self.create_widgets()
        self.update_history_display()

    def create_widgets(self):
        # Рамка для генерации
        gen_frame = LabelFrame(self.root, text="Генератор задач", padx=10, pady=10)
        gen_frame.pack(fill="x", padx=10, pady=5)

        self.generate_btn = Button(gen_frame, text="Сгенерировать задачу", 
                                   command=self.generate_task, bg="lightblue", font=("Arial", 12))
        self.generate_btn.pack(pady=5)

        self.current_task_label = Label(gen_frame, text="Нажмите кнопку, чтобы получить задачу", 
                                        font=("Arial", 11), fg="green", wraplength=500)
        self.current_task_label.pack(pady=5)

        # Рамка для фильтрации
        filter_frame = LabelFrame(self.root, text="Фильтр по типу", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        types = ["Все"] + list(self.tasks_db.keys())
        for t in types:
            Radiobutton(filter_frame, text=t, variable=self.filter_type, 
                        value=t, command=self.update_history_display).pack(side="left", padx=10)

        # Рамка для истории
        history_frame = LabelFrame(self.root, text="История задач", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Список с прокруткой
        scrollbar = Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_listbox = Listbox(history_frame, yscrollcommand=scrollbar.set, 
                                        font=("Arial", 10), height=12)
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Кнопки управления историей
        btn_frame = Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        Button(btn_frame, text="Очистить историю", command=self.clear_history, 
               bg="salmon").pack(side="left", padx=5)
        Button(btn_frame, text="Добавить свою задачу", command=self.add_custom_task, 
               bg="lightgreen").pack(side="left", padx=5)

        # Статусная строка
        self.status_label = Label(self.root, text="Готово", bd=1, relief=SUNKEN, anchor=W)
        self.status_label.pack(side="bottom", fill="x")

    def generate_task(self):
        """Выбирает случайную задачу из всех или отфильтрованных"""
        if self.filter_type.get() == "Все":
            # Собираем все задачи из всех категорий
            all_tasks = []
            for task_type, tasks in self.tasks_db.items():
                for task in tasks:
                    all_tasks.append((task, task_type))
            if not all_tasks:
                messagebox.showwarning("Нет задач", "Добавьте хотя бы одну задачу!")
                return
            selected_task, task_type = random.choice(all_tasks)
        else:
            # Выбираем из конкретной категории
            selected_type = self.filter_type.get()
            if selected_type not in self.tasks_db or not self.tasks_db[selected_type]:
                messagebox.showwarning("Нет задач", f"В категории '{selected_type}' нет задач!")
                return
            selected_task = random.choice(self.tasks_db[selected_type])
            task_type = selected_type

        # Добавляем в историю
        self.history.append({"task": selected_task, "type": task_type})
        self.save_history()
        self.current_task_label.config(text=f"✓ {selected_task} [{task_type}]")
        self.update_history_display()
        self.status_label.config(text=f"Сгенерирована задача: {selected_task}")

    def update_history_display(self):
        """Обновляет отображение истории с учётом фильтра"""
        self.history_listbox.delete(0, END)
        
        filtered = self.filter_history()
        for i, item in enumerate(filtered, 1):
            display_text = f"{i}. [{item['type']}] {item['task']}"
            self.history_listbox.insert(END, display_text)
        
        if not filtered:
            self.history_listbox.insert(END, "История пуста (или фильтр ничего не показывает)")

    def filter_history(self):
        """Фильтрует историю по выбранному типу"""
        if self.filter_type.get() == "Все":
            return self.history
        else:
            return [item for item in self.history if item["type"] == self.filter_type.get()]

    def add_custom_task(self):
        """Диалог добавления новой задачи"""
        dialog = Toplevel(self.root)
        dialog.title("Добавить задачу")
        dialog.geometry("400x200")
        dialog.grab_set()

        Label(dialog, text="Название задачи:", font=("Arial", 10)).pack(pady=5)
        task_entry = Entry(dialog, width=40)
        task_entry.pack(pady=5)

        Label(dialog, text="Тип задачи:", font=("Arial", 10)).pack(pady=5)
        type_var = StringVar()
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=list(self.tasks_db.keys()), width=37)
        type_combo.pack(pady=5)

        def save_task():
            task_text = task_entry.get().strip()
            task_type = type_var.get().strip()

            # Проверка на пустую строку
            if not task_text:
                messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
                return
            if not task_type:
                messagebox.showerror("Ошибка", "Выберите тип задачи!")
                return
            if task_type not in self.tasks_db:
                messagebox.showerror("Ошибка", "Некорректный тип задачи!")
                return

            # Добавляем задачу
            self.tasks_db[task_type].append(task_text)
            self.save_tasks_to_file()
            dialog.destroy()
            self.status_label.config(text=f"Добавлена задача: {task_text} [{task_type}]")
            messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена в категорию '{task_type}'")

        Button(dialog, text="Сохранить", command=save_task, bg="lightgreen").pack(pady=10)

    def clear_history(self):
        """Очищает историю после подтверждения"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю задач?"):
            self.history = []
            self.save_history()
            self.update_history_display()
            self.status_label.config(text="История очищена")
            self.current_task_label.config(text="Нажмите кнопку, чтобы получить задачу")

    def save_history(self):
        """Сохраняет историю в JSON файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def load_history(self):
        """Загружает историю из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_tasks_to_file(self):
        """Сохраняет задачи в отдельный JSON (опционально)"""
        try:
            with open("tasks_db.json", 'w', encoding='utf-8') as f:
                json.dump(self.tasks_db, f, ensure_ascii=False, indent=2)
        except:
            pass

if __name__ == "__main__":
    root = Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()