This is the field database for the [Lagash Archaeological Project (LAP)](https://web.sas.upenn.edu/lagash/). It is written in django, and is unlikely to be of use to anyone who isn’t on the project, but is saved on GitHub as a public repository in order to facilitate cloning.

Note that as of now (2026-09-14) running `manage.py migrate` on a newly-cloned repo will throw a “no such table: lap_seasons” error. The easiest way to avoid this is to copy db.sqlite3 from an existing installation (or get the pre-populated blank db-MASTER.sqlite3 file from Paul).
