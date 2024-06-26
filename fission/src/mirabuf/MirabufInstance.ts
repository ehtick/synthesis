import * as THREE from 'three';
import { mirabuf } from "../proto/mirabuf"
import MirabufParser, { ParseErrorSeverity } from './MirabufParser.ts';
import World from '@/systems/World.ts';

export enum MaterialStyle {
    Regular = 0,
    Normals = 1,
    Toon = 2
}

export const matToString = (mat: THREE.Matrix4) => {
    const arr = mat.toArray();
    return `[\n${arr[0].toFixed(4)}, ${arr[4].toFixed(4)}, ${arr[8].toFixed(4)}, ${arr[12].toFixed(4)},\n`
        + `${arr[1].toFixed(4)}, ${arr[5].toFixed(4)}, ${arr[9].toFixed(4)}, ${arr[13].toFixed(4)},\n`
        + `${arr[2].toFixed(4)}, ${arr[6].toFixed(4)}, ${arr[10].toFixed(4)}, ${arr[14].toFixed(4)},\n`
        + `${arr[3].toFixed(4)}, ${arr[7].toFixed(4)}, ${arr[11].toFixed(4)}, ${arr[15].toFixed(4)},\n]`
}

export const miraMatToString = (mat: mirabuf.ITransform) => {
    const arr = mat.spatialMatrix!;
    return `[\n${arr[0].toFixed(4)}, ${arr[1].toFixed(4)}, ${arr[2].toFixed(4)}, ${arr[3].toFixed(4)},\n`
        + `${arr[4].toFixed(4)}, ${arr[5].toFixed(4)}, ${arr[6].toFixed(4)}, ${arr[7].toFixed(4)},\n`
        + `${arr[8].toFixed(4)}, ${arr[9].toFixed(4)}, ${arr[10].toFixed(4)}, ${arr[11].toFixed(4)},\n`
        + `${arr[12].toFixed(4)}, ${arr[13].toFixed(4)}, ${arr[14].toFixed(4)}, ${arr[15].toFixed(4)},\n]`
}

let nextFillerMaterial = 0;
const fillerMaterials = [
    new THREE.MeshToonMaterial({
        color: 0xe32b50
    }),
    new THREE.MeshToonMaterial({
        color: 0x4ccf57
    }),
    new THREE.MeshToonMaterial({
        color: 0xcf4cca
    })
]

const transformVerts = (mesh: mirabuf.IMesh) => {
    const newVerts = new Float32Array(mesh.verts!.length);
    for (let i = 0; i < mesh.verts!.length; i += 3) {
        newVerts[i] = mesh.verts!.at(i)! / 100.0;
        newVerts[i + 1] = mesh.verts!.at(i + 1)! / 100.0;
        newVerts[i + 2] = mesh.verts!.at(i + 2)! / 100.0;
    }
    return newVerts;
}

const transformNorms = (mesh: mirabuf.IMesh) => {
    const newNorms = new Float32Array(mesh.normals!.length);
    for (let i = 0; i < mesh.normals!.length; i += 3) {
        const normLength = Math.sqrt(mesh.normals!.at(i)! * mesh.normals!.at(i)! +
            mesh.normals!.at(i + 1)! * mesh.normals!.at(i + 1)! +
            mesh.normals!.at(i + 2)! * mesh.normals!.at(i + 2)!
        );

        newNorms[i] = mesh.normals!.at(i)! / normLength;
        newNorms[i + 1] = mesh.normals!.at(i + 1)! / normLength;
        newNorms[i + 2] = mesh.normals!.at(i + 2)! / normLength;
    }
    return newNorms;
}

const transformGeometry = (geometry: THREE.BufferGeometry, mesh: mirabuf.IMesh) => {
    const newVerts = transformVerts(mesh);
    const newNorms = transformNorms(mesh);

    geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(newVerts), 3));
    geometry.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(newNorms), 3));
    geometry.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(mesh.uv!), 2));
    geometry.setIndex(mesh.indices!);
}

class MirabufInstance {
    private _mirabufParser: MirabufParser;
    private _materials: Map<string, THREE.Material>;
    private _meshes: Map<string, Array<THREE.Mesh>>;

    public get parser() { return this._mirabufParser; }
    public get materials() { return this._materials; }
    public get meshes() { return this._meshes; }

    public constructor(parser: MirabufParser, materialStyle?: MaterialStyle) {
        if (parser.errors.some(x => x[0] >= ParseErrorSeverity.Unimportable)) {
            throw new Error('Parser has significant errors...');
        }

        this._mirabufParser = parser;
        this._materials = new Map();
        this._meshes = new Map();

        this.LoadMaterials(materialStyle ?? MaterialStyle.Regular);
        this.CreateMeshes();
    }

    /**
     * Parses all mirabuf appearances into ThreeJs materials.
     */
    private LoadMaterials(materialStyle: MaterialStyle) {
        Object.entries(this._mirabufParser.assembly.data!.materials!.appearances!).forEach(([appearanceId, appearance]) => {
            let hex = 0xe32b50;
            if (appearance.albedo) {
                const {A, B, G, R} = appearance.albedo;
                if (A && B && G && R)
                    hex = A << 24 | R << 16 | G << 8  | B;
            }

            let material: THREE.Material;
            if (materialStyle == MaterialStyle.Regular) {
                material = new THREE.MeshPhongMaterial({
                    color: hex,
                    shininess: 0.0,
                });
            } else if (materialStyle == MaterialStyle.Normals) {
                material = new THREE.MeshNormalMaterial();
            } else if (materialStyle == MaterialStyle.Toon) {
                material = World.SceneRenderer.CreateToonMaterial(hex, 5);
                console.debug('Toon Material');
            }

            this._materials.set(
                appearanceId,
                material!
            );
        });
    }

    /**
     * Creates ThreeJS meshes from the parsed mirabuf file.
     */
    private CreateMeshes() {
        const assembly = this._mirabufParser.assembly;
        const instances = assembly.data!.parts!.partInstances!;

        let totalMeshCount = 0;

        for (const instance of Object.values(instances)/* .filter(x => x.info!.name!.startsWith('EyeBall')) */) {
            const definition = assembly.data!.parts!.partDefinitions![instance.partDefinitionReference!]!;
            const bodies = definition.bodies;
            const meshes = new Array<THREE.Mesh>();
            if (bodies) {
                for (const body of bodies) {
                    if (!body) continue;
                    const mesh = body.triangleMesh;
                    const geometry = new THREE.BufferGeometry();
                    if (mesh && mesh.mesh && mesh.mesh.verts && mesh.mesh.normals && mesh.mesh.uv && mesh.mesh.indices) {
                        transformGeometry(geometry, mesh.mesh!);

                        const appearanceOverride = body.appearanceOverride;
                        const material: THREE.Material =
                            appearanceOverride && this._materials.has(appearanceOverride)
                                ? this._materials.get(appearanceOverride)!
                                : fillerMaterials[nextFillerMaterial++ % fillerMaterials.length];

                        // if (NORMAL_MATERIALS) {
                        //     material = new THREE.MeshNormalMaterial();
                        // }

                        const threeMesh = new THREE.Mesh( geometry, material );
                        threeMesh.receiveShadow = true;
                        threeMesh.castShadow = true;

                        meshes.push(threeMesh);
                        
                        const mat = this._mirabufParser.globalTransforms.get(instance.info!.GUID!)!;
                        threeMesh.position.setFromMatrixPosition(mat);
                        threeMesh.rotation.setFromRotationMatrix(mat);
                    }
                }
            }
            totalMeshCount += meshes.length;
            this._meshes.set(instance.info!.GUID!, meshes);
        }

        console.debug(`Created '${ totalMeshCount }' meshes for mira file '${this._mirabufParser.assembly.info!.name!}'`);
    }

    /**
     * Adds all the meshes to the ThreeJs scene.
     * 
     * @param scene 
     */
    public AddToScene(scene: THREE.Scene) {
        this._meshes.forEach(x => x.forEach(y => scene.add(y)));
    }

    /**
     * Disposes of all ThreeJs scenes and materials.
     */
    public Dispose(scene: THREE.Scene) {
        this._meshes.forEach(x => x.forEach(y => {
            y.geometry.dispose();
            scene.remove(y);
        }));
        this._meshes.clear();

        this._materials.forEach(x => x.dispose());
        this._materials.clear();
    }
}

export default MirabufInstance;
