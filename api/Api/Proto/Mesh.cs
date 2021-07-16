using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Rendering;

using UMesh = UnityEngine.Mesh;
using UMaterial = UnityEngine.Material;

namespace SynthesisAPI.Proto {
    
    /// <summary>
    /// Partial class to add utility functions and properties to Protobuf types
    /// </summary>
    public partial class Mesh {
        // private UMesh _unityMesh = null;
        // public UMesh UnityMesh {
        //     get {
        //         if (_unityMesh == null) {
        //             _unityMesh = new UMesh();
        //             _unityMesh.indexFormat = IndexFormat.UInt32;
        //
        //             int i;
        //             var verts = new Vector3[Vertices.Count];
        //             for (i = 0; i < verts.Length; i++) {
        //                 verts[i] = Vertices[i];
        //             }
        //             var tris = new int[Triangles.Count];
        //             Triangles.CopyTo(tris, 0);
        //
        //             _unityMesh.vertices = verts;
        //             _unityMesh.triangles = tris;
        //             _unityMesh.RecalculateNormals();
        //         }
        //
        //         return _unityMesh;
        //     }
        // }
        //
        // public static implicit operator UMesh(Mesh m)
        //     => m.UnityMesh;
    }
}
