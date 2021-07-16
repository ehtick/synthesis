using UnityEngine;
using UMaterial = UnityEngine.Material;

namespace Mirabuf {
    public partial class Appearance {
        private UMaterial _unityMaterial = null;
        public UMaterial UnityMaterial {
            get {
                if (_unityMaterial == null) {
                    Color32 c = new Color32((byte)Albedo.R, (byte)Albedo.G, (byte)Albedo.B, (byte)Albedo.A);
                    
                    // TODO: Something here breaks transparent materials for builds
                    _unityMaterial = new UMaterial(Shader.Find("Standard"));
                    _unityMaterial.SetColor("_Color", c);
                    if (c.a < 1.0f) {
                        _unityMaterial.SetOverrideTag("RenderTag", "Transparent");
                        _unityMaterial.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
                        _unityMaterial.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
                        _unityMaterial.SetInt("_ZWrite", 0);
                        _unityMaterial.DisableKeyword("_ALPHATEST_ON");
                        _unityMaterial.EnableKeyword("_ALPHABLEND_ON");
                        _unityMaterial.DisableKeyword("_ALPHAPREMULTIPLY_ON");
                        _unityMaterial.renderQueue = 3000;
                    }
                    _unityMaterial.SetFloat("_Roughness", Roughness);
                    // TODO: Specular and Metallic
                }
                return _unityMaterial;
            }
        }
    }
}
