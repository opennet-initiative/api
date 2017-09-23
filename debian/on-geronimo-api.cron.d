# Die untenstehenden Imports benoetigen jeweils einen Datenbank-Lock - also nie parallel ausfuehren
# Wiki: stuendlich
13 * * * *      su -c "on-geronimo-manage import_wiki" on-geronimo >/dev/null
# ondata: die Verfallsdauer der Informationen ist aufgrund eines olsr-ondataservice-Bugs wohl recht kurz (Minuten)
*/15 * * * *    su -c "on-geronimo-manage import_olsr http://localhost:2006/" on-geronimo >/dev/null; su -c "on-geronimo-manage import_ondataservice" on-geronimo >/dev/null
