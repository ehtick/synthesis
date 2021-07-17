using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Mirabuf;
using UnityEngine;
using Transform = UnityEngine.Transform;
using Vector3 = Mirabuf.Vector3;
using UVector3 = UnityEngine.Vector3;

public static class UtilExtensions {
    public static void ForEachIndex<T>(this IEnumerable<T> arr, Action<int, T> act) {
        for (int i = 0; i < arr.Count(); i++) {
            act(i, arr.ElementAt(i));
        }
    }

    public static void ForEach<T, U>(this IDictionary<T, U> dict, Action<T, U> act) {
        foreach (var kvp in dict) {
            act(kvp.Key, kvp.Value);
        }
    }

    public static IEnumerable<U> Select<T, U>(this IEnumerable<T> e, Func<T, U> c) {
        List<U> l = new List<U>();
        foreach (var a in e) {
            l.Add(c(a));
        }
        return l;
    }

    public static T Find<T>(this IEnumerable<T> e, Func<T, bool> c) {
        foreach (var a in e) {
            if (c(a))
                return a;
        }
        return default;
    }

    public static void ApplyMatrix(this Transform trans, Matrix4x4 m) {
        trans.localPosition = m.GetPosition();
        trans.localRotation = m.rotation;
        trans.localScale = m.lossyScale;
    }

    // public static IEnumerable<Node> UnravelNodes(this IEnumerable<Edge> edges) {
    //     var nodes = new Node[edges.Count()];
    //     for (int i = 0; i < nodes.Length; i++) {
    //         nodes[i] = edges.ElementAt(i).Node;
    //     }
    //     return nodes;
    // }
    
    public static UVector3 GetPosition(this Matrix4x4 m)
        => new UVector3(m.m30, m.m31, m.m32);
}
