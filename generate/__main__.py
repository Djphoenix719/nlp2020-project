from transformers import AutoTokenizer, GPT2LMHeadModel


def main():
    model = GPT2LMHeadModel.from_pretrained('trained/distilgpt2', return_dict=True)
    tokenizer = AutoTokenizer.from_pretrained('distilgpt2')

    while True:
        print('-'*50)
        print('Enter a prompt to generate a creature description, type "exit" to stop.')

        prompt = input('Enter the creature name > ')
        prompt = prompt.strip()
        if prompt == "exit":
            exit(1)

        prompt = f"Describe a {prompt}."

        padding = input('Enter the first sentence of the description > ')
        padding = padding.strip()
        if padding == "exit":
            exit(1)

        count = input('How many completions should be generated > ')
        count = int(count)

        for i in range(count):
            print(f"({i}) {prompt}".center(50, '='))
            inputs = tokenizer.encode(prompt + padding, add_special_tokens=False, return_tensors="pt")
            outputs = model.generate(
                inputs, max_length=250, min_length=80, do_sample=True, top_p=0.95, top_k=60, pad_token_id=50256
            )

            length = len(tokenizer.decode(inputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True))
            generated = tokenizer.decode(outputs[0])[length:]
            generated = generated.replace('<|endoftext|>', '')

            print(f"{prompt}\n{padding}{generated}")
        print('-'*50)


if __name__ == '__main__':
    main()
