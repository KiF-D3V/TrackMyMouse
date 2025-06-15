# utils/math_utils.py
"""
Ce module fournit des fonctions mathématiques utilitaires pour l'application.
"""

import math
from typing import Tuple

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calcule la distance euclidienne entre deux points.

    Args:
        p1 (Tuple[float, float]): Le premier point (x1, y1).
        p2 (Tuple[float, float]): Le second point (x2, y2).

    Returns:
        float: La distance calculée entre les deux points.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.hypot(dx, dy)