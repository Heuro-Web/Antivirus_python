import os
import time
import winsound
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


signatures = {
    "EICAR_Test": "X5O!P%@AP[4\\PZX54(P^)7CC)7}EICAR-STANDARD-ANTIVIRUS-TEST-FILE!H+H*"
}

infected_files = []
scanning = False
stop_scan = False

def scan_file(file_path):
    try:
        with open(file_path, 'r', errors='ignore') as file:
            content = file.read()
            for name, signature in signatures.items():
                if signature in content:
                    infected_files.append(file_path)
    except:
        pass

def count_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count

def scan_directory(directory):
    global scanning, stop_scan
    infected_files.clear()
    scanning = True
    stop_scan = False

    total_files = count_files(directory)
    scanned = 0
    start_time = time.time()
    status_label.config(text="🔍 Scan en cours...")
    progress["maximum"] = total_files
    progress["value"] = 0
    root.update()

    for root_dir, dirs, files in os.walk(directory):
        for file in files:
            if stop_scan:
                status_label.config(text="⛔ Scan interrompu.")
                scanning = False
                return

            file_path = os.path.join(root_dir, file)
            scan_file(file_path)

            scanned += 1
            progress["value"] = scanned

            # Estimation du temps restant
            elapsed_time = time.time() - start_time
            avg_time = elapsed_time / scanned if scanned else 0
            remaining_time = avg_time * (total_files - scanned)
            percent = int((scanned / total_files) * 100)

            status_label.config(
                text=f"🔍 {percent}% - Temps restant estimé : {int(remaining_time)} sec"
            )
            root.update()

    scanning = False
    duration = time.time() - start_time
    progress["value"] = total_files
    status_label.config(text=f"✅ Scan terminé en {round(duration, 2)} secondes.")

    if infected_files:
        winsound.Beep(1000, 500)
        msg = f"🚨 Virus détecté dans {len(infected_files)} fichier(s).\n"
        msg += f"🧾 {scanned} fichiers scannés en {round(duration, 2)} secondes.\n\n"
        msg += "\n".join(infected_files)
        messagebox.showwarning("Résultat du Scan", msg)
    else:
        messagebox.showinfo(
            "Résultat du Scan",
            f"🟢 Aucun virus détecté.\n🧾 {scanned} fichiers scannés en {round(duration, 2)} secondes."
        )

def select_directory():
    if scanning:
        messagebox.showinfo("Scan en cours", "⏳ Un scan est déjà en cours.")
        return
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        scan_directory(folder_selected)

def cancel_scan():
    global scanning, stop_scan
    if scanning:
        answer = messagebox.askyesno("Annuler le scan", "⚠️ Voulez-vous vraiment interrompre le scan ?")
        if answer:
            stop_scan = True

def delete_infected():
    if not infected_files:
        messagebox.showinfo("Suppression", "Aucun fichier infecté à supprimer.")
        return

    confirm = messagebox.askyesno("Suppression", "⚠️ Supprimer tous les fichiers infectés ?")
    if confirm:
        for file_path in infected_files:
            try:
                os.remove(file_path)
            except:
                pass
            messagebox.showinfo("Suppression", "✅ Tous les fichiers infectés ont été supprimés.")
            infected_files.clear()


root = tk.Tk()
root.title("🔒 Mini Antivirus Python")
root.geometry("460x340")

label = tk.Label(root, text="Antivirus Python - Scanner et supprimer les fichiers suspects", font=("Arial", 12))
label.pack(pady=15)

scan_button = tk.Button(root, text="📁 Choisir un dossier à scanner", command=select_directory, bg="#4CAF50", fg="white", font=("Arial", 12))
scan_button.pack(pady=5)

cancel_button = tk.Button(root, text="⛔ Annuler le scan", command=cancel_scan, bg="#f39c12", fg="white", font=("Arial", 12))
cancel_button.pack(pady=5)

delete_button = tk.Button(root, text="🗑️ Supprimer les fichiers infectés", command=delete_infected, bg="#f44336", fg="white", font=("Arial", 12))
delete_button.pack(pady=5)

status_label = tk.Label(root, text="", font=("Arial", 10), fg="blue")
status_label.pack(pady=5)

progress = ttk.Progressbar(root, orient="horizontal", length=350, mode="determinate")
progress.pack(pady=10)

root.mainloop()