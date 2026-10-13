/* stenciltest.c - checks the outline10 "later geometry" (SMODE) stencil logic of ol2/outline10.py (routine dip)
 * on a real Direct3D 9 implementation and prototypes fixes.
 *
 * Stencil scene like the patch: figure = FIG (0x80), ring = category (1..48), background 0, built with the same
 * render-state sequence as d_mark (figure pass, second pass, 8 shifted invisible copies). Then "later geometry"
 * L (depth writing, not outlined) is drawn with DrawIndexedPrimitive or DrawPrimitive from a vertex/index buffer,
 * under one of these schemes:
 *   NONE   unpatched reference: stencil disabled
 *   PROBE  ALWAYS/REPLACE 0xFF: marks the pixels where L passes depth (+alpha) test = "L is in front" (P)
 *   CUR    outline10 as is: STENCILFUNC LESS, REF WPROT, PASS ZERO, FAIL/ZFAIL KEEP, masks 0xFF
 *   S1     STENCILFUNC ALWAYS, PASS ZERO, FAIL/ZFAIL KEEP, write mask 0xFF (single pass)
 *   S2     WPROT 0: like S1. WPROT>0: pass 1 stencil off (as unpatched), pass 2 same draw with COLORWRITE 0,
 *          ZWRITE 0, ZFUNC EQUAL, STENCILFUNC LESS REF WPROT, PASS ZERO; then restore
 *   S2LE   like S2 but pass 2 with ZFUNC LESSEQUAL
 *   S3     "U-bit" encoding (scene marked with figure 0xC0, ring 0x40|cat, second pass 0xC0|cat):
 *          STENCILFUNC ALWAYS, PASS ZERO, write mask 0xC0 (single pass); post: ring quad REF 0x40|cat,
 *          mask 0x3F for protected categories (<= WPROT), 0xFF otherwise
 * Readback: colour via GetRenderTargetData, stencil exactly via 8 stencil-tested full-screen quads (one per bit,
 * additive blending) into an X8R8G8B8 render target sharing the depth-stencil surface.
 * usage: stenciltest.exe [mstype] [outdir]
 */
#define COBJMACROS
#include <windows.h>
#include <d3d9.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define W 256
#define H 160
#define NPIX (W * H)

static IDirect3D9 *d3d; static IDirect3DDevice9 *dev; static HWND hwnd;
static IDirect3DSurface9 *BB, *DS, *SRT, *RES, *SYS;
static D3DMULTISAMPLE_TYPE MS;
static int nerr;
static char outdir[200] = ".";

static void chk(HRESULT hr, const char *what) { if (FAILED(hr)) { printf("ERROR %s hr=0x%08lX\n", what, (unsigned long)hr); nerr++; } }
static void SRS(DWORD s, DWORD v) { chk(IDirect3DDevice9_SetRenderState(dev, (D3DRENDERSTATETYPE)s, v), "SetRenderState"); }
static void TSS(DWORD st, DWORD t, DWORD v) { chk(IDirect3DDevice9_SetTextureStageState(dev, st, (D3DTEXTURESTAGESTATETYPE)t, v), "TSS"); }
static void SSS(DWORD st, DWORD t, DWORD v) { chk(IDirect3DDevice9_SetSamplerState(dev, st, (D3DSAMPLERSTATETYPE)t, v), "SSS"); }
static void begin(void) { chk(IDirect3DDevice9_BeginScene(dev), "BeginScene"); }
static void end(void) { chk(IDirect3DDevice9_EndScene(dev), "EndScene"); }

/* render-state numbers as used by the patch */
enum { RS_ZENABLE = 7, RS_ZWRITE = 14, RS_ATEST = 15, RS_ZFUNC = 23, RS_AREF = 24, RS_AFUNC = 25, RS_ABLEND = 27,
       RS_SENABLE = 52, RS_SFAIL = 53, RS_SZFAIL = 54, RS_SPASS = 55, RS_SFUNC = 56, RS_SREF = 57, RS_SMASK = 58,
       RS_SWMASK = 59, RS_CWRITE = 168 };
enum { KEEP = 1, ZERO = 2, REPLACE = 3 };
enum { NEVER = 1, LESS = 2, EQUAL = 3, LESSEQUAL = 4, GREATER = 5, ALWAYS = 8 };

/* ---------------- geometry ---------------- */
typedef struct { float x, y, z, rhw; DWORD c; } V2D;
typedef struct { float x, y, z, rhw; DWORD c; float u, v; } VT;
typedef struct { float x, y, z; DWORD c; float u, v; } VW;
#define FVF2D (D3DFVF_XYZRHW | D3DFVF_DIFFUSE)
#define FVFT (D3DFVF_XYZRHW | D3DFVF_DIFFUSE | D3DFVF_TEX1)
#define FVFW (D3DFVF_XYZ | D3DFVF_DIFFUSE | D3DFVF_TEX1)
#define NSEG 48
static V2D figA[3 * NSEG], figB[3 * NSEG], figC[3 * NSEG], weapB[6], wallR[6], floorR[6], tmpv[3 * NSEG];
static const float OFFS[8][2] = { {1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, 1}, {1, -1}, {-1, 1}, {-1, -1} };
static float PX = 3.0f;                       /* ring width in pixels (patch: 2) */
static const DWORD BG = 0xFF202838, FLOORC = 0xFF505050, WALLC = 0xFF806040, FIGAC = 0xFFB4B4B4, FIGBC = 0xFF8C8C9C,
                   FIGCC = 0xFFC8A0A0, WEAPC = 0xFFE0E0E0;
static const DWORD RINGCOL[4] = { 0, 0xFFFFD100, 0xFF00A0FF, 0xFFFF40FF };

static void mk_ellipse(V2D *v, float cx, float cy, float rx, float ry, float z, DWORD c) {
    int i; for (i = 0; i < NSEG; i++) {
        double a0 = 2 * 3.14159265358979 * i / NSEG, a1 = 2 * 3.14159265358979 * (i + 1) / NSEG;
        V2D p = { cx, cy, z, 1, c }, q0 = { cx + rx * (float)cos(a0), cy + ry * (float)sin(a0), z, 1, c },
            q1 = { cx + rx * (float)cos(a1), cy + ry * (float)sin(a1), z, 1, c };
        v[3 * i] = p; v[3 * i + 1] = q0; v[3 * i + 2] = q1;
    }
}
static void mk_rect(V2D *v, float x0, float y0, float x1, float y1, float z, DWORD c) {
    V2D a = { x0, y0, z, 1, c }, b = { x1, y0, z, 1, c }, d = { x0, y1, z, 1, c }, e = { x1, y1, z, 1, c };
    v[0] = a; v[1] = b; v[2] = d; v[3] = b; v[4] = e; v[5] = d;
}
static void dpup(const V2D *v, int ntri, float dx, float dy) {
    int i; for (i = 0; i < 3 * ntri; i++) { tmpv[i] = v[i]; tmpv[i].x += dx; tmpv[i].y += dy; }
    chk(IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLELIST, ntri, tmpv, sizeof(V2D)), "DrawPrimitiveUP");
}
static void fullquad(DWORD c) {
    V2D q[4] = { {-0.5f, -0.5f, 0, 1, c}, {W - 0.5f, -0.5f, 0, 1, c}, {-0.5f, H - 0.5f, 0, 1, c}, {W - 0.5f, H - 0.5f, 0, 1, c} };
    chk(IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_TRIANGLESTRIP, 2, q, sizeof(V2D)), "DrawPrimitiveUP quad");
}
static void base2d(void) {
    IDirect3DDevice9_SetVertexShader(dev, NULL); IDirect3DDevice9_SetPixelShader(dev, NULL);
    IDirect3DDevice9_SetTexture(dev, 0, NULL); chk(IDirect3DDevice9_SetFVF(dev, FVF2D), "SetFVF");
    TSS(0, D3DTSS_COLOROP, D3DTOP_SELECTARG1); TSS(0, D3DTSS_COLORARG1, D3DTA_DIFFUSE);
    TSS(0, D3DTSS_ALPHAOP, D3DTOP_SELECTARG1); TSS(0, D3DTSS_ALPHAARG1, D3DTA_DIFFUSE);
    TSS(1, D3DTSS_COLOROP, D3DTOP_DISABLE); TSS(1, D3DTSS_ALPHAOP, D3DTOP_DISABLE);
    SRS(D3DRS_LIGHTING, FALSE); SRS(D3DRS_CULLMODE, D3DCULL_NONE); SRS(D3DRS_FOGENABLE, FALSE);
    SRS(RS_ZENABLE, TRUE); SRS(RS_ZFUNC, LESSEQUAL); SRS(RS_ZWRITE, TRUE); SRS(RS_ABLEND, FALSE); SRS(RS_ATEST, FALSE);
    SRS(RS_CWRITE, 0xF); SRS(RS_SENABLE, FALSE);
}

/* ---- later geometry L: screen-space grid, drawn from VB/IB, three vertex paths ---- */
enum { P_RHW, P_XFORM, P_VS };
static const char *PATHN[3] = { "rhw", "ffp", "vs" };
enum { L_GRAD, L_FRONT, L_BACK, L_GRID, L_SMALL, L_TRANS, L_OP2, NLSH };
static const char *LSHN[NLSH] = { "grad", "front", "back", "grid", "small", "trans", "op2" };
typedef struct { IDirect3DVertexBuffer9 *vbt_i, *vbw_i, *vbt_l, *vbw_l; IDirect3DIndexBuffer9 *ib; int nv, ntri; } LMesh;
static LMesh LM[NLSH];
static float MC[4][4];                 /* clip = MC * (X,Y,Z,1)^T */
static float RM[3][3], TV[3];          /* view = RM*world + TV */
static const float PC = 10.0f / 9.0f, PD = -10.0f / 9.0f;   /* clip_z = PC*Zv + PD, clip_w = Zv  (near 1, far 10) */
static IDirect3DVertexShader9 *VS;
static IDirect3DTexture9 *TEXA;
static const DWORD VS11[] = {
    0xFFFE0101,
    0x0000001F, 0x80000000, 0x900F0000,               /* dcl_position v0 */
    0x0000001F, 0x8000000A, 0x900F0001,               /* dcl_color v1 */
    0x0000001F, 0x80000005, 0x900F0002,               /* dcl_texcoord v2 */
    0x00000014, 0xC00F0000, 0x90E40000, 0xA0E40000,   /* m4x4 oPos, v0, c0 */
    0x00000001, 0xD00F0000, 0x90E40001,               /* mov oD0, v1 */
    0x00000001, 0xE00F0000, 0x90E40002,               /* mov oT0, v2 */
    0x0000FFFF };
static void setup_matrices(void) {
    double ay = 0.31, ax = 0.17, cy = cos(ay), sy = sin(ay), cx = cos(ax), sx = sin(ax);
    double ry[3][3] = { {cy, 0, sy}, {0, 1, 0}, {-sy, 0, cy} }, rx[3][3] = { {1, 0, 0}, {0, cx, -sx}, {0, sx, cx} };
    int i, j, k; float P4[4][4] = { {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, PC, PD}, {0, 0, 1, 0} }, A4[4][4];
    for (i = 0; i < 3; i++) for (j = 0; j < 3; j++) { double s = 0; for (k = 0; k < 3; k++) s += rx[i][k] * ry[k][j]; RM[i][j] = (float)s; }
    TV[0] = 0.13f; TV[1] = -0.21f; TV[2] = 0.37f;
    memset(A4, 0, sizeof A4);
    for (i = 0; i < 3; i++) { for (j = 0; j < 3; j++) A4[i][j] = RM[i][j]; A4[i][3] = TV[i]; }
    A4[3][3] = 1;
    for (i = 0; i < 4; i++) for (j = 0; j < 4; j++) { float s = 0; for (k = 0; k < 4; k++) s += P4[i][k] * A4[k][j]; MC[i][j] = s; }
}
/* screen (sx, sy, z_ndc) -> world position + rhw */
static void unproject(float sx, float sy, float zn, float out[3], float *rhw) {
    double Zv = PD / (zn - PC), nx = 2.0 * sx / W - 1.0, ny = 1.0 - 2.0 * sy / H, v[3], t[3]; int i, k;
    v[0] = nx * Zv; v[1] = ny * Zv; v[2] = Zv;
    for (i = 0; i < 3; i++) t[i] = v[i] - TV[i];
    for (i = 0; i < 3; i++) { double s = 0; for (k = 0; k < 3; k++) s += RM[k][i] * t[k]; out[i] = (float)s; }   /* RM^T */
    *rhw = (float)(1.0 / Zv);
}
static uint32_t rng = 12345;
static float frand(void) { rng = rng * 1103515245u + 12345u; return ((rng >> 8) & 0xFFFF) / 65535.0f; }
static void build_mesh(int shape) {
    int gx, gy, layers = 1, L, i, j, nv, ntri, k; float x0, y0, x1, y1; DWORD col = 0xFF40C040;
    VT *vt; VW *vw; WORD *ix; VT *lt; VW *lw; void *p; LMesh *m = &LM[shape];
    switch (shape) {
    case L_GRID: gx = 32; gy = 20; layers = 2; x0 = 0; y0 = 0; x1 = W; y1 = H; break;
    case L_SMALL: gx = 2; gy = 2; x0 = 4; y0 = 4; x1 = 30; y1 = 30; col = 0xFFC0C040; break;
    case L_TRANS: gx = 4; gy = 4; x0 = 30; y0 = 30; x1 = 230; y1 = 130; col = 0x80FF8040; break;
    case L_OP2: gx = 4; gy = 4; x0 = 60; y0 = 90; x1 = 120; y1 = 150; col = 0xFF4060E0; break;
    default: gx = 16; gy = 6; x0 = 20; y0 = 52; x1 = 240; y1 = 112; break;
    }
    nv = (gx + 1) * (gy + 1) * layers; ntri = gx * gy * 2 * layers;
    vt = malloc(sizeof(VT) * nv); vw = malloc(sizeof(VW) * nv); ix = malloc(sizeof(WORD) * 3 * ntri);
    lt = malloc(sizeof(VT) * 3 * ntri); lw = malloc(sizeof(VW) * 3 * ntri);
    k = 0;
    for (L = 0; L < layers; L++) for (j = 0; j <= gy; j++) for (i = 0; i <= gx; i++) {
        float sx = x0 + (x1 - x0) * i / gx, sy = y0 + (y1 - y0) * j / gy, zn, pos[3], rhw; DWORD c = col;
        switch (shape) {
        case L_GRAD: zn = 0.25f + 0.5f * (sx - 20) / 220; break;
        case L_FRONT: zn = 0.3f; break;
        case L_BACK: zn = 0.7f; break;
        case L_GRID: zn = 0.3f + 0.4f * frand(); c = L ? 0xFFD06030 : 0xFF30A0D0; break;
        case L_SMALL: zn = 0.4f; break;
        case L_TRANS: zn = 0.1f; break;
        default: zn = 0.3f; break;
        }
        unproject(sx, sy, zn, pos, &rhw);
        vt[k].x = sx; vt[k].y = sy; vt[k].z = zn; vt[k].rhw = rhw; vt[k].c = c; vt[k].u = sx / 16; vt[k].v = sy / 16;
        vw[k].x = pos[0]; vw[k].y = pos[1]; vw[k].z = pos[2]; vw[k].c = c; vw[k].u = sx / 16; vw[k].v = sy / 16;
        k++;
    }
    k = 0;
    for (L = 0; L < layers; L++) for (j = 0; j < gy; j++) for (i = 0; i < gx; i++) {
        int b = L * (gx + 1) * (gy + 1), a0 = b + j * (gx + 1) + i, a1 = a0 + 1, a2 = a0 + gx + 1, a3 = a2 + 1;
        int q[6] = { a0, a1, a2, a1, a3, a2 }, t;
        for (t = 0; t < 6; t++) { ix[k] = (WORD)q[t]; lt[k] = vt[q[t]]; lw[k] = vw[q[t]]; k++; }
    }
    chk(IDirect3DDevice9_CreateVertexBuffer(dev, sizeof(VT) * nv, D3DUSAGE_WRITEONLY, FVFT, D3DPOOL_MANAGED, &m->vbt_i, NULL), "CreateVB");
    chk(IDirect3DDevice9_CreateVertexBuffer(dev, sizeof(VW) * nv, D3DUSAGE_WRITEONLY, FVFW, D3DPOOL_MANAGED, &m->vbw_i, NULL), "CreateVB");
    chk(IDirect3DDevice9_CreateVertexBuffer(dev, sizeof(VT) * 3 * ntri, D3DUSAGE_WRITEONLY, FVFT, D3DPOOL_MANAGED, &m->vbt_l, NULL), "CreateVB");
    chk(IDirect3DDevice9_CreateVertexBuffer(dev, sizeof(VW) * 3 * ntri, D3DUSAGE_WRITEONLY, FVFW, D3DPOOL_MANAGED, &m->vbw_l, NULL), "CreateVB");
    chk(IDirect3DDevice9_CreateIndexBuffer(dev, sizeof(WORD) * 3 * ntri, D3DUSAGE_WRITEONLY, D3DFMT_INDEX16, D3DPOOL_MANAGED, &m->ib, NULL), "CreateIB");
    IDirect3DVertexBuffer9_Lock(m->vbt_i, 0, 0, &p, 0); memcpy(p, vt, sizeof(VT) * nv); IDirect3DVertexBuffer9_Unlock(m->vbt_i);
    IDirect3DVertexBuffer9_Lock(m->vbw_i, 0, 0, &p, 0); memcpy(p, vw, sizeof(VW) * nv); IDirect3DVertexBuffer9_Unlock(m->vbw_i);
    IDirect3DVertexBuffer9_Lock(m->vbt_l, 0, 0, &p, 0); memcpy(p, lt, sizeof(VT) * 3 * ntri); IDirect3DVertexBuffer9_Unlock(m->vbt_l);
    IDirect3DVertexBuffer9_Lock(m->vbw_l, 0, 0, &p, 0); memcpy(p, lw, sizeof(VW) * 3 * ntri); IDirect3DVertexBuffer9_Unlock(m->vbw_l);
    IDirect3DIndexBuffer9_Lock(m->ib, 0, 0, &p, 0); memcpy(p, ix, sizeof(WORD) * 3 * ntri); IDirect3DIndexBuffer9_Unlock(m->ib);
    m->nv = nv; m->ntri = ntri;
    free(vt); free(vw); free(ix); free(lt); free(lw);
}
static void build_texture(void) {
    D3DLOCKED_RECT lr; int x, y;
    chk(IDirect3DDevice9_CreateTexture(dev, 16, 16, 1, 0, D3DFMT_A8R8G8B8, D3DPOOL_MANAGED, &TEXA, NULL), "CreateTexture");
    IDirect3DTexture9_LockRect(TEXA, 0, &lr, NULL, 0);
    for (y = 0; y < 16; y++) for (x = 0; x < 16; x++) {
        int on = ((x / 4) + (y / 4)) & 1;
        ((DWORD *)((char *)lr.pBits + y * lr.Pitch))[x] = (on ? 0xFF000000 : 0x00000000) | 0x00F0F0F0;
    }
    IDirect3DTexture9_UnlockRect(TEXA, 0);
}
/* bind L like WoW would before its draw: vertex path, texture/alpha test */
static void bind_L(int shape, int path, int api, int alpha) {
    LMesh *m = &LM[shape];
    if (path == P_RHW) { chk(IDirect3DDevice9_SetFVF(dev, FVFT), "SetFVF"); IDirect3DDevice9_SetVertexShader(dev, NULL);
                         chk(IDirect3DDevice9_SetStreamSource(dev, 0, api ? m->vbt_l : m->vbt_i, 0, sizeof(VT)), "SetStreamSource"); }
    else {
        chk(IDirect3DDevice9_SetFVF(dev, FVFW), "SetFVF");
        chk(IDirect3DDevice9_SetStreamSource(dev, 0, api ? m->vbw_l : m->vbw_i, 0, sizeof(VW)), "SetStreamSource");
        if (path == P_XFORM) {
            D3DMATRIX id, pr; int i, j; memset(&id, 0, sizeof id); id._11 = id._22 = id._33 = id._44 = 1;
            for (i = 0; i < 4; i++) for (j = 0; j < 4; j++) pr.m[i][j] = MC[j][i];
            IDirect3DDevice9_SetVertexShader(dev, NULL);
            chk(IDirect3DDevice9_SetTransform(dev, D3DTS_WORLD, &id), "SetTransform"); chk(IDirect3DDevice9_SetTransform(dev, D3DTS_VIEW, &id), "SetTransform");
            chk(IDirect3DDevice9_SetTransform(dev, D3DTS_PROJECTION, &pr), "SetTransform");
        } else {
            chk(IDirect3DDevice9_SetVertexShader(dev, VS), "SetVS");
            chk(IDirect3DDevice9_SetVertexShaderConstantF(dev, 0, &MC[0][0], 4), "SetVSConst");
        }
    }
    if (!api) chk(IDirect3DDevice9_SetIndices(dev, m->ib), "SetIndices");
    if (alpha) {
        chk(IDirect3DDevice9_SetTexture(dev, 0, (IDirect3DBaseTexture9 *)TEXA), "SetTexture");
        TSS(0, D3DTSS_COLOROP, D3DTOP_MODULATE); TSS(0, D3DTSS_COLORARG1, D3DTA_TEXTURE); TSS(0, D3DTSS_COLORARG2, D3DTA_DIFFUSE);
        TSS(0, D3DTSS_ALPHAOP, D3DTOP_SELECTARG1); TSS(0, D3DTSS_ALPHAARG1, D3DTA_TEXTURE);
        SSS(0, D3DSAMP_MINFILTER, D3DTEXF_LINEAR); SSS(0, D3DSAMP_MAGFILTER, D3DTEXF_LINEAR);
        SSS(0, D3DSAMP_ADDRESSU, D3DTADDRESS_WRAP); SSS(0, D3DSAMP_ADDRESSV, D3DTADDRESS_WRAP);
        SRS(RS_ATEST, TRUE); SRS(RS_AREF, 0x80); SRS(RS_AFUNC, D3DCMP_GREATEREQUAL);
    } else {
        IDirect3DDevice9_SetTexture(dev, 0, NULL);
        TSS(0, D3DTSS_COLOROP, D3DTOP_SELECTARG1); TSS(0, D3DTSS_COLORARG1, D3DTA_DIFFUSE);
        TSS(0, D3DTSS_ALPHAOP, D3DTOP_SELECTARG1); TSS(0, D3DTSS_ALPHAARG1, D3DTA_DIFFUSE);
        SRS(RS_ATEST, FALSE);
    }
    if (shape == L_TRANS) { SRS(RS_ABLEND, TRUE); SRS(D3DRS_SRCBLEND, D3DBLEND_SRCALPHA); SRS(D3DRS_DESTBLEND, D3DBLEND_INVSRCALPHA); SRS(RS_ZWRITE, FALSE); }
    else { SRS(RS_ABLEND, FALSE); SRS(RS_ZWRITE, TRUE); }
    SRS(RS_ZFUNC, LESSEQUAL); SRS(RS_CWRITE, 0xF); SRS(RS_ZENABLE, TRUE);
}
static void draw_raw(int shape, int api) {   /* the hooked call: IDirect3DDevice9::DrawIndexedPrimitive / DrawPrimitive */
    LMesh *m = &LM[shape];
    if (!api) chk(IDirect3DDevice9_DrawIndexedPrimitive(dev, D3DPT_TRIANGLELIST, 0, 0, m->nv, 0, m->ntri), "DrawIndexedPrimitive");
    else chk(IDirect3DDevice9_DrawPrimitive(dev, D3DPT_TRIANGLELIST, 0, m->ntri), "DrawPrimitive");
}

/* ---------------- patch emulation ---------------- */
enum { ENC_PHYS, ENC_U };
static int ENC;
static int FIGV(void) { return ENC ? 0xC0 : 0x80; }
static int RINGV(int cat) { return ENC ? (0x40 | cat) : cat; }
/* d_mark: outlined part, mode 0 normal, 1 through walls, 2 only where hidden (KZ not emulated) */
static void marked(const V2D *v, int ntri, int cat, int mode) {
    int k;
    base2d();
    SRS(RS_SENABLE, 1); SRS(RS_SFUNC, ALWAYS); SRS(RS_SREF, FIGV()); SRS(RS_SPASS, REPLACE); SRS(RS_SFAIL, KEEP);
    SRS(RS_SZFAIL, mode ? REPLACE : KEEP); SRS(RS_SMASK, 0xFF); SRS(RS_SWMASK, 0xFF);
    dpup(v, ntri, 0, 0);
    if (mode == 0) {
        SRS(RS_SFUNC, EQUAL); SRS(RS_SREF, FIGV() | cat); SRS(RS_SMASK, 0x7F); SRS(RS_ZFUNC, ALWAYS);
        dpup(v, ntri, 0, 0);                                      /* second pass on ring pixels of the same unit */
        SRS(RS_ZFUNC, LESSEQUAL); SRS(RS_SMASK, 0xFF); SRS(RS_SFUNC, GREATER); SRS(RS_SREF, RINGV(cat));
        SRS(RS_CWRITE, 0); SRS(RS_ZWRITE, 1);
    } else {
        SRS(RS_SFUNC, GREATER); SRS(RS_SZFAIL, KEEP); SRS(RS_SREF, RINGV(cat)); SRS(RS_CWRITE, 0); SRS(RS_ZWRITE, 0);
        SRS(RS_ZFUNC, mode == 2 ? GREATER : ALWAYS);
    }
    for (k = 0; k < 8; k++) dpup(v, ntri, OFFS[k][0] * PX, OFFS[k][1] * PX);
    SRS(RS_CWRITE, 0xF); SRS(RS_ZWRITE, 1); SRS(RS_ZFUNC, LESSEQUAL);   /* WoW re-sends (dirty) */
    if (mode) SRS(RS_SZFAIL, KEEP);
    SRS(RS_SENABLE, 0);
}
enum { S_NONE, S_PROBE, S_CUR, S_S1, S_S2, S_S2LE, S_S3, NSCH };
static const char *SCHN[NSCH] = { "NONE", "PROBE", "CUR", "S1", "S2", "S2LE", "S3" };
static int WPROT;
/* state the SMODE branch of dip leaves for a depth-writing unmarked draw (persistent in the real patch) */
static void smode_on(int sch) {
    switch (sch) {
    case S_CUR: SRS(RS_SENABLE, 1); SRS(RS_SFUNC, LESS); SRS(RS_SREF, WPROT); SRS(RS_SPASS, ZERO); SRS(RS_SFAIL, KEEP);
                SRS(RS_SZFAIL, KEEP); SRS(RS_SMASK, 0xFF); SRS(RS_SWMASK, 0xFF); break;
    case S_S1: case S_S2: case S_S2LE:
                SRS(RS_SENABLE, 1); SRS(RS_SFUNC, ALWAYS); SRS(RS_SPASS, ZERO); SRS(RS_SFAIL, KEEP); SRS(RS_SZFAIL, KEEP);
                SRS(RS_SWMASK, 0xFF); break;
    case S_S3: SRS(RS_SENABLE, 1); SRS(RS_SFUNC, ALWAYS); SRS(RS_SPASS, ZERO); SRS(RS_SFAIL, KEEP); SRS(RS_SZFAIL, KEEP);
                SRS(RS_SWMASK, 0xC0); break;
    case S_PROBE: SRS(RS_SENABLE, 1); SRS(RS_SFUNC, ALWAYS); SRS(RS_SREF, 0xFF); SRS(RS_SPASS, REPLACE); SRS(RS_SFAIL, KEEP);
                SRS(RS_SZFAIL, KEEP); SRS(RS_SWMASK, 0xFF); break;
    default: SRS(RS_SENABLE, 0); break;
    }
}
/* one depth-writing unmarked draw through the (fixed) hook: scheme decides single or two passes */
static void later_draw(int sch, int shape, int api, int zfunc_orig) {
    if ((sch == S_S2 || sch == S_S2LE) && WPROT > 0) {
        SRS(RS_SENABLE, 0);
        draw_raw(shape, api);                                       /* pass 1: exactly as unpatched */
        SRS(RS_CWRITE, 0); SRS(RS_ZWRITE, 0); SRS(RS_ZFUNC, sch == S_S2 ? EQUAL : LESSEQUAL);
        SRS(RS_SENABLE, 1); SRS(RS_SFUNC, LESS); SRS(RS_SREF, WPROT); SRS(RS_SPASS, ZERO); SRS(RS_SFAIL, KEEP);
        SRS(RS_SZFAIL, KEEP); SRS(RS_SMASK, 0xFF); SRS(RS_SWMASK, 0xFF);
        draw_raw(shape, api);                                       /* pass 2: only stencil */
        SRS(RS_CWRITE, 0xF); SRS(RS_ZWRITE, 1); SRS(RS_ZFUNC, zfunc_orig); SRS(RS_SENABLE, 0);
        return;
    }
    smode_on(sch);
    draw_raw(shape, api);
}
static void unbind(void) {
    IDirect3DDevice9_SetVertexShader(dev, NULL); IDirect3DDevice9_SetTexture(dev, 0, NULL); SRS(RS_ATEST, FALSE); SRS(RS_ABLEND, FALSE);
    SRS(RS_SENABLE, 0); SRS(RS_ZWRITE, 1); SRS(RS_ZFUNC, LESSEQUAL); SRS(RS_CWRITE, 0xF);
}
/* post: one full-screen quad per category, STENCILFUNC EQUAL */
static void post(int ncat) {
    int c;
    base2d();
    SRS(RS_SENABLE, 1); SRS(RS_SFUNC, EQUAL); SRS(RS_SPASS, KEEP); SRS(RS_SFAIL, KEEP); SRS(RS_SZFAIL, KEEP); SRS(RS_SMASK, 0xFF);
    SRS(RS_ZFUNC, ALWAYS); SRS(RS_ZWRITE, 0); SRS(RS_ABLEND, 0); SRS(RS_ATEST, 0);
    for (c = ncat; c >= 1; c--) {
        SRS(RS_SREF, RINGV(c)); SRS(RS_SMASK, (ENC && c <= WPROT) ? 0x3F : 0xFF);
        fullquad(RINGCOL[c]);
    }
    SRS(RS_SMASK, 0xFF); SRS(RS_SENABLE, 0); SRS(RS_ZFUNC, LESSEQUAL); SRS(RS_ZWRITE, 1);
}

/* ---------------- readback ---------------- */
static void read_rt(IDirect3DSurface9 *src, uint32_t *out) {
    D3DLOCKED_RECT lr; int y; IDirect3DSurface9 *from = src;
    if (MS != D3DMULTISAMPLE_NONE) { chk(IDirect3DDevice9_StretchRect(dev, src, NULL, RES, NULL, D3DTEXF_NONE), "StretchRect"); from = RES; }
    chk(IDirect3DDevice9_GetRenderTargetData(dev, from, SYS), "GetRenderTargetData");
    chk(IDirect3DSurface9_LockRect(SYS, &lr, NULL, D3DLOCK_READONLY), "LockRect");
    for (y = 0; y < H; y++) memcpy(out + y * W, (char *)lr.pBits + y * lr.Pitch, W * 4);
    IDirect3DSurface9_UnlockRect(SYS);
    for (y = 0; y < NPIX; y++) out[y] |= 0xFF000000;
}
static void read_color(uint32_t *out) { read_rt(BB, out); }
static void read_stencil(uint8_t *out) {
    static uint32_t t[NPIX]; int b, i;
    chk(IDirect3DDevice9_SetRenderTarget(dev, 0, SRT), "SetRenderTarget SRT");
    begin();
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_TARGET, 0, 1.0f, 0), "Clear SRT");
    base2d();
    SRS(RS_ZENABLE, FALSE); SRS(RS_ZWRITE, FALSE); SRS(RS_ABLEND, TRUE); SRS(D3DRS_SRCBLEND, D3DBLEND_ONE); SRS(D3DRS_DESTBLEND, D3DBLEND_ONE);
    SRS(D3DRS_BLENDOP, D3DBLENDOP_ADD);
    SRS(RS_SENABLE, TRUE); SRS(RS_SFUNC, EQUAL); SRS(RS_SPASS, KEEP); SRS(RS_SFAIL, KEEP); SRS(RS_SZFAIL, KEEP); SRS(RS_SWMASK, 0);
    for (b = 0; b < 8; b++) { SRS(RS_SREF, 1u << b); SRS(RS_SMASK, 1u << b); fullquad(0xFF000000 | (1u << b)); }
    SRS(RS_ABLEND, FALSE); SRS(RS_SENABLE, FALSE); SRS(RS_ZENABLE, TRUE); SRS(RS_SWMASK, 0xFF); SRS(RS_SMASK, 0xFF);
    end();
    chk(IDirect3DDevice9_SetRenderTarget(dev, 0, BB), "SetRenderTarget BB");
    read_rt(SRT, t);
    for (i = 0; i < NPIX; i++) out[i] = (uint8_t)(t[i] & 0xFF);
}

/* ---------------- images ---------------- */
static void save_bmp(const char *name, const uint32_t *pix) {
    char fn[300]; FILE *f; int x, y, rowsz = W * 3; unsigned char hdr[54] = { 'B', 'M' }; unsigned char row[W * 3];
    snprintf(fn, sizeof fn, "%s/%s.bmp", outdir, name);
    *(DWORD *)(hdr + 2) = 54 + rowsz * H; *(DWORD *)(hdr + 10) = 54; *(DWORD *)(hdr + 14) = 40;
    *(LONG *)(hdr + 18) = W; *(LONG *)(hdr + 22) = H; *(WORD *)(hdr + 26) = 1; *(WORD *)(hdr + 28) = 24; *(DWORD *)(hdr + 34) = rowsz * H;
    f = fopen(fn, "wb"); if (!f) { printf("cannot write %s\n", fn); return; }
    fwrite(hdr, 54, 1, f);
    for (y = H; y-- > 0;) {
        for (x = 0; x < W; x++) { uint32_t c = pix[y * W + x]; row[3 * x] = c & 0xFF; row[3 * x + 1] = (c >> 8) & 0xFF; row[3 * x + 2] = (c >> 16) & 0xFF; }
        fwrite(row, rowsz, 1, f);
    }
    fclose(f);
}
static void save_raw8(const char *name, const uint8_t *s) {
    char fn[300]; FILE *f; snprintf(fn, sizeof fn, "%s/%s.s8", outdir, name);
    f = fopen(fn, "wb"); if (f) { fwrite(s, 1, NPIX, f); fclose(f); }
}

/* ---------------- checks ---------------- */
typedef struct { int miss_col, stc_err, final_err, n_p, n_p_bg, n_p_clear, n_p_prot, n_cur_drop, fin_vs_s2; } Res;
static uint32_t fS2[NPIX];
static uint32_t cref[NPIX], cA[NPIX], fA[NPIX], fexp[NPIX];
static uint8_t s0[NPIX], sA[NPIX], pm[NPIX];
static uint8_t expect_s(uint8_t s, int p) {
    if (!p) return s;
    if (ENC == ENC_PHYS) return s > WPROT ? 0 : s;
    return s & 0x3F;
}
static uint8_t phys_of(uint8_t s) {            /* value in the physical encoding that a U-encoded value stands for */
    if (ENC == ENC_PHYS || s == 0) return s;
    if (s & 0x80) return 0x80 | (s & 0x3F);
    if (s & 0x40) return s & 0x3F;
    return s <= WPROT ? s : 0;                  /* covered remnant: protected ring survives, others are gone */
}
static int post_cat(uint8_t s, int ncat) {     /* which ring quad colours this stencil value (as post does) */
    int c;                                     /* quads are drawn ncat..1, so the lowest matching category wins */
    for (c = 1; c <= ncat; c++) {
        int ref = RINGV(c), mask = (ENC && c <= WPROT) ? 0x3F : 0xFF;
        if ((ref & mask) == (s & mask)) return c;
    }
    return 0;
}

/* scene: clear, floor, wall, two outlined units A (cat 1) and B (cat 2) */
static int MODEA, MODEB;
static void scene(void) {
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER | D3DCLEAR_STENCIL, BG, 1.0f, 0), "Clear");
    base2d();
    dpup(floorR, 2, 0, 0);
    dpup(wallR, 2, 0, 0);
    marked(figA, NSEG, 1, MODEA);
    marked(figB, NSEG, 2, MODEB);
}
/* one run: scene, readback S0, L via scheme, readback colour + stencil, post, readback final */
static void run(int sch, int shape, int api, int path, int alpha, uint32_t *col, uint8_t *st0, uint8_t *st1, uint32_t *fin) {
    begin(); scene(); end();
    if (st0) read_stencil(st0);
    begin();
    bind_L(shape, path, api, alpha);
    if (sch == S_NONE) { SRS(RS_SENABLE, 0); draw_raw(shape, api); } else later_draw(sch, shape, api, LESSEQUAL);
    unbind();
    end();
    if (col) read_color(col);
    if (st1) read_stencil(st1);
    if (fin) { begin(); post(2); end(); read_color(fin); }
}
static int cmp32(const uint32_t *a, const uint32_t *b) { int i, n = 0; for (i = 0; i < NPIX; i++) n += a[i] != b[i]; return n; }

/* ---------------- tests ---------------- */
static void selftest_readback(void) {
    static uint8_t s[NPIX]; int i, bad = 0, v;
    begin();
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER | D3DCLEAR_STENCIL, BG, 1.0f, 0), "Clear");
    base2d(); SRS(RS_SENABLE, 1); SRS(RS_SFUNC, ALWAYS); SRS(RS_SPASS, REPLACE); SRS(RS_SWMASK, 0xFF); SRS(RS_ZENABLE, FALSE);
    for (v = 0; v < 256; v++) { V2D r[6]; mk_rect(r, (float)(v % 16) * 16 - 0.5f, (float)(v / 16) * 10 - 0.5f, (float)(v % 16) * 16 + 15.5f, (float)(v / 16) * 10 + 9.5f, 0.5f, 0xFF000000 | v);
                                SRS(RS_SREF, v); dpup(r, 2, 0, 0); }
    SRS(RS_SENABLE, 0); SRS(RS_ZENABLE, TRUE);
    end();
    read_stencil(s);
    for (i = 0; i < NPIX; i++) { int x = i % W, y = i / W, want = (y / 10) * 16 + x / 16; if (s[i] != want) bad++; }
    printf("SELFTEST stencil readback (256 values in 16x10 px cells): %d wrong pixels -> %s\n", bad, bad ? "FAILED" : "ok");
    if (bad) nerr++;
}
static void test_clear_masks(void) {
    static uint8_t s[NPIX]; static uint32_t c[NPIX]; int i, n = 0, nc = 0;
    begin();
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER | D3DCLEAR_STENCIL, BG, 1.0f, 0xFF), "Clear");
    SRS(RS_SWMASK, 0xC0); SRS(RS_CWRITE, 0);
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_STENCIL | D3DCLEAR_TARGET, 0xFF00FF00, 1.0f, 0), "Clear masked");
    SRS(RS_SWMASK, 0xFF); SRS(RS_CWRITE, 0xF);
    end();
    read_stencil(s); read_color(c);
    for (i = 0; i < NPIX; i++) { n += s[i] != 0; nc += c[i] != 0xFF00FF00; }
    printf("CLEAR with STENCILWRITEMASK 0xC0 (stencil 0xFF -> clear 0): %d pixels not 0 (first value 0x%02X) -> Clear %s the stencil write mask\n",
           n, s[0], n ? "HONOURS" : "IGNORES");
    printf("CLEAR with COLORWRITEENABLE 0: %d pixels not cleared -> Clear %s COLORWRITEENABLE\n", nc, nc ? "HONOURS" : "IGNORES");
}

static void test_clear_region(void) {
    static uint8_t s[NPIX]; int i, n_vp = 0, n_sc = 0; D3DVIEWPORT9 half = { 0, 0, W / 2, H, 0, 1 }, full = { 0, 0, W, H, 0, 1 }; RECT sc = { 0, 0, W / 4, H };
    begin();
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_STENCIL, 0, 1.0f, 0xFF), "Clear");
    chk(IDirect3DDevice9_SetViewport(dev, &half), "SetViewport");
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_STENCIL, 0, 1.0f, 0), "Clear vp");
    chk(IDirect3DDevice9_SetViewport(dev, &full), "SetViewport");
    end();
    read_stencil(s);
    for (i = 0; i < NPIX; i++) n_vp += s[i] == 0;
    begin();
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_STENCIL, 0, 1.0f, 0xFF), "Clear");
    chk(IDirect3DDevice9_SetScissorRect(dev, &sc), "SetScissorRect"); SRS(D3DRS_SCISSORTESTENABLE, TRUE);
    chk(IDirect3DDevice9_Clear(dev, 0, NULL, D3DCLEAR_STENCIL, 0, 1.0f, 0), "Clear sc");
    SRS(D3DRS_SCISSORTESTENABLE, FALSE);
    end();
    read_stencil(s);
    for (i = 0; i < NPIX; i++) n_sc += s[i] == 0;
    printf("CLEAR(STENCIL) with viewport = left half: %d of %d pixels cleared (%s); with scissor = left quarter: %d pixels cleared (%s)\n",
           n_vp, NPIX, n_vp == NPIX / 2 ? "limited to the viewport" : "whole surface", n_sc, n_sc == NPIX / 4 ? "limited to the scissor rect" : "not limited");
}
/* expected final image: post colours ring pixels of the expected stencil */
static void make_fexp(const uint32_t *col, const uint8_t *st, int ncat, uint32_t *out) {
    int i; for (i = 0; i < NPIX; i++) { int c = post_cat(st[i], ncat); out[i] = c ? RINGCOL[c] : col[i]; }
}

static FILE *csv;
static void matrix_tests(void) {
    int wp, sh, api, path, alpha, sch;
    static Res tot[2][NSCH][2];   /* [wprot][scheme][api] */
    memset(tot, 0, sizeof tot);
    printf("\n=== matrix: scene A cat 1 + B cat 2, later geometry L (DIP/DP, rhw/ffp/vs, alpha test off/on) ===\n");
    printf("columns: miss_col = pixels where colour after L differs from unpatched; stc_err = stencil after L != expected;\n"
           "         final_err = post image != expected; n_p = pixels where L passes depth (+alpha) test; of those on stencil 0 / cleared (>WPROT) / protected (1..WPROT)\n");
    for (wp = 0; wp <= 1; wp++) {
        WPROT = wp; MODEA = wp ? 1 : 0; MODEB = 0;
        for (sh = L_GRAD; sh <= L_GRID; sh++) for (path = 0; path < 3; path++) for (alpha = 0; alpha <= 1; alpha++) for (api = 0; api <= 1; api++) {
            char tag[128];
            if (sh == L_GRID && path == P_RHW) continue;
            ENC = ENC_PHYS;
            run(S_NONE, sh, api, path, alpha, cref, NULL, NULL, NULL);
            run(S_PROBE, sh, api, path, alpha, NULL, NULL, pm, NULL);
            {   ENC = ENC_PHYS; run(S_S2, sh, api, path, alpha, NULL, NULL, NULL, fS2); }
            for (sch = S_CUR; sch < NSCH; sch++) {
                Res r; int i;
                memset(&r, 0, sizeof r);
                ENC = sch == S_S3 ? ENC_U : ENC_PHYS;
                run(sch, sh, api, path, alpha, cA, s0, sA, fA);
                for (i = 0; i < NPIX; i++) {
                    int p = pm[i] == 0xFF;
                    uint8_t e = expect_s(s0[i], p);
                    r.miss_col += cA[i] != cref[i];
                    r.stc_err += sA[i] != e;
                    if (p) { uint8_t q = phys_of(s0[i]); r.n_p++; if (q == 0) r.n_p_bg++; else if (q > WPROT) r.n_p_clear++; else r.n_p_prot++; }
                }
                {   /* expected final: post over unpatched colour and expected stencil */
                    static uint8_t ex[NPIX]; for (i = 0; i < NPIX; i++) ex[i] = expect_s(s0[i], pm[i] == 0xFF);
                    make_fexp(cref, ex, 2, fexp); r.final_err = cmp32(fA, fexp);
                }
                r.fin_vs_s2 = cmp32(fA, fS2);
                snprintf(tag, sizeof tag, "w%d_%s_%s_%s_a%d_%s", wp, LSHN[sh], api ? "DP" : "DIP", PATHN[path], alpha, SCHN[sch]);
                fprintf(csv, "%s,%d,%d,%d,%d,%d,%d,%d,%d\n", tag, r.miss_col, r.stc_err, r.final_err, r.n_p, r.n_p_bg, r.n_p_clear, r.n_p_prot, r.fin_vs_s2);
                {
                    Res *t = &tot[wp][sch][api];
                    t->miss_col += r.miss_col; t->stc_err += r.stc_err; t->final_err += r.final_err; t->n_p += r.n_p;
                    t->n_p_bg += r.n_p_bg; t->n_p_clear += r.n_p_clear; t->n_p_prot += r.n_p_prot; t->n_cur_drop++; t->fin_vs_s2 += r.fin_vs_s2;
                }
                if (sh == L_GRAD && path == P_VS && (alpha == 1 || sch == S_CUR)) {
                    char n[160];
                    snprintf(n, sizeof n, "%s_after", tag); save_bmp(n, cA);
                    snprintf(n, sizeof n, "%s_final", tag); save_bmp(n, fA);
                    snprintf(n, sizeof n, "%s_s0", tag); save_raw8(n, s0);
                    snprintf(n, sizeof n, "%s_s1", tag); save_raw8(n, sA);
                }
            }
            if (sh == L_GRAD && path == P_VS) {
                char n[160]; snprintf(n, sizeof n, "w%d_%s_%s_%s_a%d_REF", wp, LSHN[sh], api ? "DP" : "DIP", PATHN[path], alpha); save_bmp(n, cref);
                snprintf(n, sizeof n, "w%d_%s_%s_%s_a%d_P", wp, LSHN[sh], api ? "DP" : "DIP", PATHN[path], alpha); save_raw8(n, pm);
            }
        }
    }
    printf("\nTOTALS over all L shapes/paths/alpha (sums of pixel counts)\n");
    printf("%-5s %-6s %-4s %10s %10s %10s %10s %10s %10s %10s %10s %6s\n", "WPROT", "scheme", "api", "miss_col", "stc_err", "final_err", "fin_vs_S2", "n_p", "p_on_bg", "p_clear", "p_prot", "runs");
    for (wp = 0; wp <= 1; wp++) for (sch = S_CUR; sch < NSCH; sch++) for (api = 0; api <= 1; api++) {
        Res *t = &tot[wp][sch][api];
        printf("%-5d %-6s %-4s %10d %10d %10d %10d %10d %10d %10d %10d %6d\n", wp, SCHN[sch], api ? "DP" : "DIP", t->miss_col, t->stc_err, t->final_err,
               t->fin_vs_s2, t->n_p, t->n_p_bg, t->n_p_clear, t->n_p_prot, t->n_cur_drop);
    }
}

/* multi-part: after L, unit B draws a second part (weapon) and unit C (cat 3) is drawn in front of L, then a second L;
   S3 (U encoding) must give the same final image as the physical scheme (S1 for WPROT 0, S2 for WPROT 1) */
static void multipart(int sch, int api, int path, int alpha, uint32_t *col, uint32_t *fin, uint8_t *st) {
    begin(); scene();
    bind_L(L_GRAD, path, api, alpha);
    if (sch == S_NONE) { SRS(RS_SENABLE, 0); draw_raw(L_GRAD, api); } else later_draw(sch, L_GRAD, api, LESSEQUAL);
    unbind();
    marked(weapB, 2, 2, 0);
    marked(figC, NSEG, 3, 0);
    bind_L(L_OP2, path, api, alpha);
    if (sch == S_NONE) { SRS(RS_SENABLE, 0); draw_raw(L_OP2, api); } else later_draw(sch, L_OP2, api, LESSEQUAL);
    unbind();
    end();
    read_color(col);
    if (st) read_stencil(st);
    begin(); post(3); end();
    read_color(fin);
}
static void multipart_tests(void) {
    static uint32_t cN[NPIX], fN[NPIX], cP[NPIX], fP[NPIX], cX[NPIX], fX[NPIX]; int wp, api, path, alpha;
    printf("\n=== multi-part: L, then B's second part + unit C (cat 3) in front of L, then a second L; post with 3 categories ===\n");
    for (wp = 0; wp <= 1; wp++) for (path = 0; path < 3; path++) for (alpha = 0; alpha <= 1; alpha++) for (api = 0; api <= 1; api++) {
        int phys = wp ? S_S2 : S_S1, dc, dcu, df, dfc;
        WPROT = wp; MODEA = wp ? 1 : 0; MODEB = 0;
        ENC = ENC_PHYS; multipart(S_NONE, api, path, alpha, cN, fN, NULL);
        ENC = ENC_PHYS; multipart(phys, api, path, alpha, cP, fP, NULL);
        dc = cmp32(cP, cN);
        ENC = ENC_U; multipart(S_S3, api, path, alpha, cX, fX, NULL);
        dcu = cmp32(cX, cN); df = cmp32(fX, fP);
        ENC = ENC_PHYS; { static uint32_t cC[NPIX], fC[NPIX]; multipart(S_CUR, api, path, alpha, cC, fC, NULL); dfc = cmp32(cC, cN);
            if (path == P_VS && alpha == 1) { char n[96];
                snprintf(n, sizeof n, "mp_w%d_%s_CUR_final", wp, api ? "DP" : "DIP"); save_bmp(n, fC); } }
        printf("WPROT %d %-3s %-3s alpha %d: colour vs unpatched: %s %d px, S3 %d px, CUR %d px | final image S3 vs %s: %d px differ\n",
               wp, api ? "DP" : "DIP", PATHN[path], alpha, SCHN[phys], dc, dcu, dfc, SCHN[phys], df);
        if (path == P_VS && alpha == 1) {
            char n[96];
            snprintf(n, sizeof n, "mp_w%d_%s_REF", wp, api ? "DP" : "DIP"); save_bmp(n, cN);
            snprintf(n, sizeof n, "mp_w%d_%s_%s_final", wp, api ? "DP" : "DIP", SCHN[phys]); save_bmp(n, fP);
            snprintf(n, sizeof n, "mp_w%d_%s_S3_final", wp, api ? "DP" : "DIP"); save_bmp(n, fX);
        }
    }
}

/* bug B: DrawPrimitive at 0x6A3706 is not hooked and inherits the stencil state the last DIP left */
static int SMODE;
static void hook(int sch, int hooked, int shape, int api, int zwrite) {
    /* dip/dp hook for an unmarked draw with MARKED=1, walls off; zwrite = WoW's cached ZWRITE [CGx+0x3E70] */
    if (hooked) {
        if (zwrite != SMODE) { SMODE = zwrite; if (zwrite) smode_on(sch); else SRS(RS_SENABLE, 0); }
    }
    draw_raw(shape, api);
}
static void test_bugB(void) {
    static uint32_t ref[NPIX], c[NPIX], f[NPIX]; static uint8_t st[NPIX], st0[NPIX], pr[NPIX];
    int v, i;
    const char *vn[4] = { "REF (no stencil)", "CUR: DIP hooked (LESS ref 0), DP not hooked", "S1 on DIP only, DP not hooked", "S1 on DIP and DP (both hooked)" };
    printf("\n=== bug B: sequence after the outlined units: d1 DIP opaque small (ZWRITE 1), d2 DP transparent (ZWRITE 0, blended), d3 DP opaque (ZWRITE 1) ===\n");
    WPROT = 0; MODEA = 0; MODEB = 0; ENC = ENC_PHYS;
    /* probe for d3 only: where d3 is in front */
    begin(); scene();
    bind_L(L_SMALL, P_VS, 0, 0); draw_raw(L_SMALL, 0); unbind();
    bind_L(L_TRANS, P_VS, 1, 0); draw_raw(L_TRANS, 1); unbind();
    bind_L(L_OP2, P_VS, 1, 0); smode_on(S_PROBE); draw_raw(L_OP2, 1); unbind();
    end(); read_stencil(pr);
    for (v = 0; v < 4; v++) {
        int sch = v == 1 ? S_CUR : S_S1, dpk = v == 3, n_err = 0, n_trans_clear = 0, n_d3_kept = 0;
        begin(); scene(); end(); read_stencil(st0);
        begin();
        SMODE = 0;
        bind_L(L_SMALL, P_VS, 0, 0); if (v == 0) draw_raw(L_SMALL, 0); else hook(sch, 1, L_SMALL, 0, 1);
        bind_L(L_TRANS, P_VS, 1, 0); if (v == 0) draw_raw(L_TRANS, 1); else hook(sch, dpk, L_TRANS, 1, 0);
        bind_L(L_OP2, P_VS, 1, 0); if (v == 0) draw_raw(L_OP2, 1); else hook(sch, dpk, L_OP2, 1, 1);
        unbind();
        end();
        read_color(c); read_stencil(st);
        begin(); post(2); end(); read_color(f);
        if (v == 0) memcpy(ref, c, sizeof ref);
        for (i = 0; i < NPIX; i++) {
            int in3 = pr[i] == 0xFF; uint8_t e = in3 ? (st0[i] > 0 ? 0 : st0[i]) : st0[i];
            if (v) n_err += st[i] != e;
            if (!in3 && st0[i] && st[i] == 0) n_trans_clear++;
            if (in3 && st0[i] && st[i]) n_d3_kept++;
        }
        printf("variant %d %-46s colour differs from REF: %6d px | stencil: outline cleared under the transparent d2 only: %4d px, outline kept under opaque d3 in front: %4d px, stencil != ideal: %4d px\n",
               v, vn[v], cmp32(c, ref), n_trans_clear, v ? n_d3_kept : 0, v ? n_err : 0);
        { char n[64]; snprintf(n, sizeof n, "bugB_v%d_after", v); save_bmp(n, c); snprintf(n, sizeof n, "bugB_v%d_final", v); save_bmp(n, f);
          snprintf(n, sizeof n, "bugB_v%d_s1", v); save_raw8(n, st); }
    }
}

static LRESULT CALLBACK wndproc(HWND h, UINT m, WPARAM w, LPARAM l) { return DefWindowProcA(h, m, w, l); }
int main(int argc, char **argv) {
    D3DPRESENT_PARAMETERS pp; WNDCLASSA wc; RECT r = { 0, 0, W, H }; HRESULT hr; D3DADAPTER_IDENTIFIER9 id; char fn[300];
    MS = argc > 1 ? (D3DMULTISAMPLE_TYPE)atoi(argv[1]) : D3DMULTISAMPLE_NONE;
    if (argc > 2) snprintf(outdir, sizeof outdir, "%s", argv[2]);
    setvbuf(stdout, NULL, _IONBF, 0);
    memset(&wc, 0, sizeof wc); wc.lpfnWndProc = wndproc; wc.hInstance = GetModuleHandleA(NULL); wc.lpszClassName = "stenciltest";
    RegisterClassA(&wc); AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW, FALSE);
    hwnd = CreateWindowA("stenciltest", "stenciltest", WS_OVERLAPPEDWINDOW | WS_VISIBLE, 0, 0, r.right - r.left, r.bottom - r.top, NULL, NULL, wc.hInstance, NULL);
    d3d = Direct3DCreate9(D3D_SDK_VERSION); if (!d3d) { printf("Direct3DCreate9 failed\n"); return 1; }
    IDirect3D9_GetAdapterIdentifier(d3d, 0, 0, &id);
    printf("stenciltest: %ux%u, multisample %d, adapter '%s' / '%s'\n", W, H, MS, id.Description, id.Driver);
    memset(&pp, 0, sizeof pp);
    pp.BackBufferWidth = W; pp.BackBufferHeight = H; pp.BackBufferFormat = D3DFMT_X8R8G8B8; pp.BackBufferCount = 1;
    pp.MultiSampleType = MS; pp.SwapEffect = D3DSWAPEFFECT_DISCARD; pp.hDeviceWindow = hwnd; pp.Windowed = TRUE;
    pp.EnableAutoDepthStencil = TRUE; pp.AutoDepthStencilFormat = D3DFMT_D24S8; pp.PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE;
    hr = IDirect3D9_CreateDevice(d3d, 0, D3DDEVTYPE_HAL, hwnd, D3DCREATE_HARDWARE_VERTEXPROCESSING, &pp, &dev);
    if (FAILED(hr)) { printf("CreateDevice failed 0x%08lX\n", (unsigned long)hr); return 1; }
    chk(IDirect3DDevice9_GetBackBuffer(dev, 0, 0, D3DBACKBUFFER_TYPE_MONO, &BB), "GetBackBuffer");
    chk(IDirect3DDevice9_GetDepthStencilSurface(dev, &DS), "GetDepthStencilSurface");
    chk(IDirect3DDevice9_CreateRenderTarget(dev, W, H, D3DFMT_X8R8G8B8, MS, 0, FALSE, &SRT, NULL), "CreateRenderTarget SRT");
    chk(IDirect3DDevice9_CreateRenderTarget(dev, W, H, D3DFMT_X8R8G8B8, D3DMULTISAMPLE_NONE, 0, FALSE, &RES, NULL), "CreateRenderTarget RES");
    chk(IDirect3DDevice9_CreateOffscreenPlainSurface(dev, W, H, D3DFMT_X8R8G8B8, D3DPOOL_SYSTEMMEM, &SYS, NULL), "CreateOffscreenPlainSurface");
    chk(IDirect3DDevice9_CreateVertexShader(dev, VS11, &VS), "CreateVertexShader");
    setup_matrices();
    { int s; for (s = 0; s < NLSH; s++) build_mesh(s); }
    build_texture();
    mk_ellipse(figA, 75, 78, 26, 42, 0.5f, FIGAC);
    mk_ellipse(figB, 150, 80, 30, 40, 0.5f, FIGBC);
    mk_ellipse(figC, 110, 66, 12, 12, 0.2f, FIGCC);
    mk_rect(weapB, 118, 40, 128, 110, 0.45f, WEAPC);
    mk_rect(wallR, 40, 20, 80, 60, 0.35f, WALLC);
    mk_rect(floorR, -0.5f, 100, W - 0.5f, H - 0.5f, 0.8f, FLOORC);
    snprintf(fn, sizeof fn, "%s/matrix.csv", outdir); csv = fopen(fn, "w");
    if (csv) fprintf(csv, "case,miss_col,stc_err,final_err,n_p,n_p_bg,n_p_clear,n_p_prot,fin_vs_s2\n");
    if (MS == D3DMULTISAMPLE_NONE) selftest_readback();
    test_clear_masks();
    test_clear_region();
    matrix_tests();
    multipart_tests();
    test_bugB();
    if (csv) fclose(csv);
    IDirect3DDevice9_Present(dev, NULL, NULL, NULL, NULL);
    printf("\nSUMMARY api errors %d\n", nerr);
    return nerr ? 2 : 0;
}
