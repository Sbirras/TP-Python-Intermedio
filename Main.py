import tkinter as tk
from Vistas import VistaLibros

def main():
    ventana = tk.Tk()
    ventana.title('Gestión de Libros')
    
    try:
        icono = tk.PhotoImage(file='icono.png')
        ventana.iconphoto(False, icono)
    except tk.TclError:
        print("Advertencia: No se pudo cargar el archivo 'icono.png'.")

    ventana.geometry("1000x600") 
    ventana.resizable(False, False) 
    
    VistaLibros(ventana)

    ventana.mainloop()

if __name__ == '__main__':

    main()
