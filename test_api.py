from dotenv import load_dotenv
import os, requests

load_dotenv()
key = os.getenv('ALLSPORTS_API_KEY')

print(f"Clé trouvée : {key[:15] if key else 'AUCUNE'}...")

r = requests.get(
    'https://apiv2.allsportsapi.com/tennis/',
    params={
        'met'    : 'Fixtures',
        'APIkey' : key,
        'from'   : '2026-03-18',
        'to'     : '2026-03-18'
    }
)

data = r.json()
print(f"Succès     : {data.get('success')}")
print(f"Matchs     : {len(data.get('result', []))}")

if data.get('result'):
    print(f"\nExemple match :")
    m = data['result'][0]
    print(f"  {m.get('event_first_player')} vs {m.get('event_second_player')}")
    print(f"  {m.get('league_name')} — {m.get('event_date')}")
else:
    print(f"\nRéponse complète : {data}")