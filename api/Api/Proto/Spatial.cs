using UnityEngine;

namespace SynthesisAPI.Proto {
    public partial class Spatial {
        // private Matrix4x4 _unityMatrix;
        // public Matrix4x4 UnityMatrix {
        //     get {
        //         if (_unityMatrix == default) {
        //             _unityMatrix = new Matrix4x4(new Vector4(Matrix[0], Matrix[1], Matrix[2], Matrix[3]),
        //                 new Vector4(Matrix[4], Matrix[5], Matrix[6], Matrix[7]),
        //                 new Vector4(Matrix[8], Matrix[9], Matrix[10], Matrix[11]),
        //                 new Vector4(Matrix[12], Matrix[13], Matrix[14], Matrix[15]));
        //         }
        //         return _unityMatrix;
        //     }
        // }
        //
        // public static implicit operator Matrix4x4(Spatial s)
        //     => s.UnityMatrix;
        //
        // public static readonly Spatial IDENTITY = new Spatial { Matrix = { 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1 } };
    }
}
