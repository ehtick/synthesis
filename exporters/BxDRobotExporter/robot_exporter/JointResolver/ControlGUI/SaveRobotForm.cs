﻿using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;

namespace JointResolver.ControlGUI
{
    public partial class SaveRobotForm : Form
    {
        static Dictionary<string, string> fields = new Dictionary<string, string>();

        public SaveRobotForm(string initialRobotName)
        {
            InitializeComponent();
            InitializeFields();

            RobotNameLabel.Text = initialRobotName;
            ColorBox.Checked = SynthesisGUI.PluginSettings.GeneralUseFancyColors;
        }

        /// <summary>
        /// Gets the paths for all the synthesis fields.
        /// </summary>
        public void InitializeFields()
        {
            if (fields.Count == 0)
            {
                var dirs = Directory.GetDirectories(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData) + @"\Synthesis\Fields");

                foreach (var dir in dirs)
                {
                    fields.Add(dir.Split(new char[] { '\\' }, StringSplitOptions.RemoveEmptyEntries).Last(), dir);
                    FieldSelectComboBox.Items.Add(dir.Split(new char[] { '\\' }, StringSplitOptions.RemoveEmptyEntries).Last());
                }
            }
            else
            {
                foreach(KeyValuePair<string, string> pair in fields)
                {
                    FieldSelectComboBox.Items.Add(pair.Key);
                }
            }
        }

        public static DialogResult Prompt(string initialRobotName, out string robotName, out bool colors, out bool openSynthesis, out string field)
        {
            try
            {
                SaveRobotForm form = new SaveRobotForm(initialRobotName);
                form.ShowDialog();
                robotName = form.RobotNameTextBox.Text;
                colors = form.ColorBox.Checked;
                openSynthesis = form.OpenSynthesisBox.Checked;

                field = null;

                if (openSynthesis)
                    field = fields[(string)form.FieldSelectComboBox.SelectedItem];

                return form.DialogResult;
            }
            catch (Exception e)
            {
                MessageBox.Show(e.ToString());
                throw;
            }
        }

        private void ButtonOK_Click(object sender, EventArgs e)
        {
            if(RobotNameTextBox.Text != null)
            {
                var InvalidChars = (new string(Path.GetInvalidPathChars()) + new string(Path.GetInvalidFileNameChars())).Distinct();
                foreach (char c in InvalidChars)
                {
                    RobotNameTextBox.Text = RobotNameTextBox.Text.Replace(c.ToString(), "");
                }

                if(File.Exists(SynthesisGUI.PluginSettings.GeneralSaveLocation + "\\" + RobotNameTextBox.Text + @"\skeleton.bxdj") && MessageBox.Show("Overwrite Existing Robot?", "Save Robot", MessageBoxButtons.YesNo) == DialogResult.No)
                {
                    return;
                }

                DialogResult = DialogResult.OK;
                Close();
            }
            else
            {
                MessageBox.Show("Please enter a name for your robot.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ButtonCancel_Click(object sender, EventArgs e)
        {
            if((MessageBox.Show("Are you sure you want to cancel? (All export progress would be lost)", 
                "Cancel", MessageBoxButtons.YesNo, MessageBoxIcon.Warning) == DialogResult.Yes))
            {
                DialogResult = DialogResult.Cancel;
                Close();
            }
        }

        private void OpenSynthesisBox_CheckedChanged(object sender, EventArgs e)
        {
            if (OpenSynthesisBox.Checked)
            {
                FieldLabel.Enabled = true;
                FieldSelectComboBox.Enabled = true;
            }
            else
            {
                FieldLabel.Enabled = false;
                FieldSelectComboBox.Enabled = false;
            }
        }
    }
}
