import tkinter as tk
from pytube import YouTube
import ssl
import warnings
import customtkinter
from moviepy.editor import AudioFileClip # type: ignore
import threading



# Resio problem sa ssl i greskom vezano za sertifikat
# def _fixed_load_windows_store_certs(self, storename, purpose):
#     certs = bytearray()
#     try:
#         for cert, encoding, trust in ssl.enum_certificates(storename):
#             # CA certs are never PKCS#7 encoded
#             if encoding == "x509_asn":
#                 if trust is True or purpose.oid in trust:
#                     try:
#                         self.load_verify_locations(cadata=cert)
#                         certs.extend(cert)
#                     except ssl.SSLError:
#                         warnings.warn("Bad certificate in Windows certificate store")
#     except PermissionError:
#         warnings.warn("unable to enumerate Windows certificate store")
#     return certs
# ssl.SSLContext._load_windows_store_certs = _fixed_load_windows_store_certs

def clear_text():
    polje_za_link.delete(0, tk.END)

def progres_traka(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    procenat_kompletnosti = bytes_downloaded / total_size * 100
    per = str(int(procenat_kompletnosti))
    chunk_size = len(chunk)
    pPercentage.configure(text=f'{per}% - {chunk_size} bytes')
    pPercentage.update()
    progres_bar.set(float(procenat_kompletnosti) / 100)
    app.update_idletasks()

# Funkcija za preuzimanje i konverziju videa u mp3
def download_as_mp3():
    try:
        # Dobijanje linka od korisnika
        video_url = polje_za_link.get()
        ytobjects = YouTube(video_url, on_progress_callback=progres_traka)
        video = ytobjects.streams.filter(only_audio=True).first().download()
    
        

        # Konverzija videa u mp3 u posebnoj niti
        convert_thread = threading.Thread(target=convert_to_mp3, args=(video,))
        convert_thread.start() #pocinje chunk da radi
        uspesno_lbl.configure(text="Konvertuje se u mp3.....", text_color="red")
        convert_thread.join()  #zavrsava chunk da radi

        # Prikazivanje poruke o uspehu
        title.configure(text=ytobjects.title, text_color="white")
        clear_text()
        uspesno_lbl.configure(text="Preuzimanje i konverzija u mp3 zavrseni", text_color="green")
        progres_bar.set(0)
        pPercentage.configure(text="0% - 0 bytes")
        
        
    except Exception as e:
        # Prikazivanje poruke o grešci
        uspesno_lbl.configure(text=f"Greška: {e}")

def convert_to_mp3(video):
    try:
        audio_clip = AudioFileClip(video)
        audio_clip.write_audiofile(video.replace('.mp4', '.mp3'))
        audio_clip.close()
    except Exception as e:
        uspesno_lbl.configure(text=f"Greška pri konverziji: {e}")

# Funkcija za pokretanje preuzimanja u posebnoj niti
def start_download():
    video_url = polje_za_link.get()
    if video_url == "":
        uspesno_lbl.configure(text="Morate uneti link!", text_color="red")
        return

    download_thread = threading.Thread(target=download_as_mp3)
    download_thread.start()

# Pokretanje aplikacije
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("700x450")
app.title("Video2mp3 Maksa")

title = customtkinter.CTkLabel(app, text="Unesi link!", font=('Roboto', 20))
title.pack(padx=10, pady=10)

url_linka = tk.StringVar()
polje_za_link = customtkinter.CTkEntry(app, width=350, height=35, textvariable=url_linka, placeholder_text="Unesi link", placeholder_text_color="white")
polje_za_link.pack()

# Label za zavrseno preuzimanje 
uspesno_lbl = customtkinter.CTkLabel(app, text="", wraplength=500, font=('Robroto', 25))
uspesno_lbl.pack(padx=15, pady=15)

download_btn = customtkinter.CTkButton(app, text="Download", width=100, height=30, command=start_download)
download_btn.pack(padx=15, pady=15)

pPercentage = customtkinter.CTkLabel(app, text="0% - 0 bytes")
pPercentage.pack()

progres_bar = customtkinter.CTkProgressBar(app, width=400, height=20)
progres_bar.set(0)
progres_bar.pack(padx=10, pady=10)

info_label = customtkinter.CTkLabel(app, text="Ovo je aplikacija za skidanje i konverziju videa sa You Tube , linkovi sa drugih sajtova nisu podrzani i prikazace gresku", font=('Roboto', 15), text_color="yellow", wraplength=300)
info_label.pack(padx=15, pady=15)

app.mainloop()
