import os
import streamlit as st
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder

# Page Configuration
st.set_page_config(page_title="Crowdsourced Translator", page_icon="🗣️", layout="centered")

st.title("🗣️ Collaborative Mother Tongue Translator")
st.write("Translate words instantly using text or voice recordings!")

DB_FILE = "dictionary.txt"

# Default starter vocabulary
DEFAULT_VOCAB = """english,swahili,kikuyu
food,chakula,irio
walk,tembea,thie
sing,imba,ina
run,kimbia,teng'era
write,andika,andika
beautiful,mrembo,muthaka
drink,nyua,nyua
leg,mguu,kuguru
teeth,meno,magego
nose,pua,iniuru
head,kichwa,mutwe
stomach,tumbo,nda
tongue,ulimi,rurimi 
baby,mtoto,mwana
mother,mama,maitu
father,baba,baba
grandfather,babu,guka
grandmother,nyanya,cucu"""
admit,kubali,koingeria
admonish,onya,kotetia
adolescent,kijana,kahe
adorn,pamba,kogemia
adroit,hodari,moge
adulate,sifu,kohenereria
adultery,uzinzi,koiya muka
advance,tangulia,kotongoria
advantage,faida,ngerereri
adversity,shida,ruo
advertise,tangaza,koleha uhoro
advice,ushauri,shira
advise,shauri,kochira
adviser,mshauri,mchiri
affair,jambo,uhoro
affection,upendo,lwendo
afflict,tesa,kokomaka
affliction,taabu,sena
affront,matusi,irumi
afraid,ogopa,koitigera
after,baada ya,suza wa
afterwards,baadaye,ninge
afternoon,alasiri,mialaho
after to-morrow,kesho kutwa,oke
again,tena,ninge
against,dhidi ya,igoro rya
agitate,tingisha,koinainia
ago,zamani,tene
agonize,teseka,kotwekana
agree,kubaliana,koiguana
ahead,mbele,mbele
aid,saidia,koteizia
aim,shabaha,wazi
air,hewa,heho
alike,sawa,iganaine
aliment,chakula,irio
alive,hai,gima
all,wote,ose
allow,ruhusu,kotiga
aloud,kwa sauti,konegena mno
already,tayari,reu
also,pia,na
alter,badilisha,kogalula
although,ingawa,ona
altogether,kabisa,ose mno
always,kila wakati,mosenya yose
amazed,shangaa,komaka
among,katikati ya,katanati ya
amulet,hirizi,kezito
amuse,furahisha,koseka
amusement,mchezo,mzexo
ancestors,wahenga,maguka
ancient,wa kale,mzuri
and,na,na
angel,malaika,ngoma
anger,hasira,kesori
angle,pembe,lwere
angry,kasirika,korakala
animal,mnyama,nyamo
animalcule,kijidudu,kanyamo
ankle,kiwiko cha mguu,ndira ya kogoro
announce,tangaza,koleha uhoro
annoy,kasirisha,kondakaria
annul,futa,kohingura
anoint,paka mafuta,kobaka
another,nyingine,unge
answer,jibu,koetekia
ants,mchwa,saragu
antique,cha kale,zuri
antre,pango,ngurunga
anus,mkundu,mzuti
anvil,nyundo,ihiga
any,yoyote,wose
apart,kando,mwanya
ape,nyani,nogo
apparent,wazi,seri
appear,onekana,koonwo
appease,tuliza,kokiria

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_VOCAB)


def load_dictionary():
    vocab = []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[1:]:
            if line.strip():
                parts = line.strip().split(",")
                if len(parts) == 3:
                    vocab.append({
                        "english": parts[0].strip().lower(),
                        "swahili": parts[1].strip().lower(),
                        "kikuyu": parts[2].strip().lower()
                    })
    return vocab


dictionary = load_dictionary()

# Sidebar Setup
st.sidebar.header("Translation Options")
search_lang = st.sidebar.selectbox(
    "What language are you inputting?",
    options=["English", "Swahili", "Kikuyu"]
).lower()

# --- NEW SPEECH RECORDING SECTION ---
st.subheader("🎙️ Voice Translation")
st.write("Click record and speak your word clearly into your microphone:")

# This adds a live microphone recorder component
audio_record = mic_recorder(
    start_prompt="🔴 Start Recording",
    stop_prompt="⏹️ Stop Recording",
    key='recorder'
)

voice_text = ""
if audio_record:
    # Convert the raw bytes from the browser into an audio object Python can read
    try:
        r = sr.Recognizer()
        audio_data = sr.AudioData(audio_record['bytes'], sample_rate=44100, sample_width=2)

        # Use speech recognition engine
        if search_lang == "english":
            voice_text = r.recognize_google(audio_data, language="en-US")
        elif search_lang == "swahili":
            voice_text = r.recognize_google(audio_data, language="sw-KE")
        else:
            # Basic fallback for Kikuyu acoustics using localized matching
            voice_text = r.recognize_google(audio_data, language="en-KE")

        st.success(f"🗣️ Detected Audio: **\"{voice_text}\"**")
    except sr.UnknownValueError:
        st.warning("⚠️ Could not understand the audio. Please speak clearly and try again.")
    except Exception as e:
        st.error("🔬 Audio processing issue. Try typing the word below instead.")

st.markdown("---")

# Standard Search Box (Pre-filled if voice text is detected)
default_input = voice_text if voice_text else ""
user_input = st.text_input(f"Or type your {search_lang} phrase/word manually:", value=default_input).strip().lower()

# --- TRANSLATION LOGIC ---
missing_words = []

if user_input:
    words = user_input.split()
    translated_english = []
    translated_swahili = []
    translated_kikuyu = []
    found_any_missing = False

    for word in words:
        match = next((item for item in dictionary if item[search_lang] == word), None)
        if match:
            translated_english.append(match["english"])
            translated_swahili.append(match["swahili"])
            translated_kikuyu.append(match["kikuyu"])
        else:
            translated_english.append(f"[{word}]")
            translated_swahili.append(f"[{word}]")
            translated_kikuyu.append(f"[{word}]")
            if word not in missing_words:
                missing_words.append(word)
            found_any_missing = True

    st.subheader("Results:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**🇬🇧 English**\n\n {' '.join(translated_english).capitalize()}")
    with col2:
        st.markdown(f"**🇰🇪 Swahili**\n\n {' '.join(translated_swahili).capitalize()}")
    with col3:
        st.markdown(f"**🇰🇪 Kikuyu**\n\n {' '.join(translated_kikuyu).capitalize()}")

    if found_any_missing:
        st.error("⚠️ Some words are missing from our database!")
        with st.form("add_word_form", clear_on_submit=True):
            new_entries = []
            for missing in missing_words:
                st.write(f"#### Word: **{missing}**")
                eng_val = missing if search_lang == "english" else ""
                swa_val = missing if search_lang == "swahili" else ""
                kik_val = missing if search_lang == "kikuyu" else ""

                c1, c2, c3 = st.columns(3)
                with c1:
                    eng = c1.text_input(f"English:", value=eng_val, key=f"eng_{missing}").strip().lower()
                with c2:
                    swa = c2.text_input(f"Swahili:", value=swa_val, key=f"swa_{missing}").strip().lower()
                with c3:
                    kik = c3.text_input(f"Kikuyu:", value=kik_val, key=f"kik_{missing}").strip().lower()
                new_entries.append((eng, swa, kik))

            submit_btn = st.form_submit_button("💾 Save Translations to Database")
            if submit_btn:
                with open(DB_FILE, "a", encoding="utf-8") as f:
                    for eng, swa, kik in new_entries:
                        if eng and swa and kik:
                            f.write(f"\n{eng},{swa},{kik}")
                st.success("🎉 Database updated successfully!")
                st.rerun()
else:
    st.info("💡 Pro Tip: Select your input language on the left, then try the record button!")
