using System;
using System.Collections.Generic;
using System.IO;
using Game.Core;
using Game.Presentation.Services;
using UnityEngine;
using UnityEngine.UI;

namespace Game.Presentation
{
    /// <summary>
    /// Composition root. SceneBuilder puts one of these in Assets/_Game/Scenes/Main.unity; everything else
    /// (canvas, board, services) is created here at runtime, so the scene has no fragile serialized references.
    /// Flow: input -> Sim.Apply(action) -> events -> BoardView.Play / ScreenShake / audio / haptics / analytics.
    /// </summary>
    public sealed class Bootstrap : MonoBehaviour
    {
        private const float BoardPixels = 1000f; // in the 1080x1920 reference resolution

        public static Bootstrap Current { get; private set; }

        [SerializeField] private TextAsset tuningJson;

        public Sim Sim { get; private set; }
        public IAds Ads { get; set; } = new MockAds();
        public IIap Iap { get; set; } = new MockIap();

        private SaveService _save;
        private AudioService _audio;
        private BoardView _board;
        private ScreenShake _shake;
        private Text _scoreText;
        private Text _bestText;
        private Text _banner;

        private void Awake()
        {
            Current = this;
            Application.targetFrameRate = 60;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;

            Analytics.Backends.Clear();
            Analytics.Backends.Add(new DebugAnalytics());

            _save = new SaveService(Path.Combine(Application.persistentDataPath, "save.json"));
            _save.Load();
            Haptics.Enabled = _save.HapticsOn;
            _audio = gameObject.AddComponent<AudioService>();
            _audio.SfxEnabled = _save.SoundOn;

            Tuning tuning = Tuning.Parse(tuningJson != null ? tuningJson.text : null);
            Sim = new Sim(NewSeed(), tuning);
            bool restored = Sim.LoadDict(_save.Run) && Sim.State.Status == GameState.Playing;
            if (!restored) _save.ClearRun();

            BuildUi();
            var input = gameObject.AddComponent<SwipeInput>();
            input.Swiped += OnSwiped;
            input.Tapped += OnTapped;

            _board.Render(Sim.State);
            UpdateHud();
            Analytics.Log("game_start", new Dictionary<string, object> { { "seed", Sim.State.SeedValue }, { "restored", restored } });
        }

        private void OnEnable()
        {
            EventBus.AppPaused += SaveProgress;
        }

        private void OnDisable()
        {
            EventBus.AppPaused -= SaveProgress;
        }

        private void OnDestroy()
        {
            if (Current == this) Current = null;
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused) EventBus.RaiseAppPaused();
            else EventBus.RaiseAppResumed();
        }

        private void OnApplicationFocus(bool focused)
        {
            if (!focused) EventBus.RaiseAppPaused();
        }

        private void OnApplicationQuit()
        {
            EventBus.RaiseAppPaused();
        }

        /// <summary>Applies a move as if swiped. Used by ScreenshotCapture; safe to call from tests.</summary>
        public void DebugMove(string dir)
        {
            OnSwiped(dir);
        }

        private static long NewSeed()
        {
            return DateTime.UtcNow.Ticks & 0x7FFFFFFF;
        }

        private void SaveProgress()
        {
            if (Sim.State.Status == GameState.Playing) _save.StashRun(Sim.ToDict());
            _save.Flush();
        }

        private void OnSwiped(string dir)
        {
            if (Sim.State.Status != GameState.Playing) return;
            List<SimEvent> events = Sim.Apply(GameAction.Move(dir));
            SimEvent first = events[0];
            if (first.Type == SimEventType.Rejected) return;
            if (first.Type == SimEventType.InvalidMove)
            {
                _shake.Shake(8f, 0.12f);
                return;
            }

            _board.Play(events, Sim.State);
            int merges = 0;
            foreach (SimEvent e in events)
                if (e.Type == SimEventType.Merge) merges++;
            if (merges > 0)
            {
                _shake.Shake(6f + 3f * merges, 0.15f);
                _audio.PlaySfx("merge");
                Haptics.Light();
            }
            else
            {
                _audio.PlaySfx("move", 0.5f);
            }
            UpdateHud();
            EventBus.RaiseSimEvents(events);
            if (Sim.State.Status != GameState.Playing) EndRun();
        }

        private void OnTapped()
        {
            if (Sim.State.Status == GameState.Playing) return;
            Sim.Apply(GameAction.NewGame(NewSeed()));
            _board.Render(Sim.State);
            _banner.text = "";
            UpdateHud();
            Analytics.Log("game_start", new Dictionary<string, object> { { "seed", Sim.State.SeedValue }, { "restored", false } });
        }

        private void EndRun()
        {
            bool won = Sim.State.Status == GameState.Won;
            int score = Sim.State.Score;
            _save.RecordResult(score, won);
            _save.ClearRun();
            _save.Flush();
            _audio.PlaySfx(won ? "win" : "lose");
            Haptics.Heavy();
            _banner.text = (won ? "You win!" : "No moves left") + "\nTap to play again";
            UpdateHud();
            Analytics.Log("game_end", new Dictionary<string, object>
            {
                { "result", won ? "win" : "loss" }, { "score", score }, { "moves", Sim.State.Moves },
            });
            EventBus.RaiseRunEnded(won, score);
        }

        private void UpdateHud()
        {
            _scoreText.text = "Score " + Sim.State.Score;
            _bestText.text = "Best " + Math.Max(_save.BestScore, Sim.State.Score);
        }

        private void BuildUi()
        {
            Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");

            var canvasGo = new GameObject("Canvas", typeof(Canvas), typeof(CanvasScaler));
            canvasGo.transform.SetParent(transform, false);
            canvasGo.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasGo.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1080f, 1920f);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 0.5f;

            var safeGo = new GameObject("SafeArea", typeof(RectTransform), typeof(SafeArea));
            var safe = (RectTransform)safeGo.transform;
            safe.SetParent(canvasGo.transform, false);
            safe.anchorMin = Vector2.zero;
            safe.anchorMax = Vector2.one;
            safe.offsetMin = Vector2.zero;
            safe.offsetMax = Vector2.zero;

            Color ink = new Color(0.93f, 0.89f, 0.85f);
            _scoreText = MakeText(safe, "Score", font, 64, TextAnchor.MiddleLeft, new Vector2(0f, 1f), new Vector2(60f, -140f), new Vector2(500f, 100f), ink);
            _bestText = MakeText(safe, "Best", font, 64, TextAnchor.MiddleRight, new Vector2(1f, 1f), new Vector2(-60f, -140f), new Vector2(500f, 100f), ink);
            _banner = MakeText(safe, "Banner", font, 64, TextAnchor.MiddleCenter, new Vector2(0.5f, 0.5f), new Vector2(0f, -700f), new Vector2(1000f, 240f), ink);

            var boardGo = new GameObject("Board", typeof(RectTransform), typeof(Image));
            var board = (RectTransform)boardGo.transform;
            board.SetParent(safe, false);
            board.anchorMin = board.anchorMax = new Vector2(0.5f, 0.5f);
            board.sizeDelta = new Vector2(BoardPixels, BoardPixels);
            board.anchoredPosition = new Vector2(0f, 60f);
            var bg = boardGo.GetComponent<Image>();
            bg.color = new Color(0.20f, 0.19f, 0.17f);
            bg.raycastTarget = false;
            _shake = boardGo.AddComponent<ScreenShake>();
            _board = boardGo.AddComponent<BoardView>();
            _board.Build(Sim.Tuning.Size, font);
        }

        private static Text MakeText(Transform parent, string objectName, Font font, int fontSize, TextAnchor align,
            Vector2 anchor, Vector2 position, Vector2 size, Color color)
        {
            var go = new GameObject(objectName, typeof(RectTransform), typeof(Text));
            var rt = (RectTransform)go.transform;
            rt.SetParent(parent, false);
            rt.anchorMin = rt.anchorMax = anchor;
            rt.pivot = anchor;
            rt.anchoredPosition = position;
            rt.sizeDelta = size;
            var text = go.GetComponent<Text>();
            text.font = font;
            text.fontSize = fontSize;
            text.alignment = align;
            text.color = color;
            text.raycastTarget = false;
            return text;
        }
    }
}
