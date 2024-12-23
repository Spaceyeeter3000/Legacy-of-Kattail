import os
import tkinter as tk
from tkinter import ttk, messagebox

def parse_vanilla_regions(folder):
    vanilla_regions = []
    for file_name in os.listdir(folder):
        if file_name.endswith(".txt"):
            name = "-".join(file_name.split("-")[1:]).replace(".txt", "").strip()
            vanilla_regions.append((file_name, name))
    vanilla_regions.sort(key=lambda x: x[1])
    return vanilla_regions

def find_modded_region(folder, modded_id):
    for file_name in os.listdir(folder):
        if file_name.endswith(".txt"):
            with open(os.path.join(folder, file_name), 'r') as f:
                for line in f:
                    if line.strip().startswith(f"id={modded_id}"):
                        return file_name
    return None

def get_weather_block(file_path):
    weather_block = []
    in_weather_block = False
    bracket_count = 0
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip().startswith("weather={"):
                in_weather_block = True
                bracket_count += 1
            if in_weather_block:
                weather_block.append(line)
                bracket_count += line.count("{") - line.count("}")
            if in_weather_block and bracket_count == 0:
                break
    if weather_block:
        weather_block.append("}\n")  # Ensure proper closing bracket
    return weather_block

def replace_weather_block(file_path, weather_block):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    with open(file_path, 'w') as f:
        in_weather_block = False
        bracket_count = 0
        for line in lines:
            if line.strip().startswith("weather={"):
                in_weather_block = True
                bracket_count += 1
                f.writelines(weather_block)
                continue
            if in_weather_block:
                bracket_count += line.count("{") - line.count("}")
                if bracket_count == 0:
                    in_weather_block = False
                    continue
            if not in_weather_block:
                f.write(line)

def confirm_action(vanilla_regions, modded_folder, vanilla_folder, vanilla_choice, modded_id):
    vanilla_file = vanilla_regions[vanilla_choice][0]
    modded_file = find_modded_region(modded_folder, modded_id)

    if not modded_file:
        messagebox.showerror("Error", f"No modded region found with ID {modded_id}.")
        return

    vanilla_path = os.path.join(vanilla_folder, vanilla_file)
    modded_path = os.path.join(modded_folder, modded_file)

    weather_block = get_weather_block(vanilla_path)

    if not weather_block:
        messagebox.showerror("Error", f"No weather block found in {vanilla_file}.")
        return

    replace_weather_block(modded_path, weather_block)

    messagebox.showinfo("Success", f"Weather data copied from {vanilla_file} to {modded_file}.")

def main():
    script_folder = os.getcwd()
    vanilla_folder = os.path.join(script_folder, "stratres_weather_script")
    modded_folder = script_folder

    vanilla_regions = parse_vanilla_regions(vanilla_folder)

    if not vanilla_regions:
        messagebox.showerror("Error", "No vanilla regions found in the stratres_weather_script folder.")
        return

    root = tk.Tk()
    root.title("HOI4 Weather Copier")

    tk.Label(root, text="Vanilla Strategic Region to Copy Weather From:").grid(row=0, column=0, padx=10, pady=5, sticky="w")

    vanilla_choice = tk.StringVar()
    vanilla_combo = ttk.Combobox(root, textvariable=vanilla_choice, state="readonly")
    vanilla_combo['values'] = [region[1] for region in vanilla_regions]
    vanilla_combo.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Modded Strategic Region ID to Copy Weather To:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

    modded_id_entry = tk.Entry(root)
    modded_id_entry.grid(row=1, column=1, padx=10, pady=5)

    def on_confirm():
        vanilla_index = vanilla_combo.current()
        if vanilla_index == -1:
            messagebox.showerror("Error", "Please select a vanilla strategic region.")
            return

        modded_id = modded_id_entry.get().strip()
        if not modded_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric ID for the modded region.")
            return

        confirm_action(vanilla_regions, modded_folder, vanilla_folder, vanilla_index, modded_id)

    confirm_button = tk.Button(root, text="Confirm", command=on_confirm)
    confirm_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
