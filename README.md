# Snowball Server
Flask server to serve [Semantic Scholar Open Corpus](http://s2-public-api-prod.us-west-2.elasticbeanstalk.com/corpus/) to [snowball-vis](https://github.com/thiagoald/snowball-vis).

## How-to

# Set up

```sh
$ sudo apt install python3 python3-pip
$ pip3 install -r requirements
```

Download corpus (updated instructions [here](http://s2-public-api-prod.us-west-2.elasticbeanstalk.com/corpus/download/)):

```sh
$ wget https://s3-us-west-2.amazonaws.com/ai2-s2-research-public/open-corpus/2021-04-01/manifest.txt
$ wget -B https://s3-us-west-2.amazonaws.com/ai2-s2-research-public/open-corpus/2021-04-01/ -i manifest.txt
```

Decompress:

```sh
$ gunzip s2-corpus-*.gz
```

Create an index per file:
```sh
$ python3 make_index.py vars index 4 /path/to/corpus/jsons/*
```

Sort indexes:
```sh
$ find . -maxdepth 1 | egrep _.index$ | xargs -n 1 -P 4 -I % sort % -o %
```

Merge sorted:

```sh
$ sort -m *_.index -o index
```

# Run
```sh
$ python3 app.py index vars
```

The server should be running on http://localhost:5001.
