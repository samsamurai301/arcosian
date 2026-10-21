extends Node
## Ads interface. The default backend is a mock that always grants. Replace with an AppLifecycle-aware
## AppLovin MAX backend: set_backend(obj) where obj implements show_rewarded(placement) and show_interstitial(placement)
## and calls back by emitting Ads.rewarded_result / Ads.interstitial_closed.

signal rewarded_result(placement: String, granted: bool)
signal interstitial_closed(placement: String)

var enabled: bool = true  # set false after a "remove ads" purchase
var _backend: Object = MockBackend.new()


class MockBackend:
	extends RefCounted
	var grant: bool = true


func set_backend(backend: Object) -> void:
	_backend = backend


func is_rewarded_ready(_placement: String) -> bool:
	return enabled


func show_rewarded(placement: String) -> void:
	if _backend is MockBackend:
		rewarded_result.emit.call_deferred(placement, enabled and _backend.grant)
	elif _backend.has_method("show_rewarded"):
		_backend.show_rewarded(placement)


func show_interstitial(placement: String) -> void:
	if not enabled:
		interstitial_closed.emit.call_deferred(placement)
	elif _backend is MockBackend:
		interstitial_closed.emit.call_deferred(placement)
	elif _backend.has_method("show_interstitial"):
		_backend.show_interstitial(placement)
