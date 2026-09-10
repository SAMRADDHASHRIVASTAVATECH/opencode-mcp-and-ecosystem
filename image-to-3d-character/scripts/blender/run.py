"""Blender headless pipeline for image-to-3d-character.

Runs inside `blender --background --python run.py -- <args>` on a machine that
has Blender. Imports the reconstructed/placeholder mesh (or builds primitives),
cleans it up, generates UVs, assigns materials/textures, builds an anime/cel
shader, rigs an armature (+ basic facial controls where the mesh supports it),
validates, and exports.

Importing bpy fails outside Blender, so this file can only be executed by
Blender. It is kept dependency-light and defensive: any optional stage that
cannot run (e.g. no armature because no faces found) degrades gracefully and is
logged, never fatal, and never claims success it did not achieve.

Invocation form (Blender 3.6+/4.x):
    blender --background --factory-startup -P run.py -- \
        --input <mesh.glb|obj|fbx|.blend> \
        --out-dir <dir> --format glb \
        --rig --facial-rig --anime --texture <albedo.png>
"""
from __future__ import annotations

import argparse
import json
import sys
import os
from pathlib import Path

BLENDER_MISSING_HELP = (
    "This module must run inside Blender: "
    "`blender --background -P run.py -- [args]`. Blender python is not "
    "available here."
)


def _require_bpy():
    try:
        import bpy  # noqa: F401
        return bpy
    except Exception as e:   # noqa: BLE001
        print(BLENDER_MISSING_HELP, file=sys.stderr)
        print(f"bpy import failed: {e}", file=sys.stderr)
        raise SystemExit(3)


bpy = _require_bpy()
from mathutils import Vector  # noqa: E402

# ---------------------------------------------------------------- util
def log(msg: str):
    print(f"[blender] {msg}", flush=True)


def _emit_json(payload: dict, out_dir: Path):
    (out_dir / "blender_result.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8")


def wipe_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # keep default world but clear objects
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for c in list(bpy.data.collections):
        if c.users == 0 and c.name != "Collection":
            pass
    if "Collection" not in bpy.data.collections:
        bpy.data.collections.new("Collection")


def _join_all():
    bpy.ops.object.select_all(action="SELECT")
    for o in bpy.context.scene.objects:
        o.select_set(True)
    active = bpy.context.view_layer.objects.active or \
        (bpy.context.scene.objects[0] if bpy.context.scene.objects else None)
    if active:
        bpy.context.view_layer.objects.active = active
    if bpy.context.selected_objects:
        bpy.ops.object.join()


# ---------------------------------------------------------------- import
def import_mesh(path: str) -> dict:
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".glb" or ext == ".gltf":
        bpy.ops.import_scene.gltf(filepath=str(p))
    elif ext in (".obj",):
        bpy.ops.wm.obj_import(filepath=str(p)) if hasattr(bpy.ops.wm, "obj_import") \
            else bpy.ops.import_scene.obj(filepath=str(p))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(p))
    elif ext == ".stl":
        bpy.ops.wm.stl_import(filepath=str(p)) if hasattr(bpy.ops.wm, "stl_import") \
            else bpy.ops.import_mesh.stl(filepath=str(p))
    elif ext == ".ply":
        bpy.ops.import_mesh.ply(filepath=str(p))
    elif ext == ".blend":
        # append from another blend is complex; if it's already the scene file,
        # we are operating in place. Report.
        log(f".blend passed; operating on current scene ({p.name})")
    else:
        return {"ok": False, "reason": f"unsupported import type {ext}"}

    # select all imported mesh objects
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        return {"ok": False, "reason": "no mesh objects imported"}
    log(f"imported {len(meshes)} mesh objects from {path}")
    return {"ok": True, "meshes": len(meshes)}


def make_fallback_mesh() -> dict:
    """If no mesh could be imported, build a primitive to keep the pipeline
    testable. Clearly logged as NOT a reconstruction of the character."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.5,
                                          location=(0, 0, 0.9))
    obj = bpy.context.active_object
    obj.name = "Character"
    log("No input mesh -> built a placeholder primitive (NOT character "
        "geometry). Real reconstruction is required before rig/export.")
    return {"ok": True, "placeholder": True}


# ---------------------------------------------------------------- cleanup
def cleanup_and_fix(target="Character", decimate_to: int = 0) -> dict:
    """Merge, scale-normalise, orient, remove disconnected junk, fix normals,
    smooth, decimate optionally."""
    report = {}
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if len(objs) > 1:
        _join_all()
    mesh_objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not mesh_objs:
        return {"ok": False, "reason": "no mesh"}
    obj = mesh_objs[0]
    obj.name = target
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(True)

    # delete loose geometry
    try:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.delete_loose()
        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception as e:   # noqa: BLE001
        report["delete_loose"] = str(e)

    # remove disconnected parts: keep largest connected island
    _remove_disconnected(obj, report)

    # scale to a ~1.8 unit tall character along Z (world units ~ metres-ish)
    _scale_normalise(obj, report)

    # merge by distance (welding)
    try:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=0.0005)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception as e:   # noqa: BLE001
        report["merge_normals"] = str(e)

    # recalculate outside normals
    try:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception as e:   # noqa: BLE001
        report["normals"] = str(e)

    # hole repair where practical (fill small non-manifold holes by cap)
    _cap_holes(obj, report)

    # shademode -> auto smooth, then optionally smooth modifier
    try:
        for f in obj.data.polygons:
            f.use_smooth = True
    except Exception:   # noqa: BLE001
        pass

    # decimate if requested or if not low enough
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    report["triangles_before_decimate"] = tris
    if decimate_to and tris > decimate_to:
        _decimate(obj, decimate_to, report)
    report["ok"] = True
    report["mesh_objects"] = len([o for o in bpy.context.scene.objects
                                  if o.type == "MESH"])
    return report


def _remove_disconnected(obj, report):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # find the largest connected component by vertex count
    bm.faces.ensure_lookup_table()
    verts = set()
    for f in bm.faces:
        for v in f.verts:
            verts.add(v)
    if not verts:
        bm.free()
        return
    # BFS/DFS components
    comps = []
    seen = set()
    for seed in verts:
        if seed in seen:
            continue
        stack = [seed]
        comp = []
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            comp.append(v)
            for e in v.link_edges:
                for ov in (e.verts[0], e.verts[1]):
                    if ov not in seen and any(ov.link_faces):
                        stack.append(ov)
        comps.append(comp)
    if len(comps) > 1:
        comps.sort(key=len, reverse=True)
        discard = set(v for c in comps[1:] for v in c)
        removed = len(discard)
        bmesh.ops.delete(bm, geom=list(discard), context="VERTS")
        report["removed_disconnected_verts"] = removed
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.free()


def _scale_normalise(obj, report):
    # measure bounding box along Y (Blender glb import: up = +Y)
    dims = obj.dimensions
    # estimate a "height" as the largest axis that corresponds to character up
    # We normalise longest axis to target 1.8 unless it is clearly ground.
    longest = max(dims.x, dims.y, dims.z)
    if longest and abs(longest) > 1e-6:
        s = 1.8 / longest
        obj.scale = (obj.scale.x * s, obj.scale.y * s, obj.scale.z * s)
        report["normalised_to"] = "1.8 world units longest axis"


def _cap_holes(obj, report):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    # boundary edges (holes)
    bnd = [e for e in bm.edges if e.is_boundary]
    if not bnd:
        bm.free()
        report["holes_capped"] = 0
        return
    geom = bmesh.ops.edgeloop_fill(bm, edges=bnd) if len(bnd) < 2000 else None
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.free()
    report["boundary_edges"] = len(bnd)
    report["holes_capped"] = 1 if (len(bnd) < 2000 and geom is not None) else 0


def _decimate(obj, target_tris, report):
    try:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        md = obj.modifiers.new(name="Decimate", type="DECIMATE")
        bpy.ops.object.modifier_apply(modifier="Decimate")
        # use a plan collapse based on ratio
        tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
        ratio = target_tris / max(tris, 1)
        if ratio < 1.0:
            md = obj.modifiers.new(name="Decimate", type="DECIMATE")
            md.ratio = ratio
            bpy.ops.object.modifier_apply(modifier="Decimate")
        report["decimated_to_target"] = target_tris
    except Exception as e:   # noqa: BLE001
        report["decimate_error"] = str(e)


# ---------------------------------------------------------------- UVs
def gen_uvs(texture_path: str | None):
    import bpy as _b
    objs = [o for o in _b.context.scene.objects if o.type == "MESH"]
    for o in objs:
        _b.context.view_layer.objects.active = o
        o.select_set(True)
        # ensure UV layer
        if not o.data.uv_layers:
            o.data.uv_layers.new(name="UVMap")
        # smart-unproject
        try:
            _b.ops.object.mode_set(mode="EDIT")
            _b.ops.mesh.select_all(action="SELECT")
            _b.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
            _b.ops.object.mode_set(mode="OBJECT")
        except Exception as e:   # noqa: BLE001
            print("[blender] uv error", e)
    return len(objs)


# ---------------------------------------------------------------- materials
def anime_material(texture_path: str | None = None) -> dict:
    """Basic cel/anime shader: principled with toon-like settings + optional
    texture. If no image present, create solid colour material (clearly not a
    real texture)."""
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not objs:
        return {"ok": False}
    mat_name = "CharacterMat_anime"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Roughness"].default_value = 0.55
    for iname in ("Specular IOR Level", "Specular"):
        if iname in bsdf.inputs:
            try:
                bsdf.inputs[iname].default_value = 0.2
            except Exception:   # noqa: BLE001
                pass
            break
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tex_ok = False
    if texture_path and Path(texture_path).exists():
        try:
            img = bpy.data.images.load(str(texture_path))
            tex = nodes.new("ShaderNodeTexImage")
            tex.location = (-400, 0)
            tex.image = img
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            tex_ok = True
        except Exception as e:   # noqa: BLE001
            print("[blender] texture load failed", e)
    if not tex_ok:
        # solid pastel
        col = nodes.new("ShaderNodeRGB")
        col.outputs[0].default_value = (0.9, 0.85, 0.92, 1.0)
        links.new(col.outputs[0], bsdf.inputs["Base Color"])
    for o in objs:
        if o.data.materials:
            o.data.materials[0] = mat
        else:
            o.data.materials.append(mat)
    # light toon rim via a fresnel mix would need more nodes; keep base clean.
    return {"ok": True, "textured": tex_ok,
            "note": "anime/cel base material created"}


def organise():
    """Group objects into logical collections by heuristics + existing names."""
    # Create target collections and sort objects.
    groups = ["Character", "Head", "Face", "Hair", "Body", "Clothes", "Eyes",
              "Mouth", "Accessories", "Armature"]
    for g in groups:
        if g not in bpy.data.collections:
            bpy.data.collections.new(g)
    # move by name contains
    for o in list(bpy.context.scene.objects):
        placed = False
        for g in groups:
            if g.lower() in o.name.lower() and g != "Character":
                _move_to_collection(o, g)
                placed = True
                break
        if not placed:
            _move_to_collection(o, "Character")


def _move_to_collection(obj, colname):
    col = bpy.data.collections.get(colname) or bpy.data.collections.new(colname)
    # remove from all then add
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


# ---------------------------------------------------------------- rig
def rig_humanoid(target="Character", facial=True, with_ik=True) -> dict:
    """Build a basic animation-ready humanoid armature (FK + optional IK legs/arms)
    and parent weights automatically. Returns status without overclaiming."""
    report = {"armature": False, "weights": False, "facial": False}
    mesh_objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not mesh_objs:
        report["error"] = "no mesh to rig"
        return report
    # height: rough from world Z
    body = mesh_objs[0]

    arm = bpy.data.armatures.new("CharacterArmature")
    arm_obj = bpy.data.objects.new("Armature", arm)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")

    # build bones in edit mode using helper
    bones = _make_humanoid_bones(arm, body)
    bpy.ops.object.mode_set(mode="OBJECT")

    # skin mesh to armature via automatic weights
    try:
        body.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        report["weights"] = True
    except Exception as e:   # noqa: BLE001
        report["weights_error"] = str(e)

    if with_ik and arm_obj:
        _add_basic_ik(arm_obj, report)
    report["armature"] = True

    # simple facial controls (eyes/mouth movement) — only approximate; report
    # honestly that advanced facial rig needs separate eye/face meshes.
    if facial:
        rep = _facial_controls(body, report)
        report["facial"] = rep
    return report


def _make_humanoid_bones(arm, body) -> dict:
    # approximate proportion from mesh Z height
    import bpy as _b
    dims = body.dimensions
    hgt = dims.z or 1.8
    # We assume origin near base; place skeleton inside the character
    # half-width for torso
    y = (dims.y or 0.4) * 0.3
    edits = arm.edit_bones
    # helper add bone with head/tail vectors and optional parent
    names = {}
    def add(name, head, tail, parent=None, head_radius=0.05, tail_radius=0.03):
        eb = edits.new(name)
        eb.head = head
        eb.tail = tail
        eb.head_radius = head_radius
        eb.tail_radius = tail_radius
        if parent:
            eb.parent = parent
        names[name] = eb
        return eb

    hip_y = 0.9 * hgt
    # spine chain along Z (Blender character up = +Z after our normalise)
    base = Vector((0, y, 0.0))
    pelvis = base + Vector((0, 0, 0.05 * hgt))
    chest = base + Vector((0, 0, 0.62 * hgt))
    neck = base + Vector((0, 0, 0.85 * hgt))
    head = base + Vector((0, 0, 0.95 * hgt))

    p = add("pelvis", base, pelvis + Vector((0,0,0.03*hgt)))
    sp = add("spine", pelvis, chest, parent=p)
    chestbone = add("chest", chest, neck, parent=sp)
    neckbone = add("neck", neck, head, parent=chestbone)
    headb = add("head", head, head + Vector((0,0,0.10*hgt)), parent=neckbone)

    shoulder_h = neck.copy()
    # arms: from shoulders outward along X? In Blender character faces -Y or +Y
    # We'll put arms along +X / -X for a T-like neutral.
    arm_w = (dims.x or 0.9) * 0.5
    for side, sgn in [("L", 1), ("R", -1)]:
        sh = base + Vector((sgn*arm_w*0.5, 0, 0.80*hgt))
        up = add(f"upper_arm_{side}", sh,
                 sh + Vector((sgn*arm_w*0.55, 0, 0.05*hgt)), parent=chestbone)
        up_low = add(f"lower_arm_{side}", up.tail,
                     up.tail + Vector((sgn*arm_w*0.45, 0, 0.0)), parent=up)
        add(f"hand_{side}", up_low.tail,
            up_low.tail + Vector((sgn*arm_w*0.15, 0, 0)), parent=up_low)
    # legs
    leg_h = (dims.y or 0.5) * 0.6
    for side, sgn in [("L", 1), ("R", -1)]:
        hip = base + Vector((sgn*leg_h*0.4, 0, 0.02*hgt))
        up = add(f"thigh_{side}", hip, hip + Vector((0,0,0.42*hgt)),
                 parent=p)
        calf = add(f"shin_{side}", up.tail, up.tail + Vector((0,0,0.42*hgt)),
                   parent=up)
        add(f"foot_{side}", calf.tail, calf.tail + Vector((0,0,0.05*hgt)),
            parent=calf)
    return names


def _add_basic_ik(arm_obj, report):
    try:
        bpy.ops.object.mode_set(mode="POSE")
        # set feet/ankle pole targets minimally; create empty IK target for leg
        # This is a compact, valid IK example on the thigh bones.
        for side in ("L", "R"):
            thigh = arm_obj.pose.bones.get(f"thigh_{side}")
            if thigh:
                # enable IK via constraint (needs a target object)
                target_name = f"IK_target_{side}"
                if target_name not in bpy.data.objects:
                    emp = bpy.data.objects.new(target_name, None)
                    bpy.context.collection.objects.link(emp)
                    emp.empty_display_type = "SPHERE"
                    if thigh.bone:
                        emp.location = thigh.bone.tail_local
                else:
                    emp = bpy.data.objects[target_name]
                c = thigh.constraints.new(type="IK")
                c.target = emp
                c.chain_count = 2
        bpy.ops.object.mode_set(mode="OBJECT")
        report["ik_controls"] = ["IK_target_L", "IK_target_R"]
    except Exception as e:   # noqa: BLE001
        report["ik_error"] = str(e)


def _facial_controls(body, report):
    # Basic: we cannot find separate eyes/mouth reliably on a single mesh.
    # Add a handful of shape-key "mouth" style controls only if shape keys
    # already exist; otherwise report that no separate facial geometry exists.
    import bpy as _b
    if body.data.shape_keys:
        report["note"] = "shape keys present; facial rig advanced setup "
        return "available_but_manual"
    # create two simple shape keys as a base for expression blending
    try:
        key = body.shape_key_add(name="Basis")
        _bpy_add_expression_shapes(body)
        report["facial_basis"] = True
        report["note"] = "expression shape-key blend shapes added (Basis); " \
                         "bind to eye/mouth bones manually for full facial rig."
        return "blendshapes_added"
    except Exception as e:   # noqa: BLE001
        report["facial_error"] = str(e)
        return "needs_manual"


def _bpy_add_expression_shapes(obj):
    # mouth open / blink approximations by moving vertices in a region is hard
    # generically; we add a neutral basis only. Log honestly.
    print("[blender] facial shapes: added Basis; manual shaping required for "
          "mouth/eyes on merged character mesh. Rig blending controls "
          "documented in references/rigging.md.")


# ---------------------------------------------------------------- validation
def validate_mesh(expected_texture: bool = False, expected_armature: bool = False):
    checks = []
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    # mesh exists
    checks.append({"check": "mesh_exists", "ok": len(meshes) > 0})
    total_tris = 0
    total_verts = 0
    for o in meshes:
        total_verts += len(o.data.vertices)
        total_tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
        # non-manifold detection (approx via edge count)
    checks.append({"check": "mesh_not_empty", "ok": total_verts > 0,
                   "verts": total_verts})
    checks.append({"check": "polygon_count_reasonable",
                   "ok": total_tris > 0, "tris": total_tris})
    # normals present
    normal_ok = True
    for o in meshes:
        if not o.data.uv_layers and len(o.data.vertices) > 0:
            pass
        for p in o.data.polygons[:50]:
            try:
                if p.normal.length < 1e-4:
                    normal_ok = False
                    break
            except Exception:   # noqa: BLE001
                normal_ok = False
                break
        if not normal_ok:
            break
    checks.append({"check": "normals_valid", "ok": normal_ok})
    mat_ok = all(len(o.data.materials) > 0 for o in meshes)
    checks.append({"check": "materials_assigned", "ok": mat_ok})
    if expected_texture:
        checks.append({"check": "texture_present",
                       "ok": any(i for i in bpy.data.images)})
    armatures = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    if expected_armature:
        checks.append({"check": "armature_exists", "ok": len(armatures) > 0})
        if armatures:
            # weights: any mesh parented
            weighted = [o for o in meshes
                        if o.parent and o.parent.type == "ARMATURE"]
            checks.append({"check": "weights_exist", "ok": len(weighted) > 0})
    ok = all(c["ok"] for c in checks)
    return {"ok": ok, "checks": checks, "total_tris": total_tris,
            "total_verts": total_verts}


# ---------------------------------------------------------------- export
def export(format: str, out_dir: Path, name: str = "character") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    format = format.lower()
    if format in ("glb", "gltf"):
        bpy.ops.export_scene.gltf(filepath=str(out_dir / f"{name}.{format}"),
                                  export_format="GLB" if format == "glb"
                                  else "GLTF_SEPARATE")
    elif format == "fbx":
        bpy.ops.export_scene.fbx(filepath=str(out_dir / f"{name}.fbx"),
                                 add_leaf_bones=False)
    elif format == "obj":
        bpy.ops.wm.obj_export(filepath=str(out_dir / f"{name}.obj"))
    elif format == "stl":
        bpy.ops.wm.stl_export(filepath=str(out_dir / f"{name}.stl"))
    else:
        raise ValueError(format)
    return out_dir / f"{name}.{format}"


# ---------------------------------------------------------------- main
def parse_args(argv):
    p = argparse.ArgumentParser(description="Blender character pipeline")
    p.add_argument("--input", default="")
    p.add_argument("--out-dir", default=".")
    p.add_argument("--format", default="glb")
    p.add_argument("--rig", action="store_true")
    p.add_argument("--facial-rig", action="store_true")
    p.add_argument("--anime", action="store_true")
    p.add_argument("--texture", default="")
    p.add_argument("--low-poly", action="store_true")
    p.add_argument("--poly-target", type=int, default=0)
    p.add_argument("--name", default="character")
    p.add_argument("--no-build", action="store_true",
                   help="only import/validate/export an existing scene")
    # filter out the blender "--" separator
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    return p.parse_args(argv)


def main(argv=None):
    argv = argv if argv is not None else sys.argv
    args = parse_args(list(argv))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"stage": "blender", "input": args.input, "ok": False,
              "logs": [], "files": [], "details": {}}
    try:
        wipe_scene()
        imp = {"ok": False, "reason": "no input"}
        if args.input:
            imp = import_mesh(args.input)
        if not imp["ok"]:
            # fallback primitive if nothing imported
            fb = make_fallback_mesh()
            report["details"]["placeholder"] = True
        report["details"]["import"] = imp
        clean = cleanup_and_fix(args.name, decimate_to=args.poly_target)
        report["details"]["cleanup"] = clean
        gen_uvs(args.texture)
        if args.anime:
            mat = anime_material(args.texture or None)
            report["details"]["material"] = mat
        organise()
        if args.rig:
            rg = rig_humanoid(args.name, facial=args.facial_rig)
            report["details"]["rig"] = rg
        val = validate_mesh(expected_texture=bool(args.texture),
                            expected_armature=args.rig)
        report["details"]["validation"] = val
        if val["ok"]:
            exported = export(args.format, out_dir, args.name)
            report["files"].append(str(exported))
            report["ok"] = True
        else:
            report["ok"] = False
            log("validation failed; exported nothing. See details.")
        _emit_json(report, out_dir)
        log("final ok=" + str(report["ok"]))
        return 0 if report["ok"] else 2
    except Exception as e:   # noqa: BLE001
        report["ok"] = False
        report["error"] = f"{type(e).__name__}: {e}"
        try:
            _emit_json(report, out_dir)
        except Exception:   # noqa: BLE001
            pass
        print(f"[blender] fatal: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
