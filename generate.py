import re
from bs4 import BeautifulSoup

var_pattern = re.compile(r'([^_]*)_{?([^}]*)}?')
tex_pattern = re.compile(r'\$([^$]*)\$')
word_pattern = re.compile(r'{([^}]*)}')


def make_entry(out, valsi):
    entry = out.new_tag('d:entry', **{
        'id': valsi.definitionid.text,  # valsi_id(valsi),
        'd:title': valsi['word'],
    })

    rafsi = [r.text for r in valsi.find_all('rafsi')]

    entry.append(out.new_tag('d:index', **{'d:value': valsi['word']}))
    for gloss in valsi.find_all('glossword'):
        entry.append(out.new_tag('d:index', **{'d:value': gloss['word']}))
    for r in rafsi:
        entry.append(out.new_tag('d:index', **{'d:value': r}))
    # NOTE: If you want to index by selmaho, uncomment this
    # if valsi.selmaho:
    #     tag = out.new_tag('d:index', **{'d:value': valsi.selmaho.text})
    #     entry.append(tag)

    heading = out.new_tag('h1')
    heading.append(valsi['word'])
    entry.append(heading)

    kind = out.new_tag('h2')
    kind.append(valsi['type'])
    if valsi.selmaho:
        selmaho = out.new_tag('span', **{'class': 'selmaho'})
        selmaho.append(valsi.selmaho.text)
        kind.append(selmaho)
    entry.append(kind)

    defn = out.new_tag('div', **{'class': 'definition'})
    defn.append(format_text(valsi.definition.text))
    entry.append(defn)

    if valsi.notes:
        notes = out.new_tag('div', **{'class': 'notes'})
        notes.append(format_text(valsi.notes.text))
        entry.append(notes)

    if rafsi:
        rafsi_list = out.new_tag('ul', **{'class': 'rafsi'})
        for r in rafsi:
            item = out.new_tag('li')
            item.append(r)
            rafsi_list.append(item)
        entry.append(rafsi_list)

    return entry


def format_latex(match):
    latex = match.group(1)
    parts = []
    for part in latex.split('='):
        parts.append(var_pattern.sub(r'<i>\1<sub>\2</sub></i>', part))
    return '='.join(parts)


def format_text(text):
    text = tex_pattern.sub(format_latex, text)
    text = word_pattern.sub(r'<i>\1</i>', text)
    return BeautifulSoup(text, 'html.parser')


if __name__ == '__main__':
    out = BeautifulSoup(features='xml')

    with open('jbovlaste.xml', 'r') as f:
        doc = BeautifulSoup(f, 'lxml', from_encoding='utf8')

    dictionary = out.new_tag('d:dictionary', **{
        'xmlns': "http://www.w3.org/1999/xhtml",
        'xmlns:d': "http://www.apple.com/DTDs/DictionaryService-1.0.rng",
    })
    out.append(dictionary)

    for valsi in doc.find_all('valsi'):
        entry = make_entry(out, valsi)
        dictionary.append(entry)

    print(str(out).replace('</d:entry>', '</d:entry>\n'))
