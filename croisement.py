import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy.signal import find_peaks

# Charger le fichier audio avec soundfile
file_path = 'D:\\Ecole\\CS\\METZ2A\\Traitement audio\\audioprocessing\\audio_files\\croisement4.wav'  # Remplacez par le chemin de votre fichier
data, sample_rate = sf.read(file_path)

# Vérifier si le fichier est mono ou stéréo
if len(data.shape) > 1:
    data = data[:, 0]  # Prendre un seul canal si stéréo


def find_peaks_simple(x, height=None, distance=1, n_peaks=2):
    # Convertir en numpy array pour la manipulation
    x = np.array(x)
    
    # Liste pour stocker les indices des pics
    peaks = []
    
    # Trouver les maxima locaux
    for i in range(1, len(x) - 1):
        if x[i] > x[i-1] and x[i] > x[i+1]:  # Comparaison avec voisins
            if height is None or x[i] >= height:  # Filtre de hauteur
                peaks.append(i)
    
    # Filtrage par distance
    if distance > 1:
        # Liste finale de pics après filtrage de la distance
        filtered_peaks = []
        last_peak = -distance  # Initialise à une valeur inférieure à la distance minimale
        for peak in peaks:
            if peak - last_peak >= distance and len(filtered_peaks)<n_peaks:
                filtered_peaks.append(peak)
                last_peak = peak
        peaks = filtered_peaks
    
    if len(peaks)<n_peaks:
        peaks.append(peaks[-1]*(n_peaks-len(peaks)))
    return np.array(peaks)

# Normaliser le signal
data = data / np.max(np.abs(data))

# Paramètres FFT
n_fft = 2**13  # Taille de la fenêtre FFT
hop_length = round(0.001*sample_rate)  # Chevauchement
window = np.hanning(n_fft)  # Fenêtre de Hanning

# Calculer la FFT
frames = range(0, len(data) - n_fft, hop_length)
fft = np.array([np.fft.rfft(window * data[i:i + n_fft]) for i in frames])

# Magnitude spectrale
magnitude = np.abs(fft)

# Fréquences et temps associées
frequencies = np.fft.rfftfreq(n_fft, 1 / sample_rate)
times = np.arange(len(frames)) * hop_length / sample_rate

# Détection des fréquences dominantes
freqs_a = []
freqs_b = []
ampls_a=[]
ampls_b=[]
for frame in magnitude:
    peak1, peak2 = find_peaks_simple(frame, height=np.max(frame) * 0.1, n_peaks=2)  # Pics locaux significatifs
    #frame[peaks] est l'amplitude des pics
    #frequencies[peaks] est la frequence des pics
    ampl1, freq1  = frame[peak1], frequencies[peak1]
    ampl2, freq2 = frame[peak2], frequencies[peak2]

    if len(freqs_a)==0:
        ampls_a.append(ampl1)
        freqs_a.append(freq1)
        ampls_b.append(ampl2)
        freqs_b.append(freq2)
    elif np.abs(freq1 - freq2)<70:
        if np.abs(ampls_a[-1]-ampl1)<np.abs(ampls_b[-1]-ampl1):
            ampls_a.append(ampl1)
            freqs_a.append(freq1)
            ampls_b.append(ampl2)
            freqs_b.append(freq2)
        else:
            ampls_a.append(ampl2)
            freqs_a.append(freq2)
            ampls_b.append(ampl1)
            freqs_b.append(freq1)
    else:
        if np.abs(freq1-freqs_a[-1])<np.abs(freq1-freqs_b[-1]):
            freqs_a.append(freq1)
            ampls_a.append(ampl1)
            freqs_b.append(freq2)
            ampls_b.append(ampl2)
        else:
            freqs_a.append(freq2)
            ampls_a.append(ampl2)
            freqs_b.append(freq1)
            ampls_b.append(ampl1)
            


# Visualiser les fréquences dominantes au fil du temps
plt.figure(figsize=(12, 6))
plt.imshow(10 * np.log10(magnitude.T), origin="lower", aspect="auto",
           extent=[times.min(), times.max(), frequencies.min(), frequencies.max()],
           cmap="viridis")
plt.colorbar(label="Amplitude (dB)")
plt.title("Spectrogramme avec fréquences dominantes")
plt.xlabel("Temps (s)")
plt.ylabel("Fréquence (Hz)")

# Ajouter les fréquences dominantes
plt.scatter(times, freqs_a, color="red", label="Fréquences A", s=20)
plt.scatter(times, freqs_b, color="blue", label="Fréquences B", s=5)

plt.legend()
plt.show()
