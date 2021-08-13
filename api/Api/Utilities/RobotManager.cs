﻿using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using Mirabuf.Signal;
using Google.Protobuf;

namespace SynthesisAPI.Utilities
{
    
    public sealed class RobotManager
    {
        

        private Thread queueThread;
        private bool _isRunning = false;
        public bool IsRunning
        {
            get
            {
                return _isRunning; 
            }
            private set
            {
                _isRunning = value;
                if (!value)
                {
                    if (queueThread != null && queueThread.IsAlive)
                    {
                        queueThread.Join();
                    }
                }
            }
        }

        public Dictionary<string, ControllableState> Robots { get; private set; }
        public ConcurrentQueue<UpdateSignals> UpdateQueue { get; private set; }

        private static readonly Lazy<RobotManager> lazy = new Lazy<RobotManager>(() => new RobotManager());
        public static RobotManager Instance { get { return lazy.Value; } }
        private RobotManager()
        {
            Robots = new Dictionary<string, ControllableState>();
            UpdateQueue = new ConcurrentQueue<UpdateSignals>();
        }

        public void Start()
        {
            if (RobotManager.Instance.IsRunning) return;
            RobotManager.Instance.IsRunning = true;
            queueThread = new Thread(() =>
            {
                while (IsRunning)
                {
                    if (UpdateQueue.TryDequeue(out UpdateSignals tmp))
                        Robots[tmp.Guid.ToStringUtf8()].Update(tmp);
                }
            });
            queueThread.Start();
        }

        public void Stop()
        {
            IsRunning = false;
        }

        public void AddSignalLayout(Signals signalLayout)
        {
            Robots[signalLayout.Info.GUID] = new ControllableState()
            {
                CurrentSignalLayout = signalLayout
            };
        }
    }
}
