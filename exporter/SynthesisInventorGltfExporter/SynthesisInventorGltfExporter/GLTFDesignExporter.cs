﻿using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Windows.Forms;
using Google.Protobuf;
using Inventor;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using SharpGLTF.Geometry;
using SharpGLTF.Geometry.VertexTypes;
using SharpGLTF.Materials;
using SharpGLTF.Scenes;
using SharpGLTF.Schema2;
using SharpGLTF.Transforms;
using Synthesis.Gltfextras;
using Application = Inventor.Application;
using Asset = Inventor.Asset;
using Color = Inventor.Color;
using File = System.IO.File;
using ProgressBar = Inventor.ProgressBar;

namespace SynthesisInventorGltfExporter
{
    /*
     * TODO: Avoid exporting duplicate meshes using occurrences (materials didn't work when I tried to do this)
     * TODO: Figure out a more elegant method to add extras to the gltf object
     * TODO: Figure out how to use dependency redirects in an inventor addin (was not working for some reason) so we can use an updated version of sharpgltf
     */
    public class GLTFDesignExporter
    {
        private MaterialBuilder defaultMaterial = new MaterialBuilder()
            .WithMetallicRoughnessShader()
            .WithChannelParam("BaseColor", Vector4.One);

        private Dictionary<string, MassProperties> massPropertiesMap;
        private Dictionary<string, MaterialBuilder> materialCache;
        private List<AssemblyJoint> allDocumentJoints;
        
        private List<string> warnings;

        private HashSet<string> visitedDocuments = new HashSet<string>();
        private ProgressBar progressBar;
        private int progressTotal;
        private bool exportMaterials;
        private bool exportFaceMaterials;
        private bool exportHidden;
        private decimal exportTolerance;

        public void ExportDesign(Application application, AssemblyDocument assemblyDocument, string filePath, bool glb, bool checkMaterialsChecked, bool checkFaceMaterials, bool checkHiddenChecked, decimal numericToleranceValue)
        {
            Stopwatch sw = new Stopwatch();
            sw.Start();
            
            exportTolerance = numericToleranceValue;
            exportHidden = checkHiddenChecked;
            exportFaceMaterials = checkFaceMaterials;
            exportMaterials = checkMaterialsChecked;
            materialCache = new Dictionary<string, MaterialBuilder>();
            massPropertiesMap = new Dictionary<string, MassProperties>();
            allDocumentJoints = new List<AssemblyJoint>();
            warnings = new List<string>();

            progressTotal = 2 + assemblyDocument.AllReferencedDocuments.Count;
            progressBar = application.CreateProgressBar(false, progressTotal, "Exporting " + assemblyDocument.DisplayName + " to glTF");

            progressBar.Message = "Preparing for export...";

            var sceneBuilder = ExportScene(assemblyDocument);

            progressBar.Message = "Exporting joints...";
            progressBar.UpdateProgress();
            // TODO: Figure out a more elegant solution for extras. This is only needed because sharpGLTF (this version anyways) doesn't support writing extras so we need to do it manually. 
            var modelRoot = sceneBuilder.ToSchema2();
            var dictionary = modelRoot.WriteToDictionary("temp");
            var jsonString = Encoding.ASCII.GetString(dictionary["temp.gltf"].Array);
            var parsedJToken = (JObject) JToken.ReadFrom(new JsonTextReader(new StringReader(jsonString)));
            var extras = new JObject();
            extras.Add("joints", ExportJoints(assemblyDocument));
            parsedJToken.Add("extras", extras);

            try
            {
                ExportMassProperties((JArray) parsedJToken.GetValue("meshes"));
            } catch {}

            try
            {
                var asset = (JObject) parsedJToken.GetValue("asset");
                asset.Property("generator").Value = "Autodesk.Synthesis.Inventor";
            } catch { }

            var readSettings = new ReadSettings();
            readSettings.FileReader = assetFileName => dictionary[assetFileName];
            var modifiedGltf = ModelRoot.ReadGLTF(new MemoryStream(Encoding.ASCII.GetBytes(JsonConvert.SerializeObject(parsedJToken))), readSettings);
            
            progressBar.Message = "Saving file...";
            progressBar.UpdateProgress();

            if (glb)
                modifiedGltf.SaveGLB(filePath);
            else
                modifiedGltf.SaveGLTF(filePath);

            Debug.WriteLine("-----gltf export warnings-----");
            foreach (var warning in warnings)
            {
                Debug.WriteLine(warning);
            }
            Debug.WriteLine("----------");
            progressBar.Close();
            
            sw.Stop();
            
            MessageBox.Show("glTF export completed successfully in "+sw.Elapsed.TotalSeconds.ToString("N2")+" seconds.\nFile saved to: "+filePath);
        }

        private void ExportMassProperties(JArray meshList)
        {
            foreach (var jToken in meshList)
            {
                var mesh = (JObject) jToken;
                var meshName = (string) mesh.GetValue("name");
                if (meshName != null)
                {
                    if (massPropertiesMap.ContainsKey(meshName))
                    {
                        try
                        {
                            var meshExtras = new JObject();
                            meshExtras.Add("physicalProperties", PhysicalPropertiesToJSON(massPropertiesMap[meshName]));
                            mesh.Add("extras", meshExtras);
                        }
                        catch
                        {
                            
                        }
                    }
                }
            }
            
        }

        private JObject PhysicalPropertiesToJSON(MassProperties massProperties)
        {
            return JObject.Parse(JsonFormatter.Default.Format(ExportPhysicalProperties(massProperties)));
        }

        private PhysicalProperties ExportPhysicalProperties(MassProperties massProperties)
        {
            var physicalProperties = new PhysicalProperties();
            physicalProperties.Mass = massProperties.Mass; // kg -> kg
            physicalProperties.Area = massProperties.Area/Math.Pow(100, 2); // cm^2 -> m^2
            physicalProperties.Volume = massProperties.Volume/Math.Pow(100, 3); // cm^3 -> m^3
            physicalProperties.CenterOfMass = GetVector3DConvertUnits(massProperties.CenterOfMass);
            return physicalProperties;
        }


        private JArray ExportJoints(AssemblyDocument assemblyDocument)
        {
            var jointArray = new JArray();
            
            foreach (AssemblyJoint joint in allDocumentJoints)
            {
                try { jointArray.Add(JObject.Parse(JsonFormatter.Default.Format(ExportJoint(joint)))); } catch {}
            }
        
            return jointArray;
        }
        
        private Joint ExportJoint(AssemblyJoint invJoint)
        {
            var protoJoint = new Joint();
            
            var header = new Header();
            try { header.Name = invJoint.Name; } catch {}
            protoJoint.Header = header;
            
            protoJoint.Origin = GetCenterOrRoot(invJoint.Definition);
            
            try { protoJoint.IsLocked = invJoint.Locked; } catch {}
            try { protoJoint.IsSuppressed = invJoint.Suppressed; } catch {}
        
            protoJoint.OccurrenceOneUUID = GetOccurrenceUniqueId(invJoint.OccurrenceOne);
            protoJoint.OccurrenceTwoUUID = GetOccurrenceUniqueId(invJoint.OccurrenceTwo);
            
            var assemblyJointDefinition = invJoint.Definition;
            
            switch (assemblyJointDefinition.JointType)
            {
                case AssemblyJointTypeEnum.kRigidJointType:
                    protoJoint.RigidJointMotion = GetRigidJointMotion(assemblyJointDefinition);
                    break;
                case AssemblyJointTypeEnum.kRotationalJointType:
                    protoJoint.RevoluteJointMotion = GetRevoluteJointMotion(assemblyJointDefinition);
                    break;
                case AssemblyJointTypeEnum.kSlideJointType:
                    protoJoint.SliderJointMotion = GetSliderJointMotion(assemblyJointDefinition);
                    break;
                case AssemblyJointTypeEnum.kCylindricalJointType:
                    protoJoint.CylindricalJointMotion = GetCylindricalJointMotion(assemblyJointDefinition);
                    break;
                // case AssemblyJointTypeEnum.k: // pinSlot
                    // protoJoint.RigidJointMotion = GetRigidJointMotion(assemblyJointDefinition);
                // break;
                case AssemblyJointTypeEnum.kPlanarJointType:
                    protoJoint.PinSlotJointMotion = GetPinSlotJointMotion(assemblyJointDefinition);
                    break;
                case AssemblyJointTypeEnum.kBallJointType:
                    protoJoint.PlanarJointMotion = GetPlanarJointMotion(assemblyJointDefinition);
                    break;
            }
            
            return protoJoint;
        }

        private Vector3D GetNormalOrDirection(AssemblyJointDefinition assemblyJointDefinition)
        {
            try { return GetVector3D(GetNormDirFromGeometry(assemblyJointDefinition.OriginOne)); } catch {}
            try { return GetVector3D(GetNormDirFromGeometry(assemblyJointDefinition.OriginTwo)); } catch {}
            warnings.Add("No joint axis found for joint "+assemblyJointDefinition.Parent.Name);
            return new Vector3D();
        }

        private dynamic GetNormDirFromGeometry(GeometryIntent intent)
        {
            try { return GetNormDir(intent.Geometry); } catch {}
            try { return GetNormDir(intent.Geometry.Geometry); } catch {}
            throw new Exception();
        }

        private dynamic GetNormDir(dynamic var)
        {
            try { return var.Normal; } catch {}
            try { return var.Direction; } catch {}
            throw new Exception();
        }
        private Vector3D GetCenterOrRoot(AssemblyJointDefinition assemblyJointDefinition)
        {
            // TODO: The point returned from getCenter is very often wrong...
            try { return GetVector3DConvertUnits(GetCenterFromGeometry(assemblyJointDefinition.OriginTwo)); } catch {}
            try { return GetVector3DConvertUnits(GetCenterFromGeometry(assemblyJointDefinition.OriginOne)); } catch {}
            warnings.Add("No joint center found for joint "+assemblyJointDefinition.Parent.Name);
            throw new Exception();
        }

        private dynamic GetCenterFromGeometry(GeometryIntent intent)
        {
            try { return GetCenter(intent.Geometry.Geometry); } catch {}
            try { return GetCenter(intent.Geometry); } catch {}
            try
            {
                if (intent.Point != null)
                    return intent.Point; // This seems to always be wrong. hmm...
            } catch {}
            throw new Exception();
        }

        private dynamic GetCenter(dynamic var)
        {
            try { return var.RootPoint; } catch {}
            try { return var.Center; } catch {}
            try { return var.MidPoint; } catch {}
            throw new Exception();
        }

        private JointLimits GetAngularLimits(AssemblyJointDefinition assemblyJointDefinition)
        {
            var limits = new JointLimits();
            limits.IsMaximumValueEnabled = assemblyJointDefinition.HasAngularPositionLimits;
            limits.IsMinimumValueEnabled = assemblyJointDefinition.HasAngularPositionLimits;
            limits.IsRestValueEnabled = false;
            if (limits.IsMaximumValueEnabled)
                limits.MaximumValue = assemblyJointDefinition.AngularPositionEndLimit.Value;
            if (limits.IsMinimumValueEnabled)
                limits.MinimumValue = assemblyJointDefinition.AngularPositionStartLimit.Value;
            // limits.RestValue = assemblyJointDefinition.AngularPosition;
            return limits;
        }

        private JointLimits GetLinearLimits(AssemblyJointDefinition assemblyJointDefinition)
        {
            var limits = new JointLimits();
            limits.IsMaximumValueEnabled = assemblyJointDefinition.HasLinearPositionEndLimit;
            limits.IsMinimumValueEnabled = assemblyJointDefinition.HasLinearPositionStartLimit;
            limits.IsRestValueEnabled = false;
            if (limits.IsMaximumValueEnabled)
                limits.MaximumValue = assemblyJointDefinition.LinearPositionEndLimit.Value;
            if (limits.IsMinimumValueEnabled)
                limits.MinimumValue = assemblyJointDefinition.LinearPositionStartLimit.Value;
            // limits.RestValue = assemblyJointDefinition.LinearPosition;
            return limits;
        }

        private double GetAngularPosition(AssemblyJointDefinition assemblyJointDefinition)
        {
            if (assemblyJointDefinition.AngularPosition != null)
                return assemblyJointDefinition.AngularPosition.Value;
            return 0;
        }

        private double GetLinearPosition(AssemblyJointDefinition assemblyJointDefinition)
        {
            if (assemblyJointDefinition.LinearPosition != null)
                return assemblyJointDefinition.LinearPosition.Value;
            return 0;
        }

        private RigidJointMotion GetRigidJointMotion(AssemblyJointDefinition assemblyJointDefinition)
        {
            var protoJointMotion = new RigidJointMotion();
            return protoJointMotion;
        }

        private RevoluteJointMotion GetRevoluteJointMotion(AssemblyJointDefinition assemblyJointDefinition)
        {
            var protoJointMotion = new RevoluteJointMotion();
            protoJointMotion.RotationAxisVector = GetNormalOrDirection(assemblyJointDefinition);
            protoJointMotion.RotationValue = GetAngularPosition(assemblyJointDefinition);
            protoJointMotion.RotationLimits = GetAngularLimits(assemblyJointDefinition);
            return protoJointMotion;
        }

        private SliderJointMotion GetSliderJointMotion(AssemblyJointDefinition assemblyJointDefinition)
        {
            var protoJointMotion = new SliderJointMotion();
            protoJointMotion.SlideDirectionVector = GetNormalOrDirection(assemblyJointDefinition);
            protoJointMotion.SlideValue = GetLinearPosition(assemblyJointDefinition);
            protoJointMotion.SlideLimits = GetLinearLimits(assemblyJointDefinition);
            return protoJointMotion;
        }
        private CylindricalJointMotion GetCylindricalJointMotion(AssemblyJointDefinition assemblyJointDefinition)
        {
            var protoJointMotion = new CylindricalJointMotion();
            protoJointMotion.RotationAxisVector = GetNormalOrDirection(assemblyJointDefinition);
            protoJointMotion.RotationValue = GetAngularPosition(assemblyJointDefinition);
            protoJointMotion.RotationLimits = GetAngularLimits(assemblyJointDefinition);
            
            protoJointMotion.SlideValue = GetLinearPosition(assemblyJointDefinition);
            protoJointMotion.SlideLimits = GetLinearLimits(assemblyJointDefinition);
            return protoJointMotion;
        }
        private PinSlotJointMotion GetPinSlotJointMotion(AssemblyJointDefinition assemblyJointDefinition)
        {
            var protoJointMotion = new PinSlotJointMotion();
            protoJointMotion.RotationAxisVector = GetNormalOrDirection(assemblyJointDefinition);
            protoJointMotion.RotationValue = GetAngularPosition(assemblyJointDefinition);
            protoJointMotion.RotationLimits = GetAngularLimits(assemblyJointDefinition);
            
            protoJointMotion.SlideDirectionVector = GetNormalOrDirection(assemblyJointDefinition);
            protoJointMotion.SlideValue = GetLinearPosition(assemblyJointDefinition);
            protoJointMotion.SlideLimits = GetLinearLimits(assemblyJointDefinition);
            return protoJointMotion;
        }
        private PlanarJointMotion GetPlanarJointMotion(AssemblyJointDefinition assemblyJointDefinition)
        {
            var protoJointMotion = new PlanarJointMotion();
            warnings.Add("Limits not implemented for planar joints! Joint: "+assemblyJointDefinition.Parent.Name);
            // TODO
            return protoJointMotion;
        }
        private BallJointMotion GetBallJointMotion(AssemblyJointDefinition assemblyJointDefinition)
        {
            var protoJointMotion = new BallJointMotion();
            warnings.Add("Limits not implemented for ball joints! Joint: "+assemblyJointDefinition.Parent.Name);
            // TODO
            return protoJointMotion;
        }

        private string GetOccurrenceUniqueId(ComponentOccurrence occurrence)
        {
            return string.Join("+", new List<ComponentOccurrence>(occurrence.OccurrencePath.Cast<ComponentOccurrence>()).Select(o => o.Name));
        }

        private static Vector3D GetVector3DConvertUnits(dynamic getJointCenter)
        {
            var protoJointOrigin = new Vector3D();
            protoJointOrigin.X = getJointCenter.X/100;
            protoJointOrigin.Y = getJointCenter.Y/100;
            protoJointOrigin.Z = getJointCenter.Z/100;
            return protoJointOrigin;
        }
        
        private static Vector3D GetVector3D(dynamic hasXYZ)
        {
            var protoJointOrigin = new Vector3D();
            protoJointOrigin.X = hasXYZ.X;
            protoJointOrigin.Y = hasXYZ.Y;
            protoJointOrigin.Z = hasXYZ.Z;
            return protoJointOrigin;
        }
        
        private SceneBuilder ExportScene(AssemblyDocument assemblyDocument)
        {
            var scene = new SceneBuilder();
            ExportNodeRootAssembly(assemblyDocument, scene);
            return scene;
        }

        private void ExportNodeRootAssembly(AssemblyDocument assemblyDocument, SceneBuilder scene)
        {
            var root = new NodeBuilder(assemblyDocument.DisplayName).WithLocalScale(Vector3.Multiply(Vector3.One, 0.01f));
            var assemblyComponentDefinition = assemblyDocument.ComponentDefinition;
            allDocumentJoints.AddRange(assemblyComponentDefinition.Joints.Cast<AssemblyJoint>());
            ExportNodes(assemblyComponentDefinition.Occurrences.Cast<ComponentOccurrence>(), scene, root);
        }

        private void ExportNodes(IEnumerable<ComponentOccurrence> occurrences, SceneBuilder scene, NodeBuilder parent)
        {
            foreach (ComponentOccurrence childOccurrence in occurrences)
            {
                ExportNode(childOccurrence, scene, parent.CreateNode());
            }
        }

        private void ExportNode(ComponentOccurrence componentOccurrence, SceneBuilder scene, NodeBuilder node)
        {
            var componentOccurrenceDefinition = componentOccurrence.Definition;

            // ExportAppearanceCached(componentOccurrence.Appearance);

            // node.LocalTransform = InvToGltfMatrix4X4(componentOccurrence.Transformation); TODO: mesh caching by using definitions instead of occurrences (materials were an issue)
            switch (componentOccurrenceDefinition.Type)
            {
                case ObjectTypeEnum.kAssemblyComponentDefinitionObject:
                    ExportNodeAssembly(componentOccurrence, scene, node);
                    break;
                case ObjectTypeEnum.kPartComponentDefinitionObject:
                    ExportNodePart(componentOccurrence, scene, node);
                    break;
            }
        }
        private void ExportNodeAssembly(ComponentOccurrence componentOccurrence, SceneBuilder scene, NodeBuilder node)
        {
            // ReSharper disable once SuspiciousTypeConversion.Global
            var assemblyComponentDefinition = (AssemblyComponentDefinition)componentOccurrence.Definition;
            try
            {
                if (visitedDocuments.Add(assemblyComponentDefinition.Document.InternalName()))
                {
                    progressBar.Message = "Exporting mesh " + visitedDocuments.Count + " of " + progressTotal + "...";
                    progressBar.UpdateProgress();
                }
            }
            catch { }

            allDocumentJoints.AddRange(assemblyComponentDefinition.Joints.Cast<AssemblyJoint>());
            ExportNodes(componentOccurrence.SubOccurrences.Cast<ComponentOccurrence>(), scene, node);
        }

        private void ExportNodePart(ComponentOccurrence componentOccurrence, SceneBuilder scene, NodeBuilder node)
        {
            // ReSharper disable once SuspiciousTypeConversion.Global
            var partComponentDefinition = (PartComponentDefinition)componentOccurrence.Definition;
            try
            {
                if (visitedDocuments.Add(partComponentDefinition.Document.InternalName()))
                {
                    progressBar.Message = "Exporting mesh " + visitedDocuments.Count + " of " + progressTotal + "...";
                    progressBar.UpdateProgress();
                }
            }
            catch { }

            if (exportHidden || componentOccurrence.Visible)
            {
                scene.AddMesh(ExportMesh(componentOccurrence), node);
            }
        }

        private MeshBuilder<VertexPosition> ExportMesh(ComponentOccurrence componentOccurrence)
        {
            var occurrenceUniqueId = GetOccurrenceUniqueId(componentOccurrence);
            var mesh = new MeshBuilder<VertexPosition>(occurrenceUniqueId);
            try
            {
                massPropertiesMap[occurrenceUniqueId] = componentOccurrence.MassProperties;
            } catch {}
            foreach (SurfaceBody surfaceBody in componentOccurrence.SurfaceBodies)
            {
                if (exportMaterials && exportFaceMaterials)
                {
                    var surfaceBodyFaces = surfaceBody.Faces;
                    foreach (Face face in surfaceBodyFaces)
                    {
                        ExportPrimitive(face, mesh.UsePrimitive(ExportAppearanceCached(face.Appearance)));
                    }
                }
                else
                {
                    ExportPrimitive(surfaceBody, mesh.UsePrimitive(ExportAppearanceCached(componentOccurrence.Appearance)));
                }
            }

            return mesh;
        }

        private MaterialBuilder ExportAppearanceCached(Asset appearance)
        {
            if (!exportMaterials || appearance == null)
                return defaultMaterial;

            var appearanceName = appearance.Name;
            if (materialCache.ContainsKey(appearanceName))
                return materialCache[appearanceName];
            
            var colorVector = Vector4.One;
            try
            {
                Color tempColor = AttemptGetColor(appearance);
                colorVector = new Vector4(tempColor.Red / 255f, tempColor.Green / 255f, tempColor.Blue / 255f, (float) tempColor.Opacity);
            }
            catch { }
            var material = new MaterialBuilder()
                .WithMetallicRoughnessShader()
                .WithChannelParam("BaseColor", colorVector )
                .WithChannelParam("MetallicRoughness", new Vector4(1,1,0,0) ); // TODO: metallic roughness
            materialCache[appearanceName] = material;
            return material;
        }

        private Color AttemptGetColor(Asset appearance)
        { // TODO: Figure out how to identify appearance types so this isn't neccecary
            try {return ((ColorAssetValue) appearance["generic_diffuse"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["masonrycmu_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["solidglass_transmittance_custom_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["hardwood_tint_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["water_tint_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["concrete_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["plasticvinyl_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["metallicpaint_base_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["wallpaint_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["metal_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["ceramic_color"]).Value;} catch {}
            try {return ((ColorAssetValue) appearance["glazing_transmittance_map"]).Value;} catch {}
            throw new Exception("Could not get color!");
        }

        private void ExportPrimitive(SurfaceBody surfaceBody, PrimitiveBuilder<MaterialBuilder, VertexPosition, VertexEmpty, VertexEmpty> primitive)
        {
            ExportPrimitive(surfaceBody, null, primitive);
        }
        
        private void ExportPrimitive(Face surfaceFace, PrimitiveBuilder<MaterialBuilder, VertexPosition, VertexEmpty, VertexEmpty> primitive)
        {
            ExportPrimitive(null, surfaceFace, primitive);
        }
        private void ExportPrimitive(SurfaceBody surfaceBody, Face surfaceFace, PrimitiveBuilder<MaterialBuilder, VertexPosition, VertexEmpty, VertexEmpty> primitive)
        {
            int facetCount;
            int vertCount;
            var coords = new double[]{};
            var norms = new double[]{};
            var indices = new int[]{};
            if (surfaceBody != null) 
                surfaceBody.CalculateFacets((double) exportTolerance, out vertCount, out facetCount, out coords, out norms, out indices);
            else
                surfaceFace.CalculateFacets((double) exportTolerance, out vertCount, out facetCount, out coords, out norms, out indices);
            for (var c = 0; c < indices.Length; c += 3)
            {
                var indexA = indices[c];
                var indexB = indices[c+1];
                var indexC = indices[c+2];
                primitive.AddTriangle(
                    GetCoordinates(coords, indexA-1),
                    GetCoordinates(coords, indexB-1),
                    GetCoordinates(coords, indexC-1)
                );
            }
        }
        
        private VertexPosition GetCoordinates(double[] coords, int index)
        {
            return new VertexPosition(
                (float)coords[index * 3],
                (float)coords[index * 3 + 1],
                (float)coords[index * 3 + 2]
            );
        }
        
        
        private Matrix4x4 InvToGltfMatrix4X4(Matrix invTransform)
        {
            var transform = new Matrix4x4(
                (float) invTransform.Cell[1, 1],
                (float) invTransform.Cell[2, 1],
                (float) invTransform.Cell[3, 1],
                (float) invTransform.Cell[4, 1],
                (float) invTransform.Cell[1, 2],
                (float) invTransform.Cell[2, 2],
                (float) invTransform.Cell[3, 2],
                (float) invTransform.Cell[4, 2],
                (float) invTransform.Cell[1, 3],
                (float) invTransform.Cell[2, 3],
                (float) invTransform.Cell[3, 3],
                (float) invTransform.Cell[4, 3],
                (float) invTransform.Cell[1, 4],
                (float) invTransform.Cell[2, 4],
                (float) invTransform.Cell[3, 4],
                (float) invTransform.Cell[4, 4]
            );
            return AffineTransform.Evaluate(transform, null, null, null);
        }
    }
}