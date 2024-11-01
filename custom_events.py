from itertools import count
import pygame as pg

counter = count(start=1, step=1)

CHANGE_GRID_TYPE: int = pg.USEREVENT + counter.__next__()
CHANGE_GRID_COLOR: int = pg.USEREVENT + counter.__next__()
CHANGE_GRID_SIZE: int = pg.USEREVENT + counter.__next__()
CHANGE_MAP_SPECIFIC: int = pg.USEREVENT + counter.__next__()
MOVE_MAP: int = pg.USEREVENT + counter.__next__()
CHANGE_MAP_NEXT: int = pg.USEREVENT + counter.__next__()
CHANGE_MAP_PREVIOUS: int = pg.USEREVENT + counter.__next__()
MAP_CYCLE_STATE: int = pg.USEREVENT + counter.__next__()
ADD_TOKEN: int = pg.USEREVENT + counter.__next__()
PLAY_SOUND: int = pg.USEREVENT + counter.__next__()
STOP_SOUND: int = pg.USEREVENT + counter.__next__()
VOLUME_UP: int = pg.USEREVENT + counter.__next__()
VOLUME_DOWN: int = pg.USEREVENT + counter.__next__()
