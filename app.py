import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("Advertencia: Faltan credenciales de Supabase en el archivo .env")

@app.route('/')
def inicio():
    return jsonify({"mensaje": "Bienvenido al API de Tralaladopt"})

if __name__ == '__main__':
    app.run(debug=True)