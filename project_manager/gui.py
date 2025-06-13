import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from database import session
from models import User, Project, Task
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Proyectos")
        self.root.geometry("400x700")
        self.user = None
        self.logo_url = "https://i.pinimg.com/736x/6f/81/d6/6f81d6bc3814c64bc2410b0f9f481257.jpg"
        self.font = ("Segoe UI", 14, "bold")  # Fuente en negrita
        self.login_screen()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_logo(self, frame):
        try:
            response = requests.get(self.logo_url)
            image = Image.open(BytesIO(response.content)).resize((110, 95))
            logo = ImageTk.PhotoImage(image)
            label = ctk.CTkLabel(frame, image=logo, text="")
            label.image = logo
            label.pack(pady=(0, 10))
        except:
            pass

    def login_screen(self):
        self.clear()
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(expand=True, padx=30, pady=30)
        self.show_logo(frame)

        ctk.CTkLabel(frame, text="Iniciar Sesión", font=("Segoe UI", 20, "bold")).pack(pady=(5, 15))
        self.username = ctk.CTkEntry(frame, placeholder_text="Usuario", font=self.font)
        self.username.pack(pady=4, fill="x", padx=20)
        self.password = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", font=self.font)
        self.password.pack(pady=4, fill="x", padx=20)

        ctk.CTkButton(frame, text="Iniciar Sesión", command=self.login, font=self.font, height=32, fg_color="#6a0dad").pack(pady=8, fill="x", padx=20)
        ctk.CTkButton(frame, text="Registrarse", command=self.register, font=self.font, height=32, fg_color="#6a0dad").pack(pady=4, fill="x", padx=20)

    def login(self):
        if not self.username.get() or not self.password.get():
            messagebox.showwarning("Advertencia", "Por favor, ingrese su nombre de usuario y contraseña.")
            return
        
    def login(self):
        user = session.query(User).filter_by(username=self.username.get(), password=self.password.get()).first()
        if user:
            self.user = user
            self.main_menu()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def register(self):
        if not self.username.get() or not self.password.get():
            messagebox.showwarning("Advertencia", "Por favor, ingrese un nombre de usuario y una contraseña -_-")
            return
          
        user = User(username=self.username.get(), password=self.password.get(), role="member")
        session.add(user)
        session.commit()
        messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente! ^^")
    def main_menu(self):
        self.clear()
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(frame, text=f"👤 Bienvenido, {self.user.username}", font=("Segoe UI", 18, "bold")).pack(pady=10)

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="➕ Crear Proyecto", command=self.create_project_screen, font=self.font, height=28, fg_color="#6a0dad").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="📋 Ver Proyectos", command=self.view_projects, font=self.font, height=28, fg_color="#6a0dad").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="✅ Ver Tareas Completadas", command=self.view_completed_tasks, font=self.font, height=28, fg_color="#6a0dad").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="🚪 Cerrar Sesión", command=self.login_screen, font=self.font, height=28, fg_color="#6a0dad").pack(side="left", padx=5)

        self.show_pending_tasks(frame)

    def show_pending_tasks(self, frame):
        ctk.CTkLabel(frame, text="Tareas Pendientes", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))

        pending_tasks = session.query(Task).filter_by(status="pendiente").all()
        if not pending_tasks:
            ctk.CTkLabel(frame, text="No hay tareas pendientes.", font=self.font).pack()
        else:
            for task in pending_tasks:
                task_frame = ctk.CTkFrame(frame, corner_radius=10, fg_color="#161616")
                task_frame.pack(pady=4, padx=20, fill="x")

                ctk.CTkLabel(task_frame, text=f"📌 {task.description}", font=("Segoe UI", 14)).pack(anchor="w", padx=10, pady=(4, 0))
                ctk.CTkLabel(task_frame, text=f"Vence: {task.due_date.strftime('%Y-%m-%d')}", font=("Segoe UI", 11), text_color="#aaaaaa").pack(anchor="w", padx=10)

    def create_project_screen(self):
        self.clear()
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame, text="Nuevo Proyecto", font=("Segoe UI", 18, "bold")).pack(pady=10)
        name_entry = ctk.CTkEntry(frame, placeholder_text="Nombre del Proyecto", font=self.font)
        name_entry.pack(fill="x", pady=5, padx=20)
        desc_entry = ctk.CTkEntry(frame, placeholder_text="Descripción", font=self.font)
        desc_entry.pack(fill="x", pady=5, padx=20)

        # Entradas de fecha con autocompletado
        start_entry = ctk.CTkEntry(frame, placeholder_text="Inicio (YYYY-MM-DD)", font=self.font)
        start_entry.pack(fill="x", pady=5, padx=20)
        end_entry = ctk.CTkEntry(frame, placeholder_text="Fin (YYYY-MM-DD)", font=self.font)
        end_entry.pack(fill="x", pady=5, padx=20)

        # Agregar eventos para autocompletar las fechas
        self.setup_date_autocomplete(start_entry)
        self.setup_date_autocomplete(end_entry)

        def create():
            try:
                project = Project(
                    name=name_entry.get(),
                    description=desc_entry.get(),
                    start_date=datetime.strptime(start_entry.get(), "%Y-%m-%d"),
                    end_date=datetime.strptime(end_entry.get(), "%Y-%m-%d")
                )
                session.add(project)
                session.commit()
                messagebox.showinfo("Éxito", "Proyecto creado correctamente")
                self.main_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Hubo un problema: {e}")

        ctk.CTkButton(frame, text="Guardar Proyecto", command=create, font=self.font, height=32, fg_color="#6a0dad").pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame, text="Volver", command=self.main_menu, font=self.font, height=30, fg_color="#6a0dad").pack(fill="x", padx=20)

    def setup_date_autocomplete(self, entry):
        def on_key_release(event):
            text = entry.get()
            # Formatear la fecha mientras se escribe
            if len(text) == 4 and text.isdigit():
                entry.insert(4, "-")
            elif len(text) == 7 and text[4] == "-":
                entry.insert(7, "-")

        entry.bind("<KeyRelease>", on_key_release)

    def view_projects(self):
        self.clear()
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(frame, text="📋 Lista de Proyectos", font=("Segoe UI", 18, "bold")).pack(pady=10)

        projects = session.query(Project).all()
        if not projects:
            ctk.CTkLabel(frame, text="No hay proyectos disponibles.", font=self.font).pack()
        else:
            for project in projects:
                card = ctk.CTkFrame(frame, corner_radius=12, fg_color="#1e1e1e")
                card.pack(pady=6, padx=20, fill="x")

                ctk.CTkLabel(card, text=f"📁 {project.name}", font=("Segoe UI", 16)).pack(anchor="w", padx=10, pady=(5, 0))
                ctk.CTkLabel(card, text=project.description, font=("Segoe UI", 12), text_color="#a0a0a0").pack(anchor="w", padx=10)

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(padx=10, pady=6, fill="x")
                ctk.CTkButton(btn_frame, text="Ver Tareas", width=100, command=lambda p=project: self.view_tasks(p), font=self.font, height=30, fg_color="#6a0dad").pack(side="left", padx=5)
                ctk.CTkButton(btn_frame, text="✏️ Editar", width=80, command=lambda p=project: self.edit_project_screen(p), font=self.font, height=30, fg_color="#6a0dad").pack(side="left", padx=5)
                ctk.CTkButton(btn_frame, text="❌ Eliminar", width=80, command=lambda p=project: self.delete_project(p), font=self.font, height=30, fg_color="#c62828", hover_color="#e53935").pack(side="left", padx=5)

        ctk.CTkButton(frame, text="Volver", command=self.main_menu, font=self.font, height=30, fg_color="#6a0dad").pack(pady=10, fill="x", padx=20)

    def delete_project(self, project):
        if messagebox.askyesno("Confirmar eliminación", f"¿Está seguro que desea eliminar el proyecto '{project.name}' y todas sus tareas?"):
            session.delete(project)
            session.commit()
            messagebox.showinfo("Eliminado", "Proyecto eliminado correctamente")
            self.view_projects()

    def edit_project_screen(self, project):
        self.clear()
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame, text="Editar Proyecto", font=("Segoe UI", 18, "bold")).pack(pady=10)
        name_entry = ctk.CTkEntry(frame, placeholder_text="Nombre", font=self.font)
        name_entry.insert(0, project.name)
        name_entry.pack(fill="x", pady=5, padx=20)
        desc_entry = ctk.CTkEntry(frame, placeholder_text="Descripción", font=self.font)
        desc_entry.insert(0, project.description)
        desc_entry.pack(fill="x", pady=5, padx=20)

        def save_changes():
            project.name = name_entry.get()
            project.description = desc_entry.get()
            session.commit()
            messagebox.showinfo("Actualizado", "Proyecto actualizado correctamente")
            self.view_projects()

        ctk.CTkButton(frame, text="Guardar Cambios", command=save_changes, font=self.font, height=32, fg_color="#6a0dad").pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame, text="Volver", command=self.view_projects, font=self.font, height=30, fg_color="#6a0dad").pack(fill="x", padx=20)

    def view_tasks(self, project):
        self.clear()
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(frame, text=f"Tareas de {project.name}", font=("Segoe UI", 18, "bold")).pack(pady=10)

        tasks = session.query(Task).filter_by(project_id=project.id).all()
        if not tasks:
            ctk.CTkLabel(frame, text="No hay tareas registradas.", font=self.font).pack()
        else:
            for task in tasks:
                card = ctk.CTkFrame(frame, corner_radius=10, fg_color="#2a2a2a")
                card.pack(pady=6, padx=20, fill="x")

                sticker = "✅" if task.status == "completada" else "📌"
                ctk.CTkLabel(card, text=f"{sticker} {task.description}", font=("Segoe UI", 14)).pack(anchor="w", padx=10, pady=(4, 0))
                ctk.CTkLabel(card, text=f"Estado: {task.status} | Vence: {task.due_date.strftime('%Y-%m-%d')}", font=("Segoe UI", 11), text_color="#aaaaaa").pack(anchor="w", padx=10)

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(pady=4, padx=10, fill="x")
                ctk.CTkButton(btn_frame, text="✔️ Completar", width=80, command=lambda t=task: self.complete_task(t, project), font=self.font, height=28, fg_color="#6a0dad").pack(side="left", padx=4)
                ctk.CTkButton(btn_frame, text="✏️ Editar", width=80, command=lambda t=task: self.edit_task_screen(t, project), font=self.font, height=28, fg_color="#6a0dad").pack(side="left", padx=4)
                ctk.CTkButton(btn_frame, text="❌ Eliminar", width=100, command=lambda t=task: self.delete_task(t, project), font=self.font, height=28, fg_color="#c62828", hover_color="#e53935").pack(side="left", padx=4)

        ctk.CTkButton(frame, text="➕ Nueva Tarea", command=lambda: self.create_task_screen(project), font=self.font, height=30, fg_color="#6a0dad").pack(pady=8, fill="x", padx=20)
        ctk.CTkButton(frame, text="Volver", command=self.view_projects, font=self.font, height=30, fg_color="#6a0dad").pack(fill="x", padx=20)

    def complete_task(self, task, project):
        task.status = "completada"
        session.commit()
        messagebox.showinfo("Tarea Completada", "La tarea ha sido marcada como completada.")
        self.view_tasks(project)

    def create_task_screen(self, project):
        self.clear()
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame, text=f"Nueva Tarea - {project.name}", font=("Segoe UI", 18, "bold")).pack(pady=10)
        desc_entry = ctk.CTkEntry(frame, placeholder_text="Miembro", font=self.font)
        desc_entry.pack(fill="x", pady=5, padx=20)
        desc_entry = ctk.CTkEntry(frame, placeholder_text="Descripción", font=self.font)
        desc_entry.pack(fill="x", pady=5, padx=20)
        due_entry = ctk.CTkEntry(frame, placeholder_text="Vence (YYYY-MM-DD)", font=self.font)
        due_entry.pack(fill="x", pady=5, padx=20)
     
        # Agregar evento para autocompletar la fecha
        self.setup_date_autocomplete(due_entry)

        def save_task():
            try:
                task = Task(
                    description=desc_entry.get(),
                    due_date=datetime.strptime(due_entry.get(), "%Y-%m-%d"),
                    project_id=project.id,
                    status="pendiente"
                )
                session.add(task)
                session.commit()
                messagebox.showinfo("Tarea creada", "Tarea guardada exitosamente.")
                self.view_tasks(project)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

        ctk.CTkButton(frame, text="Guardar Tarea", command=save_task, font=self.font, height=30, fg_color="#6a0dad").pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame, text="Volver", command=lambda: self.view_tasks(project), font=self.font, height=30, fg_color="#6a0dad").pack(fill="x", padx=20)

    def edit_task_screen(self, task, project):
        self.clear()
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame, text="Editar Tarea", font=("Segoe UI", 18, "bold")).pack(pady=10)
        desc_entry = ctk.CTkEntry(frame, placeholder_text="Descripción", font=self.font)
        desc_entry.insert(0, task.description)
        desc_entry.pack(fill="x", pady=5, padx=20)
        due_entry = ctk.CTkEntry(frame, placeholder_text="Vence (YYYY-MM-DD)", font=self.font)
        due_entry.insert(0, task.due_date.strftime('%Y-%m-%d'))
        due_entry.pack(fill="x", pady=5, padx=20)

        # Agregar evento para autocompletar la fecha
        self.setup_date_autocomplete(due_entry)

        def save_changes():
            try:
                task.description = desc_entry.get()
                task.due_date = datetime.strptime(due_entry.get(), "%Y-%m-%d")
                session.commit()
                messagebox.showinfo("Actualizado", "Tarea actualizada correctamente")
                self.view_tasks(project)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")

        ctk.CTkButton(frame, text="Guardar Cambios", command=save_changes, font=self.font, height=30, fg_color="#6a0dad").pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame, text="Volver", command=lambda: self.view_tasks(project), font=self.font, height=30, fg_color="#6a0dad").pack(fill="x", padx=20)

    def delete_task(self, task, project):
        session.delete(task)
        session.commit()
        self.view_tasks(project)

    def view_completed_tasks(self):
        self.clear()
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(frame, text="Tareas Completadas", font=("Segoe UI", 18, "bold")).pack(pady=10)

        completed_tasks = session.query(Task).filter_by(status="completada").all()
        if not completed_tasks:
            ctk.CTkLabel(frame, text="No hay tareas completadas.", font=self.font).pack()
        else:
            for task in completed_tasks:
                card = ctk.CTkFrame(frame, corner_radius=10, fg_color="#2a2a2a")
                card.pack(pady=6, padx=20, fill="x")

                ctk.CTkLabel(card, text=f"✅ {task.description}", font=("Segoe UI", 14)).pack(anchor="w", padx=10, pady=(4, 0))
                ctk.CTkLabel(card, text=f"Vence: {task.due_date.strftime('%Y-%m-%d')}", font=("Segoe UI", 11), text_color="#aaaaaa").pack(anchor="w", padx=10)

        ctk.CTkButton(frame, text="Volver", command=self.main_menu, font=self.font, height=30, fg_color="#6a0dad").pack(pady=10, fill="x", padx=20)

    def setup_date_autocomplete(self, entry):
        def on_key_release(event):
            text = entry.get()
            if len(text) == 4 and text.isdigit():
                entry.insert(4, "-")
            elif len(text) == 7 and text[4] == "-":
                entry.insert(7, "-")
        entry.bind("<KeyRelease>", on_key_release)


if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()

