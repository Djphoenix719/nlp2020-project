from pathlib import Path, PurePath

import os
from tqdm import tqdm
from random import shuffle

from process.aon1e import process_aon1e
from process.aon2e import process_aon2e
from process.dd35 import process_dd35


def main():
    process_aon1e()
    process_aon2e()
    process_dd35()

    # merge all files into the final training text file
    paths: [PurePath] = list(Path('data/processed').glob('**/*.txt'))
    shuffle(paths)

    train_paths = paths[:-50]
    test_paths = paths[-50:]

    with open('data/train.txt', 'w', encoding='utf-8') as out_file:
        for in_file in tqdm(train_paths, total=len(train_paths), unit='file', desc='Merging processed files'):
            out_file.writelines(in_file.read_text(encoding='utf-8'))

    os.makedirs('data/test', exist_ok=True)
    for delete_file in tqdm(list(Path('data/test').glob('*.txt')), unit='file', desc='Cleaning old test data'):
        os.unlink(delete_file)

    for in_file in tqdm(test_paths, total=len(test_paths), unit='file', desc='Copying test files'):
        name = str(in_file).split('\\')[-1]
        with open(f'data/test/{name}', 'w', encoding='utf-8') as out_file:
            out_file.writelines(in_file.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
