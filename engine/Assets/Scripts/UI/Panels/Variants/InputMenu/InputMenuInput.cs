using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class InputMenuInput : MonoBehaviour
{
    InputPanel.inputType type;//type


    public TextMeshProUGUI _name;//shared

    //Toggle
    public Toggle _toggle;

    //keybind
    public TextMeshProUGUI _key;
    private bool bind = false;

    //dropdown list
    public TMP_Dropdown _dropdown;


    public void Init(string name, bool state)//TOGGLE
    {
        type = InputPanel.inputType.toggle;
        _name.text = name;
        _toggle.isOn = state;
    }
    public InputPanel.inputType getType()
    {
        return type;
    }
    public void Init(string name, string control)//KEYBIND
    {
        type = InputPanel.inputType.keybind;
        _name.text = name;
        _key.text = control;
    }
    public void Init(string name, List<string> dropdownList, int value)//DROPDOWN LIST
    {
        type = InputPanel.inputType.dropdown;
        _name.text = name;
        foreach (string c in dropdownList)
        {
            _dropdown.options.Add(new TMP_Dropdown.OptionData(c));//CREATE DROPDOWN
        }
        _dropdown.value = value;//CURRENT STATE
    }
    public void setKeybind() //CALLED BY KEYBIND
    {
        bind = true;
    }
    private void OnGUI()
    {
        if (type == InputPanel.inputType.keybind && bind) //SET KEYBIND
        {
            Event e = Event.current;
            if (e.isKey)
            {
                _key.text = e.keyCode.ToString();
                bind = false;
            }
        }
    }

}
