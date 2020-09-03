﻿using MathNet.Spatial.Euclidean;
using MathNet.Spatial.Units;
using SynthesisAPI.InputManager;
using SynthesisAPI.InputManager.InputEvents;
using SynthesisAPI.InputManager.Inputs;
using SynthesisAPI.EnvironmentManager;
using SynthesisAPI.EnvironmentManager.Components;
using SynthesisAPI.Modules.Attributes;
using SynthesisAPI.Utilities;
using SynthesisAPI.UIManager;

#nullable enable

namespace SynthesisCore.EntityControl
{
    [InitializationPriority(2)]
    public class CameraController : SystemBase
    {
        public static CameraController Instance;
        public static double SensitivityX { get => 2; } // TODO: integrate with preference manager
        public static double SensitivityY { get => 2; }
        public static double SensitivityZoom { get => 3; }

        public static double SpeedModifier => UseSpeedModifier ? 3 : 1;
        private static bool UseSpeedModifier = false;

        private bool inFreeRoamMode = true;

        private bool isMouseDragging = false;

        public Vector3D FocusPoint { get; private set; } = new Vector3D(); // Default focus point
        private Vector3D offset = new Vector3D();

        private Entity? cameraEntity = null;
        public Transform CameraTransform { get; private set; }

        /// <summary>
        /// An optional target to focus on
        /// </summary>
        private Selectable? SelectedTarget = null;
        private Selectable? LastSelectedTarget = null;
        private Selectable.SelectionType LastSelectedTargetType = Selectable.SelectionType.Unselected;

        public static bool EnableCameraPan = true;

        // These variables are used to move the camera when a new target is selected
        private bool isCameraMovingToNewFocus = false;
        private double moveTime;
        private Vector3D cameraMoveStartPosition;
        // private Quaternion startRotation;
        // private Quaternion targetRotation;
        private double timeToReachNewFocus;
        private const double MoveCameraToFocusTime = 0.1; // sec
        private const double MoveToFocusCameraMinSpeed = 8; // distance per sec
        private const double MoveToFocusCameraMinDistance = 10; // distance

        private double xMod = 0, yMod = 0, zMod = 0, lastXMod = 0, lastYMod = 0, lastZMod = 0; // Used for accelerating the camera movement speed

        private static readonly Vector3D StartPosition = new Vector3D(5, 5, 5);
        private const double MinDistance = 0.25;
        private const double MaxDistance = 50;
        private const double MinHeight = 0.25;
        private static double FreeRoamCameraMoveDelta => 0.03 * SpeedModifier;

        public struct CameraState
        {
            private Vector3D position;
            private Quaternion rotation;
            private Selectable? selectedTarget;
            private Selectable.SelectionType lastSelectedTargetType;
            private Vector3D focusPoint;
            private bool inFreeRoamMode;

            public static CameraState Save()
            {
                return new CameraState
                {
                    position = Instance.CameraTransform.Position,
                    rotation = Instance.CameraTransform.Rotation,
                    selectedTarget = Instance.SelectedTarget,
                    lastSelectedTargetType = Instance.LastSelectedTargetType,
                    focusPoint = Instance.FocusPoint,
                    inFreeRoamMode = Instance.inFreeRoamMode
                };
            }

            public static void Restore(CameraState cameraState)
            {
                Instance.LastSelectedTargetType = cameraState.lastSelectedTargetType;
                Instance.SelectedTarget = cameraState.selectedTarget;
                Instance.SetNewFocus(cameraState.focusPoint, true);
                Instance.inFreeRoamMode = cameraState.inFreeRoamMode;
                Instance.CameraTransform.Position = cameraState.position;
                Instance.CameraTransform.Rotation = cameraState.rotation;
            }
        }

        public override void Setup()
        {
            if(Instance == null)
            {
                Instance = this;
            }

            if (cameraEntity == null)
            {
                cameraEntity = EnvironmentManager.AddEntity();
                if (cameraEntity == null)
                    throw new SynthesisException("Failed to create camera");
                cameraEntity.Value.AddComponent<Camera>();
                var trans = cameraEntity.Value.AddComponent<Transform>();
                CameraTransform = trans ?? throw new SynthesisException("Failed to create camera transform");
                CameraTransform.PositionValidator = (Vector3D position) =>
                {
                    if (position.Y < MinHeight)
                    {
                        position = new Vector3D(position.X, MinHeight, position.Z);
                    }
                    return position;
                };
                CameraTransform.Position = StartPosition;
                CameraTransform.LookAt(new Vector3D());
            }
            // Bind controls for free roam
            InputManager.AssignDigitalInput("camera_forward", new Digital("w"));
            InputManager.AssignDigitalInput("camera_left", new Digital("a"));
            InputManager.AssignDigitalInput("camera_backward", new Digital("s"));
            InputManager.AssignDigitalInput("camera_right", new Digital("d"));
            InputManager.AssignDigitalInput("camera_up", new Digital("space"));
            InputManager.AssignDigitalInput("camera_down", new Digital("left shift"));
            InputManager.AssignDigitalInput("camera_boost", new Digital("left ctrl"));

            // Bind controls for orbit
            InputManager.AssignDigitalInput("camera_drag", new Digital("mouse 0 non-ui")); // TODO put control settings in preference manager
            InputManager.AssignAxis("ZoomCamera", new Analog("Mouse ScrollWheel"));
            InputManager.AssignAxis("Mouse X", new Analog("Mouse X"));
            InputManager.AssignAxis("Mouse Y", new Analog("Mouse Y"));
        }

        public override void Teardown() { }

        [TaggedCallback("input/camera_forward")]
        public void CameraForward(DigitalEvent digitalEvent)
        {
            if (inFreeRoamMode && CameraTransform != null && digitalEvent.State == DigitalState.Held)
            {
                var forward = CameraTransform.Forward;
                forward = new Vector3D(forward.X, 0, forward.Z).Normalize();
                CameraTransform.Position += forward.ScaleBy(FreeRoamCameraMoveDelta);
            }
        }

        [TaggedCallback("input/camera_backward")]
        public void CameraBackward(DigitalEvent digitalEvent)
        {
            if (inFreeRoamMode && CameraTransform != null && digitalEvent.State == DigitalState.Held)
            {
                var forward = CameraTransform.Forward;
                forward = new Vector3D(forward.X, 0, forward.Z).Normalize();
                CameraTransform.Position += forward.ScaleBy(-FreeRoamCameraMoveDelta);
            }
        }

        [TaggedCallback("input/camera_left")]
        public void CameraLeft(DigitalEvent digitalEvent)
        {
            if (inFreeRoamMode && CameraTransform != null && digitalEvent.State == DigitalState.Held)
            {
                CameraTransform.Position += CameraTransform.Forward.CrossProduct(UnitVector3D.YAxis).ScaleBy(FreeRoamCameraMoveDelta);
            }
        }

        [TaggedCallback("input/camera_right")]
        public void CameraRight(DigitalEvent digitalEvent)
        {
            if (inFreeRoamMode && CameraTransform != null && digitalEvent.State == DigitalState.Held)
            {
                CameraTransform.Position += CameraTransform.Forward.CrossProduct(UnitVector3D.YAxis).ScaleBy(-FreeRoamCameraMoveDelta);
            }
        }

        [TaggedCallback("input/camera_up")]
        public void CameraUp(DigitalEvent digitalEvent)
        {
            if (inFreeRoamMode && CameraTransform != null && digitalEvent.State == DigitalState.Held)
            {
                CameraTransform.Position += UnitVector3D.YAxis.ScaleBy(FreeRoamCameraMoveDelta);
            }
        }

        [TaggedCallback("input/camera_down")]
        public void CameraDown(DigitalEvent digitalEvent)
        {
            if (inFreeRoamMode && CameraTransform != null && digitalEvent.State == DigitalState.Held)
            {
                CameraTransform.Position += UnitVector3D.YAxis.ScaleBy(-FreeRoamCameraMoveDelta);
            }
        }

        [TaggedCallback("input/camera_boost")]
        public void CameraBoost(DigitalEvent digitalEvent)
        {
            UseSpeedModifier = inFreeRoamMode && digitalEvent.State == DigitalState.Held;
        }

        /// <summary>
        /// Function used to switch orbit control on and off
        /// </summary>
        /// <param name="e"></param>
        [TaggedCallback("input/camera_drag")]
        public void StartMouseDrag(DigitalEvent digitalEvent)
        {
            isMouseDragging = digitalEvent.State == DigitalState.Held;
            if (digitalEvent.State == DigitalState.Down)
            {
                // TODO cursor stuff
                // Cursor.lockState = CursorLockMode.Locked; // Hide and lock cursor so the mouse doesn't leave the screen
                // Cursor.visible = false;
            }
            else if (digitalEvent.State == DigitalState.Up)
            {
                // Cursor.lockState = CursorLockMode.None; // Show and unlock cursor when done
                // Cursor.visible = true;
            }
        }

        private void ProcessOrbit()
        {
            if (isMouseDragging)
            {
                // Rotate horizontally (i.e. around y-axis)
                var xDelta = offset.Rotate(UnitVector3D.YAxis, Angle.FromDegrees(-xMod)) - offset;

                // Rotate vertically
                var verticalRotationAxis = offset.CrossProduct(UnitVector3D.YAxis).Normalize();
                Vector3D yDelta = offset.Rotate(verticalRotationAxis, Angle.FromDegrees(-yMod)) - offset;

                // Stop from vertically rotating past directly above the focus point
                var newOffset = offset + yDelta;
                if (!Math.SameSign(newOffset.X, offset.X) || !Math.SameSign(newOffset.Z, offset.Z))
                {
                    yDelta = new Vector3D(0, 0, 0);
                }

                offset += xDelta + yDelta;
            }
            if (zMod != 0)
            {
                var mod = -zMod;
                // Prevent from moving too close or too far away from focus
                if ((offset.Length > MinDistance && mod < 0) || (offset.Length < MaxDistance && mod > 0))
                {
                    offset += offset.Normalize().ScaleBy(mod);
                }
            }
        }

        private void UpdateOrbitCameraPosition()
        {
            if (CameraTransform != null)
            {
                CameraTransform.Position = FocusPoint + offset;
                CameraTransform.LookAt(FocusPoint);
            }
        }

        private void ProcessFreeRoam()
        {
            if (CameraTransform != null)
            {
                if (isMouseDragging)
                {
                    var newRotation = MathUtil.Rotate(CameraTransform.Rotation, UnitVector3D.XAxis, yMod);
                    var newForward = MathUtil.QuaternionToForwardVector(newRotation);

                    // Stop from vertically rotating past looking directly up/down
                    if (Math.SameSign(newForward.X, CameraTransform.Forward.X) && Math.SameSign(newForward.Z, CameraTransform.Forward.Z))
                    {
                        CameraTransform.Rotation = newRotation;
                    }
                    CameraTransform.Rotate(UnitVector3D.YAxis, xMod, true);
                }
                CameraTransform.Position += zMod * CameraTransform.Forward;
            }
        }

        public void SetNewFocus(Vector3D newFocusPoint, bool moveToPoint)
        {
            FocusPoint = newFocusPoint;
            
            moveTime = 0;
            cameraMoveStartPosition = CameraTransform.Position;

            //startRotation = cameraTransform.Rotation;
            //targetRotation = MathUtil.LookAt((-offset).Normalize()).Normalized;

            offset = cameraMoveStartPosition - FocusPoint;
            isCameraMovingToNewFocus = moveToPoint && offset.Length > MoveToFocusCameraMinDistance;

            timeToReachNewFocus = Math.Min(MoveCameraToFocusTime, offset.Length / MoveToFocusCameraMinSpeed);

            UpdateOrbitCameraPosition();
        }

        private void UpdateMouseInput()
        {
            zMod = UIManager.CursorBlockedByUI ? 0 : InputManager.GetAxisValue("ZoomCamera") * SensitivityZoom;

            if (zMod != 0 && Math.SameSign(zMod, lastZMod))
                zMod += lastZMod * 0.5f;

            lastZMod = zMod == 0 ? lastZMod : zMod;

            if (isMouseDragging && EnableCameraPan)
            {
                // Add an intertial effect to camera movement (TODO use actual last cameraTransform.Position delta instead?), and add an option to enable this to preference manager
                xMod = -InputManager.GetAxisValue("Mouse X") * SensitivityX;
                yMod = InputManager.GetAxisValue("Mouse Y") * SensitivityY;

                if (xMod != 0 && Math.SameSign(xMod, lastXMod))
                    xMod += lastXMod * 0.3f;
                if (yMod != 0 && Math.SameSign(yMod, lastYMod))
                    yMod += lastYMod * 0.3f;

                lastXMod = xMod == 0 ? lastXMod : xMod;
                lastYMod = yMod == 0 ? lastYMod : yMod;
            }
            else
            {
                xMod = 0;
                lastXMod = 0;
                yMod = 0;
                lastYMod = 0;
            }
        }

        public override void OnUpdate()
        {
            UpdateMouseInput();

            SelectedTarget = Selectable.Selected;
            inFreeRoamMode = SelectedTarget == null;

            if (inFreeRoamMode) // Free roam mode
            {
                ProcessFreeRoam();
            }
            else // Orbit mode
            {
                var newFocusPoint = SelectedTarget?.Entity?.GetComponent<Transform>()?.GlobalPosition;
                if (newFocusPoint.HasValue)
                {
                    if (SelectedTarget != LastSelectedTarget || LastSelectedTargetType != SelectedTarget.State) // Set new focus point
                    {
                        SetNewFocus(newFocusPoint.Value, SelectedTarget.State == Selectable.SelectionType.ExtendedSelection);
                    }
                    else // Update possibly moving focus point
                    {
                        FocusPoint = newFocusPoint.Value;
                    }
                }

                if (isCameraMovingToNewFocus)
                {
                    moveTime += Time.TimeSinceLastFrameUpdate;
                    var lerpFactor = moveTime / timeToReachNewFocus;

                    CameraTransform.Position = MathUtil.Lerp(cameraMoveStartPosition, FocusPoint, lerpFactor);
                    offset = CameraTransform.Position - FocusPoint;

                    // TODO fix lerp camera rotation
                    //cameraTransform.Rotation = MathUtil.Lerp(startRotation, targetRotation, lerpFactor).Normalized;
                    //cameraTransform.Rotation = MathUtil.RotateTowards(cameraTransform.Rotation, targetRotation, 5 * Time.TimeSinceLastFrameUpdate).Normalized;

                    isCameraMovingToNewFocus = offset.Length > MoveToFocusCameraMinDistance;// && !Math.ApproxEquals(cameraTransform.Rotation - targetRotation, Quaternion.Zero);
                }
                else
                {
                    ProcessOrbit();
                    UpdateOrbitCameraPosition();
                }
            }

            LastSelectedTarget = SelectedTarget;
            LastSelectedTargetType = SelectedTarget?.State ?? Selectable.SelectionType.Unselected;
        }
        public override void OnPhysicsUpdate() { }
    }
}