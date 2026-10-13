/* shimmer_test.c - temporal stability of the outline10 soft glow on real D3D9 (Wine/wined3d).
 * Derived from agent_d3d9/glowtest.c (same glow call sequence: post/glow/g_pass/mkq/quad), but the figure comes
 * from frames.bin (gen_frames.py: polygon figure moved by sub-pixels / 1 px / rotated / scaled), and two variants:
 *   old  : current outline10 (downsample = blur shader with all 5 taps at the 2x2 block corner)
 *   tent : proposed fix (downsample = tent_ps: 4 bilinear taps at (+-0.75,+-0.75) full-res texels;
 *          t1/t2 = (u,v) +- (QDU,QDV)*O1 with QDU = TQ/RTW, QDV = TQ/RTH, TQ = 0.75/O1, exactly as the asm computes it)
 * Colours chosen for exact read-back: background black, figure red, ring/glow green (glow alpha = G/255 where
 * R = B = 0), thin line light(green) = (0x5E,0xFF,0x5E) so B/94 = ring coverage.
 * usage: shimmer_test.exe ms variant outdir [W H] [bench_iters]
 *   writes outdir/bb.raw (all frames, W*H*4 BGRA), outdir/tex0a.raw (TEX0 alpha, W*H per frame), outdir/tex1_f0.raw */
#define COBJMACROS
#include <windows.h>
#include <d3d9.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "shaders.h"      /* GPSCODE, CPSCODE, RINGPSCODE (agent_d3d9, from ol2/psasm.py) */
#include "tent_ps.h"      /* TPSCODE (psasm_tent.py) */

#define FIGCOL 0xFFFF0000
#define RINGCOL 0xFF00FF00
#define FIG 0x80
static IDirect3DDevice9 *dev;
static IDirect3DPixelShader9 *PS, *GPS, *CPS, *TPS, *VPS, *CPS1;
static IDirect3DSurface9 *MSRT, *TEX0S, *TEX1S, *TEX2S, *BBP, *DSP;
static IDirect3DTexture9 *TEX0, *TEX1, *TEX2;
static UINT RTW, RTH, RTW2, RTH2;
static D3DVIEWPORT9 VP;
typedef struct { float x, y, z, rhw; DWORD c; } V44;
static V44 VERTS[4];
static float VERTT[4][14];
static float QX0, QY0, QX1, QY1, QU0, QV0, QU1, QV1, QDU, QDV;
static const float O1 = 1.3846154f, O2 = 3.2307692f, HALF = 0.5f;
static float TQ;                                   /* 0.75 / O1, data constant of the fix */
static int tent, softv, noglow, nfail;
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
}
static int glow(void) {
    int c; D3DSURFACE_DESC d;
    IDirect3DDevice9_GetRenderTarget(dev, 0, &BBP); IDirect3DSurface9_GetDesc(BBP, &d);
    if (!MSRT) create_targets(&d);
    IDirect3DDevice9_GetDepthStencilSurface(dev, &DSP);
    SRS(D3DRS_SCISSORTESTENABLE, 0);
    chk(IDirect3DDevice9_SetRenderTarget(dev, 0, MSRT), "SetRT MSRT");
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_TARGET, 0, 1.0f, 0), "Clear MSRT");
    quad(1, RINGCOL | 0xFF000000);
    chk(IDirect3DDevice9_StretchRect(dev, MSRT, NULL, TEX0S, NULL, D3DTEXF_NONE), "StretchRect");
    IDirect3DDevice9_SetDepthStencilSurface(dev, NULL); SRS(D3DRS_ZENABLE, 0); SRS(D3DRS_STENCILENABLE, 0);
    chk(IDirect3DDevice9_SetPixelShader(dev, tent ? TPS : GPS), "SetPS down");      /* fix: TPS for the downsample */
    IDirect3DDevice9_SetFVF(dev, 0x504);
    SSS(D3DSAMP_MAGFILTER, D3DTEXF_LINEAR); SSS(D3DSAMP_MINFILTER, D3DTEXF_LINEAR); SSS(D3DSAMP_MIPFILTER, D3DTEXF_NONE);
    SSS(D3DSAMP_ADDRESSU, D3DTADDRESS_CLAMP); SSS(D3DSAMP_ADDRESSV, D3DTADDRESS_CLAMP);
    for (c = 0; c < 5; c++) { IDirect3DDevice9_SetTextureStageState(dev, c, D3DTSS_TEXCOORDINDEX, c); IDirect3DDevice9_SetTextureStageState(dev, c, D3DTSS_TEXTURETRANSFORMFLAGS, 0); }
    QX1 = (float)RTW2 - HALF; QY1 = (float)RTH2 - HALF; QX0 = -0.5f; QY0 = -0.5f;
    QU0 = 0; QV0 = 0; QU1 = 1.0f; QV1 = 1.0f;
    if (tent) { QDU = (float)((double)TQ / RTW); QDV = (float)((double)TQ / RTH); }   /* fld TQ / fidiv RTW / fstp QDU */
    else { QDU = 0; QDV = 0; }
    g_pass(TEX0, TEX1S);
    if (tent) { chk(IDirect3DDevice9_SetPixelShader(dev, GPS), "SetPS blur"); QDV = 0; }
    QDU = (float)(1.0 / RTW2);
    g_pass(TEX1, TEX2S);
    QDU = 0; QDV = (float)(1.0 / RTH2);
    if (softv) chk(IDirect3DDevice9_SetPixelShader(dev, VPS), "SetPS vblur+curve");        /* fix: curve in the V pass */
    g_pass(TEX2, TEX1S);
    IDirect3DDevice9_SetRenderTarget(dev, 0, BBP); IDirect3DDevice9_SetDepthStencilSurface(dev, DSP);
    IDirect3DDevice9_SetViewport(dev, &VP); SRS(D3DRS_ZENABLE, 1); SRS(D3DRS_STENCILENABLE, 1);
    SRS(D3DRS_STENCILFUNC, D3DCMP_GREATER); SRS(D3DRS_STENCILREF, 0x80); SRS(D3DRS_STENCILMASK, 0xFF); SRS(D3DRS_ALPHABLENDENABLE, 1);
    SRS(D3DRS_SRCBLEND, D3DBLEND_ONE); SRS(D3DRS_DESTBLEND, D3DBLEND_INVSRCALPHA); SRS(D3DRS_COLORWRITEENABLE, 7);
    IDirect3DDevice9_SetPixelShader(dev, softv ? CPS1 : CPS); IDirect3DDevice9_SetTexture(dev, 0, (IDirect3DBaseTexture9 *)TEX1);
    QX0 = (float)VP.X - HALF; QX1 = (float)(VP.X + VP.Width) - HALF; QY0 = (float)VP.Y - HALF; QY1 = (float)(VP.Y + VP.Height) - HALF;
    QU0 = (float)VP.X / (float)RTW; QU1 = (float)(VP.X + VP.Width) / (float)RTW; QV0 = (float)VP.Y / (float)RTH; QV1 = (float)(VP.Y + VP.Height) / (float)RTH;
    QDU = 0; QDV = 0;
    mkq(); chk(IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLESTRIP, 2, VERTT, 56), "DPUP composite");
    IDirect3DDevice9_SetTexture(dev, 0, NULL); SRS(D3DRS_ALPHABLENDENABLE, 0); SRS(D3DRS_STENCILFUNC, D3DCMP_EQUAL); SRS(D3DRS_COLORWRITEENABLE, 0xF);
    IDirect3DDevice9_SetPixelShader(dev, PS); IDirect3DDevice9_SetFVF(dev, 0x44);
    IDirect3DSurface9_Release(DSP); IDirect3DSurface9_Release(BBP);
    return 1;
}
static DWORD light(DWORD c) { DWORD a = (c >> 2) & 0x3F3F3F, b = (c >> 3) & 0x1F1F1F; return (c & 0xFFFFFF) - a - b + 0xFF5E5E5E; }
static void draw_fig(float dx, float dy) {
    static V44 *t; static int cap; int i;
    if (cap < 3 * ntri) { cap = 3 * ntri; t = realloc(t, sizeof(V44) * cap); }
    for (i = 0; i < 3 * ntri; i++) { t[i] = tri[i]; t[i].x += dx; t[i].y += dy; }
    chk(IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLELIST, ntri, t, sizeof(V44)), "DPUP fig");
}
static const float OFFS[8][2] = { {2, 0}, {-2, 0}, {0, 2}, {0, -2}, {2, 2}, {2, -2}, {-2, 2}, {-2, -2} };
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
    for (i = 0; i < 8; i++) draw_fig(OFFS[i][0], OFFS[i][1]);
    SRS(D3DRS_COLORWRITEENABLE, 0xF);
}
static void post(void) {
    SRS(52, 1); SRS(56, 3); SRS(55, 1); SRS(53, 1); SRS(54, 1); SRS(58, 0xFF); SRS(23, 8); SRS(14, 0); SRS(27, 0); SRS(15, 0);
    SRS(22, 1); SRS(168, 0xF); SRS(28, 0);
    IDirect3DDevice9_SetVertexShader(dev, NULL); IDirect3DDevice9_SetPixelShader(dev, PS); IDirect3DDevice9_SetFVF(dev, 0x44);
    VERTS[0].x = VERTS[2].x = (float)VP.X - HALF; VERTS[1].x = VERTS[3].x = (float)(VP.X + VP.Width) - HALF;
    VERTS[0].y = VERTS[1].y = (float)VP.Y - HALF; VERTS[2].y = VERTS[3].y = (float)(VP.Y + VP.Height) - HALF;
    { int k; for (k = 0; k < 4; k++) { VERTS[k].z = 0.0f; VERTS[k].rhw = 1.0f; } }
    if (!noglow) glow();
    quad(1, noglow ? RINGCOL : light(RINGCOL));
    IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_STENCIL, 0, 1.0f, 0); SRS(52, 0);
}
static void readback(IDirect3DSurface9 *src, FILE *f, int alpha_only) {
    D3DSURFACE_DESC d; IDirect3DSurface9 *rs = NULL, *sys = NULL, *from = src; D3DLOCKED_RECT lr; UINT y, x;
    IDirect3DSurface9_GetDesc(src, &d);
    if (d.MultiSampleType != D3DMULTISAMPLE_NONE) {
        chk(IDirect3DDevice9_CreateRenderTarget(dev, d.Width, d.Height, d.Format, D3DMULTISAMPLE_NONE, 0, FALSE, &rs, NULL), "resolveRT");
        chk(IDirect3DDevice9_StretchRect(dev, src, NULL, rs, NULL, D3DTEXF_NONE), "resolve"); from = rs;
    }
    chk(IDirect3DDevice9_CreateOffscreenPlainSurface(dev, d.Width, d.Height, d.Format, D3DPOOL_SYSTEMMEM, &sys, NULL), "sysmem");
    chk(IDirect3DDevice9_GetRenderTargetData(dev, from, sys), "GetRenderTargetData");
    if (SUCCEEDED(IDirect3DSurface9_LockRect(sys, &lr, NULL, D3DLOCK_READONLY))) {
        for (y = 0; y < d.Height; y++) {
            const unsigned char *row = (const unsigned char *)lr.pBits + y * lr.Pitch;
            if (alpha_only) for (x = 0; x < d.Width; x++) fputc(row[4 * x + 3], f);
            else fwrite(row, 4, d.Width, f);
        }
        IDirect3DSurface9_UnlockRect(sys);
    }
    IDirect3DSurface9_Release(sys); if (rs) IDirect3DSurface9_Release(rs);
}
static LRESULT CALLBACK wndproc(HWND h, UINT m, WPARAM w, LPARAM l) { return DefWindowProcA(h, m, w, l); }

int main(int argc, char **argv) {
    D3DMULTISAMPLE_TYPE ms = (D3DMULTISAMPLE_TYPE)atoi(argv[1]); const char *outdir = argv[3];
    UINT W = argc > 5 ? atoi(argv[4]) : 400, H = argc > 5 ? atoi(argv[5]) : 340; int bench = argc > 6 ? atoi(argv[6]) : 0;
    IDirect3D9 *d3d; D3DPRESENT_PARAMETERS pp; WNDCLASSA wc; RECT r = { 0, 0, 0, 0 }; HWND hwnd; HRESULT hr;
    FILE *fin, *fbb, *fa; int nframes, fr; char fn[512]; float *buf;
    softv = !strcmp(argv[2], "tsv"); tent = !strcmp(argv[2], "tent") || softv; noglow = !strcmp(argv[2], "none");
    TQ = (float)(0.75 / 1.3846154);
    setvbuf(stdout, NULL, _IONBF, 0);
    snprintf(fn, sizeof fn, "frames.bin"); fin = fopen(fn, "rb"); if (!fin) { printf("no frames.bin\n"); return 1; }
    fread(&nframes, 4, 1, fin);
    memset(&wc, 0, sizeof wc); wc.lpfnWndProc = wndproc; wc.hInstance = GetModuleHandleA(NULL); wc.lpszClassName = "shimmer"; RegisterClassA(&wc);
    r.right = W; r.bottom = H; AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW, FALSE);
    hwnd = CreateWindowA("shimmer", "shimmer", WS_OVERLAPPEDWINDOW | WS_VISIBLE, 0, 0, r.right - r.left, r.bottom - r.top, NULL, NULL, wc.hInstance, NULL);
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
    chk(IDirect3DDevice9_CreatePixelShader(dev, VPSCODE, &VPS), "VPS"); chk(IDirect3DDevice9_CreatePixelShader(dev, CPS1CODE, &CPS1), "CPS1");
    printf("shimmer_test ms=%d variant=%s %ux%u frames=%d bench=%d\n", ms, argv[2], W, H, nframes, bench);
    snprintf(fn, sizeof fn, "%s/bb.raw", outdir); fbb = bench ? NULL : fopen(fn, "wb");
    snprintf(fn, sizeof fn, "%s/tex0a.raw", outdir); fa = bench ? NULL : fopen(fn, "wb");
    buf = malloc(4 * 6 * 4096);
    for (fr = 0; fr < nframes; fr++) {
        int i, n; MSG m;
        fread(&n, 4, 1, fin); fread(buf, 4, 6 * n, fin);
        ntri = n; tri = realloc(tri, sizeof(V44) * 3 * n);
        for (i = 0; i < 3 * n; i++) { V44 v = { buf[2 * i], buf[2 * i + 1], 0.5f, 1.0f, FIGCOL }; tri[i] = v; }
        while (PeekMessageA(&m, NULL, 0, 0, PM_REMOVE)) { TranslateMessage(&m); DispatchMessageA(&m); }
        if (bench && fr > 0) break;
        IDirect3DDevice9_BeginScene(dev);
        scene(); post();
        IDirect3DDevice9_EndScene(dev);
        if (bench) {          /* time the glow alone (ring quad, resolve, 3 passes, composite) */
            IDirect3DQuery9 *q = NULL; LARGE_INTEGER f0, t0, t1; int it;
            IDirect3DDevice9_CreateQuery(dev, D3DQUERYTYPE_EVENT, &q);
            for (it = 0; it < 2; it++) {
                int k, iters = it ? bench : 10;
                QueryPerformanceFrequency(&f0); QueryPerformanceCounter(&t0);
                for (k = 0; k < iters; k++) {
                    IDirect3DDevice9_BeginScene(dev); scene(); post(); IDirect3DDevice9_EndScene(dev);
                }
                IDirect3DQuery9_Issue(q, D3DISSUE_END);
                while (IDirect3DQuery9_GetData(q, NULL, 0, D3DGETDATA_FLUSH) == S_FALSE) ;
                QueryPerformanceCounter(&t1);
                if (it) printf("BENCH %s ms=%d %ux%u: %.3f ms per frame (scene + glow)\n", softv ? "tsv" : tent ? "tent" : noglow ? "none" : "old", ms, W, H,
                               1000.0 * (t1.QuadPart - t0.QuadPart) / f0.QuadPart / iters);
            }
            IDirect3DQuery9_Release(q);
            break;
        }
        {
            IDirect3DSurface9 *bb = NULL;
            IDirect3DDevice9_GetBackBuffer(dev, 0, 0, D3DBACKBUFFER_TYPE_MONO, &bb);
            readback(bb, fbb, 0); IDirect3DSurface9_Release(bb);
            readback(TEX0S, fa, 1);
            if (fr == 0) { snprintf(fn, sizeof fn, "%s/tex1_f0.raw", outdir); FILE *f1 = fopen(fn, "wb"); readback(TEX1S, f1, 0); fclose(f1); }
        }
        IDirect3DDevice9_Present(dev, NULL, NULL, NULL, NULL);
    }
    if (fbb) fclose(fbb); if (fa) fclose(fa);
    printf("SUMMARY failed %d\n", nfail);
    return nfail ? 2 : 0;
}
