import requests
import os
from urllib.parse import urlparse

# Dados completos com os 4 times para o download
TEAMS_DATA = {
    '1': {
        'id': 'acend2021', 'name': 'Acend 2021',
        'players': [
            {'name': 'cNed', 'img_url': 'https://owcdn.net/img/65dbc5cfc3b28.png'},
            {'name': 'Starxo', 'img_url': 'https://www.prosettings.gg/wp-content/uploads/2021/09/starxo-valorant-player-profile-picture-new.webp'},
            {'name': 'zeek', 'img_url': 'https://owcdn.net/img/68644db3bfd7d.png'},
           {'name': 'Kiles', 'img_url': 'https://i.imgur.com/u15B4Xm.png'},
            {'name': 'BONECOLD', 'img_url': 'https://liquipedia.net/commons/images/thumb/c/c6/Acend_BONECOLD.png/237px-Acend_BONECOLD.png'},
        ]
    },
    '2': {
        'id': 'loud2022', 'name': 'LOUD 2022',
        'players': [
            {'name': 'Less', 'img_url': 'https://owcdn.net/img/677d651a8a520.png'},
            {'name': 'Aspas', 'img_url': 'https://i.imgur.com/CvT4ISK.webp'},
            {'name': 'Sadhak', 'img_url': 'https://owcdn.net/img/66306e037e53b.png'},
            {'name': 'Sacy', 'img_url': 'https://static.valorantzone.gg/news/2022/09/18195828/52367462016_f823cda6d8_k.jpg'},
            {'name': 'Pancada', 'img_url': 'https://i.imgur.com/kY3yAGy.png'},
        ]
    },
    '3': {
        'id': 'eg2023', 'name': 'Evil Geniuses 2023',
        'players': [
            {'name': 'Demon1', 'img_url': 'https://i.imgur.com/tH2sT1z.png'},
            {'name': 'Ethan', 'img_url': 'https://owcdn.net/img/6416939a5a1c2.png'},
            {'name': 'jawgemo', 'img_url': 'https://owcdn.net/img/64169400bfed7.png'},
            {'name': 'Boostio', 'img_url': 'https://owcdn.net/img/641693760f427.png'},
            {'name': 'C0M', 'img_url': 'https://owcdn.net/img/641693c3a0312.png'},
        ]
    },
    '4': {
        'id': 'edg2024', 'name': 'EDward Gaming 2024',
        'players': [
            {'name': 'ZmjjKK', 'img_url': 'https://owcdn.net/img/677fe40edf9da.png'},
            {'name': 'nobody', 'img_url': 'https://owcdn.net/img/677fe4210de6e.png'},
            {'name': 'CHICHOO', 'img_url': 'https://owcdn.net/img/677fe4289bb34.png'},
            {'name': 'Smoggy', 'img_url': 'https://owcdn.net/img/677fe435edc57.png'},
            # A imagem de 'S1Mon' não foi fornecida, usando uma padrão
            {'name': 'S1Mon', 'img_url': 'https://i.imgur.com/0DcnW25.png'}, 
        ]
    }
}

IMAGE_DIR = os.path.join('static', 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)

print("Iniciando download das imagens para TODOS os 4 times...")

for team_key, team_data in TEAMS_DATA.items():
    for player in team_data['players']:
        url = player['img_url']
        try:
            parsed_url = urlparse(url)
            referer = f"{parsed_url.scheme}://{parsed_url.netloc}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': referer
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()

            file_extension = os.path.splitext(parsed_url.path)[1]
            if not file_extension or len(file_extension) > 5:
                 file_extension = '.png'
            
            filename = f"{team_data['id']}_{player['name'].lower()}{file_extension}"
            filepath = os.path.join(IMAGE_DIR, filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Sucesso: {filename}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Falha ao baixar {player['name']}: {url} | Erro: {e}")

print("\nDownload concluído!")