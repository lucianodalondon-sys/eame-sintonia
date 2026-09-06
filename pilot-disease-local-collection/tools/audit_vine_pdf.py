import re, sys, hashlib, os

def analyze(path):
    d = open(path, 'rb').read()
    out = {}
    out['bytes'] = len(d)
    out['sha256'] = hashlib.sha256(d).hexdigest()
    out['header'] = d[:8].decode('latin-1')
    ids = re.findall(rb'/ID\s*\[\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\]', d)
    out['ID'] = [(a.decode(), b.decode()) for a, b in ids]
    out['n_Type_Page'] = len(re.findall(rb'/Type\s*/Page[^s]', d))
    out['n_Type_Pages'] = len(re.findall(rb'/Type\s*/Pages', d))
    cnt = re.findall(rb'/Type\s*/Pages.{0,300}?/Count\s+(\d+)', d, re.S)
    out['Pages_Count'] = [int(c) for c in cnt]
    info = re.findall(
        rb'/(Title|Author|Subject|Creator|Producer|CreationDate|ModDate)\s*(\([^)]*\)|<[0-9A-Fa-f]+>)', d)
    out['info_pairs'] = [(k.decode(), v.decode('latin-1')) for k, v in info]
    out['n_Subtype_Image'] = len(re.findall(rb'/Subtype\s*/Image', d))
    out['n_Subtype_Form'] = len(re.findall(rb'/Subtype\s*/Form', d))
    out['n_DCTDecode'] = len(re.findall(rb'/DCTDecode', d))
    out['n_Type_Font'] = len(re.findall(rb'/Type\s*/Font', d))
    out['n_FontFile'] = len(re.findall(rb'/FontFile', d))
    out['n_Annots'] = len(re.findall(rb'/Annots', d))
    out['n_ObjStm'] = len(re.findall(rb'/Type\s*/ObjStm', d))
    out['MediaBox'] = [m.decode() for m in re.findall(rb'/MediaBox\s*\[([^\]]*)\]', d)][:4]
    return out

for p in sys.argv[1:]:
    print("=" * 70)
    print(os.path.basename(p))
    r = analyze(p)
    for k, v in r.items():
        print("  %s: %s" % (k, v))
