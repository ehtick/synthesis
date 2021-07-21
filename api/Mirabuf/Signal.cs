// <auto-generated>
//     Generated by the protocol buffer compiler.  DO NOT EDIT!
//     source: signal.proto
// </auto-generated>
#pragma warning disable 1591, 0612, 3021
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
            "CgxzaWduYWwucHJvdG8SDm1pcmFidWYuc2lnbmFsGgt0eXBlcy5wcm90byJ4",
            "CgZTaWduYWwSGwoEaW5mbxgBIAEoCzINLm1pcmFidWYuSW5mbxIiCgJpbxgC",
            "IAEoDjIWLm1pcmFidWYuc2lnbmFsLklPVHlwZRItCg1zaWduYWxfZm9ybWF0",
            "GAMgASgOMhYubWlyYWJ1Zi5zaWduYWwuRm9ybWF0IqwBCgdTaWduYWxzEhsK",
            "BGluZm8YASABKAsyDS5taXJhYnVmLkluZm8SOgoKc2lnbmFsX21hcBgCIAMo",
            "CzImLm1pcmFidWYuc2lnbmFsLlNpZ25hbHMuU2lnbmFsTWFwRW50cnkaSAoO",
            "U2lnbmFsTWFwRW50cnkSCwoDa2V5GAEgASgJEiUKBXZhbHVlGAIgASgLMhYu",
            "bWlyYWJ1Zi5zaWduYWwuU2lnbmFsOgI4ASofCgZJT1R5cGUSCQoFSU5QVVQQ",
            "ABIKCgZPVVRQVVQQASozCgZGb3JtYXQSCwoHRElHSVRBTBAAEgoKBkFOQUxP",
            "RxABEgcKA1BXTRACEgcKA0kyQxADYgZwcm90bzM="));
      descriptor = pbr::FileDescriptor.FromGeneratedCode(descriptorData,
          new pbr::FileDescriptor[] { global::Mirabuf.TypesReflection.Descriptor, },
          new pbr::GeneratedClrTypeInfo(new[] {typeof(global::Mirabuf.Signal.IOType), typeof(global::Mirabuf.Signal.Format), }, null, new pbr::GeneratedClrTypeInfo[] {
            new pbr::GeneratedClrTypeInfo(typeof(global::Mirabuf.Signal.Signal), global::Mirabuf.Signal.Signal.Parser, new[]{ "Info", "Io", "SignalFormat" }, null, null, null, null),
            new pbr::GeneratedClrTypeInfo(typeof(global::Mirabuf.Signal.Signals), global::Mirabuf.Signal.Signals.Parser, new[]{ "Info", "SignalMap" }, null, null, null, new pbr::GeneratedClrTypeInfo[] { null, })
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
  /// Format is used to define the expected message format.
  /// 
  /// </summary>
  public enum Format {
    /// <summary>
    //// Digital Format 
    /// </summary>
    [pbr::OriginalName("DIGITAL")] Digital = 0,
    /// <summary>
    //// Analog Format
    /// </summary>
    [pbr::OriginalName("ANALOG")] Analog = 1,
    /// <summary>
    //// PWM Format
    /// </summary>
    [pbr::OriginalName("PWM")] Pwm = 2,
    /// <summary>
    //// I2C Format
    /// </summary>
    [pbr::OriginalName("I2C")] I2C = 3,
  }

  #endregion

  #region Messages
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
      get { return global::Mirabuf.Signal.SignalReflection.Descriptor.MessageTypes[0]; }
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
      signalFormat_ = other.signalFormat_;
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

    /// <summary>Field number for the "signal_format" field.</summary>
    public const int SignalFormatFieldNumber = 3;
    private global::Mirabuf.Signal.Format signalFormat_ = global::Mirabuf.Signal.Format.Digital;
    /// <summary>
    //// Is this a PWM, Digital, Analog, I2C, etc.
    /// </summary>
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public global::Mirabuf.Signal.Format SignalFormat {
      get { return signalFormat_; }
      set {
        signalFormat_ = value;
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
      if (SignalFormat != other.SignalFormat) return false;
      return Equals(_unknownFields, other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    [global::System.CodeDom.Compiler.GeneratedCode("protoc", null)]
    public override int GetHashCode() {
      int hash = 1;
      if (info_ != null) hash ^= Info.GetHashCode();
      if (Io != global::Mirabuf.Signal.IOType.Input) hash ^= Io.GetHashCode();
      if (SignalFormat != global::Mirabuf.Signal.Format.Digital) hash ^= SignalFormat.GetHashCode();
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
      if (SignalFormat != global::Mirabuf.Signal.Format.Digital) {
        output.WriteRawTag(24);
        output.WriteEnum((int) SignalFormat);
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
      if (SignalFormat != global::Mirabuf.Signal.Format.Digital) {
        output.WriteRawTag(24);
        output.WriteEnum((int) SignalFormat);
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
      if (SignalFormat != global::Mirabuf.Signal.Format.Digital) {
        size += 1 + pb::CodedOutputStream.ComputeEnumSize((int) SignalFormat);
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
      if (other.SignalFormat != global::Mirabuf.Signal.Format.Digital) {
        SignalFormat = other.SignalFormat;
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
          case 24: {
            SignalFormat = (global::Mirabuf.Signal.Format) input.ReadEnum();
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
          case 24: {
            SignalFormat = (global::Mirabuf.Signal.Format) input.ReadEnum();
            break;
          }
        }
      }
    }
    #endif

  }

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
      get { return global::Mirabuf.Signal.SignalReflection.Descriptor.MessageTypes[1]; }
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
      signalMap_.Add(other.signalMap_);
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

  #endregion

}

#endregion Designer generated code
