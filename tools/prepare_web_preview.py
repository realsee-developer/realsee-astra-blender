"""Create a compact web GLB using only the reviewed public USDZ.

Run with Python 3.11+ and Pillow from any directory. Blender is discovered on PATH.
The detailed Blender projects and original USDZ are never modified.
"""
from pathlib import Path
import hashlib
import json
import io
import struct
import shutil
import subprocess
import sys
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'artifacts/reconstruction_physics_v1.usdz'
OUTPUT = ROOT / 'artifacts/reconstruction_web.glb'
REPORT = ROOT / 'output/web-preview/preparation.json'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def prepare():
    import bpy
    from mathutils import Vector
    from pxr import Usd, UsdGeom

    manifest = json.loads((ROOT / 'artifacts/manifest.json').read_text())
    expected = next(a['sha256'] for a in manifest['assets'] if a['file'] == SOURCE.name)
    source_sha = digest(SOURCE)
    if source_sha != expected:
        raise ValueError('Public USDZ does not match the reviewed artifact manifest')
    # USD import can merge a transform into its child mesh and use the mesh
    # name. Classify against the USD path before those architectural names go.
    roof_prefixes = ('CEILING_', 'PLENUM_', 'FAS_CEILING_TRACK_', 'GRID_CORRIDOR_', 'GRID_BAR_')
    reference_prefixes = ('REFERENCE_SCAN', 'SOURCE_SCAN', 'SCAN_REFERENCE')
    structural_prefixes = ('WALL_', 'FLOOR_', 'DOOR_', 'WINDOW_', 'COLUMN_', 'BEAM_', 'STRUCTURE_')
    stage = Usd.Stage.Open(str(SOURCE))
    hidden_names, structural_names = set(), set()
    source_meshes = source_polygons = 0
    for prim in stage.Traverse():
        if not prim.IsA(UsdGeom.Mesh):
            continue
        source_meshes += 1
        source_polygons += len(UsdGeom.Mesh(prim).GetFaceVertexCountsAttr().Get())
        chain = str(prim.GetPath()).upper().split('/')
        if any(n.startswith(roof_prefixes + reference_prefixes) for n in chain):
            hidden_names.add(prim.GetName())
        if any(n.startswith(structural_prefixes) for n in chain):
            structural_names.add(prim.GetName())
    del stage
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.usd_import(
        filepath=str(SOURCE), import_visible_only=True,
        import_cameras=False, import_lights=False, import_curves=False,
        import_points=False, import_volumes=False, import_skeletons=False,
        import_blendshapes=False, import_textures_mode='IMPORT_PACK',
    )
    bpy.context.scene.frame_set(1)
    report = {
        'source': SOURCE.relative_to(ROOT).as_posix(), 'source_sha256': source_sha,
        'source_bytes': SOURCE.stat().st_size, 'blender_version': bpy.app.version_string,
        'derivation': 'Public USDZ only; cutaway roof; reduced dense detail and textures; Draco GLB',
        'imported_meshes': sum(o.type == 'MESH' for o in bpy.data.objects),
        'hidden': [], 'simplified': [], 'textures': [],
        'hidden_prefixes': list(roof_prefixes + reference_prefixes),
        'structural_prefixes_preserved': list(structural_prefixes),
        'source_meshes': source_meshes, 'source_polygons': source_polygons,
    }
    meshes = []
    for obj in list(bpy.data.objects):
        if obj.type != 'MESH':
            continue
        chain = []
        node = obj
        while node:
            chain.append(node.name.upper())
            node = node.parent
        if obj.name in hidden_names or any(n.startswith(roof_prefixes + reference_prefixes) for n in chain):
            obj.hide_render = True
            obj.hide_set(True)
            report['hidden'].append(obj.name)
            continue
        obj.hide_render = False
        obj.hide_set(False)
        meshes.append(obj)
        count = len(obj.data.polygons)
        if count > 300 and obj.name not in structural_names and not any(n.startswith(structural_prefixes) for n in chain):
            target = min(1500, max(120, int(count * 0.10)))
            modifier = obj.modifiers.new('Web preview detail reduction', 'DECIMATE')
            modifier.ratio = target / count
            report['simplified'].append({'name': obj.name, 'source_faces': count, 'ratio': modifier.ratio})
    bpy.context.view_layer.update()
    bounds = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    report['source_visible_bounds_z_up'] = {
        'min': [min(v[i] for v in bounds) for i in range(3)],
        'max': [max(v[i] for v in bounds) for i in range(3)],
    }
    report['retained_meshes'] = len(meshes)
    report['retained_source_faces'] = sum(len(o.data.polygons) for o in meshes)
    used_materials = {m for obj in meshes for m in obj.data.materials if m}
    used_images = {node.image for mat in used_materials if mat.use_nodes
                   for node in mat.node_tree.nodes if node.type == 'TEX_IMAGE' and node.image}
    for image in used_images:
        before = list(image.size)
        if not all(before):
            raise ValueError(f'Missing source image: {image.name}')
        limit = 1024 if 'floor' in image.name.lower() else 512
        factor = min(1, limit / max(before))
        if factor < 1:
            image.scale(max(1, round(before[0] * factor)), max(1, round(before[1] * factor)))
        report['textures'].append({'name': image.name, 'before': before, 'after': list(image.size)})
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    # A web preview does not need thousands of independently transformed
    # detail nodes. Apply detail reduction, then batch the meshes by material.
    # The original USDZ remains the downloadable component/physics source.
    bpy.ops.object.convert(target='MESH')
    report['simplified_faces'] = sum(len(o.data.polygons) for o in bpy.context.selected_objects if o.type == 'MESH')
    report['structural_meshes_preserved'] = len(structural_names)
    bpy.ops.object.join()
    bpy.context.object.name = 'Public_USDZ_Space_Preview'
    report['materials'] = len(used_materials)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2))
    print('WEB_PREVIEW_EXPORT', json.dumps({k:report[k] for k in ('imported_meshes','retained_meshes','retained_source_faces','materials')}), flush=True)
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT), export_format='GLB', use_selection=True,
        export_apply=True, export_animations=False, export_cameras=False,
        export_lights=False, export_extras=False, export_yup=True,
        export_image_format='AUTO', export_image_quality=75,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_texcoord_quantization=12,
        export_draco_normal_quantization=10,
    )
    report['output'] = OUTPUT.relative_to(ROOT).as_posix()
    report['output_bytes'] = OUTPUT.stat().st_size
    report['output_sha256'] = digest(OUTPUT)
    if digest(SOURCE) != source_sha:
        raise ValueError('Source changed during preview preparation')
    REPORT.write_text(json.dumps(report, indent=2))
    print('WEB_PREVIEW_READY', report['output_bytes'], report['output_sha256'], flush=True)


def normalize_uvs(document):
    """Keep each primitive's sampled UV data, with channels supported by Three.

    Joining Blender meshes unions UV layer names. This can export TEXCOORD_6
    even when a material samples only one layer. Rename its accessor semantic
    and Draco attribute semantic together; neither coordinate values nor Draco
    attribute IDs change. Material variants are keyed by their channel mapping.
    """
    def texture_slots(value):
        for key, item in value.items():
            if isinstance(item, dict):
                if key.endswith('Texture') and 'index' in item:
                    yield item
                else:
                    yield from texture_slots(item)

    def channel(slot):
        return slot.get('extensions', {}).get('KHR_texture_transform', {}).get(
            'texCoord', slot.get('texCoord', 0))

    originals = document.get('materials', [])
    materials, variants, records = [], {}, []
    for mesh in document.get('meshes', []):
        for primitive in mesh['primitives']:
            original_index = primitive.get('material')
            original = originals[original_index] if original_index is not None else {}
            channels = sorted({channel(slot) for slot in texture_slots(original)})
            if len(channels) > 4:
                raise ValueError(f'Material needs more than four UV channels: {original.get("name")}')
            mapping = dict(zip(channels, range(len(channels))))
            attributes = primitive['attributes']
            draco = primitive.get('extensions', {}).get('KHR_draco_mesh_compression')
            old_draco = draco['attributes'] if draco else None
            for old in channels:
                key = f'TEXCOORD_{old}'
                if key not in attributes or (old_draco is not None and key not in old_draco):
                    raise ValueError(f'Missing sampled UV channel {key}: {original.get("name")}')
            # Drop unused semantics; the compressed payload remains byte-identical.
            def remap(attributes):
                return {**{k: v for k, v in attributes.items() if not k.startswith('TEXCOORD_')},
                        **{f'TEXCOORD_{new}': attributes[f'TEXCOORD_{old}']
                           for old, new in mapping.items()}}
            primitive['attributes'] = remap(attributes)
            if draco:
                draco['attributes'] = remap(old_draco)
            if original_index is not None:
                key = (original_index, tuple(mapping.items()))
                if key not in variants:
                    material = deepcopy(original)
                    for slot in texture_slots(material):
                        new = mapping[channel(slot)]
                        slot['texCoord'] = new
                        transform = slot.get('extensions', {}).get('KHR_texture_transform')
                        if transform and 'texCoord' in transform:
                            transform['texCoord'] = new
                    variants[key] = len(materials)
                    materials.append(material)
                primitive['material'] = variants[key]
            records.append({'material': original.get('name'), 'channels': mapping,
                            'accessors': {str(old): attributes[f'TEXCOORD_{old}'] for old in channels},
                            'draco_attribute_ids': {str(old): old_draco[f'TEXCOORD_{old}'] for old in channels}
                            if old_draco is not None else None})
    document['materials'] = materials
    return records


def compact_images():
    """Repack embedded preview images; leave Draco geometry bytes unchanged."""
    from PIL import Image

    content = OUTPUT.read_bytes()
    magic, version, total = struct.unpack_from('<4sII', content)
    if magic != b'glTF' or version != 2 or total != len(content):
        raise ValueError('Invalid exported GLB header')
    json_length, json_type = struct.unpack_from('<II', content, 12)
    if json_type != 0x4E4F534A:
        raise ValueError('Missing GLB JSON chunk')
    document = json.loads(content[20:20 + json_length])
    uv_remapping = normalize_uvs(document)
    binary_offset = 20 + json_length + 8
    binary = content[binary_offset:]
    linear_images = set()
    for material in document.get('materials', []):
        slots = [material.get('normalTexture'), material.get('occlusionTexture'),
                 material.get('pbrMetallicRoughness', {}).get('metallicRoughnessTexture')]
        for slot in slots:
            if slot:
                linear_images.add(document['textures'][slot['index']]['source'])
    replacements = {}
    records = []
    for i, item in enumerate(document.get('images', [])):
        index = item['bufferView']
        view = document['bufferViews'][index]
        start = view.get('byteOffset', 0)
        original = binary[start:start + view['byteLength']]
        image = Image.open(io.BytesIO(original))
        image.load()
        alpha = 'A' in image.getbands() and image.getchannel('A').getextrema()[0] < 255
        if i in linear_images:
            image.thumbnail((512, 512), Image.Resampling.LANCZOS)
        encoded = io.BytesIO()
        if not alpha and i not in linear_images:
            image.convert('RGB').save(encoded, format='JPEG', quality=78, optimize=True)
            item['mimeType'] = 'image/jpeg'
        else:
            image.convert('RGBA' if alpha else 'RGB').save(encoded, format='PNG', optimize=True)
            item['mimeType'] = 'image/png'
        replacements[index] = encoded.getvalue()
        records.append({'name': item.get('name'), 'before_bytes': len(original),
                        'after_bytes': len(replacements[index]), 'size': list(image.size),
                        'mime_type': item['mimeType']})
    packed = bytearray()
    for index, view in enumerate(document['bufferViews']):
        start = view.get('byteOffset', 0)
        payload = replacements.get(index, binary[start:start + view['byteLength']])
        packed.extend(b'\0' * (-len(packed) % 4))
        view['byteOffset'], view['byteLength'] = len(packed), len(payload)
        packed.extend(payload)
    document['buffers'][0]['byteLength'] = len(packed)
    packed.extend(b'\0' * (-len(packed) % 4))
    encoded_json = json.dumps(document, separators=(',', ':'), ensure_ascii=True).encode()
    encoded_json += b' ' * (-len(encoded_json) % 4)
    total = 12 + 8 + len(encoded_json) + 8 + len(packed)
    OUTPUT.write_bytes(struct.pack('<4sII', b'glTF', 2, total) +
                       struct.pack('<II', len(encoded_json), 0x4E4F534A) + encoded_json +
                       struct.pack('<II', len(packed), 0x004E4942) + packed)
    report = json.loads(REPORT.read_text())
    report.update(output_bytes=OUTPUT.stat().st_size, output_sha256=digest(OUTPUT),
                  image_encoding=records, pillow_version=Image.__version__,
                  output_triangles=sum(document['accessors'][p['indices']]['count'] // 3
                                       for m in document['meshes'] for p in m['primitives']),
                  output_primitives=sum(len(m['primitives']) for m in document['meshes']),
                  output_images=len(document['images']),
                  uv_remapping=uv_remapping,
                  required_extensions=document.get('extensionsRequired', []))
    REPORT.write_text(json.dumps(report, indent=2))
    print('WEB_PREVIEW_COMPACT', report['output_bytes'], report['output_sha256'])


def main():
    if '--inside-blender' in sys.argv:
        prepare()
        return
    executable = shutil.which('blender')
    if not executable:
        raise SystemExit('Blender was not found on PATH')
    subprocess.run([
        str(Path(executable).resolve()), '--background', '--factory-startup',
        '--python-exit-code', '1', '--python', str(Path(__file__).resolve()),
        '--', '--inside-blender',
    ], cwd=ROOT, check=True)
    compact_images()


if __name__ == '__main__':
    main()
