import os
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser

# === Setup Root ===
root = tk.Tk()
root.title(" Git Loader – Push & Clone")
root.geometry("750x530")
root.config(bg="#f8f9fa")
root.resizable(False, False)

FONT = ("Segoe UI", 10)
ENTRY_WIDTH = 64

# === Helper Functions ===
def select_folder(entry):
    folder = filedialog.askdirectory()
    if folder:
        entry.delete(0, tk.END)
        entry.insert(0, folder)

def safe_update_status(text, color="black"):
    def update():
        push_status_label.config(text=text, fg=color)
    root.after(0, update)

def run_git_push_worker(folder_path, repo_link, token, replace=False):
    folder_name = os.path.basename(folder_path.rstrip("/\\"))
    branch = "main"
    temp_dir = os.path.abspath("temp_git_repo_push")

    try:
        safe_update_status("Preparing temporary directory...", "orange")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        remote_url = repo_link.replace("https://", f"https://{token}@")

        safe_update_status("Cloning repository...", "orange")
        subprocess.run(["git", "clone", remote_url, temp_dir], check=True)

        # Prevent recursive copy if user selects a folder inside temp_dir
        folder_path = os.path.abspath(folder_path)
        if os.path.commonpath([folder_path, temp_dir]) == temp_dir:
            raise Exception("Do not select a folder inside the temporary directory.")

        if replace:
            safe_update_status("Replacing repository contents...", "orange")
            for item in os.listdir(temp_dir):
                if item != ".git":
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)

        safe_update_status("Copying folder contents...", "orange")
        for item in os.listdir(folder_path):
            s = os.path.join(folder_path, item)
            d = os.path.join(temp_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        os.chdir(temp_dir)

        safe_update_status("Configuring Git user...", "orange")
        subprocess.run(["git", "config", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Your Name"], check=True)

        safe_update_status("Adding changes...", "orange")
        subprocess.run(["git", "add", "."], check=True)

        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout.strip():
            safe_update_status("Committing changes...", "orange")
            subprocess.run(["git", "commit", "-m", f"Pushed folder {folder_name} via Git Loader"], check=True)

            safe_update_status("Pushing to remote...", "orange")
            subprocess.run(["git", "push", "origin", branch], check=True)

            safe_update_status("Push successful!", "green")
            messagebox.showinfo("✅ Success", f"Folder '{folder_name}' pushed via Git Loader!")
        else:
            safe_update_status("No changes to commit.", "blue")
            messagebox.showinfo("No Changes", "Nothing to commit.")
    except subprocess.CalledProcessError as e:
        safe_update_status("Git error occurred.", "red")
        messagebox.showerror("Git Error", str(e))
    except Exception as e:
        safe_update_status("Unexpected error occurred.", "red")
        messagebox.showerror("Error", str(e))
    finally:
        os.chdir("..")
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

def run_git_push(folder_path, repo_link, token, replace=False):
    if not folder_path or not repo_link or not token:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    threading.Thread(target=run_git_push_worker, args=(folder_path, repo_link, token, replace), daemon=True).start()

def run_git_clone(repo_link, destination):
    try:
        subprocess.run(["git", "clone", repo_link, destination], check=True)
        messagebox.showinfo("✅ Success", "Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Git clone failed:\n{e}")

def open_contact():
    webbrowser.open("https://myporfolio-1o1h.onrender.com/contact")

# === Styled Entry ===
def styled_entry(parent):
    e = tk.Entry(parent, font=FONT, width=ENTRY_WIDTH, bd=0, highlightthickness=2,
                 highlightbackground="#ccc", highlightcolor="#7f9cf5", relief="flat")
    return e

# === Styled Button ===
def styled_button(parent, text, command):
    b = tk.Button(parent, text=text, command=command,
                  font=("Segoe UI Semibold", 10),
                  bg="#7f9cf5", fg="white", activebackground="#5a75d8",
                  bd=0, relief="flat", padx=10, pady=5)
    b.bind("<Enter>", lambda e: b.config(bg="#5a75d8"))
    b.bind("<Leave>", lambda e: b.config(bg="#7f9cf5"))
    return b

# === Tabs ===
notebook = tk.Frame(root, bg="#f8f9fa")
notebook.pack(pady=15)

tab_buttons = tk.Frame(notebook, bg="#f8f9fa")
tab_buttons.pack()

active_tab = tk.StringVar(value="push")

def switch_tab(name):
    active_tab.set(name)
    push_frame.pack_forget()
    clone_frame.pack_forget()
    if name == "push":
        push_frame.pack()
    else:
        clone_frame.pack()
    push_btn.config(bg="#d4e0fc" if name == "push" else "#e8e8e8")
    clone_btn.config(bg="#d4e0fc" if name == "clone" else "#e8e8e8")

push_btn = tk.Button(tab_buttons, text="Push to GitHub", command=lambda: switch_tab("push"),
                     bg="#d4e0fc", font=("Segoe UI", 10), bd=0, padx=20, pady=8)
clone_btn = tk.Button(tab_buttons, text="Clone from GitHub", command=lambda: switch_tab("clone"),
                      bg="#e8e8e8", font=("Segoe UI", 10), bd=0, padx=20, pady=8)
push_btn.grid(row=0, column=0)
clone_btn.grid(row=0, column=1)

# === Push Frame ===
push_frame = tk.Frame(root, bg="#f8f9fa")
push_frame.pack()

tk.Label(push_frame, text="📁 Local Folder Path", bg="#f8f9fa", font=FONT).pack(pady=(10, 2))
push_path = styled_entry(push_frame)
push_path.pack()
styled_button(push_frame, "Browse", lambda: select_folder(push_path)).pack(pady=5)

tk.Label(push_frame, text="🔗 GitHub Repo Link", bg="#f8f9fa", font=FONT).pack(pady=(10, 2))
repo_link = styled_entry(push_frame)
repo_link.pack()

tk.Label(push_frame, text="🔐 GitHub Access Token", bg="#f8f9fa", font=FONT).pack(pady=(10, 2))
token = styled_entry(push_frame)
token.config(show="*")
token.pack()

btn_row = tk.Frame(push_frame, bg="#f8f9fa")
btn_row.pack(pady=15)
styled_button(btn_row, "Update", lambda: run_git_push(push_path.get(), repo_link.get(), token.get(), False)).grid(row=0, column=0, padx=10)
styled_button(btn_row, "Replace", lambda: run_git_push(push_path.get(), repo_link.get(), token.get(), True)).grid(row=0, column=1, padx=10)

push_status_label = tk.Label(push_frame, text="", bg="#f8f9fa", font=("Segoe UI", 10, "italic"))
push_status_label.pack(pady=(5,10))

# === Clone Frame ===
clone_frame = tk.Frame(root, bg="#f8f9fa")

tk.Label(clone_frame, text="🔗 GitHub Repo Link", bg="#f8f9fa", font=FONT).pack(pady=(10, 2))
clone_link = styled_entry(clone_frame)
clone_link.pack()

tk.Label(clone_frame, text="📂 Destination Folder", bg="#f8f9fa", font=FONT).pack(pady=(10, 2))
clone_dest = styled_entry(clone_frame)
clone_dest.pack()
styled_button(clone_frame, "Browse", lambda: select_folder(clone_dest)).pack(pady=5)
styled_button(clone_frame, "Clone Repo", lambda: run_git_clone(clone_link.get(), clone_dest.get())).pack(pady=20)

# === Footer ===
footer = tk.Frame(root, bg="#f8f9fa")
footer.pack(side="bottom", pady=10)
tk.Label(footer, text="💬 For help or queries: ", bg="#f8f9fa", font=FONT).pack(side="left")
link = tk.Label(footer, text="Contact Developer", fg="blue", bg="#f8f9fa", cursor="hand2", font=("Segoe UI", 10, "underline"))
link.pack(side="left")
link.bind("<Button-1>", lambda e: open_contact())

root.mainloop()
