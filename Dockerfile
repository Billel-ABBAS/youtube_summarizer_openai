# Utiliser une image de base Python légère
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /home/app

# Mettre à jour les paquets et installer les dépendances nécessaires, y compris ffmpeg pour le traitement vidéo
RUN apt-get update && \
    apt-get install -y --no-install-recommends nano unzip curl ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copier le fichier des dépendances Python et installer les modules requis
COPY requirements.txt /home/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers nécessaires de l'application dans le répertoire de travail du conteneur
COPY main.py /home/app/
COPY style.css /home/app/
COPY representative_image.jpeg /home/app/
# # Si vous avez des configurations Streamlit spécifiques, assurez-vous de les copier
# COPY .streamlit/config.toml /home/app/.streamlit/

# Exposer le port utilisé par Streamlit (5000 dans cet exemple)
EXPOSE 5000

# Définir la commande par défaut pour démarrer l'application Streamlit
CMD ["streamlit", "run", "main.py", "--server.port", "5000"]







