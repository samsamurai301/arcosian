extends Node
## Audio buses, music crossfade and a pooled SFX player. Accepts null streams (no assets in the template).

const BUS_MUSIC: String = "Music"
const BUS_SFX: String = "SFX"
const SFX_POOL_SIZE: int = 8

var _music: Array[AudioStreamPlayer] = []
var _active: int = 0
var _sfx_pool: Array[AudioStreamPlayer] = []
var _sfx_next: int = 0


func _ready() -> void:
	_ensure_bus(BUS_MUSIC)
	_ensure_bus(BUS_SFX)
	for i in 2:
		_music.append(_make_player(BUS_MUSIC))
	for i in SFX_POOL_SIZE:
		_sfx_pool.append(_make_player(BUS_SFX))


func play_music(stream: AudioStream, fade_sec: float = 0.8) -> void:
	if stream == null or _music.is_empty():
		return
	var old: AudioStreamPlayer = _music[_active]
	if old.stream == stream and old.playing:
		return
	_active = 1 - _active
	var incoming: AudioStreamPlayer = _music[_active]
	incoming.stream = stream
	incoming.volume_db = -60.0
	incoming.play()
	var tw: Tween = create_tween().set_parallel(true)
	tw.tween_property(incoming, "volume_db", 0.0, fade_sec)
	tw.tween_property(old, "volume_db", -60.0, fade_sec)
	tw.chain().tween_callback(old.stop)


func play_sfx(stream: AudioStream, volume_db: float = 0.0, pitch: float = 1.0) -> void:
	if stream == null or _sfx_pool.is_empty():
		return
	var p: AudioStreamPlayer = _sfx_pool[_sfx_next]
	_sfx_next = (_sfx_next + 1) % _sfx_pool.size()
	p.stream = stream
	p.volume_db = volume_db
	p.pitch_scale = pitch
	p.play()


func set_bus_volume(bus: String, linear: float) -> void:
	var i: int = AudioServer.get_bus_index(bus)
	if i >= 0:
		AudioServer.set_bus_volume_db(i, linear_to_db(clampf(linear, 0.0, 1.0)))


func set_bus_muted(bus: String, muted: bool) -> void:
	var i: int = AudioServer.get_bus_index(bus)
	if i >= 0:
		AudioServer.set_bus_mute(i, muted)


func _ensure_bus(bus: String) -> void:
	if AudioServer.get_bus_index(bus) < 0:
		AudioServer.add_bus()
		AudioServer.set_bus_name(AudioServer.bus_count - 1, bus)


func _make_player(bus: String) -> AudioStreamPlayer:
	var p: AudioStreamPlayer = AudioStreamPlayer.new()
	p.bus = bus
	add_child(p)
	return p
