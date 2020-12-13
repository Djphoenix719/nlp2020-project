from pathlib import Path, PurePath
from transformers import AutoTokenizer, GPT2LMHeadModel
from tqdm import tqdm, trange

from nltk.translate.nist_score import sentence_nist as nist


def main():
    print('Loading model...')
    model = GPT2LMHeadModel.from_pretrained('trained/gpt2-medium', return_dict=True)
    model.eval()
    print('Loading tokenizer...')
    tokenizer = AutoTokenizer.from_pretrained('gpt2-medium')

    paths: [PurePath] = list(Path('data/test').glob('*.txt'))
    for path in tqdm(paths, total=len(paths), unit='file', desc='Testing against references'):
        text = path.read_text(encoding='utf-8')
        text = text.split('.')

        describe: str = text[0] + '.'
        describe = describe.replace('<|startoftext|>', '')
        context: str = text[1] + '.'

        reference = '.'.join(text[2:])
        hypotheses: [str] = []

        print()
        print()
        print('Prompt')
        print(describe + context)

        for i in tqdm(range(10), leave=False, desc='Generating candidates'):
            inputs = tokenizer.encode(describe + context, add_special_tokens=False, return_tensors="pt")
            outputs = model.generate(
                inputs, max_length=250, min_length=80, do_sample=True, top_p=0.95, top_k=60, pad_token_id=50256
            )

            length = len(tokenizer.decode(inputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True))
            generated = tokenizer.decode(outputs[0])[length:]
            generated = generated.replace('<|endoftext|>', '')

            hypotheses.append(generated)

        print('Reference')
        print(reference)
        print()
        print('Hypotheses')
        print(hypotheses)
        print()

        for n in range(2, 8):
            scores = [nist(reference, hypothesis, n=n) for hypothesis in hypotheses]
            print(f'n={n}')
            print(scores)


if __name__ == '__main__':
    main()
