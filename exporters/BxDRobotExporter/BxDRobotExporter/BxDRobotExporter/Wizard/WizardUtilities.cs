﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Inventor;
using System.Windows.Forms;

namespace BxDRobotExporter.Wizard
{
    public delegate void WheelTypeChangedEventHandler(object sender, WheelTypeChangedEventArgs e);
    public class WheelTypeChangedEventArgs : EventArgs
    {
        public WizardData.WizardWheelType NewWheelType;
    }

    public class WizardUtilities
    {
        public static string[] GetExportedComponentNames(RigidNode_Base baseNode)
        {
            List<string> names = new List<string>();
            foreach(RigidNode_Base node in baseNode.ListAllNodes())
            {
                names.AddRange(node.ModelFullID.Split(new string[] { "-_-" }, StringSplitOptions.RemoveEmptyEntries));
            }
            return names.ToArray();
        }

        public static ComponentOccurrence[] GetExportedComponents(RigidNode_Base baseNode)
        {
            List<ComponentOccurrence> names = new List<ComponentOccurrence>();
            foreach (RigidNode_Base node in baseNode.ListAllNodes())
            {
                foreach (string s in node.ModelFullID.Split(new string[] { "-_-" }, StringSplitOptions.RemoveEmptyEntries))
                {
                    names.Add(StandardAddInServer.Instance.GetOccurrence(s));
                }
            }
            return names.ToArray();
        }

        public static double GetVolume(ComponentOccurrences occurrences)
        {
            double volume = 0.0d;

            Inventor.Application app = StandardAddInServer.Instance.MainApplication;
            
            foreach(ComponentOccurrence component in occurrences.AllLeafOccurrences)
            { 
                foreach(SurfaceBody body in component.SurfaceBodies)
                {
                    volume += body.Volume[0.001];
                }
            }

            return volume;
        }

        public static List<RigidNode_Base> DetectWheels(RigidNode_Base baseNode, WizardData.WizardDriveTrain driveTrain, int wheelCount)
        {
            List<RigidNode_Base> jointParentFilter = new List<RigidNode_Base>();

            foreach(RigidNode_Base node in baseNode.ListAllNodes())
            {
                //For the first filter, we take out any nodes that do not have parents and rotational joints.
                if (node.GetParent() != null && node.GetSkeletalJoint() != null && node.GetSkeletalJoint().GetJointType() == SkeletalJointType.ROTATIONAL)
                {
                    jointParentFilter.Add(node);
                }
            }

            //Find node with the lowest y value
            RigidNode_Base lowestNode = null; double lowestY = double.MaxValue;
            foreach(RigidNode_Base node in jointParentFilter)
            {
                if (lowestNode == null)
                {
                    lowestNode = node;
                    lowestY = node.GetSkeletalJoint().GetAngularDOF().First().basePoint.y;
                }
                else
                {
                    if (node.GetSkeletalJoint().GetAngularDOF().First().basePoint.y < lowestY)
                    {
                        lowestNode = node;
                        lowestY = node.GetSkeletalJoint().GetAngularDOF().First().basePoint.y;
                    }
                }
            }

            //Find all nodes with y values within 0.1
            List<RigidNode_Base> lowestNodesFilter = new List<RigidNode_Base>();
            foreach (RigidNode_Base node in jointParentFilter)
            {
                if (node == lowestNode)
                    lowestNodesFilter.Add(node);
                else if (lowestY - node.GetSkeletalJoint().GetAngularDOF().First().basePoint.y <= 0.1d && lowestY - node.GetSkeletalJoint().GetAngularDOF().First().basePoint.y >= -0.1d)
                    lowestNodesFilter.Add(node);
            }
            //Hopefully this will be enough filtering :point_right:
            if (lowestNodesFilter.Count == wheelCount)
            {
                BXDJSkeleton.SetupFileNames(baseNode);
                StandardAddInServer.Instance.JointEditorPane_SelectedJoint(lowestNodesFilter);
                return lowestNodesFilter;
            }

            //Find the nodes with the highest and lowest x values
            RigidNode_Base leftMostNode = null; double highestX = double.MinValue;
            RigidNode_Base rightMostNode = null; double lowestX = double.MaxValue;
            foreach(RigidNode_Base node in lowestNodesFilter)
            {
                if (highestX == double.MinValue)
                {
                    leftMostNode = node;
                    highestX = node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x;
                }
                else if (node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x > highestX)
                {
                    leftMostNode = node;
                    highestX = node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x;
                }

                if (lowestX == double.MaxValue)
                {
                    rightMostNode = node;
                    lowestX = node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x;
                }
                else if (node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x < lowestX)
                {
                    leftMostNode = node;
                    lowestX = node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x;
                }
            }


            //Find all the nodes with x values within 0.1 of both.
            List<RigidNode_Base> rightWheels = new List<RigidNode_Base> { rightMostNode };
            List<RigidNode_Base> leftWheels = new List<RigidNode_Base> { leftMostNode };

            foreach (RigidNode_Base node in lowestNodesFilter)
            {
                if (node == leftMostNode || node == rightMostNode)
                    continue;
                if (node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x - lowestX <= 0.1d && node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x - lowestX >= -0.1d)
                    rightWheels.Add(node);
                else if (node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x - highestX <= 0.1d && node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x - highestX >= -0.1d)
                    leftWheels.Add(node);
            }

            string nodes = "Nodes detected: ";
            List<RigidNode_Base> wheels = new List<RigidNode_Base>();
            wheels.AddRange(rightWheels);
            wheels.AddRange(leftWheels);

            BXDJSkeleton.SetupFileNames(baseNode);
            foreach(var node in wheels)
            {
                nodes += node.ModelFileName + ", ";
            }
            MessageBox.Show(nodes);

            return wheels;
        }

        public static RigidNode_Base[][] SortWheels(List<RigidNode_Base> nodes, bool IsHDrive = false)
        {
            if (!IsHDrive)
            {
                Dictionary<double, RigidNode_Base> nodeDict = new Dictionary<double, RigidNode_Base>();
                foreach (var node in nodes)
                {
                    nodeDict.Add(node.GetSkeletalJoint().GetAngularDOF().First().basePoint.x, node);
                }
                var newKeyOrder = nodeDict.Keys.OrderBy(key => key);
                RigidNode_Base[] left = new RigidNode_Base[nodes.Count / 2];
                RigidNode_Base[] right = new RigidNode_Base[nodes.Count / 2];
                string leftNodes = "Left Nodes: ", rightNodes = "Right Nodes: ";
                int i = 0;
                foreach (double key in newKeyOrder)
                {
                    if(i < nodes.Count / 2)
                    {
                        left[i] = nodeDict[key];
                        leftNodes += nodeDict[key].ModelFileName + ", ";
                    }
                    else
                    {
                        right[i - (nodes.Count / 2)] = nodeDict[key];
                        rightNodes += nodeDict[key].ModelFileName + ", ";
                    }
                    i++;
                }
                MessageBox.Show(leftNodes.Substring(0, leftNodes.Length - 2) + "\n" + rightNodes.Substring(0, rightNodes.Length - 2));

                return new RigidNode_Base[][] { left, right };
            }
            else
            {
                return null;
            }

        }
    }
}