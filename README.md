# Setup instructions

- Create a virtualenv, activate it and install prerequisites from `requirements.txt`:
```
python3.9 -m venv <environment_name>
source <environment_name>/bin/activate
pip install -r requirements.txt
```
- Create a file called `secrets.yml` and enter the API key: (TODO: rewrite README, instead add proxy urls)
```
---
scraper-api-key: '<API_KEY>'
...
```
- (optional) Customize the configuration in `config.yml` (TODO: how to get the proper search URLs)
- Run the script and detach so it will continue running in the background: `nohup python3.9 run.py &`
- (optional) Kill the script by finding out the process ID via `ps` and killing it through `kill -9 <pid>`