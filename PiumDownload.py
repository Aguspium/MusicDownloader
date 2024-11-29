import yt_dlp
import pygame
import os
import pyperclip
from tkinter import filedialog
from tkinter import Tk
import threading
import time

pygame.init()

window_width = 700
window_height = 700
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("YouTube Video Downloader")

font = pygame.font.Font(None, 36)
input_font = pygame.font.Font(None, 28)

input_url = ""
message = "Introduce la URL"
save_dir = None
is_pasting = False
is_downloading = False
progress = 0


cursor_visible = True
last_cursor_time = time.time()


selected_button = None 

def download_video(url, save_path):
    global progress, is_downloading

    try:
        if not url.startswith("http"):
            url = f"ytsearch:{url}"  
        ydl_opts = {
            'format': 'bestaudio/bestvideo',
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'quiet': False,
            'progress_hooks': [progress_hook]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            is_downloading = True
            ydl.download([url])
    except Exception as e:
        global message
        message = f"Error: {str(e)}"
        is_downloading = False

def progress_hook(d):
    global progress
    if d['status'] == 'downloading':
        progress = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1)
    elif d['status'] == 'finished':
        progress = 1.0

def select_directory():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    return folder_selected

def paste_from_clipboard():
    try:
        return pyperclip.paste().strip()  
    except pyperclip.PyperclipException:
        return ""

def start_download_thread(url, save_path):
    """Inicia el hilo de descarga"""
    download_thread = threading.Thread(target=download_video, args=(url, save_path))
    download_thread.start()

def main():
    global input_url, message, save_dir, is_pasting, is_downloading, progress, cursor_visible, last_cursor_time, selected_button

    running = True
    while running:
        screen.fill((255, 255, 255))

        text = font.render(message, True, (0, 0, 0))
        screen.blit(text, (window_width // 2 - text.get_width() // 2, 70))

   
        max_text_width = 0  
        text_input = input_font.render(input_url, True, (70, 77, 77))
        screen.blit(text_input, (180, 110))  # Ubicación normal del texto

        current_time = time.time()
        if current_time - last_cursor_time >= 0.5:
            cursor_visible = not cursor_visible  
            last_cursor_time = current_time 

        if cursor_visible:
            cursor_x = 180 + text_input.get_width()  
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, 130), (cursor_x, 110), 2)

        if save_dir:
            save_text = font.render(f"Carpeta en: {save_dir}", True, (0, 0, 0))
            screen.blit(save_text, (window_width // 2 - save_text.get_width() // 2, 350))

      
        save_button_color = (0, 0, 0) if selected_button != "save" else (0, 255, 0)
        pygame.draw.rect(screen, save_button_color, (200, 200, 130, 50), 2)
        save_button_text = font.render("Directorio", True, (0, 0, 0))
        screen.blit(save_button_text, (200 + 10, 200 + 10))

        download_button_color = (0, 0, 128) if selected_button != "download" else (0, 255, 0)
        pygame.draw.rect(screen, download_button_color, (150, 270, 200, 50))
        download_button_text = font.render("Iniciar descarga", True, (255, 255, 255))
        screen.blit(download_button_text, (150 + 10, 270 + 10))

        if is_downloading:
            pygame.draw.rect(screen, (255, 0, 0), (80, 450, 400, 20))
            pygame.draw.rect(screen, (0, 255, 0), (80, 450, 400 * progress, 30))
            progress_text = font.render(f"{int(progress * 100)}%", True, (255, 255, 255))
            screen.blit(progress_text, (window_width // 2 - progress_text.get_width() // 2, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if save_dir and input_url:
                        start_download_thread(input_url, save_dir)  
                    else:
                        message = "Por favor selecciona una URL y directorio."
                elif event.key == pygame.K_BACKSPACE:
                    input_url = input_url[:-1]
                elif event.key == pygame.K_TAB:
                    input_url = paste_from_clipboard()  
                elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:  
                    pass  
                else:
                    input_url += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if 200 < pygame.mouse.get_pos()[0] < 300 and 200 < pygame.mouse.get_pos()[1] < 250:
                        save_dir = select_directory()
                        selected_button = "save"
                    elif 150 < pygame.mouse.get_pos()[0] < 350 and 270 < pygame.mouse.get_pos()[1] < 320:
                        if not save_dir:
                            message = "Debes seleccionar un directorio."
                        elif not input_url:
                            message = "Debes ingresar una URL o nombre de cancion."
                        else:
                            start_download_thread(input_url, save_dir) 
                            selected_button = "download"

            elif event.type == pygame.KEYUP:
                
                if event.key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]:
                    input_url = paste_from_clipboard()  

        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()

