from argparse import ArgumentParser, ArgumentTypeError
from typing import Callable


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '--model',
        type=str,
        default='distilgpt2',
        help='Name of model to load, or path to model folder. '
             'See https://huggingface.co/models for a list of available models.'
    )
    parser.add_argument(
        '--model_path',
        type=str,
        default='trained',
        help='Path to folder where final model was saved.',
    )

    args = parser.parse_args()

    # lazy load these down here instead of at the start of the file
    # this has the advantage of not having to load CUDA to parse arguments,
    #  which has benefit if invalid arguments are entered
    from transformers import AutoTokenizer, AutoModelWithLMHead

    model = AutoModelWithLMHead.from_pretrained(args.model_path, return_dict=True)
    tokenizer = AutoTokenizer.from_pretrained('distilgpt2')

    model.eval()

    print('Enter a prompt to generate a creature description, press Control+C to terminate.')
    print('Works best if you add a sentence of padding text to start the output.')
    while True:
        prompt = input('Enter a prompt > ')
        inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
        outputs = model.generate(inputs, max_length=250, do_sample=True, top_p=0.95, top_k=60)
        generated = tokenizer.decode(outputs[0])
        print(generated)


if __name__ == '__main__':
    main()
