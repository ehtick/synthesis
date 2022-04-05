using System;
using UnityEngine;
using Synthesis.Physics;

namespace Synthesis {
    public class BulletRunner : MonoBehaviour {

        public BulletPuppet Ground;
        private BulletPuppet TestBall;

        public void Start() {

            if (!PhysicsHandler.InstanceExists()) {
				PhysicsHandler.CreateInstance(true);
				PhysicsHandler.SetWorldGravity(new BtVec3 { x = 0f, y = 0f, z = 0f });
			}

            var o = new GameObject("BulletGround");
            BtBoxShape s = BtBoxShape.Create(new BtVec3 { x = 50f, y = 0.1f, z = 50f });
            BtRigidBody rb = BtRigidBody.Create(s);
            rb.Position = new BtVec3 { x = 0f, y = -0.1f, z = 0f };
            rb.ActivationState = BtActivationState.DISABLE_DEACTIVATION;
            Ground = o.AddComponent<BulletPuppet>();
            Ground.BulletRep = rb;

            // GameObject g = new GameObject("Hi");
            // BtSphereShape s = BtSphereShape.Create(0.1f);
            // BtRigidBody rb = BtRigidBody.Create(s, 1);
            // rb.ActivationState = BtActivationState.DISABLE_DEACTIVATION;
            // var rep = g.AddComponent<BulletPuppet>();
            // rep.BulletRep = rb;
            // TestBall = rep;
        }

        public void Update() {
            PhysicsHandler.Step(Time.deltaTime);
            BulletManager.UpdatePuppets();

            
        }

        public void OnDrawGizmos() {
            #if UNITY_EDITOR
            if (Application.isPlaying && TestBall != null) {
                Gizmos.color = Color.red;
                Gizmos.DrawSphere(TestBall.BulletRep.Position.ToUnity(), 0.1f);
            }
            #endif
        }

        private void OnDestroy() {
            BulletManager.KillAll();
            PhysicsHandler.DestroySimulation();
            PhysicsHandler.DeleteInstance();
        }
    }
}