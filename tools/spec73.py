import json,sys
de_desc = r"""**Custom Item Fix (BETA) v2 by St0ny** *(Nr. {N}, standardmäßig aus, Autor: unbekannt (v1) / St0ny (v2))*
Macht Custom-Items möglich, ohne die `Item.dbc` des Clients anzupassen. Viele
Stellen im Client lesen Display-ID, Inventartyp, Klasse, Unterklasse und Scheide
eines Items nur aus der `Item.dbc`. Items, die nur in der Datenbank des Servers
stehen, fehlen dort – der Client zeigt dann z. B. kein Modell am Charakter und
kein Icon. Die `Wow.exe` hat aber schon Hilfsfunktionen, die diese Werte zuerst
im Item-Cache suchen (also in den Daten, die der Server zu jedem Item schickt)
und erst danach in der `Item.dbc`. Der Patch leitet die reinen DBC-Zugriffe auf
diese Hilfsfunktionen um. Steht ein Item in beiden, gelten damit die Werte des
Servers.

**Empfohlen** zusammen mit „CACHE-Ordner-Erstellung deaktivieren“ (Nr. 2): Dann
speichert WoW den Item-Cache nicht auf der Festplatte und holt geänderte
Custom-Items bei jedem Start frisch vom Server. Fehlt Nr. 2 in der Auswahl,
weist der Patcher darauf hin.

> [!CAUTION]
> **BETA** – im Spiel noch nicht getestet. Die ursprüngliche Fassung v1 hatte
> zwei Fehler, mit denen der Client abgestürzt wäre: In einer Zeile fehlte ein
> Byte (die Funktion für die Item-Klasse wurde dadurch zu Datenmüll), eine
> andere war eine Kopie der Zeile davor (ein Aufruf landete mitten in einer
> fremden Funktion). v2 behebt beides. Alle umgebauten Stellen wurden per
> Emulation mit Test-Items geprüft: nur im Cache, nur in der `Item.dbc`, in
> beiden und in keinem.

Aus v1 nicht übernommen: die PE-Prüfsumme (Windows prüft sie bei Programmen
nicht) und die Änderung `Cache` → `||che` – das ist genau Patch Nr. 2.
"""
en_desc = r"""**Custom Item Fix (BETA) v2 by St0ny** *(No. {N}, off by default, Author: unknown (v1) / St0ny (v2))*
Makes custom items possible without changing the client's `Item.dbc`. Many
places in the client read the display ID, inventory type, class, subclass and
sheath of an item only from `Item.dbc`. Items that only exist in the server's
database are missing there – the client then shows e.g. no model on the
character and no icon. But `Wow.exe` already has helper functions that look
these values up in the item cache first (the data the server sends for every
item) and only then in `Item.dbc`. The patch redirects the plain DBC lookups to
these helper functions. If an item is in both, the server's values apply.

**Recommended** together with "Disable CACHE folder creation" (No. 2): then WoW
does not store the item cache on disk and fetches changed custom items fresh
from the server at every start. If No. 2 is not selected, the patcher points
this out.

> [!CAUTION]
> **BETA** – not tested in game yet. The original version v1 had two errors that
> would have crashed the client: one line was missing a byte (turning the
> function for the item class into garbage), another was a copy of the line
> before it (a call landed in the middle of an unrelated function). v2 fixes
> both. All rebuilt places were checked by emulation with test items: only in
> the cache, only in `Item.dbc`, in both and in neither.

Not taken over from v1: the PE checksum (Windows does not check it for
programs) and the change `Cache` → `||che` – that is exactly patch No. 2.
"""
spec=[{'id':'customitem',
 'de':{'row':"Custom Item Fix (BETA) v2 by St0ny *(Custom-Items ohne DBC-Anpassung: Modell, Icon und Item-Typ aus den Serverdaten)* | unbekannt (v1) / St0ny (v2) | – | –",'desc':de_desc},
 'en':{'row':"Custom Item Fix (BETA) v2 by St0ny *(custom items without DBC changes: model, icon and item type from the server data)* | unknown (v1) / St0ny (v2) | – | –",'desc':en_desc}}]
json.dump(spec,open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False,indent=1)
