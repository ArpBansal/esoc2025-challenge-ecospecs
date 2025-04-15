## Local Set-UP
```
git clone https://github.com/ArpBansal/esoc2025-challenge-ecospecs.git
```

```
cd esoc2025-challenge-ecospecs
```

**For Linux**

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
In case getting ImportError: attempted relative import with no known parent package

export PYTHONPATH=$PYTHONPATH:/home/arpbansal/code/esoc/esoc2025-challenge-ecospecs
replace this with your actual path to folder

## Run tests

```
pytest
```