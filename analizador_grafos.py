import tkinter as tk
from tkinter import messagebox
from collections import deque

RADIO_NODO = 20
MARGEN_NODO = 4
COLOR_FONDO_VENTANA = "#F4F6F7"
COLOR_FONDO_CANVAS = "white"
COLOR_NODO = "#4A90D9"
COLOR_NODO_SELECCIONADO = "#F5A623"
COLOR_BORDE_NODO = "#2C3E50"
COLOR_TEXTO_NODO = "white"
COLOR_ARISTA_NORMAL = "#5D6D7E"
ANCHO_ARISTA_NORMAL = 2
COLOR_ARISTA_SELECCIONADA = "#E67E22"
ANCHO_ARISTA_SELECCIONADA = 3
COLOR_CICLO = "#00C853"
ANCHO_CICLO = 4
UMBRAL_CLIC_ARISTA = 6                
UMBRAL_ARRASTRE = 3                   

FUENTE_TITULO = ("Segoe UI", 10, "bold")
FUENTE_NORMAL = ("Segoe UI", 9)
FUENTE_NODO = ("Segoe UI", 10, "bold")

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
        self.root.geometry("960x700")
        self.root.minsize(760, 560)
        self.root.configure(bg=COLOR_FONDO_VENTANA)
        self.root.resizable(True, True)

        self.nodos = {}                 
        self.lista_adyacencia = {}      
        self.aristas_canvas = {}
        self.contador_nodos = 0

        self.nodo_seleccionado = None       
        self.arista_seleccionada = None     
        self.aristas_ciclo_resaltadas = set()  
        self.arrastre = None                

        self._construir_interfaz()
    def _construir_interfaz(self):
        frame_info = tk.Frame(self.root, bg="#ECF0F1", pady=8, padx=10)
        frame_info.pack(side=tk.TOP, fill=tk.X)

        texto_ayuda = (
            "Clic en área vacía: crear nodo   |   Clic en un nodo y luego en otro: crear arista   |   "
            "Arrastrar un nodo: moverlo   |   Clic en nodo o arista + tecla Supr/Backspace: eliminar  :)"
        )
        tk.Label(
            frame_info, text=texto_ayuda, bg="#ECF0F1",
            font=FUENTE_NORMAL, fg="#2C3E50", wraplength=920, justify=tk.LEFT
        ).pack()

        frame_canvas = tk.Frame(self.root, bg=COLOR_FONDO_VENTANA, padx=10, pady=6)
        frame_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            frame_canvas, bg=COLOR_FONDO_CANVAS, highlightthickness=1,
            highlightbackground="#BDC3C7"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)

        frame_botones = tk.Frame(self.root, bg=COLOR_FONDO_VENTANA, pady=8, padx=10)
        frame_botones.pack(side=tk.TOP, fill=tk.X)

        btn_limpiar = tk.Button(
            frame_botones, text="Limpiar Canvas", command=self.limpiar_canvas,
            bg="#E74C3C", fg="white", font=FUENTE_TITULO,
            padx=12, pady=4, relief=tk.FLAT, activebackground="#C0392B", cursor="hand2"
        )
        btn_limpiar.pack(side=tk.LEFT, padx=6)

        btn_validar = tk.Button(
            frame_botones, text="Validar Conexión", command=self.validar_conexion,
            bg="#27AE60", fg="white", font=FUENTE_TITULO,
            padx=12, pady=4, relief=tk.FLAT, activebackground="#1E8449", cursor="hand2"
        )
        btn_validar.pack(side=tk.LEFT, padx=6)

        btn_hamiltoniano = tk.Button(
            frame_botones, text="Buscar Ciclo Hamiltoniano",
            command=self.buscar_ciclo_hamiltoniano,
            bg="#8E44AD", fg="white", font=FUENTE_TITULO,
            padx=12, pady=4, relief=tk.FLAT, activebackground="#6C3483", cursor="hand2"
        )
        btn_hamiltoniano.pack(side=tk.LEFT, padx=6)

        btn_restablecer = tk.Button(
            frame_botones, text="Restablecer Colores",
            command=self.restablecer_colores,
            bg="#5D6D7E", fg="white", font=FUENTE_TITULO,
            padx=12, pady=4, relief=tk.FLAT, activebackground="#34495E", cursor="hand2"
        )
        btn_restablecer.pack(side=tk.LEFT, padx=6)

        self.label_estado = tk.Label(
            frame_botones, text="Nodos: 0   |   Aristas: 0",
            font=FUENTE_NORMAL, fg="#2C3E50", bg=COLOR_FONDO_VENTANA
        )
        self.label_estado.pack(side=tk.RIGHT, padx=10)

        frame_ciclo = tk.Frame(self.root, bg="#EAF2F8", padx=10, pady=8)
        frame_ciclo.pack(side=tk.BOTTOM, fill=tk.X)

        self.label_ciclo = tk.Label(
            frame_ciclo, text="Ciclo Hamiltoniano: (aún no calculado)",
            font=FUENTE_TITULO, fg="#154360", bg="#EAF2F8",
            wraplength=920, justify=tk.LEFT, anchor="w"
        )
        self.label_ciclo.pack(fill=tk.X)

        self.root.bind_all("<Delete>", self._eliminar_seleccion)
        self.root.bind_all("<BackSpace>", self._eliminar_seleccion)

    def _on_mouse_down(self, event):
        nodo = self._obtener_nodo_en_posicion(event.x, event.y)
        self.arrastre = {"nodo": nodo, "x0": event.x, "y0": event.y, "movido": False}

    def _on_mouse_drag(self, event):
        if self.arrastre is None or self.arrastre["nodo"] is None:
            return

        dx = event.x - self.arrastre["x0"]
        dy = event.y - self.arrastre["y0"]
        if not self.arrastre["movido"] and (dx * dx + dy * dy) ** 0.5 >= UMBRAL_ARRASTRE:
            self.arrastre["movido"] = True

        if self.arrastre["movido"]:
            self._mover_nodo(self.arrastre["nodo"], event.x, event.y)

    def _on_mouse_up(self, event):
        info = self.arrastre
        self.arrastre = None
        if info is None:
            return

        nodo = info["nodo"]
        if nodo is not None:
            if not info["movido"]:
                self._manejar_clic_en_nodo(nodo)
            return

        clave_arista = self._obtener_arista_en_posicion(event.x, event.y)
        if clave_arista is not None:
            self._seleccionar_arista(clave_arista)
        else:
            self._crear_nodo(event.x, event.y)

    def _obtener_nodo_en_posicion(self, x, y):
        for nodo in self.nodos.values():
            distancia = ((x - nodo.x) ** 2 + (y - nodo.y) ** 2) ** 0.5
            if distancia <= RADIO_NODO:
                return nodo
        return None

    def _obtener_arista_en_posicion(self, x, y):
        mejor_clave = None
        mejor_distancia = UMBRAL_CLIC_ARISTA
        for clave, _line_id in self.aristas_canvas.items():
            id_a, id_b = tuple(clave)
            nodo_a = self.nodos.get(id_a)
            nodo_b = self.nodos.get(id_b)
            if nodo_a is None or nodo_b is None:
                continue
            distancia = self._distancia_punto_segmento(
                x, y, nodo_a.x, nodo_a.y, nodo_b.x, nodo_b.y
            )
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_clave = clave
        return mejor_clave

    @staticmethod
    def _distancia_punto_segmento(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        proy_x, proy_y = x1 + t * dx, y1 + t * dy
        return ((px - proy_x) ** 2 + (py - proy_y) ** 2) ** 0.5

    def _manejar_clic_en_nodo(self, nodo):
        self._deseleccionar_arista()

        if self.nodo_seleccionado is None:
            self.nodo_seleccionado = nodo
            self._resaltar_nodo(nodo, True)
        elif self.nodo_seleccionado.id == nodo.id:
            self._resaltar_nodo(nodo, False)
            self.nodo_seleccionado = None
        else:
            nodo_previo = self.nodo_seleccionado
            self._crear_arista(nodo_previo, nodo)
            self._resaltar_nodo(nodo_previo, False)
            self.nodo_seleccionado = None

    def _resaltar_nodo(self, nodo, seleccionado):
        color = COLOR_NODO_SELECCIONADO if seleccionado else COLOR_NODO
        self.canvas.itemconfig(nodo.circulo_id, fill=color)

    def _seleccionar_arista(self, clave):
        if self.nodo_seleccionado is not None:
            self._resaltar_nodo(self.nodo_seleccionado, False)
            self.nodo_seleccionado = None

        anterior = self.arista_seleccionada
        self.arista_seleccionada = None if anterior == clave else clave

        if anterior is not None:
            self._refrescar_estilo_arista(anterior)
        if self.arista_seleccionada is not None:
            self._refrescar_estilo_arista(self.arista_seleccionada)

    def _deseleccionar_arista(self):
        if self.arista_seleccionada is not None:
            clave = self.arista_seleccionada
            self.arista_seleccionada = None
            self._refrescar_estilo_arista(clave)

    def _refrescar_estilo_arista(self, clave):
        line_id = self.aristas_canvas.get(clave)
        if line_id is None:
            return
        if clave == self.arista_seleccionada:
            self.canvas.itemconfig(
                line_id, fill=COLOR_ARISTA_SELECCIONADA,
                width=ANCHO_ARISTA_SELECCIONADA, dash=(5, 3)
            )
        elif clave in self.aristas_ciclo_resaltadas:
            self.canvas.itemconfig(
                line_id, fill=COLOR_CICLO, width=ANCHO_CICLO, dash=()
            )
        else:
            self.canvas.itemconfig(
                line_id, fill=COLOR_ARISTA_NORMAL, width=ANCHO_ARISTA_NORMAL, dash=()
            )

    def _crear_nodo(self, x, y):
        self.contador_nodos += 1
        id_nodo = self.contador_nodos
        etiqueta = f"V{id_nodo}"

        nodo = Nodo(id_nodo, etiqueta, x, y)

        nodo.circulo_id = self.canvas.create_oval(
            x - RADIO_NODO, y - RADIO_NODO,
            x + RADIO_NODO, y + RADIO_NODO,
            fill=COLOR_NODO, outline=COLOR_BORDE_NODO, width=2
        )
        nodo.texto_id = self.canvas.create_text(
            x, y, text=etiqueta, fill=COLOR_TEXTO_NODO, font=FUENTE_NODO
        )

        self.nodos[id_nodo] = nodo
        self.lista_adyacencia[id_nodo] = set()

        self._invalidar_resultado_ciclo()
        self._actualizar_estado()

    def _crear_arista(self, nodo_a, nodo_b):
        clave = frozenset({nodo_a.id, nodo_b.id})
        if clave in self.aristas_canvas:
            messagebox.showinfo(
                "Arista existente",
                f"Ya existe una conexión entre {nodo_a.etiqueta} y {nodo_b.etiqueta}."
            )
            return

        linea_id = self.canvas.create_line(
            nodo_a.x, nodo_a.y, nodo_b.x, nodo_b.y,
            fill=COLOR_ARISTA_NORMAL, width=ANCHO_ARISTA_NORMAL
        )
        self.canvas.tag_lower(linea_id)

        self.lista_adyacencia[nodo_a.id].add(nodo_b.id)
        self.lista_adyacencia[nodo_b.id].add(nodo_a.id)
        self.aristas_canvas[clave] = linea_id

        self._invalidar_resultado_ciclo()
        self._actualizar_estado()

    def _mover_nodo(self, nodo, x, y):
        ancho_canvas = self.canvas.winfo_width()
        alto_canvas = self.canvas.winfo_height()
        limite = RADIO_NODO + MARGEN_NODO

        x = max(limite, min(x, max(limite, ancho_canvas - limite)))
        y = max(limite, min(y, max(limite, alto_canvas - limite)))

        nodo.x, nodo.y = x, y
        self.canvas.coords(
            nodo.circulo_id, x - RADIO_NODO, y - RADIO_NODO, x + RADIO_NODO, y + RADIO_NODO
        )
        self.canvas.coords(nodo.texto_id, x, y)

        for id_vecino in self.lista_adyacencia.get(nodo.id, set()):
            vecino = self.nodos.get(id_vecino)
            if vecino is None:
                continue
            clave = frozenset({nodo.id, id_vecino})
            line_id = self.aristas_canvas.get(clave)
            if line_id is not None:
                self.canvas.coords(line_id, nodo.x, nodo.y, vecino.x, vecino.y)

    def _eliminar_seleccion(self, event=None):
        if self.nodo_seleccionado is not None:
            nodo = self.nodo_seleccionado
            self.nodo_seleccionado = None
            self._eliminar_nodo(nodo)
        elif self.arista_seleccionada is not None:
            clave = self.arista_seleccionada
            self.arista_seleccionada = None
            self._eliminar_arista(clave)

    def _eliminar_nodo(self, nodo):
        vecinos = list(self.lista_adyacencia.get(nodo.id, set()))
        for id_vecino in vecinos:
            clave = frozenset({nodo.id, id_vecino})
            self._eliminar_arista(clave, actualizar_estado=False)

        self.canvas.delete(nodo.circulo_id)
        self.canvas.delete(nodo.texto_id)

        self.nodos.pop(nodo.id, None)
        self.lista_adyacencia.pop(nodo.id, None)

        self._invalidar_resultado_ciclo()
        self._actualizar_estado()

    def _eliminar_arista(self, clave, actualizar_estado=True):
        line_id = self.aristas_canvas.pop(clave, None)
        if line_id is None:
            return
        self.canvas.delete(line_id)

        id_a, id_b = tuple(clave)
        self.lista_adyacencia.get(id_a, set()).discard(id_b)
        self.lista_adyacencia.get(id_b, set()).discard(id_a)
        self.aristas_ciclo_resaltadas.discard(clave)

        self._invalidar_resultado_ciclo()
        if actualizar_estado:
            self._actualizar_estado()

    def _actualizar_estado(self):
        self.label_estado.config(
            text=f"Nodos: {len(self.nodos)}   |   Aristas: {len(self.aristas_canvas)}"
        )

    def limpiar_canvas(self):
        self.canvas.delete("all")
        self.nodos.clear()
        self.lista_adyacencia.clear()
        self.aristas_canvas.clear()
        self.aristas_ciclo_resaltadas.clear()
        self.contador_nodos = 0
        self.nodo_seleccionado = None
        self.arista_seleccionada = None
        self.arrastre = None
        self._actualizar_estado()
        self.label_ciclo.config(text="Ciclo Hamiltoniano: (aún no calculado)")

    def restablecer_colores(self):
        self._invalidar_resultado_ciclo()

    def _invalidar_resultado_ciclo(self):
        if self.aristas_ciclo_resaltadas:
            claves_previas = list(self.aristas_ciclo_resaltadas)
            self.aristas_ciclo_resaltadas.clear()
            for clave in claves_previas:
                self._refrescar_estilo_arista(clave)
        self.label_ciclo.config(text="Ciclo Hamiltoniano: (aún no calculado)")
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
                return nodo_inicio in self.lista_adyacencia.get(ultimo, set())

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

        if len(self.nodos) < 3:
            messagebox.showwarning(
                "Nodos insuficientes",
                "Se necesitan al menos 3 vértices para poder formar un Ciclo Hamiltoniano."
            )
            return

        if not self.es_conexo():
            messagebox.showerror(
                "Grafo no conexo",
                "El grafo debe ser conexo para poder buscar un Ciclo Hamiltoniano.\n"
                "Conecta todos los nodos y vuelve a intentarlo."
            )
            return

        self.restablecer_colores()

        ids_nodos = list(self.nodos.keys())
        resultado = self._buscar_ciclo_hamiltoniano_backtracking(ids_nodos)

        if resultado is not None:
            for i in range(len(resultado) - 1):
                clave = frozenset({resultado[i], resultado[i + 1]})
                self.aristas_ciclo_resaltadas.add(clave)
                self._refrescar_estilo_arista(clave)

            etiquetas = [self.nodos[id_nodo].etiqueta for id_nodo in resultado]
            secuencia_texto = " → ".join(etiquetas)

            self.label_ciclo.config(text=f"Ciclo Hamiltoniano: {secuencia_texto}")
            messagebox.showinfo(
                "Ciclo Hamiltoniano encontrado",
                f"Se encontró un Ciclo Hamiltoniano"
            )
        else:
            self.label_ciclo.config(text="Ciclo Hamiltoniano: no existe para este grafo")
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
