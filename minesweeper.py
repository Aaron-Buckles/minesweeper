import random
import pygame


# game settings
field_width = 12

field_size = field_width ** 2
number_of_bombs = 20
mines = []

first_click = False

# layout settings
spacing = None
mine_size = None

# pygame setting
display_width = 800
display_height = 600

white = (255, 255, 255)
light_grey = (200, 200, 200)
grey = (128, 128, 128)
dark_grey = (56, 56, 56)
black = (0, 0, 0)
blue = (0, 0, 220)

pygame.init()

game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Minesweeper')

default_font = 'roboto'

clock = pygame.time.Clock()


class Mine:
    def __init__(self, index, bomb):
        self.x = int(index % field_width)
        self.y = int(index // field_width)
        self.index = index
        self.bomb = bomb
        self.neighbor_bombs = 0
        self.been_clicked = False
        self.flagged = False

    def display(self, mouse_button):
        if self.index != 0:
            x = self.x * (spacing + mine_size) + spacing
            y = self.y * (spacing + mine_size) + spacing
        else:
            x = self.x + spacing
            y = self.y + spacing

        if self.flagged == True:
            text = "!"
        elif self.neighbor_bombs == 0 or self.bomb == True or self.been_clicked == False:
            text = ""
        else:
            text = str(self.neighbor_bombs)

        active = not self.been_clicked
        button(text, x, y, mine_size, mine_size, grey, light_grey, mouse_button, action=self.index, active=active)

    def check_surrounding_neighbors(self):
        self.neighbor_bombs = 0

        # top
        self.neighbor_bombs += self.check_neighbor(0, -1)
        # left
        self.neighbor_bombs += self.check_neighbor(-1, 0)
        # right
        self.neighbor_bombs += self.check_neighbor(1, 0)
        # bottom
        self.neighbor_bombs += self.check_neighbor(0, 1)
        # top, left
        self.neighbor_bombs += self.check_neighbor(-1, -1)
        # top, right
        self.neighbor_bombs += self.check_neighbor(1, -1)
        # bottom, left
        self.neighbor_bombs += self.check_neighbor(-1, 1)
        # bottom, right
        self.neighbor_bombs += self.check_neighbor(1, 1)

    def get_index(self, x, y):
        return x + (field_width * y)

    def get_xy(self, index):
        x = int(index % field_width)
        y = int(index / field_width)
        return x, y

    def check_neighbor(self, x_offset, y_offset):
        x = self.x + x_offset
        y = self.y + y_offset

        if x < 0 or x > field_width - 1 or y < 0 or y > field_width - 1:
            return 0

        index = self.get_index(x, y)
        if mines[index].bomb == True:
            return 1
        else:
            return 0

    def uncover(self):
        self.been_clicked = True

    def check_for_win(self):
        for mine in mines:
            if mine.bomb == False and mine.been_clicked == False:
                break
        else:
            game_over_screen(win=True)

    def click(self, right_clicked=False):
        if right_clicked == True:
            if self.flagged == True:
                self.flagged = False
            else:
                self.flagged = True
        else:
            if self.flagged == True:
                self.flagged = False
            else:
                self.been_clicked = True

                global first_click
                if first_click == False:
                    # this is the first mine to be clicked
                    first_click = True
                    self.bomb = False

                if self.neighbor_bombs == 0:
                    mines_to_check = [(self.x, self.y)]
                    mines_checked = []

                    while True:
                        if len(mines_to_check) == 0:
                            break

                        x = mines_to_check[0][0]
                        y = mines_to_check[0][1]

                        neighbor_mines = []
                        neighbor_mines.append(self.get_index(x, y - 1))
                        neighbor_mines.append(self.get_index(x, y + 1))
                        neighbor_mines.append(self.get_index(x - 1, y))
                        neighbor_mines.append(self.get_index(x + 1, y))

                        valid_neighbors = []
                        for mine_index in neighbor_mines:
                            neighbor_x, neighbor_y = self.get_xy(mine_index)
                            if mine_index >= 0 and mine_index < field_size:
                                if abs(neighbor_x - x) <= 1 and abs(neighbor_y - y) <= 1:
                                    valid_neighbors.append(mine_index)

                        diagonal_mines = []
                        diagonal_mines.append(self.get_index(x - 1, y - 1))
                        diagonal_mines.append(self.get_index(x - 1, y + 1))
                        diagonal_mines.append(self.get_index(x + 1, y - 1))
                        diagonal_mines.append(self.get_index(x + 1, y + 1))

                        valid_diagonals = []
                        for mine_index in diagonal_mines:
                            neighbor_x, neighbor_y = self.get_xy(mine_index)
                            if mine_index >= 0 and mine_index < field_size:
                                if abs(neighbor_x - x) <= 1 and abs(neighbor_y - y) <= 1:
                                    if mines[mine_index].bomb == False:
                                        valid_diagonals.append(mine_index)

                        valid_neighbors.extend(valid_diagonals)

                        for mine_index in valid_neighbors:
                            if mines[mine_index].been_clicked == False:
                                if mines[mine_index].bomb == False:
                                    mines[mine_index].uncover()
                                    if mines[mine_index].neighbor_bombs == 0:
                                        mines_to_check.append(self.get_xy(mine_index))

                        mines_checked.append((x, y))
                        del mines_to_check[0]
                        mines_to_check = [mine for mine in mines_to_check if mine not in mines_checked]

                self.check_surrounding_neighbors()

                self.check_for_win()

                if self.bomb == True:
                    game_over_screen()


class Slider:
    height = 10
    handle_width = 10
    handle_height = height + 5

    def __init__(self, x, y, minimum=0, maximum=1, width=200, value=0):
        self.x = x
        self.y = y
        self.minimum = minimum
        self.maximum = maximum
        self.width = width

        self.handle_x = x + int((value - minimum) / (maximum - minimum) * self.width)

    def set_handle_x(self):
        cursor_x = pygame.mouse.get_pos()[0]
        click = pygame.mouse.get_pressed()[0]

        if click:
            if self.x < cursor_x < self.x + self.width:
                self.handle_x = cursor_x - self.handle_width // 2

    @property
    def value(self):
        value = ((self.handle_x - self.x) / self.width) * self.maximum
        if value > self.maximum:
            value = self.maximum
        elif value < self.minimum:
            value = self.minimum
        return value

    def display(self):
        pygame.draw.rect(game_display, grey, [self.x, self.y, self.width, self.height])
        pygame.draw.rect(game_display, blue, [self.handle_x, self.y - self.handle_height//2, self.handle_width, self.handle_height])


def quit_game():
    pygame.quit()
    quit()


def button(text, x, y, width, height, color, active_color, mouse_button, action=None, active=True):
    global game_display

    if active == True:
        cursor = pygame.mouse.get_pos()

        if x < cursor[0] < x + width and y < cursor[1] < y + height:
            pygame.draw.rect(game_display, active_color, [x, y, width, height])
            if mouse_button == 1:
                if action != None:
                    if action == "quit":
                        quit_game()
                    elif action == "play":
                        global spacing
                        global mine_size
                        global display_width
                        global display_height

                        spacing = 100 // field_width
                        mine_size = 600 // field_width

                        display_width = ((field_width * spacing) + spacing) + (field_width * mine_size)
                        display_height = display_width

                        game_display = pygame.display.set_mode((display_width, display_height))

                        game_loop()
                    else:
                        mines[action].click()
            elif mouse_button == 3:
                if action == "quit":
                    pass
                elif action == "play":
                    pass
                else:
                    mines[action].click(right_clicked=True)
                
        else:
            pygame.draw.rect(game_display, color, [x, y, width, height])
    else:
        pygame.draw.rect(game_display, active_color, [x, y, width, height])

    if active:
        text_color = black
    else:
        text_color = dark_grey

    text_surface, text_rect = text_objects(text, text_color, 25, default_font)
    text_rect.center = (x + width//2, y + height//2)
    game_display.blit(text_surface, text_rect)


def text_objects(text, color, size, font_name):
    if font_name == "roboto":
        font = pygame.font.Font("Roboto-Black.ttf", size)
    elif font_name == "lobster":
        font = pygame.font.Font("Lobster-Regular.ttf", size)
    else:
        print("ERROR: {} does not exist".format(font_name))

    text_surface = font.render(text, True, color)

    return text_surface, text_surface.get_rect()


def display_text(text, color, x=0, y=0, centered=False, size=35, font_name=default_font):
    text_surface, text_rect = text_objects(text, color, size, font_name)

    if centered == True:
        # if centered, the y argument acts as an offset
        text_rect.center = (display_width//2, display_height//2 + y)
        game_display.blit(text_surface, text_rect)
    else:
        game_display.blit(text_surface, [x, y])


def spawn_mines():
    bomb_indexes = random.sample(range(field_size), number_of_bombs)
    for index in range(field_size):
        bomb = (True if index in bomb_indexes else False)
        mines.append(Mine(index, bomb))


def start_screen():
    global field_size

    field_width_slider = Slider(display_width//2 - 300, display_height//2 + 200, minimum=3, maximum=15, value=9)
    number_of_bombs_slider = Slider(display_width//2 + 100, display_height//2 + 200, minimum=1, maximum=field_size, value=field_size//2)

    while True:
        mouse_button = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = event.button

        game_display.fill(white)

        display_text("Minesweeper", black, y=-75, centered=True, size=60)
        button("Play", display_width//2 - 50, display_height//2, 100, 50, grey, light_grey, mouse_button, action="play")

        field_width_slider.set_handle_x()
        field_width_slider.display()

        global field_width
        global number_of_bombs

        number_of_bombs_slider.maximum = field_width ** 2
        number_of_bombs_slider.set_handle_x()
        number_of_bombs_slider.display()

        field_width = int(field_width_slider.value)
        number_of_bombs = int(number_of_bombs_slider.value)
        field_size = field_width ** 2

        display_text(str(field_width), black, x=display_width//2 - 300, y=display_height//2 + 200)
        display_text(str(number_of_bombs), black, x=display_width//2 + 100, y=display_height//2 + 200)

        pygame.display.update()



def game_over_screen(win=False):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop()

        game_display.fill(white)

        if win == True:
            display_text("Congrats!!!", black, y=-100, centered=True, size=60, font_name="lobster")
            display_text("You win :)", black, y=-25, centered=True)
        else:
            display_text("BOOOOOM!!!", black, y=-100, centered=True, size=60, font_name="lobster")
            display_text("You lost :(", black, y=-25, centered=True)

        pygame.display.update()


def game_loop():
    global first_click
    first_click = False

    global mines
    mines = []

    FPS = 15
    spawn_mines()

    for mine in mines:
        mine.check_surrounding_neighbors()

    while True:
        mouse_button = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = event.button

        game_display.fill(white)

        for mine in mines:
            mine.display(mouse_button)

        pygame.display.update()

        clock.tick(FPS)


start_screen()
