//using BulletUnity;
//using Synthesis.FSM;
//using Synthesis.States;
//using Synthesis.Utils;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEditor;
using UnityEngine;

namespace Synthesis.Configuration
{
    public class MoveArrow : MonoBehaviour
    {
        private const float Scale = 0.075f;
        private Vector3 initialScale;
        private Vector3 lastArrowPoint;
        private ArrowType activeArrow;
        private bool bufferPassed;

        /// <summary>
        /// Gets or sets the active selected arrow. When <see cref="ActiveArrow"/>
        /// is changed, the "SetActiveArrow" message is broadcasted to all
        /// <see cref="SelectableArrow"/>s.
        /// </summary>
        private ArrowType ActiveArrow
        {
            get
            {
                return activeArrow;
            }
            set
            {
                activeArrow = value;
                BroadcastMessage("SetActiveArrow", activeArrow);
            }
        }

        /// <summary>
        /// Returns a <see cref="Vector3"/> representing the direction the selected
        /// arrow is facing, or <see cref="Vector3.zero"/> if no arrow is selected.
        /// </summary>
        private Vector3 ArrowDirection
        {
            get
            {
                switch (ActiveArrow)
                {
                    case ArrowType.X:
                    case ArrowType.YZ:
                        return transform.right;
                    case ArrowType.Y:
                    case ArrowType.XZ:
                        return transform.up;
                    case ArrowType.Z:
                    case ArrowType.XY:
                        return transform.forward;
                    default:
                        return Vector3.zero;
                }
            }
        }

        /// <summary>
        /// Called when the arrows are dragged.
        /// The input parameter is the position delta of the <see cref="MoveArrows"/>.
        /// </summary>
        public Action<Vector3> Translate { get; set; }

        /// <summary>
        /// Called when an arrow is first clicked.
        /// </summary>
        public Action OnClick { get; set; }

        /// <summary>
        /// Called when an arrow is released.
        /// </summary>
        public Action OnRelease { get; set; }

        /// <summary>
        /// Sets the initial position and rotation.
        /// </summary>
        private void Awake()
        {
            transform.localPosition = Vector3.zero;
            transform.localRotation = Quaternion.identity;

            initialScale = new Vector3(transform.localScale.x / transform.lossyScale.x,
                transform.localScale.y / transform.lossyScale.y, transform.localScale.z / transform.lossyScale.z);
        }

        /// <summary>
        /// Enables all colliders of any parent objects to allow for their own click detection. 
        /// </summary>
        private void OnBeforeTransformParentChanged()
        {
            SetOtherCollidersEnabled(true);
        }

        /// <summary>
        /// Disables all colliders of any parent objects to allow for proper click detection.
        /// </summary>
        private void OnTransformParentChanged()
        {
            SetOtherCollidersEnabled(false);
        }

        /// <summary>
        /// Disables all colliders of any parent objects to allow for proper click detection.
        /// </summary>
        private void OnEnable()
        {
            SetOtherCollidersEnabled(false);
        }

        /// <summary>
        /// Re-enables all colliders of any parent objects to allow for their own click detection.
        /// </summary>
        private void OnDisable()
        {
            SetOtherCollidersEnabled(true);
        }

        /// <summary>
        /// Updates the robot's position when the arrows are dragged.
        /// </summary>
        private void Update()
        {

            if (activeArrow == ArrowType.None)
                return;

            // This allows for any updates from OnClick to complete before translation starts
            if (!bufferPassed)
            {
                bufferPassed = true;
                return;
            }

            Ray mouseRay = UnityEngine.Camera.main.ScreenPointToRay(UnityEngine.Input.mousePosition);
            Vector3 currentArrowPoint;

            if (activeArrow <= ArrowType.Z)
            {
                Vector3 closestPointScreenRay;
                ClosestPointsOnTwoLines(out closestPointScreenRay, out currentArrowPoint,
                 mouseRay.origin, mouseRay.direction, transform.position, ArrowDirection);
            }
            else
            {
                Plane plane = new Plane(ArrowDirection, transform.position);

                float enter;
                plane.Raycast(mouseRay, out enter);

                currentArrowPoint = mouseRay.GetPoint(enter);
            }

            //prevents move arrows from going below field
            if (GameObject.Find("Plane") != null)
            {
                if (currentArrowPoint.y < GameObject.Find("Plane").transform.position.y) { currentArrowPoint.y = GameObject.Find("Plane").transform.position.y; lastArrowPoint.y = GameObject.Find("Plane").transform.position.y; }
            }

            if (lastArrowPoint != Vector3.zero)
            {
                //Translate?.Invoke(currentArrowPoint - lastArrowPoint);
                gameObject.transform.parent.position += currentArrowPoint-lastArrowPoint;
            }
            lastArrowPoint = currentArrowPoint;
        }

        /// <summary>
        /// Scales the arrows to maintain a constant size relative to screen coordinates.
        /// </summary>
        private void LateUpdate()
        {
            Plane plane = new Plane(UnityEngine.Camera.main.transform.forward, UnityEngine.Camera.main.transform.position);
            float dist = plane.GetDistanceToPoint(transform.position);
            transform.localScale = initialScale * Scale * dist;
            Vector3 scaleTmp = gameObject.transform.localScale;
            scaleTmp.x /= gameObject.transform.parent.localScale.x;
            scaleTmp.y /= gameObject.transform.parent.localScale.y;
            scaleTmp.z /= gameObject.transform.parent.localScale.z;
            gameObject.transform.parent = gameObject.transform.parent;
            gameObject.transform.localScale = scaleTmp;
        }

        /// <summary>
        /// Sets the active arrow when a <see cref="SelectableArrow"/> is selected.
        /// </summary>
        /// <param name="arrowType"></param>
        private void OnArrowSelected(ArrowType arrowType)
        {
            ActiveArrow = arrowType;
            lastArrowPoint = Vector3.zero;
            bufferPassed = false;

            OnClick?.Invoke();
        }

        /// <summary>
        /// Sets the active arrow to <see cref="ArrowType.None"/> when a
        /// <see cref="SelectableArrow"/> is released.
        /// </summary>
        private void OnArrowReleased()
        {
            ActiveArrow = ArrowType.None;

            OnRelease?.Invoke();
        }

        /// <summary>
        /// Enables or disables other colliders to ensure proper arrow click
        /// detection.
        /// </summary>
        /// <param name="enabled"></param>
        private void SetOtherCollidersEnabled(bool enabled)
        {
            foreach (Collider c in GetComponentsInParent<Collider>(true))
                c.enabled = enabled;

            if (transform.parent == null)
                return;

            foreach (Transform child in transform.parent)
            {
                if (child == transform)
                    continue;

                foreach (Collider c in child.GetComponentsInChildren<Collider>(true))
                    c.enabled = enabled;
            }
        }


        /// <summary>
        /// Based on a solution provided by the Unity Wiki (http://wiki.unity3d.com/index.php/3d_Math_functions).
        /// Finds the closest points on two lines.
        /// </summary>
        /// <param name="closestPointLine1"></param>
        /// <param name="closestPointLine2"></param>
        /// <param name="linePoint1"></param>
        /// <param name="lineVec1"></param>
        /// <param name="linePoint2"></param>
        /// <param name="lineVec2"></param>
        /// <returns></returns>
        private bool ClosestPointsOnTwoLines(out Vector3 closestPointLine1, out Vector3 closestPointLine2, Vector3 linePoint1, Vector3 lineVec1, Vector3 linePoint2, Vector3 lineVec2)
        {
            closestPointLine1 = Vector3.zero;
            closestPointLine2 = Vector3.zero;

            float a = Vector3.Dot(lineVec1, lineVec1);
            float b = Vector3.Dot(lineVec1, lineVec2);
            float e = Vector3.Dot(lineVec2, lineVec2);

            float d = a * e - b * b;

            // Check if lines are parallel
            if (d == 0.0f)
                return false;

            Vector3 r = linePoint1 - linePoint2;
            float c = Vector3.Dot(lineVec1, r);
            float f = Vector3.Dot(lineVec2, r);

            float s = (b * f - c * e) / d;
            float t = (a * f - c * b) / d;

            closestPointLine1 = linePoint1 + lineVec1 * s;
            closestPointLine2 = linePoint2 + lineVec2 * t;

            return true;
        }

    }
}