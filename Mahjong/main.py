""" Mahjong

by Gherghe Tudor-Alexandru B4

This script allows the user to play mahjong
The arrangements and tiles can be changed/customized

This script requires that 'tkinter' and 'PIL'(pillow) be installed within the Python
environment you are running this script in.
"""
import random
from PIL import Image, ImageTk
import tkinter as tk
import os

HIGHLIGHT_COLOR = "yellow"
SELECTED_COLOR = "blue"
SELECTABLE_COLOR = "yellow green"
NORMAL_COLOR = "white"
BACKGROUND_COLOR = "azure4"

first_index = -1
second_index = -1

tags = list()
image_list = list()
button_list = list()
tagged_buttons = list()
structure = list()
structure_index = list()
BUTTON_SIZE = 75

hints_used = None
shuffles_used = None
selectable_tile_types = dict()
removed_pcs = 0
impossible_arrangement = False

win_screen = None
lose_screen = None
hint_image = None
shuffle_image = None
restart_image = None
exit_image = None


def free_on_top(index):
    """ Checks if the given index has a tile on top of it.
    :param index: int
        the index of the corresponding tile.
    :return: bool
        True if there is a tile on top, False otherwise.
    """

    level, i, j = structure_index[index]
    if level == len(structure) - 1:
        return True

    if structure[level + 1][i][j] == '#' and structure[level + 1][i][j + 1] == '#' and \
            structure[level + 1][i + 1][j] == '#' and structure[level + 1][i + 1][j + 1] == '#':
        return True

    return False


def free_to_east(index):
    """ Checks if the given index has a tile to the left of it.
    :param index: int
        the index of the corresponding tile.
    :return: bool
        True if there is a tile to the left, False otherwise.
    """

    level, i, j = structure_index[index]
    if j == len(structure[level][i]) - 2:
        return True

    if structure[level][i][j + 2] == '#' and structure[level][i + 1][j + 2] == '#':
        return True

    return False


def free_to_west(index):
    """ Checks if the given index has a tile to the right of it.
    :param index: int
        the index of the corresponding tile.
    :return: bool
        True if there is a tile to the right, False otherwise.
    """

    level, i, j = structure_index[index]
    if j == 0:
        return True

    if structure[level][i][j - 1] == '#' and structure[level][i + 1][j - 1] == '#':
        return True

    return False


def free_tile_space(index):
    """ Empties the 2 fine grid spaces that correspond to the given index that memorizes
        the placement of the tiles in the tile structure.
    :param index: int
        the index of the corresponding tile.
    :return: None
    """

    level, i, j = structure_index[index]
    structure[level][i][j] = '#'
    structure[level][i][j + 1] = '#'
    structure[level][i + 1][j] = '#'
    structure[level][i + 1][j + 1] = '#'


def update_selectable():
    """ Searches and changes the background color of tiles that can be selected.
        Also updates the global variable selectable_tile_types and checks if there are any available moves.
        If moves are not available show_lose_screen is called.
        If moves are not available but the player just shuffled shuffle_tiles is called.

    :return: None
    """

    global selectable_tile_types
    global impossible_arrangement
    selectable_tile_types = dict()
    lost = True

    for index in range(len(button_list)):
        if button_list[index] != '#' and (free_on_top(index) and (free_to_east(index) or free_to_west(index))):
            button_list[index]["background"] = SELECTABLE_COLOR
            button_tag = tagged_buttons[index][0][:2]
            if button_tag not in selectable_tile_types.keys():
                selectable_tile_types[button_tag] = 1
            else:
                lost = False
                selectable_tile_types[button_tag] += 1

    if lost is True and removed_pcs < 144:
        if impossible_arrangement is True and removed_pcs > 2:
            shuffle_tiles()
        else:
            show_lose_screen()
    impossible_arrangement = False


def select(index):
    """ Manages everything that is composed of selecting tiles.
        Memorizes the last two selected tiles using globals first_index and second_index.
        Changes the background color of tiles corresponding of their state (selected or not).
        When two tiles are selected checks if they are the same, if true remove_pcs is called.
        Also calls update_selected when tiles enter the not selected state.

    :param index: int
        the index of the corresponding tile.
    :return: None
    """

    global first_index
    global second_index

    if not (free_on_top(index) and (free_to_east(index) or free_to_west(index))):
        return

    if first_index == -1:
        first_index = index
        tagged_buttons[index][1].configure(background=SELECTED_COLOR)
    elif first_index == index:
        first_index = -1
        tagged_buttons[index][1].configure(background=NORMAL_COLOR)
        update_selectable()
    elif second_index == -1:
        second_index = index
        tagged_buttons[index][1].configure(background=SELECTED_COLOR)

    if first_index != -1 and second_index != -1:
        tagged_buttons[first_index][1].configure(background=NORMAL_COLOR)
        tagged_buttons[second_index][1].configure(background=NORMAL_COLOR)
        if tagged_buttons[first_index][0][:2] == tagged_buttons[second_index][0][:2]:
            remove_pcs()
        first_index = -1
        second_index = -1
        update_selectable()


def remove_pcs():
    """ Removes the tiles corresponding to globals first_index and second_index.
        Updates global button_list by replacing corresponding tiles with character '#'.
        Updates global removed_pcs, incrementing it by 2.
        Also checks if there are no more tiles left and if true show_win_screen is called.

    :return: None
    """

    free_tile_space(first_index)
    free_tile_space(second_index)
    button_list[first_index] = '#'
    button_list[second_index] = '#'
    tagged_buttons[first_index][1].destroy()
    tagged_buttons[second_index][1].destroy()

    global removed_pcs
    removed_pcs += 2
    if removed_pcs == len(tagged_buttons):
        show_win_screen()


def compute_tile_list(img_dir, exception_tags):
    """ Creates the tile buttons.
        Loads tile images from directory.
        Initializes global tags to contain all available tile prefixes.
        Creates copies of tiles(if not exception) and initializes globals button_list and tagged_buttons.
        Also sets the size of global structure_index.

    :param img_dir: string
        path to directory containing tile images.
    :param exception_tags: list of strings
        list of strings that correspond to tiles prefixes that should not have copies done.
    :return: None
    """

    try:
        if not os.path.isdir(img_dir):
            raise IOError("Path does not point to a directory")

        global tags
        global image_list
        global button_list
        global tagged_buttons
        global structure_index
        global BUTTON_SIZE
        image_list = [ImageTk.PhotoImage(Image.open(os.path.join(img_dir, imgName)).resize((BUTTON_SIZE, BUTTON_SIZE)))
                      for imgName in os.listdir(img_dir)]
        tags = [str(imgName).split(".")[0] for imgName in os.listdir(img_dir)]

        for i in range(len(image_list)):
            if tags[i][0] in exception_tags:
                copies = 1
            else:
                copies = 4

            for j in range(copies):
                button_list.append(tk.Button(root, image=image_list[i],
                                             command=lambda index=len(button_list): select(index),
                                             height=BUTTON_SIZE, width=BUTTON_SIZE, relief='sunken', border="0"))
                tagged_buttons.append((tags[i], button_list[-1]))

        structure_index = [0] * len(button_list)

    except Exception as e:
        print(e)
        exit()


def compute_tile_data_structure(path):
    """ Loads a random level from the directory and initializes the 2 fine grid global structure.

    :param path: string
        path to directory containing txt files that give the level structure for the tiles.
    :return: None
    """
    try:
        if not os.path.isdir(path):
            raise IOError("Path does not point to a directory")

        levels = [file for file in os.listdir(path)]
        selected_level = random.choice(levels)

        tile_structure = []
        fine_matrix = []
        for line in open(os.path.join(path, selected_level)):
            if not line.startswith("="):
                fine_matrix.append(list(line.split("\n")[0]))
            else:
                tile_structure.append(list(fine_matrix))
                fine_matrix = []

        if fine_matrix:
            tile_structure.append(fine_matrix)

        global structure
        structure = tile_structure

    except Exception as e:
        print(e)
        exit()


def draw_buttons():
    """ Puts the existing buttons on screen corresponding to the global variable structure.
        Possible tile places are given by variable structure, but tiles are randomised.
        Also sets global impossible_arrangement to True and calls update_selected.

    :return: None
    """

    global impossible_arrangement

    unused_buttons = [existing_button for existing_button in button_list if existing_button != '#']
    for level in range(len(structure)):
        for i in range(len(structure[level]) - 1):
            for j in range(len(structure[level][i]) - 1):
                char = structure[level][i][j]
                if char == "@":
                    button = random.choice(unused_buttons)
                    button.lift()
                    unused_buttons.remove(button)

                    index = button_list.index(button)
                    structure_index[index] = (level, i, j)
                    structure[level][i][j] = str(index)
                    structure[level][i][j + 1] = str(index)
                    structure[level][i + 1][j] = str(index)
                    structure[level][i + 1][j + 1] = str(index)

                    button_list[index].place(x=j / 2 * BUTTON_SIZE, y=i / 2 * BUTTON_SIZE)

    impossible_arrangement = True
    update_selectable()


def give_hint():
    """ Highlights a possible move and increments the global hints_used counter.

    :return: None
    """

    global hints_used
    hints_used.set(hints_used.get() + 1)

    for key, value in selectable_tile_types.items():
        if value > 1:
            count = 0
            for index in range(len(button_list)):
                if button_list[index] != '#' and tagged_buttons[index][0][:2] == key \
                        and (free_on_top(index) and (free_to_east(index) or free_to_west(index))):
                    button_list[index]["background"] = HIGHLIGHT_COLOR
                    count += 1

                if count == 2:
                    return


def shuffle_tiles():
    """ Shuffle tiles and increments the global shuffles_used counter.
        This is achieved by resetting the remaining tiles int the global structure to character '@'
        and calling draw_buttons.

    :return: None
    """

    global first_index
    global second_index
    global lose_screen
    global impossible_arrangement
    global shuffles_used

    if impossible_arrangement is False:
        shuffles_used.set(shuffles_used.get() + 1)

    if lose_screen is not None:
        lose_screen.destroy()

    first_index = -1
    second_index = -1

    for button in button_list:
        if button != '#':
            button["background"] = NORMAL_COLOR
            button.forget()

    for level in range(len(structure)):
        for i in range(len(structure[level])):
            for j in range(len(structure[level][i])):
                if structure[level][i][j] != '#':
                    structure[level][i][j] = '@'

    draw_buttons()


def restart_game():
    """ Resets game to default state.
        This is achieved by setting globals to default values and calling init_game.

    :return: None
    """

    global first_index
    global second_index
    global tags
    global image_list
    global button_list
    global tagged_buttons
    global structure
    global structure_index
    global hints_used
    global shuffles_used
    global selectable_tile_types
    global removed_pcs
    global impossible_arrangement
    global win_screen
    global lose_screen
    global hint_image
    global shuffle_image
    global restart_image
    global exit_image

    for index in range(len(button_list)):
        if button_list[index] != '#':
            button_list[index].destroy()

    if win_screen is not None:
        win_screen.destroy()

    if lose_screen is not None:
        lose_screen.destroy()

    first_index = -1
    second_index = -1
    tags = list()
    image_list = list()
    button_list = list()
    tagged_buttons = list()
    structure = list()
    structure_index = list()
    hints_used.set(0)
    shuffles_used.set(0)
    selectable_tile_types = dict()
    removed_pcs = 0
    impossible_arrangement = False
    win_screen = None
    lose_screen = None
    hint_image = None
    shuffle_image = None
    restart_image = None
    exit_image = None
    init_game()


def exit_game():
    """ Closes application.

    :return: None
    """

    exit()


def compute_menu_buttons():
    """ Creates and places all menu buttons.
        Buttons: 'hint', 'shuffle', 'reset', 'exit'.

    :return: None
    """

    global hint_image
    hint_image = ImageTk.PhotoImage(Image.open("menu_images/hint.png")
                                    .resize((BUTTON_SIZE, BUTTON_SIZE)))
    hint_button = tk.Button(root, image=hint_image, command=give_hint,
                            height=BUTTON_SIZE, width=BUTTON_SIZE, relief='raised')
    hint_button.place(x=BUTTON_SIZE * 22, y=BUTTON_SIZE * 2)

    global hints_used
    hint_label = tk.Label(root, textvariable=hints_used)
    hint_label.place(x=BUTTON_SIZE * 23, y=BUTTON_SIZE * 3)

    global shuffle_image
    shuffle_image = ImageTk.PhotoImage(Image.open("menu_images/shuffle.png")
                                       .resize((BUTTON_SIZE, BUTTON_SIZE)))
    shuffle_button = tk.Button(root, image=shuffle_image, command=shuffle_tiles,
                               height=BUTTON_SIZE, width=BUTTON_SIZE, relief='raised')
    shuffle_button.place(x=BUTTON_SIZE * 22, y=BUTTON_SIZE * 4)

    global shuffles_used
    shuffle_label = tk.Label(root, textvariable=shuffles_used)
    shuffle_label.place(x=BUTTON_SIZE * 23, y=BUTTON_SIZE * 5)

    global restart_image
    restart_image = ImageTk.PhotoImage(Image.open("menu_images/restart.png")
                                       .resize((BUTTON_SIZE, BUTTON_SIZE)))
    restart_button = tk.Button(root, image=restart_image, command=restart_game,
                               height=BUTTON_SIZE, width=BUTTON_SIZE, relief='raised')
    restart_button.place(x=BUTTON_SIZE * 22, y=BUTTON_SIZE * 6)

    global exit_image
    exit_image = ImageTk.PhotoImage(Image.open("menu_images/exit.png")
                                    .resize((BUTTON_SIZE, BUTTON_SIZE)))
    exit_button = tk.Button(root, image=exit_image, command=exit_game,
                            height=BUTTON_SIZE, width=BUTTON_SIZE, relief='raised')
    exit_button.place(x=BUTTON_SIZE * 22, y=BUTTON_SIZE * 8)


def show_lose_screen():
    """ Creates and places the lose screen.
        Contains: test and button: 'shuffle', 'restart', 'quit'.

    :return: None
    """

    global lose_screen
    global shuffle_image
    global restart_image

    lose_screen = tk.Canvas(root, height="200", background=SELECTABLE_COLOR)
    lose_screen.create_text(190, 50, text="YOU LOST", fill="black", font='Helvetica 15 bold')

    tk.Button(lose_screen, image=shuffle_image, command=shuffle_tiles,
              height=BUTTON_SIZE, width=BUTTON_SIZE, relief='raised').place(x=25, y=125)

    tk.Button(lose_screen, image=restart_image, command=restart_game,
              height=BUTTON_SIZE, width=BUTTON_SIZE, relief='raised').place(x=150, y=125)

    tk.Button(lose_screen, image=exit_image, command=exit_game,
              height=BUTTON_SIZE, width=BUTTON_SIZE, relief='raised').place(x=275, y=125)

    lose_screen.place(x=BUTTON_SIZE * 10, y=BUTTON_SIZE * 5)


def show_win_screen():
    """ Creates and places the win screen.
        Contains: test and button: 'restart', 'quit'.

    :return: None
    """

    global win_screen
    global restart_image

    win_screen = tk.Canvas(root, height="200", background=SELECTABLE_COLOR)
    win_screen.create_text(190, 50, text="YOU WON", fill="black", font='Helvetica 15 bold')

    tk.Button(win_screen, image=restart_image, command=restart_game,
              height=BUTTON_SIZE, width=BUTTON_SIZE, relief='raised').place(x=80, y=125)

    tk.Button(win_screen, image=exit_image, command=exit_game,
              height=BUTTON_SIZE, width=BUTTON_SIZE, relief='raised').place(x=220, y=125)

    win_screen.place(x=BUTTON_SIZE * 10, y=BUTTON_SIZE * 5)


def init_game():
    """ Initializes global variables hints_used and shuffles_used and calls.
        compute_menu_buttons, compute_tile_list, compute_tile_data_structure and draw_buttons.

    :return: None
    """

    global hints_used
    global shuffles_used

    hints_used = tk.IntVar()
    shuffles_used = tk.IntVar()
    hints_used.set(0)
    shuffles_used.set(0)
    compute_menu_buttons()
    compute_tile_list("tile_images", ['s', 'f'])
    compute_tile_data_structure("tile_arrangements")
    draw_buttons()


root = tk.Tk()
root.geometry('750x500')
root.configure(background=BACKGROUND_COLOR)
init_game()
root.mainloop()
