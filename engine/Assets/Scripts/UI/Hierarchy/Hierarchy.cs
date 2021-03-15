﻿using Synthesis.UI.Hierarchy.HierarchyItems;
using UnityEngine;

namespace Synthesis.UI.Hierarchy
{
    public class Hierarchy : MonoBehaviour
    {
        public static Hierarchy HierarchyInstance { get; private set; }

        public HierarchyFolderItem rootFolder;
        public static HierarchyFolderItem RootFolder => HierarchyInstance.rootFolder;
        public GameObject folderPrefab;
        public static GameObject FolderPrefab => HierarchyInstance.folderPrefab;
        public GameObject itemPrefab;
        public static GameObject ItemPrefab => HierarchyInstance.itemPrefab;
        public GameObject contentContainer;
        public static GameObject ContentContainer => HierarchyInstance.contentContainer;
        public static bool Changes = true;

        public float TabSize = 20f;

        private void Awake() {
            HierarchyInstance = this;
        }

        public void Start() {
            rootFolder.Init("Scene", null);

            var robots = rootFolder.CreateFolder("Robots");
            var fields = rootFolder.CreateFolder("Fields");

            robots.CreateItem("997 Spartan Robotics");
            robots.CreateItem("1425 Error Code");

            fields.CreateItem("2020 Infinite Recharge");

            /*
            RootFolder
                Folder A
                    Item AA
                    Folder AA
                        Item AAA
                    Item AB
                Item A
                Folder B
                    Item BA
            */

            // Big Test
            /*var folderA = RootFolder.CreateFolder("Folder A");
            var itemA = RootFolder.CreateItem("Item A");
            var folderB = RootFolder.CreateFolder("Folder B");

            var itemAA = folderA.CreateItem("Item AA");
            var folderAA = folderA.CreateFolder("Folder AA");
            var itemAB = folderA.CreateFolder("Item AB");

            var itemAAA = folderAA.CreateItem("Item AAA");

            var itemBA = folderB.CreateItem("Item BA");*/

            // folderB.Remove();
            // folderAA.Add(folderB);

            // RootFolder.DebugPrint();
        }

        public void Update() {
            if (Changes) {
                Changes = false;
                float heightAccum = RootFolder.GetComponent<RectTransform>().rect.height;
                RectTransform t;
                for (int i = 0; i < RootFolder.Items.Count; i++) {
                    if (RootFolder.Items[i].item.Visible) {
                        float tabSize = RootFolder.Items[i].item.Depth * TabSize;
                        t = RootFolder.Items[i].item.GetComponent<RectTransform>();
                        t.offsetMin = new Vector2(tabSize, t.offsetMin.y);
                        t.localPosition = new Vector3(t.localPosition.x, -heightAccum, t.localPosition.z);
                        heightAccum += t.rect.height;
                    }
                }
            }
        }
    }
}