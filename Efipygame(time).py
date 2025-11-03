import pygame
import random
import sys
import time  # Para el cronómetro

# =================================================================
# 1. CONFIGURACIÓN INICIAL DE PYGAME Y CONSTANTES DEL JUEGO
# =================================================================

pygame.init()

ANCHO_VENTANA = 800
ALTURA_VENTANA = 500
TAMANO_ELEMENTO = 20
FPS = 10

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
VERDE_CABEZA = (0, 200, 0)
VERDE_CUERPO = (0, 150, 0)
ROJO = (255, 0, 0)
GRIS = (240, 240, 240)

FONDO_IMAGEN_RUTA = "fondo_bosque.png"
VELOCIDAD_FONDO = 0.5

pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTURA_VENTANA))
pygame.display.set_caption("Snake Clásico (Modo Teletransporte)")
reloj = pygame.time.Clock()
DIRECCION_INICIAL = (TAMANO_ELEMENTO, 0)

TIEMPO_MAXIMO = 10  # ⏱ Tiempo máximo en segundos antes de terminar el juego

# =================================================================
# 2. CLASE DE MECÁNICAS DE LA MANZANA
# =================================================================
class MecanicasManzana:
    def __init__(self):
        self.maximo_x = ANCHO_VENTANA - TAMANO_ELEMENTO
        self.maximo_y = ALTURA_VENTANA - TAMANO_ELEMENTO
        self.manzana_x = 0
        self.manzana_y = 0

    def colocar_manzana_random(self, segmento_serpiente_x, segmento_serpiente_y, direccion_actual, segmentos_serpiente):
        dx, dy = direccion_actual
        mitad_ancho = ANCHO_VENTANA // 2
        mitad_altura = ALTURA_VENTANA // 2
        min_x, max_x, min_y, max_y = 0, self.maximo_x, 0, self.maximo_y

        if dx > 0: min_x = mitad_ancho
        elif dx < 0: max_x = mitad_ancho - TAMANO_ELEMENTO
        elif dy > 0: min_y = mitad_altura
        elif dy < 0: max_y = mitad_altura - TAMANO_ELEMENTO

        x_pasos = list(range(min_x // TAMANO_ELEMENTO, (max_x + TAMANO_ELEMENTO) // TAMANO_ELEMENTO))
        y_pasos = list(range(min_y // TAMANO_ELEMENTO, (max_y + TAMANO_ELEMENTO) // TAMANO_ELEMENTO))
        coords_a_evitar = set((x // TAMANO_ELEMENTO, y // TAMANO_ELEMENTO) for x, y in segmentos_serpiente)

        posiciones_validas = [
            (xs * TAMANO_ELEMENTO, ys * TAMANO_ELEMENTO)
            for xs in x_pasos
            for ys in y_pasos
            if (xs, ys) not in coords_a_evitar
        ]

        if not posiciones_validas:
            self.colocar_manzana_segura(segmentos_serpiente)
            return

        self.manzana_x, self.manzana_y = random.choice(posiciones_validas)

    def colocar_manzana_segura(self, segmentos_serpiente):
        max_x_pasos = self.maximo_x // TAMANO_ELEMENTO
        max_y_pasos = self.maximo_y // TAMANO_ELEMENTO
        coords_a_evitar = set((x // TAMANO_ELEMENTO, y // TAMANO_ELEMENTO) for x, y in segmentos_serpiente)
        posiciones_validas = [
            (xs * TAMANO_ELEMENTO, ys * TAMANO_ELEMENTO)
            for xs in range(max_x_pasos + 1)
            for ys in range(max_y_pasos + 1)
            if (xs, ys) not in coords_a_evitar
        ]
        if not posiciones_validas:
            print("ERROR FATAL: ¡No hay espacio para generar la manzana!")
            return
        self.manzana_x, self.manzana_y = random.choice(posiciones_validas)

    def obtener_coordenadas(self):
        return self.manzana_x, self.manzana_y

    def dibujar(self, superficie):
        manzana_rect = pygame.Rect(self.manzana_x, self.manzana_y, TAMANO_ELEMENTO, TAMANO_ELEMENTO)
        pygame.draw.circle(superficie, ROJO, manzana_rect.center, TAMANO_ELEMENTO // 2 - 2)

# =================================================================
# 3. CLASE DE LA SERPIENTE Y CRONÓMETRO DE 10 SEGUNDOS
# =================================================================
class JuegoSerpiente:
    def __init__(self):
        centro_x = (ANCHO_VENTANA // 2) - (TAMANO_ELEMENTO // 2)
        centro_y = (ALTURA_VENTANA // 2) - (TAMANO_ELEMENTO // 2)
        inicio_x = (centro_x // TAMANO_ELEMENTO) * TAMANO_ELEMENTO
        inicio_y = (centro_y // TAMANO_ELEMENTO) * TAMANO_ELEMENTO

        self.segmentos = [(inicio_x, inicio_y)]
        self.puntuacion = 0
        self.mecanicas_manzana = MecanicasManzana()
        self.mecanicas_manzana.colocar_manzana_random(inicio_x, inicio_y, DIRECCION_INICIAL, self.segmentos)
        self.imagen_cabeza_serpiente = self.cargar_imagen_serpiente()
        self.direccion_actual = DIRECCION_INICIAL

        self.tiempo_inicio = time.time()  # ⏱ Guardamos el tiempo de inicio del cronómetro

    def cargar_imagen_serpiente(self):
        ruta_imagen = "cabeza_serpiente.png"
        try:
            imagen = pygame.image.load(ruta_imagen).convert_alpha()
            return pygame.transform.scale(imagen, (TAMANO_ELEMENTO, TAMANO_ELEMENTO))
        except pygame.error:
            return None

    def dibujar_puntuacion(self, superficie):
        fuente = pygame.font.Font(None, 36)
        texto = fuente.render(f"Puntuación: {self.puntuacion}", True, BLANCO)
        fondo_texto = pygame.Rect(10, 10, texto.get_width() + 10, texto.get_height() + 10)
        pygame.draw.rect(superficie, (51, 51, 51), fondo_texto, border_radius=5)
        superficie.blit(texto, (15, 15))

    # ================= CRONÓMETRO =================
    def dibujar_cronometro(self, superficie):
        """Dibuja el tiempo restante (10s) en pantalla"""
        tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
        tiempo_restante = max(TIEMPO_MAXIMO - tiempo_transcurrido, 0)  # Evita negativos
        fuente = pygame.font.Font(None, 36)
        texto = fuente.render(f"Tiempo: {tiempo_restante}s", True, BLANCO)
        fondo_texto = pygame.Rect(ANCHO_VENTANA - texto.get_width() - 20, 10, texto.get_width() + 10, texto.get_height() + 10)
        pygame.draw.rect(superficie, (51, 51, 51), fondo_texto, border_radius=5)
        superficie.blit(texto, (ANCHO_VENTANA - texto.get_width() - 15, 15))
        return tiempo_restante  # Retorna para chequear fin de juego

    def dibujar_serpiente(self, superficie):
        for i, (x, y) in enumerate(self.segmentos):
            segmento_rect = pygame.Rect(x, y, TAMANO_ELEMENTO, TAMANO_ELEMENTO)
            if i == 0:
                if self.imagen_cabeza_serpiente:
                    superficie.blit(self.imagen_cabeza_serpiente, segmento_rect.topleft)
                else:
                    pygame.draw.rect(superficie, VERDE_CABEZA, segmento_rect)
            else:
                pygame.draw.rect(superficie, VERDE_CUERPO, segmento_rect)

    def mover_serpiente(self):
        dx, dy = self.direccion_actual
        cabeza_x, cabeza_y = self.segmentos[0]
        siguiente_x = (cabeza_x + dx) % ANCHO_VENTANA
        siguiente_y = (cabeza_y + dy) % ALTURA_VENTANA
        if siguiente_x < 0: siguiente_x += ANCHO_VENTANA
        if siguiente_y < 0: siguiente_y += ALTURA_VENTANA

        nueva_cabeza = (siguiente_x, siguiente_y)
        self.segmentos.insert(0, nueva_cabeza)

        # Si come manzana, reinicia cronómetro
        if self.chequeo_colision_manzana():
            self.tiempo_inicio = time.time()  # 🔹 Reinicia el cronómetro al comer
        else:
            self.segmentos.pop()

        return True

    def chequeo_colision_manzana(self):
        cabeza_x, cabeza_y = self.segmentos[0]
        manzana_x, manzana_y = self.mecanicas_manzana.obtener_coordenadas()
        if cabeza_x == manzana_x and cabeza_y == manzana_y:
            self.puntuacion += 1
            self.mecanicas_manzana.colocar_manzana_random(cabeza_x, cabeza_y, self.direccion_actual, self.segmentos)
            return True
        return False

    def manejar_entrada(self, tecla):
        dx, dy = self.direccion_actual
        nueva_direccion = None
        if tecla == pygame.K_UP and dy == 0: nueva_direccion = (0, -TAMANO_ELEMENTO)
        elif tecla == pygame.K_DOWN and dy == 0: nueva_direccion = (0, TAMANO_ELEMENTO)
        elif tecla == pygame.K_LEFT and dx == 0: nueva_direccion = (-TAMANO_ELEMENTO, 0)
        elif tecla == pygame.K_RIGHT and dx == 0: nueva_direccion = (TAMANO_ELEMENTO, 0)
        if nueva_direccion: self.direccion_actual = nueva_direccion

# =================================================================
# 4. FUNCIONES AUXILIARES
# =================================================================
def cargar_fondo_animado():
    try:
        imagen = pygame.image.load(FONDO_IMAGEN_RUTA).convert()
        return pygame.transform.scale(imagen, (ANCHO_VENTANA * 2, ALTURA_VENTANA))
    except pygame.error:
        print(f"ERROR: No se pudo cargar la imagen de fondo '{FONDO_IMAGEN_RUTA}'.")
        return None

# =================================================================
# 5. BUCLE PRINCIPAL
# =================================================================
def principal():
    juego = JuegoSerpiente()
    ejecutando = True
    fondo_animado = cargar_fondo_animado()
    pos_fondo_x = 0

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                juego.manejar_entrada(evento.key)

        if not juego.mover_serpiente():
            ejecutando = False

        if fondo_animado:
            pos_fondo_x -= VELOCIDAD_FONDO
            if pos_fondo_x <= -ANCHO_VENTANA:
                pos_fondo_x = 0
            pantalla.blit(fondo_animado, (pos_fondo_x, 0))
            pantalla.blit(fondo_animado, (pos_fondo_x + ANCHO_VENTANA, 0))
        else:
            pantalla.fill(GRIS)

        juego.mecanicas_manzana.dibujar(pantalla)
        juego.dibujar_serpiente(pantalla)
        juego.dibujar_puntuacion(pantalla)

        # 🔹 Dibuja cronómetro y chequea si se pasó de 10s
        tiempo_restante = juego.dibujar_cronometro(pantalla)
        if tiempo_restante <= 0:
            print("⏰ ¡Se acabó el tiempo!")
            ejecutando = False

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    principal()
