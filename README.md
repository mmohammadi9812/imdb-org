# IMDB Lists to org-mode check lists

This is a python script which reads imdb lists in `lists.yaml` and

generates `list.org` for each list.

## Installation

clone this repo, edit `lists.yaml` file, then:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

```bash
python3 imdb-list-to-org-mode.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.en.html)