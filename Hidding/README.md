# Hidding — prototype Windows

Compagnon VALORANT indépendant, interface française sombre/violette et overlay Alt + W.

## État actuel

- Application de bureau, icône de fenêtre/barre des tâches, overlay flottant déplaçable.
- Historique de 10 matchs avec K/D, ACS, dégâts par round et proportion de tirs touchés à la tête.
- Import JSON local ; démo explicitement fictive au premier lancement.
- Observations descriptives : domination régulière et changement d'ACS.
- Compilation Windows manuelle ou GitHub Actions.

Pas encore de connexion Riot, de détection automatique du lobby, de serveur, de classement par rang ni de détection fiable de smurf/triche. Il n'y a pas d'icône dans la zone de notification dans cette version. Rien ne lit la mémoire du jeu.

## Lancer sous Windows

Installer Python 3.12 depuis https://www.python.org/downloads/windows/ puis extraire ce dossier. Double-cliquer sur `Lancer-Hidding.bat`. Aucune dépendance Python supplémentaire pour le lancement (Tkinter doit être installé avec Python).

Alt + W affiche/masque l'overlay tant que Hidding est ouvert. Le bouton fonctionne aussi. Si le raccourci est occupé, son indisponibilité est affichée. Glisser le titre de l'overlay pour le déplacer ; Échap ou le bouton le ferme. Tester VALORANT en mode fenêtré sans bordure : une fenêtre flottante n'est pas garantie visible en plein écran exclusif. Fermer la fenêtre principale quitte l'application.

## Obtenir Hidding.exe

### Sur ton PC

Double-cliquer sur `Compiler-Hidding.bat` (connexion Internet nécessaire). Le résultat est `dist/Hidding.exe`. L'exécutable est non signé ; il doit être testé sous Windows avant distribution.

### Avec GitHub

1. Créer un dépôt `Hidding`.
2. Ajouter **le contenu** de ce dossier à la racine du dépôt, y compris `.github/workflows/windows.yml`. Ne pas ajouter uniquement le ZIP.
3. Dans Actions, choisir **Build Hidding Windows**, puis **Run workflow**.
4. Une fois terminé, télécharger l'artefact **Hidding-Windows**, puis extraire `Hidding.exe`.

Le workflow est aussi déclenché par un tag `v*`. Il ne publie pas automatiquement de Release. Le dépôt n'a pas été créé ou publié depuis cette conversation.

## Importer des matchs

Utiliser `demo.json` comme exemple. Les matchs doivent être triés du plus récent au plus ancien. Seuls les 10 premiers sont analysés. Limites : 2 Mo, 500 matchs.

Chaque match contient des nombres positifs ou nuls : kills, deaths, assists, rounds (au moins 1), damage (dégâts infligés), score (score de combat total), headshots, bodyshots, legshots (impacts, pas nombre de kills). Champs de présentation facultatifs : map, agent, result (`win` ou `loss`). `player` identifie le joueur affiché.

K/D = kills / deaths, avec un dénominateur minimum de 1 pour éviter une division par zéro. ACS et ADR sont pondérés par les rounds. HS % = headshots / ensemble des impacts. Les observations utilisent des seuils exploratoires explicités dans l'interface, sans validation scientifique ni calibration par rang. Elles ne doivent servir ni à accuser un joueur ni à automatiser des signalements.

## Validation

Depuis ce dossier : `python -m unittest discover -s tests -v`.

Les tests couvrent les agrégats, historiques incomplets, données invalides et divisions par zéro. Le raccourci Windows, l'affichage en jeu et le binaire nécessitent un test Windows ; leur fonctionnement n'a pas été vérifié dans l'environnement Linux de création.

## Prochaine étape Riot

Voir `DOSSIER-RIOT.md`. La clé de production et le secret RSO devront rester sur un serveur HTTPS, jamais dans ce dépôt ou l'exécutable. L'API officielle documentée n'est pas une source de détection de lobby en direct ; cet accès devra être étudié et validé séparément.

Hidding n'est ni affilié à Riot Games ni approuvé par Riot Games. VALORANT et Riot Games appartiennent à leurs propriétaires respectifs.
