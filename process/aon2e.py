import bs4
import os
from tqdm import tqdm

from process.util import skip_until, collect_until_end, full_clean, ladle, write_output


def process_aon2e():
    system: str = 'pf2e'
    input_dir = f"data/raw/{system}"
    no_description_notes = [
        "This entry did not have a separate description for the family.",
        "Nethys Note: no description has been provided for this family"
    ]
    os.makedirs(f'data/processed/{system}', exist_ok=True)

    for file_name in tqdm(os.listdir(input_dir), desc=f'Processing {system}', unit='file', position=0, leave=True):
        file_path = os.path.join(input_dir, file_name)

        soup, raw_text = ladle(file_path)
        soup = bs4.BeautifulSoup(str(soup.find('div', {'class': 'main'})), features='html.parser')
        title = soup.find('h1', {'class': 'title'})
        monster_name = title.text

        lines = collect_until_end(title.next_sibling, end_on_tags=['h1'])

        stats_start = title.find_next('h1', {'class': 'title'})
        lore_start = stats_start.find_next('h1', {'class': 'title'})
        if lore_start is None:
            lore_start = stats_start.find_next('h3', {'class': 'title'})
        if lore_start is not None and not any([(note in raw_text) for note in no_description_notes]):
            lore_start = skip_until(lore_start, bs4.NavigableString)
            lore_start = collect_until_end(lore_start, skip_collection=['h2', 'h3', 'h4'])
            lines.extend(lore_start)

        lines = full_clean(lines)

        write_output(monster_name, system, lines)
