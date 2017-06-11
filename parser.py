import re

var_pattern = re.compile('x([0-9])')

GISMU_FILES = ['gismu.txt', 'gismu-extra.txt']
CMAVO_FILES = ['cmavo.txt']

CMAVO_WIDTHS = [11, 9, 42, 106, None]
GISMU_WIDTHS = [6, 4, 4, 4, 21, 21, 97, 2, 8, None]


def parse_widths(entries, field_widths, skip=0):
    slices = []
    offset = 0
    for width in field_widths:
        if width is None:
            # Max field width is 1 million
            width = 1_000_000
        slices.append((offset, offset + width))
        offset += width

    for entry in entries:
        if skip > 0:
            skip -= 1
            continue
        yield tuple(entry[begin:end].strip() for begin, end in slices)


def make_id(name):
    name = name.replace("'", '_')
    # An XML id is not allowed to start with a .
    if name[0] == '.':
        name = name.replace('.', '_.')
    return name


def process_entry(word, cmavo, gismu):
    template = '''
<d:entry id="{word_id}" d:title="{word}">
  {index}
  <h1>{word}</h1>
  {body}
</d:entry>
    '''
    index = [word]
    body = ''
    if cmavo:
        index.extend(cmavo_index(*cmavo))
        body += process_cmavo(*cmavo)
    if gismu:
        index.extend(gismu_index(*gismu))
        body += process_gismu(*gismu)
    return template.format(
        word=word,
        word_id=make_id(word),
        index='\n'.join('<d:index d:value="{}"/>'.format(w) for w in index),
        body=body,
    ).strip()


# @Todo: Learn what the parts I don't understand are
def process_cmavo(cmavo, a, short_def, long_def, cf):
    template = '''
  <h2>cmavo <span class="form">({form})</span></h2>
  <div class="cmavo">
  <div>
    {short_def}
  </div>
  <div>
    {long_def}
  </div>
  {cf}
  </div>
    '''
    return template.format(
        cmavo=cmavo,
        cmavo_id=make_id(cmavo),
        form=a,
        short_def=short_def,
        long_def=long_def,
        cf=cf,
    ).strip()


def cmavo_index(cmavo, a, short_def, long_def, cf):
    return []


def process_gismu(gismu, r1, r2, r3, short_def, alt, long_def, n, m, rest):
    template = '''
  <h2>gismu</h2>
  <div class="gismu">
  <h3>{gismu}</h3>
  {rafsi}
  <div>
    {short_def}
  </div>
  <div>
    {long_def}
  </div>
  <div>
    {rest}
  </div>
  {cf}
  </div>
    '''
    # @Todo: Extract cf.
    cf = '<!-- see also... -->'
    rafsi_list = list(filter(bool, (r1, r2, r3)))
    if rafsi_list:
        rafsi = '<ul class="rafsi">\n{}\n</ul>'.format(
            '\n'.join('<li>{}</li>'.format(r) for r in rafsi_list)
        )
    else:
        rafsi = ''
    # @Todo: Other note parsing
    return template.format(
        gismu=gismu,
        rafsi=rafsi,
        short_def=short_def,
        long_def=var_pattern.sub(r'<i>x<sub>\1</sub></i>', long_def),
        cf=cf,
        rest=rest,
    ).strip()


def gismu_index(gismu, r1, r2, r3, short_def, alt, long_def, n, m, rest):
    result = [r for r in (r1, r2, r3) if r]
    result += [short_def]
    if alt:
        result += [alt.strip("'")]
    return result


print('''\
<?xml version="1.0" encoding="UTF-8"?>
<d:dictionary xmlns="http://www.w3.org/1999/xhtml" \
xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">\
''')

entries = {}

for fname in CMAVO_FILES:
    with open(fname) as f:
        for entry in parse_widths(f, CMAVO_WIDTHS, skip=1):
            word = entry[0]
            if word not in entries:
                entries[word] = [None, None]
        entries[word][0] = entry

for fname in GISMU_FILES:
    with open(fname) as f:
        for entry in parse_widths(f, GISMU_WIDTHS, skip=1):
            word = entry[0]
            if word not in entries:
                entries[word] = [None, None]
            entries[word][1] = entry

for word, (cmavo, gismu) in entries.items():
    print(process_entry(word, cmavo, gismu))


print('''\
<d:entry id="front_back_matter" d:title="Front/Back Matter">
  <h1><b>Lojban</b></h1>
  <div>
    Based on the Lojban word lists.
  </div>
</d:entry>
</d:dictionary>''')
