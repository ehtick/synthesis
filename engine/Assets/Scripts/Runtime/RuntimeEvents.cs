using System;
using System.Reflection;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

/// <summary>
/// I'm really tired of creating manager componets we have to keep track
/// of so I'm making this class to give those static managers an update
/// and start handle.
/// </summary>

public class RuntimeEvents : MonoBehaviour {
    public static event Action OnStart;
    public static event Action OnUpdate;
    public static event Action OnStop;

    public void Start() {
        OnStart?.Invoke();
    }

    public void Update() {
        OnUpdate?.Invoke();
    }

    public void OnDestroy() {
        OnStop?.Invoke();
    }
}
