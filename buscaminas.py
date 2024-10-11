import pygame
import random
from z3 import *

# Inicializar pygame
pygame.init()

# Constantes de la ventana y del tablero
WINDOW_SIZE = 400
BOARD_SIZE = 3
CELL_SIZE = 100

# Colores
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Configuración de la ventana
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 60))
pygame.display.set_caption('Buscaminas')

# Fuentes
FONT = pygame.font.Font(None, 40)
FONT_SMALL = pygame.font.Font(None, 30)

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.revealed = False
        self.marked = False
        self.neighboring_mines = 0

    def draw(self, screen):
        rect = pygame.Rect(self.col * CELL_SIZE, self.row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        
        if self.revealed:
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            if self.is_mine:
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 4)
            elif self.neighboring_mines > 0:
                text_surface = FONT.render(str(self.neighboring_mines), True, BLUE)
                screen.blit(text_surface, text_surface.get_rect(center=rect.center))
        elif self.marked:
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            pygame.draw.line(screen, GREEN, rect.topleft, rect.bottomright, 4)
            pygame.draw.line(screen, GREEN, rect.topright, rect.bottomleft, 4)
        else:
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

class Minesweeper:
    def __init__(self):
        self.grid = [[Cell(row, col) for col in range(BOARD_SIZE)] for row in range(BOARD_SIZE)]
        self.num_mines = 3
        self.populate_mines()
        self.set_neighbors()

    def populate_mines(self):
        # Colocar minas aleatoriamente
        mines_placed = 0
        while mines_placed < self.num_mines:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)
            if not self.grid[row][col].is_mine:
                self.grid[row][col].is_mine = True
                mines_placed += 1

    def set_neighbors(self):
        # Calcular el número de minas vecinas
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if not self.grid[row][col].is_mine:
                    self.grid[row][col].neighboring_mines = self.count_neighboring_mines(row, col)

    def count_neighboring_mines(self, row, col):
        mine_count = 0
        for r in range(max(0, row - 1), min(BOARD_SIZE, row + 2)):
            for c in range(max(0, col - 1), min(BOARD_SIZE, col + 2)):
                if self.grid[r][c].is_mine:
                    mine_count += 1
        return mine_count

    def reveal(self, row, col):
        # Revelar una celda
        cell = self.grid[row][col]
        if not cell.revealed and not cell.marked:
            cell.revealed = True
            if cell.neighboring_mines == 0 and not cell.is_mine:
                for r in range(max(0, row - 1), min(BOARD_SIZE, row + 2)):
                    for c in range(max(0, col - 1), min(BOARD_SIZE, col + 2)):
                        if not self.grid[r][c].revealed:
                            self.reveal(r, c)

    def mark(self, row, col):
        # Marcar una mina
        cell = self.grid[row][col]
        if not cell.revealed:
            cell.marked = not cell.marked

    def draw(self, screen):
        # Dibujar el tablero
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.grid[row][col].draw(screen)

    def check_win(self):
        # Comprobar si el jugador ha ganado
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cell = self.grid[row][col]
                if not cell.is_mine and not cell.revealed:
                    return False
        return True

    def check_loss(self):
        # Comprobar si el jugador ha perdido
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cell = self.grid[row][col]
                if cell.is_mine and cell.revealed:
                    return True
        return False

class Game:
    def __init__(self):
        self.board = Minesweeper()
        self.running = True
        self.mode = "Menu"
        self.game_over = False

    def draw_menu(self):
        screen.fill(WHITE)
        title_surface = FONT.render("Selecciona el Modo", True, BLACK)
        screen.blit(title_surface, (50, 30))

        # Botón para jugar como jugador
        pygame.draw.rect(screen, GRAY, (50, 100, 200, 50))
        pygame.draw.rect(screen, BLACK, (50, 100, 200, 50), 2)
        player_mode_surface = FONT.render("Jugador", True, BLACK)
        screen.blit(player_mode_surface, (90, 110))

        # Botón para que la IA juegue
        pygame.draw.rect(screen, GRAY, (50, 200, 200, 50))
        pygame.draw.rect(screen, BLACK, (50, 200, 200, 50), 2)
        ai_mode_surface = FONT.render("IA", True, BLACK)
        screen.blit(ai_mode_surface, (130, 210))

        pygame.display.flip()

    def handle_event(self, event):
        if self.mode == "Menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 50 <= x <= 250:
                    if 100 <= y <= 150:
                        self.mode = "Player"
                    elif 200 <= y <= 250:
                        self.mode = "AI"
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                row = y // CELL_SIZE
                col = x // CELL_SIZE

                if event.button == 1:  # Click izquierdo para revelar
                    if not self.game_over:
                        self.board.reveal(row, col)
                elif event.button == 3:  # Click derecho para marcar una mina
                    if not self.game_over:
                        self.board.mark(row, col)

                if self.board.check_loss():
                    print("Has perdido!")
                    self.game_over = True
                elif self.board.check_win():
                    print("Has ganado!")
                    self.game_over = True

    def solve_with_ia(self):
        s = Solver()
        cells = [[Bool(f'cell_{r}_{c}') for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]

        # Añadir restricciones al solver
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = self.board.grid[r][c]
                if cell.revealed and not cell.is_mine:
                    neighbors = self.get_neighbors(cells, r, c)
                    s.add(Sum([If(n, 1, 0) for n in neighbors]) == cell.neighboring_mines)

        if s.check() == sat:
            model = s.model()
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if model.evaluate(cells[r][c]):
                        print(f'Hay una mina en ({r}, {c})')
                    else:
                        print(f'No hay mina en ({r}, {c})')
        else:
            print("No se pudo resolver.")

    def get_neighbors(self, cells, row, col):
        neighbors = []
        for r in range(max(0, row - 1), min(BOARD_SIZE, row + 2)):
            for c in range(max(0, col - 1), min(BOARD_SIZE, col + 2)):
                if r != row or c != col:
                    neighbors.append(cells[r][c])
        return neighbors

    def draw(self, screen):
        if self.mode == "Menu":
            self.draw_menu()
        else:
            screen.fill(WHITE)
            self.board.draw(screen)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.handle_event(event)

            self.draw(screen)
            pygame.display.flip()

# Iniciar el juego
game = Game()
game.run()

pygame.quit()
