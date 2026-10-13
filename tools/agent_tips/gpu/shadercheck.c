/* shadercheck.c - independent check of psasm bytecode with Wine's own tools:
 *   D3DXAssembleShader (d3dx9_43) on the reference asm text -> byte compare with the psasm output,
 *   D3DXDisassembleShader (d3dx9_43) and D3DDisassemble (d3dcompiler_47, vkd3d-shader) of the psasm bytes,
 *   IDirect3DDevice9::CreatePixelShader on a HAL device (wined3d parses the bytecode).
 * usage: shadercheck.exe shader.bin shader.asm */
#define COBJMACROS
#include <windows.h>
#include <d3d9.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct XBuf XBuf;
typedef struct { HRESULT (WINAPI *QI)(XBuf *, REFIID, void **); ULONG (WINAPI *AddRef)(XBuf *); ULONG (WINAPI *Release)(XBuf *);
                 void *(WINAPI *GetBufferPointer)(XBuf *); DWORD (WINAPI *GetBufferSize)(XBuf *); } XBufVtbl;
struct XBuf { const XBufVtbl *lpVtbl; };
typedef HRESULT (WINAPI *PASM)(const char *, UINT, const void *, void *, DWORD, XBuf **, XBuf **);
typedef HRESULT (WINAPI *PDIS)(const DWORD *, BOOL, const char *, XBuf **);
typedef HRESULT (WINAPI *PDIS2)(const void *, SIZE_T, UINT, const char *, XBuf **);

static void *readall(const char *fn, long *n) {
    FILE *f = fopen(fn, "rb"); void *p; if (!f) { printf("cannot open %s\n", fn); exit(1); }
    fseek(f, 0, SEEK_END); *n = ftell(f); fseek(f, 0, SEEK_SET); p = calloc(1, *n + 1); fread(p, 1, *n, f); fclose(f); return p;
}
/* split a token stream into instructions; the leading def/dcl block is compared as a set */
static int ninstr(const DWORD *t, DWORD n, DWORD *starts) {
    DWORD i = 1; int c = 0;
    while (i < n && t[i] != 0x0000FFFF) { starts[c++] = i; i += 1 + ((t[i] >> 24) & 0xF); }
    return c;
}
static int isdecl(DWORD tok) { DWORD op = tok & 0xFFFF; return op == 0x1F || op == 0x51; }
static int canon_equal(const DWORD *a, const DWORD *b, DWORD n) {
    DWORD sa[256], sb[256]; int na = ninstr(a, n, sa), nb2 = ninstr(b, n, sb), i, j, da = 0, db = 0;
    if (na != nb2 || a[0] != b[0]) return 0;
    while (da < na && isdecl(a[sa[da]])) da++;
    while (db < nb2 && isdecl(b[sb[db]])) db++;
    if (da != db) return 0;
    for (i = 0; i < da; i++) {          /* every declaration of a appears in b */
        int found = 0; DWORD la = 1 + ((a[sa[i]] >> 24) & 0xF);
        for (j = 0; j < db && !found; j++) if (!memcmp(a + sa[i], b + sb[j], la * 4)) found = 1;
        if (!found) return 0;
    }
    return !memcmp(a + sa[da], b + sb[db], (n - sa[da]) * 4);
}
static LRESULT CALLBACK wp(HWND h, UINT m, WPARAM w, LPARAM l) { return DefWindowProcA(h, m, w, l); }

int main(int argc, char **argv) {
    long nb, nt; DWORD *bin = readall(argv[1], &nb); char *txt = readall(argv[2], &nt);
    HMODULE x = LoadLibraryA("d3dx9_43.dll"), c = LoadLibraryA("d3dcompiler_47.dll");
    PASM as = x ? (PASM)GetProcAddress(x, "D3DXAssembleShader") : NULL;
    PDIS dis = x ? (PDIS)GetProcAddress(x, "D3DXDisassembleShader") : NULL;
    PDIS2 dis2 = c ? (PDIS2)GetProcAddress(c, "D3DDisassemble") : NULL;
    XBuf *out = NULL, *err = NULL; HRESULT hr; int rc = 0;
    printf("psasm bytes: %ld\n", nb);
    if (as) {
        hr = as(txt, (UINT)nt, NULL, NULL, 0, &out, &err);
        printf("D3DXAssembleShader => 0x%08lX\n", hr);
        if (err) { printf("  messages: %s\n", (char *)err->lpVtbl->GetBufferPointer(err)); err->lpVtbl->Release(err); }
        if (SUCCEEDED(hr)) {
            DWORD sz = out->lpVtbl->GetBufferSize(out); const DWORD *p = out->lpVtbl->GetBufferPointer(out);
            /* D3DX may insert a comment block (CTAB/version string); compare after removing comment tokens */
            DWORD i = 0, k = 0, *s = calloc(sz / 4 + 1, 4);
            while (i < sz / 4) { if ((p[i] & 0xFFFF) == 0xFFFE) { i += 1 + (p[i] >> 16); continue; } s[k++] = p[i++]; }
            {   /* canonical compare: the def/dcl block may come in any order, the instruction stream must match exactly */
                int same = (k * 4 == (DWORD)nb) && canon_equal(s, bin, k);
                printf("  assembled %lu bytes (%lu without comments) -> %s psasm (byte-identical: %s)\n", sz, k * 4,
                       same ? "SAME TOKENS as" : "DIFFERENT from", (k * 4 == (DWORD)nb && !memcmp(s, bin, nb)) ? "yes" : "no, declaration order only");
                if (!same) { rc = 1; for (i = 0; i < k; i++) printf("  %08lX %08lX\n", s[i], i < (DWORD)nb / 4 ? bin[i] : 0); }
            }
            out->lpVtbl->Release(out);
        } else rc = 1;
    } else printf("D3DXAssembleShader not available\n");
    if (dis) {
        out = NULL; hr = dis(bin, FALSE, NULL, &out);
        printf("D3DXDisassembleShader => 0x%08lX\n%s\n", hr, SUCCEEDED(hr) ? (char *)out->lpVtbl->GetBufferPointer(out) : "");
        if (out) out->lpVtbl->Release(out); if (FAILED(hr)) rc = 1;
    }
    if (dis2) {
        out = NULL; hr = dis2(bin, nb, 0, NULL, &out);
        printf("D3DDisassemble (d3dcompiler_47) => 0x%08lX\n%s\n", hr, SUCCEEDED(hr) ? (char *)out->lpVtbl->GetBufferPointer(out) : "");
        if (out) out->lpVtbl->Release(out); if (FAILED(hr)) rc = 1;
    }
    {
        IDirect3D9 *d3d = Direct3DCreate9(D3D_SDK_VERSION); IDirect3DDevice9 *dev = NULL; IDirect3DPixelShader9 *ps = NULL;
        D3DPRESENT_PARAMETERS pp; WNDCLASSA wc; HWND h; D3DCAPS9 caps;
        memset(&wc, 0, sizeof wc); wc.lpfnWndProc = wp; wc.hInstance = GetModuleHandleA(NULL); wc.lpszClassName = "sc"; RegisterClassA(&wc);
        h = CreateWindowA("sc", "sc", WS_OVERLAPPEDWINDOW, 0, 0, 64, 64, NULL, NULL, wc.hInstance, NULL);
        memset(&pp, 0, sizeof pp); pp.Windowed = TRUE; pp.SwapEffect = D3DSWAPEFFECT_DISCARD; pp.BackBufferFormat = D3DFMT_UNKNOWN; pp.hDeviceWindow = h;
        hr = IDirect3D9_CreateDevice(d3d, 0, D3DDEVTYPE_HAL, h, D3DCREATE_SOFTWARE_VERTEXPROCESSING, &pp, &dev);
        printf("CreateDevice => 0x%08lX\n", hr);
        if (SUCCEEDED(hr)) {
            IDirect3DDevice9_GetDeviceCaps(dev, &caps);
            printf("PS caps %lu.%lu\n", (caps.PixelShaderVersion >> 8) & 0xFF, caps.PixelShaderVersion & 0xFF);
            hr = IDirect3DDevice9_CreatePixelShader(dev, bin, &ps);
            printf("CreatePixelShader => 0x%08lX\n", hr); if (FAILED(hr)) rc = 1;
            if (ps) {
                UINT n = 0; IDirect3DPixelShader9_GetFunction(ps, NULL, &n); printf("GetFunction size %u (input %ld)\n", n, nb);
                IDirect3DPixelShader9_Release(ps);
            }
            IDirect3DDevice9_Release(dev);
        } else rc = 1;
        IDirect3D9_Release(d3d);
    }
    printf("RESULT %s\n", rc ? "FAIL" : "OK");
    return rc;
}
