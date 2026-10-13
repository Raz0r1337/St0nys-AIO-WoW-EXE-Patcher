import sys
d=sys.argv[1]
def rep(fn,pairs,enc='utf-8'):
    p=d+'/'+fn; s=open(p,'rb').read().decode(enc)
    for a,b in pairs:
        assert s.count(a)==1,(fn,a[:70],s.count(a)); s=s.replace(a,b)
    open(p,'wb').write(s.encode(enc))
DE_OLD='Level 101+ Druid Fix (Spielwert-Tabellen, Barbierstuhl, Grundwerte)'
EN_OLD='Level 101+ Druid fix (game tables, barber chair, base stats)'
DE_NEW='Level 101+ Druid Fix (Druiden-Werte im Charakterfenster, Barbierstuhl für alle)'
EN_NEW='Level 101+ Druid fix (druid stats in the character window, barber shop for everyone)'
rep('apply_patches.ps1',[("De = '%s'"%DE_OLD,"De = '%s'"%DE_NEW.replace('ü','ue')),("En = '%s'"%EN_OLD,"En = '%s'"%EN_NEW)],'ascii')
rep('README.de.md',[('| '+DE_OLD+' |','| '+DE_NEW+' |')])
rep('README.md',[('| '+EN_OLD+' |','| '+EN_NEW+' |')])
rep('PATCHES.de.md',[('**'+DE_OLD+'**','**'+DE_NEW+'**'),
 ('100 Zeilen, eine pro Level. Ab Level 101 greift der Client außerhalb der Spalte\nzu – Druiden sehen ihre Grundwerte nicht mehr, der Barbierstuhl funktioniert\nnicht, im schlimmsten Fall stürzt der Client ab. Der Patch begrenzt die Zeile\nauf die letzte der Spalte:',
  '100 Zeilen, eine pro Level. Ab Level 101 greift der Client außerhalb der Spalte\nzu. Das fällt vor allem an zwei Stellen auf:\n- **Druiden** sehen im Charakterfenster (Reiter Charakterinfo) ihre Werte nicht\n  mehr richtig.\n- Der **Barbierstuhl** funktioniert für **alle Klassen** nicht mehr.\n\nIm schlimmsten Fall stürzt der Client ab. Der Patch begrenzt die Zeile auf die\nletzte der Spalte:')])
rep('PATCHES.en.md',[('**'+EN_OLD+'**','**'+EN_NEW+'**'),
 ('column, one per level. From level 101 on the client reads outside the column –\ndruids no longer see their base stats, the barber chair does not work, in the\nworst case the client crashes. The patch clamps the row to the last one of the\ncolumn:',
  'column, one per level. From level 101 on the client reads outside the column.\nThis shows up mainly in two places:\n- **Druids** no longer see their stats correctly in the character window\n  (character info tab).\n- The **barber shop** no longer works for **all classes**.\n\nIn the worst case the client crashes. The patch clamps the row to the last one\nof the column:')])
print('ok',d)
