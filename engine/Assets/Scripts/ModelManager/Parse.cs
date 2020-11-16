﻿using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using SharpGLTF.IO;
using SharpGLTF.Schema2;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Synthesis.ModelManager
{
    public static class Parse
    {
        //for testing call -> Synthesis.ModelManager.Parse.AsRobot("Assets/Testing/Test.glb");

        private static bool tryFix = true;

        private const float defaultMass = 1;

        /// <summary>
        /// This is a collection of rigidbody objects
        /// </summary>
        private static readonly Dictionary<string, UnityEngine.Rigidbody> RigidbodyCache = new Dictionary<string, UnityEngine.Rigidbody>();
        
        /// <summary>
        /// This is a collection of MeshColliders
        /// </summary>
        private static readonly List<MeshCollider> Colliders = new List<MeshCollider>();

        public static GameObject AsRobot(string filePath)
        {
            var model = GetModelInfo(filePath);
            var gameObject = CreateGameObject(model.DefaultScene.VisualChildren.First());
            ParseJoints(model);
            /*for(int i = 0; i < colliders.Count; i++)
            {
                for(int j = i + 1; j < colliders.Count; j++)
                {
                    Physics.IgnoreCollision(colliders[i], colliders[j]);
                }
            }*/
            Colliders.Clear();
            RigidbodyCache.Clear();
            return gameObject;
        }

        public static GameObject AsField(string filePath)
        {
            return null;
        }

        private static ModelRoot GetModelInfo(string filePath)
        {
            //set up file
            var data = File.ReadAllBytes(filePath);
            
            var stream = new MemoryStream();
            stream.Write(data, 0, data.Length);
            stream.Position = 0;

            //read glb
            var settings = tryFix ? SharpGLTF.Validation.ValidationMode.TryFix : SharpGLTF.Validation.ValidationMode.Strict;
            return ModelRoot.ReadGLB(stream, settings);
        }

        private static GameObject CreateGameObject(Node node, Node parent = null)
        {
            if (parent != null)
            {
                var scale = node.LocalTransform.Scale;
                var parentScale = parent.LocalTransform.Scale;
                scale.X *= parentScale.X;
                scale.Y *= parentScale.Y;
                scale.Z *= parentScale.Z;
                var localTransform = node.LocalTransform;
                localTransform.Scale = scale;
                node.LocalTransform = localTransform;
            }

            var gameObject = new GameObject {name = node.Name};

            ParseTransform(node, gameObject);
            
            if(node.Mesh != null)
            {
                ParseMesh(node, gameObject);
                ParseMeshCollider(node, gameObject);
                ParseRigidBody(node, gameObject);
            }

            // not sure every object should have a joint
            foreach(var child in node.VisualChildren)
            {
                var childObject = CreateGameObject(child,node);
                childObject.transform.parent = gameObject.transform;
                var joint = childObject.AddComponent<FixedJoint>();
                joint.connectedBody = gameObject.GetComponent<Rigidbody>();
            }
            return gameObject;
        }

        private static void ParseTransform(Node node, GameObject gameObject)
        {
            var transform = gameObject.transform;
            var nodeTransform = node.LocalTransform;
            transform.localPosition = new Vector3(nodeTransform.Translation.X * nodeTransform.Scale.X, nodeTransform.Translation.Y * nodeTransform.Scale.Y, nodeTransform.Translation.Z * nodeTransform.Scale.Z);
            transform.localRotation = new Quaternion(nodeTransform.Rotation.X, nodeTransform.Rotation.Y, nodeTransform.Rotation.Z, nodeTransform.Rotation.W);
        }

        private static void ParseMesh(Node node, GameObject gameObject)
        {
            //mesh
            var scale = node.LocalTransform.Scale;
            var vertices = new List<Vector3>();
            // var uvs = new List<Vector2>();
            var triangles = new List<int>();
            
            var filter = gameObject.AddComponent<UnityEngine.MeshFilter>();

            var material = new UnityEngine.Material(Shader.Find("Standard"));
            
            var c = vertices.Count();
            
            // this is a terrible parsing system - I don't have a better one other than using protobuf
            foreach (var primitive in node.Mesh.Primitives)
            {
                // checks for POSITION or NORMAL vertex as not all designs have both (TODO: This doesn't trip, if it did would we screw up the triangles?)
                if (primitive == null) continue;

                // checks if material exists and converts it to a color
                if (primitive.Material?.Channels != null)
                {
                    material.color = ChannelsToColor(primitive.Material.Channels);
                    material.name = primitive.Material.Name;
                }

                if (primitive.VertexAccessors.ContainsKey("POSITION"))
                {
                    var primitiveVertices = primitive.GetVertices("POSITION").AsVector3Array();
                    foreach (var vertex in primitiveVertices)
                        vertices.Add(new Vector3(vertex.X * scale.X, vertex.Y * scale.Y, vertex.Z * scale.Z));
                }
                    
                var primitiveTriangles = primitive.GetIndices();
                
                // shawn: make your null checks before hand
                triangles.AddRange(primitiveTriangles.Select(t => (int) t + c));
            }

            filter.mesh = new UnityEngine.Mesh
            {
                vertices = vertices.ToArray(), 
                triangles = triangles.ToArray()
            };
            
            filter.mesh.RecalculateNormals();

            var renderer = gameObject.AddComponent<UnityEngine.MeshRenderer>();
            renderer.material = material;
        }

        private static void ParseMeshCollider(Node node, GameObject gameObject)
        {
            var collider = gameObject.AddComponent<MeshCollider>();
            collider.convex = true; //outside
            collider.sharedMesh = gameObject.GetComponent<MeshFilter>().mesh; //attach mesh
            
            Colliders.Add(collider); // why is this needed?
        }

        private static void ParseRigidBody(Node node, GameObject gameObject)
        {
            var rigidbody = gameObject.AddComponent<Rigidbody>();

            //mass
            if (((JsonDictionary) node.Mesh.Extras).TryGetValue("physicalProperties", out object physicalProperties) && ((JsonDictionary) physicalProperties).TryGetValue("mass", out object massStr))
                rigidbody.mass = float.TryParse(massStr.ToString(), out var mass) ? mass : defaultMass;
            
            RigidbodyCache.Add((node.Extras as JsonDictionary)?.Get<string>("uuid") ?? string.Empty, rigidbody);
        }

        private static void ParseJoints(ModelRoot model)
        {
            var joints = (model.Extras as JsonDictionary)?["joints"] as JsonList;

            if (joints == null) return;
            
            foreach (var jointObj in joints)
            {
                var joint = jointObj as JsonDictionary;
                var name = joint.Get("header").Get<string>("name"); // Probably not gonna be used
                var anchor = ParseJointVector3D(joint.Get("origin"));
                var parent = RigidbodyCache[joint.Get<string>("occurrenceOneUUID")];
                var child = RigidbodyCache[joint.Get<string>("occurrenceTwoUUID")];

                foreach (var j in child.gameObject.GetComponents<FixedJoint>())
                {
                    Object.Destroy(j);
                }

                foreach (var j in child.gameObject.GetComponents<HingeJoint>())
                {
                    Object.Destroy(j);
                }

                if (joint != null && joint.ContainsKey("revoluteJointMotion"))
                {
                    var revoluteData = joint.Get("revoluteJointMotion");
                    var axis = ParseJointVector3D(revoluteData.Get("rotationAxisVector"));
                    // TODO: Support limits
                    var result = child.gameObject.AddComponent<HingeJoint>();
                    result.anchor = anchor;
                    result.axis = axis;
                    result.connectedBody = parent;
                }
                else
                {
                    // For yet to be supported and fixed motion joints
                    var result = child.gameObject.AddComponent<FixedJoint>();
                    result.anchor = anchor;
                    result.connectedBody = parent;
                }
            }
        }

        /// <summary>
        /// Parses the ColorChannels property of Material
        ///
        /// Does not check for null - responsibility of user
        /// </summary>
        /// <param name="channels"></param>
        /// <returns></returns>
        private static Color ChannelsToColor(in IEnumerable<MaterialChannel> channels)
        {
            // really should use first or default
            var param = channels.First().Parameter;

            var color = new UnityEngine.Color {
                r = param.X,
                g = param.Y, 
                b = param.Z, 
                a = param.W
            };
            
            return color;
        }


        private static Vector3 ParseJointVector3D(JsonDictionary dict) =>
           new Vector3((float)dict.TryGet<decimal>("x", 0),
                   (float)dict.TryGet<decimal>("y", 0), (float)dict.TryGet<decimal>("z", 0));
    }
    public static class GltfAssetExtensions
    {
        public static T Get<T>(this JsonDictionary dict, string key) => (T)dict[key];
        public static T TryGet<T>(this JsonDictionary dict, string key, T defaultObj)
        {
            if (dict.ContainsKey(key))
                return (T)dict[key];
            else
                return defaultObj;
        }
        public static JsonDictionary Get(this JsonDictionary dict, string key) => (JsonDictionary)dict[key];

        public static void ForEach<T>(this IEnumerable<T> e, Action<int, T> method)
        {
            for (int i = 0; i < e.Count(); ++i)
                method(i, e.ElementAt(i)); // I really hope this holds reference
        }
    }
}
