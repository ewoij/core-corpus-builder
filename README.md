# CORE corpus builder

Python script building a corpus of scientific articles from the [CORE](https://core.ac.uk/) repository. The articles are retrieved and stored as text, it is therefore very convenient to perform text-mining operations.

## Requirements
 - python > 3
    - tqdm>=4.0.0
    - requests>=2.0.0

 - CORE:
    - api_key: https://core.ac.uk/api-keys/register

## Usage

```python
import core_download as cd

query = 'fullText:((petroglyph "parietal art" "rock art") AND ("radiocarbon" OR "accelerator mass spectrometry" OR "AMS" OR "uranium" OR "thorax" OR "UT/H" OR "uranium/thorax" OR "luminescence"))'
api_key = '<your-api-key>'
output_dir = 'output'

cd.download_corpus(query, api_key, output_dir, max_articles=500, page_size=10)
```

## Output

Each article is saved as 2 files:
 - A plain text file containing the content of the article.
 - A json file containing the CORE metadatas.

An incremental id for each article is created to preserve the relevance order.

'_corpus_info.json' contains the query used to build the corpus and the number of hits returned.

```
├───output_dir
│       000000.fulltext.txt
│       000000.metadatas.json
│       000001.fulltext.txt
│       000001.metadatas.json
│       <...>.fulltext.txt
│       <...>.metadatas.json
│       _corpus_info.json
```
