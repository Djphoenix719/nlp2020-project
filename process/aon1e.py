import os

from bs4 import BeautifulSoup
from tqdm import tqdm

from process.util import ladle, collect_until_end, full_clean, write_output


def process_aon1e():
    system = 'pf1e'
    input_dir = f"data/raw/{system}"
    os.makedirs(f'data/processed/{system}', exist_ok=True)
    for file_name in tqdm(os.listdir(input_dir), desc=f'Processing {system}', unit='file', position=0, leave=True):
        file_path = os.path.join(input_dir, file_name)

        soup, raw_text = ladle(file_path)
        soup = BeautifulSoup(str(soup.find('div', {'class': 'main'})), features='html.parser')

        title = soup.find('h1', {'class': 'title'})
        monster_name = title.text

        lore_start = title.find_next('h3', {'class': 'framing'}, text='Description')

        if lore_start is None:
            continue

        lines = collect_until_end(lore_start.next_sibling, end_on_tags=['h1'], skip_collection=['b'])

        short_desc = title.find_next('i').text
        if "pg." not in short_desc.lower():
            lines = [short_desc, *lines]

        lines = full_clean(lines)
        # lines = "".join(lines)
        # lines = lines.replace('\n', ' ')
        # lines = lines.split('.')
        # lines = [f"{line}.".strip() for line in lines if line.strip() != ""]
        # lines = "\n".join(lines)

        write_output(monster_name, system, lines)
