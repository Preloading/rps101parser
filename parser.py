import json
import os.path
import urllib.request
from pathlib import Path

from progressbar import progressbar
from bs4 import BeautifulSoup

DEFAULT_URL = 'https://www.umop.com/rps101/{}.htm'
DEFAULT_IMG_URL = 'https://www.umop.com/rps101/{}'
OUT_FOLDER = 'out'


def read_site(gesture_id):
    url = DEFAULT_URL.format(gesture_id)
    return str(urllib.request.urlopen(url).read())


def parse_site(site_content, gesture_id):
    soup = BeautifulSoup(site_content, 'html.parser')

    img = soup.body.img
    img = img['src'] if img else False

    title = soup.body.font.b.contents[0].lower().strip()

    table = soup.body.table.tr
    rows = table.find_all('td')
    compares = []

    for td in rows:
        content = td.font.contents

        current_verb = []
        current_other = ''

        for line in content:
            if str(line) == '<br/>':
                compares.append({
                    'verb': current_verb,
                    'other_gesture_id': current_other,
                })
                current_verb = []
                current_other = ''
            elif hasattr(line, 'name') and line.name == 'a':
                current_other = line['href'].replace('.htm', '')
            else:
                current_verb.append(str(line).strip().replace('\\n', '').lower())

    return {
        'id': gesture_id,
        'title': title,
        'img': img,
        'compares': compares,
    }


def download_image_to_folder(image, folder):
    image_path = os.path.join(folder, image)
    Path(image_path).parent.mkdir(parents=True, exist_ok=True)

    with open(image_path, 'wb') as file:
        file.write(urllib.request.urlopen(DEFAULT_IMG_URL.format(image)).read())


def write_to_file(parsed, folder):
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(folder, '101.json'), 'w') as file:
        json.dump(parsed, file)


def main():
    all_parsed = []
    for i in progressbar(range(1, 102)):
        contents = read_site(i)
        parsed = parse_site(contents, i)
        download_image_to_folder(parsed['img'], OUT_FOLDER)
        all_parsed.append(parsed)

    write_to_file(all_parsed, OUT_FOLDER)


if __name__ == '__main__':
    main()
