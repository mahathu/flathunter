# Setup instructions

1) Create a virtualenv, activate it and install prerequisites from `requirements.txt`:
```
python3.9 -m venv <environment_name>
source <environment_name>/bin/activate
pip install -r requirements.txt
```

2) Create a file called `data/secrets.yml` and enter the brightdata proxy url:
```
---
proxy-url: '<PROXY_URL>'
...
```
Make sure that the IP of the VPS that the script is running on is whitelisted in the brightdata console.

3) (optional) Customize the configuration in `data/config.yml`:
- For gewobag, simply copy the URL from the search results page.
- For degewo, open the network tools and copy the link to the `/search.json` request that is sent when running a search.
- For adler, open the network tools and copy the second `immoscoutgrabber` link, the one that returns a `geodata` json object.
- for covivio, get the json link but remove `&page=1` at the end.

4) Run the script and detach so it will continue running in the background: `nohup python3.9 run.py &`
5) To run the web server: `cd server && gunicorn -b 0.0.0.0:63333 app:app`
(optional) Kill the script by finding out the process ID via `ps` and killing it through `kill -9 <pid>`
