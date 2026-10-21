using System.Collections.Generic;
using System.Globalization;

namespace Game.Core
{
    /// <summary>
    /// Seeded PCG32 (XSH-RR), identical stream to the godot-mobile template for the same seed.
    /// State serialises as signed-decimal strings because JSON numbers lose precision above 2^53.
    /// </summary>
    public sealed class Rng
    {
        private const ulong Mult = 6364136223846793005UL;

        private ulong _state;
        private ulong _inc;

        public Rng(long seed = 1, long seq = 54)
        {
            unchecked
            {
                _inc = ((ulong)seq << 1) | 1UL;
                NextU32();
                _state += (ulong)seed;
                NextU32();
            }
        }

        public uint NextU32()
        {
            unchecked
            {
                ulong old = _state;
                _state = old * Mult + _inc; // wraps modulo 2^64
                uint xs = (uint)(((old >> 18) ^ old) >> 27);
                int rot = (int)(old >> 59);
                return (xs >> rot) | (xs << ((32 - rot) & 31));
            }
        }

        /// <summary>Uniform-ish integer in [0, n). Modulo bias is below 2^-20 for n up to 4096.</summary>
        public int RandInt(int n)
        {
            return n > 0 ? (int)(NextU32() % (uint)n) : 0;
        }

        public double RandFloat()
        {
            return NextU32() / 4294967296.0;
        }

        public Dictionary<string, object> ToDict()
        {
            unchecked
            {
                return new Dictionary<string, object>
                {
                    { "state", ((long)_state).ToString(CultureInfo.InvariantCulture) },
                    { "inc", ((long)_inc).ToString(CultureInfo.InvariantCulture) },
                };
            }
        }

        /// <summary>Ignores a missing or malformed dictionary and keeps the current state.</summary>
        public void FromDict(Dictionary<string, object> d)
        {
            if (d == null) return;
            long s, i;
            if (long.TryParse(MiniJson.GetString(d, "state", ""), NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out s)
                && long.TryParse(MiniJson.GetString(d, "inc", ""), NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out i))
            {
                unchecked
                {
                    _state = (ulong)s;
                    _inc = (ulong)i;
                }
            }
        }
    }
}
