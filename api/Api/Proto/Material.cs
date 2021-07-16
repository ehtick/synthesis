using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Text;
using UnityEngine;

using UMaterial = UnityEngine.Material;

namespace SynthesisAPI.Proto {
    /// <summary>
    /// Partial class to add utility functions and properties to Protobuf types
    /// TODO: Enable GPU instancing
    /// </summary>
    public partial class Material {

        // private UMaterial _unityMaterial = null;
        // public UMaterial UnityMaterial {
        //     get {
        //         if (_unityMaterial == null) {
        //             Color c = new Color32((byte)Red, (byte)Green, (byte)Blue, (byte)Alpha);
        //
        //             // TODO: Something here breaks transparent materials for builds
        //             _unityMaterial = new UMaterial(Shader.Find("Standard"));
        //             _unityMaterial.SetColor("_Color", c);
        //             if (c.a < 1.0f) {
        //                 _unityMaterial.SetOverrideTag("RenderTag", "Transparent");
        //                 _unityMaterial.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
        //                 _unityMaterial.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
        //                 _unityMaterial.SetInt("_ZWrite", 0);
        //                 _unityMaterial.DisableKeyword("_ALPHATEST_ON");
        //                 _unityMaterial.EnableKeyword("_ALPHABLEND_ON");
        //                 _unityMaterial.DisableKeyword("_ALPHAPREMULTIPLY_ON");
        //                 _unityMaterial.renderQueue = 3000;
        //             }
        //             _unityMaterial.SetFloat("_Roughness", 1.0f - Specular);
        //         }
        //         return _unityMaterial;
        //     }
        // }
        //
        // public static implicit operator UMaterial(Material m)
        //     => m.UnityMaterial;
        //
        // public static explicit operator Material(BXDAMesh.BXDASurface surface) {
        //     Material mat = new Material();
        //     if (surface.hasColor) {
        //         mat.Red = (int)(surface.color & 0xFF);
        //         mat.Green = (int)((surface.color >> 8) & 0xFF);
        //         mat.Blue = (int)((surface.color >> 16) & 0xFF);
        //         mat.Alpha = (int)((surface.color >> 24) & 0xFF);
        //         if (surface.transparency != 0)
        //             mat.Alpha = (int)(surface.transparency * 255f);
        //         else if (surface.translucency != 0)
        //             mat.Alpha = (int)(surface.translucency * 255f);
        //         if (mat.Alpha == 0) // No invisible objects
        //             mat.Alpha = 10;
        //         mat.Emissive = false;
        //         mat.Specular = surface.specular;
        //     } else {
        //         // Default Color
        //         mat = new Material() { Red = 7, Green = 7, Blue = 7, Alpha = 255, Emissive = false, Specular = 0.0f };
        //     }
        //
        //     return mat;
        // }
    }
}
