﻿using Synthesis.InputControl;
using Synthesis.InputControl.Enums;
using Synthesis.InputControl.Inputs;
using UnityEngine;
using UnityEngine.UI;

//=========================================================================================
//                                      KeyButton.cs
// Description: OnGUI() script with functions for CreateButton.cs
// Main Content: Various functions to assist in generating control buttons and player lists.
// Adapted from: https://github.com/Gris87/InputControl
//=========================================================================================

namespace Synthesis.GUI
{
    public class KeyButton : MonoBehaviour
    {
        public static KeyButton selectedButton = null;
        public static bool ignoreMouseMovement = true;
        public static bool useKeyModifiers = false;
        public static bool keyBinded = false;

        public KeyMapping keyMapping;
        public int keyIndex;

        private Text mKeyText;

        // Use this for initialization
        void Start()
        {
            GetComponent<Button>().onClick.AddListener(OnClick);
        }

        // Update is called once per frame
        void OnGUI()
        {
            //Implement style preferances; (some assets/styles are configured in Unity: OptionsTab > Canvas > SettingsMode > SettingsPanel
            mKeyText.font = Resources.Load("Fonts/Russo_One") as Font;
            mKeyText.color = Color.white;
            mKeyText.fontSize = 13;

            //Checks if the currentInput uses the ignoreMouseMovement or useKeyModifiers
            //Currently DISABLED (hidden in the Unity menu) due to inconsistent toggle to key updates 08/2017
            if (selectedButton == this)
            {
                CustomInput currentInput = InputControl.InputControl.currentInput(ignoreMouseMovement, useKeyModifiers);

                if (currentInput != null)
                {
                    if (currentInput.modifiers == KeyModifier.NoModifier && currentInput is KeyboardInput
                        && ((KeyboardInput)currentInput).key == KeyCode.Backspace) //Allows users to use the BACKSPACE to set "None" to their controls.
                    {
                        SetInput(new KeyboardInput());
                    }
                    else if (currentInput.modifiers == KeyModifier.NoModifier && currentInput is KeyboardInput
                        && ((KeyboardInput)currentInput).key == KeyCode.Backspace || Binded())
                    {
                        SetInput(new KeyboardInput());
                    }
                    else
                    {
                        SetInput(currentInput);
                    }
                }
            }
        }

        /// <summary>
        /// Updates the primary and secondary control buttons' text label.
        /// Source: https://github.com/Gris87/InputControl
        /// </summary>
        public void UpdateText()
        {
            if (mKeyText == null)
            {
                mKeyText = GetComponentInChildren<Text>();
            }

            switch (keyIndex)
            {
                case 0:
                    mKeyText.text = keyMapping.primaryInput.ToString();
                    break;
                case 1:
                    mKeyText.text = keyMapping.secondaryInput.ToString();
                    break;
            }
        }
        //}

        /// <summary>
        /// Updates the text when the user clicks the control buttons. 
        /// Source: https://github.com/Gris87/InputControl
        /// </summary>
        public void OnClick()
        {
            selectedButton = this;

            if (mKeyText == null)
            {
                mKeyText = GetComponentInChildren<Text>();
            }

            mKeyText.text = "Press Key";
        }

        public static bool Binded()
        {
            if (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.A) || Input.GetKeyDown(KeyCode.S) || Input.GetKeyDown(KeyCode.D))
            {
                return true;
            }
            else
            {
                return false;
            }
        }

        /// <summary>
        /// Sets the primary or secondary input to the selected input from the user.
        /// Source: https://github.com/Gris87/InputControl
        /// </summary>
        /// <param name="input">Input from any device or axis (e.g. Joysticks, Mouse, Keyboard)</param>
        private void SetInput(CustomInput input)
        {
            switch (keyIndex)
            {
                case 0:
                    keyMapping.primaryInput = input;
                    break;
                case 1:
                    keyMapping.secondaryInput = input;
                    break;
            }

            UpdateText();

            selectedButton = null;
        }
    }
}