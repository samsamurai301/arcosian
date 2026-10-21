using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace Game.Core
{
    /// <summary>
    /// Gameplay tuning loaded from Assets/_Game/Data/tuning.json with safe defaults and clamping.
    /// Designers edit the JSON only; never hard-code balance values.
    /// </summary>
    public sealed class Tuning
    {
        public int Size = 5;
        public int WinTile = 1024;
        public int InitialTiles = 2;
        public double SpawnFourChance = 0.1;

        /// <summary>Unreadable or null input yields the defaults; known keys are clamped to sane ranges.</summary>
        public static Tuning Parse(string json)
        {
            var t = new Tuning();
            object parsed = null;
            if (string.IsNullOrEmpty(json) || !MiniJson.TryParse(json, out parsed)) return t;
            var d = parsed as Dictionary<string, object>;
            if (d == null) return t;
            t.Size = Math.Max(2, Math.Min(8, (int)MiniJson.GetLong(d, "size", t.Size)));
            t.WinTile = Math.Max(4, (int)MiniJson.GetLong(d, "win_tile", t.WinTile));
            t.InitialTiles = Math.Max(0, Math.Min(t.Size * t.Size, (int)MiniJson.GetLong(d, "initial_tiles", t.InitialTiles)));
            t.SpawnFourChance = Math.Max(0.0, Math.Min(1.0, MiniJson.GetDouble(d, "spawn_four_chance", t.SpawnFourChance)));
            return t;
        }
    }

    /// <summary>
    /// Tiny JSON reader/writer so Core needs no engine or third-party serializer.
    /// Parse returns Dictionary&lt;string,object&gt;, List&lt;object&gt;, string, long (integer literals), double, bool or null.
    /// </summary>
    public static class MiniJson
    {
        public static object Parse(string text)
        {
            var p = new Parser(text);
            object v = p.ReadValue();
            p.SkipWs();
            if (!p.AtEnd) throw p.Error("trailing characters");
            return v;
        }

        public static bool TryParse(string text, out object value)
        {
            try
            {
                value = Parse(text);
                return true;
            }
            catch (FormatException)
            {
                value = null;
                return false;
            }
        }

        public static string Write(object value, bool pretty = false)
        {
            var sb = new StringBuilder();
            WriteValue(sb, value, pretty ? 0 : -1);
            return sb.ToString();
        }

        /// <summary>Deep copy via a write/parse round trip (the result only holds JSON types).</summary>
        public static object Clone(object value)
        {
            return Parse(Write(value));
        }

        // ---- typed accessors (tolerant: wrong type or missing key gives the fallback) ----

        public static bool IsNumber(object v)
        {
            switch (v)
            {
                case int _:
                case long _:
                case double _:
                case float _:
                case uint _:
                case short _:
                case ushort _:
                case byte _:
                case ulong _:
                    return true;
                default:
                    return false;
            }
        }

        public static double ToDouble(object v)
        {
            return Convert.ToDouble(v, CultureInfo.InvariantCulture);
        }

        public static long AsLong(object v, long fallback = 0)
        {
            if (v is long l) return l;
            if (v is double d) return (long)d;
            if (IsNumber(v)) return Convert.ToInt64(v, CultureInfo.InvariantCulture);
            return fallback;
        }

        public static long GetLong(Dictionary<string, object> d, string key, long fallback = 0)
        {
            object v;
            return d != null && d.TryGetValue(key, out v) ? AsLong(v, fallback) : fallback;
        }

        public static double GetDouble(Dictionary<string, object> d, string key, double fallback = 0)
        {
            object v;
            return d != null && d.TryGetValue(key, out v) && IsNumber(v) ? ToDouble(v) : fallback;
        }

        public static string GetString(Dictionary<string, object> d, string key, string fallback = "")
        {
            object v;
            return d != null && d.TryGetValue(key, out v) && v is string s ? s : fallback;
        }

        public static bool GetBool(Dictionary<string, object> d, string key, bool fallback = false)
        {
            object v;
            return d != null && d.TryGetValue(key, out v) && v is bool b ? b : fallback;
        }

        public static Dictionary<string, object> GetDict(Dictionary<string, object> d, string key)
        {
            object v;
            return d != null && d.TryGetValue(key, out v) ? v as Dictionary<string, object> : null;
        }

        // ---- writer ----

        private static void WriteValue(StringBuilder sb, object v, int indent)
        {
            switch (v)
            {
                case null:
                    sb.Append("null");
                    return;
                case string s:
                    Quote(sb, s);
                    return;
                case bool b:
                    sb.Append(b ? "true" : "false");
                    return;
                case double dbl:
                    sb.Append(double.IsNaN(dbl) || double.IsInfinity(dbl) ? "null" : dbl.ToString("R", CultureInfo.InvariantCulture));
                    return;
                case float f:
                    sb.Append(float.IsNaN(f) || float.IsInfinity(f) ? "null" : f.ToString("R", CultureInfo.InvariantCulture));
                    return;
                case IDictionary<string, object> dict:
                    WriteObject(sb, dict, indent);
                    return;
                case IEnumerable seq:
                    WriteArray(sb, seq, indent);
                    return;
            }
            if (IsNumber(v) || v is decimal)
                sb.Append(Convert.ToString(v, CultureInfo.InvariantCulture));
            else
                Quote(sb, v.ToString());
        }

        private static void WriteObject(StringBuilder sb, IDictionary<string, object> dict, int indent)
        {
            if (dict.Count == 0)
            {
                sb.Append("{}");
                return;
            }
            sb.Append('{');
            bool first = true;
            foreach (KeyValuePair<string, object> kv in dict)
            {
                if (!first) sb.Append(',');
                first = false;
                NewLine(sb, indent < 0 ? -1 : indent + 1);
                Quote(sb, kv.Key);
                sb.Append(indent < 0 ? ":" : ": ");
                WriteValue(sb, kv.Value, indent < 0 ? -1 : indent + 1);
            }
            NewLine(sb, indent);
            sb.Append('}');
        }

        private static void WriteArray(StringBuilder sb, IEnumerable seq, int indent)
        {
            sb.Append('[');
            bool first = true;
            foreach (object item in seq)
            {
                if (!first) sb.Append(',');
                first = false;
                NewLine(sb, indent < 0 ? -1 : indent + 1);
                WriteValue(sb, item, indent < 0 ? -1 : indent + 1);
            }
            if (!first) NewLine(sb, indent);
            sb.Append(']');
        }

        private static void NewLine(StringBuilder sb, int indent)
        {
            if (indent < 0) return;
            sb.Append('\n').Append(' ', indent * 2);
        }

        private static void Quote(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
        }

        // ---- reader ----

        private sealed class Parser
        {
            private const int MaxDepth = 64;
            private readonly string _s;
            private int _i;
            private int _depth;

            public Parser(string s)
            {
                _s = s ?? "";
            }

            public bool AtEnd { get { return _i >= _s.Length; } }

            public FormatException Error(string message)
            {
                return new FormatException(message + " at offset " + _i.ToString(CultureInfo.InvariantCulture));
            }

            public void SkipWs()
            {
                while (_i < _s.Length && (_s[_i] == ' ' || _s[_i] == '\t' || _s[_i] == '\n' || _s[_i] == '\r')) _i++;
            }

            public object ReadValue()
            {
                SkipWs();
                if (AtEnd) throw Error("unexpected end of input");
                switch (_s[_i])
                {
                    case '{': return ReadObject();
                    case '[': return ReadArray();
                    case '"': return ReadString();
                    case 't': return ReadLiteral("true", true);
                    case 'f': return ReadLiteral("false", false);
                    case 'n': return ReadLiteral("null", null);
                    default: return ReadNumber();
                }
            }

            private object ReadLiteral(string word, object result)
            {
                if (string.CompareOrdinal(_s, _i, word, 0, word.Length) != 0) throw Error("invalid literal");
                _i += word.Length;
                return result;
            }

            private Dictionary<string, object> ReadObject()
            {
                if (++_depth > MaxDepth) throw Error("nesting too deep");
                _i++; // {
                var d = new Dictionary<string, object>();
                SkipWs();
                if (!AtEnd && _s[_i] == '}')
                {
                    _i++;
                    _depth--;
                    return d;
                }
                while (true)
                {
                    SkipWs();
                    if (AtEnd || _s[_i] != '"') throw Error("expected string key");
                    string key = ReadString();
                    SkipWs();
                    if (AtEnd || _s[_i] != ':') throw Error("expected ':'");
                    _i++;
                    d[key] = ReadValue();
                    SkipWs();
                    if (AtEnd) throw Error("unterminated object");
                    char c = _s[_i++];
                    if (c == ',') continue;
                    if (c == '}') break;
                    throw Error("expected ',' or '}'");
                }
                _depth--;
                return d;
            }

            private List<object> ReadArray()
            {
                if (++_depth > MaxDepth) throw Error("nesting too deep");
                _i++; // [
                var list = new List<object>();
                SkipWs();
                if (!AtEnd && _s[_i] == ']')
                {
                    _i++;
                    _depth--;
                    return list;
                }
                while (true)
                {
                    list.Add(ReadValue());
                    SkipWs();
                    if (AtEnd) throw Error("unterminated array");
                    char c = _s[_i++];
                    if (c == ',') continue;
                    if (c == ']') break;
                    throw Error("expected ',' or ']'");
                }
                _depth--;
                return list;
            }

            private string ReadString()
            {
                _i++; // opening quote
                var sb = new StringBuilder();
                while (true)
                {
                    if (AtEnd) throw Error("unterminated string");
                    char c = _s[_i++];
                    if (c == '"') break;
                    if (c != '\\')
                    {
                        sb.Append(c);
                        continue;
                    }
                    if (AtEnd) throw Error("unterminated escape");
                    char e = _s[_i++];
                    switch (e)
                    {
                        case '"': sb.Append('"'); break;
                        case '\\': sb.Append('\\'); break;
                        case '/': sb.Append('/'); break;
                        case 'b': sb.Append('\b'); break;
                        case 'f': sb.Append('\f'); break;
                        case 'n': sb.Append('\n'); break;
                        case 'r': sb.Append('\r'); break;
                        case 't': sb.Append('\t'); break;
                        case 'u':
                            int code;
                            if (_i + 4 > _s.Length
                                || !int.TryParse(_s.Substring(_i, 4), NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture, out code))
                                throw Error("bad \\u escape");
                            sb.Append((char)code);
                            _i += 4;
                            break;
                        default:
                            throw Error("bad escape");
                    }
                }
                return sb.ToString();
            }

            private object ReadNumber()
            {
                int start = _i;
                while (_i < _s.Length && "+-0123456789.eE".IndexOf(_s[_i]) >= 0) _i++;
                if (_i == start) throw Error("unexpected character");
                string tok = _s.Substring(start, _i - start);
                long l;
                double d;
                if (tok.IndexOfAny(new[] { '.', 'e', 'E' }) < 0
                    && long.TryParse(tok, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out l))
                    return l;
                if (double.TryParse(tok, NumberStyles.Float, CultureInfo.InvariantCulture, out d)) return d;
                throw Error("bad number");
            }
        }
    }
}
