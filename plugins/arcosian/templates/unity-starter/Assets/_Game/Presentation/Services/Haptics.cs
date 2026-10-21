using System;
using UnityEngine;

namespace Game.Presentation.Services
{
    public enum HapticStrength { Light, Medium, Heavy }

    /// <summary>
    /// Haptic feedback facade. Unity only exposes Handheld.Vibrate (one fixed buzz), so the default maps Heavy to it
    /// and ignores Light and Medium. Assign CustomBackend from a native haptics plugin for graded feedback.
    /// </summary>
    public static class Haptics
    {
        public static bool Enabled = true;
        public static Action<HapticStrength> CustomBackend;

        public static void Light() { Pulse(HapticStrength.Light); }
        public static void Medium() { Pulse(HapticStrength.Medium); }
        public static void Heavy() { Pulse(HapticStrength.Heavy); }

        public static void Pulse(HapticStrength strength)
        {
            if (!Enabled) return;
            if (CustomBackend != null)
            {
                CustomBackend(strength);
                return;
            }
            if (strength == HapticStrength.Heavy) Handheld.Vibrate();
        }
    }
}
