import sqlite3 as db
from tkinter import messagebox

NOMBRE_DB = "biblioteca.db"

# --- Funciones de Conexión y Setup ---

def conectar():
    """Establece la conexión a la base de datos."""
    try:
        conn = db.connect(NOMBRE_DB)
        return conn
    except db.Error as e:
        messagebox.showerror("Error de DB", f"No se pudo conectar a la base de datos: {e}")
        return None

def crear_tablas():
    """Crea las cuatro tablas de la base de datos (si no existen)."""
    conn = conectar()
    if conn is None: return
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Autores (
            id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Generos (
            id_genero INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Editoriales (
            id_editorial INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            pais TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Libros (
            id_libro INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            anio_publicacion INTEGER,
            paginas INTEGER,
            disponible BOOLEAN,
            fk_autor INTEGER,
            fk_genero INTEGER,
            fk_editorial INTEGER,
            FOREIGN KEY (fk_autor) REFERENCES Autores(id_autor),
            FOREIGN KEY (fk_genero) REFERENCES Generos(id_genero),
            FOREIGN KEY (fk_editorial) REFERENCES Editoriales(id_editorial)
        )
    """)
    
    conn.commit()
    conn.close()

def insertar_datos_iniciales():
    """Inserta datos de prueba en las tablas auxiliares."""
    conn = conectar()
    if conn is None: return
    cursor = conn.cursor()

    if cursor.execute("SELECT COUNT(*) FROM Autores").fetchone()[0] == 0:
        autores = [("Gabriel", "García Márquez"), ("Isabel", "Allende"), ("Jorge Luis", "Borges")]
        cursor.executemany("INSERT INTO Autores (nombre, apellido) VALUES (?, ?)", autores)

    if cursor.execute("SELECT COUNT(*) FROM Generos").fetchone()[0] == 0:
        generos = [("Ficción",), ("Ciencia Ficción",), ("Novela Histórica",)]
        cursor.executemany("INSERT INTO Generos (nombre) VALUES (?)", generos)

    if cursor.execute("SELECT COUNT(*) FROM Editoriales").fetchone()[0] == 0:
        editoriales = [("Editorial Sudamericana", "Argentina"), ("Planeta", "España"), ("Penguin Random House", "USA")]
        cursor.executemany("INSERT INTO Editoriales (nombre, pais) VALUES (?, ?)", editoriales)

    conn.commit()
    conn.close()
    
# Inicialización de la DB
crear_tablas()
insertar_datos_iniciales()
    
# --- FUNCIÓN: ALTA DE AUTOR ---

def alta_autor(nombre, apellido):
    """Inserta un nuevo autor (CREATE)."""
    conn = conectar()
    if conn is None: return False
        
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Autores (nombre, apellido)
            VALUES (?, ?)
            """,
            (nombre, apellido)
        )
        conn.commit()
        conn.close()
        return True
    except db.Error as e:
        messagebox.showerror("Error", f"Fallo al dar de alta el autor: {e}")
        conn.close()
        return False
        
# --- Funciones de LECTURA (Comboboxes y Listado) ---

def obtener_autores():
    conn = conectar()
    if conn is None: return []
    cursor = conn.cursor()
    # Concatena nombre y apellido
    cursor.execute("SELECT id_autor, nombre || ' ' || apellido FROM Autores ORDER BY nombre, apellido") 
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_generos():
    conn = conectar()
    if conn is None: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_genero, nombre FROM Generos ORDER BY nombre")
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_editoriales():
    conn = conectar()
    if conn is None: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_editorial, nombre FROM Editoriales ORDER BY nombre")
    datos = cursor.fetchall()
    conn.close()
    return datos

def listar_libros():
    """Retorna todos los libros con sus datos completos usando JOINs."""
    conn = conectar()
    if conn is None: return []
        
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            L.id_libro, L.titulo, A.nombre || ' ' || A.apellido AS Autor, 
            G.nombre AS Genero, E.nombre AS Editorial,
            L.anio_publicacion, L.paginas, L.disponible
        FROM Libros L
        JOIN Autores A ON L.fk_autor = A.id_autor
        JOIN Generos G ON L.fk_genero = G.id_genero
        JOIN Editoriales E ON L.fk_editorial = E.id_editorial
        ORDER BY L.titulo ASC
    """)
    datos = cursor.fetchall()
    conn.close()
    return datos
    
# --- Funciones CRUD para LIBROS ---

def alta_libro(titulo, anio, paginas, disponible, fk_autor, fk_genero, fk_editorial):
    """Inserta un nuevo libro (CREATE)."""
    conn = conectar()
    if conn is None: return False
        
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Libros (titulo, anio_publicacion, paginas, disponible, fk_autor, fk_genero, fk_editorial)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (titulo, anio, paginas, disponible, fk_autor, fk_genero, fk_editorial)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Libro dado de alta correctamente.")
        return True
    except db.Error as e:
        messagebox.showerror("Error", f"Fallo al dar de alta el libro: {e}")
        conn.close()
        return False

def buscar_libro_por_id(id_libro):
    """Busca y retorna todos los datos de un libro (READ for Update)."""
    conn = conectar()
    if conn is None: return None

    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            titulo, anio_publicacion, paginas, disponible, fk_autor, fk_genero, fk_editorial 
        FROM Libros WHERE id_libro = ?
    """, (id_libro,))
    datos = cursor.fetchone()
    conn.close()
    return datos

def actualizar_libro(id_libro, titulo, anio, paginas, disponible, fk_autor, fk_genero, fk_editorial):
    """Modifica un libro existente (UPDATE)."""
    conn = conectar()
    if conn is None: return False
        
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Libros SET 
                titulo = ?, anio_publicacion = ?, paginas = ?, disponible = ?, 
                fk_autor = ?, fk_genero = ?, fk_editorial = ?
            WHERE id_libro = ?
            """,
            (titulo, anio, paginas, disponible, fk_autor, fk_genero, fk_editorial, id_libro)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Libro modificado correctamente.")
        return True
    except db.Error as e:
        messagebox.showerror("Error", f"Fallo al modificar el libro: {e}")
        conn.close()
        return False
        
def baja_libro(id_libro):
    """Elimina un libro de la DB (DELETE)."""
    conn = conectar()
    if conn is None: return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Libros WHERE id_libro = ?", (id_libro,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", f"Libro con ID {id_libro} eliminado.")
        return True
    except db.Error as e:
        messagebox.showerror("Error", f"Fallo al eliminar el libro: {e}")
        conn.close()
        return False