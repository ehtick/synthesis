using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Synthesis.Physics {
    public class BtRigidBody : IDisposable {

        #region Fields

        public BtVec3 Position {
            get => PhysicsHandler.GetRigidBodyPosition(_rigidbody_ptr);
            set {
                PhysicsHandler.SetRigidBodyPosition(_rigidbody_ptr, value);
            }
        }
        public BtQuat Rotation {
            get => PhysicsHandler.GetRigidBodyRotation(_rigidbody_ptr);
            set {
                PhysicsHandler.SetRigidBodyRotation(_rigidbody_ptr, value);
            }
        }
        public BtVec3 LinearVelocity {
            get => PhysicsHandler.GetRigidBodyLinearVelocity(_rigidbody_ptr);
            set {
                PhysicsHandler.SetRigidBodyLinearVelocity(_rigidbody_ptr, value);
            }
        }
        public BtVec3 AngularVelocity {
            get => PhysicsHandler.GetRigidBodyLinearVelocity(_rigidbody_ptr);
            set {
                PhysicsHandler.SetRigidBodyLinearVelocity(_rigidbody_ptr, value);
            }
        }
        public BtActivationState ActivationState {
            get => PhysicsHandler.GetRigidBodyActivationState(_rigidbody_ptr);
            set => PhysicsHandler.SetRigidBodyActivationState(_rigidbody_ptr, value);
        }
        public (float linear, float angular) Damping {
            get => (PhysicsHandler.GetRigidBodyLinearDamping(_rigidbody_ptr), PhysicsHandler.GetRigidBodyAngularDamping(_rigidbody_ptr));
            set => PhysicsHandler.SetRigidBodyDamping(_rigidbody_ptr, value.linear, value.angular);
        }
        public BtShape CollisionShape { get; private set; }

        #endregion

        internal VoidPointer _rigidbody_ptr;

        internal BtRigidBody(VoidPointer rb_ptr) {
            _rigidbody_ptr = rb_ptr;
        }

        ~BtRigidBody() {
            // Dispose();
        }

        public static BtRigidBody Create(BtShape shape, float mass = 0.0f) {
            BtRigidBody physObj;
            if (mass == 0.0f) {
                physObj = new BtRigidBody(PhysicsHandler.CreateRigidBodyStatic(shape._shape_ptr));
            } else {
                physObj = new BtRigidBody(PhysicsHandler.CreateRigidBodyDynamic(mass, shape._shape_ptr));
            }
            physObj.CollisionShape = shape;

            return physObj;
        }

        public void ApplyForce(BtVec3 force, BtVec3 relativePosition) {
            PhysicsHandler.ApplyForce(_rigidbody_ptr, force, relativePosition);
        }

        public void Dispose() {
            PhysicsHandler.DeleteRigidBodyShape(_rigidbody_ptr);
        }
    }
}
