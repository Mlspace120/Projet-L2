from tkiteasy import *
import random
import matplotlib.pyplot as plt

# Constantes
TAILLE_CARRE = 5  # Taille d'une case en pixels
SAISONS = ["Printemps", "Été", "Automne", "Hiver"]  # Les saisons pour la simulation

# ------------------- Classes des animaux -------------------

class Lapin:
    """Classe représentant un lapin."""
    def __init__(self, x, y, duree_vie):
        """
        Initialise un lapin.
        x, y : position initiale du lapin sur la grille
        duree_vie : nombre de tours avant que le lapin meure naturellement
        """
        self.x, self.y = x, y
        self.duree_vie = duree_vie
        self.obj_graph = None  # Objet graphique correspondant à ce lapin

    def deplacer(self, plateau):
        """
        Déplacement du lapin sur le plateau.
        Priorité aux carottes voisines pour se nourrir.
        Si aucune carotte n'est proche, se déplace aléatoirement vers une case libre.
        Diminue la durée de vie du lapin à chaque tour.
        """
        directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        # Vérifie si des carottes sont à proximité
        carottes_voisines = [(dx, dy) for dx, dy in directions
                             if (self.x+dx, self.y+dy) in plateau.carottes]
        if carottes_voisines:
            # Se déplace vers une carotte aléatoire
            dx, dy = random.choice(carottes_voisines)
            nx, ny = self.x + dx, self.y + dy
            plateau.deplacer_case(self, nx, ny)
            self.duree_vie += 3  # Gagne de la vie en mangeant
            plateau.g.supprimer(plateau.obj_carottes.pop((nx,ny)))  # Supprime la carotte du graphique
            plateau.carottes.remove((nx,ny))  # Supprime la carotte de la liste
        else:
            # Déplacement aléatoire vers une case libre
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = self.x + dx, self.y + dy
                if plateau.case_libre(nx, ny):
                    plateau.deplacer_case(self, nx, ny)
                    break
        self.duree_vie -= 1  # Vie du lapin diminue à chaque tour


class Renard:
    """Classe représentant un renard."""
    def __init__(self, x, y, duree_vie, energie, miam, e_rep):
        """
        Initialise un renard.
        x, y : position initiale
        duree_vie : nombre de tours avant mort naturelle
        energie : énergie initiale
        miam : énergie gagnée en mangeant un lapin
        e_rep : énergie minimale nécessaire pour se reproduire
        """
        self.x, self.y = x, y
        self.duree_vie = duree_vie
        self.energie = energie
        self.miam = miam
        self.e_rep = e_rep
        self.obj_graph = None

    def deplacer(self, plateau):
        """
        Déplacement du renard sur le plateau.
        Cherche les lapins autour selon son flair.
        Si un lapin est trouvé, se déplace vers lui et le mange.
        Sinon, se déplace aléatoirement.
        La durée de vie et l'énergie diminuent à chaque tour.
        """
        # Ajuste le flair selon la saison (Hiver = +1, Été = -1, autres = 0)
        flair = 5 + (1 if SAISONS[plateau.saison_index]=="Hiver" else -1 if SAISONS[plateau.saison_index]=="Été" else 0)
        cible = None
        min_dist = flair+1

        # Recherche le lapin le plus proche dans la zone du flair
        for dx in range(-flair, flair+1):
            for dy in range(-flair, flair+1):
                nx, ny = self.x+dx, self.y+dy
                if 0<=nx<plateau.taille and 0<=ny<plateau.taille:
                    lap = plateau.grille_lapins[nx][ny]
                    if lap:
                        dist = abs(lap.x - self.x)+abs(lap.y - self.y)
                        if dist < min_dist:
                            min_dist = dist
                            cible = lap

        if cible:
            # Déplace le renard vers le lapin
            dx = 1 if cible.x>self.x else -1 if cible.x<self.x else 0
            dy = 1 if cible.y>self.y else -1 if cible.y<self.y else 0
            nx, ny = self.x+dx, self.y+dy
            if (nx, ny) == (cible.x, cible.y):
                plateau.supprimer_lapin(cible)
                self.energie += self.miam  # Gagne de l'énergie
        else:
            # Déplacement aléatoire si aucun lapin proche
            for _ in range(8):
                dx, dy = random.choice([(-1,0),(1,0),(0,-1),(0,1)])
                nx, ny = self.x+dx, self.y+dy
                if plateau.case_libre(nx,ny):
                    break
            else:
                nx, ny = self.x, self.y  # Reste sur place si aucune case libre

        plateau.deplacer_case(self,nx,ny)
        self.energie -= 1
        self.duree_vie -= 1

# ------------------- Classe de la forêt -------------------

class ForetInSilico:
    """Classe principale de la simulation de forêt avec lapins, renards et carottes."""
    def __init__(self, taille=60, f_n_lap=15, d_v_lap=20,
                 init_ren=20, d_v_ren=20, e_n_ren=15, miam=8, e_rep_ren=22):
        """
        Initialise la forêt et les paramètres de simulation.
        taille : dimension de la grille
        f_n_lap : nombre de lapins créés par tour
        d_v_lap : durée de vie d’un lapin
        init_ren : nombre initial de renards
        d_v_ren : durée de vie des renards
        e_n_ren : énergie initiale des renards
        miam : énergie gagnée par un renard en mangeant un lapin
        e_rep_ren : énergie minimale pour reproduction d’un renard
        """
        self.taille = taille
        self.f_n_lap = f_n_lap
        self.d_v_lap = d_v_lap
        self.init_ren = init_ren
        self.d_v_ren = d_v_ren
        self.e_n_ren = e_n_ren
        self.miam = miam
        self.e_rep_ren = e_rep_ren

        # Fenêtre graphique
        self.g = ouvrirFenetre(taille*TAILLE_CARRE, taille*TAILLE_CARRE)
        self.g.bind_all("<Key>", self.touche)  # Permet de quitter avec 'q'

        # Grilles et listes pour suivre les animaux
        self.lapins = []
        self.renards = []
        self.grille_lapins = [[None]*taille for _ in range(taille)]
        self.grille_renards = [[None]*taille for _ in range(taille)]
        self.carottes = set()  # Positions des carottes
        self.obj_carottes = {}  # Objets graphiques des carottes

        # Statistiques pour tracé
        self.pop_lapins = []
        self.pop_renards = []
        self.pop_carottes = []

        # Variables de simulation
        self.quitter = False
        self.saison_index = 0
        self.tour = 0
        self.rects = [[None]*taille for _ in range(taille)]  # Rectangle pour chaque case

        self.init_plateau()  # Initialise le plateau

    def touche(self,event):
        """Détecte si l'utilisateur appuie sur 'q' pour quitter."""
        if event.keysym.lower() == "q":
            self.quitter = True

    def init_plateau(self):
        """Dessine la grille et crée les animaux/carottes initiaux."""
        for i in range(self.taille):
            for j in range(self.taille):
                self.rects[i][j] = self.g.dessinerRectangle(
                    i*TAILLE_CARRE, j*TAILLE_CARRE, TAILLE_CARRE, TAILLE_CARRE,
                    self.couleur_case(i,j))
        # Création initiale des lapins et renards
        for _ in range(10):
            self.naitre_lapin()
        for _ in range(self.init_ren):
            self.naitre_renard()
        self.generer_carottes(5)

    def couleur_case(self,x,y):
        """Détermine la couleur du sol selon la saison actuelle."""
        base = ["#A2D149","#8CBF26"]
        saison = SAISONS[self.saison_index]
        if saison == "Printemps": return base[(x+y)%2]
        elif saison == "Été": return "#7CB342" if (x+y)%2==0 else "#558B2F"
        elif saison == "Automne": return "#D17A0B" if (x+y)%2==0 else "#A65100"
        else: return "#E0F7FA" if (x+y)%2==0 else "#B2EBF2"

    def mise_a_jour_saison(self):
        """Met à jour la couleur de la grille si une saison change."""
        if self.tour % 50 == 0:
            self.saison_index = (self.saison_index + 1) % 4
            for i in range(self.taille):
                for j in range(self.taille):
                    self.g.changerCouleur(self.rects[i][j], self.couleur_case(i,j))

    def positions_libres(self):
        """Retourne la liste des positions libres pour créer un animal ou une carotte."""
        return [(x,y) for x in range(self.taille) for y in range(self.taille)
                if self.case_libre(x,y) and (x,y) not in self.carottes]

    def case_libre(self,x,y):
        """Vérifie si une case est libre d'animaux."""
        if not (0<=x<self.taille and 0<=y<self.taille): return False
        return self.grille_lapins[x][y] is None and self.grille_renards[x][y] is None

    def deplacer_case(self,obj,nx,ny):
        """
        Déplace un animal sur la grille et met à jour le graphique.
        obj : animal à déplacer
        nx, ny : nouvelle position
        """
        if isinstance(obj,Lapin):
            self.grille_lapins[obj.x][obj.y] = None
        else:
            self.grille_renards[obj.x][obj.y] = None

        self.g.deplacer(obj.obj_graph,(nx-obj.x)*TAILLE_CARRE,(ny-obj.y)*TAILLE_CARRE)
        obj.x, obj.y = nx, ny

        if isinstance(obj,Lapin):
            self.grille_lapins[nx][ny] = obj
        else:
            self.grille_renards[nx][ny] = obj

    # ------------------- Création des animaux -------------------

    def naitre_lapin(self):
        """Créer des lapins sur des positions libres."""
        for _ in range(self.f_n_lap):
            libres = self.positions_libres()
            if not libres: return
            x, y = random.choice(libres)
            lap = Lapin(x,y,self.d_v_lap)
            lap.obj_graph = self.g.dessinerRectangle(x*TAILLE_CARRE,y*TAILLE_CARRE,TAILLE_CARRE,TAILLE_CARRE,"white")
            self.lapins.append(lap)
            self.grille_lapins[x][y] = lap

    def naitre_renard(self):
        """Créer un renard sur une position libre."""
        libres = self.positions_libres()
        if not libres: return
        x, y = random.choice(libres)
        ren = Renard(x,y,self.d_v_ren,self.e_n_ren,self.miam,self.e_rep_ren)
        ren.obj_graph = self.g.dessinerRectangle(x*TAILLE_CARRE,y*TAILLE_CARRE,TAILLE_CARRE,TAILLE_CARRE,"red")
        self.renards.append(ren)
        self.grille_renards[x][y] = ren

    # ------------------- Reproduction -------------------

    def reproduction_lapins(self):
        """Lapins se reproduisent si voisins présents."""
        nouveaux = []
        positions = set((lap.x, lap.y) for lap in self.lapins)
        RAYON = 2
        cibles = set()
        for lap in self.lapins:
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    if dx==0 and dy==0: continue
                    xx, yy = lap.x+dx, lap.y+dy
                    if (xx,yy) in positions:
                        for rx in range(-RAYON,RAYON+1):
                            for ry in range(-RAYON,RAYON+1):
                                cibles.add((lap.x+rx, lap.y+ry))
        for x, y in cibles:
            if not self.case_libre(x,y): continue
            voisins = sum((1 for dx in [-1,0,1] for dy in [-1,0,1]
                         if (dx!=0 or dy!=0) and (x+dx,y+dy) in positions))
            if voisins in (2,3):
                bebe = Lapin(x,y,self.d_v_lap)
                bebe.obj_graph = self.g.dessinerRectangle(x*TAILLE_CARRE,y*TAILLE_CARRE,TAILLE_CARRE,TAILLE_CARRE,"white")
                nouveaux.append(bebe)
                self.grille_lapins[x][y] = bebe
        self.lapins.extend(nouveaux)

    def reproduction_renards(self):
        """Renards se reproduisent si assez d'énergie."""
        nouveaux = []
        for ren in self.renards:
            if ren.energie >= ren.e_rep:
                for _ in range(8):
                    nx, ny = ren.x+random.choice([-1,0,1]), ren.y+random.choice([-1,0,1])
                    if self.case_libre(nx,ny):
                        bebe = Renard(nx,ny,self.d_v_ren,self.e_n_ren,self.miam,self.e_rep_ren)
                        bebe.obj_graph = self.g.dessinerRectangle(nx*TAILLE_CARRE,ny*TAILLE_CARRE,TAILLE_CARRE,TAILLE_CARRE,"red")
                        nouveaux.append(bebe)
                        self.grille_renards[nx][ny] = bebe
                        ren.energie //= 2
                        break
        self.renards.extend(nouveaux)

    # ------------------- Carottes -------------------

    def generer_carottes(self,nb_base):
        """Génère des carottes selon la saison."""
        saison = SAISONS[self.saison_index]
        facteur = 2 if saison in ["Printemps","Été"] else 0.5
        nb = max(1,int(nb_base*facteur))
        libres = self.positions_libres()
        for _ in range(min(nb,len(libres))):
            x, y = random.choice(libres)
            self.carottes.add((x,y))
            self.obj_carottes[(x,y)] = self.g.dessinerRectangle(x*TAILLE_CARRE,y*TAILLE_CARRE,TAILLE_CARRE,TAILLE_CARRE,"orange")

    # ------------------- Suppression -------------------

    def supprimer_lapin(self,lap):
        """Supprime un lapin mort de la grille et du graphique."""
        self.grille_lapins[lap.x][lap.y] = None
        self.g.supprimer(lap.obj_graph)
        self.lapins.remove(lap)

    # ------------------- Boucle principale -------------------

    def boucle_simulation(self):
        """Boucle principale qui fait avancer la simulation tour par tour."""
        while not self.quitter:
            self.tour += 1
            self.mise_a_jour_saison()
            self.generer_carottes(1)
            self.naitre_lapin()
            self.reproduction_lapins()

            # Déplacement et mort des lapins
            for lap in self.lapins[:]:
                lap.deplacer(self)
                if lap.duree_vie <= 0:
                    self.supprimer_lapin(lap)

            # Déplacement et mort des renards
            for ren in self.renards[:]:
                ren.deplacer(self)
                if ren.duree_vie <= 0 or ren.energie <= 0:
                    self.grille_renards[ren.x][ren.y] = None
                    self.g.supprimer(ren.obj_graph)
                    self.renards.remove(ren)

            self.reproduction_renards()

            # Collecte des statistiques
            self.pop_lapins.append(len(self.lapins))
            self.pop_renards.append(len(self.renards))
            self.pop_carottes.append(len(self.carottes))

            self.g.actualiser()

        # Fin de simulation : fermeture de la fenêtre et affichage du graphique
        self.g.fermerFenetre()
        self.afficher_graphique_final()

    def afficher_graphique_final(self):
        """Affiche l’évolution des populations avec les saisons en arrière-plan."""
        tours = list(range(len(self.pop_lapins)))
        fig, ax = plt.subplots()
        LONGUEUR_SAISON = 50
        couleurs = {"Printemps":"#A2D149","Été":"#7CB342","Automne":"#D17A0B","Hiver":"#E0F7FA"}

        # Affiche les saisons en fond
        for i, saison in enumerate(SAISONS):
            debut = i*LONGUEUR_SAISON
            fin = (i+1)*LONGUEUR_SAISON
            ax.axvspan(debut, fin, color=couleurs[saison], alpha=0.2)

        # Courbes populations
        ax.plot(tours, self.pop_lapins,label="Lapins",color="blue")
        ax.plot(tours, self.pop_renards,label="Renards",color="red")

        ax.set_xlabel("Tours")
        ax.set_ylabel("Population")
        ax.set_title("Simulation forêt (saisons en arrière-plan)")
        ax.legend()
        plt.show()


# ------------------- Exécution -------------------

if __name__=="__main__":
    foret = ForetInSilico()
    foret.boucle_simulation()
