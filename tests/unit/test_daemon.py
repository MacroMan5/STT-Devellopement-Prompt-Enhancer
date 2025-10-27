from pathlib import Path

from lazy_ptt.services.daemon import PTTDaemon


class _FakeOutcome:
    def __init__(self, index: int) -> None:
        self.saved_prompt = type('Saved', (), {'prompt_path': Path(f'prompt-{index}.md')})()
        self.enhanced = type('Enhanced', (), {'work_type': 'FEATURE'})()


class _SequenceService:
    def __init__(self, outcomes):
        self._outcomes = iter(outcomes)
        self.calls = 0

    def listen_once(self, auto_move: bool = False, **_kwargs):
        self.calls += 1
        return next(self._outcomes)


class _FlakyService:
    def __init__(self):
        self.calls = 0
        self._outcome = _FakeOutcome(2)

    def listen_once(self, auto_move: bool = False, **_kwargs):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError('transient failure')
        return self._outcome


def test_daemon_stops_when_requested():
    service = _SequenceService([_FakeOutcome(1)])
    daemon = PTTDaemon(service, auto_move=True)
    captured = []

    def on_cycle(outcome):
        captured.append(outcome)
        daemon.request_stop()

    daemon.on_cycle = on_cycle
    daemon.run()

    assert service.calls == 1
    assert captured and captured[0].saved_prompt.prompt_path.name == 'prompt-1.md'


def test_daemon_recovers_from_cycle_error():
    service = _FlakyService()
    daemon = PTTDaemon(service, auto_move=False)

    def on_cycle(_outcome):
        daemon.request_stop()

    daemon.on_cycle = on_cycle
    daemon.run()

    assert service.calls == 2
