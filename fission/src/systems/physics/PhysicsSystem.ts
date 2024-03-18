import { JoltMat44_ThreeMatrix4, MirabufFloatArr_JoltVec3, ThreeMatrix4_JoltMat44, ThreeVector3_JoltVec3, _JoltQuat } from "../../util/TypeConversions";
import JOLT from "../../util/loading/JoltSyncLoader";
import Jolt from "@barclah/jolt-physics";
import * as THREE from 'three';
import { mirabuf } from '../../proto/mirabuf';
import MirabufParser, { RigidNodeReadOnly } from "../../mirabuf/MirabufParser";
import WorldSystem from "../WorldSystem";
import { threeMatrix4ToString } from "@/util/debug/DebugPrint";

const LAYER_NOT_MOVING = 0;
const LAYER_MOVING = 1;
const COUNT_OBJECT_LAYERS = 2;

const STANDARD_TIME_STEP = 1.0 / 120.0;
const STANDARD_SUB_STEPS = 3;

/**
 * The PhysicsSystem handles all Jolt Phyiscs interactions within Synthesis.
 * This system can create physical representations of objects such as Robots,
 * Fields, and Game pieces, and simulate them.
 */
class PhysicsSystem extends WorldSystem {
    
    private _joltInterface: Jolt.JoltInterface;
    private _joltPhysSystem: Jolt.PhysicsSystem;
    private _joltBodyInterface: Jolt.BodyInterface;
    private _bodies: Array<Jolt.BodyID>;

    /**
     * Creates a PhysicsSystem object.
     */
    constructor() {
        super();

        this._bodies = [];

        const joltSettings = new JOLT.JoltSettings();
        SetupCollisionFiltering(joltSettings);

        this._joltInterface = new JOLT.JoltInterface(joltSettings);
        JOLT.destroy(joltSettings);

        this._joltPhysSystem = this._joltInterface.GetPhysicsSystem();
        this._joltBodyInterface = this._joltPhysSystem.GetBodyInterface();

        const ground = this.CreateBox(new THREE.Vector3(5.0, 0.5, 5.0), undefined, new THREE.Vector3(0.0, -2.0, 0.0), undefined);
        this._joltBodyInterface.AddBody(ground.GetID(), JOLT.EActivation_Activate);
    }

    /**
     * TEMPORARY
     * Create a box.
     * 
     * @param   halfExtents The half extents of the Box.
     * @param   mass        Mass of the Box. Leave undefined to make Box static.
     * @param   position    Posiition of the Box (default: 0, 0, 0)
     * @param   rotation    Rotation of the Box (default 0, 0, 0, 1)
     * @returns Reference to Jolt Body
     */
    public CreateBox(
    halfExtents: THREE.Vector3,
    mass: number | undefined,
    position: THREE.Vector3 | undefined,
    rotation: THREE.Euler | THREE.Quaternion | undefined) {
        const size = ThreeVector3_JoltVec3(halfExtents);
        const shape = new JOLT.BoxShape(size, 0.1);
        JOLT.destroy(size);

        const pos = position ? ThreeVector3_JoltVec3(position) : new JOLT.Vec3(0.0, 0.0, 0.0);
        const rot = _JoltQuat(rotation);
        const creationSettings = new JOLT.BodyCreationSettings(
            shape,
            pos,
            rot,
            mass ? JOLT.EMotionType_Dynamic : JOLT.EMotionType_Static,
            mass ? LAYER_MOVING : LAYER_NOT_MOVING
        );
        if (mass) {
            creationSettings.mMassPropertiesOverride.mMass = mass;
        }
        const body = this._joltBodyInterface.CreateBody(creationSettings);
        JOLT.destroy(pos);
        JOLT.destroy(rot);
        JOLT.destroy(creationSettings);

        this._bodies.push(body.GetID());
        return body;
    }

    public CreateBody(
    shape: Jolt.Shape,
    mass: number | undefined,
    position: THREE.Vector3 | undefined,
    rotation: THREE.Euler | THREE.Quaternion | undefined) {
        const pos = position ? ThreeVector3_JoltVec3(position) : new JOLT.Vec3(0.0, 0.0, 0.0);
        const rot = _JoltQuat(rotation);
        const creationSettings = new JOLT.BodyCreationSettings(
            shape,
            pos,
            rot,
            mass ? JOLT.EMotionType_Dynamic : JOLT.EMotionType_Static,
            LAYER_NOT_MOVING
        );
        if (mass) {
            creationSettings.mMassPropertiesOverride.mMass = mass;
        }
        const body = this._joltBodyInterface.CreateBody(creationSettings);
        JOLT.destroy(pos);
        JOLT.destroy(rot);
        JOLT.destroy(creationSettings);

        this._bodies.push(body.GetID());
        return body;
    }

    public CreateConvexHull(points: Float32Array, density: number = 1.0) {
        if (points.length % 3) {
            throw new Error(`Invalid size of points: ${points.length}`);
        }
        const settings = new JOLT.ConvexHullShapeSettings();
        settings.mPoints.clear();
        settings.mPoints.reserve(points.length / 3.0);
        for (let i = 0; i < points.length; i += 3) {
            settings.mPoints.push_back(new JOLT.Vec3(points[i], points[i + 1], points[i + 2]));
        }
        settings.mDensity = density;
        return settings.Create();
    }

    public CreateBodiesFromParser(parser: MirabufParser): Map<string, Jolt.BodyID> {
        const rnToBodies = new Map<string, Jolt.BodyID>();
        
        filterNonPhysicsNodes(parser.rigidNodes, parser.assembly).forEach(rn => {

            // console.debug(`Making Body for RigidNode '${rn.name}'`);
            // rn.parts.forEach(x => console.debug(parser.assembly.data!.parts!.partInstances![x]!.info!.name!));

            const compoundShapeSettings = new JOLT.StaticCompoundShapeSettings();
            let shapesAdded = 0;

            let totalMass = 0;
            const comAccum = new mirabuf.Vector3();

            const minBounds = new JOLT.Vec3(1000000.0, 1000000.0, 1000000.0);
            const maxBounds = new JOLT.Vec3(-1000000.0, -1000000.0, -1000000.0);

            rn.parts.forEach(partId => {
                const partInstance = parser.assembly.data!.parts!.partInstances![partId]!;
                if (partInstance.skipCollider == null || partInstance == undefined || partInstance.skipCollider == false) {
                    const partDefinition = parser.assembly.data!.parts!.partDefinitions![partInstance.partDefinitionReference!]!;
                    
                    const partShapeResult = this.CreateShapeSettingsFromPart(partDefinition);
                    
                    if (partShapeResult) {

                        const [shapeSettings, partMin, partMax] = partShapeResult;

                        const transform = ThreeMatrix4_JoltMat44(parser.globalTransforms.get(partId)!);
                        compoundShapeSettings.AddShape(
                            transform.GetTranslation(),
                            transform.GetQuaternion(),
                            shapeSettings,
                            0
                        );
                        shapesAdded++;

                        this.UpdateMinMaxBounds(transform.Multiply3x3(partMin), minBounds, maxBounds);
                        this.UpdateMinMaxBounds(transform.Multiply3x3(partMax), minBounds, maxBounds);

                        if (partDefinition.physicalData && partDefinition.physicalData.com && partDefinition.physicalData.mass) {
                            const mass = partDefinition.massOverride ? partDefinition.massOverride! : partDefinition.physicalData.mass!;
                            totalMass += mass;
                            comAccum.x += partDefinition.physicalData.com.x! * mass / 100.0;
                            comAccum.y += partDefinition.physicalData.com.y! * mass / 100.0;
                            comAccum.z += partDefinition.physicalData.com.z! * mass / 100.0;

                            console.debug(`COM MIRA: ${partDefinition.physicalData.com.x!.toFixed(4)}, ${partDefinition.physicalData.com.y!.toFixed(4)}, ${partDefinition.physicalData.com.z!.toFixed(4)}`);
                        }
                    }
                }
            });

            if (shapesAdded > 0) {
                
                const shapeResult = compoundShapeSettings.Create();
                // const shapeResult = new JOLT.SphereShapeSettings(0.2).Create();
                // const shapeResult = new JOLT.BoxShapeSettings(new JOLT.Vec3(2.0, 0.5, 1.0)).Create();

                const com = new JOLT.Vec3(comAccum.x / totalMass, comAccum.y / totalMass, comAccum.z / totalMass);

                const boundsCenter = minBounds.Add(maxBounds).Div(2);
                // const rtSettings = new JOLT.RotatedTranslatedShapeSettings(
                //     boundsCenter.Mul(-1), new JOLT.Quat(0, 0, 0, 1), compoundShapeSettings
                // );
                // const shapeResult = rtSettings.Create();

                if (!shapeResult.IsValid || shapeResult.HasError()) {
                    console.error(`Failed to create shape for RigidNode ${rn.name}\n${shapeResult.GetError().c_str()}`);
                }

                const shape = shapeResult.Get();
                // shape.GetMassProperties().mMass = 1;
                // shape.GetMassProperties().mMass = totalMass == 0.0 ? 1 : totalMass;
                // console.debug(`Mass: ${shape.GetMassProperties().mMass}`);
                // shape.GetMassProperties().SetMassAndInertiaOfSolidBox(new JOLT.Vec3(1, 1, 1), 100);

                console.debug(`Inertia [${rn.name}]:${threeMatrix4ToString(JoltMat44_ThreeMatrix4(shape.GetMassProperties().mInertia))}`);
                
                console.debug(`COM: ${com.GetX().toFixed(4)}, ${com.GetY().toFixed(4)}, ${com.GetZ().toFixed(4)}`);

                // const worldBounds = shape.GetWorldSpaceBounds(new JOLT.Mat44().sIdentity(), new JOLT.Vec3(1,1,1));
                // const center =  worldBounds.mMax.Sub(worldBounds.mMin);

                const bodySettings = new JOLT.BodyCreationSettings(
                    shape, new JOLT.Vec3()/*boundsCenter.Mul(-1)*/, new JOLT.Quat(0, 0, 0, 1), JOLT.EMotionType_Dynamic, LAYER_MOVING
                );
                const body = this._joltBodyInterface.CreateBody(bodySettings);
                this._joltBodyInterface.AddBody(body.GetID(), JOLT.EActivation_Activate);
                rnToBodies.set(rn.name, body.GetID());

                body.SetRestitution(0.2);
                body.SetAngularVelocity(new JOLT.Vec3(0.2, 1.0, 0.0));
            } else {
                JOLT.destroy(compoundShapeSettings);
            }
        });

        return rnToBodies;
    }

    private CreateShapeSettingsFromPart(partDefinition: mirabuf.IPartDefinition): [Jolt.ShapeSettings, Jolt.Vec3, Jolt.Vec3] | undefined | null {
        const settings = new JOLT.ConvexHullShapeSettings();

        const min = new JOLT.Vec3(1000000.0, 1000000.0, 1000000.0);
        const max = new JOLT.Vec3(-1000000.0, -1000000.0, -1000000.0);

        const points = settings.mPoints;
        partDefinition.bodies!.forEach(body => {
            if (body.triangleMesh && body.triangleMesh.mesh && body.triangleMesh.mesh.verts) {
                const vertArr = body.triangleMesh.mesh.verts;
                for (let i = 0; i < body.triangleMesh.mesh.verts.length; i += 3) {
                    const vert = MirabufFloatArr_JoltVec3(vertArr, i);
                    points.push_back(vert);
                    this.UpdateMinMaxBounds(vert, min, max);
                    JOLT.destroy(vert);
                }
            }
        });

        if (points.size() < 4) {
            JOLT.destroy(settings);
            return;
        } else {
            // JOLT.destroy(settings);
            // return [new JOLT.SphereShapeSettings(0.2), min, max];
            return [settings, min, max];
        }
    }

    private UpdateMinMaxBounds(v: Jolt.Vec3, min: Jolt.Vec3, max: Jolt.Vec3) {
        if (v.GetX() < min.GetX())
            min.SetX(v.GetX());
        if (v.GetY() < min.GetY())
            min.SetY(v.GetY());
        if (v.GetZ() < min.GetZ())
            min.SetZ(v.GetZ());

        if (v.GetX() > max.GetX())
            max.SetX(v.GetX());
        if (v.GetY() > max.GetY())
            max.SetY(v.GetY());
        if (v.GetZ() > max.GetZ())
            max.SetZ(v.GetZ());
    }

    public DestroyBodies(...bodies: Jolt.Body[]) {
        bodies.forEach(x => {
            this._joltBodyInterface.RemoveBody(x.GetID());
            this._joltBodyInterface.DestroyBody(x.GetID());
        });
    }

    public DestroyBodyIds(...bodies: Jolt.BodyID[]) {
        bodies.forEach(x => {
            this._joltBodyInterface.RemoveBody(x);
            this._joltBodyInterface.DestroyBody(x);
        });
    }

    public GetBody(bodyId: Jolt.BodyID) {
        return this._joltPhysSystem.GetBodyLockInterface().TryGetBody(bodyId);
    }

    public Update(_: number): void {
        this._joltInterface.Step(STANDARD_TIME_STEP, STANDARD_SUB_STEPS);
    }

    public Destroy(): void {
        // Destroy Jolt Bodies.
        this._bodies.forEach(x => JOLT.destroy(x));
        this._bodies = [];

        JOLT.destroy(this._joltInterface);
    }
}

function SetupCollisionFiltering(settings: Jolt.JoltSettings) {
    const objectFilter = new JOLT.ObjectLayerPairFilterTable(COUNT_OBJECT_LAYERS);
    objectFilter.EnableCollision(LAYER_NOT_MOVING, LAYER_MOVING);
    // objectFilter.EnableCollision(LAYER_MOVING, LAYER_MOVING);

    const BP_LAYER_NOT_MOVING = new JOLT.BroadPhaseLayer(LAYER_NOT_MOVING);
    const BP_LAYER_MOVING = new JOLT.BroadPhaseLayer(LAYER_MOVING);
    const COUNT_BROAD_PHASE_LAYERS = 2;

    const bpInterface = new JOLT.BroadPhaseLayerInterfaceTable(COUNT_OBJECT_LAYERS, COUNT_BROAD_PHASE_LAYERS);
    bpInterface.MapObjectToBroadPhaseLayer(LAYER_NOT_MOVING, BP_LAYER_NOT_MOVING);
    bpInterface.MapObjectToBroadPhaseLayer(LAYER_MOVING, BP_LAYER_MOVING);

    settings.mObjectLayerPairFilter = objectFilter;
    settings.mBroadPhaseLayerInterface = bpInterface;
    settings.mObjectVsBroadPhaseLayerFilter = new JOLT.ObjectVsBroadPhaseLayerFilterTable(
        settings.mBroadPhaseLayerInterface,
        COUNT_BROAD_PHASE_LAYERS,
        settings.mObjectLayerPairFilter,
        COUNT_OBJECT_LAYERS
    );
}

function filterNonPhysicsNodes(nodes: RigidNodeReadOnly[], mira: mirabuf.Assembly): RigidNodeReadOnly[] {
    return nodes.filter(x => {
        for (const part of x.parts) {
            const inst = mira.data!.parts!.partInstances![part]!;
            const def = mira.data!.parts!.partDefinitions![inst.partDefinitionReference!]!;
            if (def.bodies && def.bodies.length > 0) {
                return true;
            }
        }
        return false;
    });
}

export default PhysicsSystem;