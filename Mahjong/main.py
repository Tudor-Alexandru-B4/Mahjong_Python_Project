import random

from PIL import Image, ImageTk
import tkinter as tk
import os

first_index = -1
second_index = -1

tags = list()
image_list = list()
button_list = list()
tagged_buttons = list()


def select(index):
    global first_index
    global second_index

    if first_index == -1:
        first_index = index
        tagged_buttons[index][1].configure(background="blue")
    elif first_index == index:
        first_index = -1
        tagged_buttons[index][1].configure(background="white")
    elif second_index == -1:
        second_index = index
        tagged_buttons[index][1].configure(background="blue")

    if first_index != -1 and second_index != -1:
        tagged_buttons[first_index][1].configure(background="white")
        tagged_buttons[second_index][1].configure(background="white")
        if tagged_buttons[first_index][0][:2] == tagged_buttons[second_index][0][:2]:
            tagged_buttons[first_index][1].destroy()
            tagged_buttons[second_index][1].destroy()
        first_index = -1
        second_index = -1


def compute_tile_list(path, exception_tags):
    try:
        if not os.path.isdir(path):
            raise IOError("Path does not point to a directory")

        global tags
        global image_list
        global button_list
        global tagged_buttons
        button_size = 75
        # .crop((0, 5, 70, 100)).resize((button_size, button_size))
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

    except Exception as e:
        print(e)
        return None


def compute_tile_data_structure(path):
    try:
        if not os.path.isdir(path):
            raise IOError("Path does not point to a directory")

        levels = [file for file in os.listdir(path)]
        print(levels)
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

        return tile_structure

    except Exception as e:
        print(e)
        return None


def print_buttons(tile_structure, button_size):
    unused_buttons = list(button_list)
    for level in range(len(tile_structure)):
        for i in range(len(tile_structure[level]) - 1):
            for j in range(len(tile_structure[level][i]) - 1):
                char = tile_structure[level][i][j]
                if char == "@":
                    button = random.choice(unused_buttons)
                    button.lift()
                    unused_buttons.remove(button)

                    index = button_list.index(button)
                    tile_structure[level][i][j] = index
                    tile_structure[level][i][j + 1] = index
                    tile_structure[level][i + 1][j] = index
                    tile_structure[level][i + 1][j + 1] = index

                    button_list[index].place(x=j / 2 * button_size - level * 7, y=i / 2 * button_size - level * 4)


def add_buttons_to_grid():
    matrix = list(button_list)

    line = 0
    col = 0
    for i in range(len(matrix)):
        matrix[i].grid(row=line, column=col)
        line += 1
        if line == 12:
            line = 0
            col += 1


root = tk.Tk()
root.geometry('750x500')
img_dir = "tile_images"

offset = 50

compute_tile_list(img_dir, ['s', 'f'])
structure = compute_tile_data_structure("tile_arrangements")
print_buttons(structure, 75)

root.mainloop()
