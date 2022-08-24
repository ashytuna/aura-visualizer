import math
import os
import path
import pygame


CNVW, CNVH = 800, 600
CAPTION = 'Aura Visualizer'
ELMW, ELMH, ELMS = 65, 65, 300
FPS = 60
ELEMENT_COLOR = {
    'Anemo': (163, 243, 202),
    'Geo': (250, 182, 50),
    'Electro': (175, 142, 193),
    'Dendro': (165, 200, 59),
    'Hydro': (76, 194, 241),
    'Pyro': (239, 121, 56),
    'Cryo': (159, 214, 227)
}
REACTION_COLOR = {
    'Vaporize': (254, 203, 99),
    'Overload': (251, 136, 155),
    'Superconduct': (196, 187, 245),
    'Melt': (255, 202, 105),
    'Crystalize':  (215, 184, 130),
    'Swirl':  (163, 243, 202),
    'Electro-Charged': (212, 162, 255),
    'Burning': (233, 152, 8),
    'Overgrown': (76, 194, 241),
    'Intensified': (175, 142, 193)
}
ANEMO, GEO, ELECTRO, DENDRO, HYDRO, PYRO, CRYO = 0, 1, 2, 3, 4, 5, 6
AURA_TAX = 0.8
REACTION_MODIFIER = {
    'equal': 1,
    'reverse': 0.5,
    'forward': 2
}


def decay_rate(gauge):
    return (2.5 * gauge + 7) / (0.8 * gauge) \
        if gauge == 1 or gauge == 2 or gauge == 4 else -1


A1 = True
B2 = False
C4 = False
aura_list = []
reaction_text_list = []


elementC = [(163, 243, 202), (250, 182, 50), (175, 142, 193),
            (165, 200, 59), (76, 194, 241), (239, 121, 56), (159, 214, 227)]
elmImgs = []
for fileName in os.listdir(path.ELEMENTS):
    elmImgs.append(pygame.image.load(path.ELEMENTS + fileName))


pygame.init()
canvas = pygame.display.set_mode((CNVW, CNVH))
pygame.display.set_caption(CAPTION)
favicon = pygame.image.load(path.FAVICON)
pygame.display.set_icon(favicon)


def aura_display_size(auraCount):
    if auraCount == 1:
        if len(aura_list) == 2:  # 1 aura - middle
            return ((CNVW / 2) - (ELMS / 2) - 100, (CNVH / 2.8) - (ELMS / 2) - 30)
        if len(aura_list) == 3:  # 2 auras, 1st - left
            return ((CNVW / 2) - ELMS - 100, (CNVH / 2.8) - (ELMS / 2) - 30)
    if auraCount == 2:  # 2 auras, 2nd - right
        return (CNVW / 2 - 100, (CNVH / 2.8) - (ELMS / 2) - 30)
    return (-1, -1)


class ReactionText:
    def __init__(self, reaction):
        self.text = reaction
        self.color = REACTION_COLOR[reaction] if reaction in REACTION_COLOR \
            else (255, 255, 255)


class Aura:
    def __init__(self, aura, U, decayU, element, auraCount):
        if element == ANEMO or element == GEO:
            self.aura = False
        else:
            self.aura = aura
        self.U = U * AURA_TAX
        self.decayU = decayU
        self.element = element
        self.auraCount = auraCount

    def aura_display(self):
        if self.aura:
            img = pygame.transform.scale(
                elmImgs[self.element], (ELMS, ELMS))
            canvas.blit(img, aura_display_size(self.auraCount))

    def decay(self):
        if self.aura:
            if self.decayU == 'A':
                self.U -= 1 / (decay_rate(1) * FPSDisplay.trueFPS)
            if self.decayU == 'B':
                self.U -= 1 / (decay_rate(2) * FPSDisplay.trueFPS)
            if self.decayU == 'C':
                self.U -= 1 / (decay_rate(4) * FPSDisplay.trueFPS)
            if self.decayU == 'AB':
                self.U -= (1 / (decay_rate(1) * FPSDisplay.trueFPS)) + \
                    (1 / (decay_rate(2) * FPSDisplay.trueFPS))
            if self.decayU == 'BB':
                self.U -= (1 / (decay_rate(2) * FPSDisplay.trueFPS)) + \
                    (1 / (decay_rate(2) * FPSDisplay.trueFPS))
            if self.decayU == 'CB':
                self.U -= (1 / (decay_rate(4) * FPSDisplay.trueFPS)) + \
                    (1 / (decay_rate(2) * FPSDisplay.trueFPS))
        if self.U <= 0:
            self.U = 0
            self.aura = False

    def gauge_display(self):
        if self.aura:
            pygame.draw.rect(canvas, (elementC[self.element]), pygame.Rect(
                0, CNVH - (100 * self.auraCount), self.U * (CNVW / 4), 30))
            font = pygame.font.Font(path.FONT_JAJP, 25)
            img = font.render(
                str(math.ceil(self.U * 100) / 100) + self.decayU, True, (255, 255, 255))
            canvas.blit(img, (10, CNVH - (100 * self.auraCount) - 40))

    def dendro_decay_while_burning(self):
        if self.element == DENDRO and burning:
            if self.decayU == 'A':
                self.decayU = 'AB'
            if self.decayU == 'B':
                self.decayU = 'BB'
            if self.decayU == 'C':
                self.decayU = 'CB'


def reaction(mousex, mousey):
    if CNVH - ELMH < mousey < CNVH:
        for i in range(2):
            slot = - i - 1
            x = ELMW * ANEMO
            if x < mousex < x + ELMW:
                anemoTrigger(slot)
            x = ELMW * GEO
            if x < mousex < x + ELMW:
                geoTrigger(slot)
            x = ELMW * CRYO
            if x < mousex < x + ELMW:
                cryoTrigger(slot)
        x = ELMW * DENDRO
        if x < mousex < x + ELMW:
            dendroTrigger()
        x = ELMW * PYRO
        if x < mousex < x + ELMW:
            pyroTrigger()
        x = ELMW * ELECTRO
        if x < mousex < x + ELMW:
            electroTrigger()
        x = ELMW * HYDRO
        if x < mousex < x + ELMW:
            hydroTrigger()


# All reactions
# reaction modifiers
reverseAmpModifier = 0.5
forwardAmpModifier = 2
superconductModifier = 1
overloadModifier = 1
swirlModifier = 0.5
crystalizeModifier = 0.5
electroChargedModifier = -0.4


def anemoTrigger(slot):
    # Swirl
    if aura_list[slot].element == 2 or aura_list[slot].element == 4 or aura_list[slot].element == 5 or aura_list[slot].element == 6:
        rxnMod(swirlModifier, slot)
        reaction_text_list.insert(0, ReactionText('Swirl'))


def geoTrigger(slot):
    # Crystalize
    if aura_list[slot].element == 2 or aura_list[slot].element == 4 or aura_list[slot].element == 5 or aura_list[slot].element == 6:
        rxnMod(crystalizeModifier, slot)
        reaction_text_list.insert(0, ReactionText('Crystalize'))


def electroTrigger():
    global EC, frameEC
    for i in range(2):
        slot = -(i + 1)
        # Overload
        if aura_list[slot].element == 5:
            rxnMod(overloadModifier, slot)
            reaction_text_list.insert(0, ReactionText('Overload'))

        # Superconduct
        if aura_list[slot].element == 6:
            rxnMod(superconductModifier, slot)
            reaction_text_list.insert(0, ReactionText('Superconduct'))

        # Intensified
        if aura_list[slot].element == 3:
            reaction_text_list.insert(0, ReactionText('Intensified'))

    # Electro-charged
    if aura_list[-1].element == 4:
        doubleAura(aura_list[-1], 2)
        reaction_text_list.insert(0, ReactionText('Electro-Charged'))
        aura_list[-1].U -= 0.4
        aura_list[-2].U -= 0.4
        frameEC = 0
        EC = True

        # Electro-charged
    elif aura_list[-2].element == 4:
        doubleAura(aura_list[-2], 2)
        reaction_text_list.insert(0, ReactionText('Electro-Charged'))
        aura_list[-1].U -= 0.4
        aura_list[-2].U -= 0.4
        frameEC = 0
        EC = True


def dendroTrigger():
    global burning, frameBurning
    # Burning
    if aura_list[-1].element == 5:
        doubleAura(aura_list[-1], 3)
        reaction_text_list.insert(0, ReactionText('Burning'))
        frameBurning = 0
        burning = True
    # Burning
    elif aura_list[-2].element == 5:
        doubleAura(aura_list[-2], 3)
        reaction_text_list.insert(0, ReactionText('Burning'))
        frameBurning = 0
        burning = True

    for i in range(2):
        slot = -(i + 1)

        # Overgrown
        if aura_list[slot].element == 4:
            reaction_text_list.insert(0, ReactionText('Overgrown'))

        # Intensified
        if aura_list[slot].element == 2:
            reaction_text_list.insert(0, ReactionText('Intensified'))


def hydroTrigger():
    global EC, frameEC
    for i in range(2):
        slot = -(i + 1)
        # forward vaporize
        if aura_list[slot].element == 5:
            rxnMod(forwardAmpModifier, slot)
            reaction_text_list.insert(0, ReactionText('Vaporize'))

        # Overgrown
        if aura_list[slot].element == 3:
            reaction_text_list.insert(0, ReactionText('Overgrown'))

    # Electro-charged
    if aura_list[-1].element == 2:
        doubleAura(aura_list[-1], 4)
        reaction_text_list.insert(0, ReactionText('Electro-Charged'))
        aura_list[-1].U -= 0.4
        aura_list[-2].U -= 0.4
        frameEC = 0
        EC = True

        # Electro-charged
    elif aura_list[-2].element == 2:
        doubleAura(aura_list[-2], 4)
        reaction_text_list.insert(0, ReactionText('Electro-Charged'))
        aura_list[-1].U -= 0.4
        aura_list[-2].U -= 0.4
        frameEC = 0
        EC = True


def pyroTrigger():
    for i in range(2):
        slot = -(i + 1)
        # forward melt
        if aura_list[slot].element == 6:
            rxnMod(forwardAmpModifier, slot)
            reaction_text_list.insert(0, ReactionText('Melt'))

        # reverse vaporize
        if aura_list[slot].element == 4:
            rxnMod(reverseAmpModifier, slot)
            reaction_text_list.insert(0, ReactionText('Vaporize'))

        # Overload
        if aura_list[slot].element == 2:
            rxnMod(overloadModifier, slot)
            reaction_text_list.insert(0, ReactionText('Overload'))

    global burning, frameBurning
    # Burning
    if aura_list[-1].element == 3:
        doubleAura(aura_list[-1], 5)
        reaction_text_list.insert(0, ReactionText('Burning'))
        frameBurning = 0
        burning = True
    # Burning
    elif aura_list[-2].element == 3:
        doubleAura(aura_list[-2], 5)
        reaction_text_list.insert(0, ReactionText('Burning'))
        frameBurning = 0
        burning = True

    # Burning
    if aura_list[slot].element == 3:
        pass


def cryoTrigger(slot):
    # Superconduct
    if aura_list[slot].element == 2:
        rxnMod(superconductModifier, slot)
        reaction_text_list.insert(0, ReactionText('Superconduct'))

    # Reverse melt
    if aura_list[slot].element == 5:
        rxnMod(reverseAmpModifier, slot)
        reaction_text_list.insert(0, ReactionText('Melt'))


def rxnMod(mod, auraSlot):
    if A1:
        aura_list[auraSlot].U -= 1 * mod
    elif B2:
        aura_list[auraSlot].U -= 2 * mod
    elif C4:
        aura_list[auraSlot].U -= 4 * mod


def getDecayRate():
    if A1:
        U = 1
        d = 'A'
    elif B2:
        U = 2
        d = 'B'
    elif C4:
        U = 4
        d = 'C'

    return U, d

# sets up double auras for the electro-charged and burning reactions


def doubleAura(aura1, aura2):
    if aura1.element == 4 and aura2 == 2:  # electro on hydro
        U, d = getDecayRate()
        if aura1.auraCount == 1:
            aura_list.append(Aura(True, U, d, aura2, 2))
        elif aura1.auraCount == 2:
            aura_list.append(Aura(True, U, d, aura2, 1))

    elif aura1.element == 2 and aura2 == 4:  # hydro on electro
        U, d = getDecayRate()
        if aura1.auraCount == 1:
            aura_list.append(Aura(True, U, d, aura2, 2))
        elif aura1.auraCount == 2:
            aura_list.append(Aura(True, U, d, aura2, 1))

    elif aura1.element == 5 and aura2 == 3:  # dendro on pyro
        U, d = getDecayRate()
        if aura1.auraCount == 1:
            aura_list.append(Aura(True, U, d, aura2, 2))
        elif aura1.auraCount == 2:
            aura_list.append(Aura(True, U, d, aura2, 1))

    elif aura1.element == 3 and aura2 == 5:  # pyro on dendro
        U, d = getDecayRate()
        if aura1.auraCount == 1:
            aura_list.append(Aura(True, U, d, aura2, 2))
        elif aura1.auraCount == 2:
            aura_list.append(Aura(True, U, d, aura2, 1))


def e_charged():  # electro charged ticks
    global frameEC, EC
    if EC:
        if frameEC == (5 * round(FPSDisplay.trueFPS / 5)) and len(aura_list) >= 2:
            frameEC = 0
            aura_list[-1].U -= 0.4
            aura_list[-2].U -= 0.4
            reaction_text_list.insert(0, ReactionText('Electro-Charged'))

        if aura_list[-1].U <= 0 or aura_list[-2].U <= 0:
            EC = False
            frameEC = (5 * round(FPSDisplay.trueFPS / 5)) + 1


def burningReaction():  # burning ticks
    global frameBurning, burning
    if burning:
        if frameBurning == (FPS / 4) and len(aura_list) >= 2:
            frameBurning = 0
            reaction_text_list.insert(0, ReactionText('Burning'))

            # reapply 2B pyro every tick (-1,2 top, -2,1 bottom)
            if aura_list[-2].element == 3:
                if aura_list[-1].U <= 2 * AURA_TAX and aura_list[-1].element == 5:
                    aura_list[-1] = Aura(True, 2, 'B', 5, 2)
            elif aura_list[-1].element == 3:
                if aura_list[-2].U <= 2 * AURA_TAX and aura_list[-2].element == 5:
                    aura_list[-2] = Aura(True, 2, 'B', 5, 1)

        if aura_list[-1].U <= 0 or aura_list[-2].U <= 0:
            burning = False
            frameBurning = (FPS / 4) + 1


# (0 anemo, 1 geo, 2 electro, 3 dendro, 4 hydro, 5 pyro, 6 cryo)
# initial
aura_list.append(Aura(False, 1, 'A', 7, 3))


def clickUnit():
    global A1, B2, C4
    x = CNVW - 300
    y = CNVH - 50
    w = 45
    h = 40
    if mouse_x > x and mouse_x < x + w:
        if mouse_y > y and mouse_y < y + h:
            A1 = True
            B2 = False
            C4 = False
    x = CNVW - 200
    if mouse_x > x and mouse_x < x + w:
        if mouse_y > y and mouse_y < y + h:
            A1 = False
            B2 = True
            C4 = False
    x = CNVW - 100
    if mouse_x > x and mouse_x < x + w:
        if mouse_y > y and mouse_y < y + h:
            A1 = False
            B2 = False
            C4 = True


def click(mouse_x, mouse_y):
    global A1, B2, C4
    clickUnit()

    # Click aura
    for elementber in range(len(elmImgs)):
        w, h = 65, 65
        x = w * elementber
        y = CNVH - h
        if mouse_x > x and mouse_x < x + w:
            if mouse_y > y and mouse_y < y + h:
                # if no aura, then apply an element
                if aura_list[-1].aura == False:
                    if A1:
                        aura_list.append(Aura(True, 1, 'A', elementber, 1))
                    elif B2:
                        aura_list.append(Aura(True, 2, 'B', elementber, 1))
                    elif C4:
                        aura_list.append(Aura(True, 4, 'C', elementber, 1))

                # extending an aura with same element on slot 1
                elif (aura_list[-1].element == elementber and aura_list[-1].aura == True):
                    if A1 and aura_list[-1].U < 0.8:
                        aura_list[-1] = Aura(True, 1, aura_list[-1].decayU,
                                             elementber, aura_list[-1].auraCount)
                    elif B2 and aura_list[-1].U < 2.6:
                        aura_list[-1] = Aura(True, 2, aura_list[-1].decayU,
                                             elementber, aura_list[-1].auraCount)
                    elif C4 and aura_list[-1].U < 3.2:
                        aura_list[-1] = Aura(True, 4, aura_list[-1].decayU,
                                             elementber, aura_list[-1].auraCount)

                # extending an aura with same element on slot 2
                elif aura_list[-2].element == elementber and aura_list[-2].aura == True:
                    if A1 and aura_list[-2].U < 0.8:
                        aura_list[-2] = Aura(True, 1, aura_list[-2].decayU,
                                             elementber, aura_list[-2].auraCount)
                    elif B2 and aura_list[-2].U < 2.6:
                        aura_list[-2] = Aura(True, 2, aura_list[-2].decayU,
                                             elementber, aura_list[-2].auraCount)
                    elif C4 and aura_list[-2].U < 3.2:
                        aura_list[-2] = Aura(True, 4, aura_list[-2].decayU,
                                             elementber, aura_list[-2].auraCount)
                else:
                    # reactions
                    reaction(mouse_x, mouse_y)


def draw():
    # element buttons
    for i in range(len(elmImgs)):
        canvas.blit(pygame.transform.scale(
            elmImgs[i], (ELMW, ELMH)), (ELMW * i, CNVH - ELMH))

    # Update Aura
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
    font1A = pygame.font.Font(path.FONT_JAJP, 25)
    font1A.set_underline(A1)
    font2B = pygame.font.Font(path.FONT_JAJP, 25)
    font2B.set_underline(B2)
    font4C = pygame.font.Font(path.FONT_JAJP, 25)
    font4C.set_underline(C4)
    img = font1A.render("1A", True, (255, 255, 255))
    canvas.blit(img, (CNVW - 300, CNVH - 50))
    img = font2B.render("2B", True, (255, 255, 255))
    canvas.blit(img, (CNVW - 200, CNVH - 50))
    img = font4C.render("4C", True, (255, 255, 255))
    canvas.blit(img, (CNVW - 100, CNVH - 50))

    reactionLog()


def reactionLog():  # reaction log
    if len(reaction_text_list) > 0:
        for i in range(len(reaction_text_list)):
            font = pygame.font.SysFont('dejavusansmono', 23)
            font = font.render(
                reaction_text_list[i].text, True, reaction_text_list[i].color)
            canvas.blit(font, (CNVW - 200, (CNVH - 250) - (30 * i) + 15))


# Game loop
running = True
frameEC = 0
frameBurning = 0
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
    frameBurning += 1
    # BG color keep at top
    canvas.fill((0, 0, 0))

    draw()

    for aura in aura_list:
        aura.dendro_decay_while_burning()

    e_charged()
    burningReaction()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            click(mouse_x, mouse_y)

    # Remove inactive auras from list
    newAuraList = [aura_list[i] for i in range(
        len(aura_list)) if aura_list[i].aura or aura_list[i].auraCount == 3]
    aura_list = newAuraList

    # Remove old reaction logs
    newReactionTextList = [reaction_text_list[i]
                           for i in range(len(reaction_text_list)) if i <= 12]
    reaction_text_list = newReactionTextList

    # Update display
    fps.render()
    pygame.display.update()
    fps.clock.tick(FPS)
