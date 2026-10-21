using System;
using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace Game.Presentation
{
    /// <summary>
    /// Turns touch (and mouse, for the editor) into Swiped("left|right|up|down") and Tapped events.
    /// Uses the Input System package when it is the active input handler, else the legacy Input Manager.
    /// Arrow keys also raise Swiped, for desktop testing. Screen y grows upward, so a drag toward the top is "up".
    /// </summary>
    public sealed class SwipeInput : MonoBehaviour
    {
        public event Action<string> Swiped;
        public event Action Tapped;

        /// <summary>Minimum drag length in pixels; 0 means automatic (2.5 percent of screen height, at least 40).</summary>
        public float MinSwipePixels = 0f;

        private bool _down;
        private Vector2 _start;

        /// <summary>Returns the dominant axis direction, or null when the drag is shorter than minPixels.</summary>
        public static string Classify(Vector2 delta, float minPixels)
        {
            if (delta.magnitude < minPixels) return null;
            if (Mathf.Abs(delta.x) >= Mathf.Abs(delta.y)) return delta.x > 0f ? "right" : "left";
            return delta.y > 0f ? "up" : "down";
        }

        private void Update()
        {
#if ENABLE_INPUT_SYSTEM
            bool handled = false;
            Touchscreen touch = Touchscreen.current;
            if (touch != null)
            {
                var primary = touch.primaryTouch;
                if (primary.press.wasPressedThisFrame)
                {
                    Begin(primary.position.ReadValue());
                    handled = true;
                }
                else if (primary.press.wasReleasedThisFrame)
                {
                    End(primary.position.ReadValue());
                    handled = true;
                }
            }
            Mouse mouse = Mouse.current;
            if (!handled && mouse != null)
            {
                if (mouse.leftButton.wasPressedThisFrame) Begin(mouse.position.ReadValue());
                else if (mouse.leftButton.wasReleasedThisFrame) End(mouse.position.ReadValue());
            }
            Keyboard keys = Keyboard.current;
            if (keys != null)
            {
                if (keys.leftArrowKey.wasPressedThisFrame) Raise("left");
                else if (keys.rightArrowKey.wasPressedThisFrame) Raise("right");
                else if (keys.upArrowKey.wasPressedThisFrame) Raise("up");
                else if (keys.downArrowKey.wasPressedThisFrame) Raise("down");
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            if (Input.touchCount > 0)
            {
                Touch t = Input.GetTouch(0);
                if (t.phase == TouchPhase.Began) Begin(t.position);
                else if (t.phase == TouchPhase.Ended) End(t.position);
                else if (t.phase == TouchPhase.Canceled) _down = false;
            }
            else if (Input.GetMouseButtonDown(0)) Begin(Input.mousePosition);
            else if (Input.GetMouseButtonUp(0)) End(Input.mousePosition);
            if (Input.GetKeyDown(KeyCode.LeftArrow)) Raise("left");
            else if (Input.GetKeyDown(KeyCode.RightArrow)) Raise("right");
            else if (Input.GetKeyDown(KeyCode.UpArrow)) Raise("up");
            else if (Input.GetKeyDown(KeyCode.DownArrow)) Raise("down");
#endif
        }

        private void Begin(Vector2 position)
        {
            _down = true;
            _start = position;
        }

        private void End(Vector2 position)
        {
            if (!_down) return;
            _down = false;
            float min = MinSwipePixels > 0f ? MinSwipePixels : Mathf.Max(40f, Screen.height * 0.025f);
            string dir = Classify(position - _start, min);
            if (dir != null) Raise(dir);
            else if (Tapped != null) Tapped();
        }

        private void Raise(string dir)
        {
            if (Swiped != null) Swiped(dir);
        }
    }
}
