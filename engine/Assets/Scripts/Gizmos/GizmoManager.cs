
using UnityEngine;
/// <summary>
/// Manages Gizmos and ensures only one gizmo spawns at a time.
/// </summary>
public static class GizmoManager 
{

    private static GameObject gizmo = null;
    public static GameObject currentGizmo
    {
        get => gizmo;
    }
    /// <summary>
    /// Activates a Gizmo on a given Transform parent object
    /// </summary>
    /// <param name="Gizmo"></param>
    /// <param name="parent"></param>
    /// <param name="forceClose"></param>
    /// <returns></returns>
    public static bool SpawnGizmo(GameObject Gizmo, Transform parent, bool forceClose = false)
    {
        if (gizmo != null)
            if (forceClose)
                Object.Destroy(gizmo);
            else
                return false;
        var g = Object.Instantiate(Gizmo,parent);//set transform
        gizmo = g;
        return true;
    }
    /// <summary>
    /// Destroys the Gizmo
    /// </summary>
    public static void ExitGizmo()
    {
        Object.Destroy(gizmo);
    }
}