import math
import os
import path
import pygame

CAPTION = 'Aura Visualizer'
CNVW, CNVH = 800, 600
ELMS = 65
AURS = 250
LOGW = 250
FPS = 60
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
    'EC': 0.4
}


def decay_rate(gauge):
    if gauge in [1, 2, 4]:
        return (2.5 * gauge + 7) / (AURA_TAX * gauge)
    return -1


A1 = True
B2 = False
C4 = False
aura_list = []
reaction_text_list = []

element_imgs = []
for fileName in os.listdir(path.ELEMENTS):
    element_imgs.append(pygame.image.load(path.ELEMENTS + fileName))

pygame.init()
canvas = pygame.display.set_mode((CNVW, CNVH))
pygame.display.set_caption(CAPTION)
favicon = pygame.image.load(path.FAVICON)
pygame.display.set_icon(favicon)


def aura_display_size(aura_count):
    if aura_count == 1:
        if len(aura_list) == 2:  # 1 aura - middle
            return (CNVW - LOGW - AURS) / 2, CNVH / 2.8 - AURS / 2 - 30
        if len(aura_list) == 3:  # 2 auras, 1st - left
            return (CNVW - LOGW) / 2 - AURS, CNVH / 2.8 - AURS / 2 - 30
    if aura_count == 2:  # 2 auras, 2nd - right
        return (CNVW - LOGW) / 2, CNVH / 2.8 - AURS / 2 - 30
    return -1, -1


class ReactionText:
    def __init__(self, _reaction):
        self.text = _reaction
        self.color = REACTION_COLOR[_reaction] if _reaction in REACTION_COLOR \
            else (255, 255, 255)


class Aura:
    def __init__(self, _aura, U, decay_U, element, aura_count):
        if element == ANEMO or element == GEO:
            self.aura = False
        else:
            self.aura = _aura
        self.U = U * AURA_TAX
        self.decay_U = decay_U
        self.element = element
        self.aura_count = aura_count
        self.burning = False

    def aura_display(self):
        if self.aura:
            img = pygame.transform.scale(
                element_imgs[self.element], (AURS, AURS))
            canvas.blit(img, aura_display_size(self.aura_count))

    def decay(self):
        if self.aura:
            if self.decay_U == 'A':
                self.U -= 1 / (decay_rate(1) * FPSDisplay.trueFPS)
            elif self.decay_U == 'B':
                self.U -= 1 / (decay_rate(2) * FPSDisplay.trueFPS)
            elif self.decay_U == 'C':
                self.U -= 1 / (decay_rate(4) * FPSDisplay.trueFPS)
            if self.burning:
                self.U -= 1 / (decay_rate(2) * FPSDisplay.trueFPS)
        if self.U <= 0:
            self.U = 0
            self.aura = False

    def gauge_display(self):
        if self.aura:
            pygame.draw.rect(canvas, (ELEMENT_COLOR[self.element]), pygame.Rect(
                0, CNVH - (100 * self.aura_count), self.U * (CNVW / 4), 30))
            font = pygame.font.Font(path.FONT_JAJP, 25)
            img = font.render(
                str(math.ceil(self.U * 100) / 100) + self.decay_U, True,
                (255, 255, 255))
            canvas.blit(img, (10, CNVH - (100 * self.aura_count) - 40))

    def dendro_decay_while_burning(self):
        if self.element == DENDRO and burning:
            self.burning = True


def reaction(mousex, mousey):
    if CNVH - ELMS < mousey < CNVH:
        for i in range(2):
            slot = - i - 1
            if ELMS * ANEMO < mousex < ELMS * ANEMO + ELMS:
                anemo_trigger(slot)
            if ELMS * GEO < mousex < ELMS * GEO + ELMS:
                geo_trigger(slot)
            if ELMS * CRYO < mousex < ELMS * CRYO + ELMS:
                cryo_trigger(slot)
        if ELMS * DENDRO < mousex < ELMS * DENDRO + ELMS:
            dendro_trigger()
        if ELMS * PYRO < mousex < ELMS * PYRO + ELMS:
            pyro_trigger()
        if ELMS * ELECTRO < mousex < ELMS * ELECTRO + ELMS:
            electro_trigger()
        if ELMS * HYDRO < mousex < ELMS * HYDRO + ELMS:
            hydro_trigger()


def anemo_trigger(slot):
    if aura_list[slot].element in [ELECTRO, HYDRO, PYRO, CRYO]:
        consume_gauge(REACTION_MODIFIER['Swirl'], slot)
        reaction_text_list.insert(0, ReactionText('Swirl'))


def geo_trigger(slot):
    if aura_list[slot].element in [ELECTRO, HYDRO, PYRO, CRYO]:
        consume_gauge(REACTION_MODIFIER['Crystalize'], slot)
        reaction_text_list.insert(0, ReactionText('Crystalize'))


def cryo_trigger(slot):
    if aura_list[slot].element == ELECTRO:
        consume_gauge(REACTION_MODIFIER['normal'], slot)
        reaction_text_list.insert(0, ReactionText('Superconduct'))
    if aura_list[slot].element == PYRO:
        consume_gauge(REACTION_MODIFIER['reverse'], slot)
        reaction_text_list.insert(0, ReactionText('Melt'))


def electro_trigger():
    global EC, frameEC
    for i in [-1, -2]:
        if aura_list[i].element == PYRO:
            consume_gauge(REACTION_MODIFIER['normal'], i)
            reaction_text_list.insert(0, ReactionText('Overload'))
        if aura_list[i].element == CRYO:
            consume_gauge(REACTION_MODIFIER['normal'], i)
            reaction_text_list.insert(0, ReactionText('Superconduct'))
        if aura_list[i].element == DENDRO:
            reaction_text_list.insert(0, ReactionText('Intensified'))
    for i in [-1, -2]:
        if aura_list[i].element == HYDRO:
            double_aura(aura_list[i], ELECTRO)
            reaction_text_list.insert(0, ReactionText('Electro-Charged'))
            aura_list[-1].U -= REACTION_CONSUMER['EC']
            aura_list[-2].U -= REACTION_CONSUMER['EC']
            frameEC = 0
            EC = True
            break


def dendro_trigger():
    global burning, frame_burning
    for i in [-1, -2]:
        if aura_list[i].element == PYRO:
            double_aura(aura_list[i], DENDRO)
            reaction_text_list.insert(0, ReactionText('Burning'))
            frame_burning = 0
            burning = True
            break
    for i in [-1, -2]:
        if aura_list[i].element == HYDRO:
            reaction_text_list.insert(0, ReactionText('Bloom'))
        if aura_list[i].element == ELECTRO:
            reaction_text_list.insert(0, ReactionText('Quicken'))


def hydro_trigger():
    global EC, frameEC
    for i in [-1, -2]:
        if aura_list[i].element == PYRO:
            consume_gauge(REACTION_MODIFIER['forward'], i)
            reaction_text_list.insert(0, ReactionText('Vaporize'))
        if aura_list[i].element == DENDRO:
            reaction_text_list.insert(0, ReactionText('Bloom'))
    for i in [-1, -2]:
        if aura_list[i].element == ELECTRO:
            double_aura(aura_list[i], HYDRO)
            reaction_text_list.insert(0, ReactionText('Electro-Charged'))
            aura_list[-1].U -= REACTION_CONSUMER['EC']
            aura_list[-2].U -= REACTION_CONSUMER['EC']
            frameEC = 0
            EC = True
            break


def pyro_trigger():
    global burning, frame_burning
    for i in [-1, -2]:
        if aura_list[i].element == CRYO:
            consume_gauge(REACTION_MODIFIER['forward'], i)
            reaction_text_list.insert(0, ReactionText('Melt'))
        if aura_list[i].element == HYDRO:
            consume_gauge(REACTION_MODIFIER['reverse'], i)
            reaction_text_list.insert(0, ReactionText('Vaporize'))
        if aura_list[i].element == ELECTRO:
            consume_gauge(REACTION_MODIFIER['normal'], i)
            reaction_text_list.insert(0, ReactionText('Overload'))
    for i in [-1, -2]:
        if aura_list[i].element == DENDRO:
            double_aura(aura_list[i], PYRO)
            reaction_text_list.insert(0, ReactionText('Burning'))
            frame_burning = 0
            burning = True
            break


def consume_gauge(modifier, aura_slot):
    if A1:
        aura_list[aura_slot].U -= 1 * modifier
    elif B2:
        aura_list[aura_slot].U -= 2 * modifier
    elif C4:
        aura_list[aura_slot].U -= 4 * modifier


def get_decay_rate():
    if A1:
        return 1, 'A'
    if B2:
        return 2, 'B'
    return 4, 'C'


def double_aura(aura1, aura2):
    if aura1.element == HYDRO and aura2 == ELECTRO \
            or aura1.element == ELECTRO and aura2 == HYDRO \
            or aura1.element == PYRO and aura2 == DENDRO \
            or aura1.element == DENDRO and aura2 == PYRO:
        U, d = get_decay_rate()
        if aura1.aura_count in [1, 2]:
            aura_list.append(Aura(True, U, d, aura2, 3 - aura1.aura_count))


def EC_tick():
    global frameEC, EC
    if EC:
        if frameEC == 5 * round(FPSDisplay.trueFPS / 5) and len(aura_list) >= 2:
            frameEC = 0
            aura_list[-1].U -= REACTION_CONSUMER['EC']
            aura_list[-2].U -= REACTION_CONSUMER['EC']
            reaction_text_list.insert(0, ReactionText('Electro-Charged'))
        if aura_list[-1].U <= 0 or aura_list[-2].U <= 0:
            EC = False
            frameEC = (5 * round(FPSDisplay.trueFPS / 5)) + 1


def burning_tick():
    global frame_burning, burning
    if burning:
        if frame_burning == FPS / 4 and len(aura_list) >= 2:
            frame_burning = 0
            reaction_text_list.insert(0, ReactionText('Burning'))
            # reapply Pyro every tick
            for i in [-1, -2]:
                if aura_list[-3 - i].element == DENDRO \
                        and aura_list[i].U <= 2 * AURA_TAX \
                        and aura_list[i].element == PYRO:
                    aura_list[i] = Aura(True, 2, 'B', PYRO, 3 + i)
                    break
        if aura_list[-1].U <= 0 or aura_list[-2].U <= 0:
            burning = False
            frame_burning = (FPS / 4) + 1


# initial
aura_list.append(Aura(False, 1, 'A', 7, 3))


def click_unit():
    global A1, B2, C4
    x = CNVW - 300
    y = CNVH - 50
    w = 45
    h = 40
    if x < mouse_x < x + w:
        if y < mouse_y < y + h:
            A1, B2, C4 = True, False, False
    x = CNVW - 200
    if x < mouse_x < x + w:
        if y < mouse_y < y + h:
            A1, B2, C4 = False, True, False
    x = CNVW - 100
    if x < mouse_x < x + w:
        if y < mouse_y < y + h:
            A1, B2, C4 = False, False, True


def click(_mouse_x, _mouse_y):
    global A1, B2, C4
    click_unit()
    for element in range(len(element_imgs)):
        if ELMS * element < _mouse_x < ELMS * (element + 1):
            if CNVH - ELMS < _mouse_y < CNVH:
                # if no aura, then apply an element
                if not aura_list[-1].aura:
                    if A1:
                        aura_list.append(Aura(True, 1, 'A', element, 1))
                    elif B2:
                        aura_list.append(Aura(True, 2, 'B', element, 1))
                    elif C4:
                        aura_list.append(Aura(True, 4, 'C', element, 1))
                # extending an aura with same element, or occur reaction
                else:
                    no_reaction = False
                    for i in [-1, -2]:
                        if element == aura_list[i].element and aura_list[i].aura is True:
                            if A1 and aura_list[i].U < 0.8:
                                aura_list[i] = Aura(
                                    True, 1, aura_list[i].decay_U, element, aura_list[i].aura_count)
                            elif B2 and aura_list[i].U < 2.6:
                                aura_list[i] = Aura(
                                    True, 2, aura_list[i].decay_U, element, aura_list[i].aura_count)
                            elif C4 and aura_list[i].U < 3.2:
                                aura_list[i] = Aura(
                                    True, 4, aura_list[i].decay_U, element, aura_list[i].aura_count)
                            no_reaction = True
                            break
                    # reaction
                    if no_reaction is False:
                        reaction(_mouse_x, _mouse_y)


def reaction_log():
    if len(reaction_text_list) > 0:
        for i in range(len(reaction_text_list)):
            font = pygame.font.Font(path.FONT_JAJP, 22)
            font = font.render(
                reaction_text_list[i].text, True, reaction_text_list[i].color)
            canvas.blit(font, (CNVW - LOGW,
                               (CNVH - LOGW) - 30 * i + 15))


def draw():
    # element buttons
    for i in range(len(element_imgs)):
        canvas.blit(pygame.transform.scale(
            element_imgs[i], (ELMS, ELMS)), (ELMS * i, CNVH - ELMS))
    # Update aura
    for i in range(len(aura_list)):
        if aura_list[i].aura:
            aura_list[i].aura_display()
            aura_list[i].decay()
            aura_list[i].gauge_display()
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
    font1A.set_underline(A1)
    font2B = pygame.font.Font(path.FONT_JAJP, 30)
    font2B.set_underline(B2)
    font4C = pygame.font.Font(path.FONT_JAJP, 30)
    font4C.set_underline(C4)
    img = font1A.render("1A", True, (255, 255, 255))
    canvas.blit(img, (CNVW - 300, CNVH - 50))
    img = font2B.render("2B", True, (255, 255, 255))
    canvas.blit(img, (CNVW - 200, CNVH - 50))
    img = font4C.render("4C", True, (255, 255, 255))
    canvas.blit(img, (CNVW - 100, CNVH - 50))
    reaction_log()


# Game loop
running = True
frameEC = 0
frame_burning = 0
EC = False
burning = False


class FPSDisplay:
    trueFPS = 0

    def __init__(self):
        self.clock = pygame.time.Clock()

    def render(self):
        FPSDisplay.trueFPS = self.clock.get_fps()


fps = FPSDisplay()

while running:
    frameEC += 1
    frame_burning += 1

    canvas.fill((0, 0, 0))
    draw()

    for aura in aura_list:
        aura.dendro_decay_while_burning()

    EC_tick()
    burning_tick()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click(mouse_x, mouse_y)

    # Remove inactive auras from list
    aura_list = [aura_list[i] for i in range(
        len(aura_list)) if aura_list[i].aura or aura_list[i].aura_count == 3]
    # Remove old reaction logs
    reaction_text_list = [reaction_text_list[i]
                          for i in range(len(reaction_text_list)) if i <= 12]

    # Update display
    fps.render()
    pygame.display.update()
    fps.clock.tick(FPS)
