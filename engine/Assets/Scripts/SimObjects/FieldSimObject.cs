using System.Collections;
using System.Collections.Generic;
using Mirabuf;
using SynthesisAPI.Simulation;
using SynthesisAPI.Utilities;
using UnityEngine;

using Bounds = UnityEngine.Bounds;

public class FieldSimObject : SimObject {

    public static FieldSimObject CurrentField { get; private set; }

    public Assembly MiraAssembly { get; private set; }
    public GameObject GroundedNode { get; private set; }
    public GameObject FieldObject { get; private set; }
    public Bounds FieldBounds { get; private set; }

    public FieldSimObject(string name, ControllableState state, Assembly assembly, GameObject groundedNode) : base(name, state) {
        MiraAssembly = assembly;
        GroundedNode = groundedNode;
        FieldObject = groundedNode.transform.parent.gameObject;
        FieldBounds = FieldObject.transform.GetBounds();

        // Level the field
        var position = FieldObject.transform.position;
        position.y -= position.y - FieldBounds.extents.y;

        CurrentField = this;
    }

    public void DeleteField() {
        GameObject.Destroy(FieldObject);
        SimulationManager.RemoveSimObject(this);
    }
}