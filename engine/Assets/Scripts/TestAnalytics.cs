using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TestAnalytics: MonoBehaviour {
    private void Start() {
        var data = new AnalyticsEvent("cat", "jumped", "9ft");
        Posting.PostEvent(data);
        Posting.PostData("https://www.google-analytics.com/batch");
    }
}
