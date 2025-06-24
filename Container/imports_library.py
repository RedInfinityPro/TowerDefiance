import time
import math
import random
import pygame
import sys
import pygame_menu

from pygame_menu import themes
from perlin_noise import PerlinNoise
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import *
current_time = time.time()
random.seed(current_time)