# Die untenstehenden Imports benoetigen jeweils einen Datenbank-Lock - also nie parallel ausfuehren
# Wiki: stuendlich
13 *	* * *	on-geronimo-api	/usr/bin/on-geronimo-manage import_wiki >/dev/null
*/6 *	* * *	on-geronimo-api	/usr/bin/on-geronimo-manage import_olsr >/dev/null
# ondata: die Verfallsdauer der Informationen ist aufgrund eines olsr-ondataservice-Bugs wohl recht kurz (Minuten)
*/15 *	* * *	on-geronimo-api	/usr/bin/on-geronimo-manage import_ondataservice >/dev/null
