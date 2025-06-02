try:
    from screeninfo import get_monitors
    screen_available = True
except ImportError:
    screen_available = False
    print("La librairie 'screeninfo' n'est pas installée. La conversion en unités physiques sera moins précise.")

def get_primary_screen_info():
    if screen_available:
        monitors = get_monitors()
        if monitors:
            for monitor in monitors:
                if monitor.is_primary:
                    return monitor.width, monitor.height, monitor.width_mm / 10 if monitor.width_mm else None, monitor.height_mm / 10 if monitor.height_mm else None
            # Si aucun moniteur primaire n'est trouvé, utiliser le premier de la liste
            return monitors[0].width, monitors[0].height, monitors[0].width_mm / 10 if monitors[0].width_mm else None, monitors[0].height_mm / 10 if monitors[0].height_mm else None
    return None, None, None, None

def calculate_dpi(width_pixels, width_cm):
    if width_pixels and width_cm:
        width_inches = width_cm / 2.54
        return width_pixels / width_inches
    return None