using System;

namespace Mirabuf {
    public partial class Vector3_f32 {
        public float Magnitude => (float)Math.Sqrt(Math.Pow(X, 2) + Math.Pow(Y, 2) + Math.Pow(Z, 2));
        public Vector3_f32 Normalize() {
            var mag = Magnitude;
            X /= mag;
            Y /= mag;
            Z /= mag;
            return this;
        }

        public static implicit operator Vector3_f32(UnityEngine.Vector3 v)
            => new Vector3_f32() { X = v.x, Y = v.y, Z = v.z };
        public static implicit operator UnityEngine.Vector3(Vector3_f32 v)
            => new UnityEngine.Vector3(v.X, v.Y, v.Z);
        public static implicit operator Vector3_f32(BXDVector3 v)
            => new Vector3_f32() { X = v.x * -0.01f, Y = v.y * 0.01f, Z = v.z * 0.01f };
        public static implicit operator BXDVector3(Vector3_f32 v)
            => new BXDVector3(v.X * -100, v.Y * 100, v.Z * 100);

        public static Vector3_f32 operator +(Vector3_f32 a, Vector3_f32 b) => new Vector3_f32() { X = a.X + b.X, Y = a.Y + b.Y, Z = a.Z + b.Z };
        public static Vector3_f32 operator -(Vector3_f32 a, Vector3_f32 b) => new Vector3_f32() { X = a.X - b.X, Y = a.Y - b.Y, Z = a.Z - b.Z };
        public static Vector3_f32 operator -(Vector3_f32 a) => new Vector3_f32() { X = -a.X, Y = -a.Y, Z = -a.Z };
        public static Vector3_f32 operator /(Vector3_f32 a, float b) => new Vector3_f32 { X = a.X / b, Y = a.Y / b, Z = a.Z / b };
        public static Vector3_f32 operator *(Vector3_f32 a, float b) => new Vector3_f32 { X = a.X * b, Y = a.Y * b, Z = a.Z * b };
    }
}
