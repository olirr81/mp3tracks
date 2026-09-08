import os
import glob
from audio_separator.separator import Separator

input_dir = "input"
output_dir = "output"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Buscar todos los formatos de audio soportados
extensions = ("*.mp3", "*.wav", "*.flac", "*.m4a")
audio_files = []
for ext in extensions:
    audio_files.extend(glob.glob(os.path.join(input_dir, ext)))

if not audio_files:
    print("❌ No se encontraron archivos de audio en la carpeta 'input/'.")
    exit(1)

print(f"📁 Encontrados {len(audio_files)} archivo(s) para procesar.")

for index, target_audio in enumerate(audio_files, 1):
    file_name = os.path.basename(target_audio)
    song_name = os.path.splitext(file_name)[0]
    print(f"\n==========================================")
    print(f"🎵 [{index}/{len(audio_files)}] Procesando: {file_name}")
    print(f"==========================================")

    # Carpeta específica para cada canción dentro de output/
    song_output_dir = os.path.join(output_dir, song_name)
    os.makedirs(song_output_dir, exist_ok=True)

    try:
        # 1. Separación 6 stems principal (Demucs)
        print("🔹 Paso 1/3: Extrayendo 6 stems principales (htdemucs_6s)...")
        sep = Separator(output_dir=song_output_dir, output_format="wav")
        sep.load_model("htdemucs_6s.yaml")
        stems = sep.separate(target_audio)

        # Localizar las pistas de guitarra y batería recién creadas
        guitar_file = next((os.path.join(song_output_dir, f) for f in stems if "guitar" in f.lower()), None)
        drums_file = next((os.path.join(song_output_dir, f) for f in stems if "drums" in f.lower()), None)

        # 2. Desglose de Guitarras (Lead vs Rhythm)
        if guitar_file and os.path.exists(guitar_file):
            print("🔹 Paso 2/3: Descomponiendo guitarras (UVR-MDX-NET-Guitar)...")
            guitars_out = os.path.join(song_output_dir, "Guitarras_Desglosadas")
            os.makedirs(guitars_out, exist_ok=True)
            
            sep_g = Separator(output_dir=guitars_out, output_format="wav")
            sep_g.load_model("UVR-MDX-NET-Guitar.onnx")
            sep_g.separate(guitar_file)

        # 3. Desglose de Batería (Elementos de percusión)
        if drums_file and os.path.exists(drums_file):
            print("🔹 Paso 3/3: Descomponiendo batería (kuielab_a_drums)...")
            drums_out = os.path.join(song_output_dir, "Bateria_Desglosada")
            os.makedirs(drums_out, exist_ok=True)
            
            sep_d = Separator(output_dir=drums_out, output_format="wav")
            sep_d.load_model("kuielab_a_drums.onnx")
            sep_d.separate(drums_file)

        print(f"✅ Canción '{song_name}' procesada con éxito.")

    except Exception as e:
        print(f"❌ Error procesando {file_name}: {str(e)}")
        continue

print("\n🚀 ¡Todas las canciones se han procesado! Revisa la pestaña Actions para descargar el archivo ZIP.")
