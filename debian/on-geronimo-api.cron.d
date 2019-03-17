# Die untenstehenden Imports benoetigen jeweils einen Datenbank-Lock - also nie parallel ausfuehren
# Wiki: stuendlich
13 *	* * *	on-geronimo-api	/usr/bin/chronic /usr/bin/on-geronimo-manage import_wiki
*/6 *	* * *	on-geronimo-api	/usr/bin/chronic /usr/bin/on-geronimo-manage import_olsr
# ondata: die Verfallsdauer der Informationen ist aufgrund eines olsr-ondataservice-Bugs wohl recht kurz (Minuten)
*/15 *	* * *	on-geronimo-api	/usr/bin/chronic /usr/bin/on-geronimo-manage import_ondataservice
9 *	* * *	on-geronimo-api	/usr/bin/chronic /usr/bin/on-geronimo-manage regenerate_accesspoint_sites
