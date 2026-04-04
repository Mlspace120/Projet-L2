# Documentation Technique : Forêt In Silico

Ce document détaille le fonctionnement de la simulation écosystémique multi-agents modélisant les interactions entre proies, prédateurs et ressources.

---

## 1. Structure du Modèle et Initialisation

La simulation repose sur une grille de cases où chaque entité (Lapin, Renard, Carotte) interagit selon des règles biologiques définies. 

* **Système de coordonnées :** La grille est de taille $n \times n$ (par défaut $60 \times 60$). Chaque case mesure $5 \times 5$ pixels (`TAILLE_CARRE`).
* **Initialisation :** Au lancement, le plateau génère 10 lapins, un nombre variable de renards (par défaut 20) et un premier stock de carottes pour lancer la chaîne alimentaire.

---

## 2. Dynamique des Saisons

Le cycle complet dure 200 tours (50 tours par saison). Le changement de saison impacte l'environnement via la méthode `mise_a_jour_saison` :

| Saison | Couleur Grille | Effet sur le gameplay |
| :--- | :--- | :--- |
| **Printemps** | Vert clair | Croissance élevée des carottes (x2). |
| **Été** | Vert foncé | Flair des renards réduit (-1) / Croissance carottes élevée. |
| **Automne** | Orange/Brun | Croissance des carottes réduite (x0.5). |
| **Hiver** | Bleu/Blanc | Flair des renards augmenté (+1) / Croissance carottes réduite. |

---

## 3. Logique des Agents (Classes)

### Lapin (Proie)
* **Survie :** Possède une `duree_vie`. S'il mange une carotte, il gagne +3 points de vie.
* **Intelligence :** Vérifie les 8 cases voisines. S'il trouve une carotte, il s'y déplace et la consomme. Sinon, il effectue un mouvement aléatoire.
* **Reproduction :** Utilise un algorithme de voisinage. Un nouveau lapin naît si une case libre possède 2 ou 3 voisins lapins (similaire aux règles du Jeu de la Vie de Conway).

### Renard (Prédateur)
* **Énergie :** Démarre avec un capital `energie`. Chaque déplacement consomme 1 point. La mort survient si l'énergie ou la durée de vie tombe à zéro.
* **Chasse (Algorithme de Flair) :** 1. Scanne un rayon de cases (défini par la saison).
    2. Calcule la distance de Manhattan : $dist = |x_{lapin} - x_{renard}| + |y_{lapin} - y_{renard}|$.
    3. Se dirige vers la cible la plus proche.
* **Reproduction :** Si `energie >= e_rep`, le renard crée un descendant et transfère la moitié de son énergie à celui-ci.

---

## 4. Gestion Graphique et Performances

Le code utilise la bibliothèque `tkiteasy` avec des optimisations pour la fluidité :
* **`obj_graph` :** Chaque animal stocke son propre identifiant graphique. Cela permet d'utiliser `self.g.deplacer()` au lieu de redessiner tout le canvas à chaque tour, ce qui est beaucoup plus rapide.
* **`grille_lapins` / `grille_renards` :** Au lieu de parcourir des listes d'objets, le programme utilise des matrices 2D pour vérifier instantanément si une case est libre (`case_libre`).

---

## 5. Analyse des Données

À l'arrêt de la simulation (touche 'q'), le programme génère un graphique via **Matplotlib**. 



* **Courbes :** Evolution des populations de lapins et de renards sur la durée totale (`self.tour`).
* **Contextualisation :** Utilisation de `ax.axvspan` pour colorer l'arrière-plan du graphique selon les saisons traversées durant la simulation, permettant d'analyser visuellement l'impact du climat sur la survie des espèces.

---

## 6. Paramètres de Configuration (Variables de classe)

| Variable | Rôle | Impact |
| :--- | :--- | :--- |
| `f_n_lap` | Natalité forcée | Nombre de lapins "parachutés" par tour pour éviter l'extinction. |
| `miam` | Valeur nutritive | Énergie récupérée par un renard après avoir mangé. |
| `e_rep_ren` | Seuil de scissiparité | Énergie nécessaire pour qu'un renard se dédouble. |
