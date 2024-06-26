// <auto-generated>
//     Generated by the protocol buffer compiler.  DO NOT EDIT!
//     source: signal.proto
// </auto-generated>
#pragma warning disable 1591, 0612, 3021, 8981
#region Designer generated code

using pb = global::Google.Protobuf;
using pbc = global::Google.Protobuf.Collections;
using pbr = global::Google.Protobuf.Reflection;
using scg = global::System.Collections.Generic;
namespace Mirabuf.Signal {

  /// <summary>Holder for reflection information generated from signal.proto</summary>
  public static partial class SignalReflection {

    #region Descriptor
    /// <summary>File descriptor for signal.proto</summary>
    public static pbr::FileDescriptor Descriptor {
      get { return descriptor; }
    }
    private static pbr::FileDescriptor descriptor;

    static SignalReflection() {
      byte[] descriptorData = global::System.Convert.FromBase64String(
          string.Concat(
            "CgxzaWduYWwucHJvdG8SDm1pcmFidWYuc2lnbmFsGgt0eXBlcy5wcm90byKs",
            "AQoHU2lnbmFscxIbCgRpbmZvGAEgASgLMg0ubWlyYWJ1Zi5JbmZvEjoKCnNp",
            "Z25hbF9tYXAYAiADKAsyJi5taXJhYnVmLnNpZ25hbC5TaWduYWxzLlNpZ25h",
            "bE1hcEVudHJ5GkgKDlNpZ25hbE1hcEVudHJ5EgsKA2tleRgBIAEoCRIlCgV2",
            "YWx1ZRgCIAEoCzIWLm1pcmFidWYuc2lnbmFsLlNpZ25hbDoCOAEiogEKBlNp",
            "Z25hbBIbCgRpbmZvGAEgASgLMg0ubWlyYWJ1Zi5JbmZvEiIKAmlvGAIgASgO",
            "MhYubWlyYWJ1Zi5zaWduYWwuSU9UeXBlEhMKC2N1c3RvbV90eXBlGAMgASgJ",
            "EhEKCXNpZ25hbF9pZBgEIAEoDRIvCgtkZXZpY2VfdHlwZRgFIAEoDjIaLm1p",
            "cmFidWYuc2lnbmFsLkRldmljZVR5cGUqHwoGSU9UeXBlEgkKBUlOUFVUEAAS",
            "CgoGT1VUUFVUEAEqTwoKRGV2aWNlVHlwZRIHCgNQV00QABILCgdEaWdpdGFs",
            "EAESCgoGQW5hbG9nEAISBwoDSTJDEAMSCgoGQ0FOQlVTEAQSCgoGQ1VTVE9N",
            "EAViBnByb3RvMw=="));
      descriptor = pbr::FileDescriptor.FromGeneratedCode(descriptorData,
          new pbr::FileDescriptor[] { global::Mirabuf.TypesReflection.Descriptor, },
          new pbr::GeneratedClrTypeInfo(new[] {typeof(global::Mirabuf.Signal.IOType), typeof(global::Mirabuf.Signal.DeviceType), }, null, new pbr::GeneratedClrTypeInfo[] {
            new pbr::GeneratedClrTypeInfo(typeof(global::Mirabuf.Signal.Signals), global::Mirabuf.Signal.Signals.Parser, new[]{ "Info", "SignalMap" }, null, null, null, new pbr::GeneratedClrTypeInfo[] { null, }),
            new pbr::GeneratedClrTypeInfo(typeof(global::Mirabuf.Signal.Signal), global::Mirabuf.Signal.Signal.Parser, new[]{ "Info", "Io", "CustomType", "SignalId", "DeviceType" }, null, null, null, null)
          }));
    }
    #endregion

  }
  #region Enums
  /// <summary>
  ///*
  /// IOType is a way to specify Input or Output.
  /// 
  /// </summary>
  public enum IOType {
    /// <summary>
    //// Input Signal
    /// </summary>
    [pbr::OriginalName("INPUT")] Input = 0,
    /// <summary>
    //// Output Signal
    /// </summary>
    [pbr::OriginalName("OUTPUT")] Output = 1,
  }

  /// <summary>
  ///*
  /// DeviceType needs to be a type of device that has a supported connection
  /// As well as a signal frmae but that can come later
  /// </summary>
  public enum DeviceType {
    [pbr::OriginalName("PWM")] Pwm = 0,
    [pbr::OriginalName("Digital")] Digital = 1,
    [pbr::OriginalName("Analog")] Analog = 2,
    [pbr::OriginalName("I2C")] I2C = 3,
    [pbr::OriginalName("CANBUS")] Canbus = 4,
    [pbr::OriginalName("CUSTOM")] Custom = 5,
  }

  #endregion

  #region Messages
  /// <summary>
  ///*
  /// Signals is a container for all of the potential signals.
  /// </summary>
  public sealed partial class Signals : pb::IMessage<Signals>
  #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
      , pb::IBufferMessage
  #endif
  {
    private static readonly pb::MessageParser<Signals> _parser = new pb::MessageParser<Signals>(() => new Signals());
    private pb::UnknownFieldSet _unknownFields;
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public static pb::MessageParser<Signals> Parser { get { return _parser; } }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public static pbr::MessageDescriptor Descriptor {
      get { return global::Mirabuf.Signal.SignalReflection.Descriptor.MessageTypes[0]; }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    pbr::MessageDescriptor pb::IMessage.Descriptor {
      get { return Descriptor; }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public Signals() {
      OnConstruction();
    }

    partial void OnConstruction();

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public Signals(Signals other) : this() {
      info_ = other.info_ != null ? other.info_.Clone() : null;
      signalMap_ = other.signalMap_.Clone();
      _unknownFields = pb::UnknownFieldSet.Clone(other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public Signals Clone() {
      return new Signals(this);
    }

    /// <summary>Field number for the "info" field.</summary>
    public const int InfoFieldNumber = 1;
    private global::Mirabuf.Info info_;
    /// <summary>
    //// Has identifiable data (id, name, version)
    /// </summary>
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public global::Mirabuf.Info Info {
      get { return info_; }
      set {
        info_ = value;
      }
    }

    /// <summary>Field number for the "signal_map" field.</summary>
    public const int SignalMapFieldNumber = 2;
    private static readonly pbc::MapField<string, global::Mirabuf.Signal.Signal>.Codec _map_signalMap_codec
        = new pbc::MapField<string, global::Mirabuf.Signal.Signal>.Codec(pb::FieldCodec.ForString(10, ""), pb::FieldCodec.ForMessage(18, global::Mirabuf.Signal.Signal.Parser), 18);
    private readonly pbc::MapField<string, global::Mirabuf.Signal.Signal> signalMap_ = new pbc::MapField<string, global::Mirabuf.Signal.Signal>();
    /// <summary>
    //// Contains a full collection of symbols
    /// </summary>
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public pbc::MapField<string, global::Mirabuf.Signal.Signal> SignalMap {
      get { return signalMap_; }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public override bool Equals(object other) {
      return Equals(other as Signals);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public bool Equals(Signals other) {
      if (ReferenceEquals(other, null)) {
        return false;
      }
      if (ReferenceEquals(other, this)) {
        return true;
      }
      if (!object.Equals(Info, other.Info)) return false;
      if (!SignalMap.Equals(other.SignalMap)) return false;
      return Equals(_unknownFields, other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public override int GetHashCode() {
      int hash = 1;
      if (info_ != null) hash ^= Info.GetHashCode();
      hash ^= SignalMap.GetHashCode();
      if (_unknownFields != null) {
        hash ^= _unknownFields.GetHashCode();
      }
      return hash;
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public override string ToString() {
      return pb::JsonFormatter.ToDiagnosticString(this);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public void WriteTo(pb::CodedOutputStream output) {
    #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
      output.WriteRawMessage(this);
    #else
      if (info_ != null) {
        output.WriteRawTag(10);
        output.WriteMessage(Info);
      }
      signalMap_.WriteTo(output, _map_signalMap_codec);
      if (_unknownFields != null) {
        _unknownFields.WriteTo(output);
      }
    #endif
    }

    #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    void pb::IBufferMessage.InternalWriteTo(ref pb::WriteContext output) {
      if (info_ != null) {
        output.WriteRawTag(10);
        output.WriteMessage(Info);
      }
      signalMap_.WriteTo(ref output, _map_signalMap_codec);
      if (_unknownFields != null) {
        _unknownFields.WriteTo(ref output);
      }
    }
    #endif

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public int CalculateSize() {
      int size = 0;
      if (info_ != null) {
        size += 1 + pb::CodedOutputStream.ComputeMessageSize(Info);
      }
      size += signalMap_.CalculateSize(_map_signalMap_codec);
      if (_unknownFields != null) {
        size += _unknownFields.CalculateSize();
      }
      return size;
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public void MergeFrom(Signals other) {
      if (other == null) {
        return;
      }
      if (other.info_ != null) {
        if (info_ == null) {
          Info = new global::Mirabuf.Info();
        }
        Info.MergeFrom(other.Info);
      }
      signalMap_.MergeFrom(other.signalMap_);
      _unknownFields = pb::UnknownFieldSet.MergeFrom(_unknownFields, other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public void MergeFrom(pb::CodedInputStream input) {
    #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
      input.ReadRawMessage(this);
    #else
      uint tag;
      while ((tag = input.ReadTag()) != 0) {
        switch(tag) {
          default:
            _unknownFields = pb::UnknownFieldSet.MergeFieldFrom(_unknownFields, input);
            break;
          case 10: {
            if (info_ == null) {
              Info = new global::Mirabuf.Info();
            }
            input.ReadMessage(Info);
            break;
          }
          case 18: {
            signalMap_.AddEntriesFrom(input, _map_signalMap_codec);
            break;
          }
        }
      }
    #endif
    }

    #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    void pb::IBufferMessage.InternalMergeFrom(ref pb::ParseContext input) {
      uint tag;
      while ((tag = input.ReadTag()) != 0) {
        switch(tag) {
          default:
            _unknownFields = pb::UnknownFieldSet.MergeFieldFrom(_unknownFields, ref input);
            break;
          case 10: {
            if (info_ == null) {
              Info = new global::Mirabuf.Info();
            }
            input.ReadMessage(Info);
            break;
          }
          case 18: {
            signalMap_.AddEntriesFrom(ref input, _map_signalMap_codec);
            break;
          }
        }
      }
    }
    #endif

  }

  /// <summary>
  ///*
  /// Signal is a way to define a controlling signal.
  /// 
  /// TODO: Add Origin
  /// TODO: Decide how this is linked to a exported object
  /// </summary>
  public sealed partial class Signal : pb::IMessage<Signal>
  #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
      , pb::IBufferMessage
  #endif
  {
    private static readonly pb::MessageParser<Signal> _parser = new pb::MessageParser<Signal>(() => new Signal());
    private pb::UnknownFieldSet _unknownFields;
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public static pb::MessageParser<Signal> Parser { get { return _parser; } }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public static pbr::MessageDescriptor Descriptor {
      get { return global::Mirabuf.Signal.SignalReflection.Descriptor.MessageTypes[1]; }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    pbr::MessageDescriptor pb::IMessage.Descriptor {
      get { return Descriptor; }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public Signal() {
      OnConstruction();
    }

    partial void OnConstruction();

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public Signal(Signal other) : this() {
      info_ = other.info_ != null ? other.info_.Clone() : null;
      io_ = other.io_;
      customType_ = other.customType_;
      signalId_ = other.signalId_;
      deviceType_ = other.deviceType_;
      _unknownFields = pb::UnknownFieldSet.Clone(other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public Signal Clone() {
      return new Signal(this);
    }

    /// <summary>Field number for the "info" field.</summary>
    public const int InfoFieldNumber = 1;
    private global::Mirabuf.Info info_;
    /// <summary>
    //// Has identifiable data (id, name, version)
    /// </summary>
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public global::Mirabuf.Info Info {
      get { return info_; }
      set {
        info_ = value;
      }
    }

    /// <summary>Field number for the "io" field.</summary>
    public const int IoFieldNumber = 2;
    private global::Mirabuf.Signal.IOType io_ = global::Mirabuf.Signal.IOType.Input;
    /// <summary>
    //// Is this a Input or Output
    /// </summary>
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public global::Mirabuf.Signal.IOType Io {
      get { return io_; }
      set {
        io_ = value;
      }
    }

    /// <summary>Field number for the "custom_type" field.</summary>
    public const int CustomTypeFieldNumber = 3;
    private string customType_ = "";
    /// <summary>
    //// The name of a custom input type that is not listed as a device type
    /// </summary>
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public string CustomType {
      get { return customType_; }
      set {
        customType_ = pb::ProtoPreconditions.CheckNotNull(value, "value");
      }
    }

    /// <summary>Field number for the "signal_id" field.</summary>
    public const int SignalIdFieldNumber = 4;
    private uint signalId_;
    /// <summary>
    //// ID for a given signal that exists... PWM 2, CANBUS 4
    /// </summary>
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public uint SignalId {
      get { return signalId_; }
      set {
        signalId_ = value;
      }
    }

    /// <summary>Field number for the "device_type" field.</summary>
    public const int DeviceTypeFieldNumber = 5;
    private global::Mirabuf.Signal.DeviceType deviceType_ = global::Mirabuf.Signal.DeviceType.Pwm;
    /// <summary>
    //// Enum for device type that should always be set
    /// </summary>
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public global::Mirabuf.Signal.DeviceType DeviceType {
      get { return deviceType_; }
      set {
        deviceType_ = value;
      }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public override bool Equals(object other) {
      return Equals(other as Signal);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public bool Equals(Signal other) {
      if (ReferenceEquals(other, null)) {
        return false;
      }
      if (ReferenceEquals(other, this)) {
        return true;
      }
      if (!object.Equals(Info, other.Info)) return false;
      if (Io != other.Io) return false;
      if (CustomType != other.CustomType) return false;
      if (SignalId != other.SignalId) return false;
      if (DeviceType != other.DeviceType) return false;
      return Equals(_unknownFields, other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public override int GetHashCode() {
      int hash = 1;
      if (info_ != null) hash ^= Info.GetHashCode();
      if (Io != global::Mirabuf.Signal.IOType.Input) hash ^= Io.GetHashCode();
      if (CustomType.Length != 0) hash ^= CustomType.GetHashCode();
      if (SignalId != 0) hash ^= SignalId.GetHashCode();
      if (DeviceType != global::Mirabuf.Signal.DeviceType.Pwm) hash ^= DeviceType.GetHashCode();
      if (_unknownFields != null) {
        hash ^= _unknownFields.GetHashCode();
      }
      return hash;
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public override string ToString() {
      return pb::JsonFormatter.ToDiagnosticString(this);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public void WriteTo(pb::CodedOutputStream output) {
    #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
      output.WriteRawMessage(this);
    #else
      if (info_ != null) {
        output.WriteRawTag(10);
        output.WriteMessage(Info);
      }
      if (Io != global::Mirabuf.Signal.IOType.Input) {
        output.WriteRawTag(16);
        output.WriteEnum((int) Io);
      }
      if (CustomType.Length != 0) {
        output.WriteRawTag(26);
        output.WriteString(CustomType);
      }
      if (SignalId != 0) {
        output.WriteRawTag(32);
        output.WriteUInt32(SignalId);
      }
      if (DeviceType != global::Mirabuf.Signal.DeviceType.Pwm) {
        output.WriteRawTag(40);
        output.WriteEnum((int) DeviceType);
      }
      if (_unknownFields != null) {
        _unknownFields.WriteTo(output);
      }
    #endif
    }

    #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    void pb::IBufferMessage.InternalWriteTo(ref pb::WriteContext output) {
      if (info_ != null) {
        output.WriteRawTag(10);
        output.WriteMessage(Info);
      }
      if (Io != global::Mirabuf.Signal.IOType.Input) {
        output.WriteRawTag(16);
        output.WriteEnum((int) Io);
      }
      if (CustomType.Length != 0) {
        output.WriteRawTag(26);
        output.WriteString(CustomType);
      }
      if (SignalId != 0) {
        output.WriteRawTag(32);
        output.WriteUInt32(SignalId);
      }
      if (DeviceType != global::Mirabuf.Signal.DeviceType.Pwm) {
        output.WriteRawTag(40);
        output.WriteEnum((int) DeviceType);
      }
      if (_unknownFields != null) {
        _unknownFields.WriteTo(ref output);
      }
    }
    #endif

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public int CalculateSize() {
      int size = 0;
      if (info_ != null) {
        size += 1 + pb::CodedOutputStream.ComputeMessageSize(Info);
      }
      if (Io != global::Mirabuf.Signal.IOType.Input) {
        size += 1 + pb::CodedOutputStream.ComputeEnumSize((int) Io);
      }
      if (CustomType.Length != 0) {
        size += 1 + pb::CodedOutputStream.ComputeStringSize(CustomType);
      }
      if (SignalId != 0) {
        size += 1 + pb::CodedOutputStream.ComputeUInt32Size(SignalId);
      }
      if (DeviceType != global::Mirabuf.Signal.DeviceType.Pwm) {
        size += 1 + pb::CodedOutputStream.ComputeEnumSize((int) DeviceType);
      }
      if (_unknownFields != null) {
        size += _unknownFields.CalculateSize();
      }
      return size;
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public void MergeFrom(Signal other) {
      if (other == null) {
        return;
      }
      if (other.info_ != null) {
        if (info_ == null) {
          Info = new global::Mirabuf.Info();
        }
        Info.MergeFrom(other.Info);
      }
      if (other.Io != global::Mirabuf.Signal.IOType.Input) {
        Io = other.Io;
      }
      if (other.CustomType.Length != 0) {
        CustomType = other.CustomType;
      }
      if (other.SignalId != 0) {
        SignalId = other.SignalId;
      }
      if (other.DeviceType != global::Mirabuf.Signal.DeviceType.Pwm) {
        DeviceType = other.DeviceType;
      }
      _unknownFields = pb::UnknownFieldSet.MergeFrom(_unknownFields, other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public void MergeFrom(pb::CodedInputStream input) {
    #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
      input.ReadRawMessage(this);
    #else
      uint tag;
      while ((tag = input.ReadTag()) != 0) {
        switch(tag) {
          default:
            _unknownFields = pb::UnknownFieldSet.MergeFieldFrom(_unknownFields, input);
            break;
          case 10: {
            if (info_ == null) {
              Info = new global::Mirabuf.Info();
            }
            input.ReadMessage(Info);
            break;
          }
          case 16: {
            Io = (global::Mirabuf.Signal.IOType) input.ReadEnum();
            break;
          }
          case 26: {
            CustomType = input.ReadString();
            break;
          }
          case 32: {
            SignalId = input.ReadUInt32();
            break;
          }
          case 40: {
            DeviceType = (global::Mirabuf.Signal.DeviceType) input.ReadEnum();
            break;
          }
        }
      }
    #endif
    }

    #if !GOOGLE_PROTOBUF_REFSTRUCT_COMPATIBILITY_MODE
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    void pb::IBufferMessage.InternalMergeFrom(ref pb::ParseContext input) {
      uint tag;
      while ((tag = input.ReadTag()) != 0) {
        switch(tag) {
          default:
            _unknownFields = pb::UnknownFieldSet.MergeFieldFrom(_unknownFields, ref input);
            break;
          case 10: {
            if (info_ == null) {
              Info = new global::Mirabuf.Info();
            }
            input.ReadMessage(Info);
            break;
          }
          case 16: {
            Io = (global::Mirabuf.Signal.IOType) input.ReadEnum();
            break;
          }
          case 26: {
            CustomType = input.ReadString();
            break;
          }
          case 32: {
            SignalId = input.ReadUInt32();
            break;
          }
          case 40: {
            DeviceType = (global::Mirabuf.Signal.DeviceType) input.ReadEnum();
            break;
          }
        }
      }
    }
    #endif

  }

  #endregion

}

#endregion Designer generated code
