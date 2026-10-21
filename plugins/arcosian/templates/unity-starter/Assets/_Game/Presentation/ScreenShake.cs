using UnityEngine;

namespace Game.Presentation
{
    /// <summary>
    /// Shakes this RectTransform. Cosmetic only, so it may use UnityEngine.Random (the sim never does).
    /// The amplitude decays linearly to zero and the rest position is restored exactly.
    /// </summary>
    [RequireComponent(typeof(RectTransform))]
    public sealed class ScreenShake : MonoBehaviour
    {
        private RectTransform _rt;
        private Vector2 _rest;
        private float _amplitude;
        private float _duration;
        private float _left;

        public void Shake(float amplitudePixels, float seconds)
        {
            if (seconds <= 0f) return;
            if (_rt == null) _rt = (RectTransform)transform;
            if (_left <= 0f) _rest = _rt.anchoredPosition; // capture only when idle, never mid-shake
            _amplitude = Mathf.Max(_left > 0f ? _amplitude * (_left / _duration) : 0f, amplitudePixels);
            _duration = seconds;
            _left = seconds;
        }

        private void Update()
        {
            if (_left <= 0f) return;
            _left -= Time.unscaledDeltaTime;
            if (_left <= 0f)
            {
                _rt.anchoredPosition = _rest;
                return;
            }
            _rt.anchoredPosition = _rest + Random.insideUnitCircle * (_amplitude * (_left / _duration));
        }
    }
}
