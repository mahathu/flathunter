refactoring:
    - TODO: properties.py, scrapers.py
    - TODO: Currently, two places use absolute path "/data/config-prod.yml", this should be changed
    - remove magic variables
        - config für adler, ...-Bewerbungen auslagern (-> Datei?)
        - control applications through Celery o.ä.
            - Funktion, um bewerbungen über zeitraum zu verteilen (numpy? lol)
    - data-Ordner umbenennen
    - refactor request_data.json, vor allem das weirde "gewobag_formdata" unten
    - investigate bugs in nohup.out

features:
    - eine Funktion, die sich auf eine Anzeige n mal in einem Zeitraum von m Stunden bewirbt (refactor batch_apply)
        - use celery o.ä.
    - telegram bot integration (v1.0.1)
    - zip code visualizer
    - fake-emails, die auch ankommen
    - implement standard-readme: https://github.com/RichardLitt/standard-readme

info (angeblich, laut adler-Mitarbeiterin):
    - Bewerbungen der ersten 1-2 Tage werden berücksichtigt, Schnelligkeit zählt nicht
    - Anzeigen bleiben online, auch nachdem die Einladungen schon verschickt wurden
    - ca 18 (rechtliche) Personen werden eingeladen
    --> poisson-Verteilung?

===========================

Bewerbungen:
adler: lediglich GET-request an Adresse
degewo:
gewobag:
stadt und land:
wbm: