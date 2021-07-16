using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Synthesis.ModelManager;
using Synthesis.ModelManager.Models;
using System.Linq;
using Synthesis.UI.Bars;
using Newtonsoft.Json;

public class MyTest : MonoBehaviour {
    public Transform ExampleTransform;
    
    public void Start() {
        var m1 = Matrix4x4.TRS(new Vector3(1, 5, 3), Quaternion.Euler(0, 45, 0), Vector3.one);
        var m2 = Matrix4x4.TRS(Vector3.zero, Quaternion.Euler(30, 0, 0), Vector3.one);
        var m3 = m1 * m2;
        PrintMatrix4x4(m1 * m2);
        ExampleTransform.localPosition = new Vector3(m3.m30, m3.m31, m3.m32);
        ExampleTransform.rotation = m3.rotation;
        ExampleTransform.localScale = m3.lossyScale;
    }

    public void PrintMatrix4x4(Matrix4x4 m) {
        string a = "";
        for (int y = 0; y < 4; y++) {
            for (int x = 0; x < 4; x++) {
                a += $"{Math.Round(m[y, x], 3)},";
            }
            a += "\n";
        }
        Debug.Log(a);
    }
}
