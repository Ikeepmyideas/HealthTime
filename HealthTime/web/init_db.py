import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")

if not DB_URL:
    print("Erreur : La variable DATABASE_URL n'a pas été trouvée.")
    exit()

try:
    print("Connexion à la base de données...")
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    print("Lecture du fichier schema.sql...")
    with open("../database/schema.sql", "r", encoding="utf-8") as file:
        sql_script = file.read()

    print("Création des tables en cours...")
    cursor.execute(sql_script)
    conn.commit()

    print("Succès ! Toutes les tables ont été créées avec succès !")

except Exception as e:
    print(f"Erreur lors de l'exécution : {e}")

finally:
    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()
