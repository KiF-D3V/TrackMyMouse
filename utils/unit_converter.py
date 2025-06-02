# utils/unit_converter.py

import locale
import datetime # Ajouté pour format_seconds_to_hms

def pixels_to_inches(pixels: float, dpi: float) -> float | None:
    """Convertit une distance en pixels en pouces."""
    if dpi and dpi > 0:
        return pixels / dpi
    return None

def pixels_to_meters(pixels: float, dpi: float) -> float | None:
    """Convertit une distance en pixels en mètres."""
    inches = pixels_to_inches(pixels, dpi)
    if inches is not None:
        return inches * 0.0254
    return None

def pixels_to_feet(pixels: float, dpi: float) -> float | None:
    """Convertit une distance en pixels en pieds."""
    inches = pixels_to_inches(pixels, dpi)
    if inches is not None:
        return inches / 12
    return None

def pixels_to_miles(pixels: float, dpi: float) -> float | None:
    """Convertit une distance en pixels en miles."""
    feet = pixels_to_feet(pixels, dpi)
    if feet is not None:
        return feet / 5280
    return None

def format_distance(distance_pixels: float, dpi: float, unit_system: str, current_language: str) -> tuple[str, str]:
    """
    Formate une distance donnée en pixels pour l'afficher dans le système d'unités spécifié.
    Prend en compte le DPI pour la conversion en unités réelles.
    Retourne la valeur formatée et l'unité.
    La notation décimale (point ou virgule) est ajustée en fonction de la langue.
    """
    if dpi is None or dpi == 0:
        return f"{distance_pixels:.0f}", "pixels" 

    formatted_value = 0
    unit = ""

    if unit_system == 'metric':
        distance_cm = pixels_to_meters(distance_pixels, dpi) * 100 if pixels_to_meters(distance_pixels, dpi) is not None else 0.0
        if distance_cm >= 100000:
            formatted_value = distance_cm / 100000
            unit = "km"
        elif distance_cm >= 100:
            formatted_value = distance_cm / 100
            unit = "m"
        else:
            formatted_value = distance_cm
            unit = "cm"
    elif unit_system == 'imperial':
        distance_inches = pixels_to_inches(distance_pixels, dpi) if pixels_to_inches(distance_pixels, dpi) is not None else 0.0
        if distance_inches >= 5280 * 12: # Check if it's more than 1 mile
            formatted_value = pixels_to_miles(distance_pixels, dpi) if pixels_to_miles(distance_pixels, dpi) is not None else 0.0
            unit = "miles"
        elif distance_inches >= 12: # Check if it's more than 1 foot
            formatted_value = pixels_to_feet(distance_pixels, dpi) if pixels_to_feet(distance_pixels, dpi) is not None else 0.0
            unit = "feet"
        else:
            formatted_value = distance_inches
            unit = "inches"
    else: # Fallback to pixels if unit_system is unrecognized
        formatted_value = distance_pixels
        unit = "pixels"

    # Ajuste la notation décimale en fonction de la langue
    try:
        if current_language == 'fr':
            locale.setlocale(locale.LC_ALL, 'fr_FR.utf8') 
            return locale.format_string("%.2f", formatted_value), unit
        else:
            return f"{formatted_value:.2f}", unit
    except locale.Error:
        return f"{formatted_value:.2f}", unit

def format_seconds_to_hms(total_seconds: float) -> str:
    """
    Formate un nombre total de secondes en une chaîne "HH:MM:SS".
    """
    if total_seconds is None:
        total_seconds = 0
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


if __name__ == '__main__':
    # Exemple d'utilisation pour le test
    dpi_value = 96.0
    pixels_value = 1000

    print(f"{pixels_value} pixels à {dpi_value} DPI:")
    print(f"  Inches: {pixels_to_inches(pixels_value, dpi_value):.4f}")
    print(f"  Meters: {pixels_to_meters(pixels_value, dpi_value):.4f}")
    print(f"  Feet: {pixels_to_feet(pixels_value, dpi_value):.4f}")
    print(f"  Miles: {pixels_to_miles(pixels_value, dpi_value):.8f}")

    # Exemple de formatage de distance
    print("\nFormatage des distances:")
    print(f"Distance (métrique, fr): {format_distance(50000, dpi_value, 'metric', 'fr')}")
    print(f"Distance (impérial, en): {format_distance(100000, dpi_value, 'imperial', 'en')}")
    print(f"Distance (impérial, en - pieds): {format_distance(2000, dpi_value, 'imperial', 'en')}")
    print(f"Distance (métrique, fr - cm): {format_distance(100, dpi_value, 'metric', 'fr')}")

    # Exemple de formatage de temps
    print("\nFormatage des temps:")
    print(f"Temps (3661s): {format_seconds_to_hms(3661)}")
    print(f"Temps (59s): {format_seconds_to_hms(59)}")
    print(f"Temps (7200s): {format_seconds_to_hms(7200)}")