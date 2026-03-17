"""
Semplice pipeline: audio -> trascrizione (faster-whisper) -> traduzione (googletrans) -> TTS (pyttsx3 o gTTS)

Descrizione:
Questo script permette di prendere un segnale audio (da file o registrato dal microfono), trascriverlo in testo
usando il modello "faster-whisper", tradurre il testo in un'altra lingua e riprodurre (o salvare) il risultato via TTS.

Flusso principale:
1. (opzionale) registra dal microfono se --audio non è fornito
2. trascrive l'audio con faster-whisper
3. traduce il testo con googletrans (se installato)
4. legge il testo tradotto con pyttsx3 (offline) e opzionalmente salva un MP3 con gTTS

Requisiti (installare prima se necessario):
- faster-whisper
- googletrans==4.0.0-rc1   (opzionale — per la traduzione online)
- pyttsx3                  (opzionale — per sintesi vocale offline)
- gTTS                     (opzionale — per salvare MP3 via Google TTS)
- numpy, sounddevice, soundfile (opzionali — per registrazione da microfono)

Note:
- Su Windows potrebbe essere necessario configurare i permessi del microfono e i driver audio.
- Il parametro --model-path può puntare a una cartella locale (es. model-cache/...) o al nome di un modello supportato.

Esempio d'uso:
    python main.py --audio path\to\audio.wav --target-lang en --model-path model-cache\models--Systran--faster-whisper-base
    python main.py --target-lang it   # registra dal microfono se --audio non è fornito

"""

import argparse
import os
import sys
import tempfile
import threading
import queue
import time
import asyncio
import inspect

# Import opzionali: forniscono funzionalità addizionali. Se mancanti, lo script informa e si adatta.
try:
    from faster_whisper import WhisperModel
except Exception as e:
    # faster-whisper è essenziale per la trascrizione; se manca fermiamo l'esecuzione.
    print("Import error: faster_whisper non trovato. Installa 'faster-whisper'.", file=sys.stderr)
    raise

try:
    from googletrans import Translator
except Exception:
    # googletrans è opzionale: se non c'è il codice salta la traduzione e mantiene il testo originale.
    print("Attenzione: googletrans non trovato. Installa 'googletrans==4.0.0-rc1' per la traduzione.")
    Translator = None

try:
    import pyttsx3
except Exception:
    # pyttsx3 fornisce la riproduzione vocale offline. Se manca, l'utente può comunque salvare MP3 con gTTS.
    print("Attenzione: pyttsx3 non trovato. Installa 'pyttsx3' per la riproduzione vocale.")
    pyttsx3 = None

try:
    from gtts import gTTS
except Exception:
    # gTTS è opzionale e permette di salvare file MP3 usando il servizio Google TTS.
    gTTS = None

try:
    import numpy as np
except Exception:
    print("Attenzione: numpy non trovato. Installare 'numpy' per la registrazione audio.")
    np = None

try:
    import sounddevice as sd
    import soundfile as sf
except Exception:
    # Se queste mancano la registrazione dal microfono non sarà disponibile.
    sd = None
    sf = None


def transcribe_audio(model_path, audio_path, device="cpu"):
    """Trascrive un file audio usando faster-whisper.

    Args:
        model_path (str): percorso al modello o nome del modello (es. 'small').
        audio_path (str): percorso al file audio (WAV, MP3, ecc.).
        device (str): 'cpu' o 'cuda'.

    Returns:
        tuple: (testo_trascritto, lingua_rilevata)
    """
    # Carica il modello (l'istanza gestisce il caricamento in memoria)
    model = WhisperModel(model_path, device=device)

    # Esegui la trascrizione; 'segments' è un iterabile di segmenti con testo e timestamp
    segments, info = model.transcribe(audio_path, beam_size=5)

    # Unisce i segmenti in un unico testo
    text = "".join([s.text for s in segments])

    # 'info' può contenere metadati come la lingua rilevata
    lang = getattr(info, "language", None)

    return text.strip(), lang


def translate_text(text, target_lang):
    """Traduce il testo in target_lang.

    Gestisce sia librerie sincrone che coroutine (se la libreria di traduzione
    fornisce un'API async). Se viene restituita una coroutine, la esegue e ritorna
    il risultato atteso.
    """
    if Translator is None:
        raise RuntimeError("googletrans non è disponibile")

    translator = Translator()
    try:
        res = translator.translate(text, dest=target_lang)
    except TypeError:
        # Alcune implementazioni richiedono parametri diversi; riproviamo senza 'dest'
        res = translator.translate(text, target_lang)

    # Se la chiamata ha restituito una coroutine/awaitable, eseguila
    if inspect.isawaitable(res):
        try:
            # asyncio.run è la soluzione più semplice in uno script sincrono
            res = asyncio.run(res)
        except RuntimeError:
            # Se c'è già un loop in esecuzione (es. ambienti particolari), creare
            # un nuovo loop in thread separato
            loop = asyncio.new_event_loop()
            try:
                res = loop.run_until_complete(res)
            finally:
                loop.close()

    # res può essere singolo oggetto o lista di oggetti
    if isinstance(res, list):
        parts = [getattr(r, "text", str(r)) for r in res]
        return " ".join(parts)

    return getattr(res, "text", str(res))


def speak_text_pyttsx3(text):
    """Riproduce il testo utilizzando pyttsx3 (sintesi vocale offline).

    pyttsx3 gestisce l'output del sistema (casse) automaticamente.
    """
    if pyttsx3 is None:
        raise RuntimeError("pyttsx3 non è disponibile")

    engine = pyttsx3.init()
    # Si possono settare voce, volume, rate qui se necessario.
    engine.say(text)
    engine.runAndWait()


def save_mp3_gtts(text, target_lang, file_path):
    """Salva il testo come file MP3 usando gTTS (Google Text-to-Speech).

    Args:
        text (str): testo da convertire in parlato.
        target_lang (str): codice lingua (es. 'en', 'it') per la pronuncia.
        file_path (str): percorso del file MP3 da creare.
    """
    if gTTS is None:
        raise RuntimeError("gTTS non è disponibile")

    tts = gTTS(text=text, lang=target_lang)
    tts.save(file_path)
    print(f"File MP3 salvato in: {file_path}")


def record_from_mic(samplerate=16000, channels=1):
    """Registra audio dal microfono fino a quando l'utente preme Enter.

    La funzione usa sounddevice per l'acquisizione e soundfile per salvare un WAV temporaneo.
    Restituisce il percorso del file WAV creato (nome file temporaneo).

    Nota: l'audio viene registrato in memoria prima di essere scritto su disco; non è ottimizzato per registrazioni molto lunghe.
    """
    if sd is None or sf is None or np is None:
        raise RuntimeError("Per registrare dal microfono installa 'sounddevice', 'soundfile' e 'numpy'.")

    frames = []  # lista di blocchi acquisiti dal callback

    def callback(indata, frames_count, time, status):
        # callback chiamato dal thread audio: memorizza una copia del buffer
        if status:
            # Segnala eventuali problemi (underrun/overflow)
            print(status, file=sys.stderr)
        frames.append(indata.copy())

    print("Avvio registrazione: premi Enter per terminare...")
    # Apri lo stream di input; il callback verrà chiamato a ogni blocco
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
        try:
            # Attendi l'input dell'utente (Enter) per terminare la registrazione
            input()
        except KeyboardInterrupt:
            # Permetti la terminazione con Ctrl-C
            pass

    if not frames:
        raise RuntimeError("Nessun dato registrato dal microfono.")

    # Concatena i blocchi in un unico array numpy (frames ha shape (n_block, block_samples, channels))
    audio = np.concatenate(frames, axis=0)

    # Crea un file temporaneo .wav e scrive l'audio (soundfile accetta float32 o int16)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.close()
    sf.write(tmp.name, audio, samplerate)
    # print(f"Registrazione salvata temporaneamente in: {tmp.name}")
    return tmp.name


def transcribe_worker(q_audio, q_text, model_path, device):
    """Thread worker: prende percorsi audio da q_audio, trascrive e mette (text, detected_lang) in q_text."""
    while True:
        audio_path = q_audio.get()
        if audio_path is None:
            # segnala terminazione al prossimo stadio
            q_text.put(None)
            q_audio.task_done()
            break
        try:
            text, detected_lang = transcribe_audio(model_path, audio_path, device=device)
            q_text.put((text, detected_lang))
        except Exception as e:
            print("Errore nella trascrizione (thread):", e, file=sys.stderr)
            q_text.put(("", None))
        finally:
            q_audio.task_done()


def translate_and_tts_worker(q_text, target_lang, save_mp3_path=None):
    """Thread worker: prende (text, detected_lang) da q_text, traduce (se possibile) e legge/salva audio."""
    while True:
        item = q_text.get()
        if item is None:
            q_text.task_done()
            break
        text, detected_lang = item
        # Traduzione (se disponibile)
        if Translator is None:
            translated = text
        else:
            try:
                translated = translate_text(text, target_lang)
            except Exception as e:
                print("Errore durante la traduzione (thread):", e, file=sys.stderr)
                translated = text

        print("Testo tradotto (thread):")
        print(translated)

        # Riproduzione offline con pyttsx3 (se disponibile)
        if pyttsx3 is not None:
            try:
                speak_text_pyttsx3(translated)
            except Exception as e:
                print("Errore TTS pyttsx3 (thread):", e, file=sys.stderr)

        # Salvataggio opzionale MP3 (gTTS)
        if save_mp3_path:
            try:
                save_mp3_gtts(translated, target_lang, save_mp3_path)
            except Exception as e:
                print("Errore salvataggio MP3 (thread):", e, file=sys.stderr)

        q_text.task_done()


def main():
    """Main aggiornato: avvia tre thread (registrazione, trascrizione, traduzione/TTS) e coordina la pipeline."""
    target_lang = input("Inserisci il codice lingua di destinazione per la traduzione (es. en, it, fr): \n")

    # code per modello e device (puoi modificarli se vuoi usare cuda)
    model_path = "small"
    device = "cpu"

    # code opzionale per salvare MP3
    save_mp3_path = None

    # Code: queue per passare dati tra i thread
    q_audio = queue.Queue()
    q_text = queue.Queue()

    # Avvia thread worker
    t_transcribe = threading.Thread(target=transcribe_worker, args=(q_audio, q_text, model_path, device), daemon=True)
    t_translate = threading.Thread(target=translate_and_tts_worker, args=(q_text, target_lang, save_mp3_path), daemon=True)

    t_transcribe.start()
    t_translate.start()

    temp_file_created = False
    audio_path = None

    try:
        # Registra dal microfono in main thread (puoi spostare anche questo in un thread se preferisci)
        audio_path = record_from_mic(samplerate=16000, channels=1)
        temp_file_created = True

        # Invia il file registrato alla coda per la trascrizione
        q_audio.put(audio_path)

        # Segnala che non ci sono altri file in arrivo
        q_audio.put(None)

        # Attendi che tutte le attività siano completate
        q_audio.join()
        q_text.join()

        # Piccola pausa per permettere ai thread daemon di terminare pulitamente
        time.sleep(0.1)

    except Exception as e:
        print("Errore nella pipeline principale:", e, file=sys.stderr)
    finally:
        # Pulisce file temporanei
        if temp_file_created and audio_path and os.path.isfile(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass


if __name__ == "__main__":
    main()