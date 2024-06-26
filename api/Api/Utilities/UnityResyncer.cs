﻿using System;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;

#nullable enable

namespace SynthesisAPI.Utilities {
    /// <summary>
    /// The Unity Resyncer schedules actions to be run on the main thread. Unity requires an annoying
    /// amount to be run on the main thread, and this should help
    ///
    /// TODO: TEST THIS
    /// </summary>
    public static class UnityResyncer {

        /// <summary>
        /// Queue an action to be run on the main thread
        /// </summary>
        /// <param name="act">Action you wish to run on the main thread</param>
        /// <returns>Handler for the action</returns>
        public static ResyncHandler Resync(Action act) {

            if (Instance == null)
                throw new Exception("Instance doesn't exist yet");

            var handler = new ResyncHandler();
            Instance.queueTasks.Enqueue((act, handler));
            return handler;
        }

        public static UnityResyncerComponent? Instance = null;
    }

    /// <summary>
    /// The actual Unity component to schedule actions to run on the main thread
    /// </summary>
    public class UnityResyncerComponent : MonoBehaviour {
        public float MaxExecuteTimeS = 0.1f;

        public Queue<(Action act, ResyncHandler handler)> queueTasks = new Queue<(Action act, ResyncHandler handler)>();

        private void Awake() {
            UnityResyncer.Instance = this;
        }

        private void Update() {
            float start = Time.realtimeSinceStartup;
            while (Time.realtimeSinceStartup - start < MaxExecuteTimeS && queueTasks.Count > 0) {
                var q = queueTasks.Dequeue();
                q.act();
                q.handler.IsDone = true;
            }
        }
    }

    /// <summary>
    /// Handler class for checking on the status of a resynced task
    ///
    /// TODO: TEST THIS
    /// </summary>
    public class ResyncHandler {
        private readonly object threadLock = new object();
        private bool isDone = false;
        public bool IsDone {
            get => isDone;
            set {
                lock (threadLock) {
                    isDone = value;
                }
            }
        }

        public void Wait(double timeOutS) {
            double start = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
            while (!isDone && DateTimeOffset.UtcNow.ToUnixTimeSeconds() - start < timeOutS) {
                Thread.Sleep(5);
            }
        }
    }
}
