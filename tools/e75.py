a=s.index("    @{ Id = 'awesome';"); b=s.index("    @{ Id = 'keyprop';")
blk=s[a:b]; s=s[:a]+s[b:]
blk=blk.replace("Cat = 'modding'","Cat = 'dll'")
assert blk.count("Cat = 'dll'")==2
R("    # --- Gameplay-Fixes ---\n", "    # --- DLL-Loader ---\n\n"+blk+"    # --- Gameplay-Fixes ---\n")
R("""    modding  = @{ De = 'Modding: Interface, MPQs & Addons'; En = 'Modding: interface, MPQs & addons' }
""","""    modding  = @{ De = 'Modding: Interface, MPQs & Addons'; En = 'Modding: interface, MPQs & addons' }
    dll      = @{ De = 'DLL-Loader';                        En = 'DLL loaders' }
""")
s=s.replace("Billy''s_Wow.exe (edited by St0ny)","St0nys_Wow.exe").replace("Billy's_Wow.exe (edited by St0ny)","St0nys_Wow.exe")
