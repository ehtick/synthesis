using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ReplayRecorder : MonoBehaviour {

    private Rigidbody _rigidBody;

    public void Start() {
        _rigidBody = GetComponent<Rigidbody>();

    }

    public override int GetHashCode()
        => gameObject.GetHashCode();
    public override bool Equals(object other) {
        if (ReferenceEquals(other, null) || !(other is ReplayRecorder))
            return false;

        return (other as ReplayRecorder).GetHashCode() == GetHashCode();
    }
}
