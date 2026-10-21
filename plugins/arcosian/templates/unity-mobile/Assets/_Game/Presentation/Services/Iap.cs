using System;
using System.Collections.Generic;

namespace Game.Presentation.Services
{
    public enum PurchaseStatus { Success, Cancelled, Failed }

    /// <summary>In-app purchase abstraction. Implement it over Unity IAP or a store SDK.</summary>
    public interface IIap
    {
        void Purchase(string productId, Action<PurchaseStatus> onDone);
        /// <summary>Calls back with the ids of every product the player owns.</summary>
        void Restore(Action<IReadOnlyCollection<string>> onDone);
    }

    /// <summary>Editor and test backend: every purchase succeeds unless NextStatus says otherwise.</summary>
    public sealed class MockIap : IIap
    {
        public PurchaseStatus NextStatus = PurchaseStatus.Success;
        public readonly HashSet<string> Owned = new HashSet<string>();

        public void Purchase(string productId, Action<PurchaseStatus> onDone)
        {
            if (NextStatus == PurchaseStatus.Success) Owned.Add(productId);
            if (onDone != null) onDone(NextStatus);
        }

        public void Restore(Action<IReadOnlyCollection<string>> onDone)
        {
            if (onDone != null) onDone(Owned);
        }
    }
}
