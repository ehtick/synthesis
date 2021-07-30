using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class InputPanel : MonoBehaviour
{

    [SerializeField]
    public GameObject list;
    [SerializeField]
    public GameObject keybindInput;
    [SerializeField]
    public GameObject dropdownInput;
    [SerializeField]
    public GameObject toggleInput;
    [SerializeField]
    public GameObject titleText;

    List<GameObject> inputList = new List<GameObject>();

    public enum inputType
    {
        toggle,
        dropdown,
        keybind
    }

    // Start is called before the first frame update
    void Start()
    {
        showSettings();
    }

    private void showSettings()
    {
        //TEST SCRIPT: ADDS EXAMPLE SETTINGS. Read from preference manager
        createTitle("Keybinds");
        createKeybind("Move Forward", "W");
        createKeybind("Move Backwards", "S");
        createTitle("Graphics");
        createToggle("Shaders", true);
        List<string> resolutionList = new List<string>();
        resolutionList.Add("Low");
        resolutionList.Add("Medium");
        resolutionList.Add("High");
        createDropdown("Resolution", resolutionList, 0);
    }
    public void saveSettings()//writes settings back into preference manager when save button is clicked
    {
        foreach (GameObject g in inputList)
        {
            //MODIFY THIS: Each Input field has different outputs
            InputMenuInput si = g.GetComponent<InputMenuInput>();
            string name = si._name.text; //shared
            bool toggleState;//toggle
            string key; //for keybind
            int value; //for dropdown (value gives position in list of the selected setting)

            switch (si.getType())//sets each value based on type. Needs to be changed when writing to preference manager
            {
                case inputType.toggle:
                    toggleState = si._toggle.isOn;
                    break;
                case inputType.dropdown:
                    value = si._dropdown.value;
                    break;
                case inputType.keybind:
                    key = si._key.text;
                    break;
                default:
                    Debug.Log("Object in settingsList type not set");
                    break;
            }

            //ADD:
            //write to preference manager
        }
    }

    private void createDropdown(string title, List<string> dropdownList, int value)
    {
        GameObject g = Instantiate(dropdownInput, list.transform);
        g.GetComponent<InputMenuInput>().Init(title, dropdownList, value);
        inputList.Add(g);
    }

    private void createToggle(string title, bool state)
    {
        GameObject g = Instantiate(toggleInput, list.transform);
        g.GetComponent<InputMenuInput>().Init(title, state);
        inputList.Add(g);
    }

    private void createKeybind(string control, string key)
    {
        GameObject g = Instantiate(keybindInput, list.transform);
        g.GetComponent<InputMenuInput>().Init(control, key);
        inputList.Add(g);
    }
    private void createTitle(string title)
    {
        GameObject g = Instantiate(titleText, list.transform);
        g.GetComponentInChildren<TextMeshProUGUI>().text = title;
        inputList.Add(g);
    }
}

