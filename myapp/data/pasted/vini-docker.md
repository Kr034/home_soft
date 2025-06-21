Parfait, tu es proche du but. Le conteneur Jellyfin démarre maintenant, **mais le dossier `/data` dans le conteneur est vide**, alors que ton `./remote-data` sur l'hôte contient bien des répertoires comme `anime`, `movies`, etc.

Ce comportement indique un **problème d’accès aux fichiers SSHFS depuis Docker**, malgré le succès du montage initial. Cela survient souvent quand :

---

## 🔍 Problèmes typiques avec SSHFS + Docker

1. **Le conteneur n’a pas la permission de lire le contenu monté via SSHFS**.
2. **SSHFS a été monté sans `allow_other`**, donc seul l'utilisateur ayant monté peut y accéder.
3. Docker tourne en root et ne peut pas traverser un répertoire FUSE/SSHFS sans autorisation explicite.

---

## ✅ Solution

### 1. 📌 Vérifie `/etc/fuse.conf` contient bien :

```bash
user_allow_other
```

Sinon, édite-le avec :

```bash
sudo nano /etc/fuse.conf
```

Et décommente / ajoute la ligne. Puis **remonte** ton SSHFS.

---

### 2. 🔄 Remonte le dossier SSHFS avec les bonnes options

Démonte proprement :

```bash
fusermount -u ./remote-data
```

Puis remonte-le avec **toutes** les options nécessaires :

```bash
sshfs user@host:/remote/path ./remote-data \
  -o allow_other,default_permissions,uid=$(id -u),gid=$(id -g),reconnect
```

> 🔒 Ces options permettent :
>
> * `allow_other`: que Docker (root ou autre utilisateur) puisse accéder
> * `uid`, `gid`: faire correspondre les droits du système local
> * `default_permissions`: vérifier les droits comme un FS standard

---

### 3. 🧪 Test avec un conteneur

Avant même de relancer Jellyfin, teste :

```bash
docker run --rm -v "$PWD/remote-data:/data:ro" alpine ls /data
```

Tu dois voir :

```
anime
cartoons
movies
tv-shows
```

---

### 4. 🔁 Relance proprement

```bash
docker-compose down
docker-compose up -d
```

Puis vérifie dans le conteneur :

```bash
docker exec -it jellyfin ls /data
```

---

### 📦 Bonus : Montage permanent

Si tu veux que SSHFS soit monté automatiquement au boot (avec `systemd` ou `fstab`), je peux t’aider à configurer ça proprement aussi.

---
Voici une version **corrigée et complète** de ta commande `sshfs` pour qu’elle fonctionne **correctement avec Docker** :

---

### ✅ Commande recommandée

```bash
sshfs -p 22222 jellyreader@bratisla.freeboxos.fr:/mnt/media/plex ~/containers/jellyfin/remote-data \
  -o ro,allow_other,default_permissions,uid=$(id -u),gid=$(id -g),reconnect
```

---

### 🧠 Explication des options ajoutées

| Option                | Description                                                                         |
| --------------------- | ----------------------------------------------------------------------------------- |
| `ro`                  | Montage en lecture seule, comme tu avais initialement                               |
| `allow_other`         | Permet à Docker (ou tout autre utilisateur) d'accéder au système de fichiers FUSE   |
| `default_permissions` | Active la vérification standard des permissions Linux                               |
| `uid=$(id -u)`        | Donne au système de fichiers monté le même UID que l'utilisateur actuel (`freebox`) |
| `gid=$(id -g)`        | Même chose pour le GID                                                              |
| `reconnect`           | Autorise la reconnexion automatique en cas de déconnexion réseau                    |

---

### ⚠️ Vérification importante avant exécution

Dans le fichier `/etc/fuse.conf`, assure-toi que la ligne suivante **existe et n'est pas commentée** :

```bash
user_allow_other
```

> Si ce n’est pas le cas, ajoute-la puis **sauvegarde** le fichier :

```bash
sudo nano /etc/fuse.conf
```

---

### 🔁 Procédure complète

1. **Démonter proprement** le SSHFS s’il est encore actif :

   ```bash
   fusermount -u ~/containers/jellyfin/remote-data
   ```

2. **Remonter avec la commande corrigée** :

   ```bash
   sshfs -p 22222 jellyreader@bratisla.freeboxos.fr:/mnt/media/plex ~/containers/jellyfin/remote-data \
     -o ro,allow_other,default_permissions,uid=$(id -u),gid=$(id -g),reconnect
   ```

3. **Tester que Docker voit les fichiers** :

   ```bash
   docker run --rm -v "$PWD/remote-data:/data:ro" alpine ls /data
   ```

   Tu dois voir : `anime`, `cartoons`, etc.

4. **Redémarrer Jellyfin** :

   ```bash
   docker-compose down
   docker-compose up -d
   ```

5. **Vérifier dans le conteneur** :

   ```bash
   docker exec -it jellyfin ls /data
   ```

---

Si tu veux automatiser ce montage au démarrage, je peux aussi te générer un service `systemd` adapté à ce cas d’usage avec SSHFS.

