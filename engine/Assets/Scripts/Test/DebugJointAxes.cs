using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

public class DebugJointAxes : MonoBehaviour{

    public static List<(Vector3 point, Matrix4x4 trans)> DebugPoints = new List<(Vector3 point, Matrix4x4 trans)>();

    public void OnDrawGizmos() {
        if (Application.isPlaying) {
            SynthesisAPI.Simulation.SimulationManager.Drivers.Select(x => x.Value).ForEach(a => a/*.Where(c => c.Name == "4e87bf7e-2e13-4c09-9fa4-623027409f7c")*/.ForEach(y => {
                if (y is SynthesisAPI.Simulation.RotationalDriver) {

                    var ArmDriver = y as SynthesisAPI.Simulation.RotationalDriver;

                    var anchorA = ArmDriver.JointA.anchor;
                    var axisA = ArmDriver.JointA.axis;
                    var anchorB = ArmDriver.JointB.anchor;
                    var axisB = ArmDriver.JointB.axis;

                    Vector3 globalAnchorA = ArmDriver.JointA.gameObject.transform.localToWorldMatrix.MultiplyPoint(anchorA);
                    Vector3 globalAxisA = ArmDriver.JointA.gameObject.transform.localToWorldMatrix.MultiplyVector(axisA);
                    Vector3 globalAnchorB = ArmDriver.JointB.gameObject.transform.localToWorldMatrix.MultiplyPoint(anchorB);
                    Vector3 globalAxisB = ArmDriver.JointB.gameObject.transform.localToWorldMatrix.MultiplyVector(axisB);

                    Gizmos.color = Color.green;
                    Gizmos.DrawSphere(globalAnchorA, 0.01f);
                    Gizmos.DrawLine(globalAnchorA, globalAnchorA + (globalAxisA.normalized * 0.2f));
                    // Gizmos.color = Color.magenta;
                    // Gizmos.DrawSphere(globalAnchorB, 0.01f);
                    // Gizmos.DrawLine(globalAnchorB, globalAnchorB + (globalAxisB.normalized * 0.2f));

                    // Gizmos.color = Color.white;
                    // Gizmos.DrawSphere(ArmDriver.JointA.gameObject.transform.position, 0.05f);
                    // Gizmos.DrawSphere(ArmDriver.JointB.gameObject.transform.position, 0.05f);
                }
            }));
            DebugPoints.ForEach(x => {
                Gizmos.color = Color.red;
                Gizmos.DrawSphere(x.trans.MultiplyPoint(x.point), 0.001f);
            });
        }
    }
}
