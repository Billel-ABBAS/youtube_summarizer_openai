from youtube_transcript_api import YouTubeTranscriptApi
import openai
import streamlit as st
import re
from langdetect import detect
from googleapiclient.discovery import build
import yt_dlp
import os
import pandas as pd

# Configuration de l'API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Remplacez par votre clé API YouTube valide
API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=API_KEY)

def extract_video_id(youtube_url):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/.*v=([^&]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?&]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return None

def list_available_transcripts(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_transcripts = {}
        for transcript in transcript_list:
            language = transcript.language
            language_code = transcript.language_code
            if transcript.is_translatable:
                available_transcripts[language] = language_code
        return available_transcripts
    except Exception as e:
        print(f"Erreur lors de la récupération des listes des sous-titres : {e}")
        return None

def get_transcript(video_id, language_code):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        return transcript
    except Exception as e:
        print(f"Erreur lors de la récupération des sous-titres : {e}")
        return None

def translate_text(text, target_language='fr'):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant and translator."},
            {"role": "user", "content": f"Please translate the following text to {target_language}: {text}"}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Please summarize the following text in a maximum of 15 lines and provide a title for the topic discussed: {text}"}
        ],
        max_tokens=500
    )
    return response['choices'][0]['message']['content'].strip()

def process_video(video_id, language_code):
    transcript = get_transcript(video_id, language_code)
    if not transcript:
        return "Impossible de récupérer les sous-titres."

    transcript_text = ' '.join([entry['text'] for entry in transcript])

    detected_language = detect(transcript_text)
    
    summary = summarize_text(transcript_text)

    translated_summary = translate_text(summary, 'fr')
    
    return translated_summary

def get_video_details(video_id):
    request = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=video_id
    )
    response = request.execute()
    video_info = response['items'][0]
    snippet = video_info['snippet']
    statistics = video_info['statistics']
    details = {
        "Titre": snippet['title'],
        "Description": snippet['description'],
        "Nom de la chaîne": snippet['channelTitle'],
        "Date de publication": snippet['publishedAt'],
        "Tags": ", ".join(snippet.get('tags', [])),
        "Catégorie": snippet.get('categoryId', 'N/A'),
        "Vues": statistics.get('viewCount', 'N/A'),
        "Likes": statistics.get('likeCount', 'N/A'),
        "Commentaires": statistics.get('commentCount', 'N/A')
    }
    return details

def generate_video_script(topic):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative scriptwriter."},
            {"role": "user", "content": f"Create a detailed script for a YouTube video about {topic}."}
        ],
        max_tokens=1000
    )
    return response['choices'][0]['message']['content'].strip()

def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': '/usr/bin/ffmpeg',  # Remplacez par le chemin correct si nécessaire
        'outtmpl': 'audio.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([youtube_url])
    
    # Vérifiez si le fichier a été téléchargé et converti
    if os.path.exists("audio.mp3"):
        with open("audio.mp3", "rb") as file:
            btn = st.download_button(
                label="Télécharger l'audio",
                data=file,
                file_name="audio.mp3",
                mime="audio/mpeg"
            )
        return btn
    else:
        st.error("Erreur lors du téléchargement ou de la conversion de l'audio.")

# Fonction pour appliquer des styles CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Ajout du fichier CSS personnalisé
local_css("style.css")


# Fonction pour appliquer des styles CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Ajout du fichier CSS personnalisé
local_css("style.css")

# Interface utilisateur Streamlit
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>YouTube Service Hub</h1>", unsafe_allow_html=True)

# Ajouter une image représentative centrée en dessous du titre
st.markdown("<div class='centered-image'>", unsafe_allow_html=True)
st.image("representative_image.jpeg", width=700)
st.markdown("</div>", unsafe_allow_html=True)


st.sidebar.title("Options")
option = st.sidebar.selectbox(
    "Choisissez une option",
    ["Résumé Vidéo", "Détails de la Vidéo", "Génération de Script", "Téléchargement Audio", "À propos"]
)

if option == "Résumé Vidéo":
    st.subheader("Entrez l'URL de la vidéo YouTube")
    youtube_url = st.text_input("URL de la vidéo", "")
    
    if st.button("Générer le résumé"):
        video_id = extract_video_id(youtube_url)
        if video_id:
            available_transcripts = list_available_transcripts(video_id)
            if available_transcripts:
                selected_language = st.selectbox(
                    "Choisissez la langue des sous-titres",
                    options=list(available_transcripts.keys())
                )
                if selected_language:
                    language_code = available_transcripts[selected_language]
                    summary = process_video(video_id, language_code)
                    st.write(summary)
            else:
                st.write("Aucun sous-titre disponible pour cette vidéo.")
        else:
            st.write("Lien vidéo invalide. Veuillez entrer un lien YouTube valide.")

elif option == "Détails de la Vidéo":
    st.subheader("Entrez l'URL de la vidéo YouTube")
    youtube_url = st.text_input("URL de la vidéo", "")
    
    if st.button("Afficher les détails"):
        video_id = extract_video_id(youtube_url)
        if video_id:
            details = get_video_details(video_id)
            df = pd.DataFrame([details])
            st.dataframe(df.style.set_properties(**{
                'background-color': '#f4f4f4',
                'color': '#333',
                'border-color': '#ddd',
                'text-align': 'left',
                'font-size': '14px',
            }))
        else:
            st.write("Lien vidéo invalide. Veuillez entrer un lien YouTube valide.")

elif option == "Génération de Script":
    st.subheader("Entrez le sujet de la vidéo")
    topic = st.text_input("Sujet de la vidéo", "")
    
    if st.button("Générer le script"):
        script = generate_video_script(topic)
        st.write(script)

elif option == "Téléchargement Audio":
    st.subheader("Entrez l'URL de la vidéo YouTube")
    youtube_url = st.text_input("URL de la vidéo", "")
    
    if st.button("Télécharger l'audio"):
        download_audio(youtube_url)

elif option == "À propos":
    st.subheader("À propos de cette application")
    st.write("Cette application propose divers services autour des vidéos YouTube, y compris la génération de résumés, l'affichage des détails de la vidéo, la création de scripts et le téléchargement d'audio.")

st.markdown("<hr><footer style='text-align: center;'>© 2024 YouTube Service Hub</footer>", unsafe_allow_html=True)

