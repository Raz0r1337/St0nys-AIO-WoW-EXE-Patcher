/* tips_test.c - outline at thin features on real D3D9 (Wine/wined3d): current pipeline vs the agent_tips fix.
 * Derived from agent_shimmer/shimmer_test.c (same post call sequence as outline10 glow/g_pass/mkq/quad).
 *   old  : copies at (+-2,0),(0,+-2),(+-2,+-2); ring -> MSRT -> TEX0 -> tent TEX1 -> H TEX2 -> V+curve(2.5) TEX1 ->
 *          composite (stencil < 0x80), then the thin line = full-screen quad light(colour) on stencil == ring
 *   new  : copies at (+-1,0),(0,+-1),(+-1,+-1); ring -> MSRT -> TEX0 -> line_ps (3x3 tent, sat(4x)) TEX3 (full res) ->
 *          tent TEX3 -> TEX1 -> H -> V+curve(2.0) -> composite glow, then composite line (linecomp_ps, TEX3); no quads
 *   nsq  : like new, copies (+-1,+-1) + (+-0.5,0),(0,+-0.5)   nsqd: (+-1,+-1) + (+-0.5,+-0.5)
 * Colours: background black, figure red, ring/glow green -> G channel = composite, R = figure, B = line (94/255*a)
 * usage: tips_test.exe ms variant outdir [W H] [bench_iters] [nunits]
 *   writes outdir/bb.raw (all frames, W*H*4 BGRA); bench: times scene + post for frame 0 (nunits outlined categories) */
#define COBJMACROS
#include <windows.h>
#include <d3d9.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "tips_shaders.h"

#define FIGCOL 0xFFFF0000
#define RINGCOL 0xFF00FF00
#define FIG 0x80
static IDirect3DDevice9 *dev;
static IDirect3DPixelShader9 *PS, *GPS, *CPS, *TPS, *VPSO, *VPSN, *LPS, *LCPS;
static IDirect3DSurface9 *MSRT, *TEX0S, *TEX1S, *TEX2S, *TEX3S, *BBP, *DSP;
static IDirect3DTexture9 *TEX0, *TEX1, *TEX2, *TEX3;
static UINT RTW, RTH, RTW2, RTH2;
static D3DVIEWPORT9 VP;
typedef struct { float x, y, z, rhw; DWORD c; } V44;
static V44 VERTS[4];
static float VERTT[4][14];
static float QX0, QY0, QX1, QY1, QU0, QV0, QU1, QV1, QDU, QDV;
static const float O1 = 1.3846154f, O2 = 3.2307692f, HALF = 0.5f;
static float TQ, TL;
static int isnew, nfail, nunits = 1;
static const float (*OFFS)[2]; static int NOFFS = 8;
static const float OFF_OLD[8][2] = { {2, 0}, {-2, 0}, {0, 2}, {0, -2}, {2, 2}, {2, -2}, {-2, 2}, {-2, -2} };
static const float OFF_NEW[8][2] = { {1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, 1}, {1, -1}, {-1, 1}, {-1, -1} };
static const float OFF_NSQ[8][2] = { {1, 1}, {1, -1}, {-1, 1}, {-1, -1}, {0.5f, 0}, {-0.5f, 0}, {0, 0.5f}, {0, -0.5f} };
static const float OFF_NSQD[8][2] = { {1, 1}, {1, -1}, {-1, 1}, {-1, -1}, {0.5f, 0.5f}, {-0.5f, -0.5f}, {0.5f, -0.5f}, {-0.5f, 0.5f} };
static V44 *tri; static int ntri;

static void chk(HRESULT hr, const char *w) { if (FAILED(hr)) { nfail++; printf("FAILED 0x%08lX %s\n", hr, w); } }
static void mkq(void) {           /* x87 semantics of outline10 mkq: (float)(c +- (double)d * o) */
    int k, j;
    for (k = 0; k < 4; k++) {
        float *v = VERTT[k]; float u = (k & 1) ? QU1 : QU0, w = (k & 2) ? QV1 : QV0;
        v[0] = (k & 1) ? QX1 : QX0; v[1] = (k & 2) ? QY1 : QY0; v[2] = 0.0f; v[3] = 1.0f; v[4] = u; v[5] = w;
        for (j = 0; j < 4; j++) {
            double o = j < 2 ? O1 : O2; int sg = (j & 1) ? -1 : 1;
            v[6 + 2 * j] = (float)((double)u + sg * (double)QDU * o);
            v[7 + 2 * j] = (float)((double)w + sg * (double)QDV * o);
        }
    }
}
static void g_pass(IDirect3DTexture9 *src, IDirect3DSurface9 *dst) {
    chk(IDirect3DDevice9_SetTexture(dev, 0, (IDirect3DBaseTexture9 *)src), "SetTexture");
    chk(IDirect3DDevice9_SetRenderTarget(dev, 0, dst), "SetRT pass");
    mkq(); chk(IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLESTRIP, 2, VERTT, 56), "DPUP pass");
}
static void quad(int cat, DWORD col) {
    int k; for (k = 0; k < 4; k++) VERTS[k].c = col;
    IDirect3DDevice9_SetRenderState(dev, D3DRS_STENCILREF, cat);
    chk(IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLESTRIP, 2, VERTS, 20), "DPUP quad");
}
static void SRS(DWORD s, DWORD v) { chk(IDirect3DDevice9_SetRenderState(dev, (D3DRENDERSTATETYPE)s, v), "SRS"); }
static void SSS(DWORD t, DWORD v) { chk(IDirect3DDevice9_SetSamplerState(dev, 0, (D3DSAMPLERSTATETYPE)t, v), "SSS"); }

static void create_targets(D3DSURFACE_DESC *d) {
    RTW = d->Width; RTW2 = (RTW + 1) >> 1; RTH = d->Height; RTH2 = (RTH + 1) >> 1;
    chk(IDirect3DDevice9_CreateRenderTarget(dev, RTW, RTH, D3DFMT_A8R8G8B8, d->MultiSampleType, d->MultiSampleQuality, FALSE, &MSRT, NULL), "MSRT");
    chk(IDirect3DDevice9_CreateTexture(dev, RTW, RTH, 1, D3DUSAGE_RENDERTARGET, D3DFMT_A8R8G8B8, D3DPOOL_DEFAULT, &TEX0, NULL), "TEX0");
    IDirect3DTexture9_GetSurfaceLevel(TEX0, 0, &TEX0S);
    chk(IDirect3DDevice9_CreateTexture(dev, RTW2, RTH2, 1, D3DUSAGE_RENDERTARGET, D3DFMT_A8R8G8B8, D3DPOOL_DEFAULT, &TEX1, NULL), "TEX1");
    IDirect3DTexture9_GetSurfaceLevel(TEX1, 0, &TEX1S);
    chk(IDirect3DDevice9_CreateTexture(dev, RTW2, RTH2, 1, D3DUSAGE_RENDERTARGET, D3DFMT_A8R8G8B8, D3DPOOL_DEFAULT, &TEX2, NULL), "TEX2");
    IDirect3DTexture9_GetSurfaceLevel(TEX2, 0, &TEX2S);
    chk(IDirect3DDevice9_CreateTexture(dev, RTW, RTH, 1, D3DUSAGE_RENDERTARGET, D3DFMT_A8R8G8B8, D3DPOOL_DEFAULT, &TEX3, NULL), "TEX3");
    IDirect3DTexture9_GetSurfaceLevel(TEX3, 0, &TEX3S);
}
static void glow(void) {
    int c; D3DSURFACE_DESC d;
    IDirect3DDevice9_GetRenderTarget(dev, 0, &BBP); IDirect3DSurface9_GetDesc(BBP, &d);
    if (!MSRT) create_targets(&d);
    IDirect3DDevice9_GetDepthStencilSurface(dev, &DSP);
    SRS(D3DRS_SCISSORTESTENABLE, 0);
    chk(IDirect3DDevice9_SetRenderTarget(dev, 0, MSRT), "SetRT MSRT");
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_TARGET, 0, 1.0f, 0), "Clear MSRT");
    for (c = nunits; c >= 1; c--) { SRS(D3DRS_STENCILMASK, 0xFF); quad(c, RINGCOL | 0xFF000000); }
    chk(IDirect3DDevice9_StretchRect(dev, MSRT, NULL, TEX0S, NULL, D3DTEXF_NONE), "StretchRect");
    IDirect3DDevice9_SetDepthStencilSurface(dev, NULL); SRS(D3DRS_ZENABLE, 0); SRS(D3DRS_STENCILENABLE, 0);
    chk(IDirect3DDevice9_SetPixelShader(dev, isnew ? LPS : TPS), "SetPS first");
    IDirect3DDevice9_SetFVF(dev, 0x504);
    SSS(D3DSAMP_MAGFILTER, D3DTEXF_LINEAR); SSS(D3DSAMP_MINFILTER, D3DTEXF_LINEAR); SSS(D3DSAMP_MIPFILTER, D3DTEXF_NONE);
    SSS(D3DSAMP_ADDRESSU, D3DTADDRESS_CLAMP); SSS(D3DSAMP_ADDRESSV, D3DTADDRESS_CLAMP);
    for (c = 0; c < 5; c++) { IDirect3DDevice9_SetTextureStageState(dev, c, D3DTSS_TEXCOORDINDEX, c); IDirect3DDevice9_SetTextureStageState(dev, c, D3DTSS_TEXTURETRANSFORMFLAGS, 0); }
    QX0 = -0.5f; QY0 = -0.5f; QU0 = 0; QV0 = 0; QU1 = 1.0f; QV1 = 1.0f;
    if (isnew) {      /* line pass: full res, taps +-0.5 texel (TL = 0.5 / O1) */
        QX1 = (float)RTW - HALF; QY1 = (float)RTH - HALF;
        QDU = (float)((double)TL / RTW); QDV = (float)((double)TL / RTH);
        g_pass(TEX0, TEX3S);
        chk(IDirect3DDevice9_SetPixelShader(dev, TPS), "SetPS tent");
    }
    QX1 = (float)RTW2 - HALF; QY1 = (float)RTH2 - HALF;
    QDU = (float)((double)TQ / RTW); QDV = (float)((double)TQ / RTH);
    g_pass(isnew ? TEX3 : TEX0, TEX1S);
    chk(IDirect3DDevice9_SetPixelShader(dev, GPS), "SetPS blur"); QDV = 0;
    QDU = (float)(1.0 / RTW2);
    g_pass(TEX1, TEX2S);
    QDU = 0; QDV = (float)(1.0 / RTH2);
    chk(IDirect3DDevice9_SetPixelShader(dev, isnew ? VPSN : VPSO), "SetPS vblur+curve");
    g_pass(TEX2, TEX1S);
    IDirect3DDevice9_SetRenderTarget(dev, 0, BBP); IDirect3DDevice9_SetDepthStencilSurface(dev, DSP);
    IDirect3DDevice9_SetViewport(dev, &VP); SRS(D3DRS_ZENABLE, 1); SRS(D3DRS_STENCILENABLE, 1);
    SRS(D3DRS_STENCILFUNC, D3DCMP_GREATER); SRS(D3DRS_STENCILREF, 0x80); SRS(D3DRS_STENCILMASK, 0xFF); SRS(D3DRS_ALPHABLENDENABLE, 1);
    SRS(D3DRS_SRCBLEND, D3DBLEND_ONE); SRS(D3DRS_DESTBLEND, D3DBLEND_INVSRCALPHA); SRS(D3DRS_COLORWRITEENABLE, 7);
    IDirect3DDevice9_SetPixelShader(dev, CPS); IDirect3DDevice9_SetTexture(dev, 0, (IDirect3DBaseTexture9 *)TEX1);
    QX0 = (float)VP.X - HALF; QX1 = (float)(VP.X + VP.Width) - HALF; QY0 = (float)VP.Y - HALF; QY1 = (float)(VP.Y + VP.Height) - HALF;
    QU0 = (float)VP.X / (float)RTW; QU1 = (float)(VP.X + VP.Width) / (float)RTW; QV0 = (float)VP.Y / (float)RTH; QV1 = (float)(VP.Y + VP.Height) / (float)RTH;
    QDU = 0; QDV = 0;
    mkq(); chk(IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLESTRIP, 2, VERTT, 56), "DPUP composite");
    if (isnew) {
        IDirect3DDevice9_SetPixelShader(dev, LCPS); IDirect3DDevice9_SetTexture(dev, 0, (IDirect3DBaseTexture9 *)TEX3);
        chk(IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLESTRIP, 2, VERTT, 56), "DPUP line composite");
    }
    IDirect3DDevice9_SetTexture(dev, 0, NULL); SRS(D3DRS_ALPHABLENDENABLE, 0); SRS(D3DRS_STENCILFUNC, D3DCMP_EQUAL); SRS(D3DRS_COLORWRITEENABLE, 0xF);
    IDirect3DDevice9_SetPixelShader(dev, PS); IDirect3DDevice9_SetFVF(dev, 0x44);
    IDirect3DSurface9_Release(DSP); IDirect3DSurface9_Release(BBP);
}
static DWORD light(DWORD c) { DWORD a = (c >> 2) & 0x3F3F3F, b = (c >> 3) & 0x1F1F1F; return (c & 0xFFFFFF) - a - b + 0xFF5E5E5E; }
static void draw_fig(float dx, float dy) {
    static V44 *t; static int cap; int i;
    if (cap < 3 * ntri) { cap = 3 * ntri; t = realloc(t, sizeof(V44) * cap); }
    for (i = 0; i < 3 * ntri; i++) { t[i] = tri[i]; t[i].x += dx; t[i].y += dy; }
    chk(IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLELIST, ntri, t, sizeof(V44)), "DPUP fig");
}
static void scene(void) {
    int i;
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER | D3DCLEAR_STENCIL, 0xFF000000, 1.0f, 0), "Clear");
    IDirect3DDevice9_SetVertexShader(dev, NULL); IDirect3DDevice9_SetPixelShader(dev, NULL); IDirect3DDevice9_SetFVF(dev, D3DFVF_XYZRHW | D3DFVF_DIFFUSE);
    IDirect3DDevice9_SetTextureStageState(dev, 0, D3DTSS_COLOROP, D3DTOP_SELECTARG1); IDirect3DDevice9_SetTextureStageState(dev, 0, D3DTSS_COLORARG1, D3DTA_DIFFUSE);
    IDirect3DDevice9_SetTextureStageState(dev, 0, D3DTSS_ALPHAOP, D3DTOP_SELECTARG1); IDirect3DDevice9_SetTextureStageState(dev, 0, D3DTSS_ALPHAARG1, D3DTA_DIFFUSE);
    SRS(D3DRS_CULLMODE, D3DCULL_NONE); SRS(D3DRS_ZENABLE, D3DZB_FALSE); SRS(D3DRS_ALPHABLENDENABLE, FALSE); SRS(D3DRS_LIGHTING, FALSE);
    SRS(D3DRS_STENCILENABLE, TRUE); SRS(D3DRS_STENCILFUNC, D3DCMP_ALWAYS); SRS(D3DRS_STENCILREF, FIG);
    SRS(D3DRS_STENCILPASS, D3DSTENCILOP_REPLACE); SRS(D3DRS_STENCILFAIL, D3DSTENCILOP_KEEP); SRS(D3DRS_STENCILZFAIL, D3DSTENCILOP_KEEP);
    SRS(D3DRS_STENCILMASK, 0xFF); SRS(D3DRS_STENCILWRITEMASK, 0xFF); SRS(D3DRS_COLORWRITEENABLE, 0xF);
    draw_fig(0, 0);
    SRS(D3DRS_STENCILFUNC, D3DCMP_GREATER); SRS(D3DRS_STENCILREF, 1); SRS(D3DRS_COLORWRITEENABLE, 0);
    for (i = 0; i < NOFFS; i++) draw_fig(OFFS[i][0], OFFS[i][1]);
    SRS(D3DRS_COLORWRITEENABLE, 0xF);
}
static void post(void) {
    int c;
    SRS(52, 1); SRS(56, 3); SRS(55, 1); SRS(53, 1); SRS(54, 1); SRS(58, 0xFF); SRS(23, 8); SRS(14, 0); SRS(27, 0); SRS(15, 0);
    SRS(22, 1); SRS(168, 0xF); SRS(28, 0);
    IDirect3DDevice9_SetVertexShader(dev, NULL); IDirect3DDevice9_SetPixelShader(dev, PS); IDirect3DDevice9_SetFVF(dev, 0x44);
    VERTS[0].x = VERTS[2].x = (float)VP.X - HALF; VERTS[1].x = VERTS[3].x = (float)(VP.X + VP.Width) - HALF;
    VERTS[0].y = VERTS[1].y = (float)VP.Y - HALF; VERTS[2].y = VERTS[3].y = (float)(VP.Y + VP.Height) - HALF;
    { int k; for (k = 0; k < 4; k++) { VERTS[k].z = 0.0f; VERTS[k].rhw = 1.0f; } }
    glow();
    if (!isnew) for (c = nunits; c >= 1; c--) quad(c, light(RINGCOL));       /* new: line comes from TEX3, no quads */
    IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_STENCIL, 0, 1.0f, 0); SRS(52, 0);
}
static void readback(IDirect3DSurface9 *src, FILE *f) {
    D3DSURFACE_DESC d; IDirect3DSurface9 *rs = NULL, *sys = NULL, *from = src; D3DLOCKED_RECT lr; UINT y;
    IDirect3DSurface9_GetDesc(src, &d);
    if (d.MultiSampleType != D3DMULTISAMPLE_NONE) {
        chk(IDirect3DDevice9_CreateRenderTarget(dev, d.Width, d.Height, d.Format, D3DMULTISAMPLE_NONE, 0, FALSE, &rs, NULL), "resolveRT");
        chk(IDirect3DDevice9_StretchRect(dev, src, NULL, rs, NULL, D3DTEXF_NONE), "resolve"); from = rs;
    }
    chk(IDirect3DDevice9_CreateOffscreenPlainSurface(dev, d.Width, d.Height, d.Format, D3DPOOL_SYSTEMMEM, &sys, NULL), "sysmem");
    chk(IDirect3DDevice9_GetRenderTargetData(dev, from, sys), "GetRenderTargetData");
    if (SUCCEEDED(IDirect3DSurface9_LockRect(sys, &lr, NULL, D3DLOCK_READONLY))) {
        for (y = 0; y < d.Height; y++) fwrite((const unsigned char *)lr.pBits + y * lr.Pitch, 4, d.Width, f);
        IDirect3DSurface9_UnlockRect(sys);
    }
    IDirect3DSurface9_Release(sys); if (rs) IDirect3DSurface9_Release(rs);
}
static LRESULT CALLBACK wndproc(HWND h, UINT m, WPARAM w, LPARAM l) { return DefWindowProcA(h, m, w, l); }

int main(int argc, char **argv) {
    D3DMULTISAMPLE_TYPE ms = (D3DMULTISAMPLE_TYPE)atoi(argv[1]); const char *var = argv[2], *outdir = argv[3];
    UINT W = argc > 5 ? atoi(argv[4]) : 170, H = argc > 5 ? atoi(argv[5]) : 120; int bench = argc > 6 ? atoi(argv[6]) : 0;
    IDirect3D9 *d3d; D3DPRESENT_PARAMETERS pp; WNDCLASSA wc; RECT r = { 0, 0, 0, 0 }; HWND hwnd; HRESULT hr;
    FILE *fin, *fbb = NULL; int nframes, fr; char fn[512]; float *buf;
    if (argc > 7) nunits = atoi(argv[7]);
    isnew = strcmp(var, "old") != 0;
    OFFS = !strcmp(var, "old") ? OFF_OLD : !strcmp(var, "nsq") ? OFF_NSQ : !strcmp(var, "nsqd") ? OFF_NSQD : OFF_NEW;
    TQ = (float)(0.75 / 1.3846154); TL = (float)(0.5 / 1.3846154);
    setvbuf(stdout, NULL, _IONBF, 0);
    fin = fopen("frames.bin", "rb"); if (!fin) { printf("no frames.bin\n"); return 1; }
    fread(&nframes, 4, 1, fin);
    memset(&wc, 0, sizeof wc); wc.lpfnWndProc = wndproc; wc.hInstance = GetModuleHandleA(NULL); wc.lpszClassName = "tips"; RegisterClassA(&wc);
    r.right = W; r.bottom = H; AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW, FALSE);
    hwnd = CreateWindowA("tips", "tips", WS_OVERLAPPEDWINDOW | WS_VISIBLE, 0, 0, r.right - r.left, r.bottom - r.top, NULL, NULL, wc.hInstance, NULL);
    d3d = Direct3DCreate9(D3D_SDK_VERSION);
    memset(&pp, 0, sizeof pp);
    pp.BackBufferWidth = W; pp.BackBufferHeight = H; pp.BackBufferFormat = D3DFMT_X8R8G8B8; pp.BackBufferCount = 1;
    pp.MultiSampleType = ms; pp.SwapEffect = D3DSWAPEFFECT_DISCARD; pp.hDeviceWindow = hwnd; pp.Windowed = TRUE;
    pp.EnableAutoDepthStencil = TRUE; pp.AutoDepthStencilFormat = D3DFMT_D24S8; pp.PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE;
    hr = IDirect3D9_CreateDevice(d3d, 0, D3DDEVTYPE_HAL, hwnd, D3DCREATE_HARDWARE_VERTEXPROCESSING, &pp, &dev);
    if (FAILED(hr)) { printf("CreateDevice failed 0x%08lX\n", hr); return 1; }
    IDirect3DDevice9_GetViewport(dev, &VP);
    chk(IDirect3DDevice9_CreatePixelShader(dev, GPSCODE, &GPS), "GPS"); chk(IDirect3DDevice9_CreatePixelShader(dev, CPSCODE, &CPS), "CPS");
    chk(IDirect3DDevice9_CreatePixelShader(dev, RINGPSCODE, &PS), "PS"); chk(IDirect3DDevice9_CreatePixelShader(dev, TPSCODE, &TPS), "TPS");
    chk(IDirect3DDevice9_CreatePixelShader(dev, VPSOLD, &VPSO), "VPSO"); chk(IDirect3DDevice9_CreatePixelShader(dev, VPSNEW, &VPSN), "VPSN");
    chk(IDirect3DDevice9_CreatePixelShader(dev, LPSCODE, &LPS), "LPS"); chk(IDirect3DDevice9_CreatePixelShader(dev, LCPSCODE, &LCPS), "LCPS");
    printf("tips_test ms=%d variant=%s %ux%u frames=%d bench=%d nunits=%d\n", ms, var, W, H, nframes, bench, nunits);
    snprintf(fn, sizeof fn, "%s/bb.raw", outdir); if (!bench) fbb = fopen(fn, "wb");
    buf = malloc(4 * 6 * 8192);
    for (fr = 0; fr < nframes; fr++) {
        int i, n; MSG m;
        fread(&n, 4, 1, fin); fread(buf, 4, 6 * n, fin);
        ntri = n; tri = realloc(tri, sizeof(V44) * 3 * n);
        for (i = 0; i < 3 * n; i++) { V44 v = { buf[2 * i], buf[2 * i + 1], 0.5f, 1.0f, FIGCOL }; tri[i] = v; }
        while (PeekMessageA(&m, NULL, 0, 0, PM_REMOVE)) { TranslateMessage(&m); DispatchMessageA(&m); }
        IDirect3DDevice9_BeginScene(dev); scene(); post(); IDirect3DDevice9_EndScene(dev);
        if (bench) {          /* time post alone (with and without) on frame 0 */
            IDirect3DQuery9 *q = NULL; LARGE_INTEGER f0, t0, t1; int it, k, pass; double tm[2];
            IDirect3DDevice9_CreateQuery(dev, D3DQUERYTYPE_EVENT, &q);
            for (pass = 0; pass < 2; pass++) {
                for (it = 0; it < 2; it++) {
                    int iters = it ? bench : 5;
                    QueryPerformanceFrequency(&f0); QueryPerformanceCounter(&t0);
                    for (k = 0; k < iters; k++) { IDirect3DDevice9_BeginScene(dev); scene(); if (pass) post(); IDirect3DDevice9_EndScene(dev); }
                    IDirect3DQuery9_Issue(q, D3DISSUE_END);
                    while (IDirect3DQuery9_GetData(q, NULL, 0, D3DGETDATA_FLUSH) == S_FALSE) ;
                    QueryPerformanceCounter(&t1);
                    if (it) tm[pass] = 1000.0 * (t1.QuadPart - t0.QuadPart) / f0.QuadPart / iters;
                }
            }
            printf("BENCH %s ms=%d %ux%u units=%d: scene %.3f ms, scene+post %.3f ms, post %.3f ms\n", var, ms, W, H, nunits, tm[0], tm[1], tm[1] - tm[0]);
            IDirect3DQuery9_Release(q);
            break;
        }
        { IDirect3DSurface9 *bb = NULL; IDirect3DDevice9_GetBackBuffer(dev, 0, 0, D3DBACKBUFFER_TYPE_MONO, &bb); readback(bb, fbb); IDirect3DSurface9_Release(bb); }
        IDirect3DDevice9_Present(dev, NULL, NULL, NULL, NULL);
    }
    if (fbb) fclose(fbb);
    printf("SUMMARY failed %d\n", nfail);
    return nfail ? 2 : 0;
}
