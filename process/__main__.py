from pathlib import Path, PurePath

from tqdm import tqdm

from process.aon1e import process_aon1e
from process.aon2e import process_aon2e
from process.dd35 import process_dd35


def main():
    process_aon1e()
    process_aon2e()
    process_dd35()

    # merge all files into the final training text file
    paths: [PurePath] = list(Path('data/processed').glob('**/*.txt'))
    with open('data/train/all.txt', 'w', encoding='utf-8') as out_file:
        for in_file in tqdm(paths, total=len(paths), unit='file', desc='Merging processed files'):
            out_file.writelines(in_file.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
