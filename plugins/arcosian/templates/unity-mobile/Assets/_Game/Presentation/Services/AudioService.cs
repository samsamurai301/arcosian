using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Game.Presentation.Services
{
    /// <summary>
    /// 8-voice SFX pool and a two-source music crossfade. Clips load lazily from Resources/Audio/&lt;key&gt;;
    /// a missing clip is silently skipped, so the game runs before any audio is imported.
    /// </summary>
    public sealed class AudioService : MonoBehaviour
    {
        private const int Voices = 8;

        private readonly Dictionary<string, AudioClip> _cache = new Dictionary<string, AudioClip>();
        private AudioSource[] _sfx;
        private AudioSource[] _music;
        private int _nextVoice;
        private int _activeMusic;
        private Coroutine _fade;

        public bool SfxEnabled { get; set; } = true;
        public bool MusicEnabled { get; set; } = true;

        private void Awake()
        {
            _sfx = new AudioSource[Voices];
            for (int i = 0; i < Voices; i++) _sfx[i] = NewSource("Sfx" + i, false);
            _music = new[] { NewSource("MusicA", true), NewSource("MusicB", true) };
        }

        private AudioSource NewSource(string sourceName, bool loop)
        {
            var go = new GameObject(sourceName);
            go.transform.SetParent(transform, false);
            AudioSource s = go.AddComponent<AudioSource>();
            s.playOnAwake = false;
            s.loop = loop;
            return s;
        }

        private AudioClip Get(string key)
        {
            AudioClip clip;
            if (!_cache.TryGetValue(key, out clip))
            {
                clip = Resources.Load<AudioClip>("Audio/" + key);
                _cache[key] = clip; // null is cached too: do not hit Resources again for a missing clip
            }
            return clip;
        }

        public void PlaySfx(string key, float volume = 1f)
        {
            if (!SfxEnabled) return;
            AudioClip clip = Get(key);
            if (clip == null) return;
            AudioSource s = _sfx[_nextVoice];
            _nextVoice = (_nextVoice + 1) % Voices;
            s.clip = clip;
            s.volume = volume;
            s.Play();
        }

        public void PlayMusic(string key, float fadeSeconds = 1f)
        {
            AudioClip clip = Get(key);
            if (!MusicEnabled || clip == null) return;
            if (_fade != null) StopCoroutine(_fade);
            _fade = StartCoroutine(Crossfade(clip, Mathf.Max(0.01f, fadeSeconds)));
        }

        private IEnumerator Crossfade(AudioClip clip, float seconds)
        {
            AudioSource fadeOut = _music[_activeMusic];
            _activeMusic = 1 - _activeMusic;
            AudioSource fadeIn = _music[_activeMusic];
            fadeIn.clip = clip;
            fadeIn.volume = 0f;
            fadeIn.Play();
            for (float t = 0f; t < seconds; t += Time.unscaledDeltaTime)
            {
                float k = t / seconds;
                fadeIn.volume = k;
                fadeOut.volume = 1f - k;
                yield return null;
            }
            fadeIn.volume = 1f;
            fadeOut.Stop();
            fadeOut.volume = 0f;
            _fade = null;
        }
    }
}
