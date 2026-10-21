using System;
using System.Collections.Generic;
using Game.Core;
using UnityEngine;

namespace Game.Presentation.Services
{
    public interface IAnalytics
    {
        void LogEvent(string name, IDictionary<string, object> parameters);
    }

    /// <summary>Keeps the last Capacity events in memory and writes them to the Unity console.</summary>
    public sealed class DebugAnalytics : IAnalytics
    {
        public const int Capacity = 64;
        public readonly List<string> Entries = new List<string>();

        public void LogEvent(string name, IDictionary<string, object> parameters)
        {
            string line = name + " " + MiniJson.Write(parameters);
            if (Entries.Count >= Capacity) Entries.RemoveAt(0);
            Entries.Add(line);
            Debug.Log("[analytics] " + line);
        }
    }

    /// <summary>Fan-out to every registered backend. Event names must match the project's event taxonomy (snake_case).</summary>
    public static class Analytics
    {
        public static readonly List<IAnalytics> Backends = new List<IAnalytics>();

        public static void Log(string name, IDictionary<string, object> parameters = null)
        {
            if (!IsSnakeCase(name)) Debug.LogWarning("[analytics] event name is not snake_case: " + name);
            foreach (IAnalytics backend in Backends)
            {
                try
                {
                    backend.LogEvent(name, parameters);
                }
                catch (Exception e)
                {
                    Debug.LogException(e); // a broken backend must never break gameplay
                }
            }
        }

        private static bool IsSnakeCase(string name)
        {
            if (string.IsNullOrEmpty(name) || name.Length > 40 || name[0] < 'a' || name[0] > 'z') return false;
            foreach (char c in name)
                if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_')) return false;
            return true;
        }
    }
}
