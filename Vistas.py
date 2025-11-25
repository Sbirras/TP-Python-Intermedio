import tkinter as tk
from tkinter import ttk, messagebox
import Consultas as dao 

# ===============================================
# CLASE PARA EL ALTA DE AUTORES 
# ===============================================

class VentanaAutor(tk.Toplevel):
    """Ventana emergente para registrar un nuevo autor."""
    def __init__(self, master, callback_refresh_cb):
        super().__init__(master)
        self.title("Nuevo Autor")
        self.geometry("350x150")
        self.resizable(False, False)
        self.transient(master) 
        self.grab_set() 
        
        # Callback para refrescar el Combobox de la ventana principal
        self.callback_refresh_cb = callback_refresh_cb
        
        self.nombre = tk.StringVar()
        self.apellido = tk.StringVar()
        
        self._crear_widgets()
        
    def _crear_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame, textvariable=self.nombre, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Apellido:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame, textvariable=self.apellido, width=30).grid(row=1, column=1, padx=5, pady=5)

        btn_guardar = ttk.Button(frame, text="Guardar Autor", command=self._guardar_autor)
        btn_guardar.grid(row=2, column=0, columnspan=2, pady=10)
        
    def _guardar_autor(self):
        nombre = self.nombre.get().strip().title()
        apellido = self.apellido.get().strip().title()
        
        if not nombre or not apellido:
            messagebox.showwarning("Advertencia", "Debe ingresar el nombre y el apellido del autor.")
            return

        # Llamar a la función de alta en Consultas.py
        if dao.alta_autor(nombre, apellido):
            # No se muestra messagebox aquí porque ya se muestra en Consultas.py para autores
            # Pero sí llamamos al callback
            self.callback_refresh_cb() 
            self.destroy() 
            
# ===============================================
# CLASE PRINCIPAL: VistaLibros
# ===============================================

class VistaLibros(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        self.id_libro_seleccionado = None 
        
        # Mapeos Nombre->ID y ID->Nombre
        self.map_autores = {}
        self.map_generos = {}
        self.map_editoriales = {}
        self.map_id_autor_nombre = {} 
        self.map_id_genero_nombre = {} 
        self.map_id_editorial_nombre = {} 
        
        # Variables de control para Comboboxes
        self.nombres_autores = []
        self.nombres_generos = []
        self.nombres_editoriales = []

        # Variables de control de los campos
        self.titulo = tk.StringVar()
        self.anio = tk.StringVar()
        self.paginas = tk.StringVar()
        self.autor_sel = tk.StringVar()
        self.genero_sel = tk.StringVar()
        self.editorial_sel = tk.StringVar()
        self.disponible = tk.BooleanVar(value=True)

        self.cargar_datos_combobox() # Solo carga los datos y mapeos
        self.crear_widgets()
        self.actualizar_combobox_widgets() # Asigna los datos a los widgets

        self.mostrar_libros()
        self.deshabilitar_campos()

    def crear_widgets(self):
        # Frame para el formulario (Alta/Modificación)
        frame_form = ttk.LabelFrame(self, text="Alta/Modificación de Libro", padding=(20, 10))
        frame_form.pack(pady=10, padx=10, fill="x")

        # Entradas y Comboboxes
        ttk.Label(frame_form, text="Título:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_titulo = ttk.Entry(frame_form, textvariable=self.titulo, width=40)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        
        self.check_disponible = ttk.Checkbutton(frame_form, text="Disponible", variable=self.disponible, state='disabled')
        self.check_disponible.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        ttk.Label(frame_form, text="Año Publicación:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_anio = ttk.Entry(frame_form, textvariable=self.anio, width=15)
        self.entry_anio.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_form, text="N° Páginas:", font=("Arial", 10, "bold")).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_paginas = ttk.Entry(frame_form, textvariable=self.paginas, width=15)
        self.entry_paginas.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Fila del Autor (Ajuste para el botón "➕")
        ttk.Label(frame_form, text="Autor:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.combo_autor = ttk.Combobox(frame_form, textvariable=self.autor_sel, state="disabled", width=30) 
        self.combo_autor.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.btn_alta_autor = ttk.Button(frame_form, text="➕", width=3, command=self.abrir_alta_autor, state='disabled')
        self.btn_alta_autor.grid(row=2, column=2, padx=(0, 5), pady=5, sticky="w")

        # Fila de Género y Editorial
        ttk.Label(frame_form, text="Género:", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.combo_genero = ttk.Combobox(frame_form, textvariable=self.genero_sel, state="disabled", width=15) 
        self.combo_genero.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_form, text="Editorial:", font=("Arial", 10, "bold")).grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.combo_editorial = ttk.Combobox(frame_form, textvariable=self.editorial_sel, state="disabled", width=15) 
        self.combo_editorial.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        # Botones de Acción del Formulario
        self.btn_guardar = ttk.Button(frame_form, text="Guardar Libro", command=self.ejecutar_guardar, state='disabled') 
        self.btn_guardar.grid(row=4, column=0, pady=10)
        
        self.btn_nuevo = ttk.Button(frame_form, text="Nuevo Libro", command=self.habilitar_para_alta)
        self.btn_nuevo.grid(row=4, column=1, pady=10)
        
        self.btn_limpiar = ttk.Button(frame_form, text="Limpiar/Cancelar Edición", command=self.limpiar_campos)
        self.btn_limpiar.grid(row=4, column=2, pady=10, columnspan=2)

        # Frame para botones CRUD (ARRIBA de la tabla)
        frame_crud_top = ttk.Frame(self, padding=(10, 5))
        frame_crud_top.pack(pady=5, padx=10, fill="x")
        
        btn_modificar = ttk.Button(frame_crud_top, text="Cargar para Modificar", command=self.cargar_datos_para_modificar)
        btn_modificar.pack(side="left", padx=5)

        btn_eliminar = ttk.Button(frame_crud_top, text="Eliminar", command=self.ejecutar_baja)
        btn_eliminar.pack(side="left", padx=5)

        # Frame para el listado (Treeview - Tabla)
        frame_listado = ttk.Frame(self, padding=(10, 10))
        frame_listado.pack(pady=10, padx=10, fill="both", expand=True)

        # Configuración del Treeview
        columnas = ("titulo", "autor", "genero", "editorial", "anio", "paginas", "disponible")
        self.tree = ttk.Treeview(frame_listado, columns=columnas, show="headings", height=10)
        
        self.bind_treeview_headers(self.tree)
        
        self.tree.column("titulo", width=250)
        self.tree.column("autor", width=150)
        self.tree.column("genero", width=100)
        self.tree.column("editorial", width=100)
        self.tree.column("anio", width=50, anchor="center")
        self.tree.column("paginas", width=70, anchor="center")
        self.tree.column("disponible", width=50, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_listado, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)
        
    # --- FUNCIONES DE HABILITACIÓN/DESHABILITACIÓN ---

    def habilitar_campos(self):
        self.entry_titulo.config(state='normal')
        self.entry_anio.config(state='normal')
        self.entry_paginas.config(state='normal')
        self.combo_autor.config(state='readonly') 
        self.combo_genero.config(state='readonly')
        self.combo_editorial.config(state='readonly')
        self.check_disponible.config(state='normal')
        self.btn_guardar.config(state='normal')
        self.btn_nuevo.config(state='disabled')
        self.btn_alta_autor.config(state='normal') 

    def deshabilitar_campos(self):
        self.entry_titulo.config(state='disabled')
        self.entry_anio.config(state='disabled')
        self.entry_paginas.config(state='disabled')
        self.combo_autor.config(state='disabled')
        self.combo_genero.config(state='disabled')
        self.combo_editorial.config(state='disabled')
        self.check_disponible.config(state='disabled')
        self.btn_guardar.config(state='disabled')
        self.btn_nuevo.config(state='normal')
        self.btn_alta_autor.config(state='disabled') 

    def limpiar_campos_datos(self):
        self.titulo.set("")
        self.anio.set("")
        self.paginas.set("")
        self.autor_sel.set("")
        self.genero_sel.set("")
        self.editorial_sel.set("")
        self.disponible.set(True)
        self.id_libro_seleccionado = None

    def habilitar_para_alta(self):
        self.limpiar_campos_datos() 
        self.habilitar_campos()
        self.entry_titulo.focus_set()
        messagebox.showinfo("Modo Alta", "Ingrese los datos del nuevo libro y presione 'Guardar Libro'.")
            
    def limpiar_campos(self):
        self.limpiar_campos_datos()
        self.deshabilitar_campos()
        
    # --- FUNCIONALIDAD DE ORDENAMIENTO (ASC/DESC) ---

    def treeview_sort_column(self, tree, col, reverse):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        
        def sort_key(t):
            value = t[0]
            if col in ('anio', 'paginas') and str(value).isdigit():
                return int(value)
            elif col == 'disponible':
                return 0 if value == 'Sí' else 1
            return str(value).lower()

        data.sort(key=sort_key, reverse=reverse)

        for index, item in enumerate(data):
            tree.move(item[1], '', index)

        tree.heading(col, command=lambda: 
                     self.treeview_sort_column(tree, col, not reverse))

    def bind_treeview_headers(self, tree):
        for col in tree["columns"]:
            tree.heading(col, text=col.capitalize(), 
                         command=lambda c=col: self.treeview_sort_column(tree, c, False))
                         
    # --- FUNCIONES DE ALTA DE AUTOR Y RECARGA ---
    
    def cargar_datos_combobox(self):
        """Carga los datos (ID y nombre) de Autores, Géneros y Editoriales en los mapeos."""
        
        # Se limpian los mapeos antes de recargar
        self.map_autores.clear(); self.map_id_autor_nombre.clear()
        self.map_generos.clear(); self.map_id_genero_nombre.clear()
        self.map_editoriales.clear(); self.map_id_editorial_nombre.clear()
        
        # --- Carga de Autores ---
        autores = dao.obtener_autores()
        self.nombres_autores = [] 
        for id_aut, nombre_aut in autores:
            self.nombres_autores.append(nombre_aut)
            self.map_autores[nombre_aut] = id_aut
            self.map_id_autor_nombre[id_aut] = nombre_aut 
        
        # --- Carga de Géneros ---
        generos = dao.obtener_generos()
        self.nombres_generos = []
        for id_gen, nombre_gen in generos:
            self.nombres_generos.append(nombre_gen)
            self.map_generos[nombre_gen] = id_gen
            self.map_id_genero_nombre[id_gen] = nombre_gen
        
        # --- Carga de Editoriales ---
        editoriales = dao.obtener_editoriales()
        self.nombres_editoriales = []
        for id_edit, nombre_edit in editoriales:
            self.nombres_editoriales.append(nombre_edit)
            self.map_editoriales[nombre_edit] = id_edit
            self.map_id_editorial_nombre[id_edit] = nombre_edit

    def actualizar_combobox_widgets(self):
        """Asigna los valores cargados a los widgets Combobox."""
        if hasattr(self, 'combo_autor'):
             self.combo_autor['values'] = self.nombres_autores
             self.combo_genero['values'] = self.nombres_generos
             self.combo_editorial['values'] = self.nombres_editoriales

    def refrescar_comboboxes(self):
        """Recarga los datos de los comboboxes (llamada después de un alta/modificación)."""
        self.cargar_datos_combobox()
        self.actualizar_combobox_widgets()

    def abrir_alta_autor(self):
        """Abre una nueva ventana para dar de alta un autor."""
        # Pasa self.refrescar_comboboxes como callback
        VentanaAutor(self.master, self.refrescar_comboboxes)
                         
    # --- FUNCIONES CRUD LIBROS ---
    
    def mostrar_libros(self):
        if not hasattr(self, 'tree'): return
        
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        libros = dao.listar_libros()
        
        for libro in libros:
            disponible_str = "Sí" if libro[7] else "No"
            self.tree.insert('', tk.END, iid=libro[0], values=(libro[1], libro[2], libro[3], libro[4], libro[5], libro[6], disponible_str))
            
    def validar_campos(self):
        if not self.titulo.get() or not self.anio.get():
            messagebox.showerror("Error de Validación", "Los campos Título y Año son obligatorios.")
            return False
            
        try:
            int(self.anio.get())
            if self.paginas.get(): int(self.paginas.get())
        except ValueError:
             messagebox.showerror("Error de Validación", "Año y Páginas deben ser números enteros.")
             return False

        if not self.autor_sel.get() or not self.genero_sel.get() or not self.editorial_sel.get():
            messagebox.showerror("Error de Validación", "Debe seleccionar Autor, Género y Editorial.")
            return False
            
        return True

    def ejecutar_guardar(self):
        if not self.validar_campos(): return
            
        fk_autor = self.map_autores[self.autor_sel.get()]
        fk_genero = self.map_generos[self.genero_sel.get()]
        fk_editorial = self.map_editoriales[self.editorial_sel.get()]
        
        datos_comunes = (
            self.titulo.get(), 
            int(self.anio.get()), 
            int(self.paginas.get() if self.paginas.get() else 0), 
            1 if self.disponible.get() else 0,
            fk_autor, 
            fk_genero, 
            fk_editorial
        )

        exito = False
        if self.id_libro_seleccionado is None:
            exito = dao.alta_libro(*datos_comunes)
        else:
            exito = dao.actualizar_libro(self.id_libro_seleccionado, *datos_comunes)

        if exito:
            self.limpiar_campos()
            self.mostrar_libros()
            
    def seleccionar_registro(self, event):
        try:
            item_seleccionado = self.tree.selection()[0] 
            self.id_libro_seleccionado = item_seleccionado 
        except IndexError:
            self.id_libro_seleccionado = None


    def cargar_datos_para_modificar(self):
        id_libro_a_cargar = None
        
        try:
            item_seleccionado = self.tree.selection()[0]
            id_libro_a_cargar = item_seleccionado 
        except IndexError:
            id_libro_a_cargar = self.id_libro_seleccionado

        if id_libro_a_cargar is None:
            messagebox.showwarning("Advertencia", "Debe seleccionar un libro de la tabla con un clic para modificar.")
            return

        self.habilitar_campos()
        self.id_libro_seleccionado = id_libro_a_cargar 
        
        libro = dao.buscar_libro_por_id(self.id_libro_seleccionado)
        
        if libro:
            try:
                autor_nombre = self.map_id_autor_nombre.get(libro[4])
                genero_nombre = self.map_id_genero_nombre.get(libro[5])
                editorial_nombre = self.map_id_editorial_nombre.get(libro[6])
                
                if not autor_nombre or not genero_nombre or not editorial_nombre:
                     raise KeyError(f"Claves foráneas no válidas en DB.")

                self.titulo.set(libro[0])
                self.anio.set(str(libro[1]))
                self.paginas.set(str(libro[2]))
                self.disponible.set(True if libro[3] == 1 else False)
                
                self.autor_sel.set(autor_nombre)
                self.genero_sel.set(genero_nombre)
                self.editorial_sel.set(editorial_nombre)
                
                self.entry_titulo.focus_set()
                messagebox.showinfo("Modificación", f"Cargados datos. Modifique y pulse 'Guardar Libro'.")
            except KeyError as e:
                messagebox.showerror("Error de Mapeo", f"El libro tiene una clave foránea inválida. Error: {e}")
                self.limpiar_campos()
                
        else:
            messagebox.showerror("Error", "No se encontró el libro en la base de datos o el ID es inválido.")
            self.limpiar_campos()

    def ejecutar_baja(self):
        id_libro_a_eliminar = None
        
        try:
            item_seleccionado = self.tree.selection()[0]
            id_libro_a_eliminar = item_seleccionado
        except IndexError:
            id_libro_a_eliminar = self.id_libro_seleccionado

        if id_libro_a_eliminar is None:
            messagebox.showwarning("Advertencia", "Debe seleccionar un libro de la tabla con un clic para eliminar.")
            return
            
        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar el libro con ID {id_libro_a_eliminar}?"):
            if dao.baja_libro(id_libro_a_eliminar):
                self.limpiar_campos()

                self.mostrar_libros()
