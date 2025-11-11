import pygame
import random
import sys

# =================================================================
# 1. CONFIGURACIÓN INICIAL DE PYGAME Y CONSTANTES DEL JUEGO
# =================================================================

# Inicializar Pygame
pygame.init()

# Constantes de la Ventana y la Cuadrícula
ANCHO_VENTANA = 800 # Ancho total de la ventana en píxeles
ALTURA_VENTANA = 500  # Altura total de la ventana en píxeles
TAMANO_ELEMENTO = 20  # Tamaño de cada segmento de la serpiente y la manzana (define la cuadrícula)
FPS = 10 # Velocidad del juego (frames por segundo)

# Colores (Tuplas RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
VERDE_CABEZA = (0, 200, 0) # Color de la cabeza (si no se carga la imagen)
VERDE_CUERPO = (0, 150, 0) # Color del cuerpo
ROJO = (255, 0, 0)
GRIS = (240, 240, 240) # Color de fondo

# Pantalla
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTURA_VENTANA)) # Crea la ventana
pygame.display.set_caption("Snake Clásico (Modo Teletransporte)") # Establece el título de la ventana

# Reloj para controlar el FPS
reloj = pygame.time.Clock()

# Dirección inicial (Vector de movimiento por paso: X, Y)
DIRECCION_INICIAL = (TAMANO_ELEMENTO, 0) # Inicialmente se mueve a la derecha (20 píxeles en X)

# =================================================================
# 2. CLASE DE MECÁNICAS DE LA MANZANA (MecanicasManzana)
# =================================================================
class MecanicasManzana:
    def __init__(self):
        # Límites máximos para que la manzana no aparezca fuera de la ventana
        self.maximo_x = ANCHO_VENTANA - TAMANO_ELEMENTO
        self.maximo_y = ALTURA_VENTANA - TAMANO_ELEMENTO
        self.manzana_x = 0 # Coordenada X inicial
        self.manzana_y = 0 # Coordenada Y inicial

    def colocar_manzana_random(self, segmento_serpiente_x, segmento_serpiente_y, direccion_actual, segmentos_serpiente):
        """
        Coloca la manzana en un punto aleatorio, priorizando la mitad de la ventana
        hacia donde se dirige la serpiente, y asegurando que no aparezca en el cuerpo.
        
       Uso de set (conjunto) para coords_a_evitar y listas por comprensión para posiciones_validas.
        """
        dx, dy = direccion_actual
        
        mitad_ancho = ANCHO_VENTANA // 2
        mitad_altura = ALTURA_VENTANA // 2
        
        min_x, max_x, min_y, max_y = 0, self.maximo_x, 0, self.maximo_y
        
        # Ajustar límites según la dirección (Crear la "mitad delantera")
        if dx > 0: # Derecha
            min_x = mitad_ancho
        elif dx < 0: # Izquierda
            max_x = mitad_ancho - TAMANO_ELEMENTO 
        elif dy > 0: # Abajo
            min_y = mitad_altura
        elif dy < 0: # Arriba
            max_y = mitad_altura - TAMANO_ELEMENTO 

        # Crea listas de pasos X e Y que cumplen con la cuadrícula (TAMANO_ELEMENTO) y el rango de la "mitad delantera"
        x_pasos = list(range(min_x // TAMANO_ELEMENTO, (max_x + TAMANO_ELEMENTO) // TAMANO_ELEMENTO))
        y_pasos = list(range(min_y // TAMANO_ELEMENTO, (max_y + TAMANO_ELEMENTO) // TAMANO_ELEMENTO))
        
        # Crea un CONJUNTO de coordenadas de cuadrícula ocupadas por la serpiente.
        coords_a_evitar = set((x // TAMANO_ELEMENTO, y // TAMANO_ELEMENTO) for x, y in segmentos_serpiente)

        #  Usa lista por comprensión para generar posiciones_validas 
        posiciones_validas = [
            (xs * TAMANO_ELEMENTO, ys * TAMANO_ELEMENTO) 
            for xs in x_pasos 
            for ys in y_pasos 
            if (xs, ys) not in coords_a_evitar
        ]
        
        if not posiciones_validas:
            self.colocar_manzana_segura(segmentos_serpiente) # Llamada de respaldo si no hay espacio en la mitad delantera
            return

        self.manzana_x, self.manzana_y = random.choice(posiciones_validas) # Elige una posición válida al azar

    def colocar_manzana_segura(self, segmentos_serpiente):
        """
        Método de respaldo   busca en toda la ventana y evita el cuerpo.
        
         Ademas usa  conjuntos para coords_a_evitar y listas por comprensión para posiciones_validas.
        """
        max_x_pasos = self.maximo_x // TAMANO_ELEMENTO
        max_y_pasos = self.maximo_y // TAMANO_ELEMENTO
        
        #Crear un CONJUNTO de coordenadas de cuadrícula ocupadas por la serpiente.
        coords_a_evitar = set((x // TAMANO_ELEMENTO, y // TAMANO_ELEMENTO) for x, y in segmentos_serpiente)

        #  Usa lista por comprensión para generar posiciones_validas .
        # Itera sobre toda la cuadrícula de la ventana
        posiciones_validas = [
            (xs * TAMANO_ELEMENTO, ys * TAMANO_ELEMENTO) 
            for xs in range(max_x_pasos + 1)
            for ys in range(max_y_pasos + 1)
            if (xs, ys) not in coords_a_evitar#evita manzanas fuera de ventana o cuerpo de la serpiente
        ]
        
        if not posiciones_validas:
            print("ERROR : ¡No hay espacio para generar la manzana!")
            return

        self.manzana_x, self.manzana_y = random.choice(posiciones_validas)#una vez hecho el calculo elije una posicion random de las validas
        print(f"🍏 Nueva Manzana (Respaldo) en: ({self.manzana_x}, {self.manzana_y})")

    def obtener_coordenadas(self):
        """Retorna la posición actual (x, y) de la manzana."""
        return self.manzana_x, self.manzana_y

    def dibujar(self, superficie):
        """Dibuja la manzana en la superficie de la pantalla."""
        manzana_rect = pygame.Rect(self.manzana_x, self.manzana_y, TAMANO_ELEMENTO, TAMANO_ELEMENTO)
        # Dibuja un círculo rojo, centrado en el segmento de la cuadrícula
        pygame.draw.circle(superficie, ROJO, manzana_rect.center, TAMANO_ELEMENTO // 2 - 2) 

# =================================================================
# 3. CLASE DE LA SERPIENTE Y LÓGICA DEL JUEGO (JuegoSerpiente)
# =================================================================

class JuegoSerpiente:
    def __init__(self):
        # Calcular la posición inicial centrada y alineada a la cuadrícula
        centro_x = (ANCHO_VENTANA // 2) - (TAMANO_ELEMENTO // 2)
        centro_y = (ALTURA_VENTANA // 2) - (TAMANO_ELEMENTO // 2)
        inicio_x = (centro_x // TAMANO_ELEMENTO) * TAMANO_ELEMENTO
        inicio_y = (centro_y // TAMANO_ELEMENTO) * TAMANO_ELEMENTO
        
        self.segmentos = [(inicio_x, inicio_y)] # Lista que almacena las coordenadas de cada segmento de la serpiente
        self.puntuacion = 0
        self.mecanicas_manzana = MecanicasManzana() # Crea el objeto manzana
        self.mecanicas_manzana.colocar_manzana_random(inicio_x, inicio_y, DIRECCION_INICIAL, self.segmentos)
        
        self.imagen_cabeza_serpiente = self.cargar_imagen_serpiente() # Carga la imagen de la cabeza
        self.direccion_actual = DIRECCION_INICIAL # Establece la dirección inicial

    def cargar_imagen_serpiente(self):
        """Carga la imagen de la cabeza  y la coloca a escala adecuada para la ventana."""
        ruta_imagen = "cabeza_serpiente.png" 
        try:
            imagen = pygame.image.load(ruta_imagen).convert_alpha()#Si la imagen tiene fondo transparente, usa siempre convert_alpha().
            imagen_escalada = pygame.transform.scale(imagen, (TAMANO_ELEMENTO, TAMANO_ELEMENTO))#ajusta el tamaño
            return imagen_escalada
        except pygame.error:
            return None # Retorna None si el archivo no se encuentra

    def dibujar_puntuacion(self, superficie):
        """Dibuja la puntuación actual en la superficie del juego. 
        Y personaliza algunos aspectos de esta"""
        fuente = pygame.font.Font(None, 36)
        texto = fuente.render(f"Puntuación: {self.puntuacion}", True, BLANCO) 
        fondo_texto = pygame.Rect(10, 10, texto.get_width() + 10, texto.get_height() + 10)
        pygame.draw.rect(superficie, (51, 51, 51), fondo_texto, border_radius=5) 
        superficie.blit(texto, (15, 15))#blit = copiar un Surface(superficie) dentro de otro Surface

    def dibujar_serpiente(self, superficie):
        """Dibuja cada segmento de la serpiente (cabeza y cuerpo)."""
        for i, (x, y) in enumerate(self.segmentos):#recorre los segmentos de la serpiente
            segmento_rect = pygame.Rect(x, y, TAMANO_ELEMENTO, TAMANO_ELEMENTO)
            if i == 0:
                # Dibuja la cabeza (usa imagen si está disponible, sino color VERDE_CABEZA)
                if self.imagen_cabeza_serpiente:
                    superficie.blit(self.imagen_cabeza_serpiente, segmento_rect.topleft)
                else:
                    pygame.draw.rect(superficie, VERDE_CABEZA, segmento_rect) 
            else:
                # Dibuja el cuerpo
                pygame.draw.rect(superficie, VERDE_CUERPO, segmento_rect) 

    def mover_serpiente(self):
        """
        Calcula el nuevo movimiento.
        
        """
        dx, dy = self.direccion_actual
        cabeza_x, cabeza_y = self.segmentos[0]#posicion cabeza
        
        # Calcular la siguiente posición sin aplicar límites aún
        siguiente_x = cabeza_x + dx
        siguiente_y = cabeza_y + dy

        # 1. Aplica el efecto de teletransporte  si se topa con el limite de ventana
        siguiente_x = siguiente_x % ANCHO_VENTANA
        siguiente_y = siguiente_y % ALTURA_VENTANA

        # Asegura que si la posición es negativa (al salir por la izquierda o arriba) 
        # se ajuste correctamente al extremo opuesto.
        if siguiente_x < 0:
            siguiente_x += ANCHO_VENTANA
        if siguiente_y < 0:
            siguiente_y += ALTURA_VENTANA

        # 2. Mueve el cuerpo: Inserta la nueva cabeza(al cuerpo)
        nueva_cabeza = (siguiente_x, siguiente_y)
        self.segmentos.insert(0, nueva_cabeza)
        
        

        # 3. Colisión con manzana
        esta_comiendo = self.chequeo_colision_manzana()
        
        if not esta_comiendo:
            self.segmentos.pop() # Elimina la cola si NO comió (simula el movimiento)
        
        return True # El movimiento fue exitoso

    def chequeo_colision_manzana(self):
        """Verifica si la cabeza choca con la manzana, viendo si ambas coords son iguales"""
        cabeza_x, cabeza_y = self.segmentos[0]
        manzana_x, manzana_y = self.mecanicas_manzana.obtener_coordenadas()
        
        if cabeza_x == manzana_x and cabeza_y == manzana_y:
            self.puntuacion += 1 # Incrementa la puntuación
            print(f"🎉 ¡COLISIÓN! Puntuación actual: {self.puntuacion}")
            
            # Coloca una nueva manzana lejos del cuerpo
            self.mecanicas_manzana.colocar_manzana_random(cabeza_x, cabeza_y, self.direccion_actual, self.segmentos)
            
            return True # La serpiente creció
        
        return False

    def manejar_entrada(self, tecla):
        """Maneja la entrada del teclado y actualiza la dirección dependiendo el evento de presion de tecla."""
        dx, dy = self.direccion_actual
        
        nueva_direccion = None
        
        # Cambia la dirección si no es la opuesta a la actual (ej: no puede ir de derecha a izquierda instantáneamente)
        if tecla == pygame.K_UP:
            if dy == 0: nueva_direccion = (0, -TAMANO_ELEMENTO) # Moverse -Y (hacia arriba)
        elif tecla == pygame.K_DOWN:
            if dy == 0: nueva_direccion = (0, TAMANO_ELEMENTO) # Moverse +Y (hacia abajo)
        elif tecla == pygame.K_LEFT:
            if dx == 0: nueva_direccion = (-TAMANO_ELEMENTO, 0) # Moverse -X (hacia izquierda)
        elif tecla == pygame.K_RIGHT:
            if dx == 0: nueva_direccion = (TAMANO_ELEMENTO, 0) # Moverse +X (hacia derecha)
                
        if nueva_direccion:
            self.direccion_actual = nueva_direccion # Aplica la nueva dirección


# =================================================================
# 4. BUCLE PRINCIPAL DEL JUEGO (CicloJuego)
# =================================================================
def principal():
    juego = JuegoSerpiente() # Crea el objeto principal del juego
    ejecutando = True # Bandera para mantener el ciclo activo

    while ejecutando:
        # 1. Procesamiento de Eventos (Entrada del usuario)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False # Cierra si el usuario hace clic en X
            elif evento.type == pygame.KEYDOWN:
                juego.manejar_entrada(evento.key) # Procesa la tecla presionada

        # 2. Lógica del Juego (Actualización)
        if not juego.mover_serpiente():#Mantiene el movimiento de la serpiente constante
            ejecutando = False

        # 3. Dibujo (Renderizado)
        pantalla.fill(GRIS) # Pinta el fondo
        
        juego.mecanicas_manzana.dibujar(pantalla) # Dibuja la manzana
        juego.dibujar_serpiente(pantalla) # Dibuja la serpiente
        juego.dibujar_puntuacion(pantalla) # Dibuja la puntuación
        
        pygame.display.flip() # Actualiza toda la pantalla para mostrar los dibujos

        # 4. Control de Velocidad
        reloj.tick(FPS) # Espera el tiempo necesario para cumplir con los FPS definidos

    # 5. Salida del Juego
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    principal()