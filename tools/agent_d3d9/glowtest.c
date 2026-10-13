/* glowtest.c - replays the outline10 "soft glow" D3D9 call sequence (ol2/outline10.py, routines
 * post/glow/g_pass/mkq/quad/glfree) against a real D3D9 implementation (Wine/wined3d here).
 * Every call is logged as an EXP-style tuple ("T (...) => hr") so the log can be compared with
 * EXP in ol2/test_outline10.py section 20.  v2 sequence: COLORWRITEENABLE 7 for the composite, 0xF in the
 * tail, TEXTURETRANSFORMFLAGS 0-4 restored from the (emulated) WoW state cache, GLFAIL if a pass SetRenderTarget fails.
 * usage: glowtest.exe [mstype] [msquality] [width] [height] [outprefix] [vpX vpY vpW vpH]
 * env:   GLOW_A8RT=1  scene is rendered into an A8R8G8B8 render target (RT0 during post/glow), cleared to alpha 0x40
 *        GLOW_V1=1    v1 sequence (no COLORWRITE 7/0xF, no TTFF restore, no pass GLFAIL check) - for contrast only
 *        GLOW_TTFF_NORESET=1  sensitivity control: glow does NOT set TTFF 0 for its passes (deliberately broken)
 */
#define COBJMACROS
#include <windows.h>
#include <d3d9.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <math.h>
#include "scene.h"
#include "shaders.h"

#define NUNITS 2
static const DWORD UCOL[NUNITS + 1] = { 0, 0xFFFFD100, 0xFF0070DE };   /* cat 1 gold, cat 2 shaman blue */
#define FIGCOL 0xFF8C8C8C
#define BGCOL 0xFF384030
#define FIG 0x80

static IDirect3D9 *d3d;
static IDirect3DDevice9 *dev;
static int nfail, ncalls;
static char phase[32] = "init";
static char prefix[64] = "r";

/* game data area (outline10 DO[...]) */
static IDirect3DPixelShader9 *PS, *GPS, *CPS;
static IDirect3DDevice9 *PSDEV, *GPSDEV, *RTDEV, *GLFAIL;
static IDirect3DSurface9 *MSRT, *TEX0S, *TEX1S, *TEX2S, *BBP, *DSP;
static IDirect3DTexture9 *TEX0, *TEX1, *TEX2;
static UINT RTW, RTH, RTW2, RTH2;
static D3DMULTISAMPLE_TYPE RTMS;
static DWORD RTMQ;
static int GLOK;
static D3DVIEWPORT9 VP;
static DWORD RTWFULL, RTHFULL;
static D3DSURFACE_DESC DESC;
typedef struct { float x, y, z, rhw; DWORD c; } V44;
static V44 VERTS[4];
static float VERTT[4][14];
static float QX0, QY0, QX1, QY1, QU0, QV0, QU1, QV1, QDU, QDV;
static const float O1 = 1.3846154f, O2 = 3.2307692f, HALF = 0.5f;
static void *BBREF, *DSREF;     /* the device's backbuffer / auto depth-stencil (for names in the log) */
static int force_glfail;
static int use_subvp; static D3DVIEWPORT9 SUBVP;
/* v2 */
static DWORD TTSAV[5];                                                         /* DO['TTSAV'] */
static DWORD ttcache[5] = { 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF };  /* emulated WoW cache [DEV+0x3BC4+4*(0x52+i)] */
static const DWORD TTFF_WOW[5] = { D3DTTFF_COUNT2, D3DTTFF_COUNT3 | D3DTTFF_PROJECTED, 0, 0, 0 };   /* "WoW" state before the glow */
static int v1mode, a8rt_mode, ttff_noreset;
static IDirect3DSurface9 *A8RT;      /* variant: A8R8G8B8 scene render target (RT0 while post/glow run) */
static DWORD bgcol = BGCOL;
static D3DMULTISAMPLE_TYPE g_ms; static DWORD g_mq;

static const char *nm(const void *p) {
    static char buf[8][24]; static int k;
    if (!p) return "0";
    if (p == BBREF || (A8RT && p == A8RT)) return "'BB'";     /* the game's current RT0 */
    if (p == DSREF) return "'DS'";
    if (p == MSRT) return "'MSRT'";
    if (p == TEX0) return "'TEX0'";
    if (p == TEX0S) return "'TEX0S'";
    if (p == TEX1) return "'TEX1'";
    if (p == TEX1S) return "'TEX1S'";
    if (p == TEX2) return "'TEX2'";
    if (p == TEX2S) return "'TEX2S'";
    if (p == GPS) return "'GPS'";
    if (p == CPS) return "'CPS'";
    if (p == PS) return "'PS'";
    k = (k + 1) & 7; snprintf(buf[k], sizeof buf[k], "'%p'", p); return buf[k];
}
static const char *hrname(HRESULT hr) {
    switch ((unsigned long)hr) {
    case 0: return "D3D_OK";
    case 0x8876086CUL: return "D3DERR_INVALIDCALL";
    case 0x8876086AUL: return "D3DERR_NOTAVAILABLE";
    case 0x8876017CUL: return "D3DERR_OUTOFVIDEOMEMORY";
    case 0x8007000EUL: return "E_OUTOFMEMORY";
    case 0x88760868UL: return "D3DERR_DEVICELOST";
    case 0x88760869UL: return "D3DERR_DEVICENOTRESET";
    case 0x88760827UL: return "D3DERR_DRIVERINTERNALERROR";
    case 0x88760866UL: return "D3DERR_NOTFOUND";
    case 0x8876021CUL: return "D3DERR_WASSTILLDRAWING";
    case 0x80004005UL: return "E_FAIL";
    case 0x80004001UL: return "E_NOTIMPL";
    default: return "?";
    }
}
static HRESULT lg(HRESULT hr, const char *fmt, ...) {
    char buf[600]; va_list ap; va_start(ap, fmt); vsnprintf(buf, sizeof buf, fmt, ap); va_end(ap);
    ncalls++; if (FAILED(hr)) nfail++;
    printf("%-7s T (%s) => 0x%08lX %s%s\n", phase, buf, (unsigned long)hr, hrname(hr), FAILED(hr) ? "   <<<<< FAILED" : "");
    return hr;
}
static HRESULT expect(HRESULT hr, HRESULT want, const char *what) {
    ncalls++;
    printf("%-7s X (%s) => 0x%08lX %s   expected 0x%08lX %s -> %s\n", phase, what, (unsigned long)hr, hrname(hr),
           (unsigned long)want, hrname(want), hr == want ? "AS EXPECTED" : "<<<<< UNEXPECTED");
    if (hr != want) nfail++;
    return hr;
}
static ULONG Rel(void *p) {
    const char *n = nm(p);
    ULONG r = IUnknown_Release((IUnknown *)p);
    printf("%-7s T ('Release', %s) => refs %lu\n", phase, n, r);
    return r;
}
static float hf(DWORD x) { float f; memcpy(&f, &x, 4); return f; }
static DWORD fh(float f) { DWORD x; memcpy(&x, &f, 4); return x; }

/* --- logged D3D wrappers (names as in test_outline10.py) --- */
static HRESULT SRS(DWORD s, DWORD v) { return lg(IDirect3DDevice9_SetRenderState(dev, (D3DRENDERSTATETYPE)s, v), "'SRS', %lu, 0x%lX", s, v); }
static HRESULT SSS(DWORD st, DWORD t, DWORD v) { return lg(IDirect3DDevice9_SetSamplerState(dev, st, (D3DSAMPLERSTATETYPE)t, v), "'SSS', %lu, %lu, %lu", st, t, v); }
static HRESULT TSS(DWORD st, DWORD t, DWORD v) { return lg(IDirect3DDevice9_SetTextureStageState(dev, st, (D3DTEXTURESTAGESTATETYPE)t, v), "'TSS', %lu, %lu, %lu", st, t, v); }
static HRESULT SetPS(IDirect3DPixelShader9 *p) { return lg(IDirect3DDevice9_SetPixelShader(dev, p), "'SetPS', %s", nm(p)); }
static HRESULT SetVS0(void) { return lg(IDirect3DDevice9_SetVertexShader(dev, NULL), "'SetVS', 0"); }
static HRESULT SetFVF(DWORD f) { return lg(IDirect3DDevice9_SetFVF(dev, f), "'SetFVF', 0x%lX", f); }
static HRESULT SetTex(DWORD st, IDirect3DTexture9 *t) { return lg(IDirect3DDevice9_SetTexture(dev, st, (IDirect3DBaseTexture9 *)t), "'SetTex', %lu, %s", st, nm(t)); }
static HRESULT SetRT(DWORD i, IDirect3DSurface9 *s) { return lg(IDirect3DDevice9_SetRenderTarget(dev, i, s), "'SetRT', %lu, %s", i, nm(s)); }
static HRESULT SetDS(IDirect3DSurface9 *s) { return lg(IDirect3DDevice9_SetDepthStencilSurface(dev, s), "'SetDS', %s", nm(s)); }
static HRESULT SetVP(void) { return lg(IDirect3DDevice9_SetViewport(dev, &VP), "'SetVP', '&VP'"); }
static HRESULT Clear(DWORD flags, D3DCOLOR c, float z, DWORD s) { return lg(IDirect3DDevice9_Clear(dev, 0, NULL, flags, c, z, s), "'Clear', 0, 0, %lu, 0x%lX, 0x%08lX, %lu", flags, (unsigned long)c, fh(z), s); }
static HRESULT DPUP(D3DPRIMITIVETYPE t, UINT n, const void *v, UINT stride, const char *vn) { return lg(IDirect3DDevice9_DrawPrimitiveUP(dev, t, n, v, stride), "'DPUP', %d, %u, %s, %u", (int)t, n, vn, stride); }
static HRESULT CreatePS(const DWORD *code, IDirect3DPixelShader9 **pp, const char *cn, const char *pn) { return lg(IDirect3DDevice9_CreatePixelShader(dev, code, pp), "'CreatePS', '&%s', '&%s'", cn, pn); }

/* --- geometry --- */
static V44 *fig1v, *fig2v, *tmpv; static int fig1t, fig2t;
static const float OFFS[8][2] = { {2, 0}, {-2, 0}, {0, 2}, {0, -2}, {2, 2}, {2, -2}, {-2, 2}, {-2, -2} };
static void build_geometry(void) {
    int i, k = 0;
    fig1t = FIG1_NRECT * 2; fig1v = malloc(sizeof(V44) * 3 * fig1t);
    for (i = 0; i < FIG1_NRECT; i++) {
        float x0 = fig1_rects[i][0] + FIG1_OX - 0.5f, y0 = fig1_rects[i][1] + FIG1_OY - 0.5f;
        float x1 = fig1_rects[i][2] + FIG1_OX - 0.5f, y1 = fig1_rects[i][3] + FIG1_OY - 0.5f;
        float q[6][2] = { {x0, y0}, {x1, y0}, {x0, y1}, {x1, y0}, {x1, y1}, {x0, y1} };
        int j; for (j = 0; j < 6; j++) { V44 v = { q[j][0], q[j][1], 0.5f, 1.0f, FIGCOL }; fig1v[k++] = v; }
    }
    fig2t = FIG2_N; fig2v = malloc(sizeof(V44) * 3 * fig2t); k = 0;
    for (i = 0; i < FIG2_N; i++) {
        double a0 = 2 * 3.14159265358979 * i / FIG2_N, a1 = 2 * 3.14159265358979 * (i + 1) / FIG2_N;
        V44 c = { FIG2_CX, FIG2_CY, 0.5f, 1.0f, FIGCOL };
        V44 p0 = { FIG2_CX + FIG2_R * (float)cos(a0), FIG2_CY + FIG2_R * (float)sin(a0), 0.5f, 1.0f, FIGCOL };
        V44 p1 = { FIG2_CX + FIG2_R * (float)cos(a1), FIG2_CY + FIG2_R * (float)sin(a1), 0.5f, 1.0f, FIGCOL };
        fig2v[k++] = c; fig2v[k++] = p0; fig2v[k++] = p1;
    }
    tmpv = malloc(sizeof(V44) * 3 * (fig1t > fig2t ? fig1t : fig2t));
}
static void draw_fig(const V44 *v, int ntri, float dx, float dy, const char *vn) {
    int i; for (i = 0; i < 3 * ntri; i++) { tmpv[i] = v[i]; tmpv[i].x += dx; tmpv[i].y += dy; }
    DPUP(D3DPT_TRIANGLELIST, ntri, tmpv, sizeof(V44), vn);
}
/* stencil scene: figure = 0x80 (ALWAYS/REPLACE), 8 copies shifted by 2 px with GREATER ref=cat -> ring = cat */
static void build_scene(void) {
    int c, i;
    strcpy(phase, "scene");
    Clear(D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER | D3DCLEAR_STENCIL, bgcol, 1.0f, 0);
    SetVS0(); SetPS(NULL); SetFVF(D3DFVF_XYZRHW | D3DFVF_DIFFUSE);
    TSS(0, D3DTSS_COLOROP, D3DTOP_SELECTARG1); TSS(0, D3DTSS_COLORARG1, D3DTA_DIFFUSE);
    TSS(0, D3DTSS_ALPHAOP, D3DTOP_SELECTARG1); TSS(0, D3DTSS_ALPHAARG1, D3DTA_DIFFUSE);
    SRS(D3DRS_CULLMODE, D3DCULL_NONE); SRS(D3DRS_ZENABLE, D3DZB_TRUE); SRS(D3DRS_ZFUNC, D3DCMP_LESSEQUAL); SRS(D3DRS_ZWRITEENABLE, TRUE);
    SRS(D3DRS_ALPHABLENDENABLE, FALSE);
    for (c = 1; c <= NUNITS; c++) {
        const V44 *v = c == 1 ? fig1v : fig2v; int n = c == 1 ? fig1t : fig2t; const char *vn = c == 1 ? "'&FIG1'" : "'&FIG2'";
        SRS(D3DRS_STENCILENABLE, TRUE); SRS(D3DRS_STENCILFUNC, D3DCMP_ALWAYS); SRS(D3DRS_STENCILREF, FIG);
        SRS(D3DRS_STENCILPASS, D3DSTENCILOP_REPLACE); SRS(D3DRS_STENCILFAIL, D3DSTENCILOP_KEEP); SRS(D3DRS_STENCILZFAIL, D3DSTENCILOP_KEEP);
        SRS(D3DRS_STENCILMASK, 0xFF); SRS(D3DRS_STENCILWRITEMASK, 0xFF); SRS(D3DRS_COLORWRITEENABLE, 0xF);
        draw_fig(v, n, 0, 0, vn);
        SRS(D3DRS_STENCILFUNC, D3DCMP_GREATER); SRS(D3DRS_STENCILREF, c); SRS(D3DRS_COLORWRITEENABLE, 0);
        for (i = 0; i < 8; i++) draw_fig(v, n, OFFS[i][0], OFFS[i][1], vn);
        SRS(D3DRS_COLORWRITEENABLE, 0xF); SRS(D3DRS_STENCILENABLE, FALSE);
    }
    /* state "WoW" leaves behind: non-identity texture matrices (2D: translation in row 3) and non-zero
       TEXTURETRANSFORMFLAGS on stages 0/1; the emulated WoW cache remembers the TTFF values */
    {
        D3DMATRIX m; memset(&m, 0, sizeof m);
        m._11 = 0.5f; m._22 = 0.5f; m._31 = 0.25f; m._32 = 0.25f; m._33 = 1.0f; m._44 = 1.0f;
        for (i = 0; i < 5; i++) {
            lg(IDirect3DDevice9_SetTransform(dev, (D3DTRANSFORMSTATETYPE)(D3DTS_TEXTURE0 + i), &m), "'SetTransform', 'TEXTURE%d', 'scale 0.5 + 0.25'", i);
            TSS(i, D3DTSS_TEXTURETRANSFORMFLAGS, TTFF_WOW[i]); ttcache[i] = TTFF_WOW[i];
        }
    }
}

/* --- outline10 routines --- */
static void glfree(void) {           /* GLRES index 6..0: TEX2S TEX2 TEX1S TEX1 TEX0S TEX0 MSRT */
    void **res[7] = { (void **)&MSRT, (void **)&TEX0, (void **)&TEX0S, (void **)&TEX1, (void **)&TEX1S, (void **)&TEX2, (void **)&TEX2S };
    int i;
    for (i = 6; i >= 0; i--) { void *p = *res[i]; if (p) { Rel(p); } *res[i] = NULL; }
    RTDEV = NULL;
}
static void mkq(void) {
    int k, j;
    for (k = 0; k < 4; k++) {
        float *v = VERTT[k];
        float u = (k & 1) ? QU1 : QU0, w = (k & 2) ? QV1 : QV0;
        v[0] = (k & 1) ? QX1 : QX0; v[1] = (k & 2) ? QY1 : QY0; v[2] = 0.0f; v[3] = 1.0f;
        v[4] = u; v[5] = w;
        for (j = 0; j < 4; j++) {
            float o = j < 2 ? O1 : O2; int sg = (j & 1) ? -1 : 1;
            float du = QDU * o, dv = QDV * o;
            v[6 + 2 * j] = sg > 0 ? u + du : u - du;
            v[7 + 2 * j] = sg > 0 ? w + dv : w - dv;
        }
    }
}
static void dumpvertt(void) {
    int k, j;
    for (k = 0; k < 4; k++) { printf("V"); for (j = 0; j < 14; j++) printf(" %08lX", fh(VERTT[k][j])); printf("\n"); }
}
static void g_pass(IDirect3DTexture9 *src, IDirect3DSurface9 *dst) {
    SetTex(0, src);
    if (FAILED(SetRT(0, dst)) && !v1mode) GLFAIL = dev;       /* v2: test eax,eax / jge gp_ok / GLFAIL = device */
    mkq(); DPUP(D3DPT_TRIANGLESTRIP, 2, VERTT, 56, "'&VERTT'"); dumpvertt();
}
static DWORD ucol(int cat) { return UCOL[cat]; }
static void quad(int cat, DWORD col) {
    int k; for (k = 0; k < 4; k++) VERTS[k].c = col;
    SRS(D3DRS_STENCILREF, cat);
    DPUP(D3DPT_TRIANGLESTRIP, 2, VERTS, 20, "'&VERTS'");
}
static void glow(void) {
    int c; HRESULT hr;
    GLOK = 0;
    if (GLFAIL == dev) return;
    if (GPSDEV != dev) {
        GPSDEV = dev; GPS = NULL; CPS = NULL;
        CreatePS(GPSCODE, &GPS, "GPSCODE", "GPS");
        CreatePS(CPSCODE, &CPS, "CPSCODE", "CPS");
    }
    if (!GPS || !CPS) { GLFAIL = dev; return; }
    BBP = NULL; DSP = NULL;
    if (FAILED(lg(IDirect3DDevice9_GetRenderTarget(dev, 0, &BBP), "'GetRT', 0, '&BBP'"))) return;
    if (FAILED(lg(IDirect3DSurface9_GetDesc(BBP, &DESC), "'GetDesc', %s", nm(BBP)))) goto relbb;
    printf("%-7s   DESC: Format %d Type %d Usage 0x%lX Pool %d MultiSampleType %d MultiSampleQuality %lu Width %u Height %u\n", phase,
           DESC.Format, DESC.Type, DESC.Usage, DESC.Pool, DESC.MultiSampleType, DESC.MultiSampleQuality, DESC.Width, DESC.Height);
    if (DESC.Width != RTW || DESC.Height != RTH || DESC.MultiSampleType != RTMS || DESC.MultiSampleQuality != RTMQ || RTDEV != dev || !TEX2S) {
        glfree();
        RTW = DESC.Width; RTW2 = (RTW + 1) >> 1; RTH = DESC.Height; RTH2 = (RTH + 1) >> 1;
        RTMS = DESC.MultiSampleType; RTMQ = DESC.MultiSampleQuality;
        hr = lg(IDirect3DDevice9_CreateRenderTarget(dev, RTW, RTH, D3DFMT_A8R8G8B8, RTMS, RTMQ, FALSE, &MSRT, NULL),
                "'CreateRT', %u, %u, %d, %d, %lu, 0, '&MSRT', 0", RTW, RTH, D3DFMT_A8R8G8B8, RTMS, RTMQ);
        if (FAILED(hr)) goto nfail;
        hr = lg(IDirect3DDevice9_CreateTexture(dev, RTW, RTH, 1, D3DUSAGE_RENDERTARGET, D3DFMT_A8R8G8B8, D3DPOOL_DEFAULT, &TEX0, NULL),
                "'CreateTex', %u, %u, 1, 1, 21, 0, '&TEX0', 0", RTW, RTH);
        if (FAILED(hr)) goto nfail;
        hr = lg(IDirect3DTexture9_GetSurfaceLevel(TEX0, 0, &TEX0S), "'GetLevel', 'TEX0', 0"); if (FAILED(hr)) goto nfail;
        hr = lg(IDirect3DDevice9_CreateTexture(dev, RTW2, RTH2, 1, D3DUSAGE_RENDERTARGET, D3DFMT_A8R8G8B8, D3DPOOL_DEFAULT, &TEX1, NULL),
                "'CreateTex', %u, %u, 1, 1, 21, 0, '&TEX1', 0", RTW2, RTH2);
        if (FAILED(hr)) goto nfail;
        hr = lg(IDirect3DTexture9_GetSurfaceLevel(TEX1, 0, &TEX1S), "'GetLevel', 'TEX1', 0"); if (FAILED(hr)) goto nfail;
        hr = lg(IDirect3DDevice9_CreateTexture(dev, RTW2, RTH2, 1, D3DUSAGE_RENDERTARGET, D3DFMT_A8R8G8B8, D3DPOOL_DEFAULT, &TEX2, NULL),
                "'CreateTex', %u, %u, 1, 1, 21, 0, '&TEX2', 0", RTW2, RTH2);
        if (FAILED(hr)) goto nfail;
        hr = lg(IDirect3DTexture9_GetSurfaceLevel(TEX2, 0, &TEX2S), "'GetLevel', 'TEX2', 0"); if (FAILED(hr)) goto nfail;
        RTDEV = dev;
    }
    if (FAILED(lg(IDirect3DDevice9_GetDepthStencilSurface(dev, &DSP), "'GetDS', '&DSP'"))) goto relbb;
    if (!v1mode) {     /* v2: TTSAV[i] = WoW cache entry of TEXTURETRANSFORMFLAGS stage i */
        for (c = 0; c < 5; c++) TTSAV[c] = ttcache[c];
        printf("%-7s   TTSAV %08lX %08lX %08lX %08lX %08lX\n", phase, TTSAV[0], TTSAV[1], TTSAV[2], TTSAV[3], TTSAV[4]);
    }
    SRS(D3DRS_SCISSORTESTENABLE, 0);
    if (FAILED(SetRT(0, MSRT))) goto sfail;
    Clear(D3DCLEAR_TARGET, 0, 1.0f, 0);
    for (c = NUNITS; c >= 1; c--) quad(c, ucol(c) | 0xFF000000);
    if (FAILED(lg(IDirect3DDevice9_StretchRect(dev, MSRT, NULL, TEX0S, NULL, D3DTEXF_NONE), "'StretchRect', %s, 0, %s, 0, 0", nm(MSRT), nm(TEX0S)))) goto sfail;
    SetDS(NULL); SRS(D3DRS_ZENABLE, 0); SRS(D3DRS_STENCILENABLE, 0); SetPS(GPS); SetFVF(0x504);
    SSS(0, D3DSAMP_MAGFILTER, D3DTEXF_LINEAR); SSS(0, D3DSAMP_MINFILTER, D3DTEXF_LINEAR); SSS(0, D3DSAMP_MIPFILTER, D3DTEXF_NONE);
    SSS(0, D3DSAMP_ADDRESSU, D3DTADDRESS_CLAMP); SSS(0, D3DSAMP_ADDRESSV, D3DTADDRESS_CLAMP);
    for (c = 0; c < 5; c++) { TSS(c, D3DTSS_TEXCOORDINDEX, c); if (!ttff_noreset) TSS(c, D3DTSS_TEXTURETRANSFORMFLAGS, 0); }
    QX1 = (float)RTW2 - HALF; QY1 = (float)RTH2 - HALF; QX0 = hf(0xBF000000); QY0 = hf(0xBF000000);
    QU0 = 0; QV0 = 0; QU1 = 1.0f; QV1 = 1.0f; QDU = 0; QDV = 0;
    g_pass(TEX0, TEX1S);
    QDU = 1.0f / (float)RTW2;
    g_pass(TEX1, TEX2S);
    QDU = 0; QDV = 1.0f / (float)RTH2;
    g_pass(TEX2, TEX1S);
    if (!v1mode && GLFAIL == dev) goto rest;                 /* v2: a pass failed -> no composite */
    GLOK = 1;
    goto rest;
sfail:
    GLFAIL = dev;
rest:
    SetRT(0, BBP); SetDS(DSP); SetVP(); SRS(D3DRS_ZENABLE, 1); SRS(D3DRS_STENCILENABLE, 1);
    if (GLOK) {
        SRS(D3DRS_STENCILFUNC, D3DCMP_GREATER); SRS(D3DRS_STENCILREF, 0x80); SRS(D3DRS_ALPHABLENDENABLE, 1);
        SRS(D3DRS_SRCBLEND, D3DBLEND_ONE); SRS(D3DRS_DESTBLEND, D3DBLEND_INVSRCALPHA);
        if (!v1mode) SRS(D3DRS_COLORWRITEENABLE, 7);          /* v2: composite writes RGB only */
        SetPS(CPS); SetTex(0, TEX1);
        QX0 = (float)VP.X - HALF; QX1 = (float)(VP.X + VP.Width) - HALF;
        QY0 = (float)VP.Y - HALF; QY1 = (float)(VP.Y + VP.Height) - HALF;
        QU0 = (float)VP.X / (float)RTW; QU1 = (float)(VP.X + VP.Width) / (float)RTW;
        QV0 = (float)VP.Y / (float)RTH; QV1 = (float)(VP.Y + VP.Height) / (float)RTH;
        QDU = 0; QDV = 0;
        mkq(); DPUP(D3DPT_TRIANGLESTRIP, 2, VERTT, 56, "'&VERTT'"); dumpvertt();
    }
    SetTex(0, NULL); SRS(D3DRS_ALPHABLENDENABLE, 0); SRS(D3DRS_STENCILFUNC, D3DCMP_EQUAL);
    if (!v1mode) SRS(D3DRS_COLORWRITEENABLE, 0xF);            /* v2 */
    SetPS(PS); SetFVF(0x44);
    if (!v1mode)                                              /* v2: TTFF 0-4 back to WoW's cached values */
        for (c = 0; c < 5; c++) {
            if (TTSAV[c] != 0xFFFFFFFF) TSS(c, D3DTSS_TEXTURETRANSFORMFLAGS, TTSAV[c]);
            else printf("%-7s   TTSAV[%d] unknown -> no TSS (game marks its texture matrix dirty)\n", phase, c);
        }
    Rel(DSP); DSP = NULL;
relbb:
    Rel(BBP); BBP = NULL;
    return;
nfail:
    glfree(); GLFAIL = dev; goto relbb;
}
static DWORD light(DWORD c) {
    DWORD a = (c >> 2) & 0x3F3F3F, b = (c >> 3) & 0x1F1F1F;
    return (c & 0xFFFFFF) - a - b + 0xFF5E5E5E;
}
static void post(void) {
    int cat;
    if (PSDEV != dev) { PS = NULL; PSDEV = dev; CreatePS(RINGPSCODE, &PS, "PSCODE", "PS"); }
    if (!PS) return;
    SRS(52, 1); SRS(56, 3); SRS(55, 1); SRS(53, 1); SRS(54, 1); SRS(58, 0xFF); SRS(23, 8); SRS(14, 0); SRS(27, 0); SRS(15, 0);
    SRS(22, 1); SRS(168, 0xF); SRS(28, 0);
    SetVS0(); SetPS(PS); SetFVF(0x44);
    printf("MARK glowpart-begin\n");
    VERTS[0].x = VERTS[2].x = (float)VP.X - HALF; VERTS[1].x = VERTS[3].x = (float)(VP.X + VP.Width) - HALF;
    VERTS[0].y = VERTS[1].y = (float)VP.Y - HALF; VERTS[2].y = VERTS[3].y = (float)(VP.Y + VP.Height) - HALF;
    { int k; for (k = 0; k < 4; k++) { VERTS[k].z = 0.0f; VERTS[k].rhw = 1.0f; } }
    if (force_glfail) GLFAIL = dev;
    glow();
    if (force_glfail) GLFAIL = NULL;
    for (cat = NUNITS; cat >= 1; cat--) {
        DWORD c = ucol(cat);
        if (GLOK) c = light(c);
        quad(cat, c);
    }
    Clear(D3DCLEAR_STENCIL, 0, 1.0f, 0); SRS(52, 0);
    printf("MARK glowpart-end GLOK=%d\n", GLOK);
}

/* --- readback --- */
static void write_out(const char *name, const D3DLOCKED_RECT *lr, UINT w, UINT h, int alpha) {
    char fn[160]; FILE *f; UINT x, y; int rowsz = (w * 3 + 3) & ~3; unsigned char hdr[54] = { 'B', 'M' };
    unsigned char *row = calloc(1, rowsz);
    snprintf(fn, sizeof fn, "%s_%s.raw", prefix, name);
    f = fopen(fn, "wb"); fwrite(&w, 4, 1, f); fwrite(&h, 4, 1, f);
    for (y = 0; y < h; y++) fwrite((const char *)lr->pBits + y * lr->Pitch, 4, w, f);
    fclose(f);
    snprintf(fn, sizeof fn, "%s_%s%s.bmp", prefix, name, alpha ? "_alpha" : "");
    *(DWORD *)(hdr + 2) = 54 + rowsz * h; *(DWORD *)(hdr + 10) = 54; *(DWORD *)(hdr + 14) = 40;
    *(LONG *)(hdr + 18) = w; *(LONG *)(hdr + 22) = h; *(WORD *)(hdr + 26) = 1; *(WORD *)(hdr + 28) = 24;
    *(DWORD *)(hdr + 34) = rowsz * h;
    f = fopen(fn, "wb"); fwrite(hdr, 54, 1, f);
    for (y = h; y-- > 0;) {
        const unsigned char *s = (const unsigned char *)lr->pBits + y * lr->Pitch;
        for (x = 0; x < w; x++) {
            if (alpha) { row[3 * x] = row[3 * x + 1] = row[3 * x + 2] = s[4 * x + 3]; }
            else { row[3 * x] = s[4 * x]; row[3 * x + 1] = s[4 * x + 1]; row[3 * x + 2] = s[4 * x + 2]; }
        }
        fwrite(row, rowsz, 1, f);
    }
    fclose(f); free(row);
    printf("%-7s   saved %s (%ux%u)\n", phase, fn, w, h);
}
static void save_surface(IDirect3DSurface9 *src, const char *name, int with_alpha) {
    D3DSURFACE_DESC d; IDirect3DSurface9 *rs = NULL, *sys = NULL, *from = src; D3DLOCKED_RECT lr;
    lg(IDirect3DSurface9_GetDesc(src, &d), "'GetDesc', %s", nm(src));
    if (d.MultiSampleType != D3DMULTISAMPLE_NONE) {
        if (FAILED(lg(IDirect3DDevice9_CreateRenderTarget(dev, d.Width, d.Height, d.Format, D3DMULTISAMPLE_NONE, 0, FALSE, &rs, NULL),
                      "'CreateRT', %u, %u, %d, 0, 0, 0, '&resolve', 0", d.Width, d.Height, d.Format))) return;
        if (FAILED(lg(IDirect3DDevice9_StretchRect(dev, src, NULL, rs, NULL, D3DTEXF_NONE), "'StretchRect', %s, 0, 'resolve', 0, 0", nm(src)))) goto out;
        from = rs;
    }
    if (FAILED(lg(IDirect3DDevice9_CreateOffscreenPlainSurface(dev, d.Width, d.Height, d.Format, D3DPOOL_SYSTEMMEM, &sys, NULL),
                  "'CreateOffscreenPlainSurface', %u, %u, %d, 'SYSTEMMEM'", d.Width, d.Height, d.Format))) goto out;
    if (FAILED(lg(IDirect3DDevice9_GetRenderTargetData(dev, from, sys), "'GetRenderTargetData', %s, 'sys'", rs ? "'resolve'" : nm(src)))) goto out;
    if (SUCCEEDED(lg(IDirect3DSurface9_LockRect(sys, &lr, NULL, D3DLOCK_READONLY), "'LockRect', 'sys'"))) {
        write_out(name, &lr, d.Width, d.Height, 0);
        if (with_alpha) write_out(name, &lr, d.Width, d.Height, 1);
        lg(IDirect3DSurface9_UnlockRect(sys), "'UnlockRect', 'sys'");
    }
out:
    if (sys) Rel(sys);
    if (rs) Rel(rs);
}
static void save_backbuffer(const char *name) {
    IDirect3DSurface9 *bb = NULL;
    if (FAILED(lg(IDirect3DDevice9_GetBackBuffer(dev, 0, 0, D3DBACKBUFFER_TYPE_MONO, &bb), "'GetBackBuffer', 0, 0, 0"))) return;
    save_surface(bb, name, 0);
    Rel(bb);
}
static void make_a8rt(void) {
    if (!a8rt_mode || A8RT) return;
    lg(IDirect3DDevice9_CreateRenderTarget(dev, RTWFULL, RTHFULL, D3DFMT_A8R8G8B8, g_ms, g_mq, FALSE, &A8RT, NULL),
       "'CreateRT', %lu, %lu, 21, %d, %lu, 0, '&A8RT', 0", RTWFULL, RTHFULL, g_ms, g_mq);
}
static void drop_a8rt(void) {
    if (A8RT) { ULONG r = IUnknown_Release((IUnknown *)A8RT); printf("%-7s T ('Release', 'A8RT') => refs %lu\n", phase, r); A8RT = NULL; }
}
static void refresh_refs(void) {
    IDirect3DSurface9 *s = NULL;
    if (SUCCEEDED(IDirect3DDevice9_GetBackBuffer(dev, 0, 0, D3DBACKBUFFER_TYPE_MONO, &s))) { BBREF = s; IUnknown_Release((IUnknown *)s); }
    s = NULL;
    if (SUCCEEDED(IDirect3DDevice9_GetDepthStencilSurface(dev, &s))) { DSREF = s; IUnknown_Release((IUnknown *)s); }
    IDirect3DDevice9_GetViewport(dev, &VP);
    printf("%-7s   viewport %lu,%lu %lux%lu z %.1f..%.1f\n", phase, VP.X, VP.Y, VP.Width, VP.Height, VP.MinZ, VP.MaxZ);
    make_a8rt();
}
static void frame(const char *name, int save_tex) {
    { MSG m; while (PeekMessageA(&m, NULL, 0, 0, PM_REMOVE)) { TranslateMessage(&m); DispatchMessageA(&m); } }
    strcpy(phase, name);
    lg(IDirect3DDevice9_BeginScene(dev), "'BeginScene'");
    if (a8rt_mode) lg(IDirect3DDevice9_SetRenderTarget(dev, 0, A8RT), "'SetRT', 0, 'A8RT'");
    if (use_subvp) {      /* game viewport with offset: clear the whole target, then draw into the sub-viewport */
        D3DVIEWPORT9 full = { 0, 0, RTWFULL, RTHFULL, 0.0f, 1.0f };
        lg(IDirect3DDevice9_SetViewport(dev, &full), "'SetVP', 'full'");
        Clear(D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER | D3DCLEAR_STENCIL, bgcol, 1.0f, 0);
        VP = SUBVP;
        lg(IDirect3DDevice9_SetViewport(dev, &VP), "'SetVP', 'sub %lu,%lu %lux%lu'", VP.X, VP.Y, VP.Width, VP.Height);
    }
    build_scene();
    strcpy(phase, name);
    post();
    lg(IDirect3DDevice9_EndScene(dev), "'EndScene'");
    if (a8rt_mode) {
        IDirect3DSurface9 *bb = NULL;
        save_surface(A8RT, name, 1);                       /* RGB + alpha of the A8R8G8B8 scene target */
        if (SUCCEEDED(lg(IDirect3DDevice9_GetBackBuffer(dev, 0, 0, D3DBACKBUFFER_TYPE_MONO, &bb), "'GetBackBuffer', 0, 0, 0"))) {
            lg(IDirect3DDevice9_StretchRect(dev, A8RT, NULL, bb, NULL, D3DTEXF_NONE), "'StretchRect', 'A8RT', 0, 'BB', 0, 0");
            lg(IDirect3DDevice9_SetRenderTarget(dev, 0, bb), "'SetRT', 0, 'BB'");
            Rel(bb);
        }
    } else
        save_backbuffer(name);
    if (save_tex && TEX0S) {
        char n[48];
        snprintf(n, sizeof n, "%s_tex0", name); save_surface(TEX0S, n, 1);
        snprintf(n, sizeof n, "%s_tex2", name); save_surface(TEX2S, n, 1);
        snprintf(n, sizeof n, "%s_tex1", name); save_surface(TEX1S, n, 1);
    }
    lg(IDirect3DDevice9_Present(dev, NULL, NULL, NULL, NULL), "'Present'");
}
static LRESULT CALLBACK wndproc(HWND h, UINT m, WPARAM w, LPARAM l) { return DefWindowProcA(h, m, w, l); }

int main(int argc, char **argv) {
    D3DMULTISAMPLE_TYPE ms = argc > 1 ? (D3DMULTISAMPLE_TYPE)atoi(argv[1]) : D3DMULTISAMPLE_4_SAMPLES;
    DWORD mq = argc > 2 ? (DWORD)atoi(argv[2]) : 0;
    UINT W = argc > 3 ? (UINT)atoi(argv[3]) : 640, H = argc > 4 ? (UINT)atoi(argv[4]) : 480;
    D3DPRESENT_PARAMETERS pp0, pp; D3DADAPTER_IDENTIFIER9 id; D3DCAPS9 caps; HRESULT hr;
    WNDCLASSA wc; RECT r = { 0, 0, 0, 0 }; HWND hwnd; DWORD q;
    D3DFORMAT fmts[3] = { D3DFMT_X8R8G8B8, D3DFMT_A8R8G8B8, D3DFMT_D24S8 }; int i;
    if (argc > 5) snprintf(prefix, sizeof prefix, "%s", argv[5]);
    if (argc > 9) { use_subvp = 1; SUBVP.X = atoi(argv[6]); SUBVP.Y = atoi(argv[7]); SUBVP.Width = atoi(argv[8]); SUBVP.Height = atoi(argv[9]); SUBVP.MinZ = 0; SUBVP.MaxZ = 1;
                    printf("sub-viewport %lu,%lu %lux%lu\n", SUBVP.X, SUBVP.Y, SUBVP.Width, SUBVP.Height); }
    RTWFULL = W; RTHFULL = H;
    setvbuf(stdout, NULL, _IONBF, 0);
    v1mode = getenv("GLOW_V1") && atoi(getenv("GLOW_V1"));
    a8rt_mode = getenv("GLOW_A8RT") && atoi(getenv("GLOW_A8RT"));
    ttff_noreset = getenv("GLOW_TTFF_NORESET") && atoi(getenv("GLOW_TTFF_NORESET"));
    if (a8rt_mode) bgcol = 0x40384030;
    g_ms = ms; g_mq = mq;
    printf("glowtest: %u-bit build, ms=%d mq=%lu %ux%u prefix=%s sequence=%s rt0=%s%s\n", (unsigned)(sizeof(void *) * 8), ms, mq, W, H, prefix,
           v1mode ? "v1" : "v2", a8rt_mode ? "A8R8G8B8 render target (alpha 0x40)" : "X8R8G8B8 backbuffer", ttff_noreset ? " TTFF-NORESET(control)" : "");
    build_geometry();
    memset(&wc, 0, sizeof wc); wc.lpfnWndProc = wndproc; wc.hInstance = GetModuleHandleA(NULL); wc.lpszClassName = "glowtest";
    RegisterClassA(&wc);
    r.right = W; r.bottom = H; AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW, FALSE);
    hwnd = CreateWindowA("glowtest", "glowtest", WS_OVERLAPPEDWINDOW | WS_VISIBLE, 0, 0, r.right - r.left, r.bottom - r.top, NULL, NULL, wc.hInstance, NULL);
    d3d = Direct3DCreate9(D3D_SDK_VERSION);
    if (!d3d) { printf("Direct3DCreate9 failed\n"); return 1; }
    lg(IDirect3D9_GetAdapterIdentifier(d3d, 0, 0, &id), "'GetAdapterIdentifier'");
    printf("  adapter: Driver '%s' Description '%s' Vendor 0x%04lX Device 0x%04lX\n", id.Driver, id.Description, id.VendorId, id.DeviceId);
    for (i = 0; i < 3; i++) {
        q = 0; hr = IDirect3D9_CheckDeviceMultiSampleType(d3d, 0, D3DDEVTYPE_HAL, fmts[i], TRUE, ms, &q);
        lg(hr, "'CheckDeviceMultiSampleType', fmt %d, windowed, ms %d", fmts[i], ms);
        printf("         quality levels: %lu\n", q);
    }
    for (i = 2; i <= 16; i++) {
        DWORD q1 = 0, q2 = 0;
        HRESULT h1 = IDirect3D9_CheckDeviceMultiSampleType(d3d, 0, D3DDEVTYPE_HAL, D3DFMT_A8R8G8B8, TRUE, (D3DMULTISAMPLE_TYPE)i, &q1);
        HRESULT h2 = IDirect3D9_CheckDeviceMultiSampleType(d3d, 0, D3DDEVTYPE_HAL, D3DFMT_D24S8, TRUE, (D3DMULTISAMPLE_TYPE)i, &q2);
        if (SUCCEEDED(h1) || SUCCEEDED(h2)) printf("  supported MS type %d: A8R8G8B8 hr=0x%08lX q=%lu, D24S8 hr=0x%08lX q=%lu\n", i, h1, q1, h2, q2);
    }
    { DWORD q1 = 0; HRESULT h1 = IDirect3D9_CheckDeviceMultiSampleType(d3d, 0, D3DDEVTYPE_HAL, D3DFMT_X8R8G8B8, TRUE, D3DMULTISAMPLE_NONMASKABLE, &q1);
      printf("  NONMASKABLE X8R8G8B8: hr=0x%08lX quality levels %lu\n", h1, q1); }
    memset(&pp0, 0, sizeof pp0);
    pp0.BackBufferWidth = W; pp0.BackBufferHeight = H; pp0.BackBufferFormat = D3DFMT_X8R8G8B8; pp0.BackBufferCount = 1;
    pp0.MultiSampleType = ms; pp0.MultiSampleQuality = mq; pp0.SwapEffect = D3DSWAPEFFECT_DISCARD; pp0.hDeviceWindow = hwnd;
    pp0.Windowed = TRUE; pp0.EnableAutoDepthStencil = TRUE; pp0.AutoDepthStencilFormat = D3DFMT_D24S8;
    pp0.PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE;
    pp = pp0;
    hr = lg(IDirect3D9_CreateDevice(d3d, 0, D3DDEVTYPE_HAL, hwnd, D3DCREATE_HARDWARE_VERTEXPROCESSING, &pp, &dev), "'CreateDevice', HAL, HWVP, ms %d", ms);
    if (FAILED(hr)) { printf("CreateDevice failed\n"); return 1; }
    lg(IDirect3DDevice9_GetDeviceCaps(dev, &caps), "'GetDeviceCaps'");
    printf("  caps: PS %lu.%lu VS %lu.%lu MaxSimultaneousTextures %lu FVF texcoords %lu TextureCaps POW2=%d NONPOW2CONDITIONAL=%d StretchRectFilterCaps 0x%lX NumSimultaneousRTs %lu MaxTex %lux%lu\n",
           (caps.PixelShaderVersion >> 8) & 0xFF, caps.PixelShaderVersion & 0xFF, (caps.VertexShaderVersion >> 8) & 0xFF, caps.VertexShaderVersion & 0xFF,
           caps.MaxSimultaneousTextures, caps.FVFCaps & 0xFFFF, !!(caps.TextureCaps & D3DPTEXTURECAPS_POW2), !!(caps.TextureCaps & D3DPTEXTURECAPS_NONPOW2CONDITIONAL),
           caps.StretchRectFilterCaps, caps.NumSimultaneousRTs, caps.MaxTextureWidth, caps.MaxTextureHeight);
    printf("  caps: PrimitiveMiscCaps COLORWRITEENABLE=%d\n", !!(caps.PrimitiveMiscCaps & D3DPMISCCAPS_COLORWRITEENABLE));
    refresh_refs();

    /* frame 0: reference without glow (GLFAIL -> thin lines in normal colour) */
    force_glfail = 1; frame("f0", 0); force_glfail = 0;
    /* frame 1: glow, objects created */
    frame("f1", 1);
    /* frame 1b: glow, objects reused (nothing created) */
    frame("f1b", 0);

    /* release before Reset like glrel: 7 objects (BBP/DSP are released at the end of glow) */
    strcpy(phase, "reset1");
    glfree(); drop_a8rt();
    pp = pp0;
    expect(IDirect3DDevice9_Reset(dev, &pp), D3D_OK, "'Reset' after releasing all 7 glow objects");
    expect(IDirect3DDevice9_TestCooperativeLevel(dev), D3D_OK, "'TestCooperativeLevel' after successful Reset");
    refresh_refs();
    /* frame 2: after Reset - shaders kept, textures recreated */
    frame("f2", 0);

    /* negative control: TEX1 (default pool render-target texture) still alive */
    strcpy(phase, "reset2");
    {
        IDirect3DTexture9 *keep = TEX1;
        Rel(TEX2S); TEX2S = NULL; Rel(TEX2); TEX2 = NULL; Rel(TEX1S); TEX1S = NULL; TEX1 = NULL;  /* TEX1 itself not released */
        Rel(TEX0S); TEX0S = NULL; Rel(TEX0); TEX0 = NULL; Rel(MSRT); MSRT = NULL; RTDEV = NULL;
        drop_a8rt();
        pp = pp0;
        expect(IDirect3DDevice9_Reset(dev, &pp), D3DERR_INVALIDCALL, "'Reset' with TEX1 (D3DPOOL_DEFAULT texture) still alive");
        hr = IDirect3DDevice9_TestCooperativeLevel(dev);
        printf("%-7s   TestCooperativeLevel after failed Reset => 0x%08lX %s\n", phase, hr, hrname(hr));
        hr = IDirect3DDevice9_BeginScene(dev);
        printf("%-7s   BeginScene while not reset => 0x%08lX %s\n", phase, hr, hrname(hr));
        if (SUCCEEDED(hr)) IDirect3DDevice9_EndScene(dev);
        TEX1 = keep; Rel(TEX1); TEX1 = NULL;
        pp = pp0;
        expect(IDirect3DDevice9_Reset(dev, &pp), D3D_OK, "'Reset' after releasing TEX1 too");
        expect(IDirect3DDevice9_TestCooperativeLevel(dev), D3D_OK, "'TestCooperativeLevel' after second successful Reset");
        refresh_refs();
    }
    /* negative control 2: only a surface reference (GetSurfaceLevel) still alive */
    frame("f3", 1);
    strcpy(phase, "reset3");
    {
        IDirect3DSurface9 *keep = TEX0S;
        Rel(TEX2S); TEX2S = NULL; Rel(TEX2); TEX2 = NULL; Rel(TEX1S); TEX1S = NULL; Rel(TEX1); TEX1 = NULL;
        TEX0S = NULL; Rel(TEX0); TEX0 = NULL; Rel(MSRT); MSRT = NULL; RTDEV = NULL;   /* TEX0S not released */
        drop_a8rt();
        pp = pp0;
        expect(IDirect3DDevice9_Reset(dev, &pp), D3DERR_INVALIDCALL, "'Reset' with TEX0S (surface of default-pool texture) still referenced");
        TEX0S = keep; Rel(TEX0S); TEX0S = NULL;
        pp = pp0;
        expect(IDirect3DDevice9_Reset(dev, &pp), D3D_OK, "'Reset' after releasing TEX0S");
        refresh_refs();
    }
    frame("f4", 0);
    /* teardown like glrel(1): also the 3 pixel shaders */
    strcpy(phase, "end");
    glfree();
    if (GPS) Rel(GPS);
    if (CPS) Rel(CPS);
    if (PS) Rel(PS);
    drop_a8rt();
    printf("%-7s   device Release => %lu\n", phase, IDirect3DDevice9_Release(dev));
    printf("%-7s   d3d Release => %lu\n", phase, IDirect3D9_Release(d3d));
    DestroyWindow(hwnd);
    printf("SUMMARY calls %d failed %d\n", ncalls, nfail);
    return nfail ? 2 : 0;
}
