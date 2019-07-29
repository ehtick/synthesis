using System;
using System.Collections.Generic;
using System.Windows.Forms;
using InventorRobotExporter.GUI.Editors.JointSubEditors;
using InventorRobotExporter.Managers;
using InventorRobotExporter.Utilities;
using InventorRobotExporter.Utilities.ImageFormat;

namespace InventorRobotExporter.GUI.Editors.JointEditor
{
    public sealed partial class JointCard : UserControl
    {
        private readonly JointForm jointForm;
        private readonly RigidNode_Base node;

        private bool isHighlighted;
        private bool hasLoadedEditor;

        public JointCard(RigidNode_Base node, JointForm jointForm, RobotDataManager robotDataManager)
        {
            this.robotDataManager = robotDataManager;
            this.jointForm = jointForm;
            this.node = node;

            InitializeComponent();
            AnalyticsUtils.LogEvent("Joint Editor", "System", "Init");
            jointEditorUserControl.Initialize(new List<RigidNode_Base> {node}, this);

            AddHighlightAction(this);
        }

        public void LoadValues()
        {
            var joint = node.GetSkeletalJoint();
            jointName.Text = ToStringUtils.NodeNameString(node);
            jointTypeValue.Text = ToStringUtils.JointTypeString(joint, robotDataManager);
            driverValue.Text = ToStringUtils.DriverString(joint);
            wheelTypeValue.Text = ToStringUtils.WheelTypeString(joint);
        }

        public void LoadValuesRecursive()
        {
            LoadValues();
            hasLoadedEditor = false;
        }

        private void HighlightSelf()
        {
            AnalyticsUtils.LogEvent("Joint Editor", "System", "Highlight");
            if (isHighlighted)
            {
                return;
            }

            jointForm.ResetAllHighlight();
            isHighlighted = true;

            InventorUtils.FocusAndHighlightNode(node, RobotExporterAddInServer.Instance.Application.ActiveView.Camera, 0.8);
        }

        public void LoadPreviewIcon()
        {
            var iconCamera = RobotExporterAddInServer.Instance.Application.TransientObjects.CreateCamera();
            iconCamera.SceneObject = RobotExporterAddInServer.Instance.OpenAssemblyDocument.ComponentDefinition;

            const double zoom = 0.6; // Zoom, where a zoom of 1 makes the camera the size of the whole robot
            
            const int widthConst = 3; // The image needs to be wide to hide the XYZ coordinate labels in the bottom left corner

            var occurrences = InventorUtils.GetComponentOccurrencesFromNodes(new List<RigidNode_Base> {node});
            iconCamera.Fit();
            iconCamera.GetExtents(out _, out var height);

            InventorUtils.SetCameraView(InventorUtils.GetOccurrencesCenter(occurrences), 15, height * zoom * widthConst, height * zoom, iconCamera);


            pictureBox1.Image = AxHostConverter.PictureDispToImage(
                iconCamera.CreateImage(pictureBox1.Height * widthConst, pictureBox1.Height,
                    RobotExporterAddInServer.Instance.Application.TransientObjects.CreateColor(210, 222, 239),
                    RobotExporterAddInServer.Instance.Application.TransientObjects.CreateColor(175, 189, 209)));
        }

        public void ResetHighlight()
        {
            isHighlighted = false;
        }

        private void AddHighlightAction(Control baseControl)
        {
            baseControl.MouseHover += (sender, args) => HighlightSelf();

            foreach (Control control in baseControl.Controls)
                AddHighlightAction(control);
        }

        private void ToggleCollapsed()
        {
            jointForm.CollapseAllCards(this);
            SetCollapsed(!IsCollapsed());


        }

        public void SetCollapsed(bool collapse)
        {
            AnalyticsUtils.LogEvent("Joint Editor", "System", "SetCollapsed", collapse ? 0: 1);
            jointEditorUserControl.Visible = !collapse;
        }


        public bool IsCollapsed()
        {
            return !jointEditorUserControl.Visible;
        }

        private void editButton_Click(object sender, EventArgs e)
        {
            AnalyticsUtils.LogEvent("Joint Editor", "Control Clicked", "Edit Button");

            ToggleCollapsed();
            if (!hasLoadedEditor)
            {
                hasLoadedEditor = true;
                jointEditorUserControl.SuspendLayout();
                jointEditorUserControl.LoadValues();
                jointEditorUserControl.ResumeLayout();
            }
        }

        private void constraintsButton_Click(object sender, EventArgs e)
        {
            AnalyticsUtils.LogEvent("Joint Editor", "Control Clicked", "Constraints Button");
            var limitEditor = new JointLimitEditorForm(node.GetSkeletalJoint());// show the limit editor form
            limitEditor.ShowDialog(ParentForm);
        }

        private void sensorsButton_Click(object sender, EventArgs e)
        {
            AnalyticsUtils.LogEvent("Joint Editor", "Control Clicked", "Sensors Button");
            var listForm = new JointSensorListForm(node.GetSkeletalJoint());
            listForm.ShowDialog(ParentForm);
        }
    }
}