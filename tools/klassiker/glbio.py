"""Minimaler GLB-Leser/-Schreiber (numpy) für die Klassiker-Autos."""
import json, struct, io
import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def read_glb(path):
    b = open(path, 'rb').read(); assert b[:4] == b'glTF'
    off, js, bn = 12, None, b''
    while off < len(b):
        ln, ty = struct.unpack_from('<II', b, off); d = b[off + 8:off + 8 + ln]; off += 8 + ln
        if ty == 0x4E4F534A: js = json.loads(d)
        elif ty == 0x004E4942: bn = d
    return js, bn


def accessor(js, bn, i):
    a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
    dt = np.dtype(CT[a['componentType']]); nc = NC[a['type']]; cnt = a['count']
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0); stride = bv.get('byteStride', 0) or dt.itemsize * nc
    rows = np.frombuffer(bn, np.uint8, count=stride * (cnt - 1) + dt.itemsize * nc, offset=off)
    if stride != dt.itemsize * nc:
        rows = np.lib.stride_tricks.as_strided(rows, (cnt, dt.itemsize * nc), (stride, 1)).copy()
    arr = np.ascontiguousarray(rows).view(dt).reshape(cnt, nc) if nc > 1 else np.ascontiguousarray(rows).view(dt)
    if a.get('normalized'):
        m = {np.int8: 127, np.uint8: 255, np.int16: 32767, np.uint16: 65535}[CT[a['componentType']]]
        arr = np.maximum(arr.astype(np.float32) / m, -1)
    return np.array(arr)


def image_bytes(js, bn, img_i):
    im = js['images'][img_i]; bv = js['bufferViews'][im['bufferView']]
    o = bv.get('byteOffset', 0); return bn[o:o + bv['byteLength']]


def node_matrix(n):
    if 'matrix' in n: return np.array(n['matrix'], np.float64).reshape(4, 4).T
    t = np.array(n.get('translation', [0, 0, 0]), np.float64); r = n.get('rotation', [0, 0, 0, 1]); s = np.array(n.get('scale', [1, 1, 1]), np.float64)
    x, y, z, w = r
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4); M[:3, :3] = R * s; M[:3, 3] = t; return M


def flatten(js, bn):
    """Alle Dreiecks-Primitive in Weltkoordinaten: Liste von dict(pos, nrm, uv, idx, mat, name, col)."""
    out = []; nodes = js.get('nodes', [])
    roots = js['scenes'][js.get('scene', 0)]['nodes']

    def walk(i, M):
        n = nodes[i]; W = M @ node_matrix(n)
        if 'mesh' in n:
            for p in js['meshes'][n['mesh']]['primitives']:
                if p.get('mode', 4) != 4: continue
                at = p['attributes']; P = accessor(js, bn, at['POSITION']).astype(np.float64)
                P = P @ W[:3, :3].T + W[:3, 3]
                N = None
                if 'NORMAL' in at:
                    N = accessor(js, bn, at['NORMAL']).astype(np.float64) @ np.linalg.inv(W[:3, :3])
                    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
                mat = js['materials'][p['material']] if 'material' in p else {}
                tc = mat.get('pbrMetallicRoughness', {}).get('baseColorTexture', {}).get('texCoord', 0)
                key = 'TEXCOORD_%d' % tc
                UV = accessor(js, bn, at[key]).astype(np.float64) if key in at else np.zeros((len(P), 2))
                I = accessor(js, bn, p['indices']).astype(np.int64).reshape(-1, 3) if 'indices' in p else np.arange(len(P)).reshape(-1, 3)
                if np.linalg.det(W[:3, :3]) < 0: I = I[:, ::-1]
                C = accessor(js, bn, at['COLOR_0'])[:, :3].astype(np.float64) if 'COLOR_0' in at else None
                out.append(dict(pos=P, nrm=N, uv=UV, idx=I, mat=p.get('material', -1), name=n.get('name', ''), col=C))
        for c in n.get('children', []): walk(c, W)
    for r in roots: walk(r, np.eye(4))
    return out


class GLBWriter:
    def __init__(self):
        self.js = {'asset': {'version': '2.0', 'generator': 'F1Racing tools/klassiker'}, 'scene': 0, 'scenes': [{'nodes': []}],
                   'nodes': [], 'meshes': [], 'materials': [], 'textures': [], 'images': [], 'samplers': [],
                   'accessors': [], 'bufferViews': [], 'buffers': []}
        self.bin = io.BytesIO()

    def _view(self, data, target=None):
        while self.bin.tell() % 4: self.bin.write(b'\0')
        o = self.bin.tell(); self.bin.write(data)
        v = {'buffer': 0, 'byteOffset': o, 'byteLength': len(data)}
        if target: v['target'] = target
        self.js['bufferViews'].append(v); return len(self.js['bufferViews']) - 1

    def acc(self, arr, kind, target=None, minmax=False, normalized=False):
        arr = np.ascontiguousarray(arr)
        ct = {np.dtype(np.float32): 5126, np.dtype(np.uint16): 5123, np.dtype(np.uint32): 5125, np.dtype(np.int8): 5120,
              np.dtype(np.int16): 5122, np.dtype(np.uint8): 5121}[arr.dtype]
        a = {'bufferView': self._view(arr.tobytes(), target), 'componentType': ct, 'count': int(arr.shape[0]), 'type': kind}
        if normalized: a['normalized'] = True
        if minmax: a['min'] = arr.min(0).astype(float).tolist(); a['max'] = arr.max(0).astype(float).tolist()
        self.js['accessors'].append(a); return len(self.js['accessors']) - 1

    def image(self, data, mime, name=None):
        im = {'bufferView': self._view(data), 'mimeType': mime}
        if name: im['name'] = name
        self.js['images'].append(im); return len(self.js['images']) - 1

    def texture(self, img, repeat=True):
        if not self.js['samplers']:
            self.js['samplers'] += [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497},
                                    {'magFilter': 9729, 'minFilter': 9987, 'wrapS': 33071, 'wrapT': 33071}]
        self.js['textures'].append({'source': img, 'sampler': 0 if repeat else 1}); return len(self.js['textures']) - 1

    def material(self, m):
        self.js['materials'].append(m); return len(self.js['materials']) - 1

    def mesh(self, name, prims):
        self.js['meshes'].append({'name': name, 'primitives': prims}); return len(self.js['meshes']) - 1

    def node(self, n, root=True):
        self.js['nodes'].append(n); i = len(self.js['nodes']) - 1
        if root: self.js['scenes'][0]['nodes'].append(i)
        return i

    def save(self, path):
        for k in ['textures', 'images', 'samplers', 'materials']:
            if not self.js[k]: del self.js[k]
        b = self.bin.getvalue()
        while len(b) % 4: b += b'\0'
        self.js['buffers'] = [{'byteLength': len(b)}]
        j = json.dumps(self.js, separators=(',', ':')).encode()
        while len(j) % 4: j += b' '
        with open(path, 'wb') as f:
            f.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(b)))
            f.write(struct.pack('<II', len(j), 0x4E4F534A)); f.write(j)
            f.write(struct.pack('<II', len(b), 0x004E4942)); f.write(b)
