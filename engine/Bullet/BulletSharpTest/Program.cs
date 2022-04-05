using System;
// using Synthesis;
using Synthesis.Physics;

namespace BulletSharpTest {
    class Program {
        static void Main(string[] args) {
            var box = BtBoxShape.Create(new BtVec3() { x = 1, y = 5, z = 3 });
            var extents = box.HalfExtents;
            Console.WriteLine($"{extents.x}, {extents.y}, {extents.z}");
        }
    }
}
