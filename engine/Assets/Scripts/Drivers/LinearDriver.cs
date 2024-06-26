using UnityEngine;
using SynthesisAPI.Simulation;
using Synthesis.PreferenceManager;
using Google.Protobuf.WellKnownTypes;
using Synthesis.Physics;

namespace Synthesis {
    public class LinearDriver : Driver {
        public string Signal => _inputs[0];

        public ConfigurableJoint JointA { get; private set; }
        public ConfigurableJoint JointB { get; private set; }
        private float _lastVel = 0;
        public float _position = 0f;
        public float Position {
            get => _position;
        private
            set {
                var newPos             = Mathf.Clamp(value, Limits.Lower, Limits.Upper);
                JointA.connectedAnchor = JointA.anchor + (JointA.axis * newPos);
                if (newPos == Limits.Lower || newPos == Limits.Upper)
                    _lastVel = 0;
                _position = newPos;
            }
        }
        // Note: only used to save between sessions
        private JointMotor _motor;
        public JointMotor Motor {
            get => _motor;
            set {
                _motor = value;
                SimulationPreferences.SetRobotJointMotor((_simObject as RobotSimObject)!.RobotGUID, Name, _motor);
            }
        }
        public (float Upper, float Lower) Limits { get; private set; }

        public double MainInput {
            get {
                if (PhysicsManager.IsFrozen)
                    return 0f;
                var val = State.GetValue(_inputs[0]);
                return val == null ? 0.0 : val.NumberValue;
            }
            set => State.SetValue(_inputs[0], Value.ForNumber(value));
        }

        public new string Name => State.SignalMap[_inputs[0]].Name;

        public readonly string MotorRef;

        public LinearDriver(string name, string[] inputs, string[] outputs, SimObject simObject,
            ConfigurableJoint jointA, ConfigurableJoint jointB, (float, float) limits, string motorRef)
            : base(name, inputs, outputs, simObject) {
            // Takeover joint configuration and make it more suited to control rather than passive
            var l              = jointA.linearLimit;
            l.limit            = 0f;
            jointA.linearLimit = l;

            JointA   = jointA;
            JointB   = jointB;
            Position = 0f;
            Limits   = limits;
            MotorRef = motorRef;

            var motor = SimulationPreferences.GetRobotJointMotor((simObject as RobotSimObject)!.RobotGUID, motorRef);

            if (motor != null) {
                _motor = motor.Value;
            } else {
                Motor = new JointMotor() {
                    force          = 0.1f,
                    freeSpin       = false,
                    targetVelocity = 0.2f,
                };
            }
        }

        public override void Update() {
            // TODO: Position

            // VelocityControl

            float value = (float) MainInput;

            var tarVel = value * _motor.targetVelocity;

            var delta         = tarVel - _lastVel;
            var possibleDelta = _motor.force * Time.deltaTime; // Force = acceleration in M/S/S

            if (Mathf.Abs(delta) > possibleDelta)
                delta = possibleDelta * Mathf.Sign(delta);

            _lastVel += delta;

            if (Mathf.Abs(_lastVel * Time.deltaTime) > _motor.targetVelocity)
                _lastVel = _motor.targetVelocity * Mathf.Sign(_lastVel);

            Position += _lastVel * Time.deltaTime;
        }
    }
}
