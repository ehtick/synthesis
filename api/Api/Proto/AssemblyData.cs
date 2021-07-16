﻿using System.Collections.Generic;
using System.IO;
using Google.Protobuf;
using UnityEngine;

namespace SynthesisAPI.Proto {
    public partial class AssemblyData : IMessage<AssemblyData> {

        public Dictionary<string, GameObject> ImportedOccurrences = new Dictionary<string, GameObject>();

        // public string Serialize(string outputDir) {
        //     string outputPath;
        //     
        //     var ms = new MemoryStream();
        //     this.WriteTo(ms);
        //     int size = this.CalculateSize();
        //     ms.Seek(0, SeekOrigin.Begin);
        //     byte[] content = new byte[size];
        //     ms.Read(content, 0, size);
        //     
        //     if (outputDir == null) {
        //         string tempPath = Path.GetTempPath() + Path.AltDirectorySeparatorChar + "synth_temp";
        //         if (!Directory.Exists(tempPath))
        //             Directory.CreateDirectory(tempPath);
        //         outputPath = tempPath + Path.AltDirectorySeparatorChar + $"{Translator.TempFileName(content)}.synth";
        //     } else {
        //         if (!Directory.Exists(outputDir))
        //             Directory.CreateDirectory(outputDir);
        //         outputPath = outputDir + Path.AltDirectorySeparatorChar + $"{SimObject.Name}.synth";
        //     }
        //     var stream = File.Create(outputPath);
        //     // this.WriteTo(stream); // Try just using any old stream???
        //     stream.Write(content, 0, content.Length);
        //     stream.Close();
        //     return outputPath;
        // }
    }
}
