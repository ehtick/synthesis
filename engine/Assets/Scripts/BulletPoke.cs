using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Synthesis.Physics;

public class BulletPoke : MonoBehaviour {

    private List<Vector3> Contacts = new List<Vector3>();

    private void Update() {
        if (Input.GetKeyDown(KeyCode.X)) {
            Contacts.Clear();
            Debug.Log("Cleared Contacts");
        }

        if (Input.GetKey(KeyCode.G)) {
            float castDistance = 20;
            Vector3 from = Camera.main.transform.position;
            Vector3 to = from + ((Camera.main.ScreenToWorldPoint(new Vector3(Input.mousePosition.x, Input.mousePosition.y, 1)) - from).normalized * castDistance);
            var res = PhysicsHandler.RayCastClosest(from.ToBullet(), to.ToBullet());

            if (res.hit) {
                Debug.Log("Hit");
                Contacts.Add(res.hit_point.ToUnity());
            } else {
                Debug.Log("Miss");
            }
        }
    }

    public void OnDrawGizmos() {
        #if UNITY_EDITOR
        if (Application.isPlaying) {
            Gizmos.color = Color.red;
            foreach (var p in Contacts) {
                Gizmos.DrawSphere(p, 0.002f);
            }
        }
        #endif
    }
}
