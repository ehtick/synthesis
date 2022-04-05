using System;
using System.Collections.Generic;
using System.Text;

namespace Synthesis.Physics {
    public class BtShape : IDisposable {
        internal VoidPointer _shape_ptr;

        protected BtShape(VoidPointer ptr) {
            _shape_ptr = ptr;
        }

        ~BtShape() {
            // Dispose();
        }

        public void Dispose() {
            PhysicsHandler.DeleteCollisionShape(_shape_ptr);
        }
    }

    public class BtBoxShape : BtShape {

        private BtVec3 _halfExtents;
        public BtVec3 HalfExtents { get => _halfExtents; }

        internal BtBoxShape(VoidPointer ptr) : base(ptr) {
            _halfExtents = PhysicsHandler.GetBoxShapeExtents(ptr);
        }

        public static BtBoxShape Create(BtVec3 halfExtents)
            => new BtBoxShape(PhysicsHandler.CreateBoxShape(halfExtents));
    }

    public class BtCompoundShape : BtShape {

        public int ChildrenCount => PhysicsHandler.GetCompoundShapeChildCount(_shape_ptr);
        private List<BtShape> _children = new List<BtShape>();
        public IReadOnlyCollection<BtShape> Children => _children.AsReadOnly();

        internal BtCompoundShape(VoidPointer ptr) : base(ptr) { }

        public static BtCompoundShape Create(int initChildCapacity) {
            var shape = new BtCompoundShape(PhysicsHandler.CreateCompoundShape(initChildCapacity));
            return shape;
        }

        public void AddShape(BtShape shape, BtVec3 offset, BtQuat orientation) {
            PhysicsHandler.AddShapeToCompoundShape(_shape_ptr, shape._shape_ptr, offset, orientation);
            _children.Add(shape);
        }
    }

    public class BtSphereShape : BtShape {

        public float Radius => PhysicsHandler.GetSphereShapeRadius(_shape_ptr);

        internal BtSphereShape(VoidPointer ptr) : base(ptr) { }

        public static BtSphereShape Create(float radius) {
            var shape = new BtSphereShape(PhysicsHandler.CreateSphereShape(radius));
            return shape;
        }
    }

    public class BtConvexShape : BtShape {
        internal BtConvexShape(VoidPointer ptr) : base(ptr) { }

        public static BtConvexShape Create(BtVec3[] vertCloud) {
            var shape = new BtConvexShape(PhysicsHandler.CreateConvexShape(vertCloud));
            return shape;
        }
    }
}
