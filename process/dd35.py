import os

from bs4 import BeautifulSoup
from tqdm import tqdm

from process.util import full_clean, write_output, ladle


def process_dd35():
    system = 'dd35'
    input_dir = f"data/raw/{system}"
    os.makedirs(f'data/processed/{system}', exist_ok=True)
    for file_name in tqdm(os.listdir(input_dir), desc=f'Processing {system}', unit='file', position=0, leave=True):
        file_path = os.path.join(input_dir, file_name)
        soup, raw_text = ladle(file_path)

        soup = BeautifulSoup(raw_text, features='html.parser')
        soup = soup.find('div', {'id': 'main'}).find('nav').find_next_sibling('div')
        soup = BeautifulSoup(str(soup.contents), features='html.parser')

        title = soup.find('h1')
        monster_name = title.text.split('(')[0].strip()

        divider = title.find_all_next('hr')[-1]
        paragraphs = divider.find_next('p')
        paragraphs = paragraphs.find_all_next('p')
        lines = [p.text for p in paragraphs if
                 hasattr(p, 'next') and hasattr(p.next, 'name') and p.next.name != 'strong']
        lines = full_clean(lines)

        write_output(monster_name, system, lines)