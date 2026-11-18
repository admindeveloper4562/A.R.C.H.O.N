"""Build an original, offline, skinned Aurelia preview as glTF 2.0 GLB.

This is a DCC-independent, art-direction prototype with genuine skin joints,
10 morph targets and six animated clips. It is not the Blender editable sculpt.
Coordinates use glTF's Y-up metres, facing -Z. Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

ASSET_VERSION = "0.013.003"
MORPHS = ("Blink_L", "Blink_R", "Smile", "Frown", "Surprise", "Brows_Up", "Brows_Down", "Viseme_A", "Viseme_E", "Viseme_O")
CLIPS = ("Idle", "Greeting", "Listening", "Reflecting", "Joyful", "Ascend")
MATERIALS = {
    "Skin_Porcelain": (.95, .73, .64, 1),
    "Hair_Midnight": (.09, .07, .23, 1),
    "Hair_Highlight": (.35, .25, .59, 1),
    "Gown_Ivory": (.87, .88, .98, 1),
    "Gown_Lavender": (.40, .32, .71, 1),
    "Gown_TrimGold": (.94, .71, .37, 1),
    "Iris_Azure": (.27, .57, .87, 1),
    "Sclera": (.97, .97, 1, 1),
    "Lashes": (.08, .05, .17, 1),
    "Feather_Pearl": (.78, .86, .99, 1),
    "Feather_Azure": (.42, .64, .95, 1),
    "Halo_Gold": (.97, .79, .42, 1),
}


def normalized_wings(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("wings must be an integer")
    return max(2, min(12, (value // 2) * 2))


def quaternion(axis: tuple[float,float,float], angle: float) -> tuple[float,...]:
    scale = math.sin(angle * .5)
    return (*[v * scale for v in axis], math.cos(angle * .5))


class GLB:
    def __init__(self):
        self.data = bytearray()
        self.views: list[dict] = []
        self.accessors: list[dict] = []
        self.meshes: list[dict] = []
        self.nodes: list[dict] = []
        self.materials: list[dict] = []
        self.animations: list[dict] = []
        self.skins: list[dict] = []

    def accessor(self, values, *, fmt: str, kind: str, component: int, target=None, bounds=False):
        # A single bufferView per attribute allows alignment and simple QA.
        raw = b"".join(struct.pack("<" + fmt, *item) for item in values)
        while len(self.data) % 4:
            self.data.append(0)
        offset = len(self.data)
        self.data.extend(raw)
        view = {"buffer":0, "byteOffset":offset, "byteLength":len(raw)}
        if target is not None:
            view["target"] = target
        view_id = len(self.views)
        self.views.append(view)
        item = {"bufferView":view_id, "componentType":component, "count":len(values), "type":kind}
        if bounds and values:
            n = len(values[0])
            item["min"] = [min(row[i] for row in values) for i in range(n)]
            item["max"] = [max(row[i] for row in values) for i in range(n)]
        idx = len(self.accessors)
        self.accessors.append(item)
        return idx

    def material(self, name):
        r,g,b,a = MATERIALS[name]
        result = {"name":name,"pbrMetallicRoughness":{
            "baseColorFactor":[r,g,b,a],
            "metallicFactor":0.6 if name in ("Halo_Gold","Gown_TrimGold") else .04,
            "roughnessFactor":.28 if name.startswith("Hair") else .48,
        }, "doubleSided": True}
        if name.startswith("Feather") or name=="Halo_Gold":
            result["emissiveFactor"] = [r*.14,g*.14,b*.14]
        self.materials.append(result)
        return len(self.materials)-1

    def add_mesh(self, name, vertices, faces, material, *, joint, morphs=None, meta=None, skin=None):
        if not vertices or not faces:
            raise ValueError("cannot add empty mesh")
        if len(vertices) > 65000:
            raise ValueError("mesh exceeds 16-bit vertex limit")
        positions = self.accessor(vertices,fmt="fff",kind="VEC3",component=5126,target=34962,bounds=True)
        # Geometry normals are computed from the local triangle winding.
        accum = [[0.0,0.0,0.0] for _ in vertices]
        for a,b,c in faces:
            p,q,r=vertices[a],vertices[b],vertices[c]
            u=[q[i]-p[i] for i in range(3)]
            v=[r[i]-p[i] for i in range(3)]
            normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            for idx in (a,b,c):
                for component in range(3):
                    accum[idx][component]+=normal[component]
        normals=[]
        for v in accum:
            norm=math.sqrt(sum(x*x for x in v)) or 1.0
            normals.append(tuple(x/norm for x in v))
        n_id=self.accessor(normals,fmt="fff",kind="VEC3",component=5126,target=34962)
        indices=self.accessor([(x,) for face in faces for x in face],fmt="H",kind="SCALAR",component=5123,target=34963)
        # Keep rigid attachment for small ornaments, but allow smooth deformation
        # across multiple joints for large garment surfaces.
        joint_rows=[]
        weight_rows=[]
        if skin is not None and len(skin)!=len(vertices):
            raise ValueError("skin influence count must equal vertex count")
        for influence in (skin if skin is not None else [[(joint,1.)]]*len(vertices)):
            if not 1<=len(influence)<=4:
                raise ValueError("each vertex needs one to four joint influences")
            if any(not isinstance(idx,int) or idx<0 or idx>=44 or
                   not math.isfinite(float(weight)) or weight<0
                   for idx,weight in influence):
                raise ValueError("skin joints and weights must be finite and in range")
            total=sum(weight for _,weight in influence)
            if not math.isfinite(total) or total<=0:
                raise ValueError("vertex has no usable skin weights")
            joint_rows.append(tuple([idx for idx,_ in influence]+[0]*(4-len(influence))))
            weight_rows.append(tuple([weight/total for _,weight in influence]+
                                     [0.]*(4-len(influence))))
        jointid=self.accessor(joint_rows,fmt="HHHH",kind="VEC4",component=5123,target=34962)
        weights=self.accessor(weight_rows,fmt="ffff",kind="VEC4",component=5126,target=34962)
        prim={"attributes":{"POSITION":positions,"NORMAL":n_id,"JOINTS_0":jointid,"WEIGHTS_0":weights},
              "indices":indices,"material":material,"mode":4}
        mesh={"name":name,"primitives":[prim]}
        if morphs is not None:
            if len(morphs)!=len(MORPHS):
                raise ValueError("expected all original facial morphs")
            prim["targets"]=[{"POSITION":self.accessor(delta,fmt="fff",kind="VEC3",component=5126,target=34962)}
                             for delta in morphs]
            mesh["weights"]=[0.]*len(MORPHS)
            mesh["extras"]={"targetNames":list(MORPHS)}
        mesh_id=len(self.meshes)
        self.meshes.append(mesh)
        node={"name":name,"mesh":mesh_id,"skin":0}
        if meta:
            node["extras"]=meta
        nid=len(self.nodes)
        self.nodes.append(node)
        return nid

    def save(self, path: Path, joints: list[int], root: int):
        self.skins=[{"name":"Aurelia_Skeleton", "joints":joints, "skeleton":root,
                     "inverseBindMatrices":self.ibm}]
        gltf={"asset":{"version":"2.0","generator":"Aurelia portable rig 0.013.003"},
              "scene":0,"scenes":[{"name":"Aurelia Character","nodes":[root,*self.scene_meshes]}],
              "nodes":self.nodes,"meshes":self.meshes,"skins":self.skins,
              "materials":self.materials,"animations":self.animations,
              "accessors":self.accessors,"bufferViews":self.views,
              "buffers":[{"byteLength":len(self.data)}],
              "extras":{"asset":"Aurelia","version":ASSET_VERSION,"wings":12}}
        body=json.dumps(gltf,separators=(",",":"),ensure_ascii=True).encode()
        body+=b" "*(-len(body)%4)
        payload=bytes(self.data)+b"\0"*(-len(self.data)%4)
        length=12+8+len(body)+8+len(payload)
        with path.open("wb") as output:
            output.write(struct.pack("<4sII",b"glTF",2,length))
            output.write(struct.pack("<II",len(body),0x4E4F534A))
            output.write(body)
            output.write(struct.pack("<II",len(payload),0x004E4942))
            output.write(payload)
        return gltf


def sphere(cx,cy,cz,rx,ry,rz,segments=18,rings=12):
    vertices=[]
    for i in range(rings+1):
        theta=math.pi*i/rings
        for j in range(segments+1):
            phi=2*math.pi*j/segments
            vertices.append((cx+rx*math.sin(theta)*math.cos(phi),
                             cy+ry*math.cos(theta),
                             cz+rz*math.sin(theta)*math.sin(phi)))
    faces=[]
    for i in range(rings):
        for j in range(segments):
            a=i*(segments+1)+j
            b=a+segments+1
            faces.extend([(a,b,a+1),(a+1,b,b+1)])
    return vertices,faces


def tapered(cx,cz,profiles,segments=22):
    vertices=[]
    for y,rx,rz in profiles:
        for j in range(segments):
            t=2*math.pi*j/segments
            vertices.append((cx+rx*math.cos(t),y,cz+rz*math.sin(t)))
    faces=[]
    for i in range(len(profiles)-1):
        for j in range(segments):
            n=(j+1)%segments
            a=i*segments+j;b=i*segments+n
            c=(i+1)*segments+n;d=(i+1)*segments+j
            faces.extend([(a,b,c),(a,c,d)])
    faces.extend([(0,j,j+1) for j in range(1,segments-1)])
    base=(len(profiles)-1)*segments
    faces.extend([(base,base+j+1,base+j) for j in range(1,segments-1)])
    return vertices,faces


def feather(start,end,width):
    sx,sy,sz=start;ex,ey,ez=end
    dx=ex-sx;dy=ey-sy;dz=ez-sz
    # Symmetric leaf 3D surface around its wing vector, facing the camera.
    lengths=(0.,.23,.50,.78,1.)
    widths=(.10,.80,1.,.66,.06)
    verts=[]
    for t,w in zip(lengths,widths):
        x=sx+dx*t;y=sy+dy*t;z=sz+dz*t
        verts.extend([(x-width*w*.5,y,z-.018*(1-t)),(x+width*w*.5,y,z+.018*(1-t))])
    faces=[]
    for j in range(len(lengths)-1):
        a=2*j
        faces.extend([(a,a+1,a+2),(a+1,a+3,a+2)])
    return verts,faces


def facial_mesh():
    positions=[];faces=[];features={}
    def patch(name,x,y,z,w,h):
        i=len(positions)
        positions.extend([(x-w/2,y+h/2,z),(x+w/2,y+h/2,z),
                          (x+w/2,y-h/2,z),(x-w/2,y-h/2,z)])
        faces.extend([(i,i+1,i+2),(i,i+2,i+3)])
        features[name]=range(i,i+4)
    patch("Eye_L",-.058,1.80,-.151,.048,.023)
    patch("Eye_R",.058,1.80,-.151,.048,.023)
    patch("Brow_L",-.058,1.836,-.154,.059,.008)
    patch("Brow_R",.058,1.836,-.154,.059,.008)
    patch("Mouth",0,1.715,-.159,.053,.012)
    targets=[]
    for name in MORPHS:
        morph=[[0.,0.,0.] for _ in positions]
        def shift(feature,dx=0.,dy=0.):
            for index in features[feature]:
                morph[index][0]+=dx
                morph[index][1]+=dy
        if name.startswith("Blink_"):
            f="Eye_L" if name.endswith("_L") else "Eye_R"
            for index in features[f]:
                morph[index][1]=-(positions[index][1]-(1.80))*.95
        elif name=="Smile":
            for i in features["Mouth"]:
                morph[i][1]+=.012 if i%4 in (0,3) else .003
        elif name=="Frown": shift("Mouth",dy=-.013)
        elif name in ("Surprise","Viseme_A","Viseme_O"):
            amount=.024 if name=="Viseme_O" else .042
            for i in features["Mouth"]:
                if i%4 in (2,3):morph[i][1]-=amount
                if name=="Viseme_O": morph[i][0]=-positions[i][0]*.35
        elif name=="Viseme_E":
            for i in features["Mouth"]:
                morph[i][0]=positions[i][0]*.30
        elif name=="Brows_Up":
            shift("Brow_L",dy=.020);shift("Brow_R",dy=.020)
        elif name=="Brows_Down":
            shift("Brow_L",dy=-.012);shift("Brow_R",dy=-.012)
        targets.append([tuple(v) for v in morph])
    return positions,faces,targets


def build(path:Path,*,wings:int=12):
    # Always preserve all 12 model wings; their MIN_STAGE is metadata.
    # Runtime must explicitly hide unearned wing pairs.
    stage=normalized_wings(wings)
    g=GLB()
    mats={name:g.material(name) for name in MATERIALS}
    bone_specs=[]
    def bone(name,loc,parent=None): bone_specs.append((name,loc,parent))
    bone("Root",(0.,.09,0.))
    bone("Pelvis",(0.,.94,0.),"Root")
    bone("Spine",(0.,1.12,0.),"Pelvis")
    bone("Chest",(0.,1.42,0.),"Spine")
    bone("Neck",(0.,1.61,0.),"Chest")
    bone("Head",(0.,1.82,0.),"Neck")
    for side,sgn in (("L",-1),("R",1)):
        bone("Clavicle_"+side,(sgn*.25,1.49,0.),"Chest")
        bone("UpperArm_"+side,(sgn*.37,1.40,0.),"Clavicle_"+side)
        bone("Forearm_"+side,(sgn*.53,1.19,0.),"UpperArm_"+side)
        bone("Hand_"+side,(sgn*.61,1.0,-.01),"Forearm_"+side)
        bone("Thigh_"+side,(sgn*.13,.83,0.),"Pelvis")
        bone("Shin_"+side,(sgn*.14,.46,0.),"Thigh_"+side)
        bone("Foot_"+side,(sgn*.14,.12,-.07),"Shin_"+side)
    for side,sgn in (("L",-1),("R",1)):
        for index in range(1,7):
            h=1.37+.044*index
            b=f"Wing_{side}_{index:02d}"
            bone(b+"_Base",(sgn*.19,h,.16),"Chest")
            bone(b+"_Tip",(sgn*(.67+.06*index),h+.12,.25),b+"_Base")
    assert len(bone_specs)==44
    world={name:loc for name,loc,_ in bone_specs}
    joint_nodes={}
    for name,loc,parent in bone_specs:
        local=tuple(loc[i] - (world[parent][i] if parent else 0.) for i in range(3))
        n=len(g.nodes)
        g.nodes.append({"name":name,"translation":list(local)})
        joint_nodes[name]=n
        if parent:
            g.nodes[joint_nodes[parent]].setdefault("children",[]).append(n)
    joints=list(joint_nodes.values())
    joint_map={name:index for index,name in enumerate(joint_nodes)}
    ibms=[]
    for name,loc,_ in bone_specs:
        x,y,z=loc
        ibms.append((1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,-x,-y,-z,1.))
    g.ibm=g.accessor(ibms,fmt="f"*16,kind="MAT4",component=5126)
    g.scene_meshes=[]
    def add(name,geom,mat,bone,*,morphs=None,meta=None,skin_fn=None):
        verts,faces=geom
        skin=[skin_fn(vertex) for vertex in verts] if skin_fn else None
        node=g.add_mesh(name,verts,faces,mats[mat],joint=joint_map[bone],
                        morphs=morphs,meta=meta,skin=skin)
        g.scene_meshes.append(node)
        return node

    def smoothstep(value):
        t=max(0.,min(1.,value))
        return t*t*(3.-2.*t)

    def gown_skin(vertex):
        # Three-joint continuous skin blending lets upper fabric follow the
        # spine/chest while keeping the hem attached to the pelvis.
        y=vertex[1]
        lower=smoothstep((y-.90)/.40)
        upper=smoothstep((y-1.04)/.48)
        return [(joint_map["Pelvis"],1.-lower),
                (joint_map["Spine"],lower*(1.-upper)),
                (joint_map["Chest"],lower*upper)]

    add("Gown_Base",tapered(0.,0.,[(.08,.43,.34),(.42,.36,.28),(.80,.27,.21),(1.12,.16,.16),(1.42,.21,.17)]),"Gown_Ivory","Pelvis",skin_fn=gown_skin)
    add("Gown_Overlayer",tapered(0.,-.035,[(.10,.44,.32),(.26,.37,.29),(.55,.28,.20),(.88,.18,.16),(1.18,.11,.12)]),"Gown_Lavender","Pelvis",skin_fn=gown_skin)
    add("Torso",sphere(0,1.40,0,.225,.16,.17),"Gown_Ivory","Chest")
    add("Neck",sphere(0,1.64,0,.063,.13,.064),"Skin_Porcelain","Neck")
    add("Head_Sculpt",sphere(0,1.83,0,.145,.205,.13),"Skin_Porcelain","Head")
    add("Hair_Back",sphere(0,1.78,.08,.164,.30,.118),"Hair_Midnight","Head")
    add("Hair_Crown",sphere(0,1.97,.00,.158,.075,.127),"Hair_Midnight","Head")
    for side,sgn in (("L",-1),("R",1)):
        add("Arm_"+side,sphere(sgn*.35,1.37,0,.076,.22,.082),"Gown_Lavender","UpperArm_"+side)
        add("Forearm_"+side,sphere(sgn*.53,1.16,-.02,.058,.16,.052),"Skin_Porcelain","Forearm_"+side)
        add("Hand_"+side,sphere(sgn*.63,.98,-.02,.05,.065,.04),"Skin_Porcelain","Hand_"+side)
        add("Boot_"+side,sphere(sgn*.15,.14,-.08,.11,.14,.13),"Gown_Lavender","Foot_"+side)
        add("Ear_"+side,sphere(sgn*.139,1.85,-.015,.028,.041,.026),"Skin_Porcelain","Head")
        for j in range(7):
            x=sgn*(.11+j*.012)
            add(f"Hair_{side}_{j:02d}", sphere(x,1.71-j*.03,.09,.026,.24,.044),
                "Hair_Highlight" if j%3==0 else "Hair_Midnight","Head")
    verts,faces,targets=facial_mesh()
    face_node=add("Face_Expressions",(verts,faces),"Lashes","Head",morphs=targets)
    add("Halo_Gold_Ring",tapered(0,0,[(2.11,.18,.18),(2.116,.19,.19),(2.13,.18,.18)]),"Halo_Gold","Head")
    for side,sgn in (("L",-1),("R",1)):
        for i in range(1,7):
            height=1.36+i*.044
            for k in range(10):
                t=k/10
                sx=sgn*(.22+.13*t);ex=sgn*(.54+.10*i+.80*t)
                sy=height-.05+t*.11;ey=height+.10+t*.21
                shape=feather((sx,sy,.13+.03*t),(ex,ey,.19+.09*t),.10+.06*math.sin(math.pi*t))
                add(f"wing_{side}_{i:02d}_feather_{k:02d}",shape,
                    "Feather_Azure" if k%4==0 else "Feather_Pearl",f"Wing_{side}_{i:02d}_Tip",
                    meta={"tws_min_wings":2*i})
    # Complete skin joint graph and meshes. All meshes use skin=0.
    # Add real authored quaternion channels and facial morph animations.
    timeline=[(0.,),(.7,),(1.4,),(2.1,),(2.8,)]
    timeline_accessor=g.accessor(timeline,fmt="f",kind="SCALAR",component=5126,bounds=True)
    for clip in CLIPS:
        anim={"name":clip,"samplers":[],"channels":[]}
        def channel(node,path,rows,fmt,kind):
            output=g.accessor(rows,fmt=fmt,kind=kind,component=5126)
            sampler=len(anim["samplers"])
            anim["samplers"].append({"input":timeline_accessor,"output":output,"interpolation":"LINEAR"})
            anim["channels"].append({"sampler":sampler,"target":{"node":node,"path":path}})
        factor={"Idle":.04,"Greeting":.22,"Listening":.07,"Reflecting":.13,"Joyful":.20,"Ascend":.31}[clip]
        cycle=(0.,1.,0.,-.6,0.)
        for name,ax in [("Head",(0,0,1)),("Chest",(1,0,0)),
                        ("UpperArm_R",(0,0,1)),("UpperArm_L",(0,0,1))]:
            mult=1.5 if name=="UpperArm_R" and clip=="Greeting" else .28
            channel(joint_nodes[name],"rotation",
                    [quaternion(ax,factor*v*mult) for v in cycle],"ffff","VEC4")
        for side in ("L","R"):
            for index in range(1,7):
                sign=-1 if side=="L" else 1
                channel(joint_nodes[f"Wing_{side}_{index:02d}_Base"],"rotation",
                        [quaternion((0.,0.,1.),sign*factor*v*(.8+index*.05)) for v in cycle],"ffff","VEC4")
        # Root translation animates a true world-space hover (not just UI).
        channel(joint_nodes["Root"],"translation",
                [(0.,.09+factor*.14*max(0,v),0.) for v in cycle],"fff","VEC3")
        blink_index=MORPHS.index("Blink_L")
        blink_right=MORPHS.index("Blink_R")
        smile_index=MORPHS.index("Smile")
        weights=[]
        for frame in range(len(timeline)):
            row=[0.]*len(MORPHS)
            if frame==2:
                row[blink_index]=row[blink_right]=1.
            if clip in ("Greeting","Joyful"):
                row[smile_index]=.7 if frame>0 else .25
            weights.extend((v,) for v in row)
        channel(face_node,"weights",weights,"f","SCALAR")
        g.animations.append(anim)
    doc=g.save(path,joints,joint_nodes["Root"])
    info={
        "asset":"Aurelia", "version":ASSET_VERSION,"source":"portable-python-gltf",
        "type":"rigged-original-preview-not-artist-reviewed", "unit":"metre", "up_axis":"Y",
        "wings_on_stage":stage, "wing_stages":[2,4,6,8,10,12],
        "bones":[name for name,_,_ in bone_specs], "morphs":list(MORPHS),
        "animation_clips":list(CLIPS),"material_names":list(MATERIALS),
        "skin_count":len(doc["skins"]),"node_count":len(doc["nodes"]),
        "mesh_count":len(doc["meshes"]),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    path.with_suffix(".manifest.json").write_text(json.dumps(info,indent=2)+"\n")
    return info


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output",type=Path,default=Path("Aurelia_Rigged_Preview.glb"))
    cli.add_argument("--wings",type=int,default=12)
    args=cli.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    result=build(args.output,wings=args.wings)
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()