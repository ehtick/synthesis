using UnityEngine;

namespace Mirabuf {
    public partial class SpatialTransformMatrix {
        private Matrix4x4 _unityMatrix;
        public Matrix4x4 UnityMatrix {
            get {
                if (_unityMatrix == default) {
                    _unityMatrix = new Matrix4x4(new Vector4(Values[0], Values[1], Values[2], Values[3]),
                        new Vector4(Values[4], Values[5], Values[6], Values[7]),
                        new Vector4(Values[8], Values[9], Values[10], Values[11]),
                        new Vector4(Values[12], Values[13], Values[14], Values[15]));
                }
                return _unityMatrix;
            }
        }
        
        public static implicit operator Matrix4x4(SpatialTransformMatrix s)
            => s.UnityMatrix;
        
        // I think?
        public static readonly SpatialTransformMatrix IDENTITY = new SpatialTransformMatrix { Values = {
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        } }; // (row, column) => (0, 0), (0, 1), (0, 2), (0, 3), (1, 0) ...
    }
}
