Mittach!
========

Installation
------------

### Mac-User

    brew install md5sha1sum

### Anforderungen

* Python >= 2.5
* [pip](http://www.pip-installer.org/en/latest/installing.html)
* virtualenv `sudo pip install virtualenv`

### Entwicker-Setup

Umgebung anlegen:

    make init

Server starten:

    source activate
    make server

[http://localhost:5000/](http://localhost:5000)

### Produktions-Setup

* Installation (oder Upgrade) mittels `deploy`-Skript
* Instanzordner anlegen mittels `python -m mittach.instancer <Instanzpfad> [Modus]`
* `app.wsgi` in den Instanzordner kopieren
* Apache so konfigurieren, dass mod_wsgi `app.wsgi` aufruft
