import tkinter as tk
from PIL import Image, ImageTk
from gui.login_view import LoginView
from gui.register_view import RegisterView

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HealthTime")
        self.root.geometry("500x450")

        self.theme = tk.StringVar(value="light")

        self.render()

    def render(self):
        theme = self.theme.get()

        if theme == "dark":
            self.bg_color = "#16212A"
            self.card_color = "#253747"
            self.text_color = "#EAEAEA"
            self.accent = "#4FC3F7"
        else:
            self.bg_color = "#f0f2f5"
            self.card_color = "#FFFFFF"
            self.text_color = "#000000"
            self.accent = "#4CAF50"

        self.root.configure(bg=self.bg_color)

        for widget in self.root.winfo_children():
            widget.destroy()

        logo_path = "assets/logo_dark.png" if theme == "dark" else "assets/logo_light.png"
        img = Image.open(logo_path).resize((120, 120))
        self.logo_img = ImageTk.PhotoImage(img)

        logo_label = tk.Label(self.root, image=self.logo_img, bg=self.bg_color)
        logo_label.pack(pady=(25, 10))

        card = tk.Frame(self.root, bg=self.card_color, padx=30, pady=30)
        card.pack(pady=20)

        tk.Label(
            card,
            text="Welcome to HealthTime",
            font=("Helvetica", 18, "bold"),
            bg=self.card_color,
            fg=self.accent
        ).pack(pady=(0, 20))

        tk.Label(
            card,
            text="Theme",
            bg=self.card_color,
            fg=self.text_color
        ).pack(anchor="w")

        theme_menu = tk.OptionMenu(card, self.theme, "light", "dark", command=lambda _: self.render())
        theme_menu.config(bg=self.bg_color, fg=self.text_color, relief="flat")
        theme_menu["menu"].config(bg=self.bg_color, fg=self.text_color)
        theme_menu.pack(fill="x", pady=(5, 20))

        tk.Button(
            card,
            text="Login",
            bg=self.accent,
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            pady=10,
            command=self.open_login
        ).pack(fill="x", pady=(0, 10))

        tk.Button(
            card,
            text="Register",
            bg="#607D8B",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            pady=10,
            command=self.open_register
        ).pack(fill="x")

    def open_login(self):
        login_window = tk.Toplevel(self.root)
        LoginView(login_window, theme=self.theme.get())

    def open_register(self):
        register_window = tk.Toplevel(self.root)
        RegisterView(register_window, theme=self.theme.get())


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
