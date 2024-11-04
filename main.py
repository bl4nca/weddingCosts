import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Crear la base de datos y agregar campo de categoría
conn = sqlite3.connect('gastos_boda.db')
cursor = conn.cursor()

# Crear tabla con la columna de categoría si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS gastos (
                    id INTEGER PRIMARY KEY,
                    monto REAL,
                    pagador TEXT,
                    motivo TEXT,
                    categoria TEXT
                 )''')
conn.commit()


# Función para agregar un gasto
def agregar_gasto():
    try:
        monto = float(entry_monto.get())
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa un monto válido.")
        return

    pagador = pagador_var.get()
    motivo = entry_motivo.get()
    categoria = categoria_var.get()

    if not monto or not pagador or not motivo or not categoria:
        messagebox.showwarning("Datos incompletos", "Por favor completa todos los campos.")
        return

    cursor.execute("INSERT INTO gastos (monto, pagador, motivo, categoria) VALUES (?, ?, ?, ?)",
                   (monto, pagador, motivo, categoria))
    conn.commit()
    messagebox.showinfo("Éxito", "Gasto agregado exitosamente.")
    actualizar_lista()
    entry_monto.delete(0, tk.END)
    entry_motivo.delete(0, tk.END)


# Función para actualizar la lista de gastos con los filtros aplicados
def actualizar_lista():
    for row in tree.get_children():
        tree.delete(row)

    query = "SELECT * FROM gastos WHERE 1=1"
    params = []

    # Filtrar por pagador si se selecciona uno específico
    if filtro_pagador_var.get() != "Todos":
        query += " AND pagador = ?"
        params.append(filtro_pagador_var.get())

    # Filtrar por categoría si se selecciona una específica
    if filtro_categoria_var.get() != "Todas":
        query += " AND categoria = ?"
        params.append(filtro_categoria_var.get())

    cursor.execute(query, params)
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

    # Actualizar el total
    cursor.execute("SELECT SUM(monto) FROM gastos WHERE 1=1 " +
                   (" AND pagador = ?" if filtro_pagador_var.get() != "Todos" else "") +
                   (" AND categoria = ?" if filtro_categoria_var.get() != "Todas" else ""), params)
    total = cursor.fetchone()[0]
    total_var.set(f"Total Gastado: ${total:.2f}" if total else "Total Gastado: $0.00")


# Configuración de la interfaz
root = tk.Tk()
root.title("Organizador de Gastos de Boda")

# Crear un Frame para agrupar los campos de entrada y reducir el espacio entre ellos
frame_inputs = tk.Frame(root)
frame_inputs.grid(row=0, column=0, columnspan=2, pady=10)

# Campo para el monto
tk.Label(frame_inputs, text="Monto:").grid(row=0, column=0, sticky="e")
entry_monto = tk.Entry(frame_inputs, width=20)
entry_monto.grid(row=0, column=1, padx=5)

# Campo para el pagador
tk.Label(frame_inputs, text="Pagador:").grid(row=1, column=0, sticky="e")
pagador_var = tk.StringVar()
pagador_menu = ttk.Combobox(frame_inputs, textvariable=pagador_var, values=["Blanca", "Antonio"], width=18)
pagador_menu.grid(row=1, column=1, padx=5)

# Campo para el motivo
tk.Label(frame_inputs, text="Motivo:").grid(row=2, column=0, sticky="e")
entry_motivo = tk.Entry(frame_inputs, width=20)
entry_motivo.grid(row=2, column=1, padx=5)

# Campo para la categoría
tk.Label(frame_inputs, text="Categoría:").grid(row=3, column=0, sticky="e")
categoria_var = tk.StringVar()
categoria_menu = ttk.Combobox(frame_inputs, textvariable=categoria_var,
                              values=["Catedral", "Local", "Catering", "Extra"], width=18)
categoria_menu.grid(row=3, column=1, padx=5)

# Botón para agregar el gasto
btn_agregar = tk.Button(root, text="Agregar Gasto", command=agregar_gasto)
btn_agregar.grid(row=1, columnspan=2, pady=10)

# Filtros
frame_filters = tk.Frame(root)
frame_filters.grid(row=2, column=0, columnspan=2, pady=10)

tk.Label(frame_filters, text="Filtrar por Pagador:").grid(row=0, column=0, sticky="e")
filtro_pagador_var = tk.StringVar(value="Todos")
filtro_pagador_menu = ttk.Combobox(frame_filters, textvariable=filtro_pagador_var,
                                   values=["Todos", "Blanca", "Antonio"], width=18)
filtro_pagador_menu.grid(row=0, column=1, padx=5)

tk.Label(frame_filters, text="Filtrar por Categoría:").grid(row=1, column=0, sticky="e")
filtro_categoria_var = tk.StringVar(value="Todas")
filtro_categoria_menu = ttk.Combobox(frame_filters, textvariable=filtro_categoria_var,
                                     values=["Todas", "Catedral", "Local", "Catering", "Extra"], width=18)
filtro_categoria_menu.grid(row=1, column=1, padx=5)

# Botón para aplicar los filtros
btn_filtrar = tk.Button(root, text="Aplicar Filtros", command=actualizar_lista)
btn_filtrar.grid(row=3, columnspan=2, pady=10)

# Lista de gastos
tree = ttk.Treeview(root, columns=("ID", "Monto", "Pagador", "Motivo", "Categoria"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Monto", text="Monto")
tree.heading("Pagador", text="Pagador")
tree.heading("Motivo", text="Motivo")
tree.heading("Categoria", text="Categoría")
tree.grid(row=4, column=0, columnspan=2, pady=10)

# Total de gastos
total_var = tk.StringVar(value="Total Gastado: $0.00")
lbl_total = tk.Label(root, textvariable=total_var, font=("Arial", 14, "bold"))
lbl_total.grid(row=5, columnspan=2, pady=10)

# Actualizar la lista de gastos al inicio
actualizar_lista()

# Ejecutar la aplicación
root.mainloop()

# Cerrar la conexión a la base de datos al salir
conn.close()