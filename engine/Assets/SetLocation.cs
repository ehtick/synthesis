using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Synthesis.ModelManager;
using Synthesis.Configuration;

public class SetLocation : MonoBehaviour
{
    public GameObject gizmo;
    public MoveArrow gizmoScript;
    public void SetRobotSpawn()
    {
        if (ModelManager.primaryModel == null) return;
        ResetRobotChildren();
        Transform currentRobot = ModelManager.primaryModel._object.transform;
        GizmoManager.SpawnGizmo(gizmo, currentRobot,ModelManager.spawnLocation);        
    }
    public void ResetRobot()
    {
        if (ModelManager.primaryModel == null) return;

        ModelManager.primaryModel._object.transform.position = ModelManager.spawnLocation;
        ModelManager.primaryModel._object.transform.rotation = ModelManager.spawnRotation;

        ResetRobotChildren();
    }
    private void ResetRobotChildren()
    {
        for(int i = 0; i < ModelManager.primaryModel._object.transform.childCount; i++)
        {
            ModelManager.primaryModel._object.transform.GetChild(i).transform.localRotation = Quaternion.identity;
            ModelManager.primaryModel._object.transform.GetChild(i).transform.localPosition = new Vector3(0, 0, 0);
        }
    }
}
