#Chemin vers le répertoire contenant les fichiers à supprimer
cd /data/history/
echo "Suppression des fichiers..."
find . -maxdepth 1 -type f -name *.json -exec rm -f {} \;

echo "Fichiers supprimés avec succès."
fi


echo "Liste des fichiers supprimés :"
find . -maxdepth 1 -type f -name *.json | xargs ls -l