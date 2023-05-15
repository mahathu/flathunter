refactoring:
    - TODO: various places use the absolute path "/data/config-prod.yml", this should be changed
    - better config management
    - remove magic variables
        - config für adler, ...-Bewerbungen auslagern (-> Datei?)
        - control applications through Celery o.ä.
            - Funktion, um bewerbungen über zeitraum zu verteilen (numpy? lol)
    - better readme to match standards
    - data-Ordner umbenennen
    - bessere Command-Line-Argumente statt magic values (click?)
        - Auswahl der config
    - investigate bugs in nohup.out

features:
    - eine Funktion, die sich auf eine Anzeige n mal in einem Zeitraum von m Stunden bewirbt (change batch-apply)
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

DONE:
- moved to standard library logging instead of using a custom log function.