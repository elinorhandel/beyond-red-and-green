"""
make_plates.py - Creates the dotted color test images ("plates").

Run this ONCE on your own computer with:  python make_plates.py
It saves PNG files into the images/ folder. main.py only displays those
saved images, so this file is NOT part of the website and is not imported
by main.py. (It uses libraries the deployed site doesn't need.)

ADVANCED TECHNIQUES (not covered in class), explained:

1. Pillow (PIL) draws pictures in Python. Image.new() makes a blank
   picture, ImageDraw lets us draw circles on it, and ImageFont lets us
   draw a number in a large font.

2. NumPy does math on whole lists of numbers at once. Here each color is
   a group of 3 numbers (red, green, blue), and NumPy lets us multiply a
   color by a 3x3 "matrix" (a grid of numbers) in one step.

3. How the hidden number works: we first draw the number in white on a
   black "mask" picture that the user never sees. Then we scatter many
   random dots on the plate. If a dot's center lands on a white pixel of
   the mask, it is a "figure" dot (part of the number); otherwise it is a
   "background" dot. Figure dots and background dots get different colors.

4. How the colors are chosen (the science part): scientists (Machado,
   Oliveira & Fernandes, 2009) published 3x3 matrices that turn a color
   into how it looks to someone with a type of color blindness:
     - protanopia   (red-green, missing red cones)
     - deuteranopia (red-green, missing green cones)
     - tritanopia   (blue-yellow, missing blue cones)
   Each matrix has a "blind direction": a way of changing a color that
   that matrix cannot see. We start with a background color and push it
   along the blind direction to get the figure color. A person with normal
   vision sees two clearly different colors, but a person with that type
   of color blindness sees almost the same color, so the number vanishes.
   For total color blindness (seeing only light and dark), we instead
   pick two colors with the SAME brightness but different hues.

5. To stop people from finding the number by brightness alone, every dot
   is randomly made a bit lighter or darker.

6. "Control" plates use a big brightness difference that everyone can see,
   so they check that the user understands the test and their screen works.

DISCLAIMER: These are homemade screening images, not a medical test.
"""
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FINAL_SIZE = 400        # width/height of the saved image in pixels
DRAW_SCALE = 2          # draw twice as big, then shrink, for smooth edges
CANVAS = FINAL_SIZE * DRAW_SCALE
PLATE_RADIUS = CANVAS * 0.47
OUTPUT_FOLDER = "images"

# Simulation matrices from Machado et al. (2009), full severity.
# They work on "linear" RGB values (explained in srgb_to_linear below).
PROTAN = np.array([[0.152286, 1.052583, -0.204868],
                   [0.114503, 0.786281, 0.099216],
                   [-0.003882, -0.048116, 1.051998]])
DEUTAN = np.array([[0.367322, 0.860646, -0.227968],
                   [0.280085, 0.672501, 0.047413],
                   [-0.011820, 0.042940, 0.968881]])
TRITAN = np.array([[1.255528, -0.076749, -0.178779],
                   [-0.078411, 0.930809, 0.147602],
                   [0.004733, 0.691367, 0.303900]])
# How bright each of red, green, blue looks to the human eye.
LUMINANCE = np.array([0.2126, 0.7152, 0.0722])

# Every plate the site uses:
# (file name, hidden number, test type, color recipe, background color)
PLATE_LIST = [
    ("red_green_1.png", "12", "red-green", "control", (225, 200, 150)),
    ("red_green_2.png", "8", "red-green", "protan", (150, 160, 90)),
    ("red_green_3.png", "29", "red-green", "deutan", (120, 160, 100)),
    ("red_green_4.png", "74", "red-green", "protan", (130, 165, 110)),
    ("red_green_5.png", "6", "red-green", "deutan", (150, 165, 95)),
    ("blue_yellow_1.png", "15", "blue-yellow", "control", (180, 200, 230)),
    ("blue_yellow_2.png", "3", "blue-yellow", "tritan", (150, 175, 120)),
    ("blue_yellow_3.png", "42", "blue-yellow", "tritan", (170, 160, 150)),
    ("blue_yellow_4.png", "9", "blue-yellow", "tritan", (140, 170, 160)),
    ("blue_yellow_5.png", "57", "blue-yellow", "tritan", (165, 170, 110)),
    ("total_1.png", "23", "total", "control", (200, 205, 210)),
    ("total_2.png", "4", "total", "mono", (180, 130, 140)),
    ("total_3.png", "86", "total", "mono", (120, 170, 140)),
    ("total_4.png", "7", "total", "mono", (140, 140, 190)),
    ("total_5.png", "35", "total", "mono", (190, 150, 100)),
]


def srgb_to_linear(color: np.ndarray) -> np.ndarray:
    """Convert 0-255 screen colors to 0-1 'linear light' values.

    Screens store colors on a curved scale; the simulation math only
    works on the straight (linear) scale, so we convert first.
    """
    c = color / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(color: np.ndarray) -> np.ndarray:
    """Convert 0-1 linear light values back to 0-255 screen colors."""
    c = np.clip(color, 0, 1)
    c = np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
    return np.round(c * 255)


def blind_direction(matrix: np.ndarray) -> np.ndarray:
    """Find the color change that a simulation matrix can barely see.

    numpy.linalg.svd breaks the matrix into pieces; its last row of
    'vt' is the direction the matrix shrinks the most (the blind spot).
    """
    _, _, vt = np.linalg.svd(matrix)
    return vt[-1]


def equal_brightness_direction(color: np.ndarray) -> np.ndarray:
    """Find a hue change that keeps brightness exactly the same.

    np.cross gives a direction at a right angle to both LUMINANCE (so
    brightness doesn't change) and the color itself (so it changes hue
    rather than just becoming more or less gray).
    """
    direction = np.cross(LUMINANCE, color)
    return direction / np.linalg.norm(direction)


def largest_safe_step(base: np.ndarray, direction: np.ndarray) -> float:
    """Return how far we can move along direction and stay a real color.

    Tries both signs (+ and -) and keeps whichever allows the bigger step,
    with a little margin so dot brightness changes stay in range.
    """
    best_step = 0.0
    for sign in [1, -1]:
        step = 0.0
        while step < 1.0:
            moved = base + sign * (step + 0.01) * direction
            if np.any(moved < 0.03) or np.any(moved > 0.8):
                break
            step += 0.01
        if step > abs(best_step):
            best_step = sign * step
    return best_step


def pick_colors(recipe: str, background: tuple) -> tuple:
    """Return (figure_color, background_color) in linear RGB."""
    base = srgb_to_linear(np.array(background, dtype=float))
    if recipe == "control":
        # Large brightness difference: everyone should see the number.
        return base * 0.25 + np.array([0.12, 0.03, 0.0]), base
    if recipe == "mono":
        direction = equal_brightness_direction(base)
    else:
        matrix = {"protan": PROTAN, "deutan": DEUTAN, "tritan": TRITAN}
        direction = blind_direction(matrix[recipe])
    step = largest_safe_step(base, direction)
    return base + step * direction, base


def make_number_mask(number: str) -> Image.Image:
    """Draw the number in white on a black image the size of the plate."""
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    draw = ImageDraw.Draw(mask)
    font = ImageFont.load_default(size=int(CANVAS * 0.55))
    draw.text((CANVAS / 2, CANVAS / 2), number, fill=255, font=font,
              anchor="mm", stroke_width=int(CANVAS * 0.02), stroke_fill=255)
    return mask


def scatter_dots(rng: random.Random) -> list:
    """Place non-overlapping random dots inside the plate circle.

    Returns a list of (x, y, radius). Big dots are placed first, then
    smaller ones fill the gaps. NumPy checks a new dot against all the
    existing dots at once, which is much faster than a Python loop.
    """
    center = CANVAS / 2
    xs, ys, rs = [], [], []
    gap = CANVAS * 0.004
    for max_radius, tries in [(CANVAS * 0.028, 4000), (CANVAS * 0.018, 9000),
                              (CANVAS * 0.011, 15000)]:
        for _ in range(tries):
            radius = rng.uniform(max_radius * 0.6, max_radius)
            x = rng.uniform(center - PLATE_RADIUS, center + PLATE_RADIUS)
            y = rng.uniform(center - PLATE_RADIUS, center + PLATE_RADIUS)
            if np.hypot(x - center, y - center) + radius > PLATE_RADIUS:
                continue
            if xs:
                dist = np.hypot(np.array(xs) - x, np.array(ys) - y)
                if np.any(dist < np.array(rs) + radius + gap):
                    continue
            xs.append(x)
            ys.append(y)
            rs.append(radius)
    return list(zip(xs, ys, rs))


def draw_plate(number: str, recipe: str, background: tuple,
               seed: int) -> Image.Image:
    """Create one finished plate image."""
    rng = random.Random(seed)   # same seed -> same picture every run
    figure_color, background_color = pick_colors(recipe, background)
    mask = make_number_mask(number)
    plate = Image.new("RGB", (CANVAS, CANVAS), (255, 255, 255))
    draw = ImageDraw.Draw(plate)
    for x, y, radius in scatter_dots(rng):
        on_number = mask.getpixel((int(x), int(y))) > 128
        color = figure_color if on_number else background_color
        # Random lightness change hides any brightness clue.
        color = color * rng.uniform(0.7, 1.25)
        r, g, b = linear_to_srgb(color).astype(int)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                     fill=(int(r), int(g), int(b)))
    return plate.resize((FINAL_SIZE, FINAL_SIZE), Image.LANCZOS)


def main() -> None:
    """Draw every plate in PLATE_LIST and save it to the images folder."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    for seed, (file_name, number, _, recipe, background) in \
            enumerate(PLATE_LIST):
        plate = draw_plate(number, recipe, background, seed)
        plate.save(os.path.join(OUTPUT_FOLDER, file_name), optimize=True)
        print("Saved", file_name)


if __name__ == "__main__":
    main()
