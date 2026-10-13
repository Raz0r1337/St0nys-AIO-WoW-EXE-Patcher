R('''       De = 'HD Unit-Frame Portraits: 256x256 (live 3D-Portraits)'
       En = 'HD unit frame portraits: 256x256 (live 3D portraits)'
''','''       De = 'HD Unit-Frame Portraits: Renderaufloesung 256 statt 64 Pixel'
       En = 'HD unit frame portraits: render resolution 256 instead of 64 pixels'
''')
R('''        # Haengt die .hdp-Sektion an und biegt den Model-Render-Pfad auf 256px um.
''','''        # Haengt die .hdp-Sektion an und biegt den Model-Render-Pfad auf 256px um.
        # Erzeugt keine neuen Portraits: Die Unit-Frames zeigen schon im Original
        # das 3D-Modell, nur die Textur, in die es gerendert wird, waechst von
        # 64x64 auf 256x256 Pixel. Die Groesse ist der einzige Parameter.
''')
