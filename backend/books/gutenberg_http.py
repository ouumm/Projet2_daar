"""Petite fonction HTTP avec retries pour les indisponibilites temporaires de Gutenberg.

Simple a tester independamment de Django. Une requete GET qui echoue
est reessayee apres une courte pause, sans toucher aux donnees importees.
"""
import time
import requests


def get_with_retries(session, url, timeout=60, attempts=4, delay=5, log=None):
    """Renvoie une reponse HTTP valide, ou remonte la derniere erreur.

    timeout peut etre un entier ou (connexion, lecture). La pause augmente
    legerement entre chaque essai, sans boucle infinie dans une requete.
    """
    for attempt in range(1, attempts + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            if attempt == attempts:
                raise
            seconds = min(delay * attempt, 30)
            if log is not None:
                log(f"[reseau] Echec HTTP ({type(exc).__name__}) ; "
                    f"nouvel essai {attempt + 1}/{attempts} dans {seconds} s")
            time.sleep(seconds)
