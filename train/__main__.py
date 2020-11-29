from argparse import ArgumentParser, ArgumentTypeError
from typing import Callable


def main():
    def bounded_int(lower: int, upper: int) -> Callable[[str], int]:
        """
        Construct a bounded integer argument type checker.
        :param lower: The lower bound.
        :param upper: The upper bound.
        :return: A function to be used as an argparser argument type.
        """
        def _inner(x: str) -> int:
            x = int(x)
            if x < lower:
                raise ArgumentTypeError(f"must be >= to {lower}.")
            if x > upper:
                raise ArgumentTypeError(f"must be <= to {upper}.")
            return x
        return _inner

    parser = ArgumentParser()
    parser.add_argument(
        '--model',
        type=str,
        default='distilgpt2',
        help='Name of model to load, or path to model folder. '
             'See https://huggingface.co/models for a list of available models.'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='trained',
        help='Path to folder where checkpoints and final model will be saved.',
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/train.txt',
        help='Path to input fully parsed text file.',
    )
    parser.add_argument(
        '--checkpoint-steps',
        type=bounded_int(1, 2**64),
        default=25,
        help='Number of steps between checkpoints.'
    )
    parser.add_argument(
        '--max_checkpoints',
        type=bounded_int(1, 2**64),
        default=3,
        help='Maximum number of checkpoints to keep.',
    )
    parser.add_argument(
        '--epochs',
        type=bounded_int(1, 2**64),
        default=2,
        help='Number of epochs through the data to perform.',
    )

    args = parser.parse_args()

    # lazy load these down here instead of at the start of the file
    # this has the advantage of not having to load CUDA to parse arguments,
    #  which has benefit if invalid arguments are entered
    from transformers import AutoTokenizer
    from transformers import TextDataset, DataCollatorForLanguageModeling
    from transformers import Trainer, TrainingArguments, AutoModelForCausalLM

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model)

    train_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=args.input,
        block_size=128
    )
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    training_args = TrainingArguments(
        output_dir=args.output,
        overwrite_output_dir=True,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=32,
        save_steps=args.checkpoint_steps,
        save_total_limit=args.max_checkpoints,
        prediction_loss_only=True,
        warmup_steps=50,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )

    trainer.train()
    trainer.save_model(args.output_path)


if __name__ == '__main__':
    main()
