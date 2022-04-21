using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using SynthesisAPI.Utilities;

using Logger = SynthesisAPI.Utilities.Logger;

public static class ReplayManager {

    static ReplayManager() {
        RuntimeEvents.OnStart += _instance.Start;
        RuntimeEvents.OnUpdate += _instance.Update;
        RuntimeEvents.OnStop += _instance.Stop;
    }

    private class Inner {

        private List<ReplayRecorder> _recorders;


        private Inner() {
            _recorders = new List<ReplayRecorder>();
        }

        public void Start() {

        }

        public void Update() {

        }

        public void Stop() {

        }

        public void ResetRecording() {

        }

        public void RegisterRecorder(ReplayRecorder rec) {
            if (_recorders.Contains(rec)) {
                Logger.Log("Recorder already exists", LogLevel.Error);
                throw new Exception();
            }
        }

        public void ForgetRecorder(ReplayRecorder rec) {
            
        }

        private static Inner _innerInstance;
        public static Inner InnerInstance {
            get {
                if (_innerInstance == null)
                    _innerInstance = new Inner();
                return _innerInstance;
            }
        }
    }

    private static Inner _instance => Inner.InnerInstance;
}

public struct SingleRecorderKeyFrame {
    public Vector3 Position;
    public Quaternion Rotation;
    public Vector3 LinearVelocity;
    public Vector3 AngularVelocity;
}
