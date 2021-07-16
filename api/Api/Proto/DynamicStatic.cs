using Google.Protobuf;

namespace SynthesisAPI.Proto {
    public partial class DynamicStatic : IMessage<DynamicStatic> {
        
        public static implicit operator DynamicStatic(byte[] buf)
            => Parser.ParseFrom(buf);
        
    }
}
