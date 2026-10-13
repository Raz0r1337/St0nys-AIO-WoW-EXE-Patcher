    # newdesc:
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0x31, 0xD2)                                    # xor edx,edx
    AddRaw $c @(0x8B, 0x71, 0x0C)                              # mov esi,[ecx+0xC]
    AddRaw $c @(0x8B, 0x79, 0x04)                              # mov edi,[ecx+4]
    # nd_loop:
    AddRaw $c @(0x85, 0xF6)                                    # test esi,esi
    AddRaw $c @(0x74, 0x21)                                    # jz nd_end
    AddRaw $c @(0xF7, 0xC6, 0x01, 0x00, 0x00, 0x00)            # test esi,1
    AddRaw $c @(0x75, 0x19)                                    # jnz nd_end
    AddRaw $c @(0x8B, 0x5E, 0x30)                              # mov ebx,[esi+0x30]
    AddRaw $c @(0x39, 0xD3)                                    # cmp ebx,edx
    AddRaw $c @(0x76, 0x08)                                    # jbe nd_skip
    AddRaw $c @(0x29, 0xD3)                                    # sub ebx,edx
    AddRaw $c @(0x39, 0xC3)                                    # cmp ebx,eax
    AddRaw $c @(0x76, 0x02)                                    # jbe nd_skip
    AddRaw $c @(0x89, 0xD8)                                    # mov eax,ebx
    # nd_skip:
    AddRaw $c @(0x8B, 0x56, 0x34)                              # mov edx,[esi+0x34]
    AddRaw $c @(0x42)                                          # inc edx
    AddRaw $c @(0x8B, 0x74, 0x3E, 0x04)                        # mov esi,[esi+edi+4]
    AddRaw $c @(0xEB, 0xDB)                                    # jmp nd_loop
    # nd_end:
    AddRaw $c @(0xBB, 0x00, 0x01, 0x00, 0x00)                  # mov ebx,0x100
    AddRaw $c @(0x39, 0xD3)                                    # cmp ebx,edx
    AddRaw $c @(0x76, 0x08)                                    # jbe nd_store
    AddRaw $c @(0x29, 0xD3)                                    # sub ebx,edx
    AddRaw $c @(0x39, 0xC3)                                    # cmp ebx,eax
    AddRaw $c @(0x76, 0x02)                                    # jbe nd_store
    AddRaw $c @(0x89, 0xD8)                                    # mov eax,ebx
    # nd_store:
    AddRaw $c @(0x89, 0x01)                                    # mov [ecx],eax
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x0C)                              # sub esp,0xC
    AddRaw $c @(0xE9); AddLE32 $c (0x6C5126 - ($CAVE + 0x53))  # jmp 0x6C5126
    # clear:
    AddRaw $c @(0x83, 0x61, 0x60, 0x00)                        # and dword ptr [ecx+0x60],0
    AddRaw $c @(0x83, 0x61, 0x64, 0x00)                        # and dword ptr [ecx+0x64],0
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x89, 0xCE)                                    # mov esi,ecx
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0xE9); AddLE32 $c (0x6C6B96 - ($CAVE + 0x66))  # jmp 0x6C6B96
    # render:
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xCB)                                    # mov ebx,ecx
    AddRaw $c @(0x31, 0xED)                                    # xor ebp,ebp
    # rb_pass:
    AddRaw $c @(0x31, 0xFF)                                    # xor edi,edi
    AddRaw $c @(0x8B, 0x73, 0x24)                              # mov esi,[ebx+0x24]
    # rb_str:
    AddRaw $c @(0x85, 0xF6)                                    # test esi,esi
    AddRaw $c @(0x74, 0x25)                                    # jz rb_end
    AddRaw $c @(0xF7, 0xC6, 0x01, 0x00, 0x00, 0x00)            # test esi,1
    AddRaw $c @(0x75, 0x1D)                                    # jnz rb_end
    AddRaw $c @(0x8B, 0x46, 0x64)                              # mov eax,[esi+0x64]
    AddRaw $c @(0x85, 0xED)                                    # test ebp,ebp
    AddRaw $c @(0x74, 0x04)                                    # jz rb_do
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x74, 0x09)                                    # jz rb_next
    # rb_do:
    AddRaw $c @(0x09, 0xC7)                                    # or edi,eax
    AddRaw $c @(0x89, 0xF1)                                    # mov ecx,esi
    AddRaw $c @(0xE8); AddLE32 $c (0x6C7480 - ($CAVE + 0x93))  # call 0x6C7480
    # rb_next:
    AddRaw $c @(0x8B, 0x43, 0x1C)                              # mov eax,[ebx+0x1C]
    AddRaw $c @(0x8B, 0x74, 0x06, 0x04)                        # mov esi,[esi+eax+4]
    AddRaw $c @(0xEB, 0xD7)                                    # jmp rb_str
    # rb_end:
    AddRaw $c @(0x85, 0xFF)                                    # test edi,edi
    AddRaw $c @(0x74, 0x06)                                    # jz rb_out
    AddRaw $c @(0x45)                                          # inc ebp
    AddRaw $c @(0x83, 0xFD, 0x04)                              # cmp ebp,4
    AddRaw $c @(0x72, 0xC8)                                    # jb rb_pass
    # rb_out:
    AddRaw $c @(0x89, 0xD9)                                    # mov ecx,ebx
    AddRaw $c @(0x5D)                                          # pop ebp
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x20)                              # sub esp,0x20
    AddRaw $c @(0xE9); AddLE32 $c (0x6C4AD6 - ($CAVE + 0xB7))  # jmp 0x6C4AD6
    # tex:
    AddRaw $c @(0x83, 0x7C, 0x24, 0x04, 0x01)                  # cmp dword ptr [esp+4],1
    AddRaw $c @(0x75, 0x14)                                    # jne tx_go
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x51)                                          # push ecx
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xBF, 0x28, 0xD3, 0xC7, 0x00)                  # mov edi,0xC7D328
    AddRaw $c @(0xB9, 0x00, 0x80, 0x00, 0x00)                  # mov ecx,0x8000
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0xF3, 0xAB)                                    # rep stosd
    AddRaw $c @(0x58)                                          # pop eax
    AddRaw $c @(0x59)                                          # pop ecx
    AddRaw $c @(0x5F)                                          # pop edi
    # tx_go:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x51)                                          # push ecx
    AddRaw $c @(0x83, 0x7D, 0x08, 0x01)                        # cmp dword ptr [ebp+8],1
    AddRaw $c @(0xE9); AddLE32 $c (0x6C9F58 - ($CAVE + 0xDF))  # jmp 0x6C9F58
