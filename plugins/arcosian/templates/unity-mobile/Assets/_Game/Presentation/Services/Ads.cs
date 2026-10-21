using System;

namespace Game.Presentation.Services
{
    /// <summary>Ad abstraction. Implement it over your mediation SDK; callbacks must arrive on the main thread.</summary>
    public interface IAds
    {
        bool IsRewardedReady { get; }
        /// <summary>onComplete(true) only when the reward was earned.</summary>
        void ShowRewarded(string placement, Action<bool> onComplete);
        void ShowInterstitial(string placement, Action onClosed);
    }

    /// <summary>Editor and test backend: always ready, completes synchronously with RewardResult.</summary>
    public sealed class MockAds : IAds
    {
        public bool RewardResult = true;
        public bool IsRewardedReady { get { return true; } }

        public void ShowRewarded(string placement, Action<bool> onComplete)
        {
            if (onComplete != null) onComplete(RewardResult);
        }

        public void ShowInterstitial(string placement, Action onClosed)
        {
            if (onClosed != null) onClosed();
        }
    }
}
