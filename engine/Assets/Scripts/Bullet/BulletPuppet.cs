using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using Synthesis;
using Synthesis.Physics;

public class BulletPuppet : MonoBehaviour {
    public bool SkipDelete = false;
    public BtRigidBody BulletRep;

    public float Mass;
    public Vector3 Position;
    public Quaternion Rotation;

    public void Start() {
        BulletManager.RegisterPuppet(this);
    }

    public void FixedUpdate() {
        
        Position = BulletRep.Position.ToUnity();
        Rotation = BulletRep.Rotation.ToUnity();
    }

    public void OnDestroy() {
        if (!SkipDelete)
            BulletManager.UnregisterPuppet(this);
    }
}
