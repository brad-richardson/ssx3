#pragma once

// Frontend intent, separate from the runtime's asynchronously changing state.
// Returning to an existing session waits at the menu for an explicit Resume.
struct SSXSessionPause {
  enum class RuntimeState { Unavailable, Running, Paused };
  enum class Action { None, Pause, Resume };
  bool active = true;
  bool menu = false;
  bool audio_interrupted = false;
  bool return_to_menu = false;

  void SetActive(bool value, bool has_session) {
    active = value;
    if (!value && has_session) return_to_menu = true;
  }
  void SetAudioInterrupted(bool value, bool has_session) {
    audio_interrupted = value;
    if (value && has_session) return_to_menu = true;
  }
  void NewSession() { menu = false; return_to_menu = false; }
  void OpenMenu() { menu = true; }
  bool RequestResume(bool is_active, bool audio_activated) {
    active = is_active;
    audio_interrupted = !audio_activated;
    menu = false;
    return_to_menu = !active || audio_interrupted;
    return !WantsPause();
  }
  bool WantsPause() const { return !active || menu || audio_interrupted || return_to_menu; }
  bool NeedsMenu(bool ready) const { return ready && active && return_to_menu && !menu; }
  Action Reconcile(RuntimeState state) const {
    if (WantsPause() && state == RuntimeState::Running) return Action::Pause;
    if (!WantsPause() && state == RuntimeState::Paused) return Action::Resume;
    return Action::None;
  }
};
