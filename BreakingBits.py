import pygame
from pygame import mixer
import math
import json
import os
import time
import re
from cryptography.fernet import Fernet
from dataclasses import dataclass, asdict
from typing import List

# Constants
DEFAULT_X = -136
DEFAULT_Y = -176
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 512



# Initialization

# Fernet Initialization
key = Fernet.generate_key()
keyfile = os.path.join("data", "key.key")
if not os.path.exists(keyfile):
    with open(keyfile, "wb") as file:
        file.write(key)
else:
    with open(keyfile, "rb") as file:
        key = file.read()
fernet = Fernet(key)
# Pygame Initialization
pygame.init()
pygame.display.set_caption("Breaking Bits Tycoon")
pygame.display.set_icon(pygame.image.load("assets/logos/logo.png"))
# Mixer Initialization
mixer.init()



# Misc Functions

# Timestamp
def get_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())
# Format Amount
def format_amount(amount: float):
    lst = "_KMBtqQsSondU"
    a = amount
    for i in range(len(lst)):
        if a < 1000:
            if i == 0:
                return "$" + "{:.2f}".format(amount)
            else:
                return "$" + "{:.2f}".format(amount/(10**(i*3))) + lst[i]
        a = a/1000
# Format Grams
def format_grams(amount: float):
    lst = "g,kg,t,Mt,Gt".split(",")
    a = amount
    for i in range(len(lst)):
        if a < 1000:
            if i == 0:
                return "{:.1f}".format(amount) + lst[i]
            else:
                return "{:.1f}".format(amount/(10**(i*3))) + lst[i]
        a = a/1000            
# Font
def font(size: float, bold = False, mono = False) -> pygame.font.Font:
    if bold: return pygame.font.Font("assets/fonts/pixeloid/Pixeloid-Bold.ttf", size)
    if mono: return pygame.font.Font("assets/fonts/pixeloid/Pixeloid-Mono.ttf", size)
    return pygame.font.Font("assets/fonts/pixeloid/Pixeloid-Regular.ttf", size)



# Data Classes

# Assets
@dataclass
class Assets:
    background: str | pygame.Surface = "assets/environment/background.png"
    banner_logo: str | pygame.Surface = "assets/game/banner-outline.png"
    banner_logo_transparent: str | pygame.Surface = "assets/game/banner.png"
    x_mark: str | pygame.Surface = "assets/game/x-mark.png"
    x_mark_hover: str | pygame.Surface = "assets/game/x-mark-hover.png"
    check_mark: str | pygame.Surface = "assets/game/check-mark.png"
    check_mark_hover: str | pygame.Surface = "assets/game/check-mark-hover.png"
    dist_lock_overlay: str | pygame.Surface = "assets/game/dist-lock-overlay.png"
    speakers: List[str | pygame.Surface] = None
    upgrades: List[List[str | pygame.Surface]] = None
    # Functions
    def __post_init__(self):
        if type(self.background) == str:
            self.background = pygame.image.load(self.background)
        if type(self.banner_logo) == str:
            self.banner_logo = pygame.image.load(self.banner_logo)
        if type(self.banner_logo_transparent) == str:
            self.banner_logo_transparent = pygame.image.load(self.banner_logo_transparent)
        if type(self.x_mark) == str:
            self.x_mark = pygame.image.load(self.x_mark)
        if type(self.x_mark_hover) == str:
            self.x_mark_hover = pygame.image.load(self.x_mark_hover)
        if type(self.check_mark) == str:
            self.check_mark = pygame.image.load(self.check_mark)
        if type(self.check_mark_hover) == str:
            self.check_mark_hover = pygame.image.load(self.check_mark_hover)
        if type(self.dist_lock_overlay) == str:
            self.dist_lock_overlay = pygame.image.load(self.dist_lock_overlay)
        if self.speakers == None:
            self.speakers = ["assets/game/speaker0.png", "assets/game/speaker1.png", "assets/game/speaker2.png", "assets/game/speaker3.png"]
        self.speakers = [pygame.image.load(i) if type(i) == str else i for i in self.speakers]
        if self.upgrades == None:
            self.upgrades = [["assets/game/upgrade-1x-locked.png", "assets/game/upgrade-1x-locked-hover.png", "assets/game/upgrade-1x-unlocked.png", "assets/game/upgrade-1x-unlocked-hover.png"],
                             ["assets/game/upgrade-10x-locked.png", "assets/game/upgrade-10x-locked-hover.png", "assets/game/upgrade-10x-unlocked.png", "assets/game/upgrade-10x-unlocked-hover.png"],
                             ["assets/game/upgrade-100x-locked.png", "assets/game/upgrade-100x-locked-hover.png", "assets/game/upgrade-100x-unlocked.png", "assets/game/upgrade-100x-unlocked-hover.png"]]
        self.upgrades = [[pygame.image.load(i) if type(i) == str else i for i in x] for x in self.upgrades]
assets = Assets()
# Character
@dataclass
class Character:
    name: str
    path: str = None
    icon: str | pygame.Surface = None
    standing: str | pygame.Surface = None
    L: List[str | pygame.Surface] = None
    R: List[str | pygame.Surface] = None
    # Functions
    def __post_init__(self):
        if self.path == None:
            self.path = f"assets/characters/{self.name}"
        if self.icon == None:
            self.icon = self.path+"/icon1.png"
        if type(self.icon) == str:
            self.icon = pygame.image.load(self.icon)
        if self.standing == None:
            self.standing = self.path+"/standing.png"
        if type(self.standing) == str:
            self.standing = pygame.image.load(self.standing)
        if self.L == None:
            self.L = [f'{self.path}/{os.fsdecode(f)}' for f in os.listdir(self.path) if bool(re.match("L[0-9]{1,}.png", os.fsdecode(f)))]
        self.L = [pygame.image.load(i) if type(i) == str else i for i in self.L]
        if self.R == None:
            self.R = [f'{self.path}/{os.fsdecode(f)}' for f in os.listdir(self.path) if bool(re.match("R[0-9]{1,}.png", os.fsdecode(f)))]
        self.R = [pygame.image.load(i) if type(i) == str else i for i in self.R]
# Music
@dataclass
class Music:
    volume: int = 3
    # Functions
    def __post_init__(self):
        if self.volume < 0:
            self.volume = 0
        elif self.volume > 3:
            self.volume = 3
        self.music = mixer.Sound("assets/music/background-music.mp3")
        self.music.set_volume(1)
        self.music.play()
    def to_dict(self) -> dict:
        return asdict(self)
    def set_volume(self, v: int):
        self.volume = v
        self.music.set_volume(round(v/3, 2))
music = Music()
# Distributor
@dataclass
class Distributor:
    name: str
    multiplier: float
    price: int
    unlock: int
    icon: str
    level: int = 0
    # Functions
    def __post_init__(self):
        if type(self.icon) == str:
            self.icon = pygame.image.load(self.icon)
    def to_dict(self) -> dict:
        return asdict(self)
    def color(self) -> List[List[tuple]]:
        levels = [[(0, 192, 0), (0, 112, 0)],
                  [(0, 192, 255), (0, 112, 148)],
                  [(192, 0, 192), (112, 0, 112)]]
        if not (0 <= self.level < len(levels)):
            self.level = 0
        return levels[self.level]
# Shop
@dataclass
class Shop:
    name: str
    distributors: List[Distributor]
    give_formula: str = "{}"
    upgrade_formula: str = "{}"
    base_g_price: int = 50
    level: int = 0
    distributor: int = -1
    # Functions
    def to_dict(self) -> dict:
        return asdict(self)
    def grams_per_second(self) -> float:
        return round(eval(self.give_formula.format(x=self.level)), 1)
    def price_per_gram(self) -> float:
        return round(self.base_g_price*(1 if self.distributor == -1 else self.distributors[self.distributor].multiplier), 2)
    def amount_per_second(self) -> float:
        return round(self.grams_per_second()*self.price_per_gram(), 2)
    def upgrade_price(self, amount: int):
        total = 0
        lvl = self.level
        for _ in range(amount):
            total += round(eval(self.upgrade_formula.format(x=lvl, give=eval(self.give_formula.format(x=lvl)), default_g=self.base_g_price)), 2)
            lvl += 1
        return round(total, 2)
# Game Data
@dataclass
class GameData:
    shops: List[Shop]
    characters: List[Character]
    fps: int = 60
    run = True
    left: bool = False
    right: bool = False
    facing: str = "right"
    vel: float = 4
    diag_vel: float = vel/(math.sqrt((vel**2)*2))*vel
    walk_amt: int = 4
    walk_count: int = 0
    esc_pressed: bool = False
    space_pressed: bool = False
    in_shop_menu: bool = False
    open_shop = None
    in_main_menu: bool = False
    last_give: int = time.time_ns()
    last_save: int = time.time_ns()
    win: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Functions
    def __post_init__(self):
        for i in range(len(self.shops)):
            if type(self.shops[i]) != Shop:
                self.shops[i] = Shop(**self.shops[i])
    def to_dict(self) -> dict:
        try:
            self.shops = [s.to_dict() for s in self.shops]
            return asdict(self)
        except:
            self.shops = [Shop(**s) for s in self.shops]
    def grams_per_second(self) -> float:
        return round(sum([s.grams_per_second() for s in self.shops]), 1)
    def amount_per_second(self) -> float:
        return round(sum([s.amount_per_second() for s in self.shops]), 2)
    def open_main_menu(self):
        self.in_main_menu = True
    def close_main_menu(self):
        self.in_main_menu = False
    def open_shop_menu(self, shop: int):
        if (0 <= shop < len(self.shops)):
            self.open_shop = shop
            self.in_shop_menu = True
    def close_shop_menu(self):
        self.open_shop = None
        self.in_shop_menu = False
    def get_open_shop(self) -> Shop:
        return self.shops[self.open_shop]
# STATE
state = GameData(
    shops = [
        Shop(name="Portable Lab",
             give_formula="(10*math.sqrt(3.5*({x}-1))+3.5)",
             upgrade_formula="(1/500*({x}-1)**2+10)*({give}*{default_g})",
             base_g_price=50,
             level=1,
             distributors=[
                 Distributor(name="Jesse Pinkman",
                             multiplier=1.5,
                             price=10000000,
                             unlock=100,
                             icon="assets/distributors/jesse1.png",
                             level=0)
             ])
    ],
    characters=[
        Character(name="mista-white-1"),
        Character(name="mista-white-2"),
    ])
# Player Data
@dataclass
class PlayerData:
    global fernet, state
    # Data
    x: float = -136
    y: float = -176
    money: float = 0
    shops: List[List[int]] = None
    # Settings
    character: str | Character = "mista-white-1"
    music_volume: int = 3
    # Misc
    updated_at: str = get_timestamp()
    # Functions
    def __post_init__(self):
        # Character
        self.character = [x for x in state.characters if x.name == self.character][0]
        # Music
        music.set_volume(self.music_volume)
        # Shops
        for i in range(len(state.shops)):
            if len(self.shops) >= i:
                state.shops[i].level = self.shops[i][0]
                state.shops[i].distributor = self.shops[i][1]
            else:
                self.shops.append([state.shops[i].level, state.shops[i].distributor])
        # Save
        self.last_save = time.time_ns()
        # Offline Earnings
        offline_seconds = round(time.mktime(time.localtime()) - time.mktime(time.strptime(self.updated_at, "%Y-%m-%dT%H:%M:%S%z")))
        offline_earnings = round(state.amount_per_second()*offline_seconds*0.01, 2)
        self.money += offline_earnings
    def to_dict(self) -> dict:
        try:
            self.character = self.character.name
            return asdict(self)
        finally:
            self.character = [x for x in state.characters if x.name == self.character][0]
    def save(self):
        _file = os.path.join("data", "playerdata.xml")
        self.music_volume = music.volume
        self.updated_at = get_timestamp()
        self.last_save = time.time_ns()
        self.shops = [[x.level, x.distributor] for x in state.shops]
        with open(_file, "wb") as _f:
            _f.write(fernet.encrypt(bytes(json.dumps(self.to_dict()), "utf-8")))
    def check_save(self):
        if time.time_ns() - state.last_save >= 30e9:
            self.save()
            self.last_save = time.time_ns()
    def load() -> dict:
        _file = os.path.join("data", "playerdata.xml")
        _default = {
            "x": -136, 
            "y": -176, 
            "money": 0, 
            "shops": [[s.level, s.distributor] for s in state.shops],
            "character": 
            "mista-white-1",
            "music_volume": 3,
            "updated_at": get_timestamp()
        }
        if os.path.exists(_file):
            try:
                with open(_file, "rb") as _f:
                    return json.loads(fernet.decrypt(_f.read()))
            except:
                return _default
        else:
            with open(_file, "wb") as _f:
                _f.write(fernet.encrypt(bytes(json.dumps(_default), "utf-8")))
            return _default
    def check_give(self):
        if time.time_ns() - state.last_give >= 1e9:
            self.money += state.amount_per_second()
            state.last_give = time.time_ns()
    def upgrade(self, shop: int, amount: int):
        if not (0 <= shop < len(state.shops)):
            return
        if self.money < state.shops[shop].upgrade_price(amount):
            return
        self.money -= state.shops[shop].upgrade_price(amount)
        state.shops[shop].level += amount
    def save_and_quit(self):
        self.save()
        state.run = False
# PLAYERDATA
playerdata = PlayerData(**PlayerData.load())



# Draw Functions

# Main Menu
def drawMainMenu():
    global playerdata
    # Bg
    pygame.draw.rect(state.win, (48, 48, 48), (32, 64, 448, 384), 0, 4)
    # Logo
    state.win.blit(pygame.transform.scale(assets.banner_logo_transparent, (364, 96)), ((512-364)/2, 70))
    # Close
    if (444 <= mouse[0] <= 476) and (68 <= mouse[1] <= 100):
        state.win.blit(assets.x_mark_hover, (444, 68))
    else:
        state.win.blit(assets.x_mark, (444, 68))
    # Character Select
    charactertext = font(20).render("Select Character", True, (255, 255, 255))
    state.win.blit(charactertext, ((512-charactertext.get_rect().width)/2, 192))
    totalcharwidth = (len(state.characters)*72)-8
    xindex = (512-totalcharwidth)/2
    for c in state.characters:
        pygame.draw.rect(state.win, ((255, 255, 0) if (playerdata.character == c) else (255, 255, 255) if ((xindex <= mouse[0] <= xindex+64) and (220 <= mouse[1] <= 284)) else (192, 192, 192)), (xindex, 220, 64, 64))
        state.win.blit(pygame.transform.scale(c.icon, (60, 60)), (xindex+2, 222))
        xindex += 72
    # Music
    musictext = font(20).render("Music", True, ((255, 255, 255) if ((205.5 <= mouse[0] <= 306.5) and (324 <= mouse[1] <= 356)) else (192, 192, 192)))
    state.win.blit(musictext, ((512-musictext.get_rect().width)/2+20, 324+((32-musictext.get_rect().height)/2)))
    state.win.blit(assets.speakers[music.volume], ((512-musictext.get_rect().width)/2-20, 324))

    # Quit
    pygame.draw.rect(state.win, (255, 255, 255), (96, 392, 320, 48))
    if (100 <= mouse[0] <= 412) and (396 <= mouse[1] <= 436):
        pygame.draw.rect(state.win, (255, 0, 0), (100, 396, 312, 40))
    else:
        pygame.draw.rect(state.win, (192, 0, 0), (100, 396, 312, 40))
    q_text = font(24, bold=True).render("QUIT", True, (255, 255, 255))
    state.win.blit(q_text, ((512-q_text.get_rect().width)/2, 392+(48-q_text.get_rect().height)/2))
# Shop Menu
def drawShopMenu():
    global playerdata, state, mouse
    # Bg
    pygame.draw.rect(state.win, (48, 48, 48), (32, 72, 448, 376), 0, 4)
    # Close
    if (444 <= mouse[0] <= 476) and (68 <= mouse[1] <= 100):
        state.win.blit(assets.x_mark_hover, (444, 76))
    else:
        state.win.blit(assets.x_mark, (444, 76))
    # Upgrade 1
    upgrade1 = assets.upgrades[0][3] if (
        playerdata.money >= state.get_open_shop().upgrade_price(1) and (
            ((512-200)/2 <= mouse[0] <= (512-200)/2+64) and ((512-64)/2 <= mouse[1] <= (512-64)/2+64)
        )
    ) else assets.upgrades[0][2] if (
        playerdata.money >= state.get_open_shop().upgrade_price(1)
    ) else assets.upgrades[0][1] if (
        ((512-200)/2 <= mouse[0] <= (512-200)/2+64) and ((512-64)/2 <= mouse[1] <= (512-64)/2+64)
    ) else assets.upgrades[0][0]
    upgrade1text = font(10).render(format_amount(state.get_open_shop().upgrade_price(1)), True, ((0, 255, 0) if playerdata.money >= state.get_open_shop().upgrade_price(1) else (255, 0, 0)))
    # Upgrade 10
    upgrade10 = assets.upgrades[1][3] if (
        playerdata.money >= state.get_open_shop().upgrade_price(10) and (
            ((512-200)/2+68 <= mouse[0] <= (512-200)/2+64+68) and ((512-64)/2 <= mouse[1] <= (512-64)/2+64)
        )
    ) else assets.upgrades[1][2] if (
        playerdata.money >= state.get_open_shop().upgrade_price(10)
    ) else assets.upgrades[1][1] if (
        ((512-200)/2+68 <= mouse[0] <= (512-200)/2+64+68) and ((512-64)/2 <= mouse[1] <= (512-64)/2+64)
    ) else assets.upgrades[1][0]
    upgrade10text = font(10).render(format_amount(state.get_open_shop().upgrade_price(10)), True, ((0, 255, 0) if playerdata.money >= state.get_open_shop().upgrade_price(10) else (255, 0, 0)))
    # Upgrade 100
    upgrade100 = assets.upgrades[2][3] if (
        playerdata.money >= state.get_open_shop().upgrade_price(100) and (
            ((512-200)/2+(68*2) <= mouse[0] <= (512-200)/2+64+(68*2)) and ((512-64)/2 <= mouse[1] <= (512-64)/2+64)
        )
    ) else assets.upgrades[2][2] if (
        playerdata.money >= state.get_open_shop().upgrade_price(100)
    ) else assets.upgrades[2][1] if (
        ((512-200)/2+(68*2) <= mouse[0] <= (512-200)/2+64+(68*2)) and ((512-64)/2 <= mouse[1] <= (512-64)/2+64)
    ) else assets.upgrades[2][0]
    upgrade100text = font(10).render(format_amount(state.get_open_shop().upgrade_price(100)), True, ((0, 255, 0) if playerdata.money >= state.get_open_shop().upgrade_price(100) else (255, 0, 0)))

    # Lab info
    # Title
    titletext = font(32, bold=True).render(state.get_open_shop().name, True, (255, 255, 255))
    state.win.blit(titletext, (48, 80))
    # Level
    leveltext = font(24, bold=True).render(f"Level {state.get_open_shop().level}", True, (192, 192, 192))
    state.win.blit(leveltext, (48, 120))
    # Grams Per Second
    gpersecondtext = font(16).render(format_grams(state.get_open_shop().grams_per_second()) + "/second", True, (160, 217, 239))
    state.win.blit(gpersecondtext, (48, 152))
    
    # Upgrade Box
    # Bg
    upgrade_bg_y = 176
    pygame.draw.rect(state.win, (160, 160, 160), ((512-216)/2, upgrade_bg_y, 216, 134))
    # Upgrades Text
    upgradetext = font(24, mono=True).render("UPGRADES", True, (255, 255, 255))
    state.win.blit(upgradetext, ((512-upgradetext.get_rect().width)/2, upgrade_bg_y+4))
    # Upgrade Buttons
    state.win.blit(upgrade1, ((512-200)/2, upgrade_bg_y+38))
    state.win.blit(upgrade10, ((512-200)/2+68, upgrade_bg_y+38))
    state.win.blit(upgrade100, ((512-200)/2+(68*2), upgrade_bg_y+38))
    # Price BG
    pygame.draw.rect(state.win, (32, 32, 32), ((512-64)/2-68, upgrade_bg_y+106, 64, 24), border_radius=8)
    pygame.draw.rect(state.win, (32, 32, 32), ((512-64)/2, upgrade_bg_y+106, 64, 24), border_radius=8)
    pygame.draw.rect(state.win, (32, 32, 32), ((512-64)/2+68, upgrade_bg_y+106, 64, 24), border_radius=8)
    # Price
    state.win.blit(upgrade1text, (((512-64)/2)-68+(64-upgrade1text.get_rect().width)/2, upgrade_bg_y+112))
    state.win.blit(upgrade10text, ((512-64)/2+(64-upgrade10text.get_rect().width)/2, upgrade_bg_y+112))
    state.win.blit(upgrade100text, (((512-64)/2)+68+(64-upgrade100text.get_rect().width)/2, upgrade_bg_y+112))
    
    # Distributors
    dist_bg_x = 96
    dist_bg_y = 352
    # Bg
    pygame.draw.rect(state.win, (160, 160, 160), (dist_bg_x, dist_bg_y-34, 320, 114))
    # Title
    disttext = font(24, mono=True).render("DISTRIBUTOR", True, (255, 255, 255))
    state.win.blit(disttext, ((512-disttext.get_rect().width)/2, dist_bg_y-30))
    # Name
    nametext = font(16).render((state.get_open_shop().distributors[state.get_open_shop().distributor].name if state.get_open_shop().distributor > -1 else "N/A"), True, (64, 64, 64))
    state.win.blit(nametext, ((512-nametext.get_rect().width)/2, dist_bg_y+4))
    # Price Per Gram
    ppg = f'{format_amount(state.get_open_shop().price_per_gram())}/g'
    if state.get_open_shop().distributor >= 0:
        _d = state.get_open_shop().distributors[state.get_open_shop().distributor]
        ppg = ppg + " (" + str(int(_d.multiplier*100)) + "%)"
    ppgtext = font(12).render(ppg, True, ((64, 64, 64) if (state.get_open_shop().distributor == -1) else state.get_open_shop().distributors[state.get_open_shop().distributor].color()[1]))
    state.win.blit(ppgtext, ((512-ppgtext.get_rect().width)/2, dist_bg_y+24))
    _d = state.get_open_shop().distributor
    # Upgrade Btn
    _btn_width = 156
    if _d < len(state.get_open_shop().distributors)-1:
        # Locked
        if state.get_open_shop().level < state.get_open_shop().distributors[_d+1].unlock:
            pygame.draw.rect(state.win, (64, 64, 64), ((512-_btn_width)/2, dist_bg_y+40, _btn_width, 32), border_radius=4)
            pygame.draw.rect(state.win, (112, 112, 112), ((512-_btn_width)/2+2, dist_bg_y+42, _btn_width-4, 28), border_radius=4)
            upgradebtntxt = font(12).render(f'Unlocks lvl. {state.get_open_shop().distributors[_d+1].unlock}', True, (64, 64, 64))
            state.win.blit(upgradebtntxt, ((512-upgradebtntxt.get_rect().width)/2, dist_bg_y+42+(28-upgradebtntxt.get_rect().height)/2))
        # Not Enough Money
        elif playerdata.money < state.get_open_shop().distributors[_d+1].price:
            pygame.draw.rect(state.win, (64, 0, 0), ((512-_btn_width)/2, dist_bg_y+40, _btn_width, 32), border_radius=4)
            pygame.draw.rect(state.win, (192, 0, 0), ((512-_btn_width)/2+2, dist_bg_y+42, _btn_width-4, 28), border_radius=4)
            upgradebtntxt = font(12).render(f'Upgrade ({format_amount(state.get_open_shop().distributors[_d+1].price)})', True, (64, 0, 0))
            state.win.blit(upgradebtntxt, ((512-upgradebtntxt.get_rect().width)/2, dist_bg_y+42+(28-upgradebtntxt.get_rect().height)/2))
        # Enough Money
        else:
            pygame.draw.rect(state.win, (0, 64, 0), ((512-_btn_width)/2, dist_bg_y+40, _btn_width, 32), border_radius=4)
            if ((512-_btn_width)/2 <= mouse[0] <= (512-_btn_width)/2+_btn_width) and (dist_bg_y+40 <= mouse[1] <= dist_bg_y+40+32):
                pygame.draw.rect(state.win, (0, 192, 0), ((512-_btn_width)/2+2, dist_bg_y+42, _btn_width-4, 28), border_radius=4)
            else:
                pygame.draw.rect(state.win, (0, 160, 0), ((512-_btn_width)/2+2, dist_bg_y+42, _btn_width-4, 28), border_radius=4)
            upgradebtntxt = font(12).render(f'Upgrade ({format_amount(state.get_open_shop().distributors[_d+1].price)})', True, (0, 64, 0))
            state.win.blit(upgradebtntxt, ((512-upgradebtntxt.get_rect().width)/2, dist_bg_y+42+(28-upgradebtntxt.get_rect().height)/2))
    # Max
    else:
        pygame.draw.rect(state.win, (64, 64, 64), ((512-_btn_width)/2, dist_bg_y+40, _btn_width, 32), border_radius=4)
        pygame.draw.rect(state.win, (112, 112, 112), ((512-_btn_width)/2+2, dist_bg_y+42, _btn_width-4, 28), border_radius=4)
        upgradebtntxt = font(12).render("MAX", True, (64, 64, 64))
        state.win.blit(upgradebtntxt, ((512-upgradebtntxt.get_rect().width)/2, dist_bg_y+42+(28-upgradebtntxt.get_rect().height)/2))
    # Active Box
    if _d == -1:
        pygame.draw.rect(state.win, (128, 128, 128), (dist_bg_x+4, dist_bg_y+4, 72, 72))
        pygame.draw.rect(state.win, (192, 192, 192), (dist_bg_x+8, dist_bg_y+8, 64, 64))
        etext = font(16).render("EMPTY", True, (64, 64, 64))
        state.win.blit(etext, ((72-etext.get_rect().width)/2+dist_bg_x+4, (72-etext.get_rect().height)/2+dist_bg_y+4))
    else:
        _dist = state.get_open_shop().distributors[_d]
        pygame.draw.rect(state.win, _dist.color()[0], (dist_bg_x+4, dist_bg_y+4, 72, 72))
        pygame.draw.rect(state.win, _dist.color()[1], (dist_bg_x+8, dist_bg_y+8, 64, 64))
        state.win.blit(_dist.icon, (dist_bg_x+8, dist_bg_y+8))
    # Next Box
    if _d < len(state.get_open_shop().distributors)-1:
        _dist = state.get_open_shop().distributors[_d+1]
        pygame.draw.rect(state.win, _dist.color()[0], (dist_bg_x+244, dist_bg_y+4, 72, 72))
        pygame.draw.rect(state.win, _dist.color()[1], (dist_bg_x+248, dist_bg_y+8, 64, 64))
        state.win.blit(_dist.icon, (dist_bg_x+248, dist_bg_y+8))
        if state.get_open_shop().level < _dist.unlock:
            state.win.blit(assets.dist_lock_overlay, (dist_bg_x+244, dist_bg_y+4))



# Game Window
def redrawGameWindow():
    global state
    # Background
    state.win.blit(assets.background, (playerdata.x, playerdata.y))
    # Character Left
    if state.left:
        # Walk Count
        if state.walk_count+1 > state.walk_amt*len(playerdata.character.L):
            state.walk_count = 0
        state.win.blit(playerdata.character.L[(state.walk_count//state.walk_amt)], (224, 192))
    # Character Right
    elif state.right:
        if state.walk_count+1 > state.walk_amt*len(playerdata.character.R):
            state.walk_count = 0
        state.win.blit(playerdata.character.R[(state.walk_count//state.walk_amt)], (224, 192))
    # Character Standing
    else:
        state.win.blit(playerdata.character.standing, (224, 192))
    # Header
    if not state.in_main_menu:
        # Banner Logo
        state.win.blit(assets.banner_logo, (0, 0))
        # Balance
        moneyoutline = font(24).render(format_amount(playerdata.money), True, (0, 0, 0))
        moneywidth = moneyoutline.get_rect().width
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                if a == 0 and b == 0: continue
                state.win.blit(moneyoutline, (496-moneywidth+a, 16+b))
        moneytext = font(24).render(format_amount(playerdata.money), True, (0, 255, 0))
        state.win.blit(moneytext, (496-moneywidth, 16))
        # Per Second
        persectext = font(16).render(format_amount(state.amount_per_second()) + "/sec", True, (0, 0, 0))
        state.win.blit(persectext, (496-persectext.get_rect().width, 48))
    # Game Surfaces
    if not state.in_main_menu and not state.in_shop_menu:
        # RV Button
        if (-272 <= playerdata.x <= 0) and (-112 <= playerdata.y <= 0):
            pygame.draw.rect(state.win, (0, 0, 0), (128, 424, 256, 80), border_radius=4)
            pygame.draw.rect(state.win, (48, 48, 48), (130, 426, 252, 76))
            rvnametext = font(16, bold=True).render("Portable Lab", True, (255, 255, 255))
            state.win.blit(rvnametext, (138, 430))
            rvlvltext = font(16, bold=True).render(f"Lvl. {state.shops[0].level}", True, (255, 255, 255))
            state.win.blit(rvlvltext, (374-rvlvltext.get_rect().width, 430))
            rvopentext = font(16).render("Press SPACE to open", True, (255, 255, 255))
            state.win.blit(rvopentext, ((512-rvopentext.get_rect().width)/2, 426+(76/2)-(rvnametext.get_rect().height/2)+(rvopentext.get_rect().height/2)))
        
    # Draw Main menu
    if state.in_main_menu:
        drawMainMenu()
    elif state.in_shop_menu:
        drawShopMenu()
    pygame.display.update()



# Main Loop

while state.run:
    # Check give or save
    playerdata.check_give()
    playerdata.check_save()

    pygame.time.delay(math.floor(1000/state.fps))

    # Event Handling

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playerdata.save_and_quit()
        # Screen Clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Main Menu
            if state.in_main_menu and (444 <= mouse[0] <= 476) and (68 <= mouse[1] <= 100):
                state.close_main_menu()
            elif state.in_main_menu and (205.5 <= mouse[0] <= 306.5) and (324 <= mouse[1] <= 356):
                if music.volume <= 2:
                    music.set_volume(music.volume + 1)
                else:
                    music.set_volume(0)
            elif state.in_main_menu and (100 <= mouse[0] <= 412) and (396 <= mouse[1] <= 436):
                playerdata.save_and_quit()
            elif state.in_main_menu:
                xindex = (512-(len(state.characters)*72)-8)/2
                for c in state.characters:
                    if ((xindex <= mouse[0] <= xindex+64) and (204 <= mouse[1] <= 268)):
                        playerdata.character = c
                        break
                    xindex += 72
            # Shop Menu
            elif state.in_shop_menu and (444 <= mouse[0] <= 476) and (76 <= mouse[1] <= 108):
                state.close_shop_menu()
            elif state.in_shop_menu and ((512-200)/2 <= mouse[0] <= (512-200)/2+64) and ((512-64)/2 <= mouse[1] <= (512-64)/2+64):
                playerdata.upgrade(state.open_shop, 1)
            elif state.in_shop_menu and ((512-200)/2+68 <= mouse[0] <= (512-200)/2+64+68) and ((512-64)/2 <= mouse[1] <= (512-64)/2+64):
                playerdata.upgrade(state.open_shop, 10)
            elif state.in_shop_menu and ((512-200)/2+(68*2) <= mouse[0] <= (512-200)/2+64+(68*2)) and ((512-64)/2 <= mouse[1] <= (512-64)/2+64):
                playerdata.upgrade(state.open_shop, 100)
            elif state.in_shop_menu and ((512-156)/2 <= mouse[0] <= (512-156)/2+156) and (352+40 <= mouse[1] <= 352+40+32):
                if playerdata.money >= state.get_open_shop().distributors[state.get_open_shop().distributor+1].price:
                    playerdata.money -= state.get_open_shop().distributors[state.get_open_shop().distributor+1].price
                    state.get_open_shop().distributor += 1



    #  Keys

    mouse = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    # Escape
    if keys[pygame.K_ESCAPE]:
        if not state.esc_pressed:
            state.esc_pressed = True
            if not state.in_main_menu and not state.in_shop_menu:
                state.open_main_menu()
            elif state.in_main_menu:
                state.close_main_menu()
            elif state.in_shop_menu:
                state.close_shop_menu()
    else:
        state.esc_pressed = False
    # Space
    if keys[pygame.K_SPACE]:
        if not state.space_pressed:
            state.space_pressed = True
            if not state.in_main_menu:
                if (-272 <= playerdata.x <= 0) and (-112 <= playerdata.y <= 0):
                    state.open_shop_menu(0)
    else:
        state.space_pressed = False



    # Movement
    if not (state.in_main_menu or state.in_shop_menu):
        # Left
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if playerdata.x+state.vel <= -32:
                playerdata.x += (state.diag_vel if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_DOWN] or keys[pygame.K_s]) else state.vel)
                state.walk_count += 1
            else:
                playerdata.x = -32
            state.left = True
            state.right = False
            state.facing = "left"
        # Right
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if playerdata.x-state.vel >= -992:
                playerdata.x -= (state.diag_vel if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_DOWN] or keys[pygame.K_s]) else state.vel)
                state.walk_count += 1
            else:
                playerdata.x = -992
            state.left = False
            state.right = True
            state.facing = "right"
        # Up
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if playerdata.y+state.vel <= -64:
                playerdata.y += (state.diag_vel if (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]) else state.vel)
                if not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                    state.walk_count += 1
            else:
                playerdata.y = -64
            if not state.left and not state.right:
                state.left = bool(state.facing == "left")
                state.right = bool(state.facing == "right")
        # Down
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if playerdata.y-state.vel >= -1024:
                playerdata.y -= (state.diag_vel if (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]) else state.vel)
                if not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                    state.walk_count += 1
            else:
                playerdata.y = -1024
            if not state.left and not state.right:
                state.left = bool(state.facing == "left")
                state.right = bool(state.facing == "right")
        # None
        if not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_DOWN] or keys[pygame.K_s]):
            state.left = False
            state.right = False
            state.walk_count = 0

    # Draw
    redrawGameWindow()



pygame.quit()
