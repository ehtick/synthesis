using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Reflection;
using Google.Protobuf.WellKnownTypes;
// using SynthesisAPI.Translation;
using UnityEngine;

public static class Posting {

    private static string AllData = "";
    
    public const string TRACKING_ID = "UA-81892961-3";
    public const string CLIENT_ID = "666";

    public static void PostEvent(AnalyticsEvent e) {
        AllData += $"v=1&tid={TRACKING_ID}&cid={CLIENT_ID}&{e.GetPostData()}\n";
    }

    public static void PostData(string url) {
        WebClient cli = new WebClient();
        string res = cli.UploadString(url, "POST", AllData);
        Debug.Log($"{res}");
    }
    
}

public class AnalyticsEvent {

    public string Category, Value, Action;
    
    public AnalyticsEvent(string category, string action, string value) {
        Category = category;
        Action = action;
        Value = value;
    }

    public string GetPostData()
        => $"t=event&ec={Category}&ea={Action}&ev={Value}";
}

/*

COLLECT
v=1&tid=[something]&cid=666&t=event&ec=dpmode&ea=spawn_robot&ev=Mean_Machine

BATCH
v=1&tid=[something]&cid=666&t=event&ec=dpmode&ea=spawn_robot&ev=Mean_Machine
v=1&tid=[something]&cid=666&t=event&ec=dpmode&ea=spawn_robot&ev=Mean_Machine

 */
