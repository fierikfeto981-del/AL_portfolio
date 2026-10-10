from settings import *
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def import_image(*path, format='png', alpha=True):
    if not pygame.get_init():
        pygame.init()
    full_path = BASE_DIR.joinpath(*path).with_suffix(f'.{format}').resolve()
    image = pygame.image.load(str(full_path))
    if alpha:
        return image.convert_alpha()
    return image.convert()

def import_folder(*path):
    if not pygame.get_init():
        pygame.init()
    frames = []
    folder_path = BASE_DIR.joinpath(*path).resolve()
    for file_name in sorted(folder_path.iterdir(), key=lambda p: int(p.stem)):
        if file_name.is_file():
            frames.append(pygame.image.load(str(file_name)).convert_alpha())
    return frames

def audio_importer(*path):
    if not pygame.get_init():
        pygame.init()

    audio_dict = {}
    supported_extensions = ('.wav', '.mp3', '.ogg')
    folder_path = BASE_DIR.joinpath(*path).resolve()

    if not folder_path.exists():
        return audio_dict

    for file_path in sorted(folder_path.rglob('*')):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            audio_key = file_path.stem
            audio_dict[audio_key] = pygame.mixer.Sound(str(file_path))

    return audio_dict

def slice_spritesheet(path_str, frame_width=128, frame_height=128):
    """Memotong spritesheet horizontal/grid menjadi list frame individual."""
    if not pygame.get_init():
        pygame.init()
    sheet = pygame.image.load(path_str).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()
    frames = []
    cols = sheet_w // frame_width
    rows = sheet_h // frame_height
    for r in range(rows):
        for c in range(cols):
            x = c * frame_width
            y = r * frame_height
            frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
            frames.append(frame)
    return frames
