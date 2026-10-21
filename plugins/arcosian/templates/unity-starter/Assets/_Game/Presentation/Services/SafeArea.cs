using UnityEngine;

namespace Game.Presentation.Services
{
    /// <summary>
    /// Fits this RectTransform to Screen.safeArea (notch, rounded corners, gesture bar).
    /// Put HUD under it; backgrounds go outside it. Zero insets on desktop; set DebugRect to preview a notch.
    /// </summary>
    [RequireComponent(typeof(RectTransform))]
    public sealed class SafeArea : MonoBehaviour
    {
        /// <summary>When set, replaces Screen.safeArea (screen pixels) to preview insets in the editor.</summary>
        public static Rect? DebugRect;

        private Rect _applied;
        private Vector2Int _screen;

        public static Rect Current { get { return DebugRect ?? Screen.safeArea; } }

        /// <summary>Insets in screen pixels: x=left, y=bottom, z=right, w=top.</summary>
        public static Vector4 Insets()
        {
            Rect r = Current;
            return new Vector4(r.xMin, r.yMin, Screen.width - r.xMax, Screen.height - r.yMax);
        }

        private void Update()
        {
            if (Current != _applied || _screen.x != Screen.width || _screen.y != Screen.height) Apply();
        }

        private void Apply()
        {
            _applied = Current;
            _screen = new Vector2Int(Screen.width, Screen.height);
            if (_screen.x <= 0 || _screen.y <= 0) return;
            var rt = (RectTransform)transform;
            rt.anchorMin = new Vector2(_applied.xMin / _screen.x, _applied.yMin / _screen.y);
            rt.anchorMax = new Vector2(_applied.xMax / _screen.x, _applied.yMax / _screen.y);
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
        }
    }
}
