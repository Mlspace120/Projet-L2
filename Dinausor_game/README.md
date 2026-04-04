
# Documentation Technique : Ride ton Toulousain

Ce document détaille l'architecture, la physique et la logique de programmation du jeu.

## 1. Structure du Canvas et de l'Interface
* **Dimensions :** 1200 * 700 pixels.
* **Système d'UI :** Bascule entre `startScreen` (menu) et `gameArea` (jeu) via la manipulation de la classe CSS `.hidden`.
* **Score :** Calculé en temps réel (`score += 0.05` par frame). La valeur est arrondie à l'entier inférieur pour l'affichage et l'enregistrement final.

## 2. Moteur de Rendu et Animation
Le jeu utilise `requestAnimationFrame` pour synchroniser le rendu à 60 images par seconde.

### Gestion des Sprites
* **Animation du Joueur :** Un tableau `dinoFrames` contient 4 images. L'index change toutes les 12 frames (`frameTimer > 12`), créant l'illusion de course.
* **Parallaxe (Arrière-plan) :** Deux images de fond (`bg1_x` et `bg2_x`) défilent à 1.5px/frame. Lorsqu'une image sort complètement à gauche, elle est téléportée à la droite de la seconde pour un cycle infini.
* **Gestion du Sol :** Utilise `groundScroll` avec l'opérateur modulo (`%`) sur la largeur réelle de l'image de brique (`drawWidth`). Cela garantit que le motif se répète parfaitement sans jamais laisser de vide.

## 3. Physique et Saut
La physique repose sur l'accumulation de forces sur l'axe vertical (Y).

* **`gravity` (0.5) :** Force constante ajoutée à `velocityY` à chaque frame, simulant le poids.
* **`jumpPower` (-17) :** Impulsion initiale négative (vers le haut) appliquée lors de l'appui sur Espace ou Flèche Haut.
* **`groundLevel` (580) :** Limite basse calculée ($canvasHeight - groundHeight$). Si `dino.y` dépasse ce seuil, la vélocité est remise à zéro.
* **Offsets (Correction visuelle) :** `offsetDino` (135) et `offsetPaparazzi` (75) sont utilisés pour aligner les pieds des personnages avec le sol malgré la taille des fichiers images.

## 4. Système de Collision (Hitboxes)
Pour éviter les collisions injustes dues aux zones transparentes des fichiers PNG, le code utilise des hitboxes réduites par rapport à la taille des images.

### Marges appliquées (Pixels)
| Élément | Gauche | Droite | Haut |Bas |
| Dino    | 130    | 130    | 110  | 90 |
| Obstacle| 65     | 110    | 95   | 20 |

**Logique de détection :** Utilisation de l'algorithme AABB. Une collision est détectée si :
`dino.right > obs.left` ET `dino.left < obs.right` ET `dino.bottom > obs.top` ET `dino.top < obs.bottom`.

## 5. Cycle de Vie des Obstacles
* **Apparition :** Toutes les 130 frames, un test de probabilité (`Math.random() < 0.5`) décide de l'apparition d'un nouvel obstacle.
* **Mouvement :** Déplacement linéaire vers la gauche à une vitesse de 5px/frame.
* **Nettoyage mémoire :** Les obstacles ayant une coordonnée `x + width < 0` sont supprimés du tableau `obstacles` via `splice()` pour optimiser les performances.

## 6. Persistance des Données (Leaderboard)
* **Stockage :** Utilisation du `localStorage` du navigateur.
* **Traitement des scores :**
    1. Récupération de la chaîne JSON et conversion en tableau.
    2. Ajout de l'objet `{name, score}`.
    3. Tri décroissant : `b.score - a.score`.
    4. Limitation aux 5 meilleures entrées avec `slice(0, 5)`.
* **Mise à jour UI :** La fonction `updateLeaderboardUI` reconstruit dynamiquement le code HTML des listes de scores.

## 7. Commandes Utilisateur
* **Barre Espace / Flèche Haut :** Saut (uniquement si le personnage est au sol).
* **Echap :** Arrêt immédiat de la boucle de jeu et enregistrement du score.
