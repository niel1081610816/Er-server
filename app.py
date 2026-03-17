
import streamlit as st
from supabase import create_client

# ====== CONFIG SUPABASE ======
url = "https://TUO_PROGETTO.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98"

supabase = create_client(url, key)

st.title("🎧 Music Collaboration Platform")

# ====== CREAZIONE PROFILO ======
nome = st.text_input("Nome artista")

ruolo = st.selectbox(
    "Chi sei?",
    ["produttore", "cantante", "entrambi"]
)

genere = st.multiselect(
    "Generi musicali",
    ["pop","rock","hiphop","trap","edm","techno","house","indie","jazz","metal"]
)

bpm = st.slider("BPM preferito", 60, 200, 120)

audio_file = st.file_uploader("Carica traccia MP3", type=["mp3"])


# ====== SALVATAGGIO PROFILO ======
if st.button("Salva profilo"):

    audio_url = None

    if audio_file is not None:
        file_bytes = audio_file.read()

        supabase.storage.from_("audio").upload(
            f"{nome}.mp3",
            file_bytes
        )

        audio_url = supabase.storage.from_("audio").get_public_url(f"{nome}.mp3")

    supabase.table("utenti").insert({
        "nome": nome,
        "ruolo": ruolo,
        "generi": genere,
        "bpm": bpm,
        "audio_url": audio_url
    }).execute()

    st.success("Profilo salvato!")



# ====== MATCHING ======
def match(user, others):

    risultati = []

    for u in others:

        if u["nome"] == user["nome"]:
            continue

        score = 0

        # compatibilità generi
        common = set(user["generi"]).intersection(set(u["generi"]))
        if common:
            score += len(common) * 20

        # compatibilità bpm
        if abs(user["bpm"] - u["bpm"]) < 10:
            score += 30

        # ruolo complementare
        if user["ruolo"] != u["ruolo"]:
            score += 30

        risultati.append((u, score))

    risultati = [r for r in risultati if r[1] >= 40]

    return sorted(risultati, key=lambda x: x[1], reverse=True)



# ====== MOSTRA COLLABORATORI ======
response = supabase.table("utenti").select("*").execute()

if response.data:

    current_user = response.data[-1]

    risultati = match(current_user, response.data)

    st.subheader("🔥 Collaboratori suggeriti")

    # filtri
    soglia = st.slider("Compatibilità minima", 0, 100, 40)

    search = st.text_input("Cerca nome artista")

    for u, score in risultati:

        if score < soglia:
            continue

        if search and search.lower() not in u["nome"].lower():
            continue

        st.write(f"🎤 {u['nome']} — Compatibilità: {score}%")

        if u["audio_url"]:
            st.audio(u["audio_url"])
