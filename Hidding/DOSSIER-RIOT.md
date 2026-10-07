# Présentation de Hidding pour une demande d'accès

## Objectif

Hidding est un projet de compagnon Windows destiné à devenir accessible à la communauté VALORANT. Il aide les joueurs à comprendre leur historique récent et leur progression. La première version est un prototype local utilisant uniquement des données fictives ou importées manuellement.

## Parcours proposé

1. Le joueur ouvre Hidding et peut explorer une démonstration clairement identifiée.
2. Dans la future version connectée, il relie son compte via Riot Sign On et accepte explicitement le partage de ses données dans Hidding.
3. Le service récupère l'historique autorisé, puis les détails des dix derniers matchs disponibles.
4. Hidding présente les agrégats, les matchs et des observations explicables.
5. Un overlay Alt + W permet de consulter ces informations. Son contenu, ses phases d'affichage et l'accès aux données des autres joueurs seront soumis à validation.

## Fonction à faire examiner explicitement

Nous souhaitons étudier des indicateurs de performances atypiques ou pouvant correspondre à un compte secondaire, à partir d'un historique récent. Aucun verdict de triche, aucune probabilité de culpabilité, aucun signalement automatique. Les seuils actuels sont expérimentaux. Cette fonctionnalité doit être décrite dans la demande et peut être modifiée ou retirée selon le retour de Riot.

## Données et architecture envisagées

API VAL-MATCH-V1 : liste de matchs par PUUID et détails par matchId. Serveur HTTPS pour conserver les secrets Riot et gérer quotas/cache. RSO pour l'identité et le consentement. Respect des joueurs masqués et des profils non consentants. Pas de statistiques adverses avant le match, de calcul de MMR caché ni d'accès à la mémoire du jeu.

## Éléments restant à fournir avant une demande complète

- URL du dépôt et URL d'une présentation/démonstration accessible.
- Identité et adresse de contact du responsable du projet.
- Politique de confidentialité et conditions adaptées à la future version hébergée : conservation, suppression, consentement, hébergeur et responsabilités.
- Démonstration du parcours de connexion prévu et modalités d'affichage de l'overlay.
- Confirmation par Riot de la recevabilité de l'analyse des profils atypiques.

## Confidentialité du prototype actuel

Le prototype n'effectue aucune requête réseau, ne demande aucun identifiant Riot et ne stocke aucun historique importé sur disque. Les fichiers importés restent sur le PC et sont chargés en mémoire jusqu'à fermeture. La compilation télécharge des dépendances ; le workflow GitHub utilise les services GitHub. La future version connectée nécessitera une nouvelle politique couvrant le serveur.
