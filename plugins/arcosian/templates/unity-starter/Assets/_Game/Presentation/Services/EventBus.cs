using System;
using System.Collections.Generic;
using Game.Core;
using UnityEngine;

namespace Game.Presentation.Services
{
    /// <summary>
    /// Decoupled notifications between presentation and services. Only the owner raises; anyone subscribes.
    /// Subscribers must unsubscribe in OnDisable/OnDestroy. Handlers are cleared on every play-mode start,
    /// so "Enter Play Mode without domain reload" does not leak subscriptions.
    /// </summary>
    public static class EventBus
    {
        public static event Action AppPaused;
        public static event Action AppResumed;
        public static event Action<IReadOnlyList<SimEvent>> SimEvents;
        public static event Action<bool, int> RunEnded; // won, score

        public static void RaiseAppPaused() { AppPaused?.Invoke(); }
        public static void RaiseAppResumed() { AppResumed?.Invoke(); }
        public static void RaiseSimEvents(IReadOnlyList<SimEvent> events) { SimEvents?.Invoke(events); }
        public static void RaiseRunEnded(bool won, int score) { RunEnded?.Invoke(won, score); }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void Reset()
        {
            AppPaused = null;
            AppResumed = null;
            SimEvents = null;
            RunEnded = null;
        }
    }
}
