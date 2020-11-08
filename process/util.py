import re
import bs4
from typing import Union, List
from Levenshtein import distance


def ladle(file_path: str) -> (bs4.BeautifulSoup, str):
    """
    Open an HTML file and soupify it.
    :param file_path:
    :return:
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_text = file.readlines()
        raw_text = ''.join(raw_text)
        raw_text = clean_multi_newlines(raw_text)

    soup = bs4.BeautifulSoup(raw_text, features='html.parser')
    return soup, raw_text


def write_output(name: str, system: str, lines: [str]) -> None:
    clean_name = "".join([c for c in name if c.isalnum()]).strip()
    with open(f'data/processed/{system}/{clean_name}.txt', 'w', encoding='utf-8') as file:
        file.write(f'<|startoftext|>Describe a {name}.\n')
        file.writelines(lines)
        file.write('<|endoftext|>\n')


def clean_multi_newlines(text: str) -> str:
    """
    Clean spacing of text to make it easier to work with.
    """
    text = re.sub(r"(\n)+", '\n', text)
    return text


def strip_extra_spacing(text: [str]) -> [str]:
    text = [re.sub(r"\s+", " ", line) for line in text]
    text = [line.strip() for line in text]
    return text


def strip_undesirable_lines(text: [str]) -> [str]:
    text = [line for line in text if "Spells DC" not in line]
    text = [line for line in text if "Recall Knowledge -" not in line]
    text = [line for line in text if not line.startswith("Related Groups")]
    return text


def skip_until(tag: bs4.Tag, cls, exclude_empty: bool = True):
    next_element: bs4.PageElement = tag.next_sibling
    while not isinstance(next_element, cls) or (exclude_empty and str(next_element).strip() == ""):
        next_element = next_element.next_sibling

    return next_element


def collect_until_end(
        first_element: bs4.PageElement,
        skip_collection: Union[None, List[str]] = None,
        end_on_tags: Union[None, List[str]] = None) -> [str]:
    """
    Collect text until one of a number of specified tags is encountered,
    optionally skipping the collection of certain tags.
    :param first_element: The element to start collection after
    :param skip_collection: Do not collect contents of these tags
    :param end_on_tags: Collection will end when any of these tags are encountered
    :return:
    """

    if end_on_tags is None:
        end_on_tags = []
    if skip_collection is None:
        skip_collection = []

    contents: [str] = [str(first_element)]
    next_element: bs4.PageElement = first_element.next_sibling

    def should_end(element: bs4.PageElement):
        if hasattr(element, 'name') and any([tag == element.name for tag in end_on_tags]):
            return True
        return element is None

    def should_collect(element: bs4.PageElement):
        if hasattr(element, 'name') and any([tag == element.name for tag in skip_collection]):
            return False
        if hasattr(element, 'next') and any([tag == element.next.name for tag in skip_collection]):
            return False
        return True

    while not should_end(next_element):
        if should_collect(next_element):
            if hasattr(next_element, 'text'):
                if hasattr(next_element, 'name') and next_element.name == 'br':
                    contents.append('\n')
                else:
                    contents.append(next_element.text)
            else:
                contents.append(str(next_element))
        else:
            contents.append('\n\n')

        next_element = next_element.next_sibling

    return contents


def strip_similar_lines(text: [str], lev_dist_thresh: int = 3) -> [str]:
    """
    Strip similar lines in the list according to an edit distance threshold.
    """
    idx1, idx2 = 0, len(text) - 1
    while idx1 < len(text):
        a = text[idx1]

        while idx2 >= 0:
            if idx1 == idx2:
                idx2 -= 1
                continue

            b = text[idx2]

            d = distance(a, b)
            if d <= lev_dist_thresh:
                text.pop(idx2)

            idx2 -= 1

        idx2 = len(text) - 1
        idx1 += 1
    return text


def full_clean(text: [str]) -> str:
    text = "".join(text)
    text = clean_multi_newlines(text)
    text = text.split("\n")
    text = strip_extra_spacing(text)
    text = strip_undesirable_lines(text)
    text = strip_similar_lines(text)
    text = strip_extra_spacing(text)
    # text = "".join(text).split('.')
    # text = [line + '.' for line in text]
    text = "\n".join(text)
    return text
