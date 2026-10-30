# Hidden Bible Facts : prochaines étapes

> ✅ **Tout est fait : la chaîne est en ligne depuis le 31 octobre 2026.** Ce fichier reste comme historique.

Suivi des étapes du blueprint (`CHANNEL-BLUEPRINT.md`, section 3) pour cette chaîne.
✅ = fait · 👤 = à faire par toi · 🤖 = je le fais quand tu me dis que c'est prêt

## 3.1 Questions de départ ✅
Christianisme (mix : Bible, saints, histoire de l'Église, cathédrales, traditions), anglais, 2 vidéos/jour
vers 8h et 20h (Paris, ±35 min), format 3 faits + bonus.

## Style des vidéos ✅ (validé)
Voix Christopher, style calme (or chaud, fondus enchaînés, mouvements lents), tableaux du domaine public
(Wikimedia, sans nudité) mélangés aux vidéos Pixabay, tes 6 musiques triées en 3 ambiances.

## 3.2 Comptes 👤
1. **GitHub** : compte créé ✅. Il reste à connecter ce PC au nouveau compte : dans un terminal,
   `"C:\Program Files\GitHub CLI\gh.exe" auth login` → GitHub.com → HTTPS → Login with a web browser,
   avec le **nouveau** compte. (Fun Facts n'est pas touché ; pour revenir à l'ancien compte : `gh auth switch`.)
2. **TikTok** : compte **personnel** (jamais "Entreprise", sinon pas de Creator Rewards), avec un mot de passe.
   Nom, bio et photo : `profile/PROFILE.md`.
3. **Instagram** : compte **Créateur**, catégorie Éducation. Ne pas activer "profil généré par IA".
4. **Pixabay** : compte avec le nouvel email → ta clé sur pixabay.com/api/docs.
5. **Zernio** : attendre la réponse du support (2e compte gratuit autorisé ?). Ensuite : connecter TikTok +
   Instagram, créer une clé API. 🤖 Je récupère les identifiants des comptes (`python src/publish.py accounts`)
   et je les mets dans `config.json`.
6. **Telegram** : on garde le même bot que Fun Facts ; chaque message commence par **[Hidden Bible Facts]**.
7. **Application Claude sur GitHub** : sur le nouveau compte GitHub, installer github.com/apps/claude
   (→ Configure → accès au dépôt `hidden-bible-facts`). Sans ça, la tâche hebdomadaire ne peut pas être créée.

## 3.3 Dépôt GitHub
1. 🤖 Créer le dépôt **privé** `hidden-bible-facts` sur le nouveau compte et tout envoyer (déjà prêt en local).
2. 👤 Ajouter les secrets sur GitHub (dépôt → Settings → Secrets and variables → Actions) :
   `PIXABAY_API_KEY`, `TELEGRAM_BOT_TOKEN` (le même que Fun Facts), puis `ZERNIO_API_KEY`.
   Ne jamais coller une clé dans le chat.
3. 👤 Sur le PC : copier `.env.example` en `.env` et y coller tes clés (pour les tests en local).

## 3.4 Contenu
- ✅ Plan d'un an : 730 sujets, du 9 nov. 2026 au 8 nov. 2027, fêtes à leur date (Noël le 25/12, Pâques le 28/03/2027…).
- ✅ Mois 1 écrit : 60 sujets, avec tableaux.
- 🤖 Tâche hebdomadaire (lundi 7h UTC) qui écrit les 60 sujets suivants et vérifie les faits sur le web.
  Je la crée une fois le dépôt en ligne et l'application Claude installée, puis je relis les faits du mois 2.

## 3.5 Tests puis mise en ligne
1. 🤖 Test GitHub `no-publish` (fabrique les vidéos sans rien envoyer), puis `dry-run`.
2. 🤖 Test `run` en mode **brouillon** : la vidéo arrive dans tes brouillons TikTok, rien n'est public.
3. 👤 Tu valides → 🤖 je passe en `"publish_mode": "schedule"` (publication automatique).
4. 🤖 Audit complet (section 7 du blueprint) jusqu'à 0 problème.

## Bon à savoir (section 3.6, plusieurs chaînes)
- Nouveau compte GitHub = ses propres 2 000 minutes gratuites par mois (une chaîne en utilise environ 1 200
  maintenant que les vidéos prennent ~10 min).
- Les tâches de la journée démarrent 20 min après celles de Fun Facts (04h20 UTC), pour ne pas se gêner.
- Clé Pixabay séparée = pas de limite partagée avec Fun Facts.
