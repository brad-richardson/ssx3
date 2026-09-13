#include "SessionPause.h"
#include <cassert>
#include <initializer_list>

int main() {
  using P = SSXSessionPause;
  using R = P::RuntimeState;
  using A = P::Action;
  P p;
  assert(p.Reconcile(R::Unavailable) == A::None);
  // A paused core can be recovered even without a frontend-owned Pause call.
  assert(p.Reconcile(R::Paused) == A::Resume);
  assert(p.Reconcile(R::Running) == A::None);
  for (int i = 0; i < 3; ++i) {
    p.OpenMenu();
    assert(p.Reconcile(R::Running) == A::Pause);
    assert(p.Reconcile(R::Paused) == A::None);
    assert(p.RequestResume(true, true));
    assert(p.Reconcile(R::Paused) == A::Resume);
    assert(p.Reconcile(R::Paused) == A::Resume); // Retry transient runtime state.
    assert(p.Reconcile(R::Running) == A::None);
  }
  p.SetActive(false, true);
  assert(!p.NeedsMenu(true));
  p.SetActive(true, true);
  assert(p.NeedsMenu(true));
  assert(p.Reconcile(R::Paused) == A::None); // Foreground does not start riding.
  p.OpenMenu();
  assert(!p.NeedsMenu(true));
  assert(p.RequestResume(true, true));
  // Missing interruption-ended notification must not trap explicit Resume.
  p.SetAudioInterrupted(true, true);
  p.OpenMenu();
  assert(!p.RequestResume(true, false));
  assert(p.WantsPause());
  assert(p.NeedsMenu(true));
  assert(p.RequestResume(true, true));
  // Either ordering of interruption end / foreground waits for the user.
  for (bool audioFirst : {false, true}) {
    p.SetAudioInterrupted(true, true);
    p.SetActive(false, true);
    if (audioFirst) p.SetAudioInterrupted(false, true);
    p.SetActive(true, true);
    if (!audioFirst) p.SetAudioInterrupted(false, true);
    assert(p.NeedsMenu(true));
    assert(p.WantsPause());
    assert(p.RequestResume(true, true));
  }
  assert(!p.RequestResume(false, true));
  assert(p.WantsPause());
  p.SetActive(true, true);
  assert(p.NeedsMenu(true));
  p.NewSession();
  assert(!p.WantsPause());
  p.SetActive(false, false);
  p.NewSession();
  assert(p.WantsPause());
  p.SetActive(true, false);
  assert(!p.NeedsMenu(true));
  assert(!p.WantsPause());
}
