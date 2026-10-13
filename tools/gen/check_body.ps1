    AddRaw $k @(0x56)                                          # push esi
    AddRaw $k @(0x89, 0xCE)                                    # mov esi,ecx
    AddRaw $k @(0x83, 0x7E, 0x64, 0x00)                        # cmp dword ptr [esi+0x64],0
    AddRaw $k @(0x74, 0x07)                                    # je L
    AddRaw $k @(0x89, 0xF1)                                    # mov ecx,esi
    AddRaw $k @(0xE8, 0x00, 0xF7, 0xFF, 0xFF)                  # call 0x6C6B90
    # L:
    AddRaw $k @(0x89, 0xF1)                                    # mov ecx,esi
    AddRaw $k @(0xE8, 0x79, 0x06, 0x00, 0x00)                  # call 0x6C7B10
    AddRaw $k @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $k @(0x89, 0x46, 0x64)                              # mov [esi+0x64],eax
    AddRaw $k @(0x89, 0x86, 0xD4, 0x00, 0x00, 0x00)            # mov [esi+0xD4],eax
    AddRaw $k @(0x39, 0x86, 0xB0, 0x00, 0x00, 0x00)            # cmp [esi+0xB0],eax
    AddRaw $k @(0x0F, 0x95, 0xC0)                              # setne al
    AddRaw $k @(0x5E)                                          # pop esi
    AddRaw $k @(0xC3)                                          # ret
