using System.Collections;
using System.Collections.Generic;
using Game.Core;
using UnityEngine;
using UnityEngine.UI;

namespace Game.Presentation
{
    /// <summary>
    /// Draws the grid with uGUI and animates the events returned by Sim.Apply. It never mutates game state.
    /// Tiles are pooled; cell index i sits at row i / size, column i % size, row 0 at the top.
    /// </summary>
    public sealed class BoardView : MonoBehaviour
    {
        private const float Gap = 12f;
        private const float MoveSeconds = 0.09f;
        private const float PopSeconds = 0.12f;

        private static readonly Color[] Palette =
        {
            new Color(0.93f, 0.89f, 0.85f), new Color(0.93f, 0.88f, 0.78f), new Color(0.95f, 0.69f, 0.47f),
            new Color(0.96f, 0.58f, 0.39f), new Color(0.96f, 0.49f, 0.37f), new Color(0.96f, 0.37f, 0.23f),
            new Color(0.93f, 0.81f, 0.45f), new Color(0.93f, 0.80f, 0.38f), new Color(0.93f, 0.78f, 0.31f),
            new Color(0.93f, 0.77f, 0.25f), new Color(0.93f, 0.76f, 0.18f), new Color(0.24f, 0.23f, 0.20f),
        };

        private sealed class TileView
        {
            public RectTransform Rt;
            public Image Bg;
            public Text Label;
        }

        private readonly Stack<TileView> _pool = new Stack<TileView>();
        private TileView[] _shown;
        private int[] _pending; // the grid the view is animating toward (or showing)
        private RectTransform _rt;
        private Font _font;
        private int _size;
        private float _boardPx;
        private float _cell;
        private bool _animating;

        /// <summary>Create the empty cells. The RectTransform must already have its final sizeDelta (square).</summary>
        public void Build(int size, Font font)
        {
            _size = size;
            _font = font;
            _rt = (RectTransform)transform;
            _boardPx = _rt.sizeDelta.x;
            _cell = (_boardPx - Gap * (size + 1)) / size;
            _shown = new TileView[size * size];
            for (int i = 0; i < size * size; i++)
            {
                var go = new GameObject("Cell" + i, typeof(RectTransform), typeof(Image));
                var rt = (RectTransform)go.transform;
                rt.SetParent(_rt, false);
                rt.sizeDelta = new Vector2(_cell, _cell);
                rt.anchoredPosition = CellPos(i);
                var img = go.GetComponent<Image>();
                img.color = new Color(1f, 1f, 1f, 0.12f);
                img.raycastTarget = false;
            }
        }

        /// <summary>Show the state immediately, cancelling any animation (new game, restore, resume).</summary>
        public void Render(GameState state)
        {
            StopAllCoroutines();
            _animating = false;
            _pending = (int[])state.Grid.Clone();
            RenderGrid(_pending);
        }

        /// <summary>Animate the events of one Sim.Apply call; state is the state after the move.</summary>
        public void Play(IReadOnlyList<SimEvent> events, GameState state)
        {
            if (_animating)
            {
                StopAllCoroutines();
                RenderGrid(_pending); // snap to the previous move's result so slide origins match what is shown
            }
            _pending = (int[])state.Grid.Clone();
            SimEvent slide = null;
            var pops = new List<int>();
            foreach (SimEvent e in events)
            {
                if (e.Type == SimEventType.Slide) slide = e;
                else if (e.Type == SimEventType.Merge || e.Type == SimEventType.Spawn) pops.Add(e.At);
            }
            StartCoroutine(Animate(slide, pops));
        }

        private IEnumerator Animate(SimEvent slide, List<int> pops)
        {
            _animating = true;
            if (slide != null && slide.Moves != null)
            {
                var tiles = new List<TileView>();
                var starts = new List<Vector2>();
                var ends = new List<Vector2>();
                foreach (TileMove m in slide.Moves)
                {
                    TileView tv = _shown[m.From];
                    if (tv == null) continue;
                    tiles.Add(tv);
                    starts.Add(CellPos(m.From));
                    ends.Add(CellPos(m.To));
                }
                for (float t = 0f; t < MoveSeconds; t += Time.unscaledDeltaTime)
                {
                    float k = t / MoveSeconds;
                    k = k * (2f - k); // ease out
                    for (int i = 0; i < tiles.Count; i++) tiles[i].Rt.anchoredPosition = Vector2.Lerp(starts[i], ends[i], k);
                    yield return null;
                }
            }
            RenderGrid(_pending);
            foreach (int at in pops)
                if (at >= 0 && at < _shown.Length && _shown[at] != null) StartCoroutine(Pop(_shown[at].Rt));
            _animating = false;
        }

        private IEnumerator Pop(RectTransform rt)
        {
            for (float t = 0f; t < PopSeconds; t += Time.unscaledDeltaTime)
            {
                rt.localScale = Vector3.one * (1f + 0.18f * Mathf.Sin(t / PopSeconds * Mathf.PI));
                yield return null;
            }
            rt.localScale = Vector3.one;
        }

        private void RenderGrid(int[] grid)
        {
            for (int i = 0; i < grid.Length; i++)
            {
                if (_shown[i] != null)
                {
                    _shown[i].Rt.gameObject.SetActive(false);
                    _pool.Push(_shown[i]);
                    _shown[i] = null;
                }
                if (grid[i] == 0) continue;
                TileView tv = Acquire(grid[i]);
                tv.Rt.anchoredPosition = CellPos(i);
                tv.Rt.localScale = Vector3.one;
                _shown[i] = tv;
            }
        }

        private TileView Acquire(int value)
        {
            TileView tv;
            if (_pool.Count > 0)
            {
                tv = _pool.Pop();
                tv.Rt.gameObject.SetActive(true);
            }
            else
            {
                var go = new GameObject("Tile", typeof(RectTransform), typeof(Image));
                tv = new TileView { Rt = (RectTransform)go.transform, Bg = go.GetComponent<Image>() };
                tv.Rt.SetParent(_rt, false);
                tv.Rt.sizeDelta = new Vector2(_cell, _cell);
                tv.Bg.raycastTarget = false;

                var labelGo = new GameObject("Label", typeof(RectTransform), typeof(Text));
                var lrt = (RectTransform)labelGo.transform;
                lrt.SetParent(tv.Rt, false);
                lrt.anchorMin = Vector2.zero;
                lrt.anchorMax = Vector2.one;
                lrt.offsetMin = Vector2.zero;
                lrt.offsetMax = Vector2.zero;
                tv.Label = labelGo.GetComponent<Text>();
                tv.Label.font = _font;
                tv.Label.alignment = TextAnchor.MiddleCenter;
                tv.Label.raycastTarget = false;
            }
            int idx = 0;
            for (int v = value; v > 2; v >>= 1) idx++;
            tv.Bg.color = Palette[Mathf.Clamp(idx, 0, Palette.Length - 1)];
            tv.Label.text = value.ToString();
            tv.Label.fontSize = value < 100 ? 72 : value < 1000 ? 60 : 48;
            tv.Label.color = value <= 4 ? new Color(0.47f, 0.43f, 0.40f) : Color.white;
            return tv;
        }

        private Vector2 CellPos(int i)
        {
            int row = i / _size;
            int col = i % _size;
            float x = Gap + col * (_cell + Gap) + _cell * 0.5f - _boardPx * 0.5f;
            float y = _boardPx * 0.5f - (Gap + row * (_cell + Gap) + _cell * 0.5f);
            return new Vector2(x, y);
        }
    }
}
