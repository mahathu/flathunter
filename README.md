# Setup instructions

1) Create a virtual environment, activate it and install prerequisites from `requirements.txt`:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) **TODO** set up a brightdata account and proxy

3) Create a file called `data/secrets.yml` and enter the brightdata proxy url:
```
---
proxy-url: '<PROXY_URL>'
...
```

Make sure that the IP of the server/VM the script is running on is whitelisted in the brightdata web console.

4) (optional) Customize the configuration in `data/config.yml`:
- For gewobag, simply copy the URL from the search results page.
- For degewo, open the network tools and copy the link to the `/search.json` request that is sent when running a search.
- For adler, open the network tools and copy the second `immoscoutgrabber` link, the one that returns a `geodata` json object.
- for covivio, get the json link but remove `&page=1` at the end.

5) Run the script and detach so it will continue running in the background: `nohup python3 ./run.py -c config.yml &`
6) To run the web server: `cd server && gunicorn -b 0.0.0.0:63333 app:app`
(optional) Kill the script by finding out the process ID via `ps` and killing it through `kill -9 <pid>`
