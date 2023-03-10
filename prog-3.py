import math
import pygame
import sys

BLEUCLAIR = (127, 191, 255)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
NOIR = (0, 0, 0)

#Données pour le dessin vectoriel
A = 2
B = 5
C = 20

#Constante de coulomb
K = 8.9876 * 10**9
M = 1e-10

RAYON_OBJET = 10

dimensions_fenetre = (1600, 900)
images_par_seconde = 25

pygame.init()

fenetre = pygame.display.set_mode(dimensions_fenetre)
pygame.display.set_caption("Programmme 3")

police = pygame.font.SysFont("monospcae",16)
horloge = pygame.time.Clock()

objets = []

def ajouter_objet(x, y,q):
    objets.append((x, y, q))


def retirer_objet(x, y):
    for obj in objets:
        if distance((x, y), (obj[0], obj[1])) <= RAYON_OBJET:
            objets.remove(obj)

def dessiner_objects(): 
    for obj in objets:
        x, y, q = obj
        coleur = NOIR if q < 0 else ROUGE
        
        pygame.draw.circle(fenetre, coleur, (x, y), RAYON_OBJET)

def distance(a, b) :
    xa, ya = a
    xb, yb = b
    return math.sqrt((xb - xa)**2  + (yb - ya)**2)

def norme(x, y):
    return math.sqrt(x**2 + y**2)

def calculer_champ(x, y):
    resultat_x, resultat_y = 0, 0

    for charge in objets:
        r = distance((x, y), (charge[0], charge[1]))
        
        if r < 20:
            return None
        
        norme_v = K*abs(charge[2])/r**2
        alpha = 0
        
        if charge[2] > 0:
            alpha = math.atan2(y-charge[1], x-charge[0])
        else:
            alpha = math.atan2(charge[1]-y, charge[0]-x)
            
        vecteur_champ = (math.cos(alpha)*norme_v, math.sin(alpha)*norme_v)
            
        resultat_x += vecteur_champ[0]
        resultat_y += vecteur_champ[1]
    
    return resultat_x, resultat_y

def dessiner_mobile():
    if mobile_est_present:
        mobile_couleur = NOIR if mobile_charge < 0 else ROUGE
        pygame.draw.circle(fenetre, mobile_couleur, (mobile_x, mobile_y), RAYON_OBJET, 4)
    
def mettre_a_jour_mobile(t):
    global mobile_est_present, mobile_x, mobile_y, mobile_vx, mobile_vy, temps_precedent_en_seconde
    
    if mobile_est_present:
        e = calculer_champ(mobile_x, mobile_y)
        
        if not e:
            mobile_est_present = False
            return
        
        f = (e[0]*mobile_charge, e[1]*mobile_charge)
        dt = t - temps_precedent_en_seconde
        
        a = (f[0]/M, f[1]/M)
        mobile_vx += a[0]*dt
        mobile_vy += a[1]*dt
        mobile_x += mobile_vx*dt + 0.5*a[0]*dt**2
        mobile_y += mobile_vy*dt + 0.5*a[1]*dt**2
        temps_precedent_en_seconde = t

def calculer_energie_potentielle(x, y, charge):
    energie_cinetique, energie_potentielle = 0, 0
    
    e = 0
    for item in objets:
        r = distance((x, y), (item[0], item[1]))
        if r > 1e-10:
            e += K*item[2]*charge / r
    energie_potentielle = e
    energie_cinetique = 0.5*M*norme(mobile_vx, mobile_vy)**2
        
    return energie_cinetique, energie_potentielle

def calculer_potentiel(x, y):
    pt = calculer_energie_potentielle(x, y, 1)[1]
    if mobile_est_present:
        pt += K*mobile_charge/distance((x, y), (mobile_x, mobile_y))
    return pt
    
def afficher_tableau_de_bord():
    texte = "Energie cinétique   : {0:.2f} uJ".format(energie_cinetique*1e6)
    image = police.render(texte, True, NOIR)
    fenetre.blit(image, (40, 40))
    
    texte = "Energie potentielle : {0:.2f} uJ".format(energie_potentielle*1e6)
    image = police.render(texte, True, NOIR)
    fenetre.blit(image, (40, 55))
    
    texte = "Energie totale      : {0:.2f} uJ".format((energie_cinetique + energie_potentielle)*1e6)
    image = police.render(texte, True, NOIR)
    fenetre.blit(image, (40, 70))
    
    texte = "Potentiel souris    : {0:.2f} v".format(potentiel_souris)
    image = police.render(texte, True, NOIR)
    fenetre.blit(image, (40, 85))


mobile_est_present = False
mobile_x, mobile_y, mobile_vx, mobile_vy = 0, 0, 0, 0
energie_cinetique, energie_potentielle = 0, 0
mobile_charge = 0
temps_precedent = pygame.time.get_ticks()
temps_precedent_en_seconde = temps_precedent/1000
potentiel_souris = 0

while True:
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_n:
                mobile_est_present, mobile_charge = True, -1e-7
                mobile_x, mobile_y = pygame.mouse.get_pos()
                mobile_vx, mobile_vy = 0, 0
            elif evenement.key == pygame.K_p:
                mobile_est_present, mobile_charge = True, 1e-7
                mobile_x, mobile_y = pygame.mouse.get_pos()
                mobile_vx, mobile_vy = 0, 0
                
        elif evenement.type == pygame.MOUSEBUTTONDOWN:
            x, y = evenement.pos
            if evenement.button == 1 or evenement.button == 3:
                ajouter_objet(x, y, 1e-7 if evenement.button == 1 else -1e-7)
            elif evenement.button == 2:
                retirer_objet(x, y)
    
    fenetre.fill(BLEUCLAIR)
    dessiner_objects()
    
    temps_maintenant = pygame.time.get_ticks()
    for t in range(temps_precedent, temps_maintenant-1):
        mettre_a_jour_mobile(t/1000)
    temps_precedent = temps_maintenant
        
    dessiner_mobile()
    
    if mobile_est_present:
        energie_cinetique, energie_potentielle = calculer_energie_potentielle(mobile_x, mobile_y, mobile_charge)
    sx, sy = pygame.mouse.get_pos()
    potentiel_souris = calculer_potentiel(sx, sy)
    
    afficher_tableau_de_bord()
    
    pygame.display.flip()
    horloge.tick(images_par_seconde)