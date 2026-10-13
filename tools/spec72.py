import json,sys
de_desc = r"""**Addon-Daten aller Accounts zusammenlegen (SavedVariables)** *(Nr. {N}, standardmäßig aus, Autor: boredatom / St0ny)*
WoW speichert die Daten der Addons normalerweise pro Account unter
`WTF\Account\<ACCOUNT>\`. Mit dem Patch nutzen alle Accounts dafür den
gemeinsamen Ordner `WTF\Account\global\` – wer mehrere Accounts spielt, richtet
seine Addons so nur einmal ein. Zusammengelegt werden:

- die accountweiten Addon-Daten (`SavedVariables\*.lua`),
- die Addon-Daten der Charaktere (`<Realm>\<Charakter>\SavedVariables\*.lua`),
- die Liste der aktivierten Addons (`AddOns.txt`, accountweit und je Charakter).

Makros, Tastenbelegungen sowie Chat- und Spieleinstellungen bleiben wie bisher
pro Account getrennt.

> [!NOTE]
> Vorhandene Addon-Daten zieht der Patch nicht um. Wer sie behalten will,
> kopiert vor dem ersten Start den Inhalt von `WTF\Account\<ACCOUNT>\` nach
> `WTF\Account\global\`. Nimmt man den Patch zurück, nutzt WoW wieder die
> Ordner der einzelnen Accounts; `global` bleibt unverändert liegen.

Technisch ändert der Patch 9 Byte in der Funktion, die nach dem Login den
Account-Namen für die Addon-Pfade übernimmt (VA `0x5F9080`): Statt des Namens
kopiert sie den Text `global`, der schon in der `Wow.exe` steht. Das Original
von boredatom (`patch_globalvariables.exe`) verschiebt dafür den Rest der
Funktion um 4 Byte, hier bleibt alles an seinem Platz. Die Werbung, die das
Original zusätzlich in die `Wow.exe` schreibt (ein Telegram-Hinweis im
Login-Bildschirm), ist nicht enthalten.
"""
en_desc = r"""**Merge addon data of all accounts (SavedVariables)** *(No. {N}, off by default, Author: boredatom / St0ny)*
WoW normally stores addon data per account under `WTF\Account\<ACCOUNT>\`. With
this patch all accounts use the shared folder `WTF\Account\global\` instead – if
you play several accounts, you only have to set up your addons once. Merged are:

- the account-wide addon data (`SavedVariables\*.lua`),
- the per-character addon data (`<Realm>\<Character>\SavedVariables\*.lua`),
- the list of enabled addons (`AddOns.txt`, account-wide and per character).

Macros, key bindings and chat and game settings stay separate per account as
before.

> [!NOTE]
> The patch does not move existing addon data. To keep it, copy the contents of
> `WTF\Account\<ACCOUNT>\` to `WTF\Account\global\` before the first start. If
> the patch is reverted, WoW uses the folders of the individual accounts again;
> `global` is simply left as it is.

Technically the patch changes 9 bytes in the function that takes over the
account name for the addon paths after login (VA `0x5F9080`): instead of the
name it copies the text `global`, which is already in `Wow.exe`. The original by
boredatom (`patch_globalvariables.exe`) moves the rest of the function by 4 bytes
for this; here everything stays in place. The advertising that the original
additionally writes into `Wow.exe` (a Telegram notice on the login screen) is
not included.
"""
spec=[{'id':'globalsv',
 'de':{'row':r"Addon-Daten aller Accounts zusammenlegen (SavedVariables) *(gemeinsamer Ordner `WTF\Account\global`)* | boredatom / St0ny | – | –",'desc':de_desc},
 'en':{'row':r"Merge addon data of all accounts (SavedVariables) *(shared folder `WTF\Account\global`)* | boredatom / St0ny | – | –",'desc':en_desc}}]
json.dump(spec,open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False,indent=1)
