import math
import os
import path
import pygame


####### Constants #######

CAPTION = 'Elemental Gauge Visualizer'
CNVW, CNVH = 800, 600
ELMS = 65
AURS = 250
LOGW = 250
FPS = 60
# TODO font sizes
# TODO size of buttons
# TODO change selected button appearance

# Elements order depends on files order in ELEMENTS path
ANEMO, CRYO, DENDRO, ELECTRO, GEO, HYDRO, PYRO = 0, 1, 2, 3, 4, 5, 6

ELEMENT_COLOR = {
    ANEMO: (163, 243, 202),
    GEO: (250, 182, 50),
    ELECTRO: (175, 142, 193),
    DENDRO: (165, 200, 59),
    HYDRO: (76, 194, 241),
    PYRO: (239, 121, 56),
    CRYO: (159, 214, 227)
}

REACTION_COLOR = {
    'Vaporize': (254, 203, 99),
    'Overload': (251, 136, 155),
    'Superconduct': (196, 187, 245),
    'Melt': (255, 202, 105),
    'Crystalize': (215, 184, 130),
    'Swirl': (163, 243, 202),
    'Electro-Charged': (212, 162, 255),
    'Burning': (233, 152, 8),
    'Bloom': (76, 194, 241),
    'Quicken': (175, 142, 193)
}

AURA_TAX = 0.8

REACTION_MODIFIER = {
    'normal': 1,
    'forward': 2,
    'reverse': 0.5,
    'Swirl': 0.5,
    'Crystalize': 0.5
}

REACTION_CONSUMER = {
    'Electro-Charged': 0.4
}


####### Global variables #######

canvas = 0
[A1_button, B2_button, C4_button] = [False] * 3
element_imgs = []
reaction_text_list = []
running = True
fps = 0
aura_list = []
electro_charged, frame_electro_charged = False, 0
burning, frame_burning = False, 0


####### Classes #######

class FPSDisplay:
    trueFPS = 0

    def __init__(self):
        self.clock = pygame.time.Clock()

    def render(self):
        FPSDisplay.trueFPS = self.clock.get_fps()


class ReactionText:

    def __init__(self, reaction):
        self.text = reaction
        self.color = REACTION_COLOR[reaction] if reaction in REACTION_COLOR \
            else (255, 255, 255)


class Aura:
    def __init__(self, aura, U, decay_U, element, aura_count):
        if element == ANEMO or element == GEO:
            self.aura = False
        else:
            self.aura = aura
        self.U = U * AURA_TAX
        self.decay_U = decay_U
        self.element = element
        self.aura_count = aura_count

    def decay(self):
        if self.aura:
            if self.decay_U == 'A':
                self.U -= 1 / (decay_rate(1) * FPSDisplay.trueFPS)
            elif self.decay_U == 'B':
                self.U -= 1 / (decay_rate(2) * FPSDisplay.trueFPS)
            elif self.decay_U == 'C':
                self.U -= 1 / (decay_rate(4) * FPSDisplay.trueFPS)
            if burning:
                self.U -= 1 / (decay_rate(2) * FPSDisplay.trueFPS)
        if self.U <= 0:
            self.U = 0
            self.aura = False

    def check_burning_status(self):
        if self.element == DENDRO and burning:
            self.burning = True


####### Functions #######

# Logical functions

def decay_rate(gauge):
    if gauge in [1, 2, 4]:
        return (2.5 * gauge + 7) / (AURA_TAX * gauge)


def get_decay_rate_notation():
    if A1_button:
        return 1, 'A'
    elif B2_button:
        return 2, 'B'
    elif C4_button:
        return 4, 'C'


def consume_gauge(modifier, aura_slot):
    if A1_button:
        aura_list[aura_slot].U -= 1 * modifier
    elif B2_button:
        aura_list[aura_slot].U -= 2 * modifier
    elif C4_button:
        aura_list[aura_slot].U -= 4 * modifier


def double_aura(aura1, aura2):
    if aura1.element == HYDRO and aura2 == ELECTRO \
            or aura1.element == ELECTRO and aura2 == HYDRO \
            or aura1.element == PYRO and aura2 == DENDRO \
            or aura1.element == DENDRO and aura2 == PYRO:
        U, d = get_decay_rate_notation()
        if aura1.aura_count in [1, 2]:
            aura_list.append(Aura(True, U, d, aura2, 3 - aura1.aura_count))


def anemo_trigger(slot):
    if aura_list[slot].element in [ELECTRO, HYDRO, PYRO, CRYO]:
        consume_gauge(REACTION_MODIFIER['Swirl'], slot)
        record_to_log('Swirl')


def geo_trigger(slot):
    if aura_list[slot].element in [ELECTRO, HYDRO, PYRO, CRYO]:
        consume_gauge(REACTION_MODIFIER['Crystalize'], slot)
        record_to_log('Crystalize')


def electro_trigger():
    global electro_charged, frame_electro_charged
    for i in [-1, -2]:
        if aura_list[i].element == PYRO:
            consume_gauge(REACTION_MODIFIER['normal'], i)
            record_to_log('Overload')
        if aura_list[i].element == CRYO:
            consume_gauge(REACTION_MODIFIER['normal'], i)
            record_to_log('Superconduct')
        if aura_list[i].element == DENDRO:
            record_to_log('Intensified')
    for i in [-1, -2]:
        if aura_list[i].element == HYDRO:
            double_aura(aura_list[i], ELECTRO)
            record_to_log('Electro-Charged')
            aura_list[-1].U -= REACTION_CONSUMER['Electro-Charged']
            aura_list[-2].U -= REACTION_CONSUMER['Electro-Charged']
            frame_electro_charged = 0
            electro_charged = True
            break


def hydro_trigger():
    global electro_charged, frame_electro_charged
    for i in [-1, -2]:
        if aura_list[i].element == PYRO:
            consume_gauge(REACTION_MODIFIER['forward'], i)
            record_to_log('Vaporize')
        if aura_list[i].element == DENDRO:
            record_to_log('Bloom')
    for i in [-1, -2]:
        if aura_list[i].element == ELECTRO:
            double_aura(aura_list[i], HYDRO)
            record_to_log('Electro-Charged')
            aura_list[-1].U -= REACTION_CONSUMER['Electro-Charged']
            aura_list[-2].U -= REACTION_CONSUMER['Electro-Charged']
            frame_electro_charged = 0
            electro_charged = True
            break


def pyro_trigger():
    global burning, frame_burning
    for i in [-1, -2]:
        if aura_list[i].element == CRYO:
            consume_gauge(REACTION_MODIFIER['forward'], i)
            record_to_log('Melt')
        if aura_list[i].element == HYDRO:
            consume_gauge(REACTION_MODIFIER['reverse'], i)
            record_to_log('Vaporize')
        if aura_list[i].element == ELECTRO:
            consume_gauge(REACTION_MODIFIER['normal'], i)
            record_to_log('Overload')
    for i in [-1, -2]:
        if aura_list[i].element == DENDRO:
            double_aura(aura_list[i], PYRO)
            record_to_log('Burning')
            frame_burning = 0
            burning = True
            break


def cryo_trigger(slot):
    if aura_list[slot].element == ELECTRO:
        consume_gauge(REACTION_MODIFIER['normal'], slot)
        record_to_log('Superconduct')
    if aura_list[slot].element == PYRO:
        consume_gauge(REACTION_MODIFIER['reverse'], slot)
        record_to_log('Melt')


def dendro_trigger():
    global burning, frame_burning
    for i in [-1, -2]:
        if aura_list[i].element == PYRO:
            double_aura(aura_list[i], DENDRO)
            record_to_log('Burning')
            frame_burning = 0
            burning = True
            break
    for i in [-1, -2]:
        if aura_list[i].element == HYDRO:
            record_to_log('Bloom')
        if aura_list[i].element == ELECTRO:
            record_to_log('Quicken')


def electro_charged_tick():
    global electro_charged, frame_electro_charged
    if electro_charged:
        if frame_electro_charged == 5 * round(FPSDisplay.trueFPS / 5) and len(aura_list) >= 2:
            frame_electro_charged = 0
            aura_list[-1].U -= REACTION_CONSUMER['Electro-Charged']
            aura_list[-2].U -= REACTION_CONSUMER['Electro-Charged']
            record_to_log('Electro-Charged')
        if aura_list[-1].U <= 0 or aura_list[-2].U <= 0:
            electro_charged = False
            frame_electro_charged = (
                5 * round(FPSDisplay.trueFPS / 5)) + 1


def burning_tick():
    global frame_burning, burning
    if burning:
        if frame_burning == FPS / 4 and len(aura_list) >= 2:
            frame_burning = 0
            record_to_log('Burning')
            # reapply 1A Pyro every tick
            for i in [-1, -2]:
                if aura_list[-3 - i].element == DENDRO \
                        and aura_list[i].element == PYRO \
                        and aura_list[i].U <= AURA_TAX * 1:
                    aura_list[i] = Aura(True, 1, 'A', PYRO, 3 + i)
                    break
        if aura_list[-1].U <= 0 or aura_list[-2].U <= 0:
            burning = False
            frame_burning = FPS / 4 + 1


def apply_aura(element):
    # return True or False based on 'Has any aura been applied or refreshed?'

    # if no aura, then apply an element
    if not aura_list[-1].aura:
        U, d = get_decay_rate_notation()
        aura_list.append(Aura(True, U, d, element, 1))
        return True

    # if there a same aura existed, then refresh it
    for i in [-1, -2]:
        if element == aura_list[i].element and aura_list[i].aura:
            if A1_button and aura_list[i].U < 1 * AURA_TAX:
                aura_list[i] = Aura(
                    True, 1, aura_list[i].decay_U, element, aura_list[i].aura_count)
            elif B2_button and aura_list[i].U < 2 * AURA_TAX:
                aura_list[i] = Aura(
                    True, 2, aura_list[i].decay_U, element, aura_list[i].aura_count)
            elif C4_button and aura_list[i].U < 4 * AURA_TAX:
                aura_list[i] = Aura(
                    True, 4, aura_list[i].decay_U, element, aura_list[i].aura_count)
            return True

    return False


def update_aura_list():
    for i in range(len(aura_list)):
        if aura_list[i].aura:
            display_aura(aura_list[i])
            aura_list[i].decay()
            display_gauge(aura_list[i])


def update_frames():
    global frame_electro_charged, frame_burning
    frame_electro_charged += 1
    frame_burning += 1


def update_burning_status():
    for aura in aura_list:
        aura.check_burning_status()


# Appearance functions

def aura_display_size(aura_count):
    if aura_count == 1:
        if len(aura_list) == 2:  # 1 aura - middle
            return (CNVW - LOGW - AURS) / 2, CNVH / 2.8 - AURS / 2 - 30
        if len(aura_list) == 3:  # 2 auras, 1st - left
            return (CNVW - LOGW) / 2 - AURS, CNVH / 2.8 - AURS / 2 - 30
    if aura_count == 2:  # 2 auras, 2nd - right
        return (CNVW - LOGW) / 2, CNVH / 2.8 - AURS / 2 - 30


def record_to_log(reaction_text):
    reaction_text_list.insert(0, ReactionText(reaction_text))


def display_aura(aura):
    if aura.aura:
        img = pygame.transform.scale(element_imgs[aura.element], (AURS, AURS))
        canvas.blit(img, aura_display_size(aura.aura_count))


def display_gauge(aura):
    if aura.aura:
        pygame.draw.rect(canvas, (ELEMENT_COLOR[aura.element]), pygame.Rect(
            0, CNVH - (100 * aura.aura_count), aura.U * (CNVW / 4), 30))


def reaction_trigger(mouse_x, mouse_y):
    if CNVH - ELMS < mouse_y < CNVH:
        for i in range(2):
            slot = - i - 1
            if ELMS * ANEMO < mouse_x < ELMS * (ANEMO + 1):
                anemo_trigger(slot)
            if ELMS * GEO < mouse_x < ELMS * (GEO + 1):
                geo_trigger(slot)
            if ELMS * CRYO < mouse_x < ELMS * (CRYO + 1):
                cryo_trigger(slot)
        if ELMS * DENDRO < mouse_x < ELMS * (DENDRO + 1):
            dendro_trigger()
        if ELMS * PYRO < mouse_x < ELMS * (PYRO + 1):
            pyro_trigger()
        if ELMS * ELECTRO < mouse_x < ELMS * (ELECTRO + 1):
            electro_trigger()
        if ELMS * HYDRO < mouse_x < ELMS * (HYDRO + 1):
            hydro_trigger()


def click_button(mouse_x, mouse_y):
    global A1_button, B2_button, C4_button
    x = CNVW - 300
    y = CNVH - 50
    w = 45
    h = 40
    if x < mouse_x < x + w:
        if y < mouse_y < y + h:
            A1_button, B2_button, C4_button = True, False, False
    x = CNVW - 200
    if x < mouse_x < x + w:
        if y < mouse_y < y + h:
            A1_button, B2_button, C4_button = False, True, False
    x = CNVW - 100
    if x < mouse_x < x + w:
        if y < mouse_y < y + h:
            A1_button, B2_button, C4_button = False, False, True


def click(mouse_x, mouse_y):
    click_button(mouse_x, mouse_y)
    for element in range(len(element_imgs)):
        if ELMS * element < mouse_x < ELMS * (element + 1) \
                and CNVH - ELMS < mouse_y < CNVH:
            if apply_aura(element) == False:
                reaction_trigger(mouse_x, mouse_y)


def reaction_log():
    if len(reaction_text_list) > 0:
        for i in range(len(reaction_text_list)):
            font = pygame.font.Font(path.FONT_JAJP, 22)
            font = font.render(
                reaction_text_list[i].text, True, reaction_text_list[i].color)
            canvas.blit(font, (CNVW - LOGW, (CNVH - LOGW) - 30 * i + 15))


def draw():
    # element buttons
    for i in range(len(element_imgs)):
        canvas.blit(pygame.transform.scale(
            element_imgs[i], (ELMS, ELMS)), (ELMS * i, CNVH - ELMS))
    # Update aura
    update_aura_list()
    # Unit value tics
    for i in range(2):
        i += 1
        for x in range(5):
            pygame.draw.rect(canvas, (0, 0, 0), pygame.Rect(
                x * (CNVW / 4) - 2, CNVH - (100 * i), 2, 30))
            if x == 4:
                pygame.draw.rect(canvas, (0, 0, 0), pygame.Rect(
                    x * (CNVW / 4) - 3, CNVH - (100 * i), 2, 30))
        for x in range(40):
            pygame.draw.rect(canvas, (0, 0, 0), pygame.Rect(
                x * (CNVW / 40) - 2, CNVH - (100 * i), 1, 20))
    # Units buttons
    font1A = pygame.font.Font(path.FONT_JAJP, 30)
    font1A.set_underline(A1_button)
    img = font1A.render("1A", True, (255, 255, 255))
    canvas.blit(img, (CNVW - 300, CNVH - 50))
    font2B = pygame.font.Font(path.FONT_JAJP, 30)
    font2B.set_underline(B2_button)
    img = font2B.render("2B", True, (255, 255, 255))
    canvas.blit(img, (CNVW - 200, CNVH - 50))
    font4C = pygame.font.Font(path.FONT_JAJP, 30)
    font4C.set_underline(C4_button)
    img = font4C.render("4C", True, (255, 255, 255))
    canvas.blit(img, (CNVW - 100, CNVH - 50))
    reaction_log()


def remove_inactive_auras():
    global aura_list
    aura_list = [aura_list[i] for i in range(
        len(aura_list)) if aura_list[i].aura or aura_list[i].aura_count == 3]


def trim_reaction_text_list():
    global reaction_text_list
    reaction_text_list = [reaction_text_list[i]
                          for i in range(len(reaction_text_list)) if i <= 12]


####### Actual program #######

# initialize

A1_button = True
for fileName in os.listdir(path.ELEMENTS):
    element_imgs.append(pygame.image.load(path.ELEMENTS + fileName))
pygame.init()
canvas = pygame.display.set_mode((CNVW, CNVH))
pygame.display.set_caption(CAPTION)
favicon = pygame.image.load(path.FAVICON)
pygame.display.set_icon(favicon)
fps = FPSDisplay()
aura_list.append(Aura(False, 1, 'A', 7, 3))

# game loop

running = True
while running:
    update_frames()

    canvas.fill((0, 0, 0))
    draw()

    update_burning_status()

    electro_charged_tick()
    burning_tick()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click(mouse_x, mouse_y)

    remove_inactive_auras()
    trim_reaction_text_list()

    fps.render()
    pygame.display.update()
    fps.clock.tick(FPS)
