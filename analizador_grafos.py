import tkinter as tk
from tkinter import messagebox
from collections import deque

RADIO_NODO = 20
COLOR_NODO = "#4A90D9"      
COLOR_NODO_SELECCIONADO = "#F5A623"  
COLOR_BORDE = "#2C3E50"
COLOR_ARISTA = "#2C3E50"
COLOR_TEXTO = "white"


class Nodo:
    def __init__(self, id_nodo, etiqueta, x, y):
        self.id = id_nodo
        self.etiqueta = etiqueta   
        self.x = x                 
        self.y = y
        self.circulo_id = None
        self.texto_id = None


class GrafoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Grafos - Proyecto Final MC2N")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        self.nodos = {}
        self.lista_adyacencia = {}
        self.aristas = []
        self.contador_nodos = 0
        self.nodo_seleccionado = None
        self._construir_interfaz()
    def _construir_interfaz(self):
        frame_info = tk.Frame(self.root, bg="#ECF0F1", pady=6)
        frame_info.pack(side=tk.TOP, fill=tk.X)

        texto_ayuda = (
            "Clic en área vacía: crear nodo   |   "
            "Clic en un nodo y luego en otro: crear arista   |   "
            "Clic en un nodo ya seleccionado: cancelar selección"
        )
        tk.Label(
            frame_info, text=texto_ayuda, bg="#ECF0F1",
            font=("Segoe UI", 9), fg="#2C3E50"
        ).pack()

        self.canvas = tk.Canvas(
            self.root, bg="white", highlightthickness=1,
            highlightbackground="#BDC3C7"
        )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.canvas.bind("<Button-1>", self.on_click_canvas)

        frame_botones = tk.Frame(self.root, pady=10)
        frame_botones.pack(side=tk.BOTTOM, fill=tk.X)

        btn_limpiar = tk.Button(
            frame_botones, text="Limpiar Canvas", command=self.limpiar_canvas,
            bg="#E74C3C", fg="white", font=("Segoe UI", 10, "bold"),
            padx=12, pady=4, relief=tk.FLAT
        )
        btn_limpiar.pack(side=tk.LEFT, padx=15)

        btn_validar = tk.Button(
            frame_botones, text="Validar Conexión", command=self.validar_conexion,
            bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"),
            padx=12, pady=4, relief=tk.FLAT
        )
        btn_validar.pack(side=tk.LEFT, padx=15)

        btn_hamiltoniano = tk.Button(
            frame_botones, text="Buscar Ciclo Hamiltoniano",
            command=self.buscar_ciclo_hamiltoniano,
            bg="#8E44AD", fg="white", font=("Segoe UI", 10, "bold"),
            padx=12, pady=4, relief=tk.FLAT
        )
        btn_hamiltoniano.pack(side=tk.LEFT, padx=15)

        self.label_estado = tk.Label(
            frame_botones, text="Nodos: 0   |   Aristas: 0",
            font=("Segoe UI", 10), fg="#2C3E50"
        )
        self.label_estado.pack(side=tk.RIGHT, padx=20)

    def on_click_canvas(self, event):
        nodo_clicado = self._obtener_nodo_en_posicion(event.x, event.y)

        if nodo_clicado is not None:
            self._manejar_clic_en_nodo(nodo_clicado)
        else:
            self._crear_nodo(event.x, event.y)

    def _obtener_nodo_en_posicion(self, x, y):
        for nodo in self.nodos.values():
            distancia = ((x - nodo.x) ** 2 + (y - nodo.y) ** 2) ** 0.5
            if distancia <= RADIO_NODO:
                return nodo
        return None

    def _manejar_clic_en_nodo(self, nodo):
        if self.nodo_seleccionado is None:
            self.nodo_seleccionado = nodo
            self._resaltar_nodo(nodo, True)
        elif self.nodo_seleccionado.id == nodo.id:
            self._resaltar_nodo(nodo, False)
            self.nodo_seleccionado = None
        else:
            self._crear_arista(self.nodo_seleccionado, nodo)
            self._resaltar_nodo(self.nodo_seleccionado, False)
            self.nodo_seleccionado = None

    def _resaltar_nodo(self, nodo, seleccionado):
        color = COLOR_NODO_SELECCIONADO if seleccionado else COLOR_NODO
        self.canvas.itemconfig(nodo.circulo_id, fill=color)
    def _crear_nodo(self, x, y):
        self.contador_nodos += 1
        id_nodo = self.contador_nodos
        etiqueta = f"V{id_nodo}"

        nodo = Nodo(id_nodo, etiqueta, x, y)

        nodo.circulo_id = self.canvas.create_oval(
            x - RADIO_NODO, y - RADIO_NODO,
            x + RADIO_NODO, y + RADIO_NODO,
            fill=COLOR_NODO, outline=COLOR_BORDE, width=2
        )
        nodo.texto_id = self.canvas.create_text(
            x, y, text=etiqueta, fill=COLOR_TEXTO,
            font=("Segoe UI", 10, "bold")
        )

        self.nodos[id_nodo] = nodo
        self.lista_adyacencia[id_nodo] = set()

        self._actualizar_estado()

    def _crear_arista(self, nodo_a, nodo_b):
        if nodo_b.id in self.lista_adyacencia[nodo_a.id]:
            messagebox.showinfo(
                "Arista existente",
                f"Ya existe una conexión entre {nodo_a.etiqueta} y {nodo_b.etiqueta}."
            )
            return

        linea_id = self.canvas.create_line(
            nodo_a.x, nodo_a.y, nodo_b.x, nodo_b.y,
            fill=COLOR_ARISTA, width=2
        )
        self.canvas.tag_lower(linea_id)

        self.lista_adyacencia[nodo_a.id].add(nodo_b.id)
        self.lista_adyacencia[nodo_b.id].add(nodo_a.id)

        self.aristas.append((nodo_a.id, nodo_b.id))
        self._actualizar_estado()

    def _actualizar_estado(self):
        self.label_estado.config(
            text=f"Nodos: {len(self.nodos)}   |   Aristas: {len(self.aristas)}"
        )

    def limpiar_canvas(self):
        self.canvas.delete("all")
        self.nodos.clear()
        self.lista_adyacencia.clear()
        self.aristas.clear()
        self.contador_nodos = 0
        self.nodo_seleccionado = None
        self._actualizar_estado()

    def es_conexo(self):
        if len(self.nodos) <= 1:
            return True
        nodo_inicio = next(iter(self.nodos))

        visitados = set()
        cola = deque([nodo_inicio])
        visitados.add(nodo_inicio)

        while cola:
            actual = cola.popleft()
            for vecino in self.lista_adyacencia.get(actual, []):
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)

        return len(visitados) == len(self.nodos)

    def validar_conexion(self):
        if len(self.nodos) == 0:
            messagebox.showwarning(
                "Grafo vacío",
                "No hay nodos en el canvas. Agrega al menos un nodo."
            )
            return

        if self.es_conexo():
            messagebox.showinfo("Resultado", "El grafo es CONEXO.")
        else:
            messagebox.showwarning("Resultado", "El grafo NO es conexo.")

    def _buscar_ciclo_hamiltoniano_backtracking(self, ids_nodos):
        n = len(ids_nodos)
        nodo_inicio = ids_nodos[0]

        camino = [nodo_inicio]
        visitados = {nodo_inicio}

        def backtrack():
            if len(camino) == n:
                ultimo = camino[-1]
                if nodo_inicio in self.lista_adyacencia.get(ultimo, set()):
                    return True
                return False

            ultimo = camino[-1]
            for vecino in self.lista_adyacencia.get(ultimo, set()):
                if vecino not in visitados:
                    camino.append(vecino)
                    visitados.add(vecino)

                    if backtrack():
                        return True
                    camino.pop()
                    visitados.remove(vecino)
            return False
        if backtrack():
            return camino + [nodo_inicio]
        return None

    def buscar_ciclo_hamiltoniano(self):
        if len(self.nodos) == 0:
            messagebox.showwarning(
                "Grafo vacío",
                "No hay nodos en el canvas. Agrega al menos un nodo."
            )
            return
        if not self.es_conexo():
            messagebox.showerror(
                "Grafo no conexo",
                "El grafo debe ser conexo para poder buscar un Ciclo Hamiltoniano.\n"
                "Conecta todos los nodos y vuelve a intentarlo."
            )
            return
        if len(self.nodos) < 3:
            messagebox.showwarning(
                "Nodos insuficientes",
                "Se necesitan al menos 3 nodos para formar un Ciclo Hamiltoniano."
            )
            return

        ids_nodos = list(self.nodos.keys())
        resultado = self._buscar_ciclo_hamiltoniano_backtracking(ids_nodos)

        if resultado is not None:
            etiquetas = [self.nodos[id_nodo].etiqueta for id_nodo in resultado]
            secuencia_texto = " -> ".join(etiquetas)
            messagebox.showinfo(
                "Ciclo Hamiltoniano encontrado",
                f"Se encontró un Ciclo Hamiltoniano:\n\n{secuencia_texto}"
            )
        else:
            messagebox.showwarning(
                "Sin Ciclo Hamiltoniano",
                "El grafo NO posee un Ciclo Hamiltoniano."
            )

def main():
    root = tk.Tk()
    app = GrafoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
