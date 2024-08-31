# Utiliser une image de base Python légère
FROM python:3.8-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /home/app

# Mettre à jour les paquets et installer les dépendances nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends nano unzip curl ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copier le fichier des dépendances Python et installer les modules requis
COPY requirements.txt /home/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers de l'application dans le répertoire de travail
COPY . /home/app/

# Exposer le port attendu par Render
EXPOSE 10000

# Définir la commande par défaut pour démarrer l'application Streamlit
CMD ["streamlit", "run", "main.py", "--server.port", "10000", "--server.enableCORS", "false"]








