    # exec:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x81, 0xEC, 0x04, 0x01, 0x00, 0x00)            # sub esp,0x104
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x89, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov [ebp-0x104],ecx
    AddRaw $c @(0xC6, 0x85, 0x00, 0xFF, 0xFF, 0xFF, 0x00)      # mov byte ptr [ebp-0x100],0
    AddRaw $c @(0x68, 0x80, 0x00, 0x00, 0x00)                  # push 0x80
    AddRaw $c @(0x8D, 0x85, 0x00, 0xFF, 0xFF, 0xFF)            # lea eax,[ebp-0x100]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xFF, 0x75, 0x0C)                              # push dword ptr [ebp+0xC]
    AddRaw $c @(0xFF, 0x75, 0x18)                              # push dword ptr [ebp+0x18]
    AddRaw $c @(0xE8); AddLE32 $c (0x5622E0 - ($CAVE + 0x150)) # call 0x5622E0
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0x47, 0x01, 0x00, 0x00)            # jz ex_orig
    AddRaw $c @(0xFF, 0x75, 0x18)                              # push dword ptr [ebp+0x18]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0x8B, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov ecx,[ebp-0x104]
    AddRaw $c @(0xE8); AddLE32 $c (0x55E470 - ($CAVE + 0x167)) # call 0x55E470
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0x30, 0x01, 0x00, 0x00)            # jz ex_orig
    AddRaw $c @(0x89, 0xC6)                                    # mov esi,eax
    AddRaw $c @(0xBF); AddLE32 $c ($CAVE + 0x114)              # mov edi,strab
    AddRaw $c @(0xB9, 0x0C, 0x00, 0x00, 0x00)                  # mov ecx,12
    # ex_cmp:
    AddRaw $c @(0x8A, 0x06)                                    # mov al,[esi]
    AddRaw $c @(0x3C, 0x61)                                    # cmp al,0x61
    AddRaw $c @(0x72, 0x06)                                    # jb ex_c1
    AddRaw $c @(0x3C, 0x7A)                                    # cmp al,0x7A
    AddRaw $c @(0x77, 0x02)                                    # ja ex_c1
    AddRaw $c @(0x2C, 0x20)                                    # sub al,0x20
    # ex_c1:
    AddRaw $c @(0x3A, 0x07)                                    # cmp al,[edi]
    AddRaw $c @(0x0F, 0x85, 0x10, 0x01, 0x00, 0x00)            # jne ex_orig
    AddRaw $c @(0x46)                                          # inc esi
    AddRaw $c @(0x47)                                          # inc edi
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xE7)                                    # jnz ex_cmp
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    # ex_dig:
    AddRaw $c @(0x0F, 0xB6, 0x16)                              # movzx edx,byte ptr [esi]
    AddRaw $c @(0x83, 0xEA, 0x30)                              # sub edx,0x30
    AddRaw $c @(0x83, 0xFA, 0x09)                              # cmp edx,9
    AddRaw $c @(0x77, 0x11)                                    # ja ex_num
    AddRaw $c @(0x6B, 0xC0, 0x0A)                              # imul eax,eax,10
    AddRaw $c @(0x01, 0xD0)                                    # add eax,edx
    AddRaw $c @(0x83, 0xF8, 0x0C)                              # cmp eax,12
    AddRaw $c @(0x0F, 0x87, 0xF0, 0x00, 0x00, 0x00)            # ja ex_orig
    AddRaw $c @(0x46)                                          # inc esi
    AddRaw $c @(0xEB, 0xE4)                                    # jmp ex_dig
    # ex_num:
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0xE5, 0x00, 0x00, 0x00)            # jz ex_orig
    AddRaw $c @(0x8D, 0x58, 0xFF)                              # lea ebx,[eax-1]
    AddRaw $c @(0x83, 0x3D, 0xA0, 0xE5, 0xC1, 0x00, 0x00)      # cmp dword ptr [0xC1E5A0],0
    AddRaw $c @(0x74, 0x07)                                    # je ex_p1
    AddRaw $c @(0xBA, 0x01, 0x00, 0x00, 0x00)                  # mov edx,1
    AddRaw $c @(0xEB, 0x07)                                    # jmp ex_p2
    # ex_p1:
    AddRaw $c @(0x8B, 0x15, 0x98, 0xE5, 0xC1, 0x00)            # mov edx,dword ptr [0xC1E598]
    AddRaw $c @(0x42)                                          # inc edx
    # ex_p2:
    AddRaw $c @(0x83, 0xFA, 0x01)                              # cmp edx,1
    AddRaw $c @(0x75, 0x0D)                                    # jne ex_p3
    AddRaw $c @(0x8B, 0x0D, 0x9C, 0xE5, 0xC1, 0x00)            # mov ecx,dword ptr [0xC1E59C]
    AddRaw $c @(0x85, 0xC9)                                    # test ecx,ecx
    AddRaw $c @(0x74, 0x03)                                    # jz ex_p3
    AddRaw $c @(0x8D, 0x51, 0x06)                              # lea edx,[ecx+6]
    # ex_p3:
    AddRaw $c @(0x4A)                                          # dec edx
    AddRaw $c @(0x6B, 0xD2, 0x0C)                              # imul edx,edx,12
    AddRaw $c @(0x01, 0xD3)                                    # add ebx,edx
    AddRaw $c @(0x8B, 0x55, 0x0C)                              # mov edx,[ebp+0xC]
    AddRaw $c @(0xE8, 0xC5, 0x00, 0x00, 0x00)                  # call find
    AddRaw $c @(0x83, 0x7D, 0x10, 0x00)                        # cmp dword ptr [ebp+0x10],0
    AddRaw $c @(0x74, 0x5D)                                    # je ex_up
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x75, 0x0D)                                    # jnz ex_init
    AddRaw $c @(0xE8, 0xD3, 0x00, 0x00, 0x00)                  # call findfree
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0x94, 0x00, 0x00, 0x00)            # jz ex_orig
    # ex_init:
    AddRaw $c @(0x89, 0xC6)                                    # mov esi,eax
    AddRaw $c @(0x89, 0x5E, 0x04)                              # mov [esi+4],ebx
    AddRaw $c @(0xE8); AddLE32 $c (0x86AE20 - ($CAVE + 0x215)) # call 0x86AE20
    AddRaw $c @(0x89, 0x46, 0x08)                              # mov [esi+8],eax
    AddRaw $c @(0x89, 0x46, 0x0C)                              # mov [esi+12],eax
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0x89, 0x46, 0x10)                              # mov [esi+16],eax
    AddRaw $c @(0x89, 0x46, 0x14)                              # mov [esi+20],eax
    AddRaw $c @(0x8B, 0x55, 0x0C)                              # mov edx,[ebp+0xC]
    AddRaw $c @(0x89, 0x16)                                    # mov [esi],edx
    AddRaw $c @(0xC7, 0x46, 0x18, 0x01, 0x00, 0x00, 0x00)      # mov dword ptr [esi+24],1
    AddRaw $c @(0x83, 0x3D); AddLE32 $c ($CAVE + 0x104); AddRaw $c @(0x00) # cmp dword ptr [evreg],0
    AddRaw $c @(0x75, 0x67)                                    # jne ex_orig
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x104); AddRaw $c @(0x01, 0x00, 0x00, 0x00) # mov dword ptr [evreg],1
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0x68); AddLE32 $c ($CAVE + 0x2EF)              # push focus
    AddRaw $c @(0x6A, 0x02)                                    # push 2
    AddRaw $c @(0xE8); AddLE32 $c (0x47D3C0 - ($CAVE + 0x252)) # call 0x47D3C0
    AddRaw $c @(0x83, 0xC4, 0x10)                              # add esp,16
    AddRaw $c @(0xEB, 0x48)                                    # jmp ex_orig
    # ex_up:
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x74, 0x44)                                    # jz ex_orig
    AddRaw $c @(0xC7, 0x40, 0x18, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [eax+24],0
    AddRaw $c @(0x83, 0x78, 0x14, 0x00)                        # cmp dword ptr [eax+20],0
    AddRaw $c @(0x74, 0x37)                                    # je ex_orig
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x01, 0x00, 0x00, 0x00) # mov dword ptr [suppress],1
    AddRaw $c @(0xFF, 0x75, 0x18)                              # push dword ptr [ebp+0x18]
    AddRaw $c @(0xFF, 0x75, 0x14)                              # push dword ptr [ebp+0x14]
    AddRaw $c @(0xFF, 0x75, 0x10)                              # push dword ptr [ebp+0x10]
    AddRaw $c @(0xFF, 0x75, 0x0C)                              # push dword ptr [ebp+0xC]
    AddRaw $c @(0xFF, 0x75, 0x08)                              # push dword ptr [ebp+8]
    AddRaw $c @(0x8B, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov ecx,[ebp-0x104]
    AddRaw $c @(0xE8, 0x1F, 0x00, 0x00, 0x00)                  # call exec_tramp
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x00, 0x00, 0x00, 0x00) # mov dword ptr [suppress],0
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x89, 0xEC)                                    # mov esp,ebp
    AddRaw $c @(0x5D)                                          # pop ebp
    AddRaw $c @(0xC2, 0x14, 0x00)                              # ret 0x14
    # ex_orig:
    AddRaw $c @(0x8B, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov ecx,[ebp-0x104]
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x89, 0xEC)                                    # mov esp,ebp
    AddRaw $c @(0x5D)                                          # pop ebp
    # exec_tramp:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x81, 0xEC, 0xC4, 0x00, 0x00, 0x00)            # sub esp,0xC4
    AddRaw $c @(0xE9); AddLE32 $c (0x563159 - ($CAVE + 0x2B9)) # jmp 0x563159
    # find:
    AddRaw $c @(0xB8); AddLE32 $c ($CAVE + 0x0)                # mov eax,held
    AddRaw $c @(0xB9, 0x08, 0x00, 0x00, 0x00)                  # mov ecx,8
    # f_l:
    AddRaw $c @(0x83, 0x78, 0x18, 0x00)                        # cmp dword ptr [eax+24],0
    AddRaw $c @(0x74, 0x04)                                    # je f_n
    AddRaw $c @(0x39, 0x10)                                    # cmp [eax],edx
    AddRaw $c @(0x74, 0x08)                                    # je f_r
    # f_n:
    AddRaw $c @(0x83, 0xC0, 0x20)                              # add eax,32
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xF0)                                    # jnz f_l
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    # f_r:
    AddRaw $c @(0xC3)                                          # ret
    # findfree:
    AddRaw $c @(0xB8); AddLE32 $c ($CAVE + 0x0)                # mov eax,held
    AddRaw $c @(0xB9, 0x08, 0x00, 0x00, 0x00)                  # mov ecx,8
    # ff_l:
    AddRaw $c @(0x83, 0x78, 0x18, 0x00)                        # cmp dword ptr [eax+24],0
    AddRaw $c @(0x74, 0x08)                                    # je ff_r
    AddRaw $c @(0x83, 0xC0, 0x20)                              # add eax,32
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xF4)                                    # jnz ff_l
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    # ff_r:
    AddRaw $c @(0xC3)                                          # ret
    # focus:
    AddRaw $c @(0xB8); AddLE32 $c ($CAVE + 0x0)                # mov eax,held
    AddRaw $c @(0xB9, 0x08, 0x00, 0x00, 0x00)                  # mov ecx,8
    # fo_l:
    AddRaw $c @(0xC7, 0x40, 0x18, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [eax+24],0
    AddRaw $c @(0x83, 0xC0, 0x20)                              # add eax,32
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xF3)                                    # jnz fo_l
    AddRaw $c @(0xB8, 0x01, 0x00, 0x00, 0x00)                  # mov eax,1
    AddRaw $c @(0xC3)                                          # ret
    # use:
    AddRaw $c @(0x83, 0x3D); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x00) # cmp dword ptr [suppress],0
    AddRaw $c @(0x74, 0x0B)                                    # je use_tramp
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x00, 0x00, 0x00, 0x00) # mov dword ptr [suppress],0
    AddRaw $c @(0xC3)                                          # ret
    # use_tramp:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x0C)                              # sub esp,0xC
    AddRaw $c @(0xE9); AddLE32 $c (0x5ABBC6 - ($CAVE + 0x32B)) # jmp 0x5ABBC6
    # render:
    AddRaw $c @(0xE8, 0x08, 0x00, 0x00, 0x00)                  # call render_tramp
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xE8, 0x0D, 0x00, 0x00, 0x00)                  # call update
    AddRaw $c @(0x58)                                          # pop eax
    AddRaw $c @(0xC3)                                          # ret
    # render_tramp:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x34)                              # sub esp,0x34
    AddRaw $c @(0xE9); AddLE32 $c (0x4F8EA6 - ($CAVE + 0x343)) # jmp 0x4F8EA6
    # update:
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x83, 0xEC, 0x0C)                              # sub esp,12
    AddRaw $c @(0x89, 0xE3)                                    # mov ebx,esp
    AddRaw $c @(0xE8); AddLE32 $c (0x86AE20 - ($CAVE + 0x351)) # call 0x86AE20
    AddRaw $c @(0x89, 0xC5)                                    # mov ebp,eax
    AddRaw $c @(0xBE); AddLE32 $c ($CAVE + 0x0)                # mov esi,held
    AddRaw $c @(0xBF, 0x08, 0x00, 0x00, 0x00)                  # mov edi,8
    # up_l:
    AddRaw $c @(0x83, 0x7E, 0x18, 0x00)                        # cmp dword ptr [esi+24],0
    AddRaw $c @(0x0F, 0x84, 0xA8, 0x00, 0x00, 0x00)            # je up_n
    AddRaw $c @(0x89, 0xE8)                                    # mov eax,ebp
    AddRaw $c @(0x2B, 0x46, 0x08)                              # sub eax,[esi+8]
    AddRaw $c @(0x3D, 0xF4, 0x01, 0x00, 0x00)                  # cmp eax,500
    AddRaw $c @(0x0F, 0x82, 0x98, 0x00, 0x00, 0x00)            # jb up_n
    AddRaw $c @(0x83, 0x3D, 0xE4, 0xF4, 0xD3, 0x00, 0x00)      # cmp dword ptr [0xD3F4E4],0
    AddRaw $c @(0x74, 0x0C)                                    # je up_nc
    AddRaw $c @(0xC7, 0x46, 0x10, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [esi+16],0
    AddRaw $c @(0xE9, 0x83, 0x00, 0x00, 0x00)                  # jmp up_n
    # up_nc:
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0x89, 0x03)                                    # mov [ebx],eax
    AddRaw $c @(0x89, 0x43, 0x04)                              # mov [ebx+4],eax
    AddRaw $c @(0x89, 0x43, 0x08)                              # mov [ebx+8],eax
    AddRaw $c @(0x8D, 0x43, 0x08)                              # lea eax,[ebx+8]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0x8D, 0x43, 0x04)                              # lea eax,[ebx+4]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0xFF, 0x76, 0x04)                              # push dword ptr [esi+4]
    AddRaw $c @(0xE8); AddLE32 $c (0x5A8E40 - ($CAVE + 0x3A7)) # call 0x5A8E40
    AddRaw $c @(0x83, 0xC4, 0x10)                              # add esp,16
    AddRaw $c @(0x8B, 0x43, 0x04)                              # mov eax,[ebx+4]
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x7E, 0x11)                                    # jle up_ready
    AddRaw $c @(0x89, 0xE9)                                    # mov ecx,ebp
    AddRaw $c @(0x2B, 0x0B)                                    # sub ecx,[ebx]
    AddRaw $c @(0x39, 0xC1)                                    # cmp ecx,eax
    AddRaw $c @(0x73, 0x09)                                    # jae up_ready
    AddRaw $c @(0xC7, 0x46, 0x10, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [esi+16],0
    AddRaw $c @(0xEB, 0x4D)                                    # jmp up_n
    # up_ready:
    AddRaw $c @(0x83, 0x7E, 0x10, 0x00)                        # cmp dword ptr [esi+16],0
    AddRaw $c @(0x75, 0x03)                                    # jne up_r2
    AddRaw $c @(0x89, 0x6E, 0x10)                              # mov [esi+16],ebp
    # up_r2:
    AddRaw $c @(0x89, 0xE8)                                    # mov eax,ebp
    AddRaw $c @(0x2B, 0x46, 0x10)                              # sub eax,[esi+16]
    AddRaw $c @(0x83, 0xF8, 0x64)                              # cmp eax,100
    AddRaw $c @(0x72, 0x3A)                                    # jb up_n
    AddRaw $c @(0x89, 0xE8)                                    # mov eax,ebp
    AddRaw $c @(0x2B, 0x46, 0x0C)                              # sub eax,[esi+12]
    AddRaw $c @(0x83, 0xF8, 0x64)                              # cmp eax,100
    AddRaw $c @(0x72, 0x30)                                    # jb up_n
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0xA3); AddLE32 $c ($CAVE + 0x108)              # mov dword ptr [guid],eax
    AddRaw $c @(0xA3); AddLE32 $c ($CAVE + 0x10C)              # mov dword ptr [guid+4],eax
    AddRaw $c @(0xA3); AddLE32 $c ($CAVE + 0x110)              # mov dword ptr [btn],eax
    AddRaw $c @(0x68); AddLE32 $c ($CAVE + 0x110)              # push btn
    AddRaw $c @(0x68); AddLE32 $c ($CAVE + 0x108)              # push guid
    AddRaw $c @(0xFF, 0x76, 0x04)                              # push dword ptr [esi+4]
    AddRaw $c @(0xE8, 0x1E, 0xFF, 0xFF, 0xFF)                  # call use_tramp
    AddRaw $c @(0x83, 0xC4, 0x0C)                              # add esp,12
    AddRaw $c @(0x89, 0x6E, 0x0C)                              # mov [esi+12],ebp
    AddRaw $c @(0xC7, 0x46, 0x14, 0x01, 0x00, 0x00, 0x00)      # mov dword ptr [esi+20],1
    # up_n:
    AddRaw $c @(0x83, 0xC6, 0x20)                              # add esi,32
    AddRaw $c @(0x4F)                                          # dec edi
    AddRaw $c @(0x0F, 0x85, 0x44, 0xFF, 0xFF, 0xFF)            # jnz up_l
    AddRaw $c @(0x83, 0xC4, 0x0C)                              # add esp,12
    AddRaw $c @(0x5D)                                          # pop ebp
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0xC3)                                          # ret
