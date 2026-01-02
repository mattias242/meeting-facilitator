from faster_whisper import WhisperModel

# Sätt upp modell
model_size = "base"
audio_fil = "din_ljudfil.mp3"

print(f"Laddar modell: {model_size}")
print(f"Transkriberar: {audio_fil}\n")

# Ladda modellen
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# Transkribera
segments, info = model.transcribe(
    audio_fil,
    language="sv",
    beam_size=5,
)

# Skriva ut och spara resultat
full_text = ""
print("Transkribering:\n")
for segment in segments:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
    full_text += segment.text + " "

# Spara till fil
with open("transkribering.txt", "w", encoding="utf-8") as f:
    f.write(full_text.strip())

print(f"\n✅ Transkribering sparad till transkribering.txt")
print(f"Språk: {info.language}")
