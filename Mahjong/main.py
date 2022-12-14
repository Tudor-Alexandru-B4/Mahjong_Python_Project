import random

from PIL import Image, ImageTk
import tkinter as tk
import os

selected_color = "blue"
selectable_color = "green"
normal_color = "white"
background_color = "azure4"

first_index = -1
second_index = -1

tags = list()
image_list = list()
button_list = list()
tagged_buttons = list()
structure = list()
structure_index = list()
button_size = 75

shuffle_image = None
restart_image = None


def free_on_top(index):
    level, i, j = structure_index[index]
    if level == len(structure) - 1:
        return True

    if structure[level + 1][i][j] == '#' and structure[level + 1][i][j + 1] == '#' and \
            structure[level + 1][i + 1][j] == '#' and structure[level + 1][i + 1][j + 1] == '#':
        return True

    return False


def free_to_east(index):
    level, i, j = structure_index[index]
    if j == len(structure[level][i]) - 2:
        return True

    if structure[level][i][j + 2] == '#' and structure[level][i + 1][j + 2] == '#':
        return True

    return False


def free_to_west(index):
    level, i, j = structure_index[index]
    if j == 0:
        return True

    if structure[level][i][j - 1] == '#' and structure[level][i + 1][j - 1] == '#':
        return True

    return False


def free_tile_space(index):
    level, i, j = structure_index[index]
    structure[level][i][j] = '#'
    structure[level][i][j + 1] = '#'
    structure[level][i + 1][j] = '#'
    structure[level][i + 1][j + 1] = '#'


def update_selectable():
    for index in range(len(button_list)):
        if button_list[index] != '#' and (free_on_top(index) and (free_to_east(index) or free_to_west(index))):
            button_list[index]["background"] = selectable_color


def select(index):
    global first_index
    global second_index

    if not (free_on_top(index) and (free_to_east(index) or free_to_west(index))):
        return

    if first_index == -1:
        first_index = index
        tagged_buttons[index][1].configure(background=selected_color)
    elif first_index == index:
        first_index = -1
        tagged_buttons[index][1].configure(background=normal_color)
        update_selectable()
    elif second_index == -1:
        second_index = index
        tagged_buttons[index][1].configure(background=selected_color)

    if first_index != -1 and second_index != -1:
        tagged_buttons[first_index][1].configure(background=normal_color)
        tagged_buttons[second_index][1].configure(background=normal_color)
        if tagged_buttons[first_index][0][:2] == tagged_buttons[second_index][0][:2]:
            free_tile_space(first_index)
            free_tile_space(second_index)
            button_list[first_index] = '#'
            button_list[second_index] = '#'
            tagged_buttons[first_index][1].destroy()
            tagged_buttons[second_index][1].destroy()
        first_index = -1
        second_index = -1
        update_selectable()


def compute_tile_list(img_dir, exception_tags):
    try:
        if not os.path.isdir(img_dir):
            raise IOError("Path does not point to a directory")

        global tags
        global image_list
        global button_list
        global tagged_buttons
        global structure_index
        global button_size
        image_list = [ImageTk.PhotoImage(Image.open(os.path.join(img_dir, imgName)).resize((button_size, button_size)))
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
                                             height=button_size, width=button_size, relief='sunken', border="0"))
                tagged_buttons.append((tags[i], button_list[-1]))

        structure_index = [0] * len(button_list)

    except Exception as e:
        print(e)
        return None


def compute_tile_data_structure(path):
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
        return None


def draw_buttons():
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

                    button_list[index].place(x=j / 2 * button_size, y=i / 2 * button_size)

    update_selectable()


def shuffle_tiles():
    global first_index
    global second_index
    first_index = -1
    second_index = -1

    for button in button_list:
        if button != '#':
            button["background"] = normal_color
            button.forget()

    for level in range(len(structure)):
        for i in range(len(structure[level])):
            for j in range(len(structure[level][i])):
                if structure[level][i][j] != '#':
                    structure[level][i][j] = '@'

    draw_buttons()


def restart_game():
    global first_index
    global second_index
    global tags
    global image_list
    global button_list
    global tagged_buttons
    global structure
    global structure_index
    global shuffle_image
    global restart_image

    for index in range(len(button_list)):
        if button_list[index] != '#':
            button_list[index]["background"] = background_color

    first_index = -1
    second_index = -1
    tags = list()
    image_list = list()
    button_list = list()
    tagged_buttons = list()
    structure = list()
    structure_index = list()
    shuffle_image = None
    restart_image = None

    init_game()


def compute_menu_buttons():
    global shuffle_image
    shuffle_image = ImageTk.PhotoImage(Image.open("menu_images/shuffle.png")
                                                              .resize((button_size, button_size)))
    shuffle_button = tk.Button(root, image=shuffle_image, command=shuffle_tiles,
                               height=button_size, width=button_size, relief='raised')
    shuffle_button.place(x=button_size * 22, y=button_size * 2)

    global restart_image
    restart_image = ImageTk.PhotoImage(Image.open("menu_images/restart.png")
                                       .resize((button_size, button_size)))
    restart_button = tk.Button(root, image=restart_image, command=restart_game,
                               height=button_size, width=button_size, relief='raised')
    restart_button.place(x=button_size * 22, y=button_size * 4)


def init_game():
    compute_menu_buttons()
    compute_tile_list("tile_images", ['s', 'f'])
    compute_tile_data_structure("tile_arrangements")
    draw_buttons()


root = tk.Tk()
root.geometry('750x500')
root.configure(background=background_color)
init_game()
root.mainloop()
