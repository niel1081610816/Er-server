
# SALVA




import streamlit as st
from supabase import create_client

url = "https://kjqncgasirjzilovibat.supabase.co"
key = "LA_TUA_KEY"

supabase = create_client(url, key)

st.title("Titolo del sito")

nome = st.text_input("Nome")
ruolo = st.selectbox("Chi sei?", ["produttore", "cantante", "entrambi"])
genere = st.selectbox("Genere", ["uomo", "donna", "nessuno dei due", "preferisco non rispondere"])

# 👉 SALVATAGGIO
if st.button("Salva il profilo"):
    supabase.table("utenti").insert({
        "nome": nome,
        "genere": genere,
        "ruolo": ruolo
    }).execute()

    st.success("Profilo salvato!")

# 👉 MATCH FUNCTION (SEMPLICE)
def match(user, others):
    risultati = []
    for u in others:
        score = 0
        if user["genere"] == u["genere"]:
            score += 50
        if user["ruolo"] != u["ruolo"]:
            score += 50
        risultati.append((u, score))
    return sorted(risultati, key=lambda x: x[1], reverse=True)

# 👉 PRENDI DATI
response = supabase.table("utenti").select("*").execute()

if response.data and len(response.data) > 1:
    current_user = response.data[-1]

    risultati = match(current_user, response.data)

    st.subheader("Collaboratori suggeriti")

    for u, score in risultati:
        if u["nome"] != current_user["nome"]:
            st.write(f"{u['nome']} → compatibilità: {score}%")

else:
    st.write("Inserisci almeno 2 utenti per vedere i match")


