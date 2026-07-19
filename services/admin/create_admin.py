"""
Crée un compte administrateur avec un mot de passe hashé.

Lance :  python -m services.admin.create_admin
"""
import getpass
import sys

from services.admin.auth import hash_password
from services.admin.db import moonpilot_cursor


def main():
    print("=" * 45)
    print("  CRÉATION D'UN COMPTE ADMIN")
    print("=" * 45)

    username = input("Username : ").strip()
    email = input("Email    : ").strip()

    if not username or not email:
        print("Username et email sont obligatoires.")
        sys.exit(1)

    password = getpass.getpass("Mot de passe        : ")
    confirm = getpass.getpass("Confirmer le mot de passe : ")

    if password != confirm:
        print("Les mots de passe ne correspondent pas.")
        sys.exit(1)

    if len(password) < 8:
        print("Le mot de passe doit faire au moins 8 caractères.")
        sys.exit(1)

    try:
        with moonpilot_cursor() as cur:
            cur.execute(
                "INSERT INTO admins (username, email, password_hash) "
                "VALUES (%s, %s, %s)",
                (username, email, hash_password(password)),
            )
        print(f"\n✅ Admin '{username}' créé avec succès.")
    except Exception as e:
        print(f"\n❌ Échec : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()