﻿namespace BxDRobotExporter.Wizard
{
    partial class DefineWheelsPage
    {
        /// <summary> 
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary> 
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Component Designer generated code

        /// <summary> 
        /// Required method for Designer support - do not modify 
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.DefineWheelsInstruction1 = new System.Windows.Forms.Label();
            this.WheelNodeGroupBox = new System.Windows.Forms.GroupBox();
            this.WheelJointsLayout = new System.Windows.Forms.TableLayoutPanel();
            this.NodeListBox = new System.Windows.Forms.ListBox();
            this.AutoFill = new System.Windows.Forms.Button();
            this.LeftWheelsGroup = new System.Windows.Forms.GroupBox();
            this.LeftWheelsPanel = new System.Windows.Forms.TableLayoutPanel();
            this.RobotInfoGroupBox = new System.Windows.Forms.GroupBox();
            this.RobotInfoLayout = new System.Windows.Forms.TableLayoutPanel();
            this.DriveTrainLayout = new System.Windows.Forms.TableLayoutPanel();
            this.DriveTrainLabel = new System.Windows.Forms.Label();
            this.DriveTrainDropdown = new System.Windows.Forms.ComboBox();
            this.WeightLayout = new System.Windows.Forms.TableLayoutPanel();
            this.label3 = new System.Windows.Forms.Label();
            this.WeightUnitSelector = new System.Windows.Forms.ComboBox();
            this.WeightBox = new System.Windows.Forms.NumericUpDown();
            this.RightWheelsGroup = new System.Windows.Forms.GroupBox();
            this.RightWheelsPanel = new System.Windows.Forms.TableLayoutPanel();
            this.MainLayout = new System.Windows.Forms.TableLayoutPanel();
            this.WheelNodeGroupBox.SuspendLayout();
            this.WheelJointsLayout.SuspendLayout();
            this.LeftWheelsGroup.SuspendLayout();
            this.RobotInfoGroupBox.SuspendLayout();
            this.RobotInfoLayout.SuspendLayout();
            this.DriveTrainLayout.SuspendLayout();
            this.WeightLayout.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.WeightBox)).BeginInit();
            this.RightWheelsGroup.SuspendLayout();
            this.MainLayout.SuspendLayout();
            this.SuspendLayout();
            // 
            // DefineWheelsInstruction1
            // 
            this.DefineWheelsInstruction1.AutoSize = true;
            this.DefineWheelsInstruction1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.DefineWheelsInstruction1.Location = new System.Drawing.Point(227, 3);
            this.DefineWheelsInstruction1.Margin = new System.Windows.Forms.Padding(3);
            this.DefineWheelsInstruction1.Name = "DefineWheelsInstruction1";
            this.DefineWheelsInstruction1.Size = new System.Drawing.Size(218, 55);
            this.DefineWheelsInstruction1.TabIndex = 2;
            this.DefineWheelsInstruction1.Text = "Drag the appropriate parts from the list to the left into their respective column" +
    "s below.";
            // 
            // WheelNodeGroupBox
            // 
            this.WheelNodeGroupBox.AutoSize = true;
            this.WheelNodeGroupBox.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.MainLayout.SetColumnSpan(this.WheelNodeGroupBox, 2);
            this.WheelNodeGroupBox.Controls.Add(this.WheelJointsLayout);
            this.WheelNodeGroupBox.Dock = System.Windows.Forms.DockStyle.Top;
            this.WheelNodeGroupBox.Location = new System.Drawing.Point(3, 55);
            this.WheelNodeGroupBox.Name = "WheelNodeGroupBox";
            this.WheelNodeGroupBox.Size = new System.Drawing.Size(454, 109);
            this.WheelNodeGroupBox.TabIndex = 3;
            this.WheelNodeGroupBox.TabStop = false;
            this.WheelNodeGroupBox.Text = "Select Wheels";
            // 
            // WheelJointsLayout
            // 
            this.WheelJointsLayout.AutoSize = true;
            this.WheelJointsLayout.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.WheelJointsLayout.ColumnCount = 2;
            this.WheelJointsLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50F));
            this.WheelJointsLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50F));
            this.WheelJointsLayout.Controls.Add(this.NodeListBox, 0, 0);
            this.WheelJointsLayout.Controls.Add(this.AutoFill, 1, 1);
            this.WheelJointsLayout.Controls.Add(this.DefineWheelsInstruction1, 1, 0);
            this.WheelJointsLayout.Dock = System.Windows.Forms.DockStyle.Top;
            this.WheelJointsLayout.Location = new System.Drawing.Point(3, 16);
            this.WheelJointsLayout.Name = "WheelJointsLayout";
            this.WheelJointsLayout.RowCount = 2;
            this.WheelJointsLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.WheelJointsLayout.RowStyles.Add(new System.Windows.Forms.RowStyle());
            this.WheelJointsLayout.Size = new System.Drawing.Size(448, 90);
            this.WheelJointsLayout.TabIndex = 8;
            // 
            // NodeListBox
            // 
            this.NodeListBox.AllowDrop = true;
            this.NodeListBox.Dock = System.Windows.Forms.DockStyle.Top;
            this.NodeListBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.NodeListBox.FormattingEnabled = true;
            this.NodeListBox.Location = new System.Drawing.Point(3, 4);
            this.NodeListBox.Margin = new System.Windows.Forms.Padding(3, 4, 3, 4);
            this.NodeListBox.Name = "NodeListBox";
            this.WheelJointsLayout.SetRowSpan(this.NodeListBox, 2);
            this.NodeListBox.Size = new System.Drawing.Size(218, 82);
            this.NodeListBox.TabIndex = 4;
            this.NodeListBox.SelectedIndexChanged += new System.EventHandler(this.NodeListBox_SelectedIndexChanged);
            this.NodeListBox.DragDrop += new System.Windows.Forms.DragEventHandler(this.NodeListBox_DragDrop);
            this.NodeListBox.DragEnter += new System.Windows.Forms.DragEventHandler(this.Field_DragEnter);
            this.NodeListBox.MouseDown += new System.Windows.Forms.MouseEventHandler(this.NodeListBox_MouseDown);
            // 
            // AutoFill
            // 
            this.AutoFill.Dock = System.Windows.Forms.DockStyle.Top;
            this.AutoFill.Location = new System.Drawing.Point(227, 64);
            this.AutoFill.Name = "AutoFill";
            this.AutoFill.Size = new System.Drawing.Size(218, 23);
            this.AutoFill.TabIndex = 7;
            this.AutoFill.Text = "AutoFill";
            this.AutoFill.UseVisualStyleBackColor = true;
            // 
            // LeftWheelsGroup
            // 
            this.LeftWheelsGroup.AllowDrop = true;
            this.LeftWheelsGroup.Controls.Add(this.LeftWheelsPanel);
            this.LeftWheelsGroup.Dock = System.Windows.Forms.DockStyle.Fill;
            this.LeftWheelsGroup.Location = new System.Drawing.Point(3, 170);
            this.LeftWheelsGroup.Name = "LeftWheelsGroup";
            this.LeftWheelsGroup.Size = new System.Drawing.Size(224, 480);
            this.LeftWheelsGroup.TabIndex = 1;
            this.LeftWheelsGroup.TabStop = false;
            this.LeftWheelsGroup.Text = "Left Wheels";
            this.LeftWheelsGroup.DragDrop += new System.Windows.Forms.DragEventHandler(this.LeftWheelsPanel_DragDrop);
            this.LeftWheelsGroup.DragEnter += new System.Windows.Forms.DragEventHandler(this.Field_DragEnter);
            // 
            // LeftWheelsPanel
            // 
            this.LeftWheelsPanel.AllowDrop = true;
            this.LeftWheelsPanel.AutoScroll = true;
            this.LeftWheelsPanel.ColumnCount = 2;
            this.LeftWheelsPanel.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.LeftWheelsPanel.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 0F));
            this.LeftWheelsPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.LeftWheelsPanel.Location = new System.Drawing.Point(3, 16);
            this.LeftWheelsPanel.Margin = new System.Windows.Forms.Padding(0);
            this.LeftWheelsPanel.Name = "LeftWheelsPanel";
            this.LeftWheelsPanel.RowCount = 1;
            this.LeftWheelsPanel.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 438F));
            this.LeftWheelsPanel.Size = new System.Drawing.Size(218, 461);
            this.LeftWheelsPanel.TabIndex = 0;
            this.LeftWheelsPanel.DragDrop += new System.Windows.Forms.DragEventHandler(this.LeftWheelsPanel_DragDrop);
            this.LeftWheelsPanel.DragEnter += new System.Windows.Forms.DragEventHandler(this.Field_DragEnter);
            // 
            // RobotInfoGroupBox
            // 
            this.RobotInfoGroupBox.AutoSize = true;
            this.RobotInfoGroupBox.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.MainLayout.SetColumnSpan(this.RobotInfoGroupBox, 2);
            this.RobotInfoGroupBox.Controls.Add(this.RobotInfoLayout);
            this.RobotInfoGroupBox.Dock = System.Windows.Forms.DockStyle.Top;
            this.RobotInfoGroupBox.Location = new System.Drawing.Point(3, 3);
            this.RobotInfoGroupBox.Name = "RobotInfoGroupBox";
            this.RobotInfoGroupBox.Size = new System.Drawing.Size(454, 46);
            this.RobotInfoGroupBox.TabIndex = 6;
            this.RobotInfoGroupBox.TabStop = false;
            this.RobotInfoGroupBox.Text = "General Information";
            // 
            // RobotInfoLayout
            // 
            this.RobotInfoLayout.AutoSize = true;
            this.RobotInfoLayout.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.RobotInfoLayout.ColumnCount = 2;
            this.RobotInfoLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50F));
            this.RobotInfoLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50F));
            this.RobotInfoLayout.Controls.Add(this.DriveTrainLayout, 0, 0);
            this.RobotInfoLayout.Controls.Add(this.WeightLayout, 1, 0);
            this.RobotInfoLayout.Dock = System.Windows.Forms.DockStyle.Top;
            this.RobotInfoLayout.Location = new System.Drawing.Point(3, 16);
            this.RobotInfoLayout.Name = "RobotInfoLayout";
            this.RobotInfoLayout.RowCount = 1;
            this.RobotInfoLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.RobotInfoLayout.Size = new System.Drawing.Size(448, 27);
            this.RobotInfoLayout.TabIndex = 5;
            // 
            // DriveTrainLayout
            // 
            this.DriveTrainLayout.AutoSize = true;
            this.DriveTrainLayout.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.DriveTrainLayout.ColumnCount = 2;
            this.DriveTrainLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
            this.DriveTrainLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
            this.DriveTrainLayout.Controls.Add(this.DriveTrainLabel, 0, 0);
            this.DriveTrainLayout.Controls.Add(this.DriveTrainDropdown, 1, 0);
            this.DriveTrainLayout.Dock = System.Windows.Forms.DockStyle.Top;
            this.DriveTrainLayout.Location = new System.Drawing.Point(0, 0);
            this.DriveTrainLayout.Margin = new System.Windows.Forms.Padding(0);
            this.DriveTrainLayout.Name = "DriveTrainLayout";
            this.DriveTrainLayout.RowCount = 1;
            this.DriveTrainLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.DriveTrainLayout.Size = new System.Drawing.Size(224, 27);
            this.DriveTrainLayout.TabIndex = 0;
            // 
            // DriveTrainLabel
            // 
            this.DriveTrainLabel.AutoSize = true;
            this.DriveTrainLabel.Dock = System.Windows.Forms.DockStyle.Left;
            this.DriveTrainLabel.Location = new System.Drawing.Point(3, 3);
            this.DriveTrainLabel.Margin = new System.Windows.Forms.Padding(3);
            this.DriveTrainLabel.Name = "DriveTrainLabel";
            this.DriveTrainLabel.Size = new System.Drawing.Size(59, 21);
            this.DriveTrainLabel.TabIndex = 0;
            this.DriveTrainLabel.Text = "Drive Train";
            this.DriveTrainLabel.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // DriveTrainDropdown
            // 
            this.DriveTrainDropdown.Dock = System.Windows.Forms.DockStyle.Top;
            this.DriveTrainDropdown.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.DriveTrainDropdown.FormattingEnabled = true;
            this.DriveTrainDropdown.Items.AddRange(new object[] {
            "Select Drive Train...",
            "Tank",
            "Mecanum",
            "Swerve",
            "H-Drive",
            "Other/Custom"});
            this.DriveTrainDropdown.Location = new System.Drawing.Point(68, 3);
            this.DriveTrainDropdown.Name = "DriveTrainDropdown";
            this.DriveTrainDropdown.Size = new System.Drawing.Size(153, 21);
            this.DriveTrainDropdown.TabIndex = 1;
            this.DriveTrainDropdown.SelectionChangeCommitted += new System.EventHandler(this.DriveTrainDropdown_SelectedIndexChanged);
            // 
            // WeightLayout
            // 
            this.WeightLayout.AutoSize = true;
            this.WeightLayout.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.WeightLayout.ColumnCount = 3;
            this.WeightLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
            this.WeightLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.WeightLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
            this.WeightLayout.Controls.Add(this.label3, 0, 0);
            this.WeightLayout.Controls.Add(this.WeightUnitSelector, 2, 0);
            this.WeightLayout.Controls.Add(this.WeightBox, 1, 0);
            this.WeightLayout.Dock = System.Windows.Forms.DockStyle.Top;
            this.WeightLayout.Location = new System.Drawing.Point(224, 0);
            this.WeightLayout.Margin = new System.Windows.Forms.Padding(0);
            this.WeightLayout.Name = "WeightLayout";
            this.WeightLayout.RowCount = 1;
            this.WeightLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.WeightLayout.Size = new System.Drawing.Size(224, 27);
            this.WeightLayout.TabIndex = 1;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Dock = System.Windows.Forms.DockStyle.Left;
            this.label3.Location = new System.Drawing.Point(3, 3);
            this.label3.Margin = new System.Windows.Forms.Padding(3);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(41, 21);
            this.label3.TabIndex = 2;
            this.label3.Text = "Weight";
            this.label3.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // WeightUnitSelector
            // 
            this.WeightUnitSelector.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.WeightUnitSelector.DropDownWidth = 60;
            this.WeightUnitSelector.FormattingEnabled = true;
            this.WeightUnitSelector.Items.AddRange(new object[] {
            "Pounds",
            "Kilograms"});
            this.WeightUnitSelector.Location = new System.Drawing.Point(112, 3);
            this.WeightUnitSelector.Name = "WeightUnitSelector";
            this.WeightUnitSelector.Size = new System.Drawing.Size(109, 21);
            this.WeightUnitSelector.TabIndex = 4;
            // 
            // WeightBox
            // 
            this.WeightBox.Dock = System.Windows.Forms.DockStyle.Fill;
            this.WeightBox.Location = new System.Drawing.Point(50, 3);
            this.WeightBox.Maximum = new decimal(new int[] {
            150,
            0,
            0,
            0});
            this.WeightBox.Name = "WeightBox";
            this.WeightBox.Size = new System.Drawing.Size(56, 20);
            this.WeightBox.TabIndex = 3;
            // 
            // RightWheelsGroup
            // 
            this.RightWheelsGroup.AllowDrop = true;
            this.RightWheelsGroup.Controls.Add(this.RightWheelsPanel);
            this.RightWheelsGroup.Dock = System.Windows.Forms.DockStyle.Fill;
            this.RightWheelsGroup.Location = new System.Drawing.Point(233, 170);
            this.RightWheelsGroup.Name = "RightWheelsGroup";
            this.RightWheelsGroup.Size = new System.Drawing.Size(224, 480);
            this.RightWheelsGroup.TabIndex = 2;
            this.RightWheelsGroup.TabStop = false;
            this.RightWheelsGroup.Text = "Right Wheels";
            this.RightWheelsGroup.DragDrop += new System.Windows.Forms.DragEventHandler(this.RightWheelsPanel_DragDrop);
            this.RightWheelsGroup.DragEnter += new System.Windows.Forms.DragEventHandler(this.Field_DragEnter);
            // 
            // RightWheelsPanel
            // 
            this.RightWheelsPanel.AllowDrop = true;
            this.RightWheelsPanel.AutoScroll = true;
            this.RightWheelsPanel.ColumnCount = 2;
            this.RightWheelsPanel.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.RightWheelsPanel.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 0F));
            this.RightWheelsPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.RightWheelsPanel.Location = new System.Drawing.Point(3, 16);
            this.RightWheelsPanel.Margin = new System.Windows.Forms.Padding(0);
            this.RightWheelsPanel.Name = "RightWheelsPanel";
            this.RightWheelsPanel.RowCount = 1;
            this.RightWheelsPanel.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 438F));
            this.RightWheelsPanel.Size = new System.Drawing.Size(218, 461);
            this.RightWheelsPanel.TabIndex = 1;
            this.RightWheelsPanel.DragDrop += new System.Windows.Forms.DragEventHandler(this.RightWheelsPanel_DragDrop);
            this.RightWheelsPanel.DragEnter += new System.Windows.Forms.DragEventHandler(this.Field_DragEnter);
            // 
            // MainLayout
            // 
            this.MainLayout.ColumnCount = 2;
            this.MainLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50F));
            this.MainLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50F));
            this.MainLayout.Controls.Add(this.RobotInfoGroupBox, 0, 0);
            this.MainLayout.Controls.Add(this.RightWheelsGroup, 1, 2);
            this.MainLayout.Controls.Add(this.WheelNodeGroupBox, 0, 1);
            this.MainLayout.Controls.Add(this.LeftWheelsGroup, 0, 2);
            this.MainLayout.Dock = System.Windows.Forms.DockStyle.Fill;
            this.MainLayout.Location = new System.Drawing.Point(0, 0);
            this.MainLayout.Name = "MainLayout";
            this.MainLayout.RowCount = 3;
            this.MainLayout.RowStyles.Add(new System.Windows.Forms.RowStyle());
            this.MainLayout.RowStyles.Add(new System.Windows.Forms.RowStyle());
            this.MainLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.MainLayout.Size = new System.Drawing.Size(460, 653);
            this.MainLayout.TabIndex = 7;
            // 
            // DefineWheelsPage
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.MainLayout);
            this.Name = "DefineWheelsPage";
            this.Size = new System.Drawing.Size(460, 653);
            this.WheelNodeGroupBox.ResumeLayout(false);
            this.WheelNodeGroupBox.PerformLayout();
            this.WheelJointsLayout.ResumeLayout(false);
            this.WheelJointsLayout.PerformLayout();
            this.LeftWheelsGroup.ResumeLayout(false);
            this.RobotInfoGroupBox.ResumeLayout(false);
            this.RobotInfoGroupBox.PerformLayout();
            this.RobotInfoLayout.ResumeLayout(false);
            this.RobotInfoLayout.PerformLayout();
            this.DriveTrainLayout.ResumeLayout(false);
            this.DriveTrainLayout.PerformLayout();
            this.WeightLayout.ResumeLayout(false);
            this.WeightLayout.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.WeightBox)).EndInit();
            this.RightWheelsGroup.ResumeLayout(false);
            this.MainLayout.ResumeLayout(false);
            this.MainLayout.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion
        private System.Windows.Forms.Label DefineWheelsInstruction1;
        private System.Windows.Forms.GroupBox WheelNodeGroupBox;
        private System.Windows.Forms.GroupBox RobotInfoGroupBox;
        private System.Windows.Forms.ComboBox DriveTrainDropdown;
        private System.Windows.Forms.Label DriveTrainLabel;
        private System.Windows.Forms.Button AutoFill; 
        private System.Windows.Forms.ListBox NodeListBox;
        private System.Windows.Forms.NumericUpDown WeightBox;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.GroupBox LeftWheelsGroup;
        private System.Windows.Forms.GroupBox RightWheelsGroup;
        private System.Windows.Forms.ComboBox WeightUnitSelector;
        private System.Windows.Forms.TableLayoutPanel MainLayout;
        private System.Windows.Forms.TableLayoutPanel WheelJointsLayout;
        private System.Windows.Forms.TableLayoutPanel RobotInfoLayout;
        private System.Windows.Forms.TableLayoutPanel DriveTrainLayout;
        private System.Windows.Forms.TableLayoutPanel WeightLayout;
        private System.Windows.Forms.TableLayoutPanel LeftWheelsPanel;
        private System.Windows.Forms.TableLayoutPanel RightWheelsPanel;
    }
}
